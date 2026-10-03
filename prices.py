#!/usr/bin/env python3
"""Weekly price history (10y) for every ticker in data/index.json.

Output: prices/<TICKER>.json -> {"t":"AAPL","as_of":"2026-10-03","src":"stooq","w":[["2016-10-07",26.12],...]}
Source: Nasdaq chart API https://api.nasdaq.com/api/quote/<T>/chart (daily closes, downsampled to weekly)
Published on the orphan branch `prices` so the main repo never grows.
"""
import json, os, sys, time, io, zipfile, urllib.request, urllib.error, datetime as dt, concurrent.futures as cf

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
IDX = os.path.join(ROOT, 'data', 'index.json')
OUT = os.path.join(ROOT, 'prices')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
TODAY = dt.date.today()
CUTOFF = (TODAY - dt.timedelta(days=3660)).isoformat()


def get(url, timeout=60, headers=None):
    h = {'User-Agent': UA, 'Accept': '*/*'}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def weekly(rows):
    """rows: sorted [[date_iso, close]] daily -> last close of each ISO week."""
    out, wk = [], None
    for d, c in rows:
        y, w, _ = dt.date.fromisoformat(d).isocalendar()
        key = (y, w)
        if key == wk:
            out[-1] = [d, c]
        else:
            out.append([d, c]); wk = key
    return out


# ---------- source 1: stooq bulk ----------
def stooq_bulk(wanted):
    """Return {ticker: daily rows} for tickers present in the archive."""
    url = 'https://static.stooq.com/db/h/d_us_txt.zip'
    print('downloading', url, flush=True)
    data = get(url, timeout=900)
    print('zip bytes', len(data), flush=True)
    z = zipfile.ZipFile(io.BytesIO(data))
    want = {t.lower().replace('.', '-') + '.us.txt': t for t in wanted}
    found = {}
    for name in z.namelist():
        base = name.rsplit('/', 1)[-1].lower()
        t = want.get(base)
        if not t:
            continue
        rows = []
        for line in z.open(name).read().decode('utf-8', 'ignore').splitlines()[1:]:
            p = line.split(',')
            if len(p) < 8:
                continue
            d = p[2]
            if len(d) != 8:
                continue
            d = d[:4] + '-' + d[4:6] + '-' + d[6:]
            if d < CUTOFF:
                continue
            try:
                rows.append([d, round(float(p[7]), 4)])
            except ValueError:
                pass
        if len(rows) >= 4:
            rows.sort()
            found[t] = rows
    print('stooq matched', len(found), 'of', len(wanted), flush=True)
    return found


# ---------- source 2: nasdaq per ticker ----------
def nasdaq(t):
    url = ('https://api.nasdaq.com/api/quote/%s/chart?assetclass=stocks&fromdate=%s&todate=%s'
           % (t.replace('.', '%2E'), CUTOFF, TODAY.isoformat()))
    j = json.loads(get(url, timeout=30, headers={'Accept': 'application/json, text/plain, */*',
                                                  'Accept-Language': 'en-US,en;q=0.9', 'Origin': 'https://www.nasdaq.com',
                                                  'Referer': 'https://www.nasdaq.com/'}))
    ch = ((j.get('data') or {}).get('chart')) or []
    rows = []
    for p in ch:
        z = p.get('z') or {}
        d, c = z.get('dateTime'), z.get('value')
        if not d or c is None:
            continue
        try:
            mm, dd, yy = d.split('/')
            rows.append(['%04d-%02d-%02d' % (int(yy), int(mm), int(dd)), round(float(str(c).replace(',', '')), 4)])
        except Exception:
            pass
    rows.sort()
    return rows


def nasdaq_one(t):
    for attempt in range(3):
        try:
            rows = nasdaq(t)
            if len(rows) >= 4:
                return t, rows
            return t, None
        except urllib.error.HTTPError as e:
            if e.code in (429, 403):
                time.sleep(10 * (attempt + 1)); continue
            return t, None
        except Exception:
            time.sleep(2)
    return t, None


def write(t, rows, src):
    json.dump({'t': t, 'as_of': TODAY.isoformat(), 'src': src, 'w': weekly(rows)},
              open(os.path.join(OUT, t + '.json'), 'w'), separators=(',', ':'))


def main():
    tickers = [x['t'] for x in json.load(open(IDX)) if not x.get('a')]  # skip alias entries (secondary share classes)
    if len(sys.argv) > 1 and sys.argv[1]:
        tickers = tickers[:int(sys.argv[1])]
    os.makedirs(OUT, exist_ok=True)
    ok = {'stooq': 0, 'nasdaq': 0}
    bulk = {}  # stooq bulk archive needs a login (HTTP 401); nasdaq is the primary source for now
    for t, rows in bulk.items():
        write(t, rows, 'stooq'); ok['stooq'] += 1
    missing = [t for t in tickers if t not in bulk]
    print('fetching via nasdaq for', len(missing), flush=True)
    fail = 0
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for i, (t, rows) in enumerate(ex.map(nasdaq_one, missing)):
            if rows:
                write(t, rows, 'nasdaq'); ok['nasdaq'] += 1
            else:
                fail += 1
            if i % 100 == 0:
                print('%d/%d ok=%s fail=%d %.0fs' % (i, len(missing), ok, fail, time.time() - t0), flush=True)
    json.dump({'as_of': TODAY.isoformat(), 'ok': ok, 'fail': fail, 'tickers': len(tickers)},
              open(os.path.join(OUT, 'meta.json'), 'w'))
    print('done', ok, 'fail', fail)


if __name__ == '__main__':
    main()
