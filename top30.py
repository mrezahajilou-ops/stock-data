#!/usr/bin/env python3
"""«۳۰ سهم برتر» — stocks with the largest upside to the analysts' average price target (Stock Pro tool).

Inputs (all public data the other pipelines already publish):
  est.json        branch "estimates"  -> tgt (mean target), tlo/thi (low/high), nt (analysts with a target), rec, rm
  screener.json   main data/          -> name, sector, market cap
  quotes.json     branch "quotes"     -> latest price [close, pct, prev, iso]
  prices/<T>.json branch "prices"     -> 'd' last ~40 daily closes (used for the "recent big drop" warning)

Quality rules (so the list is not filled with $1 biotech lottery tickets):
  market cap >= MIN_MCAP, analysts with a price target >= MIN_ANALYSTS, price >= MIN_PRICE, upside <= MAX_UP.
Output: top30.json {as_of, rules, rows:[...]} with the best CANDIDATES rows sorted by upside; the page re-ranks them
with live prices and shows the top 30, so the list stays correct during the day.

Usage: python top30.py est.json screener.json quotes.json <prices_dir or 'web'> out.json
"""
import json, os, sys, datetime as dt, urllib.request

MIN_MCAP = 2e9
MIN_ANALYSTS = 8
MIN_PRICE = 5.0
MAX_UP = 4.0           # +400%: anything above is treated as a data error
CANDIDATES = 80
DROP_WARN = -0.25      # price fell 25%+ over ~20 trading days -> targets may be stale, show a warning
RAW = 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/prices/'


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def closes(t, pdir):
    try:
        if pdir == 'web':
            with urllib.request.urlopen(RAW + t + '.json', timeout=20) as r:
                j = json.loads(r.read())
        else:
            j = load(os.path.join(pdir, t + '.json'))
        return [c for _, c in (j.get('d') or []) if c]
    except Exception:
        return []


def main(est_p, scr_p, q_p, pdir, out_p):
    E = load(est_p)
    est = E.get('est', E)
    S = load(scr_p)
    I = {k: i for i, k in enumerate(S['cols'])}
    scr = {r[0]: r for r in S['rows']}
    Q = load(q_p)
    q = Q.get('q', Q)
    rows = []
    for t, v in est.items():
        r, p = scr.get(t), q.get(t)
        if not r or not p or not p[0]:
            continue
        px, tgt = float(p[0]), v.get('tgt')
        na = v.get('nt') or v.get('n') or 0
        mcap = r[I['mcap']] or 0
        if not tgt or na < MIN_ANALYSTS or mcap < MIN_MCAP or px < MIN_PRICE:
            continue
        up = tgt / px - 1
        if up <= 0 or up > MAX_UP:
            continue
        rows.append({'t': t, 'n': r[I['n']], 'sec': r[I['sector']], 'mcap': round(mcap), 'px': round(px, 2),
                     'tgt': round(tgt, 2), 'tlo': v.get('tlo'), 'thi': v.get('thi'), 'na': na,
                     'rec': v.get('rec'), 'rm': v.get('rm'), 'up': round(up, 4)})
    rows.sort(key=lambda x: -x['up'])
    rows = rows[:CANDIDATES]
    for x in rows:
        c = closes(x['t'], pdir)
        if len(c) >= 21 and c[-21] > 0:
            x['c20'] = round(c[-1] / c[-21] - 1, 4)
    out = {'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'est_as_of': E.get('as_of'),
           'rules': {'mcap': MIN_MCAP, 'analysts': MIN_ANALYSTS, 'price': MIN_PRICE, 'drop_warn': DROP_WARN},
           'rows': rows}
    with open(out_p, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print('top30: %d candidates (eligible universe above the rules)' % len(rows))


if __name__ == '__main__':
    main(*sys.argv[1:6])
