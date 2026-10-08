#!/usr/bin/env python3
"""Daily closes of the benchmarks (SPY, QQQ) since 2025-01-01, for the portfolio chart.
Public market data -> orphan branch `bench` (bench/bench.json: {"SPY": [[date, close], ...], ...})."""
import json, os, datetime as dt, urllib.request

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}


def hist(sym):
    to = dt.date.today().isoformat()
    url = ('https://api.nasdaq.com/api/quote/%s/historical?assetclass=etf&fromdate=2025-01-01&todate=%s&limit=9999' % (sym, to))
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=60) as r:
        rows = (((json.loads(r.read()).get('data') or {}).get('tradesTable') or {}).get('rows')) or []
    out = []
    for x in rows:
        m, d, y = x['date'].split('/')
        out.append(['%s-%s-%s' % (y, m, d), float(x['close'].replace('$', '').replace(',', ''))])
    return sorted(out)


def main():
    res = {s: hist(s) for s in ('SPY', 'QQQ')}
    print({k: len(v) for k, v in res.items()})
    os.makedirs('bench', exist_ok=True)
    json.dump(res, open('bench/bench.json', 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
