#!/usr/bin/env python3
"""Rebuild Reza's portfolio history after the Savvy Trader lock date from OFFICIAL daily closes.

Why: stale evening quotes (see close_fix.py) wrote duplicate / out-of-order points (e.g. 2026-10-28 twice).
Everything up to meta.savvy.as_of (the digitized Savvy history) is kept as it is; every trading day after it
is recomputed with the same time-weighted method as portfolio.py:
    r_D = (V_D - flows_D) / V_{D-1}     V = cash + sum(shares x close)
Inputs: trades (Shopify rz_trade), daily closes (prices branch 'd', SPY from the bench branch).
usage: python portfolio_repair.py <prices_dir> <bench.json>      (nothing private is printed)
"""
import json, os, sys, datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_shopify import token, gql  # noqa: E402
from portfolio import load_trades, book, flows, MAIN, UPDATE, NY  # noqa: E402


def closes(pdir, tick):
    out = {}
    for t in tick:
        f = os.path.join(pdir, t + '.json')
        if os.path.exists(f):
            j = json.load(open(f))
            out[t] = dict(map(tuple, j.get('d') or [])) or dict(map(tuple, j.get('w') or []))
    return out


def px_at(series, day):
    """close on `day`, else the last close before it"""
    if day in series:
        return series[day]
    prev = [d for d in series if d <= day]
    return series[max(prev)] if prev else None


def main(pdir, bench):
    tok = token()
    trades = load_trades(tok)
    mo = (gql(tok, MAIN, {}).get('data') or {}).get('metaobjectByHandle')
    F = {x['key']: x['value'] for x in mo['fields']}
    hist, vals = json.loads(F['history']), json.loads(F['values'])
    meta = json.loads(F.get('meta') or '{}')
    lock = (meta.get('savvy') or {}).get('as_of')
    spy0 = meta.get('spy0')
    SPY = dict(map(tuple, json.load(open(bench))['SPY']))
    keep = sorted({h[0]: h for h in hist if h[0] <= lock}.values())
    keepv = sorted({v[0]: v for v in vals if v[0] <= lock}.values())
    tick = sorted({t['t'] for t in trades if t['t']})
    C = closes(pdir, tick)
    missing = [t for t in tick if t not in C]
    days = sorted(d for d in SPY if d > lock)
    last_data = max(max(s) for s in C.values() if s)
    days = [d for d in days if d <= last_data]
    idx = keep[-1][1]
    prev_day = lock
    new_h, new_v = [], []
    for D in days:
        sod = dt.datetime.combine(dt.date.fromisoformat(D), dt.time(0, 0), NY)
        eod = sod + dt.timedelta(days=1)
        h0, c0 = book([t for t in trades if t['d'] < sod])
        h1, c1 = book([t for t in trades if t['d'] < eod])
        Vb = c0 + sum(n * (px_at(C.get(k, {}), prev_day) or 0) for k, n in h0.items())
        V = c1 + sum(n * (px_at(C.get(k, {}), D) or 0) for k, n in h1.items())
        r = (V - flows(trades, D)) / Vb if Vb > 0 else 1.0
        if not (0.5 < r < 1.5):
            sys.exit('implausible daily change on %s, nothing saved' % D)
        idx = idx * r
        new_h.append([D, round(idx, 6), round(SPY[D] / spy0, 6) if spy0 else None])
        new_v.append([D, round(V, 2)])
        prev_day = D
    hist, vals = keep + new_h, keepv + new_v
    live = json.loads(F.get('live') or '{}')
    if new_h:
        live.update({'date': new_h[-1][0], 'idx': new_h[-1][1], 'spy': new_h[-1][2],
                     'day': round(new_h[-1][1] / (hist[-2][1] or 1) - 1, 6), 'status': 'Closed',
                     'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    fields = [{'key': 'history', 'value': json.dumps(hist, separators=(',', ':'))},
              {'key': 'values', 'value': json.dumps(vals, separators=(',', ':'))},
              {'key': 'live', 'value': json.dumps(live, separators=(',', ':'))}]
    j = gql(tok, UPDATE, {'id': mo['id'], 'f': fields})
    ue = ((j.get('data') or {}).get('metaobjectUpdate') or {}).get('userErrors') or j.get('errors')
    if ue:
        sys.exit('update failed: %s' % json.dumps(ue)[:300])
    print('rebuilt %d trading days after %s (%s .. %s); tickers without closes: %d'
          % (len(new_h), lock, days[0] if days else '-', days[-1] if days else '-', len(missing)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
