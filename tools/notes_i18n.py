"""Earnings analyses and big-move explanations in fa/es/tr/ar: the translated headline and takeaway (summary for moves)
live in content/i18n_notes/<lang>.json as {"earn": {T: {d, headline, takeaway}}, "move": {T: {d, headline, summary}}};
this writes data/earnings_notes/<lang>/ and data/movers/<lang>/ in the same shape as the English files, keeping the
date, quarter, move size and source links from the English record. The full sections are optional per entry:
earn: results / mgmt / view / watch (lists of paragraphs); move: why / context. When present they are published, so
every language reaches the depth of the English analysis; without them the page shows the headline and takeaway."""
import glob, io, json, os
SD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_WORD = {'fa': 'منبع', 'es': 'Fuente', 'tr': 'Kaynak', 'ar': 'المصدر'}   # source titles are English: a local label instead


def build():
    for lang in ('fa', 'es', 'tr', 'ar'):
        p = os.path.join(SD, 'content', 'i18n_notes', lang + '.json')
        if not os.path.exists(p):
            continue
        tr = json.load(io.open(p, encoding='utf-8'))
        od = os.path.join(SD, 'data', 'earnings_notes', lang); os.makedirs(od, exist_ok=True)
        idx = {}
        for t, x in (tr.get('earn') or {}).items():
            f = os.path.join(SD, 'content', 'earnings_en', t, x['d'] + '.json')
            if not os.path.exists(f):
                continue
            en = json.load(io.open(f, encoding='utf-8'))
            n = dict(t=t, d=en['d'], q=en['q'], headline=x['headline'], takeaway=x['takeaway'], src=en.get('src'))
            for k in ('results', 'mgmt', 'view', 'watch'):
                if x.get(k):
                    n[k] = x[k]
            io.open(os.path.join(od, t + '.json'), 'w', encoding='utf-8').write(json.dumps({'t': t, 'notes': [n]}, ensure_ascii=False))
            idx[t] = {'d': n['d'], 'q': n['q'], 'headline': n['headline']}
        io.open(os.path.join(od, 'index.json'), 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False))
        md = os.path.join(SD, 'data', 'movers', lang); os.makedirs(md, exist_ok=True)
        latest = {}
        for t, x in (tr.get('move') or {}).items():
            f = os.path.join(SD, 'content', 'movers_en', x['d'], t + '.json')
            if not os.path.exists(f):
                continue
            en = json.load(io.open(f, encoding='utf-8'))
            m = dict(t=t, d=en['d'], pct=en['pct'], close=en['close'], prev=en['prev'], kind=en['kind'],
                     headline=x['headline'], summary=x['summary'], why=x.get('why') or [], context=x.get('context') or [],
                     src=[{'title': '%s %d' % (SRC_WORD[lang], i + 1), 'url': z['url']} for i, z in enumerate(en.get('src') or [])])
            io.open(os.path.join(md, t + '.json'), 'w', encoding='utf-8').write(json.dumps({'t': t, 'moves': [m]}, ensure_ascii=False, separators=(',', ':')))
            latest[t] = {'d': m['d'], 'pct': m['pct'], 'headline': m['headline']}
        io.open(os.path.join(md, 'index.json'), 'w', encoding='utf-8').write(json.dumps({'latest': latest}, ensure_ascii=False, separators=(',', ':')))
        print(lang, 'notes', len(idx), 'moves', len(latest))


if __name__ == '__main__':
    build()
