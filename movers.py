"""The day's big movers: companies worth $2B+ whose share price closed 10% or more up or down.

Reads the daily closes on the `prices` branch (unpacked into PRICES_DIR) and data/stocks for names and market values,
and writes out/movers/<date>.json: [{t, n, pct, close, prev, mcap, sector, earn}] sorted by size of move. `earn` is the
date of an earnings report on that day or the day before, when there was one (from EARN_DIR, the `earnings` branch).

The explanation of each move (what happened and why) is written afterwards from the news and the company's own
announcements, and kept in content/movers_<lang>/<date>/<T>.json; see data/movers/.
usage: PRICES_DIR=/tmp/prices [EARN_DIR=/tmp/earn] python3 movers.py [YYYY-MM-DD]"""
import os, sys, json, glob

PR = os.environ.get('PRICES_DIR', 'prices')
ER = os.environ.get('EARN_DIR', '')
MIN_MCAP = float(os.environ.get('MOVERS_MCAP') or 2e9)
MIN_MOVE = float(os.environ.get('MOVERS_PCT') or 10)


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else None
    rows = []
    for f in glob.glob(os.path.join(PR, '*.json')):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        d = j.get('d') or []
        if len(d) < 2:
            continue
        if day is None:
            # the newest day most files end on
            continue
        i = next((k for k, x in enumerate(d) if x[0] == day), None)
        if not i:
            continue
        prev, close = d[i - 1][1], d[i][1]
        if not prev or not close:
            continue
        pct = (close / prev - 1) * 100
        if abs(pct) < MIN_MOVE:
            continue
        t = j['t']
        try:
            st = json.load(open(os.path.join('data', 'stocks', t + '.json')))
        except Exception:
            continue
        mc = (st.get('market') or {}).get('mcap') or 0
        if mc < MIN_MCAP:
            continue
        earn = None
        if ER:
            try:
                q = json.load(open(os.path.join(ER, 'e', t + '.json')))['q']
                earn = next((x['d'] for x in q if x.get('d') and d[i - 1][0] <= x['d'] <= day), None)
            except Exception:
                pass
        rows.append(dict(t=t, n=st.get('name'), pct=round(pct, 2), close=close, prev=prev, prev_day=d[i - 1][0], mcap=mc,
                         sector=st.get('sector'), industry=st.get('industry'), earn=earn))
    rows.sort(key=lambda r: -abs(r['pct']))
    os.makedirs('out/movers', exist_ok=True)
    json.dump(rows, open('out/movers/%s.json' % day, 'w'), ensure_ascii=False, indent=0)
    for r in rows:
        print('%-6s %+7.2f%%  %8.2f <- %8.2f  $%5.1fB  %s%s' % (r['t'], r['pct'], r['close'], r['prev'], r['mcap'] / 1e9, (r['n'] or '')[:38], ('  [earnings %s]' % r['earn']) if r['earn'] else ''))
    print(len(rows), 'movers on', day)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # default: the newest day in a liquid stock's history
        try:
            sys.argv.append(json.load(open(os.path.join(PR, 'AAPL.json')))['d'][-1][0])
        except Exception:
            sys.exit('give a date')
    main()
