#!/usr/bin/env python3
"""Gold & silver page data (web/gold.html). Dollars only; every source is outside Iran and free/public.

Sources
  prices   Yahoo chart API: GC=F (COMEX gold futures), SI=F (silver), ^GSPC (S&P 500), BTC-USD
  rates    US Treasury daily par real / nominal yield curves (10-year), dollar index DX-Y.NYB (Yahoo),
           CPI-U from the public BLS API (inflation-adjusted line); FRED only as a fallback (slow from GitHub runners)
  COT      CFTC public reporting (disaggregated futures): managed-money long/short, gold 088691, silver 084691
  calendar federalreserve.gov FOMC calendar (bls.gov blocks automated reads of its schedule pages)

Output gold.json (published to the orphan branch "gold" by .github/workflows/gold.yml):
  as_of, spot{gold,silver,spx,btc: {p, chg, prev, t}}, ratio{now, avg20, min20, max20},
  d{gold,silver: [[date, close, ma50, ma200], ...]  last ~2 years daily}
  w{gold,silver,spx,btc: [[date, close], ...]       weekly, 20 years}
  real{gold: [[date, close in today's dollars], ...] weekly, 20 years}
  cmp{gold,silver,spx,btc: {"1": r, "5": r, "10": r, "20": r}}   total price change, fraction
  drv{ry, y10, dxy: {v, d, w1, y1, s: [[date, v], ...] weekly 2y}}
  cot{gold,silver: [{d, l, s, n, oi}, ...] last 52 weeks, newest last}
  cal{fomc: "YYYY-MM-DD"}  next FOMC decision day
  note  one Farsi sentence built from today's numbers (rule-based, no buy/sell language)
"""
import csv, io, json, os, re, signal, sys, time, datetime as dt, urllib.request, urllib.parse

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
OUT = os.environ.get('OUT', os.path.join(ROOT, 'gold.json'))
LOG = []
TODAY = dt.date.today()


def get(url, timeout=20, accept='application/json, text/csv, text/html, */*'):
    last = None
    for a in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept, 'Accept-Language': 'en-US,en;q=0.9'})
            return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'replace')
        except Slow:
            raise
        except Exception as e:
            last = e
            time.sleep(2 * (a + 1))
    raise last


# ------------------------------------------------------------------ prices
def yahoo(sym, rng=None, interval='1d'):
    """rng=None: daily bars for the last 21 years (period1/period2 keeps Yahoo from thinning long ranges)."""
    if rng:
        q = 'range=%s' % rng
    else:
        now = int(time.time())
        q = 'period1=%d&period2=%d' % (now - int(21 * 365.25 * 86400), now)
    url = ('https://query2.finance.yahoo.com/v8/finance/chart/%s?%s&interval=%s&includeAdjustedClose=false'
           % (urllib.parse.quote(sym), q, interval))
    j = json.loads(get(url))
    r = ((j.get('chart') or {}).get('result') or [None])[0] or {}
    meta = r.get('meta') or {}
    ts = r.get('timestamp') or []
    cl = (((r.get('indicators') or {}).get('quote') or [{}])[0]).get('close') or []
    rows = {}
    for a, c in zip(ts, cl):
        if c is not None and c > 0:
            rows[dt.datetime.utcfromtimestamp(a).date().isoformat()] = round(float(c), 4)
    return sorted(rows.items()), meta


def spot(sym):
    """Last price, change vs previous close, time. 5-minute bars of the last 2 days."""
    # range=1d: chartPreviousClose is the previous session's close, regularMarketPrice the latest trade
    rows, meta = yahoo(sym, '1d', '5m')
    p = meta.get('regularMarketPrice') or (rows[-1][1] if rows else None)
    prev = meta.get('chartPreviousClose') or meta.get('previousClose')
    t = meta.get('regularMarketTime')
    return {'p': round(p, 2) if p else None, 'prev': round(prev, 2) if prev else None,
            'chg': round((p / prev - 1) * 100, 2) if p and prev else None,
            't': dt.datetime.utcfromtimestamp(t).strftime('%Y-%m-%dT%H:%M:%SZ') if t else None}


def ma(vals, n):
    out, s = [], 0.0
    for i, v in enumerate(vals):
        s += v
        if i >= n:
            s -= vals[i - n]
        out.append(round(s / n, 2) if i >= n - 1 else None)
    return out


def weekly(rows):
    """Last close of each ISO week."""
    wk = {}
    for d, c in rows:
        y, w, _ = dt.date.fromisoformat(d).isocalendar()
        wk[(y, w)] = (d, c)
    return [list(v) for _, v in sorted(wk.items())]


def ret(rows, years):
    if not rows:
        return None
    target = (dt.date.fromisoformat(rows[-1][0]) - dt.timedelta(days=round(365.25 * years))).isoformat()
    old = [c for d, c in rows if d <= target]
    if not old or rows[0][0] > (dt.date.fromisoformat(target) + dt.timedelta(days=20)).isoformat():
        return None  # history too short
    return round(rows[-1][1] / old[-1] - 1, 4)


# ------------------------------------------------------------------ FRED
def fred(series):
    txt = get('https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + series, accept='text/csv')
    rows = []
    for r in csv.reader(io.StringIO(txt)):
        if len(r) < 2 or not re.match(r'\d{4}-\d\d-\d\d', r[0]):
            continue
        try:
            rows.append([r[0], float(r[1])])
        except ValueError:
            pass
    return rows


def treasury(kind, col='10 YR'):
    """US Treasury daily par yield curves (public domain). kind: daily_treasury_real_yield_curve | daily_treasury_yield_curve."""
    rows = []
    for y in range(TODAY.year - 2, TODAY.year + 1):
        url = ('https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/%d/all'
               '?type=%s&field_tdr_date_value=%d&page&_format=csv' % (y, kind, y))
        rd = csv.DictReader(io.StringIO(get(url, accept='text/csv')))
        for r in rd:
            try:
                rows.append([dt.datetime.strptime(r['Date'], '%m/%d/%Y').date().isoformat(), float(r[col])])
            except (KeyError, ValueError, TypeError):
                pass
    return sorted(rows)


def yrows(sym):
    return [[d, c] for d, c in yahoo(sym)[0]]


def bls_cpi():
    """CPI-U all items (CUUR0000SA0) monthly, 21 years, from the public BLS API (no key, 10 years per call)."""
    rows = []
    for a in range(TODAY.year - 20, TODAY.year + 1, 10):
        body = json.dumps({'seriesid': ['CUUR0000SA0'], 'startyear': str(a), 'endyear': str(min(a + 9, TODAY.year))}).encode()
        req = urllib.request.Request('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=body,
                                     headers={'Content-Type': 'application/json', 'User-Agent': UA})
        j = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        for r in ((j.get('Results') or {}).get('series') or [{}])[0].get('data') or []:
            if r.get('period', '').startswith('M') and r['period'] != 'M13':
                try:
                    rows.append(['%s-%s-01' % (r['year'], r['period'][1:]), float(r['value'])])
                except ValueError:
                    pass
    if len(rows) < 100:
        raise ValueError('BLS CPI: %d rows' % len(rows))
    return sorted(rows)


def driver(series, rows=None):
    rows = rows if rows is not None else fred(series)
    if not rows:
        return None
    last = rows[-1]

    def back(days):
        t = (dt.date.fromisoformat(last[0]) - dt.timedelta(days=days)).isoformat()
        old = [v for d, v in rows if d <= t]
        return round(last[1] - old[-1], 3) if old else None
    cut = (dt.date.fromisoformat(last[0]) - dt.timedelta(days=730)).isoformat()
    return {'v': round(last[1], 3), 'd': last[0], 'w1': back(7), 'y1': back(365),
            's': [[d, round(v, 3)] for d, v in weekly([x for x in rows if x[0] >= cut])]}


# ------------------------------------------------------------------ CFTC
def cot(code):
    q = urllib.parse.urlencode({'cftc_contract_market_code': code, '$order': 'report_date_as_yyyy_mm_dd DESC', '$limit': 52})
    j = json.loads(get('https://publicreporting.cftc.gov/resource/72hh-3qpy.json?' + q))
    out = []
    for r in j:
        try:
            l, s = int(float(r['m_money_positions_long_all'])), int(float(r['m_money_positions_short_all']))
            out.append({'d': r['report_date_as_yyyy_mm_dd'][:10], 'l': l, 's': s, 'n': l - s, 'oi': int(float(r['open_interest_all']))})
        except (KeyError, ValueError):
            pass
    return sorted(out, key=lambda x: x['d'])


# ------------------------------------------------------------------ calendar
MON = {m: i + 1 for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                                        'october', 'november', 'december'])}


def next_fomc():
    html = get('https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm', accept='text/html')
    days = []
    for yb in re.finditer(r'(\d{4}) FOMC Meetings(.*?)(?=\d{4} FOMC Meetings|$)', html, re.S):
        y = int(yb.group(1))
        for m in re.finditer(r'fomc-meeting__month[^>]*>\s*<strong>([A-Za-z/]+)</strong>.*?fomc-meeting__date[^>]*>\s*([\d\-–]+)',
                             yb.group(2), re.S):
            mon = m.group(1).split('/')[-1].lower()
            dd = re.findall(r'\d+', m.group(2))
            if mon in MON and dd:
                # decision day = last day of the meeting; month of the last day when the meeting spans two months
                try:
                    days.append(dt.date(y, MON[mon], int(dd[-1])))
                except ValueError:
                    pass
    fut = sorted(d for d in days if d >= TODAY)
    return fut[0].isoformat() if fut else None


def next_bls(page):
    html = get('https://www.bls.gov/schedule/news_release/%s.htm' % page, accept='text/html')
    out = []
    for m in re.finditer(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),\s+(\d{4})', html):
        try:
            d = dt.datetime.strptime('%s %s %s' % (m.group(1), m.group(2), m.group(3)), '%b %d %Y').date()
        except ValueError:
            continue
        if d >= TODAY:
            out.append(d)
    return min(out).isoformat() if out else None


# ------------------------------------------------------------------ Farsi note
FA = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')


def fa(x, nd=1):
    return ('%.*f' % (nd, abs(x))).translate(FA)


def note(sp, drv):
    g, s = sp.get('gold') or {}, sp.get('silver') or {}
    if g.get('chg') is None:
        return None
    c = g['chg']
    if abs(c) < 0.15:
        head = 'قیمت طلا امروز تقریباً بدون تغییر بوده'
    else:
        head = 'قیمت طلا امروز %s٪ %s' % (fa(c), 'بالا رفته' if c > 0 else 'پایین آمده')
    parts = []
    ry = (drv or {}).get('ry') or {}
    dx = (drv or {}).get('dxy') or {}
    if ry.get('w1') is not None and abs(ry['w1']) >= 0.05:
        parts.append('بازده واقعی اوراق ۱۰ ساله‌ی آمریکا در هفته‌ی گذشته %s واحد درصد %s' % (fa(ry['w1'], 2), 'بالا رفته' if ry['w1'] > 0 else 'پایین آمده'))
    if dx.get('w1') is not None and dx.get('v'):
        pct = dx['w1'] / (dx['v'] - dx['w1']) * 100
        if abs(pct) >= 0.3:
            parts.append('شاخص دلار %s٪ %s' % (fa(pct), 'قوی‌تر شده' if pct > 0 else 'ضعیف‌تر شده'))
    tail = ''
    if parts:
        tail = '؛ ' + ' و '.join(parts) + '. معمولاً بالا رفتن بازده واقعی و دلار قوی‌تر به ضرر طلاست و برعکس'
    if s.get('chg') is not None:
        tail += '. نقره هم %s٪ %s' % (fa(s['chg']), 'بالا رفته' if s['chg'] >= 0 else 'پایین آمده')
    return head + tail + '.'


# ------------------------------------------------------------------ main
class Slow(Exception):
    pass


def _alarm(*_):
    raise Slow('took over 75 s')


def safe(name, fn, *a):
    """Run one source; a slow or broken source is skipped (its block is hidden on the page), never blocks the rest."""
    t0 = time.time()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(75)
    try:
        v = fn(*a)
        LOG.append('%s ok %.0fs' % (name, time.time() - t0))
        return v
    except Exception as e:
        LOG.append('%s FAILED %s' % (name, repr(e)[:120]))
        return None
    finally:
        signal.alarm(0)
        print(LOG[-1], flush=True)


def main():
    out = {'as_of': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
    syms = {'gold': 'GC=F', 'silver': 'SI=F', 'spx': '^GSPC', 'btc': 'BTC-USD'}
    hist = {k: (safe('hist ' + k, yahoo, s) or [[], {}])[0] for k, s in syms.items()}
    LOG.append('rows ' + ' '.join('%s=%d' % (k, len(v)) for k, v in hist.items()))
    if len(hist['gold']) < 500 or len(hist['silver']) < 500:
        print('\n'.join(LOG)); sys.exit('gold/silver history missing')
    out['spot'] = {k: safe('spot ' + k, spot, s) for k, s in syms.items()}

    # daily last ~2 years with moving averages
    out['d'] = {}
    for k in ('gold', 'silver'):
        rows = hist[k]
        vals = [c for _, c in rows]
        m50, m200 = ma(vals, 50), ma(vals, 200)
        cut = (TODAY - dt.timedelta(days=760)).isoformat()
        out['d'][k] = [[d, c, m50[i], m200[i]] for i, (d, c) in enumerate(rows) if d >= cut]
    cut20 = (TODAY - dt.timedelta(days=round(365.25 * 20) + 10)).isoformat()
    out['w'] = {k: weekly([r for r in hist[k] if r[0] >= cut20]) for k in syms}
    out['cmp'] = {k: {str(y): ret(hist[k], y) for y in (1, 5, 10, 20)} for k in syms}

    # gold / silver ratio, 20-year context
    sv = dict(hist['silver'])
    rat = [(d, c / sv[d]) for d, c in hist['gold'] if d >= cut20 and sv.get(d)]
    g, s = out['spot']['gold'] or {}, out['spot']['silver'] or {}
    if rat:
        rv = [r for _, r in rat]
        out['ratio'] = {'now': round(g['p'] / s['p'], 1) if g.get('p') and s.get('p') else round(rv[-1], 1),
                        'avg20': round(sum(rv) / len(rv), 1), 'min20': round(min(rv), 1), 'max20': round(max(rv), 1)}

    # inflation-adjusted gold (today's dollars)
    cpi = safe('cpi bls', bls_cpi) or safe('cpi fred', fred, 'CPIAUCSL') or []
    if cpi:
        cm = {d[:7]: v for d, v in cpi}
        last_cpi = cpi[-1][1]
        real = []
        for d, c in out['w']['gold']:
            v = cm.get(d[:7]) or cm.get(max((k for k in cm if k <= d[:7]), default=''), None)
            if v:
                real.append([d, round(c * last_cpi / v, 2)])
        out['real'] = {'gold': real, 'cpi_month': cpi[-1][0][:7]}

    ry = safe('treasury real', treasury, 'daily_treasury_real_yield_curve')
    y10 = safe('treasury nominal', treasury, 'daily_treasury_yield_curve')
    dxy = safe('dollar index', yrows, 'DX-Y.NYB')
    out['drv'] = {'ry': safe('drv ry', driver, 'DFII10', ry) if ry else None,
                  'y10': safe('drv y10', driver, 'DGS10', y10) if y10 else None,
                  'dxy': safe('drv dxy', driver, 'DXY', [r for r in dxy if r[0] >= (TODAY - dt.timedelta(days=800)).isoformat()]) if dxy else None}
    out['cot'] = {'gold': safe('cot gold', cot, '088691'), 'silver': safe('cot silver', cot, '084691')}
    out['cal'] = {'fomc': safe('fomc', next_fomc)}
    out['note'] = note(out['spot'], out['drv'])
    out['log'] = [x for x in LOG if 'FAILED' in x]

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print('gold', g, '| silver', s, '| size', os.path.getsize(OUT))


if __name__ == '__main__':
    main()
