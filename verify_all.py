#!/usr/bin/env python3
"""Compare every stock's key numbers with an independent source (Yahoo Finance reference values collected by
estimates.py). Writes data/verify_all.json: per-metric agreement rates and the worst outliers.
Usage: python verify_all.py [est.json]"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'estimates', 'est.json')))['est']
M = {  # ours -> ref key, tolerance
    'mcap': ('mcap', .05), 'pe': ('pe', .10), 'ps': ('ps', .10), 'pb': ('pb', .15), 'ev_ebitda': ('evebitda', .15),
    'rev_ttm': ('rev', .05), 'fcf_ttm': ('fcf', .15), 'debt': ('debt', .20), 'cash': ('cash', .20), 'divy': ('divy', .15),
    'fwd_pe': ('fpe', .20)}
stats = collections.defaultdict(lambda: [0, 0, 0])  # ok, bad, missing-ours
bad = collections.defaultdict(list)
for t, e in est.items():
    ref = e.get('ref') or {}
    p = os.path.join(ROOT, 'data', 'stocks', t + '.json')
    if not ref or not os.path.exists(p):
        continue
    d = json.load(open(p))
    L, r, mk, T = d['annual'][-1], d.get('ratios') or {}, d.get('market') or {}, d.get('ttm') or {}
    if (e.get('cur') or 'USD') != 'USD':
        continue  # foreign currencies: Yahoo's financials are in local currency
    ours = {'mcap': mk.get('mcap'), 'pe': r.get('pe'), 'ps': r.get('ps'), 'pb': r.get('pb'), 'ev_ebitda': r.get('ev_ebitda'),
            'rev_ttm': T.get('revenue') if T.get('revenue') is not None else L.get('revenue'),
            'fcf_ttm': T.get('fcf') if T.get('fcf') is not None else L.get('fcf'),
            'debt': L.get('debt'), 'cash': L.get('cash'), 'divy': r.get('div_yield'), 'fwd_pe': r.get('fwd_pe')}
    # rescale price-based ratios to Yahoo's price (different snapshot times)
    f = (ref['price'] / mk['price']) if (ref.get('price') and mk.get('price')) else 1.0
    for k in ('mcap', 'pe', 'ps', 'pb', 'fwd_pe'):
        if ours[k] is not None:
            ours[k] *= f
    if ours['divy']:
        ours['divy'] /= f
    for k, (rk, tol) in M.items():
        a, b = ours.get(k), ref.get(rk)
        if not isinstance(b, (int, float)):
            continue
        if b in (None, 0) or (k in ('pe', 'ps', 'pb', 'ev_ebitda', 'fwd_pe') and b < 0):
            continue
        if k == 'divy' and b == 0 and not a:
            stats[k][0] += 1; continue
        if a is None:
            stats[k][2] += 1; bad[k].append((t, None, b, mk.get('mcap') or 0)); continue
        dev = abs(a / b - 1)
        if dev <= tol:
            stats[k][0] += 1
        else:
            stats[k][1] += 1
            bad[k].append((t, round(a, 3), round(b, 3), mk.get('mcap') or 0))
out = {'metrics': {k: {'ok': v[0], 'off': v[1], 'missing': v[2], 'ok_pct': round(100 * v[0] / max(1, sum(v)), 1)} for k, v in stats.items()},
       'worst': {k: sorted(v, key=lambda x: -x[3])[:40] for k, v in bad.items()}}
json.dump(out, open(os.path.join(ROOT, 'data', 'verify_all.json'), 'w'), indent=1)
for k, v in out['metrics'].items():
    print('%-10s ok %5.1f%%  (%d ok, %d off, %d missing)' % (k, v['ok_pct'], v['ok'], v['off'], v['missing']))
