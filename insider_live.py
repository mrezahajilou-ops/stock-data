#!/usr/bin/env python3
"""Live insider-trading feed for every site: the newest Form 4 filings on SEC EDGAR, open-market buys (P) and sales (S).

Runs every few minutes (.github/workflows/insider-live.yml). Reads the SEC "latest filings" Atom feed, opens each Form 4 it has
not seen yet (the full submission text holds the XML) and keeps one row per filing and code: shares summed, price weighted.
Output: live/live.json on the orphan branch `insider-live`; the worker serves it at /c/insider.json.
Row: a accession, t ticker, co company, n insider, r role, c P|S, d trade date, q shares, p avg price, v value $, h shares held
after, f filed (UTC), x 1 = traded under a 10b5-1 plan, m 1 = joint filing (several owners).
Usage: python insider_live.py [previous live.json]"""
import json, os, re, sys, time, datetime as dt
from xml.etree import ElementTree as ET
from extras import get, SEC_HDR

FEED = ('https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=include&start=%d&count=100&output=atom')
KEEP, SEEN, PER_RUN = 6000, 12000, 150


def x(el, path):
    e = el.find(path) if el is not None else None
    return (e.text or '').strip() if e is not None and e.text else ''


def num(s):
    try:
        return float(str(s).replace(',', ''))
    except Exception:
        return 0.0


def name(n):
    out = []
    for w in re.sub(r'\s+', ' ', n or '').strip().split(' '):
        if len(w) > 1 and (w.isupper() or w.islower()) and not re.match(r'^(II|III|IV|LLC|LP|L\.P\.|INC\.?|JR\.?|SR\.?)$', w, re.I):
            w = w[0].upper() + w[1:].lower()
        out.append(w)
    return ' '.join(out)


def parse(xml, acc, filed):
    try:
        root = ET.fromstring(xml)
    except Exception:
        return []
    t = re.split(r'[,;/\s]+', x(root, 'issuer/issuerTradingSymbol').upper().strip())[0]   # "CRDA, CRDB" -> CRDA
    t = re.sub(r'[^A-Z0-9.\-]', '', t).replace('.', '-')
    if not t or t in ('NONE', 'NA', 'N-A') or len(t) > 8:
        return []
    owners = root.findall('reportingOwner')
    own = owners[0] if owners else None
    rel = own.find('reportingOwnerRelationship') if own is not None else None
    yes = lambda k: x(rel, k).lower() in ('1', 'true')
    if yes('isOfficer'):
        r = re.sub(r'\s+', ' ', x(rel, 'officerTitle') or 'Officer')[:60]
    elif yes('isDirector'):
        r = 'Director'
    elif yes('isTenPercentOwner'):
        r = '10% owner'
    else:
        r = 'Other'
    plan = x(root, 'aff10b5One').lower() in ('1', 'true') or '10b5-1' in xml
    by = {}
    for tr in root.findall('nonDerivativeTable/nonDerivativeTransaction'):
        c = x(tr, 'transactionCoding/transactionCode')
        if c not in ('P', 'S'):
            continue
        q = num(x(tr, 'transactionAmounts/transactionShares/value'))
        p = num(x(tr, 'transactionAmounts/transactionPricePerShare/value'))
        if q <= 0:
            continue
        d = x(tr, 'transactionDate/value')[:10]
        h = num(x(tr, 'postTransactionAmounts/sharesOwnedFollowingTransaction/value'))
        o = by.setdefault(c, {'a': acc, 't': t, 'co': x(root, 'issuer/issuerName'), 'n': name(x(own, 'reportingOwnerId/rptOwnerName')),
                              'r': r, 'c': c, 'd': d, 'q': 0.0, 'v': 0.0, 'h': 0.0, 'f': filed, 'x': 1 if plan else 0,
                              'm': 1 if len(owners) > 1 else 0})
        o['q'] += q
        o['v'] += q * p
        o['d'] = max(o['d'], d)
        if h:
            o['h'] = h
    out = []
    for o in by.values():
        o['p'] = round(o['v'] / o['q'], 2) if o['q'] else 0
        o['q'], o['v'], o['h'] = round(o['q']), round(o['v']), round(o['h'])
        if o['v'] > 1e10 or o['p'] > 1e6:   # a typo in the filing (price in cents, shares in the price box): never shown
            continue
        out.append(o)
    return out


def backfill_todo(days, seen):
    """Form 4 filings of the last `days` business days from EDGAR's daily form index (filed time unknown: 21:00 UTC)."""
    todo, d = [], dt.date.today()
    n = 0
    while n < days:
        d -= dt.timedelta(days=1)
        if d.weekday() > 4:
            continue
        n += 1
        q = (d.month - 1) // 3 + 1
        raw = get('https://www.sec.gov/Archives/edgar/daily-index/%d/QTR%d/form.%s.idx' % (d.year, q, d.strftime('%Y%m%d')), SEC_HDR, timeout=60, tries=2)
        time.sleep(0.15)
        if not raw:
            continue
        for line in raw.decode('latin-1').splitlines():
            if not (line.startswith('4 ') or line.startswith('4/A ')):
                continue
            m = re.search(r'edgar/data/(\d+)/(\d{10}-\d{2}-\d{6})\.txt', line)
            if not m or m.group(2) in seen:
                continue
            acc = m.group(2)
            todo.append((m.group(1), acc.replace('-', ''), acc, d.isoformat() + 'T21:00:00Z'))
    return todo


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    bf = next((int(a.split('=')[1]) for a in sys.argv[1:] if a.startswith('--backfill=')), 0)
    prev = args[0] if args else ''
    st = {'rows': [], 'seen': []}
    if prev and os.path.exists(prev):
        try:
            st = json.load(open(prev))
        except Exception:
            pass
    seen = set(st.get('seen') or [])
    if bf:   # a backfill re-reads everything in its window; rows already kept are de-duplicated below
        seen = set()
    todo, infeed = [], set()
    for start in (0, 100, 200):
        raw = get(FEED % start, SEC_HDR, timeout=30, tries=3)
        if not raw:
            print('feed failed at', start)
            break
        feed = raw.decode('utf-8', 'replace')
        new_here = 0
        for e in feed.split('<entry>')[1:]:
            m = re.search(r'href="[^"]*/edgar/data/(\d+)/(\d{18})/', e)
            if not m:
                continue
            d18 = m.group(2)
            acc = '%s-%s-%s' % (d18[:10], d18[10:12], d18[12:])
            if acc in infeed:
                continue
            infeed.add(acc)
            if acc in seen:
                continue
            new_here += 1
            u = re.search(r'<updated>([^<]+)</updated>', e)
            try:
                f = dt.datetime.fromisoformat(u.group(1)).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                f = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            todo.append((m.group(1), d18, acc, f))
        time.sleep(0.15)
        if not new_here:   # older pages are already known
            break
    global PER_RUN
    if bf:
        todo += backfill_todo(bf, seen | infeed)
        PER_RUN = 20000
    add, done = [], 0
    for cik, d18, acc, f in todo[:PER_RUN]:
        raw = get('https://www.sec.gov/Archives/edgar/data/%s/%s/%s.txt' % (cik, d18, acc), SEC_HDR, timeout=30, tries=2)
        time.sleep(0.11)   # SEC fair access: under 10 requests a second
        if not raw:
            continue
        seen.add(acc)
        done += 1
        txt = raw.decode('utf-8', 'replace')
        m = re.search(r'<ownershipDocument>.*?</ownershipDocument>', txt, re.S)
        if m:
            add.extend(parse(m.group(0), acc, f))
    rows, have = [], set()
    for r in add + (st.get('rows') or []):
        k = (r.get('a'), r.get('c'))
        if (r.get('v') or 0) > 1e10 or (r.get('p') or 0) > 1e6:
            continue
        if k not in have:
            have.add(k)
            rows.append(r)
    rows.sort(key=lambda r: r.get('f') or '', reverse=True)
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    old = list(st.get('seen') or [])
    olds = set(old)
    order = old + [a for _, _, a, _ in reversed(todo[:PER_RUN]) if a in seen and a not in olds]
    out = {'as_of': now, 'src': 'SEC EDGAR Form 4', 'rows': rows[:KEEP], 'seen': order[-SEEN:], 'backlog': max(0, len(todo) - PER_RUN)}
    os.makedirs('live', exist_ok=True)
    json.dump(out, open('live/live.json', 'w'), separators=(',', ':'))
    print('new filings %d, rows added %d, kept %d, backlog %d' % (done, len(add), len(out['rows']), out['backlog']))


if __name__ == '__main__':
    main()
