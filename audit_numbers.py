#!/usr/bin/env python3
"""Numeric self-audit of data/stocks: internal consistency (price x shares = market cap, EPS x shares = profit, growth
math, per-share sanity, TTM vs annual) and agreement with the independent Yahoo reference (estimates/est.json).
Usage: python audit_numbers.py [est.json] [--apply]   (--apply = run the build-time fixers in memory first)
Prints each check with its count and the biggest companies affected; writes data/audit_numbers.json."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
est = json.load(open(args[0] if args else os.path.join(ROOT, 'estimates', 'est.json')))['est']
APPLY = '--apply' in sys.argv
if APPLY:
    sys.argv = ['x']; import build; build.EST = est
    build.FX_LATEST.update({'TWD': 31.0, 'EUR': 0.86, 'GBP': 0.75, 'JPY': 150.0, 'CHF': 0.80, 'CAD': 1.38, 'DKK': 6.4, 'HKD': 7.8, 'BRL': 5.4, 'KRW': 1380.0, 'INR': 88.0, 'AUD': 1.5, 'SEK': 9.4, 'NOK': 10.0, 'CNY': 7.1, 'MXN': 18.5, 'SGD': 1.29, 'ZAR': 17.0, 'ILS': 3.3})
sc = json.load(open(os.path.join(ROOT, 'data', 'screener.json'))); ci = {c: i for i, c in enumerate(sc['cols'])}
rows = [r for r in sc['rows'] if (r[ci['mcap']] or 0) >= 1e9]
issues = collections.defaultdict(list)
def add(k, t, m, *v): issues[k].append((t, round(m / 1e9, 1)) + v)
n = 0
for r in rows:
    t = r[ci['t']]
    try: d = json.load(open(os.path.join(ROOT, 'data', 'stocks', t + '.json')))
    except Exception: continue
    e = est.get(t) or {}; ref = e.get('ref') or {}; usd = (e.get('cur') or 'USD') == 'USD'
    if APPLY:
        build.fill_from_yahoo(d, e); build.reconcile_per_share(d, d.get('market'), ref)
    n += 1
    mk = d.get('market') or {}; ra = d.get('ratios') or {}; T = d.get('ttm') or {}; A = d['annual']; L = A[-1]; bs = d.get('bs') or {}
    price, mcap = mk.get('price'), mk.get('mcap'); m = mcap or 0
    sh = T.get('shares_diluted') or L.get('shares_diluted')
    ni = T.get('net_income') if T.get('net_income') is not None else L.get('net_income')
    eps = T.get('eps') if T.get('eps') is not None else L.get('eps_diluted')
    if price and mcap and sh and not 0.75 < price * sh / mcap < 1.33: add('shares_vs_market', t, m, round(price * sh / mcap, 2))
    if eps and sh and ni and abs(ni) > 1e7 and not 0.8 < eps * sh / ni < 1.25: add('eps_x_shares_vs_profit', t, m, round(eps * sh / ni, 2), eps)
    if usd and ref.get('teps') and eps and ref['teps'] > 0 and eps > 0 and not 0.8 < eps / ref['teps'] < 1.25: add('eps_vs_yahoo', t, m, eps, ref['teps'])
    if usd and ref.get('rev') and (T.get('revenue') or L.get('revenue')):
        ours = T.get('revenue') or L.get('revenue')
        if not 0.85 < ours / ref['rev'] < 1.18: add('revenue_vs_yahoo', t, m, round(ours / 1e9, 2), round(ref['rev'] / 1e9, 2))
    if ref.get('pe') and ra.get('pe') and ref['pe'] > 0 and not 0.8 < ra['pe'] / ref['pe'] < 1.25: add('pe_vs_yahoo', t, m, round(ra['pe'], 1), round(ref['pe'], 1))
    if ref.get('mcap') and mcap and not 0.9 < mcap / ref['mcap'] < 1.1: add('mcap_vs_yahoo', t, m, round(ref['mcap'] / 1e9, 1))
    dps = T.get('dps') if T.get('dps') is not None else L.get('div_per_share')
    if dps and price and dps / price > 0.4: add('dps_not_per_share', t, m, dps)
    if ra.get('div_yield') and dps and price and not 0.7 < (dps / price) / ra['div_yield'] < 1.4: add('divyield_vs_dps', t, m, round(ra['div_yield'] * 100, 2), round(dps / price * 100, 2))
    if ra.get('div_yield') and ra['div_yield'] > 0.25: add('divyield_huge', t, m, ra['div_yield'])
    if len(A) >= 2 and A[-2].get('revenue') and L.get('revenue') and L.get('revenue_growth') is not None and abs(L['revenue'] / A[-2]['revenue'] - 1 - L['revenue_growth']) > 0.02: add('growth_math', t, m)
    if L.get('revenue') is not None and L['revenue'] < 0: add('negative_revenue', t, m, L['revenue'])
    if T.get('revenue') and L.get('revenue') and not 0.4 < T['revenue'] / L['revenue'] < 3: add('ttm_vs_annual_revenue', t, m, round(T['revenue'] / 1e9, 2), round(L['revenue'] / 1e9, 2))
    for k in ('roe', 'roic'):
        if L.get(k) is not None and abs(L[k]) > 5: add('bound_' + k, t, m, L[k])
    if ra.get('pe') and ra['pe'] > 1000: add('pe_above_1000', t, m, round(ra['pe']))
    debt = bs.get('debt') if bs.get('debt') is not None else L.get('debt')
    if debt is not None and (bs.get('assets') or L.get('assets')) and debt > 2.5 * (bs.get('assets') or L.get('assets')): add('debt_gt_assets', t, m, round(debt / 1e9, 1))
    if T.get('end') and L.get('fy_end') and T['end'] < L['fy_end']: add('ttm_older_than_annual', t, m, T['end'], L['fy_end'])
print('checked', n, '(apply=%s)' % APPLY)
out = {}
for k, v in sorted(issues.items(), key=lambda x: -len(x[1])):
    v = sorted(v, key=lambda x: -x[1]); out[k] = v[:40]
    print('== %-26s %4d   %s' % (k, len(v), v[:8]))
json.dump({'checked': n, 'issues': out}, open(os.path.join(ROOT, 'data', 'audit_numbers.json'), 'w'), indent=1)
