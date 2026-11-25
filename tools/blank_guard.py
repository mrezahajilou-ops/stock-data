#!/usr/bin/env python3
"""Blank-value guard: every '—' a reader sees must have a reason.

Scans the built site for key/value cells and table cells that show '—' and groups them by label and page kind,
weighted toward large companies (the ones people actually open). Run with the stock-data folder to also
check the raw data behind the interactive tools (DCF calculator, stock analysis): fields that are empty for a
company whose filings should contain them.

    python3 tools/blank_guard.py <built site> [stock-data folder]
"""
import collections, glob, json, os, re, sys

ROOT = sys.argv[1]
SD = sys.argv[2] if len(sys.argv) > 2 else None
KV = re.compile(r'<small>([^<]{1,60})</small><b[^>]*>(?:<span[^>]*>)?—')
TH = re.compile(r'(?s)<table>.*?</table>')
DASH = {'—', '-', 'n/a', 'N/A', ''}


def kind(rel):
    s = [x for x in rel.split('/') if x and x != 'index.html']
    if not s:
        return 'home'
    return s[0] + ('/*/' + s[2] if len(s) > 2 else '/*' if len(s) > 1 else '')


cnt, pages, ex = collections.Counter(), collections.Counter(), {}
for p in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True):
    rel = os.path.relpath(p, ROOT)
    k = kind(rel)
    pages[k] += 1
    s = open(p, encoding='utf-8', errors='ignore').read()
    for lab in KV.findall(s):
        key = (k, 'kv', lab.strip())
        cnt[key] += 1
        ex.setdefault(key, rel)
    for tb in TH.findall(s):
        heads = [re.sub('<[^>]+>', '', h).strip() for h in re.findall(r'(?s)<th[^>]*>(.*?)</th>', tb.split('</thead>')[0])] if '</thead>' in tb else []
        for row in re.findall(r'(?s)<tr>(.*?)</tr>', tb.split('</thead>')[-1]):
            cells = re.findall(r'(?s)<t[dh][^>]*>(.*?)</t[dh]>', row)
            for i, c in enumerate(cells):
                if re.sub('<[^>]+>', '', c).strip() == '—' and i < len(heads):
                    key = (k, 'col', heads[i])
                    cnt[key] += 1
                    ex.setdefault(key, rel)

print('blank guard: dashes by page kind and label (share of pages of that kind)')
for (k, typ, lab), n in sorted(cnt.items(), key=lambda x: -x[1] / max(pages[x[0][0]], 1))[:40]:
    print('  %-26s %-4s %-34s %6d  %5.1f%%  e.g. /%s' % (k[:26], typ, lab[:34], n, 100 * n / max(pages[k], 1), ex[(k, typ, lab)]))

if SD:
    # raw data behind the tools: large companies (market cap > $10B) missing what their filings should give
    need = {'revenue 5y growth': lambda d: (d.get('summary') or {}).get('rev_cagr_5y'),
            'revenue 1y growth': lambda d: (d.get('summary') or {}).get('rev_cagr_1y'),
            'EPS 5y growth': lambda d: (d.get('summary') or {}).get('eps_cagr_5y'),
            'ROIC 5y avg': lambda d: (d.get('summary') or {}).get('roic_avg_5y'),
            'revenue TTM': lambda d: (d.get('ttm') or {}).get('revenue'),
            'net income TTM': lambda d: (d.get('ttm') or {}).get('net_income'),
            'free cash flow TTM': lambda d: (d.get('ttm') or {}).get('fcf'),
            'shares (TTM diluted)': lambda d: (d.get('ttm') or {}).get('shares_diluted'),
            'DCF base': lambda d: (d.get('dcf') or {}).get('base'),
            'analyst target': lambda d: (d.get('analyst') or {}).get('tgt')}
    miss, big = collections.defaultdict(list), 0
    for f in glob.glob(os.path.join(SD, 'data', 'stocks', '*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if ((d.get('market') or {}).get('mcap') or 0) < 1e10:
            continue
        big += 1
        for k, fn in need.items():
            try:
                v = fn(d)
            except Exception:
                v = None
            if v is None:
                miss[k].append(d['ticker'])
    print('raw data: %d companies above $10B' % big)
    for k, ts in sorted(miss.items(), key=lambda x: -len(x[1])):
        print('  %-22s missing for %4d  e.g. %s' % (k, len(ts), ' '.join(sorted(ts)[:12])))
