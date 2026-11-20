#!/usr/bin/env python3
"""Fetch the text of each company's own earnings release, for the written earnings analysis.

When a company reports, it furnishes its press release to the SEC as exhibit 99.1 of an 8-K
(item 2.02); a foreign filer does the same on a 6-K. That release is the primary source for what
management said: the quarter's commentary, the outlook and any guidance. This script finds it for
every large company that reported in the last few days and stores the plain text.

Universe: the largest companies by market value in data/stocks (TOP, default 500).
Input:    earnings/e/<T>.json   (branch "earnings": report dates and the reported figures)
Output:   out/pr/<T>.json       {t, d, form, filed, url, text}   -> branch "earnings-pr"
          out/recent.json       [{t, d, name, mcap, has_pr}]     reports of the last DAYS days

The SEC asks for a contact in the User-Agent; it is read from the environment (SEC_USER_AGENT),
the same value every other SEC job in this repository uses.
"""
import json, os, re, sys, time, html, datetime as dt
import urllib.request, urllib.error

TOP = int(os.environ.get('PR_TOP', '500'))
DAYS = int(os.environ.get('PR_DAYS', '12'))
STOCKS, EARN, OUT = 'data/stocks', 'earnings/e', 'out'
UA = os.environ.get('SEC_USER_AGENT') or os.environ.get('SEC_UA') or ''
HDR = {'User-Agent': UA, 'Accept-Encoding': 'identity'}
TODAY = dt.date.today()
_last = [0.0]


def get(url, tries=3):
    for i in range(tries):
        wait = 0.15 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503):
                time.sleep(3 + 4 * i)
                continue
            return None
        except Exception:
            time.sleep(2 + 2 * i)
    return None


def universe():
    rows = []
    for f in os.listdir(STOCKS):
        if not f.endswith('.json'):
            continue
        try:
            d = json.load(open(os.path.join(STOCKS, f), encoding='utf-8'))
        except Exception:
            continue
        mc = (d.get('market') or {}).get('mcap')
        if mc and d.get('cik'):
            rows.append((mc, f[:-5], int(d['cik']), d.get('name') or f[:-5]))
    rows.sort(reverse=True)
    seen, out = set(), []
    for mc, t, cik, name in rows:          # one listing per company (GOOGL/GOOG share a CIK)
        if cik in seen:
            continue
        seen.add(cik)
        out.append((t, cik, name, mc))
        if len(out) >= TOP:
            break
    return out


def last_report(t):
    try:
        q = json.load(open(os.path.join(EARN, t + '.json'), encoding='utf-8')).get('q') or []
        return q[0]['d'] if q else None
    except Exception:
        return None


def text_of(raw):
    s = raw.decode('utf-8', 'replace')
    s = re.sub(r'(?is)<(script|style|head)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</tr>|</h[1-6]>|</li>', '\n', s)
    s = re.sub(r'(?i)</td>|</th>', ' | ', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'(\s*\|\s*){2,}', ' | ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()


def release(cik, day):
    """(form, filed, url, text) for the earnings release filed around `day`, or None."""
    b = get('https://data.sec.gov/submissions/CIK%010d.json' % cik)
    if not b:
        return None
    try:
        rec = (json.loads(b).get('filings') or {}).get('recent') or {}
    except Exception:
        return None
    d0 = dt.date.fromisoformat(day)
    forms, dates, accs = rec.get('form') or [], rec.get('filingDate') or [], rec.get('accessionNumber') or []
    items, prim = rec.get('items') or [], rec.get('primaryDocument') or []
    cands = []
    for i, f in enumerate(forms):
        if f not in ('8-K', '6-K'):
            continue
        try:
            fd = dt.date.fromisoformat(dates[i])
        except Exception:
            continue
        gap = (fd - d0).days
        if gap < -2 or gap > 4:
            continue
        it = items[i] if i < len(items) else ''
        score = (0 if (f == '8-K' and '2.02' in it) else 1 if f == '6-K' else 2, abs(gap))
        cands.append((score, f, dates[i], accs[i], prim[i] if i < len(prim) else ''))
    for score, form, filed, acc, primary in sorted(cands)[:4]:
        base = 'https://www.sec.gov/Archives/edgar/data/%d/%s/' % (cik, acc.replace('-', ''))
        idx = get(base + 'index.json')
        if not idx:
            continue
        try:
            files = [x['name'] for x in json.loads(idx)['directory']['item']]
        except Exception:
            continue
        docs = [n for n in files if n.lower().endswith(('.htm', '.html', '.txt'))
                and not re.match(r'(?i)(R\d+\.htm|.*index.*|.*-index-headers.*)$', n)]

        def rank(n):
            named = bool(re.search(r'(?i)(ex[-_]?99|exhibit99|ex991|press|earn|release|result)', n))
            first = bool(re.search(r'(?i)99[-_.d]?1(?!\d)', n))
            return (n == primary, not named, not first, len(n))
        best = None
        for n in sorted(docs, key=rank)[:6]:
            raw = get(base + n)
            if not raw:
                continue
            txt = text_of(raw)
            if len(txt) < 1500 or not re.search(r'(?i)(revenue|net income|earnings|quarter)', txt):
                continue
            cover = 'Check the appropriate box' in txt[:6000] or 'CURRENT REPORT' in txt[:1500]
            if not cover:
                return form, filed, base + n, txt[:70000]
            if best is None:
                best = (form, filed, base + n, txt[:70000])
        if best and form == '6-K':
            return best
    return None


def main():
    if not UA:
        sys.exit('SEC_USER_AGENT is not set')
    os.makedirs(os.path.join(OUT, 'pr'), exist_ok=True)
    only = set(a.upper() for a in sys.argv[1:])
    recent, got, miss = [], 0, []
    for t, cik, name, mc in universe():
        d = last_report(t)
        if not d:
            continue
        try:
            age = (TODAY - dt.date.fromisoformat(d)).days
        except Exception:
            continue
        if only and t not in only:
            continue
        if not only and (age < 0 or age > DAYS):
            continue
        path = os.path.join(OUT, 'pr', t + '.json')
        have = None
        if os.path.exists(path):
            try:
                have = json.load(open(path, encoding='utf-8'))
            except Exception:
                have = None
        cover = bool(have and 'Check the appropriate box' in (have.get('text') or '')[:6000])
        if only or cover or not (have and have.get('d') == d and have.get('text')):
            r = release(cik, d)
            if r:
                form, filed, url, txt = r
                json.dump({'t': t, 'd': d, 'form': form, 'filed': filed, 'url': url, 'text': txt},
                          open(path, 'w', encoding='utf-8'), ensure_ascii=False)
                got += 1
                have = {'d': d, 'text': txt}
            else:
                miss.append(t)
        recent.append({'t': t, 'd': d, 'name': name, 'mcap': mc,
                       'has_pr': bool(have and have.get('d') == d and have.get('text'))})
    recent.sort(key=lambda r: (r['d'], r['mcap']), reverse=True)
    if not only:
        json.dump({'as_of': TODAY.isoformat(), 'days': DAYS, 'reports': recent},
                  open(os.path.join(OUT, 'recent.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('reported in window:', len(recent), '| releases fetched now:', got, '| not found:', ' '.join(miss[:40]))


if __name__ == '__main__':
    main()
