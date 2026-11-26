"""The day's big movers: companies worth $2B+ whose share price closed 10% or more up or down.

Reads the daily closes on the `prices` branch (unpacked into PRICES_DIR) and data/stocks for names and market values,
and writes data/movers/raw/<date>.json: [{t, n, pct, close, prev, mcap, sector, earn}] sorted by size of move. `earn` is the
date of an earnings report on that day or the day before, when there was one (from EARN_DIR, the `earnings` branch).

The explanation of each move (what happened and why) is written afterwards from the news and the company's own
announcements, and kept in content/movers_<lang>/<date>/<T>.json; see data/movers/.
usage: PRICES_DIR=/tmp/prices [EARN_DIR=/tmp/earn] python3 movers.py [YYYY-MM-DD]
   or: QUOTES=/tmp/quotes.json [EARN_DIR=/tmp/earn] python3 movers.py   (the same day, right after the close, from the
       last near-live quote snapshot: used by .github/workflows/movers.yml so the list exists the evening of the move)"""
import os, sys, json, glob, datetime as dt

PR = os.environ.get('PRICES_DIR', 'prices')
ER = os.environ.get('EARN_DIR', '')
MIN_MCAP = float(os.environ.get('MOVERS_MCAP') or 2e9)
MIN_MOVE = float(os.environ.get('MOVERS_PCT') or 10)


def from_quotes(path):
    """-> (day, rows) from the quotes branch snapshot: [last, % change, previous close, last trade time] per ticker."""
    j = json.load(open(path))
    q = j.get('q') or {}
    days = {}
    for v in q.values():
        if v and len(v) > 3 and v[3]:
            days[v[3][:10]] = days.get(v[3][:10], 0) + 1
    # the newest trading day with a real number of fresh quotes (the near-live set covers the large companies)
    day = max((d for d, n in days.items() if n >= 500), default=None)
    # guard: a stale previous close (still the close of two sessions ago) re-lists yesterday's movers under today's
    # date (seen 2026-11-25). If a ticker was on the previous list and its "previous close" equals that list's prev, skip it.
    older = sorted(f for f in glob.glob('data/movers/raw/*.json') if os.path.basename(f)[:10] < (day or ''))
    yest = {r['t']: r for r in json.load(open(older[-1]))} if older else {}
    rows = []
    for t, v in q.items():
        if not v or len(v) < 4 or not v[3] or v[3][:10] != day or not v[0] or not v[2]:
            continue
        y = yest.get(t)
        if y and y.get('prev') and abs(v[2] / y['prev'] - 1) < 0.002:
            continue
        pct = (v[0] / v[2] - 1) * 100
        if abs(pct) >= MIN_MOVE:
            rows.append((t, v[2], v[0], pct))
    return day, rows


def main():
    if os.environ.get('QUOTES'):
        day, cand = from_quotes(os.environ['QUOTES'])
        if not day:
            sys.exit('no quotes')
        return finish(day, cand, prev_day=None)
    day = sys.argv[1] if len(sys.argv) > 1 else None
    cand, pdays = [], {}
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
        cand.append((j['t'], prev, close, pct))
        pdays[j['t']] = d[i - 1][0]
    return finish(day, cand, pdays)


def finish(day, cand, prev_day):
    rows = []
    for t, prev, close, pct in cand:
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
                lo = (prev_day or {}).get(t) or (dt.date.fromisoformat(day) - dt.timedelta(days=4)).isoformat()
                earn = next((x['d'] for x in q if x.get('d') and lo <= x['d'] <= day), None)
            except Exception:
                pass
        rows.append(dict(t=t, n=st.get('name'), pct=round(pct, 2), close=close, prev=prev, prev_day=(prev_day or {}).get(t), mcap=mc,
                         sector=st.get('sector'), industry=st.get('industry'), earn=earn))
    rows.sort(key=lambda r: -abs(r['pct']))
    os.makedirs('data/movers/raw', exist_ok=True)
    json.dump(rows, open('data/movers/raw/%s.json' % day, 'w'), ensure_ascii=False, indent=0)
    for r in rows:
        print('%-6s %+7.2f%%  %8.2f <- %8.2f  $%5.1fB  %s%s' % (r['t'], r['pct'], r['close'], r['prev'], r['mcap'] / 1e9, (r['n'] or '')[:38], ('  [earnings %s]' % r['earn']) if r['earn'] else ''))
    print(len(rows), 'movers on', day)


if __name__ == '__main__':
    if len(sys.argv) < 2 and not os.environ.get('QUOTES'):
        # default: the newest day in a liquid stock's history
        try:
            sys.argv.append(json.load(open(os.path.join(PR, 'AAPL.json')))['d'][-1][0])
        except Exception:
            sys.exit('give a date')
    main()
