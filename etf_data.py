#!/usr/bin/env python3
"""Build data/etfs/*.json: holdings, weights, prices, returns and weighted fundamentals.

Holdings come from the funds' own N-PORT filings with the SEC, because every US fund has to file
them and nobody can put a bot wall in front of EDGAR. iShares, Invesco and Vanguard all serve a
product page instead of their published holdings file when a script asks, so their own downloads
are not usable here. SPY is the exception: it is a unit investment trust, so its holdings come
from State Street's daily workbook instead.

The fundamentals are not fetched at all. Every holding is matched to our own company data and the
fund's price/earnings, growth and margins are computed from the same numbers that are on our stock
pages, weighted by the fund's own weights. That is the whole point of the section: the P/E we show
for QQQ is built from the same filings as the P/E we show for Nvidia, and every holding row links
to the page for that company.

Output: data/etfs/<TICKER>.json and data/etfs/index.json.
"""
import json, os, re, sys, time, io, zipfile, html as _html, datetime as dt
import urllib.request, urllib.error, urllib.parse

import etf_list

OUT = os.environ.get('ETF_OUT', 'data/etfs')
MIN_COVER = 85.0   # below this share of the fund's weight, our figures describe a slice, not the fund
STOCKS = 'data/stocks'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
SEC_UA = os.environ.get('SEC_UA', 'stockanaliz.com research contact@stockanaliz.com')
SEC_HDR = {'User-Agent': SEC_UA, 'Accept-Encoding': 'gzip, deflate'}
NASDAQ_HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*',
              'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}
TODAY = dt.date.today()
_last_sec = [0.0]


def days(a, b):
    try:
        return (dt.date.fromisoformat(b[:10]) - dt.date.fromisoformat(a[:10])).days
    except Exception:
        return 10 ** 6


def fetch(url, hdr=None, timeout=90, tries=3, rng=None):
    h = dict(hdr or {'User-Agent': UA, 'Accept': '*/*'})
    if rng:
        h['Range'] = 'bytes=0-%d' % rng
    for i in range(tries):
        if hdr is SEC_HDR:                     # EDGAR asks for no more than ten requests a second
            gap = time.time() - _last_sec[0]
            if gap < 0.15:
                time.sleep(0.15 - gap)
            _last_sec[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    import gzip
                    body = gzip.decompress(body)
                return body
        except urllib.error.HTTPError as ex:
            if ex.code in (403, 404):
                return None
            if i == tries - 1:
                return None
            time.sleep(2 + 3 * i)
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(2 + 3 * i)
    return None


# ---------------------------------------------------------------- our own company data

_NOISE = re.compile(r'\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|PLC|NV|SA|AG|SE|'
                    r'HOLDINGS?|GROUP|TRUST|THE|CLASS|CL|COM|NEW|ORD|SHS|SPON|ADR|REIT|LP|LLC|'
                    r'INTERNATIONAL|INTL|TECHNOLOGIES|TECHNOLOGY|SYSTEMS|SERVICES)\b')


def norm(n):
    s = re.sub(r'[^A-Z0-9 ]', ' ', str(n or '').upper())
    s = _NOISE.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def keys(n):
    """Normalised name, then the same without a trailing share-class letter.

    Funds write 'Alphabet Inc Class A' where our own data says 'Alphabet Inc.', and once CLASS is
    stripped the stray A would otherwise stop the two from matching.
    """
    k = norm(n)
    out = [k]
    while len(k.split()) > 1 and len(k.split()[-1]) == 1:
        k = k.rsplit(' ', 1)[0]
        out.append(k)
    return out


def load_universe():
    """ticker -> our record, plus a normalised-name index for matching N-PORT holdings."""
    idx = json.load(open('data/index.json'))
    by_name, by_ticker, squash = {}, {}, {}
    for row in idx:
        t, n = row['t'], row.get('n') or ''
        by_ticker[t] = n
        for k in keys(n):
            if k and k not in by_name:        # first listing wins; index.json is ordered by size
                by_name[k] = t
            sq = k.replace(' ', '')
            if sq and sq not in squash:       # 'Exxon Mobil' against our own 'ExxonMobil'
                squash[sq] = t
    by_name['\x00squash'] = squash
    return by_ticker, by_name


def stock(t):
    try:
        return json.load(open(os.path.join(STOCKS, t + '.json')))
    except Exception:
        return None


# ---------------------------------------------------------------- holdings: SEC N-PORT

CACHE = os.path.join(OUT, '_series_cache.json')


def _cache():
    try:
        return json.load(open(CACHE))
    except Exception:
        return {}


def series_accessions(cik, series, want=4, cache=None):
    """Recent NPORT-P accession numbers for one fund series.

    A trust files one report per series under the same CIK, and the submissions index does not say
    which series a filing covers, so the series feed is asked first and the filing headers are read
    only if that fails.
    """
    url = ('https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=NPORT-P'
           '&dateb=&owner=include&count=%d&output=atom' % (series, want))
    b = fetch(url, SEC_HDR)
    accs = []
    if b:
        txt = b.decode('utf-8', 'replace')
        accs = re.findall(r'<accession-n\w+>\s*([\d-]{18,20})\s*<', txt)
        if not accs:
            raw = re.findall(r'/Archives/edgar/data/\d+/(\d{18})[/\-]', txt)
            accs = ['%s-%s-%s' % (a[:10], a[10:12], a[12:]) for a in raw]
    if accs:
        print('      series feed -> %d accessions' % len(accs))
        return list(dict.fromkeys(accs))[:want]

    # Reports are filed quarterly, so a hit found last week is still the right one this week. Without
    # this the walk below runs for every fund on every run and the whole build takes the best part of
    # an hour; iShares alone files well over a thousand reports under one CIK.
    if cache is not None:
        hit = cache.get(series)
        if hit and hit.get('acc') and days(hit.get('found') or '2000-01-01', TODAY.isoformat()) < 75:
            print('      cached accession %s' % hit['acc'])
            return [hit['acc']]

    # Fallback: walk the trust's own NPORT-P filings and read just enough of each to see the series.
    print('      series feed empty, scanning the trust\'s filings')
    b = fetch('https://data.sec.gov/submissions/CIK%010d.json' % int(cik), SEC_HDR)
    if not b:
        return []
    rec = (json.loads(b).get('filings') or {}).get('recent') or {}
    forms = rec.get('form') or []
    cands = [rec['accessionNumber'][i] for i in range(len(forms)) if forms[i].startswith('NPORT-P')]
    out = []
    for acc in cands[:400]:
        head = fetch('https://www.sec.gov/Archives/edgar/data/%d/%s/%s-index-headers.html'
                     % (int(cik), acc.replace('-', ''), acc), SEC_HDR, rng=6000)
        if head and series.encode() in head:
            out.append(acc)
            if cache is not None and len(out) == 1:
                cache[series] = dict(acc=acc, found=TODAY.isoformat())
            if len(out) >= want:
                break
    return out


_HOLD = re.compile(r'<invstOrSec>(.*?)</invstOrSec>', re.S)


def _tag(block, name):
    m = re.search(r'<%s>(.*?)</%s>' % (name, name), block, re.S)
    return m.group(1).strip() if m else None


def parse_nport(xml):
    """(as_of, [holding, ...]) from one N-PORT report."""
    s = xml.decode('utf-8', 'replace')
    as_of = _tag(s, 'repPdDate') or _tag(s, 'repPdEnd') or ''
    rows = []
    for blk in _HOLD.findall(s):
        name = _tag(blk, 'name')
        pct = _tag(blk, 'pctVal')
        val = _tag(blk, 'valUSD')
        if not name or pct is None:
            continue
        try:
            pct = float(pct)
        except ValueError:
            continue
        if pct <= 0:
            continue
        iso = re.search(r'<isin\s+value="([^"]+)"', blk)
        rows.append(dict(name=re.sub(r'\s+', ' ', _html.unescape(name)).strip(),
                         pct=round(pct, 4),
                         usd=float(val) if val and re.match(r'^-?[\d.]+$', val) else None,
                         isin=iso.group(1) if iso else None,
                         cusip=_tag(blk, 'cusip')))
    rows.sort(key=lambda r: -r['pct'])
    return as_of[:10], rows


def nport_holdings(cik, series, cache=None):
    for acc in series_accessions(cik, series, cache=cache):
        a = acc.replace('-', '')
        idx = fetch('https://www.sec.gov/Archives/edgar/data/%d/%s/index.json' % (int(cik), a), SEC_HDR)
        if not idx:
            continue
        items = (json.loads(idx).get('directory') or {}).get('item') or []
        xmls = [x for x in items if x['name'].endswith('.xml')]
        if not xmls:
            continue
        big = max(xmls, key=lambda x: int(x.get('size') or 0))
        body = fetch('https://www.sec.gov/Archives/edgar/data/%d/%s/%s' % (int(cik), a, big['name']), SEC_HDR)
        if not body:
            continue
        as_of, rows = parse_nport(body)
        if rows:
            return as_of, rows, 'SEC N-PORT'
    return None, [], None


# ---------------------------------------------------------------- holdings: State Street workbook

def _xlsx_rows(body):
    z = zipfile.ZipFile(io.BytesIO(body))
    shared = re.findall(r'<si>(?:.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8', 'replace'), re.S) \
        if 'xl/sharedStrings.xml' in z.namelist() else []
    shared = [re.sub(r'<[^>]+>', '', x) for x in shared]
    sheet = z.read('xl/worksheets/sheet1.xml').decode('utf-8', 'replace')
    out = []
    for r in re.findall(r'<row[^>]*>(.*?)</row>', sheet, re.S):
        cells = []
        for c in re.findall(r'<c\b([^>]*)>(.*?)</c>', r, re.S):
            attrs, inner = c
            v = re.search(r'<v>(.*?)</v>', inner, re.S)
            v = v.group(1) if v else ''
            if ' t="s"' in attrs and v.isdigit():
                v = shared[int(v)] if int(v) < len(shared) else v
            elif ' t="inlineStr"' in attrs:
                m = re.search(r'<t[^>]*>(.*?)</t>', inner, re.S)
                v = m.group(1) if m else ''
            cells.append(v)
        out.append(cells)
    return out


def ssga_holdings(ticker):
    url = ('https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/'
           'holdings-daily-us-en-%s.xlsx' % ticker.lower())
    body = fetch(url)
    if not body:
        return None, [], None
    try:
        rows = _xlsx_rows(body)
    except Exception:
        return None, [], None
    hdr_i = None
    for i, r in enumerate(rows[:20]):
        low = [str(x).strip().lower() for x in r]
        if 'name' in low and any('weight' in x for x in low):
            hdr_i = i
            cols = low
            break
    if hdr_i is None:
        return None, [], None
    ni = cols.index('name')
    wi = next(i for i, x in enumerate(cols) if 'weight' in x)
    ti = next((i for i, x in enumerate(cols) if x in ('ticker', 'symbol')), None)
    as_of = ''
    for r in rows[:hdr_i]:
        for c in r:
            m = re.search(r'(\d{4}-\d{2}-\d{2})|([A-Z][a-z]{2} \d{1,2}, \d{4})', str(c))
            if m:
                as_of = m.group(0)
                break
    out = []
    for r in rows[hdr_i + 1:]:
        if len(r) <= max(ni, wi):
            continue
        try:
            pct = float(str(r[wi]).replace('%', '').strip())
        except ValueError:
            continue
        if pct <= 0 or not str(r[ni]).strip():
            continue
        out.append(dict(name=re.sub(r'\s+', ' ', str(r[ni])).strip(), pct=round(pct, 4),
                        usd=None, isin=None, cusip=None,
                        ticker=(str(r[ti]).strip().upper() if ti is not None and len(r) > ti else None)))
    out.sort(key=lambda r: -r['pct'])
    return as_of[:10], out, 'State Street daily holdings'


# ---------------------------------------------------------------- price history and returns

def history(sym, years=6):
    frm = (TODAY - dt.timedelta(days=int(365.25 * years))).isoformat()
    rows = []
    for cls in ('etf', 'stocks'):          # a few listings answer only for one of the two
        url = ('https://api.nasdaq.com/api/quote/%s/historical?assetclass=%s&fromdate=%s&todate=%s&limit=9999'
               % (sym, cls, frm, TODAY.isoformat()))
        b = fetch(url, NASDAQ_HDR)
        if not b:
            continue
        try:
            rows = (((json.loads(b).get('data') or {}).get('tradesTable') or {}).get('rows')) or []
        except Exception:
            rows = []
        if rows:
            break
    if not rows:
        return []
    out = []
    for x in rows:
        try:
            m, d, y = x['date'].split('/')
            out.append(['%s-%s-%s' % (y, m, d), float(str(x['close']).replace('$', '').replace(',', ''))])
        except Exception:
            continue
    return sorted(out)


def last_price(sym):
    """Just the latest price, for a listing whose history endpoint returns nothing (SPLG)."""
    for cls in ('etf', 'stocks'):
        b = fetch('https://api.nasdaq.com/api/quote/%s/info?assetclass=%s' % (sym, cls), NASDAQ_HDR)
        if not b:
            continue
        try:
            d = ((json.loads(b).get('data') or {}).get('primaryData') or {})
            v = str(d.get('lastSalePrice') or '').replace('$', '').replace(',', '')
            if v:
                return float(v)
        except Exception:
            continue
    return None


def ret_over(series, days):
    """Price return over a window, as a fraction. None when the history does not reach back."""
    if len(series) < 2:
        return None
    end_d, end_p = series[-1]
    target = (dt.date.fromisoformat(end_d) - dt.timedelta(days=days)).isoformat()
    older = [x for x in series if x[0] <= target]
    if not older:
        return None
    start_p = older[-1][1]
    if not start_p:
        return None
    return round(end_p / start_p - 1, 4)


def cagr_years(series):
    """How many years of price history we actually have, which the average return has to be labelled with."""
    if len(series) < 2:
        return None
    d0 = dt.date.fromisoformat(series[0][0])
    d1 = dt.date.fromisoformat(series[-1][0])
    y = (d1 - d0).days / 365.25
    return round(y, 1) if y >= 1 else None


def cagr(series):
    """Average return a year over the history we hold — not since the fund launched, and labelled so."""
    y = cagr_years(series)
    if not y or not series[0][1] or not series[-1][1]:
        return None
    try:
        return round((series[-1][1] / series[0][1]) ** (1 / y) - 1, 4)
    except Exception:
        return None


def monthly(series):
    """One close per month, for a chart that does not need 1,500 points."""
    seen, out = set(), []
    for d, p in series:
        k = d[:7]
        if k not in seen:
            seen.add(k)
            out.append([d, round(p, 2)])
    if series and (not out or out[-1][0] != series[-1][0]):
        out.append([series[-1][0], round(series[-1][1], 2)])
    return out


# ---------------------------------------------------------------- weighted fundamentals

def weighted(holdings, by_name, by_ticker):
    """Match each holding to a company we cover and roll the fund's figures up from ours."""
    matched, cov = [], 0.0
    for h in holdings:
        t = h.get('ticker')
        if t and t not in by_ticker:
            t = None
        if not t:
            ks = keys(h['name'])
            t = next((by_name[k] for k in ks if k in by_name), None)
            if not t:
                sq = by_name.get('\x00squash') or {}
                t = next((sq[k.replace(' ', '')] for k in ks if k.replace(' ', '') in sq), None)
        h['t'] = t
        if t:
            cov += h['pct']
            matched.append((t, h['pct']))
    num_pe = den_pe = 0.0
    num_ps = den_ps = 0.0
    growth_n = growth_w = 0.0
    margin_n = margin_w = 0.0
    score_n = score_w = 0.0
    profitable_w = 0.0
    for t, w in matched:
        d = stock(t)
        if not d:
            continue
        r = d.get('ratios') or {}
        l = (d.get('annual') or [{}])[-1]
        sc = (d.get('scores') or {}).get('total')
        pe, ps = r.get('pe'), r.get('ps')
        if pe and pe > 0:
            num_pe += w
            den_pe += w / pe
            profitable_w += w
        if ps and ps > 0:
            num_ps += w
            den_ps += w / ps
        g = l.get('revenue_growth')
        if g is not None and -1 < g < 5:
            growth_n += w * g
            growth_w += w
        nm = l.get('net_margin')
        if nm is not None and -2 < nm < 1:
            margin_n += w * nm
            margin_w += w
        if sc is not None:
            score_n += w * sc
            score_w += w
    f = lambda n, d_, nd=4: round(n / d_, nd) if d_ else None
    return dict(
        covered_pct=round(cov, 2),
        covered_n=len([1 for h in holdings if h.get('t')]),
        holdings_n=len(holdings),
        pe=f(num_pe, den_pe, 2),
        ps=f(num_ps, den_ps, 2),
        revenue_growth=f(growth_n, growth_w),
        net_margin=f(margin_n, margin_w),
        score=f(score_n, score_w, 2),
        profitable_weight=round(profitable_w, 2),
    )


# ---------------------------------------------------------------- per-fund build

def build_one(e, by_ticker, by_name, cache=None):
    t = e['t']
    hist = history(t)
    as_of, holds, src = (None, [], None)
    if t == 'SPY' or e['issuer'] == 'State Street':
        as_of, holds, src = ssga_holdings(t)
    if not holds and e.get('cik') and e.get('series'):
        as_of, holds, src = nport_holdings(e['cik'], e['series'], cache)
    rec = dict(
        t=t, name=e['name'], issuer=e['issuer'], index=e['index'], since=e['since'],
        cls=e['cls'], focus=e['focus'], idea=e['idea'], strategy=e['strategy'], ucits=e['ucits'],
        price=(hist[-1][1] if hist else last_price(t)),
        price_date=(hist[-1][0] if hist else None),
        chart=monthly(hist),
        returns=dict(m1=ret_over(hist, 30), m3=ret_over(hist, 91), ytd=None,
                     y1=ret_over(hist, 365), y3=ret_over(hist, 1095), y5=ret_over(hist, 1826)),
        cagr=cagr(hist), cagr_years=cagr_years(hist),
        holdings_as_of=as_of, holdings_source=src,
        built=TODAY.isoformat(),
    )
    if hist:
        jan = [x for x in hist if x[0] >= '%d-01-01' % TODAY.year]
        prev = [x for x in hist if x[0] < '%d-01-01' % TODAY.year]
        if jan and prev and prev[-1][1]:
            rec['returns']['ytd'] = round(jan[-1][1] / prev[-1][1] - 1, 4)
    if holds:
        w = weighted(holds, by_name, by_ticker)                 # sets h['t'] on each holding
        if e['cls'] != 'equity':
            # the match is only meaningful for shares: a bond fund's holdings are that company's
            # debt, and rolling our equity figures onto it would invent a P/E that cannot exist
            w = dict(holdings_n=w['holdings_n'], covered_pct=None, covered_n=None, not_equity=True)
        elif (w.get('covered_pct') or 0) < MIN_COVER:
            w = dict(holdings_n=w['holdings_n'], covered_pct=w['covered_pct'],
                     covered_n=w['covered_n'], thin=True)
        rec['weighted'] = w

    # A fund's historical P/E cannot be fetched from anywhere: it depends on what the fund held at
    # the time, and nobody publishes that series. So we start one. Each day's figure is appended, and
    # after a few months the pages can show where today sits against the fund's own range.
    if (rec.get('weighted') or {}).get('pe'):
        hp = os.path.join(OUT, 'history')
        os.makedirs(hp, exist_ok=True)
        hf = os.path.join(hp, t + '.json')
        try:
            ser = json.load(open(hf))
        except Exception:
            ser = []
        ser = [x for x in ser if x[0] != TODAY.isoformat()]
        ser.append([TODAY.isoformat(), rec['weighted']['pe'], rec.get('price')])
        ser = sorted(ser)[-2000:]
        json.dump(ser, open(hf, 'w'), separators=(',', ':'))
        rec['pe_history_n'] = len(ser)
        rec['pe_since'] = ser[0][0]
        pes = [x[1] for x in ser if x[1]]
        if len(pes) >= 20:      # about a month of trading days; an 'average' of three is not one
            rec['pe_avg'] = round(sum(pes) / len(pes), 2)
            rec['pe_hi'] = max(pes)
            rec['pe_lo'] = min(pes)
    rec['holdings'] = [{k: v for k, v in h.items() if k in ('name', 'pct', 't')} for h in holds[:60]]
    return rec


def main():
    only = set(a.upper() for a in sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    by_ticker, by_name = load_universe()

    # the SEC's own fund map: ticker -> trust CIK and fund series
    mf = {}
    b = fetch('https://www.sec.gov/files/company_tickers_mf.json', SEC_HDR)
    if b:
        d = json.loads(b)
        ix = {k: d['fields'].index(k) for k in d['fields']}
        for row in d['data']:
            mf.setdefault(str(row[ix['symbol']]).upper(),
                          dict(cik=row[ix['cik']], series=row[ix['seriesId']]))
    print('SEC fund map:', len(mf), 'tickers')

    cache = _cache()
    index, failed = [], []
    for e in etf_list.ETFS:
        if only and e['t'] not in only:
            continue
        e = dict(e, **(mf.get(e['t']) or {}))
        try:
            rec = build_one(e, by_ticker, by_name, cache)
        except Exception as ex:
            print('  %-5s FAILED %s: %s' % (e['t'], type(ex).__name__, str(ex)[:120]))
            failed.append(e['t'])
            continue
        w = rec.get('weighted') or {}
        print('  %-5s price %-9s 1y %-8s holdings %-5s covered %-6s pe %-7s src %s'
              % (e['t'], rec['price'], rec['returns']['y1'], w.get('holdings_n', 0),
                 w.get('covered_pct'), w.get('pe'), rec['holdings_source']))
        if not rec['holdings'] and e['cls'] not in ('commodity', 'crypto'):
            failed.append(e['t'])
        json.dump(rec, open(os.path.join(OUT, e['t'] + '.json'), 'w'), separators=(',', ':'))
        index.append(dict(t=e['t'], name=e['name'], issuer=e['issuer'], cls=e['cls'],
                          focus=e['focus'], idea=e['idea'], price=rec['price'],
                          y1=rec['returns']['y1'], y3=rec['returns']['y3'], ytd=rec['returns']['ytd'],
                          cagr=rec.get('cagr'), cagr_years=rec.get('cagr_years'),
                          covered=(rec.get('weighted') or {}).get('covered_pct'),
                          pe=(rec.get('weighted') or {}).get('pe'),
                          pe_avg=rec.get('pe_avg'), pe_n=rec.get('pe_history_n'), pe_since=rec.get('pe_since'),
                          holdings_n=(rec.get('weighted') or {}).get('holdings_n')))
    json.dump(cache, open(CACHE, 'w'), separators=(',', ':'))
    json.dump(dict(built=TODAY.isoformat(), etfs=index),
              open(os.path.join(OUT, 'index.json'), 'w'), separators=(',', ':'))
    print('wrote', len(index), 'ETFs to', OUT)
    if failed:
        print('NO HOLDINGS for:', ' '.join(failed))
    return 0


if __name__ == '__main__':
    sys.exit(main())
