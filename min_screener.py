#!/usr/bin/env python3
"""data/screener.json -> data/screener.min.json (same rows, ~25% smaller; the page also caches it).

- repeated strings (sector, industry, currency) become indexes into small dictionaries
- market cap and revenue are stored in thousands of dollars
- other numbers are rounded to what the screener displays / filters on
The page decodes it back to the full-row format, so nothing else changes.
"""
import json, os

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
SRC = os.path.join(ROOT, 'data', 'screener.json')
DST = os.path.join(ROOT, 'data', 'screener.min.json')
DICT_COLS = ('sector', 'industry', 'cur')
SCALE = {'mcap': 1e3, 'rev': 1e3}


def rnd(v):
    if not isinstance(v, float):
        return v
    a = abs(v)
    if a >= 100:
        return round(v, 1)
    if a >= 10:
        return round(v, 2)
    return round(v, 3)


def main():
    j = json.load(open(SRC))
    cols = j['cols']
    dicts = {c: [] for c in DICT_COLS if c in cols}
    pos = {c: {} for c in dicts}
    out = []
    for r in j['rows']:
        row = []
        for c, v in zip(cols, r):
            if c in dicts:
                if v is None:
                    row.append(None); continue
                if v not in pos[c]:
                    pos[c][v] = len(dicts[c]); dicts[c].append(v)
                row.append(pos[c][v])
            elif c in SCALE:
                row.append(None if v is None else int(round(v / SCALE[c])))
            else:
                row.append(rnd(v))
        out.append(row)
    json.dump({'v': 1, 'cols': cols, 'as_of': j.get('as_of'), 'dict': dicts, 'scale': SCALE, 'rows': out},
              open(DST, 'w'), separators=(',', ':'), ensure_ascii=False)
    print('screener.min.json', os.path.getsize(DST), 'bytes (from', os.path.getsize(SRC), ')')


if __name__ == '__main__':
    main()
