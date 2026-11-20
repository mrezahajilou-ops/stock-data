import json, os, glob
SD = '/home/claude/stock-data'
DAY = None
def day(d):
    global DAY, ROWS
    DAY = d
    ROWS = {r['t']: r for r in json.load(open('%s/data/movers/raw/%s.json' % (SD, d)))}
def mv(t, headline, summary, why, context=None, src=None, kind='news'):
    r = ROWS[t]
    assert 50 <= len(headline) <= 140, len(headline)
    assert 120 <= len(summary) <= 420, len(summary)
    assert len(why) >= 2 and all(len(p) > 150 for p in why), [len(p) for p in why]
    out = dict(t=t, d=DAY, pct=r['pct'], close=r['close'], prev=r['prev'], kind=kind, headline=headline, summary=summary, why=why,
               context=context or [], src=src or [])
    p = '%s/content/movers_en/%s' % (SD, DAY)
    os.makedirs(p, exist_ok=True)
    json.dump(out, open('%s/%s.json' % (p, t), 'w'), ensure_ascii=False, indent=1)
    print('mover', t, r['pct'])
def compile_movers():
    by, days = {}, {}
    for f in sorted(glob.glob('%s/content/movers_en/*/*.json' % SD)):
        n = json.load(open(f)); by.setdefault(n['t'], []).append(n)
    out = '%s/data/movers/en' % SD
    os.makedirs(out + '/days', exist_ok=True)
    for t, ns in by.items():
        ns.sort(key=lambda n: n['d'], reverse=True)
        json.dump({'t': t, 'moves': ns[:12]}, open('%s/%s.json' % (out, t), 'w'), ensure_ascii=False, separators=(',', ':'))
    # one file per day: every mover, with the headline and summary where an explanation was written
    for f in sorted(glob.glob('%s/data/movers/raw/*.json' % SD)):
        d = os.path.basename(f)[:-5]
        rows = []
        for r in json.load(open(f)):
            n = next((x for x in by.get(r['t'], []) if x['d'] == d), None)
            rows.append(dict(t=r['t'], n=r['n'], pct=r['pct'], close=r['close'], mcap=r['mcap'], earn=r.get('earn'),
                             headline=n['headline'] if n else None, summary=n['summary'] if n else None, kind=n['kind'] if n else None))
        if any(x['headline'] for x in rows):
            json.dump({'d': d, 'rows': rows}, open('%s/days/%s.json' % (out, d), 'w'), ensure_ascii=False, separators=(',', ':'))
            days[d] = len(rows)
    idx = {t: {'d': ns[0]['d'], 'pct': ns[0]['pct'], 'headline': ns[0]['headline']} for t, ns in by.items()}
    json.dump({'days': sorted(days, reverse=True)[:30], 'latest': idx}, open(out + '/index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('compiled movers:', len(by), 'tickers,', len(days), 'days')
