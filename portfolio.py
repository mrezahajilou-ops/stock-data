#!/usr/bin/env python3
"""Daily performance history for Reza's portfolio page (https://rezahajiloubooks.com/pages/portfolio).

The holdings are PRIVATE: they live only in Shopify (metaobjects `rz_trade`, one per trade, entered in the
Shopify admin) and are shown on the page only to subscribers. This repository and the Actions logs are
public, so this script never writes holdings, values or trades to a file or to the log.

Each run (after every quotes refresh):
  1. reads all rz_trade entries and the rz_portfolio/main entry from the Shopify Admin API
  2. values the portfolio at the latest prices (quotes branch) and computes today's time-weighted return
     (deposits/withdrawals don't count as performance)
  3. updates rz_portfolio/main: history [[date, index, spyIndex]] (public, percentages only),
     values [[date, usd]] (private), live {...} (public, percentages only)
Auth: same Dev Dashboard app as sync_shopify.py (SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET).
"""
import json, os, sys, datetime as dt, urllib.request
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_shopify import token, gql  # noqa: E402

NY = ZoneInfo('America/New_York')
RAW = 'https://raw.githubusercontent.com/' + os.environ.get('GITHUB_REPOSITORY', 'mrezahajilou-ops/stock-data')

TRADES = '''query($c: String) { metaobjects(type: "rz_trade", first: 250, after: $c) {
  nodes { fields { key value } } pageInfo { hasNextPage endCursor } } }'''
MAIN = '''{ metaobjectByHandle(handle: {type: "rz_portfolio", handle: "main"}) { id fields { key value } } }'''
UPDATE = '''mutation($id: ID!, $f: [MetaobjectFieldInput!]!) { metaobjectUpdate(id: $id, metaobject: {fields: $f}) {
  metaobject { id } userErrors { field message } } }'''


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def load_trades(tok):
    out, cur = [], None
    while True:
        j = gql(tok, TRADES, {'c': cur})
        mo = ((j.get('data') or {}).get('metaobjects')) or {}
        for n in mo.get('nodes') or []:
            f = {x['key']: x['value'] for x in n['fields']}
            if not f.get('date') or not f.get('action'):
                continue
            out.append({'d': dt.datetime.fromisoformat(f['date'].replace('Z', '+00:00')), 'a': f['action'],
                        't': (f.get('ticker') or '').strip().upper(), 'n': num(f.get('shares')),
                        'p': num(f.get('price')), 'm': num(f.get('amount'))})
        if not (mo.get('pageInfo') or {}).get('hasNextPage'):
            break
        cur = mo['pageInfo']['endCursor']
    out.sort(key=lambda t: t['d'])
    return out


def book(trades):
    """Same rules as web_src/portfolio.js -> book()."""
    pos, cash = {}, 0.0
    for t in trades:
        a, k, n, p, m = t['a'], t['t'], t['n'], t['p'], t['m']
        o = pos.setdefault(k, {'n': 0.0, 'cost': 0.0}) if k else None
        if a == 'OPEN':
            if o is not None:
                o['n'] += n; o['cost'] += n * p
            else:
                cash += m
        elif a == 'BUY' and o is not None:
            o['n'] += n; o['cost'] += n * p; cash -= n * p
        elif a == 'SELL' and o is not None and o['n'] > 0:
            q = min(n, o['n']); avg = o['cost'] / o['n']
            o['cost'] -= avg * q; o['n'] -= q; cash += q * p
        elif a == 'DIVIDEND' and o is not None:
            cash += m or (p * o['n'])
        elif a == 'DEPOSIT':
            cash += m
        elif a == 'WITHDRAW':
            cash -= m
    return {k: v['n'] for k, v in pos.items() if v['n'] > 1e-9}, cash


def flows(trades, day):
    f = 0.0
    for t in trades:
        if t['d'].astimezone(NY).date().isoformat() == day:
            if t['a'] == 'DEPOSIT':
                f += t['m']
            elif t['a'] == 'WITHDRAW':
                f -= t['m']
    return f


def main():
    with urllib.request.urlopen(RAW + '/quotes/quotes.json', timeout=60) as r:
        Q = json.loads(r.read())
    q = Q.get('q') or {}
    tok = token()
    trades = load_trades(tok)
    j = gql(tok, MAIN, {})
    mo = (j.get('data') or {}).get('metaobjectByHandle')
    if not mo:
        sys.exit('rz_portfolio/main missing')
    F = {x['key']: x['value'] for x in mo['fields']}
    hist = json.loads(F.get('history') or '[]')
    vals = json.loads(F.get('values') or '[]')
    meta = json.loads(F.get('meta') or '{}')
    if not trades:
        print('no trades yet'); return

    now = dt.datetime.now(dt.timezone.utc)
    # the trading day the quotes belong to (not the clock: before the open the feed still shows yesterday)
    days = {}
    for v in q.values():
        if v and len(v) > 3 and v[3]:
            days[str(v[3])[:10]] = days.get(str(v[3])[:10], 0) + 1
    if not days:
        print('no quote dates'); return
    d = max(days, key=days.get)
    today = dt.date.fromisoformat(d)
    lock = (meta.get('savvy') or {}).get('as_of') or ''
    if d <= lock:
        print('quotes are from %s, history up to %s comes from Savvy Trader - nothing to do' % (d, lock)); return
    start_of_day = dt.datetime.combine(today, dt.time(0, 0), NY)

    end_of_day = start_of_day + dt.timedelta(days=1)
    hold, cash = book([t for t in trades if t['d'] < min(now, end_of_day)])
    missing = [k for k in hold if not (q.get(k) and q[k][0])]
    if missing:
        print('::warning::%d holdings without a quote' % len(missing))
    px = lambda k, i: (q.get(k) or [None, None, None])[i]
    V = cash + sum(n * (px(k, 0) or 0) for k, n in hold.items())

    # base = previous trading day's close, valued with the same quote feed (previous close)
    bhold, bcash = book([t for t in trades if t['d'] < start_of_day])
    Vb = bcash + sum(n * (px(k, 2) or px(k, 0) or 0) for k, n in bhold.items())
    spy = px('SPY', 0)
    spy0 = meta.get('spy0')

    if hist and hist[-1][0] == d:
        base = hist[-2] if len(hist) > 1 else hist[-1]
        hist = hist[:-1]
        vals = [v for v in vals if v[0] != d]
    else:
        base = hist[-1] if hist else None
    if base is None:
        sv = meta.get('savvy') or {}
        base = [sv.get('as_of', d), 1 + (sv.get('total') or 0) / 100, 1.0]
        hist = [base]
    r = (V - flows(trades, d)) / Vb if Vb > 0 else 1.0
    if not (0.5 < r < 1.5):
        sys.exit('implausible daily change, not saving')
    if spy and not spy0:
        # anchor: the base day's SPY close maps to the base point's benchmark index
        spy0 = meta['spy0'] = (px('SPY', 2) or spy) / (base[2] or 1)
    spy_idx = round(spy / spy0, 6) if spy and spy0 else (base[2] if base else None)
    hist.append([d, round(base[1] * r, 6), spy_idx])
    vals.append([d, round(V, 2)])
    live = {'as_of': Q.get('as_of'), 'status': Q.get('status'), 'date': d, 'idx': hist[-1][1], 'spy': spy_idx,
            'day': round(r - 1, 6), 'n': len(hold)}
    fields = [{'key': 'history', 'value': json.dumps(hist, separators=(',', ':'))},
              {'key': 'values', 'value': json.dumps(vals, separators=(',', ':'))},
              {'key': 'live', 'value': json.dumps(live, separators=(',', ':'))},
              {'key': 'meta', 'value': json.dumps(meta, separators=(',', ':'), ensure_ascii=False)}]
    j = gql(tok, UPDATE, {'id': mo['id'], 'f': fields})
    ue = ((j.get('data') or {}).get('metaobjectUpdate') or {}).get('userErrors') or j.get('errors')
    if ue:
        sys.exit('update failed: %s' % json.dumps(ue)[:300])
    print('updated: %d history points, %d holdings, %d trades' % (len(hist), len(hold), len(trades)))


if __name__ == '__main__':
    main()
