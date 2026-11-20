import json, io, os, datetime as dt
SD = '/home/claude/stock-data'
SRC = os.path.join(SD, 'content', 'earnings_en'); OUTD = os.path.join(SD, 'data', 'earnings_notes', 'en')

def note(t, d, q, headline, takeaway, results, mgmt, view, watch):
    for k, v in (('results', results), ('mgmt', mgmt), ('view', view)):
        assert isinstance(v, list) and v and all(len(p) > 120 for p in v), (t, k)
    assert len(view) >= 3 and 60 < len(headline) < 150 and 150 < len(takeaway) < 520, (t, len(headline), len(takeaway))
    src = None
    try:
        pr = json.load(io.open('/tmp/epr/pr/%s.json' % t, encoding='utf-8'))
        if pr.get('d') == d: src = pr.get('url')
    except Exception: pass
    fix = lambda s: s.replace("'", '’')
    rec = dict(t=t, d=d, q=q, headline=fix(headline), takeaway=fix(takeaway), results=[fix(p) for p in results],
               mgmt=[fix(p) for p in mgmt], view=[fix(p) for p in view], watch=fix(watch), src=src,
               written=dt.date.today().isoformat())
    os.makedirs(os.path.join(SRC, t), exist_ok=True)
    io.open(os.path.join(SRC, t, d + '.json'), 'w', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False))
    print('note', t, d, 'src' if src else 'NO SRC')

def compile_notes():
    os.makedirs(OUTD, exist_ok=True); idx = {}
    for t in sorted(os.listdir(SRC)):
        notes = sorted((json.load(io.open(os.path.join(SRC, t, f), encoding='utf-8')) for f in os.listdir(os.path.join(SRC, t)) if f.endswith('.json')),
                       key=lambda n: n['d'], reverse=True)
        if not notes: continue
        io.open(os.path.join(OUTD, t + '.json'), 'w', encoding='utf-8').write(json.dumps({'t': t, 'notes': notes[:8]}, ensure_ascii=False))
        idx[t] = {'d': notes[0]['d'], 'q': notes[0]['q'], 'headline': notes[0]['headline']}
    io.open(os.path.join(OUTD, 'index.json'), 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False))
    print('compiled', len(idx), 'tickers')
