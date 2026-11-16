"""One-off helper: find SEC CIKs of 13F filers by name and show their latest 13F-HR (period, filed)."""
import json, re, sys, time, urllib.request
UA = {'User-Agent': 'SahamAnaliz research contact@sahamanaliz.com'}
def get(u):
    for a in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except Exception:
            time.sleep(2 + a * 3)
    return b''
QUERIES = sys.argv[1].split(';')
txt = get('https://www.sec.gov/Archives/edgar/cik-lookup-data.txt').decode('latin-1')
print('lookup lines', txt.count('\n'))
for q in QUERIES:
    pat = re.compile(r'^(.*%s.*):(\d{10}):$' % re.escape(q.upper()), re.M)
    hits = pat.findall(txt)[:15]
    best = []
    for name, cik in hits:
        time.sleep(0.15)
        b = get('https://data.sec.gov/submissions/CIK%s.json' % cik)
        try:
            r = json.loads(b)['filings']['recent']
        except Exception:
            continue
        f = [(r['reportDate'][i], r['filingDate'][i]) for i, x in enumerate(r['form']) if x == '13F-HR']
        if f:
            best.append((f[0][1], int(cik), name.strip(), f[0][0], len(f)))
    best.sort(reverse=True)
    print('##', q, '=>', best[:4] if best else 'NO 13F')
