#!/usr/bin/env python3
"""Per-stock extras for the stock analysis page.

  python extras.py news     -> news/<T>.json     latest headlines with links (Yahoo Finance RSS); we only link, never copy articles
  python extras.py insider  -> insider/<T>.json  insider (Form 4) activity: 3/12-month summary + latest transactions (Nasdaq)

Each is published by .github/workflows/extras.yml to its own orphan branch (`news`, `insider`), one commit, no history growth.
Optional 2nd arg N = only the first N tickers (test run).
"""
import json, os, sys, time, re, html, datetime as dt, email.utils, urllib.request, urllib.parse, concurrent.futures as cf
from xml.etree import ElementTree as ET

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
STOCKS = os.path.join(ROOT, 'data', 'stocks')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
NASDAQ_HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.9',
              'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}


def get(url, headers, timeout=30, tries=4):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 400):
                return None
            time.sleep(2 * (a + 1) + (5 if e.code == 429 else 0))
        except Exception:
            time.sleep(2 * (a + 1))
    return None


def tickers(limit):
    ts = sorted(f[:-5] for f in os.listdir(STOCKS) if f.endswith('.json'))
    # only listed stocks with a market value (the ones that have pages / are searched)
    out = []
    for t in ts:
        try:
            if (json.load(open(os.path.join(STOCKS, t + '.json'))).get('market') or {}).get('mcap'):
                out.append(t)
        except Exception:
            pass
    return out[:limit] if limit else out


def num(s):
    if s in (None, '', 'N/A', '--'):
        return None
    s = str(s).replace('$', '').replace(',', '').strip()
    neg = s.startswith('(') and s.endswith(')')
    try:
        v = float(s.strip('()'))
    except ValueError:
        return None
    return -v if neg else v


# ------------------------------------------------------------------ news
NAMES = {}
SUFFIX = re.compile(r'[,.]?\s+(inc|incorporated|corp|corporation|co|com|company|ltd|limited|plc|holdings?|group|n\.?v|s\.?a|ag|se|lp|l\.?p|llc|class [a-c]|common stock|ordinary shares|adr|the)\.?$', re.I)


def clean_name(n):
    n = re.sub(r'\s+', ' ', (n or '').replace('&amp;', '&')).strip(' .,')
    for _ in range(4):
        m = SUFFIX.sub('', n).strip(' .,')
        if m == n:
            break
        n = m
    n = re.sub(r'^the\s+', '', n, flags=re.I)
    if n.isupper() and not (len(n.split()) == 1 and len(n) <= 5):
        n = n.title()
    return n


def gnews_one(t):
    name = clean_name(NAMES.get(t, ''))
    q = ('"%s" stock' % name) if len(name) >= 3 else ('%s stock' % t)
    raw = get('https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q + ' when:14d', 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}),
              {'User-Agent': UA, 'Accept': 'application/rss+xml, application/xml'})
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None
    items, seen = [], set()
    for it in root.iter('item'):
        title = html.unescape((it.findtext('title') or '').strip())
        link = (it.findtext('link') or '').strip()
        src = it.find('source')
        pub = (src.text or '').strip() if src is not None else ''
        if pub and title.endswith(' - ' + pub):
            title = title[: -len(pub) - 3]
        if not title or not link.startswith('http') or title.lower() in seen:
            continue
        try:
            d = email.utils.parsedate_to_datetime(it.findtext('pubDate') or '')
        except Exception:
            d = None
        seen.add(title.lower())
        host = urllib.parse.urlparse(src.get('url')).netloc.replace('www.', '') if (src is not None and src.get('url')) else ''
        items.append({'h': title[:220], 'u': link, 's': pub or host, 'd': d.strftime('%Y-%m-%dT%H:%M:%SZ') if d else None})
    items.sort(key=lambda x: x['d'] or '', reverse=True)
    return items[:10] or None


YSTAT = {'try': 0, 'ok': 0}


def news_one(t):
    # Yahoo's feed is tagged by ticker (best quality) but often blocks cloud servers:
    # stop trying it after 25 attempts without a single success, then use Google News only.
    if not (YSTAT['try'] >= 25 and YSTAT['ok'] == 0):
        YSTAT['try'] += 1
        y = yahoo_one(t)
        if y:
            YSTAT['ok'] += 1
            return t, y
    return t, gnews_one(t)


def yahoo_one(t):
    raw = get('https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US' % urllib.parse.quote(t.replace('-', '.')),
              {'User-Agent': UA, 'Accept': 'application/rss+xml, application/xml, text/xml'}, tries=1, timeout=15)
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None
    cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=45)
    items, seen = [], set()
    for it in root.iter('item'):
        title = html.unescape((it.findtext('title') or '').strip())
        link = (it.findtext('link') or '').strip()
        if not title or not link.startswith('http') or title.lower() in seen:
            continue
        try:
            d = email.utils.parsedate_to_datetime(it.findtext('pubDate') or '')
        except Exception:
            d = None
        if d and d < cut:
            continue
        link = re.sub(r'[?&]\.tsrc=rss$', '', link)
        host = urllib.parse.urlparse(link).netloc.replace('www.', '')
        seen.add(title.lower())
        items.append({'h': title[:220], 'u': link, 's': host, 'd': d.strftime('%Y-%m-%dT%H:%M:%SZ') if d else None})
        if len(items) >= 10:
            break
    return items or None


# ------------------------------------------------------------------ insider
def insider_one(t):
    url = ('https://api.nasdaq.com/api/company/%s/insider-trades?limit=15&type=ALL&sortColumn=lastDate&sortOrder=DESC'
           % urllib.parse.quote(t.replace('-', '.')))
    raw = get(url, NASDAQ_HDR)
    if not raw:
        return t, None
    try:
        d = json.loads(raw).get('data') or {}
    except Exception:
        return t, None

    def table(key):
        out = {}
        for r in ((d.get(key) or {}).get('rows') or []):
            out[(r.get('insiderTrade') or '').lower()] = (num(r.get('months3')), num(r.get('months12')))
        return out

    n, s = table('numberOfTrades'), table('numberOfSharesTraded')
    rows = []
    for r in (((d.get('transactionTable') or {}).get('table') or {}).get('rows') or []):
        try:
            m, dd, yy = (r.get('lastDate') or '').split('/')
            date = '%04d-%02d-%02d' % (int(yy), int(m), int(dd))
        except Exception:
            date = None
        rows.append({'n': (r.get('insider') or '').title(), 'r': r.get('relation'), 'd': date, 'x': r.get('transactionType'),
                     'o': r.get('ownType'), 'q': num(r.get('sharesTraded')), 'p': num(r.get('lastPrice')), 'h': num(r.get('sharesHeld'))})
    g = lambda tb, k, i: (tb.get(k) or (None, None))[i]
    summ = {'buys3': g(n, 'number of open market buys', 0), 'buys12': g(n, 'number of open market buys', 1),
            'sells3': g(n, 'number of sells', 0), 'sells12': g(n, 'number of sells', 1),
            'bought3': g(s, 'number of shares bought', 0), 'bought12': g(s, 'number of shares bought', 1),
            'sold3': g(s, 'number of shares sold', 0), 'sold12': g(s, 'number of shares sold', 1),
            'net3': g(s, 'net activity', 0), 'net12': g(s, 'net activity', 1),
            'total': num(((d.get('transactionTable') or {}).get('totalRecords')))}
    if not rows and not any(v for v in summ.values()):
        return t, None
    return t, {'sum': summ, 'rows': rows}


# ------------------------------------------------------------------ company profile (official description)
def profile_one(t):
    raw = get('https://api.nasdaq.com/api/company/%s/company-profile' % urllib.parse.quote(t.replace('-', '.')), NASDAQ_HDR)
    if not raw:
        return t, None
    try:
        d = json.loads(raw).get('data') or {}
    except Exception:
        return t, None
    val = lambda k: (((d.get(k) or {}).get('value')) or '').strip()
    desc = re.sub(r'\s+', ' ', html.unescape(val('CompanyDescription')))
    if len(desc) < 40:
        return t, None
    return t, {'desc': desc[:4000], 'web': val('CompanyUrl'), 'sector': val('Sector'), 'industry': val('Industry'),
               'country': val('Region') or val('Country'), 'employees': val('Employees') or None}


# ------------------------------------------------------------------ insider fallback: SEC EDGAR Form 4 (when Nasdaq has nothing)
LOG = []
SEC_UA = os.environ.get('SEC_USER_AGENT', 'Reza Hajilou mreza.hajilou@gmail.com')
SEC_HDR = {'User-Agent': SEC_UA, 'Accept': 'application/json, text/xml, */*'}
# Form 4 transaction codes -> the labels Nasdaq uses (the page already knows how to colour / translate those)
F4_CODE = {'P': 'Buy', 'S': 'Sell', 'M': 'Option Execute', 'A': 'Acquisition (Non Open Market)', 'F': 'Disposition (Non Open Market)',
           'G': 'Gift', 'D': 'Disposition (Non Open Market)', 'C': 'Acquisition (Non Open Market)', 'J': 'Disposition (Non Open Market)',
           'W': 'Acquisition (Non Open Market)', 'I': 'Disposition (Non Open Market)', 'X': 'Option Execute'}


def _x(el, path):
    e = el.find(path)
    return (e.text or '').strip() if e is not None and e.text else ''


def sec_form4(cik, max_docs=40):
    """Latest Form 4 filings for a CIK, parsed from the XML on EDGAR. Returns the same shape as insider_one()."""
    try:
        sub = json.loads(get('https://data.sec.gov/submissions/CIK%010d.json' % int(cik), SEC_HDR, timeout=30, tries=2) or b'null')
    except Exception:
        sub = None
    if not sub:
        LOG.append('sec submissions failed cik %s' % cik)
        return None
    rec = sub.get('filings', {}).get('recent', {})
    forms, accs, docs, dates = rec.get('form', []), rec.get('accessionNumber', []), rec.get('primaryDocument', []), rec.get('filingDate', [])
    today = dt.date.today()
    cut12 = (today - dt.timedelta(days=365)).isoformat()
    f4 = [(dates[i], accs[i], docs[i]) for i in range(len(forms)) if forms[i] in ('4', '4/A') and dates[i] >= cut12]
    if not f4:
        return None
    rows, nb3 = [], 0
    cut3 = (today - dt.timedelta(days=91)).isoformat()
    summ = {'buys3': 0, 'buys12': 0, 'sells3': 0, 'sells12': 0, 'bought3': 0, 'bought12': 0, 'sold3': 0, 'sold12': 0, 'net3': 0, 'net12': 0,
            'total': len(f4)}
    for fd, acc, doc in f4[:max_docs]:
        if not doc:
            continue
        # primaryDocument is the XSL-rendered path ("xslF345X05/wk-form4_....xml"); the raw XML is the file name alone
        url = 'https://www.sec.gov/Archives/edgar/data/%d/%s/%s' % (int(cik), acc.replace('-', ''), doc.split('/')[-1])
        raw = get(url, SEC_HDR, timeout=30, tries=2)
        time.sleep(0.12)   # SEC fair-use: < 10 requests / second
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
        except Exception:
            continue
        owner = root.find('reportingOwner')
        name = _x(owner, 'reportingOwnerId/rptOwnerName') if owner is not None else ''
        rel = ''
        if owner is not None:
            r = owner.find('reportingOwnerRelationship')
            if r is not None:
                if _x(r, 'isTenPercentOwner') in ('1', 'true'):
                    rel = 'Beneficial Owner (10% or more)'
                elif _x(r, 'isDirector') in ('1', 'true'):
                    rel = 'Director'
                elif _x(r, 'isOfficer') in ('1', 'true'):
                    rel = _x(r, 'officerTitle') or 'Officer'
                else:
                    rel = 'Other'
        # "Smith John A" (SEC order) -> "John A Smith" style is not reliable; keep SEC order, title-cased like Nasdaq
        name = ' '.join(w.capitalize() if w.isupper() or w.islower() else w for w in name.split())
        for tr in root.findall('nonDerivativeTable/nonDerivativeTransaction'):
            code = _x(tr, 'transactionCoding/transactionCode')
            date = _x(tr, 'transactionDate/value') or fd
            q = num(_x(tr, 'transactionAmounts/transactionShares/value'))
            pr = num(_x(tr, 'transactionAmounts/transactionPricePerShare/value'))
            ad = _x(tr, 'transactionAmounts/transactionAcquiredDisposedCode/value')
            held = num(_x(tr, 'postTransactionAmounts/sharesOwnedFollowingTransaction/value'))
            own = 'Direct' if _x(tr, 'ownershipNature/directOrIndirectOwnership/value') == 'D' else 'Indirect'
            label = F4_CODE.get(code) or ('Acquisition (Non Open Market)' if ad == 'A' else 'Disposition (Non Open Market)')
            if code == 'S' and tr.find('transactionCoding/footnoteId') is not None:
                pass  # Nasdaq calls 10b5-1 sales "Automatic Sell"; the XML does not say, so we keep "Sell"
            rows.append({'n': name, 'r': rel, 'd': date, 'x': label, 'o': own, 'q': q, 'p': pr, 'h': held})
            if q:
                if code == 'P':
                    summ['buys12'] += 1; summ['bought12'] += q
                    if date >= cut3:
                        summ['buys3'] += 1; summ['bought3'] += q
                elif code == 'S':
                    summ['sells12'] += 1; summ['sold12'] += q
                    if date >= cut3:
                        summ['sells3'] += 1; summ['sold3'] += q
    if not rows:
        LOG.append('sec form4 no rows cik %s (%d filings)' % (cik, len(f4)))
        return None
    summ['net3'] = summ['bought3'] - summ['sold3']
    summ['net12'] = summ['bought12'] - summ['sold12']
    rows.sort(key=lambda r: r['d'] or '', reverse=True)
    return {'sum': summ, 'rows': rows[:15], 'src': 'sec'}


def insider_fill(ts, got):
    """Second pass for tickers Nasdaq had nothing for: share-class sibling (GOOG <- GOOGL), foreign-filer marker, or SEC Form 4."""
    info = {}
    for t in ts:
        try:
            d = json.load(open(os.path.join(STOCKS, t + '.json')))
            info[t] = (d.get('cik'), bool(d.get('foreign')), (d.get('market') or {}).get('mcap') or 0)
        except Exception:
            info[t] = (None, False, 0)
    by_cik = {}
    for t, (c, _, m) in info.items():
        if c and t in got:
            by_cik.setdefault(c, []).append((m, t))
    out, sec_tries = {}, 0
    for t in ts:
        if t in got:
            continue
        c, foreign, m = info[t]
        sib = sorted(by_cik.get(c) or [], reverse=True)
        if sib:
            d = dict(got[sib[0][1]]); d['via'] = sib[0][1]
            out[t] = d
        elif foreign:
            out[t] = {'foreign': True}
        elif c and m >= 2e8 and sec_tries < 400:
            sec_tries += 1
            d = sec_form4(c)
            if d:
                out[t] = d
                by_cik.setdefault(c, []).append((m, t)); got[t] = d
    return out


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else ''
    arg = sys.argv[2] if len(sys.argv) > 2 else ''
    fn, workers = {'news': (news_one, 10), 'insider': (insider_one, 4), 'profile': (profile_one, 4)}[kind]
    out_dir = os.path.join(ROOT, kind)
    os.makedirs(out_dir, exist_ok=True)
    # 2nd arg: N = first N tickers, or an explicit comma-separated list (test runs)
    ts = [x.strip().upper() for x in arg.split(',') if x.strip()] if arg and not arg.isdigit() else tickers(int(arg) if arg else 0)
    if kind == 'news':
        for t in ts:
            try:
                NAMES[t] = json.load(open(os.path.join(STOCKS, t + '.json'))).get('name') or ''
            except Exception:
                pass
    ok = fail = 0
    t0 = time.time()
    got = {}

    def save(t, res):
        json.dump({'t': t, 'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
                   ('items' if kind == 'news' else 'data'): res},
                  open(os.path.join(out_dir, t + '.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (t, res) in enumerate(ex.map(fn, ts)):
            if res:
                save(t, res); got[t] = res; ok += 1
            else:
                fail += 1
            if i % 500 == 0:
                print('%s %d/%d ok=%d fail=%d %.0fs' % (kind, i, len(ts), ok, fail, time.time() - t0), flush=True)
    if kind == 'insider':
        extra = insider_fill(ts, got)
        for t, res in extra.items():
            save(t, res)
        ok += len(extra); fail -= len(extra)
        print('insider fallback: %d filled (%d via share class, %d foreign, %d from SEC)' % (
            len(extra), sum(1 for v in extra.values() if v.get('via')), sum(1 for v in extra.values() if v.get('foreign')),
            sum(1 for v in extra.values() if v.get('src') == 'sec')), flush=True)
    meta = {'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'ok': ok, 'fail': fail}
    if kind == 'insider':
        meta['missing'] = [t for t in ts if not os.path.exists(os.path.join(out_dir, t + '.json'))][:200]
        meta['log'] = LOG[-50:]
    json.dump(meta, open(os.path.join(out_dir, 'meta.json'), 'w'))
    print('::notice::%s done: ok %d, no data %d, %.0fs%s' % (kind, ok, fail, time.time() - t0,
          (' (yahoo ok %d of %d tries)' % (YSTAT['ok'], YSTAT['try'])) if kind == 'news' else ''))
    if ok < len(ts) * 0.2:
        sys.exit('too little data, keeping the previous branch')


if __name__ == '__main__':
    main()
