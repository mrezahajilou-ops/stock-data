#!/usr/bin/env python3
"""One-off data diagnostics: which XBRL tags a company reports (public SEC data). Output: diag/<T>.json"""
import json, os, sys, time, gzip, urllib.request
UA = os.environ.get('SEC_USER_AGENT', 'Reza Hajilou mreza.hajilou@gmail.com')
KW = ('Revenue', 'Sales', 'Debt', 'Borrowing', 'Notes', 'Depreciation', 'Amortization', 'EarningsPerShare', 'Dividend',
      'Liabilities', 'OperatingIncome', 'CostsAndExpenses', 'OperatingExpenses', 'ProfitLoss', 'NetIncome', 'Shares',
      'Capital', 'PropertyPlant', 'RealEstate', 'Repurchase', 'GrossProfit', 'CostOf', 'Equity', 'Cash')
os.makedirs('diag', exist_ok=True)
for t in sys.argv[1:]:
    try:
        cik = json.load(open('data/stocks/%s.json' % t))['cik']
    except Exception:
        print(t, 'no file'); continue
    req = urllib.request.Request('https://data.sec.gov/api/xbrl/companyfacts/CIK%010d.json' % int(cik), headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            b = r.read()
            if r.headers.get('Content-Encoding') == 'gzip': b = gzip.decompress(b)
    except Exception as e:
        print(t, 'err', e); continue
    j = json.loads(b); out = {'t': t, 'cik': cik, 'name': j.get('entityName'), 'tags': {}}
    for ns, tags in (j.get('facts') or {}).items():
        for name, node in tags.items():
            if ns not in ('dei',) and not any(k in name for k in KW): continue
            for unit, arr in (node.get('units') or {}).items():
                ann = [f for f in arr if f.get('form') in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '10-KT')]
                if not ann: continue
                last = max(ann, key=lambda f: (f.get('end', ''), f.get('filed', '')))
                out['tags']['%s:%s|%s' % (ns, name, unit)] = [last.get('start'), last.get('end'), last.get('val'), last.get('form'), last.get('filed'), len(ann)]
    forms = sorted({(f.get('form'), f.get('fy')) for node in (j.get('facts') or {}).get('dei', {}).values() for arr in node.get('units', {}).values() for f in arr if f.get('form')})
    out['dei_forms'] = forms[-12:]
    for full in (os.environ.get('FULL') or '').split():
        ns, name = full.split(':')
        node = (j.get('facts') or {}).get(ns, {}).get(name) or {}
        out.setdefault('full', {})[full] = {u: [[f.get('start'), f.get('end'), f.get('val'), f.get('form'), f.get('filed'), f.get('fy'), f.get('fp'), f.get('frame')] for f in arr if (f.get('end') or '') >= '2024-06'] for u, arr in (node.get('units') or {}).items()}
    json.dump(out, open('diag/%s.json' % t, 'w'), indent=0)
    print(t, len(out['tags']))
    time.sleep(0.15)
