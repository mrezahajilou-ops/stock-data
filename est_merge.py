#!/usr/bin/env python3
"""Merge a partial estimates run (fast lane: only the companies that just reported) into the full file.

  python est_merge.py <full est.json> <partial est.json> <out est.json>
The partial entries replace the full ones; everything else is kept. Never shrinks the file.
"""
import json, sys, datetime as dt

full_p, part_p, out_p = sys.argv[1:4]
try:
    full = json.load(open(full_p))
except Exception:
    full = {'est': {}}
try:
    part = json.load(open(part_p))
except Exception:
    part = {'est': {}}
est = dict(full.get('est') or {})
n = 0
for t, v in (part.get('est') or {}).items():
    if v:
        est[t] = v
        n += 1
if len(est) < len(full.get('est') or {}):
    sys.exit('merge would shrink the estimates file')
json.dump({'as_of': full.get('as_of'), 'fast_as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'est': est},
          open(out_p, 'w'), separators=(',', ':'))
print('merged', n, 'fresh entries into', len(est))
