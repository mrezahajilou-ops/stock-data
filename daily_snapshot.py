#!/usr/bin/env python3
"""One file per trading day with every company worth $2B+ and its closing move, for the dated
'stock market on <day>' pages of every site (a page per day that stays indexed, unlike the live 'today' page).

data/daily/<YYYY-MM-DD>.json = {"d": day, "src": "quotes"|"prices", "rows": [[ticker, close, change, mcap], ...]}
  change = close / previous close - 1;  mcap = market value at that close (today's shares x close).

usage: QUOTES=/tmp/quotes.json python3 daily_snapshot.py            (evening of the day, from the closing quotes)
       PRICES_DIR=/tmp/prices python3 daily_snapshot.py 2026-11-20 ... (backfill from the daily price history)"""
import os, sys, json, glob

MIN = 2e9
OUT = os.path.join('data', 'daily')


def stocks():
    out = {}
    for f in glob.glob(os.path.join('data', 'stocks', '*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        m = d.get('market') or {}
        if m.get('mcap') and m.get('price'):
            out[d['ticker']] = (m['mcap'] / m['price'])          # shares
    return out


def write(day, rows, src):
    rows = [r for r in rows if r[3] >= MIN]
    if len(rows) < 300:
        print('too few rows for', day, len(rows)); return
    rows.sort(key=lambda r: -r[3])
    os.makedirs(OUT, exist_ok=True)
    json.dump({'d': day, 'src': src, 'rows': rows}, open(os.path.join(OUT, day + '.json'), 'w'), separators=(',', ':'))
    print('daily', day, src, len(rows))


def from_quotes(path):
    sh = stocks()
    q = (json.load(open(path)).get('q')) or {}
    days = {}
    for v in q.values():
        if v and len(v) > 3 and v[3]:
            days[v[3][:10]] = days.get(v[3][:10], 0) + 1
    day = max((d for d, n in days.items() if n >= 500), default=None)
    if not day:
        return
    rows = []
    for t, v in q.items():
        if t in sh and v and len(v) > 3 and v[3] and v[3][:10] == day and v[0] and v[2]:
            rows.append([t, round(v[0], 4), round(v[0] / v[2] - 1, 5), round(sh[t] * v[0])])
    write(day, rows, 'quotes')


def from_prices(pr, days):
    sh = stocks()
    hist = {}
    for f in glob.glob(os.path.join(pr, '*.json')):
        t = os.path.basename(f)[:-5]
        if t not in sh:
            continue
        try:
            hist[t] = json.load(open(f)).get('d') or []
        except Exception:
            pass
    for day in days:
        rows = []
        for t, d in hist.items():
            i = next((k for k in range(len(d) - 1, 0, -1) if d[k][0] == day), None)
            if i and d[i][1] and d[i - 1][1]:
                rows.append([t, d[i][1], round(d[i][1] / d[i - 1][1] - 1, 5), round(sh[t] * d[i][1])])
        write(day, rows, 'prices')


if __name__ == '__main__':
    if os.environ.get('QUOTES'):
        from_quotes(os.environ['QUOTES'])
    elif os.environ.get('PRICES_DIR'):
        from_prices(os.environ['PRICES_DIR'], sys.argv[1:])
