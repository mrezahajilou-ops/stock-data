#!/usr/bin/env python3
"""python3 add.py new_items.json [lang]  -> merges into <lang>.json (default en), newest first, deduped."""
import json, sys, re, datetime as dt
lang = sys.argv[2] if len(sys.argv) > 2 else 'en'
f = '%s.json' % lang
try:
    doc = json.load(open(f, encoding='utf8'))
except FileNotFoundError:
    doc = {'items': []}
norm = lambda s: re.sub(r'[^a-z0-9$]', '', s.lower())
have = {i['id'] for i in doc['items']}
seen = {norm(i['text'])[:80] for i in doc['items']}
added = 0
for it in json.load(open(sys.argv[1], encoding='utf8')):
    assert it.get('id') and it.get('t') and it.get('text') and it.get('src'), it
    dt.datetime.strptime(it['t'][:19], '%Y-%m-%dT%H:%M:%S')
    k = norm(it['text'])[:80]
    if it['id'] in have or k in seen:
        print('skip duplicate:', it['id']); continue
    doc['items'].append({x: it[x] for x in ('id', 't', 'text', 'src', 'url') if it.get(x)})
    have.add(it['id']); seen.add(k); added += 1
doc['items'] = sorted(doc['items'], key=lambda i: i['t'], reverse=True)[:3000]
doc['updated'] = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
json.dump(doc, open(f, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('added', added, 'total', len(doc['items']))
