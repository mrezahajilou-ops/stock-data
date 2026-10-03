#!/usr/bin/env python3
"""Weekly price history (10y, dividend/split adjusted) for every ticker in data/index.json.

Output: prices/<TICKER>.json  ->  {"t": "AAPL", "as_of": "2026-10-03", "w": [[ "2016-10-03", 26.12 ], ...]}
Source: Yahoo Finance chart endpoint (adjclose), fallback Stooq weekly CSV (close).
Published on the orphan branch `prices` so the main repo never grows.
"""
import json, os, sys, time, urllib.request, urllib.error, datetime as dt, csv, io, concurrent.futures as cf

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
IDX = os.path.join(ROOT, 'data', 'index.json')
OUT = os.path.join(ROOT, 'prices')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
TODAY = dt.date.today().isoformat()


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def yahoo(t):
    sym = t.replace('.', '-')          # BRK.B -> BRK-B
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=10y&interval=1wk&events=div%2Csplit'
    j = json.loads(get(url))
    res = j['chart']['result'][0]
    ts = res['timestamp']
    ind = res['indicators']
    closes = (ind.get('adjclose') or [{}])[0].get('adjclose') or ind['quote'][0]['close']
    rows = []
    for s, c in zip(ts, closes):
        if c is None:
            continue
        rows.append([dt.datetime.utcfromtimestamp(s).date().isoformat(), round(float(c), 4)])
    return rows


def stooq(t):
    url = f'https://stooq.com/q/d/l/?s={t.lower()}.us&i=w'
    txt = get(url).decode('utf-8', 'ignore')
    rows = []
    for r in csv.DictReader(io.StringIO(txt)):
        try:
            rows.append([r['Date'], round(float(r['Close']), 4)])
        except Exception:
            pass
    cutoff = (dt.date.today() - dt.timedelta(days=3660)).isoformat()
    return [r for r in rows if r[0] >= cutoff]


def one(t):
    for attempt in range(3):
        try:
            rows = yahoo(t)
            if len(rows) >= 4:
                return t, rows, 'yahoo'
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20 * (attempt + 1)); continue
            break
        except Exception:
            time.sleep(2)
    try:
        rows = stooq(t)
        if len(rows) >= 4:
            return t, rows, 'stooq'
    except Exception:
        pass
    return t, None, None


def main():
    tickers = [x['t'] for x in json.load(open(IDX))]
    if len(sys.argv) > 1:
        tickers = tickers[:int(sys.argv[1])]
    os.makedirs(OUT, exist_ok=True)
    ok = fail = 0
    src = {'yahoo': 0, 'stooq': 0}
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for i, (t, rows, s) in enumerate(ex.map(one, tickers)):
            if rows:
                json.dump({'t': t, 'as_of': TODAY, 'src': s, 'w': rows}, open(os.path.join(OUT, t + '.json'), 'w'), separators=(',', ':'))
                ok += 1; src[s] += 1
            else:
                fail += 1
            if i % 250 == 0:
                print(f'{i}/{len(tickers)} ok={ok} fail={fail} {time.time()-t0:.0f}s', flush=True)
    json.dump({'as_of': TODAY, 'ok': ok, 'fail': fail, 'src': src}, open(os.path.join(OUT, 'meta.json'), 'w'))
    print('done', ok, fail, src)


if __name__ == '__main__':
    main()
