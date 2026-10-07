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


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else ''
    limit = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else 0
    fn, workers = {'news': (news_one, 10), 'insider': (insider_one, 4)}[kind]
    out_dir = os.path.join(ROOT, kind)
    os.makedirs(out_dir, exist_ok=True)
    ts = tickers(limit)
    if kind == 'news':
        for t in ts:
            try:
                NAMES[t] = json.load(open(os.path.join(STOCKS, t + '.json'))).get('name') or ''
            except Exception:
                pass
    ok = fail = 0
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (t, res) in enumerate(ex.map(fn, ts)):
            if res:
                json.dump({'t': t, 'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
                           ('items' if kind == 'news' else 'data'): res},
                          open(os.path.join(out_dir, t + '.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
                ok += 1
            else:
                fail += 1
            if i % 500 == 0:
                print('%s %d/%d ok=%d fail=%d %.0fs' % (kind, i, len(ts), ok, fail, time.time() - t0), flush=True)
    json.dump({'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'ok': ok, 'fail': fail},
              open(os.path.join(out_dir, 'meta.json'), 'w'))
    print('::notice::%s done: ok %d, no data %d, %.0fs%s' % (kind, ok, fail, time.time() - t0,
          (' (yahoo ok %d of %d tries)' % (YSTAT['ok'], YSTAT['try'])) if kind == 'news' else ''))
    if ok < len(ts) * 0.2:
        sys.exit('too little data, keeping the previous branch')


if __name__ == '__main__':
    main()
