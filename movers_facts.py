"""What each big mover filed on the day: the 8-K / 6-K filings (and press-release exhibits) made on the day of the move
or the day before, so the explanation of the move can be written from the company's own announcements.

usage: SEC_USER_AGENT=... python3 movers_facts.py YYYY-MM-DD TICKER [TICKER ...]
writes out/mv/<date>/<T>.json: {t, d, filings: [{form, filed, items, url, text}]} (an empty list when nothing was filed)."""
import os, sys, json, re, datetime as dt
import earnings_pr as E

OUT = os.environ.get('MV_OUT', 'out')
ITEMS = {'1.01': 'material agreement', '1.02': 'agreement terminated', '2.01': 'acquisition or disposal completed', '2.02': 'results of operations',
         '2.05': 'restructuring', '2.06': 'impairment', '3.01': 'listing notice', '4.01': 'auditor change', '4.02': 'earlier statements not reliable',
         '5.02': 'executive or director change', '7.01': 'disclosure (Reg FD)', '8.01': 'other event'}


def filings(cik, day):
    b = E.get('https://data.sec.gov/submissions/CIK%010d.json' % cik)
    if not b:
        return None
    rec = (json.loads(b).get('filings') or {}).get('recent') or {}
    d0 = dt.date.fromisoformat(day)
    out = []
    forms, dates, accs = rec.get('form') or [], rec.get('filingDate') or [], rec.get('accessionNumber') or []
    items, prim = rec.get('items') or [], rec.get('primaryDocument') or []
    for i, f in enumerate(forms):
        if f not in ('8-K', '6-K', '8-K/A', '6-K/A'):
            continue
        try:
            gap = (dt.date.fromisoformat(dates[i]) - d0).days
        except Exception:
            continue
        if gap < -3 or gap > 0:
            continue
        base = 'https://www.sec.gov/Archives/edgar/data/%d/%s/' % (cik, accs[i].replace('-', ''))
        idx = E.get(base + 'index.json')
        if not idx:
            continue
        try:
            names = [x['name'] for x in json.loads(idx)['directory']['item']]
        except Exception:
            continue
        docs = [n for n in names if n.lower().endswith(('.htm', '.html', '.txt')) and not re.match(r'(?i)(R\d+\.htm|.*index.*)$', n)]
        primary = prim[i] if i < len(prim) else ''
        docs.sort(key=lambda n: (n == primary, not re.search(r'(?i)(ex[-_]?99|exhibit99|ex991|press|release)', n), len(n)))
        texts = []
        for n in docs[:3]:
            raw = E.get(base + n)
            if raw:
                t = E.text_of(raw)
                if len(t) > 400:
                    texts.append({'doc': base + n, 'text': t[:20000]})
        it = items[i] if i < len(items) else ''
        out.append({'form': f, 'filed': dates[i], 'items': it, 'about': [ITEMS[x] for x in it.split(',') if x in ITEMS], 'docs': texts})
        if len(out) >= 4:
            break
    return out


def main():
    day, ticks = sys.argv[1], [a.upper() for a in sys.argv[2:]]
    os.makedirs(os.path.join(OUT, 'mv', day), exist_ok=True)
    for t in ticks:
        try:
            cik = int(json.load(open(os.path.join(E.STOCKS, t + '.json'), encoding='utf-8'))['cik'])
        except Exception:
            print(t, 'no CIK'); continue
        fl = filings(cik, day)
        json.dump({'t': t, 'd': day, 'filings': fl or []}, open(os.path.join(OUT, 'mv', day, t + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        print(t, len(fl or []), 'filings', [x['items'] for x in fl or []])


if __name__ == '__main__':
    if not E.UA:
        sys.exit('SEC_USER_AGENT is not set')
    main()
