#!/usr/bin/env python3
"""content/batches/*.json (hand-written Persian company profiles) -> content/profiles/<TICKER>.json

- validates the fields the stock page expects
- copies a profile to the company's other share classes (same SEC CIK, e.g. GOOGL -> GOOG, BRK-B -> BRK-A)
- drops the link part of a rival ("Name|TICKER") when that ticker is not covered by the site
Run:  python content/build_profiles.py
"""
import json, os, glob, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCKS = os.path.join(ROOT, 'data', 'stocks')
OUT = os.path.join(ROOT, 'content', 'profiles')
UPDATED = '2026-10'
REQ = ('what', 'problem', 'customers', 'money', 'moat', 'risks')


def main():
    covered = {f[:-5] for f in os.listdir(STOCKS) if f.endswith('.json')}
    cik_of, by_cik = {}, defaultdict(list)
    for t in covered:
        try:
            c = json.load(open(os.path.join(STOCKS, t + '.json'))).get('cik')
        except Exception:
            continue
        cik_of[t] = c
        by_cik[c].append(t)
    os.makedirs(OUT, exist_ok=True)
    n = errors = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'content', 'batches', '*.json'))):
        for p in json.load(open(f, encoding='utf-8')):
            t = p.get('t')
            miss = [k for k in REQ if not p.get(k)]
            if not t or miss or t not in covered:
                print('skip', os.path.basename(f), t, 'missing' if miss else 'not covered', miss)
                errors += 1
                continue
            rivals = []
            for r in p.get('rivals') or []:
                if '|' in r:
                    name, tk = r.rsplit('|', 1)
                    r = r if tk in covered else name
                rivals.append(r)
            p['rivals'] = rivals
            p['updated'] = p.get('updated') or UPDATED
            for tk in by_cik.get(cik_of.get(t), [t]) or [t]:
                q = dict(p, t=tk)
                json.dump(q, open(os.path.join(OUT, tk + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
                n += 1
    print('profiles written:', n, 'problems:', errors)
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
