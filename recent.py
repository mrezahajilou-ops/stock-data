#!/usr/bin/env python3
"""Companies that published results in the last days (SEC EDGAR), for the fast earnings lane (fast.yml).

  today:          EDGAR "current events" feed (getcurrent, Atom), 8-K / 10-Q / 10-K / 6-K / 20-F / 40-F
  previous days:  EDGAR daily form index (form.YYYYMMDD.idx)
Writes to $GITHUB_OUTPUT (or prints):
  tickers = every company in data/index.json that filed one of those forms (Yahoo's reported quarter is re-read)
  ciks    = companies that filed a 10-Q / 10-K / 20-F / 40-F (their SEC facts are re-read from the per-company API)
SEC asks for a contact in the User-Agent: set SEC_USER_AGENT (the workflow does).
"""
import json, os, re, sys, time, datetime as dt, urllib.request

UA = os.environ.get('SEC_USER_AGENT', 'stock-data-build')
FORMS = {'8-K', '10-Q', '10-K', '6-K', '20-F', '40-F', '10-Q/A', '10-K/A', '20-F/A', '40-F/A'}
FACTS = {'10-Q', '10-K', '20-F', '40-F', '10-Q/A', '10-K/A', '20-F/A', '40-F/A'}
DAYS = int(os.environ.get('RECENT_DAYS', '3'))


def get(url):
    for a in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode('latin-1')
        except Exception as e:
            print('retry', url, e, file=sys.stderr)
            time.sleep(2 + 3 * a)
    return ''


def current():
    out = []
    for form in ('8-K', '10-Q', '10-K', '6-K', '20-F', '40-F'):
        for start in range(0, 800, 100):
            x = get('https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=%s&company=&dateb=&owner=include&start=%d&count=100&output=atom' % (form, start))
            ents = re.findall(r'<entry>(.*?)</entry>', x, re.S)
            for e in ents:
                t = re.search(r'<title>(.*?)</title>', e, re.S)
                m = re.search(r'\((\d{10})\)', t.group(1) if t else '')
                f = (t.group(1).split(' - ')[0].strip() if t else '')
                if m and f in FORMS:
                    out.append((int(m.group(1)), f))
            time.sleep(0.25)
            if len(ents) < 100:
                break
    print('current feed filings', len(out), file=sys.stderr)
    return out


def daily(day):
    q = (day.month - 1) // 3 + 1
    x = get('https://www.sec.gov/Archives/edgar/daily-index/%d/QTR%d/form.%s.idx' % (day.year, q, day.strftime('%Y%m%d')))
    out = []
    for line in x.splitlines():
        f = line[:12].strip()
        if f in FORMS:
            m = re.search(r'\s(\d{3,10})\s+\d{8}\s', line)
            if m:
                out.append((int(m.group(1)), f))
    print('daily index', day, len(out), file=sys.stderr)
    return out


def main():
    hits = current()
    d = dt.date.today()
    for i in range(1, DAYS + 3):
        day = d - dt.timedelta(days=i)
        if day.weekday() < 5:
            hits += daily(day)
        time.sleep(0.25)
    tick = json.loads(get('https://www.sec.gov/files/company_tickers.json') or '{}')
    by_cik = {}
    for v in tick.values():
        by_cik.setdefault(int(v['cik_str']), []).append(v['ticker'].replace('.', '-'))
    ours = {x['t'] for x in json.load(open(os.path.join('data', 'index.json')))}
    tickers, ciks = set(), set()
    for cik, f in hits:
        ts = [t for t in by_cik.get(cik, []) if t in ours]
        if not ts:
            continue
        tickers.update(ts)
        if f in FACTS:
            ciks.add(cik)
    for t in os.environ.get('EXTRA_TICKERS', '').split():
        tickers.add(t)
    print('filings', len(hits), 'our companies', len(tickers), 'with new XBRL facts', len(ciks), file=sys.stderr)
    res = {'tickers': ' '.join(sorted(tickers)), 'ciks': ','.join(str(c) for c in sorted(ciks))}
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        with open(gh, 'a') as fh:
            for k, v in res.items():
                fh.write('%s=%s\n' % (k, v))
    print(json.dumps({k: v[:300] for k, v in res.items()}))


if __name__ == '__main__':
    main()
