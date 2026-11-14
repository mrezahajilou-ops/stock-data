#!/usr/bin/env python3
"""After the US close: replace the live quotes with the official daily closes.

The Nasdaq watchlist API (quotes.py) sometimes keeps returning the previous day's last sale and timestamp
for part of the symbols in the evening runs (on 2026-10-30 a quarter of all stocks still showed Thursday's
price all weekend, e.g. INTC 92.07 instead of the official 65.76 close). The price-history job (prices.py)
gets the official daily closes, so right after it runs we overwrite the quotes with them.

usage: python close_fix.py <prices_dir> <dir with quotes.json [+ bench.json]>
"""
import json, os, sys, datetime as dt
from zoneinfo import ZoneInfo

def main(pdir, qdir):
    qp = os.path.join(qdir, 'quotes.json')
    Q = json.load(open(qp))
    q = Q.get('q') or {}
    daily = {}
    for fn in os.listdir(pdir):
        if fn.endswith('.json') and fn != 'meta.json':
            try:
                d = json.load(open(os.path.join(pdir, fn))).get('d') or []
            except Exception:
                continue
            if len(d) >= 2:
                daily[fn[:-5]] = d
    bp = os.path.join(qdir, 'bench.json')
    if os.path.exists(bp):
        for k, v in json.load(open(bp)).items():
            if len(v) >= 2:
                daily[k] = v
    if not daily:
        sys.exit('no daily closes found')
    # the latest session in the data; tickers whose own series ends earlier are left alone (no regressions)
    days = {}
    for d in daily.values():
        days[d[-1][0]] = days.get(d[-1][0], 0) + 1
    last = max(k for k, c in days.items() if c >= 0.2 * len(daily))
    stamp = dt.datetime.combine(dt.date.fromisoformat(last), dt.time(16, 0), ZoneInfo('America/New_York')).isoformat()
    # compact official closes for the worker, which serves the site's quotes (branch "closes")
    cl = {t: [round(d[-1][1], 4), round(d[-2][1], 4)] for t, d in daily.items() if d[-1][0] == last}
    json.dump({'d': last, 'stamp': stamp, 'c': cl}, open(os.path.join(qdir, 'closes.json'), 'w'), separators=(',', ':'))
    changed = same = 0
    for t, v in q.items():
        d = daily.get(t)
        if not d or d[-1][0] != last:
            continue
        close, prev = d[-1][1], d[-2][1]
        new = [round(close, 4), round((close / prev - 1) * 100, 2) if prev else None, prev, stamp]
        if abs((v[0] or 0) - close) > 1e-6 or (v[3] or '')[:10] != last:
            changed += 1
        else:
            same += 1
        q[t] = new
    Q['q'] = q
    Q['status'] = 'Closed'
    Q['close'] = last
    Q['as_of'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    json.dump(Q, open(qp, 'w'), separators=(',', ':'))
    print('official closes of %s: %d quotes corrected, %d already right' % (last, changed, same))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
