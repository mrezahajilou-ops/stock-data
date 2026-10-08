#!/usr/bin/env python3
"""Quarterly earnings history for the stock pages (Persian "latest report" card).

Keeps ./earnings (published to the branch "earnings"):
  e/<TICKER>.json  {"t":..,"q":[{"d","tm","q","act","f","sur","ly","rev","revly","rx"}, ...]}  newest first, max 8
     d = report date, tm = pre|after|na, q = fiscal quarter ending ("Jun/2026"), act/f = reported / expected EPS,
     sur = surprise %, ly = EPS same quarter last year, rev/revly = quarterly revenue now / a year ago (SEC),
     rx = share price reaction on the first trading day after the report
  state.json       which calendar days were already read
Sources: Nasdaq earnings calendar (EPS), Nasdaq daily chart (reaction), SEC companyfacts (revenue).
Only companies covered on the site with a market cap of at least $1B.
"""
import json, os, sys, time, datetime as dt, urllib.request, urllib.error, gzip, concurrent.futures as cf

ROOT = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'earnings')
STOCKS = os.path.join(ROOT, 'data', 'stocks')
UA_SEC = os.environ.get('SEC_USER_AGENT', 'Reza Hajilou mreza.hajilou@gmail.com')
NHDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}
TIME = {'time-pre-market': 'pre', 'time-after-hours': 'after'}
TODAY = dt.date.today()
BACK_DAYS = 400          # first run: read this many days of the calendar
MAX_NEW_DAYS = 160       # calendar days read per run (spreads the backfill over a few runs)
KEEP = 9
REV_TAGS = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax',
            'SalesRevenueNet', 'SalesRevenueGoodsNet', 'RevenuesNetOfInterestExpense', 'InterestAndDividendIncomeOperating']


def num(s):
    if s in (None, '', 'N/A'):
        return None
    s = str(s).replace('$', '').replace(',', '').replace('%', '').strip()
    neg = s.startswith('(') and s.endswith(')')
    try:
        v = float(s.strip('()'))
    except ValueError:
        return None
    return -v if neg else v


def get(url, headers, tries=4, timeout=40):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
                b = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    b = gzip.decompress(b)
                return b
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(4 * (a + 1))
        except Exception:
            time.sleep(3 * (a + 1))
    return None


def cal_day(d):
    b = get('https://api.nasdaq.com/api/calendar/earnings?date=' + d, NHDR)
    try:
        return ((json.loads(b).get('data') or {}).get('rows')) or []
    except Exception:
        return None


def daily(t, frm):
    b = get('https://api.nasdaq.com/api/quote/%s/chart?assetclass=stocks&fromdate=%s&todate=%s' % (t.replace('.', '%2E'), frm, TODAY.isoformat()), NHDR, tries=3)
    if not b:
        return []
    try:
        ch = ((json.loads(b).get('data') or {}).get('chart')) or []
    except Exception:
        return []
    rows = []
    for p in ch:
        z = p.get('z') or {}
        d, c = z.get('dateTime'), z.get('value')
        try:
            mm, dd, yy = d.split('/')
            rows.append(['%04d-%02d-%02d' % (int(yy), int(mm), int(dd)), float(str(c).replace(',', ''))])
        except Exception:
            pass
    rows.sort()
    return rows


def reaction(rows, d, tm):
    if not rows:
        return None
    idx = {r[0]: i for i, r in enumerate(rows)}
    before = [i for i, r in enumerate(rows) if r[0] < d]
    after = [i for i, r in enumerate(rows) if r[0] > d]
    on = idx.get(d)
    if tm == 'pre':
        if on is None or not before:
            return None
        a, b = rows[before[-1]][1], rows[on][1]
    elif tm == 'after':
        if on is None or not after:
            return None
        a, b = rows[on][1], rows[after[0]][1]
    else:
        if not before or not after:
            return None
        a, b = rows[before[-1]][1], rows[after[0]][1]
    return round(b / a - 1, 4) if a else None


_last = [0.0]


def sec(url):
    w = 0.13 - (time.time() - _last[0])
    if w > 0:
        time.sleep(w)
    _last[0] = time.time()
    return get(url, {'User-Agent': UA_SEC, 'Accept-Encoding': 'gzip'}, tries=3, timeout=60)


def quarters(cik):
    """{quarter end 'YYYY-MM-DD': revenue} from SEC companyfacts (Q4 = fiscal year minus Q1-Q3)."""
    b = sec('https://data.sec.gov/api/xbrl/companyfacts/CIK%010d.json' % int(cik))
    if not b:
        return {}
    facts = (json.loads(b).get('facts') or {}).get('us-gaap') or {}
    cands = []
    for tag in REV_TAGS:
        units = ((facts.get(tag) or {}).get('units') or {}).get('USD') or []
        q, y = {}, []
        for u in units:
            if not u.get('start') or u.get('form') not in ('10-Q', '10-K', '10-Q/A', '10-K/A'):
                continue
            s, e = dt.date.fromisoformat(u['start']), dt.date.fromisoformat(u['end'])
            n = (e - s).days
            if 80 <= n <= 100:
                q[u['end']] = u['val']
            elif 350 <= n <= 380:
                y.append((s, e, u['val']))
        for s, e, v in y:
            k = e.isoformat()
            inside = [val for end, val in q.items() if s < dt.date.fromisoformat(end) < e]
            if k not in q and len(inside) == 3:
                q[k] = v - sum(inside)
        if q:
            cands.append((max(q), len(q), q))
    if not cands:
        return {}
    cands.sort(key=lambda c: (c[0], c[1]), reverse=True)
    return cands[0][2]


def match(qmap, qlabel, years_back=0):
    """qlabel 'Jun/2026' -> revenue of the quarter ending in that month (+- a few days)."""
    try:
        mon, yr = qlabel.split('/')
        m = dt.datetime.strptime(mon[:3], '%b').month
        y = int(yr) - years_back
    except Exception:
        return None
    for k, v in qmap.items():
        e = dt.date.fromisoformat(k)
        e2 = e - dt.timedelta(days=8)  # 52/53-week years end a few days into the next month
        if (e.year, e.month) == (y, m) or (e2.year, e2.month) == (y, m):
            return v
    return None


def main():
    os.makedirs(os.path.join(OUT, 'e'), exist_ok=True)
    try:
        state = json.load(open(os.path.join(OUT, 'state.json')))
    except Exception:
        state = {'days': []}
    done = set(state.get('days') or [])
    cover = {}
    for f in os.listdir(STOCKS):
        if f.endswith('.json'):
            cover[f[:-5]] = None
    db = {}
    for f in os.listdir(os.path.join(OUT, 'e')):
        try:
            db[f[:-5]] = json.load(open(os.path.join(OUT, 'e', f)))
        except Exception:
            pass

    # 1) calendar days: the last 10 days are always re-read (late EPS updates), older ones once
    want = []
    for k in range(0, BACK_DAYS):
        d = TODAY - dt.timedelta(days=k)
        if d.weekday() >= 5:
            continue
        ds = d.isoformat()
        if k <= 10 or ds not in done:
            want.append(ds)
    want = want[:MAX_NEW_DAYS]
    touched = set()
    for ds in want:
        rows = cal_day(ds)
        if rows is None:
            continue
        for r in rows:
            t = (r.get('symbol') or '').strip().upper().replace('.', '-').replace('/', '-')
            mc = num(r.get('marketCap'))
            act = num(r.get('eps'))
            if t not in cover or not mc or mc < 1e9 or act is None:
                continue
            rec = {'d': ds, 'tm': TIME.get(r.get('time'), 'na'), 'q': r.get('fiscalQuarterEnding'), 'act': act,
                   'f': num(r.get('epsForecast')), 'sur': num(r.get('surprise')), 'ly': num(r.get('lastYearEPS'))}
            e = db.setdefault(t, {'t': t, 'q': []})
            old = [x for x in e['q'] if x.get('q') == rec['q']]
            if old:
                for k2 in ('act', 'f', 'sur', 'ly', 'tm', 'd'):
                    if rec.get(k2) is not None:
                        old[0][k2] = rec[k2]
            else:
                e['q'].append(rec)
            touched.add(t)
        if (TODAY - dt.date.fromisoformat(ds)).days > 10:
            done.add(ds)
        time.sleep(0.35)
    print('calendar days read: %d, companies updated: %d' % (len(want), len(touched)))

    # 2) price reaction + revenue for records that miss them (recent ones keep trying for 75 days)
    need_rx = [t for t, e in db.items() if any(x.get('rx') is None and (TODAY - dt.date.fromisoformat(x['d'])).days <= 400
                                              and not x.get('rxno') for x in e['q'])]
    need_rev = [t for t, e in db.items() if any(x.get('rev') is None and not x.get('revno') for x in e['q'])]
    print('need reaction: %d, need revenue: %d' % (len(need_rx), len(need_rev)))
    frm = (TODAY - dt.timedelta(days=430)).isoformat()

    def rx_one(t):
        return t, daily(t, frm)
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for t, rows in ex.map(rx_one, need_rx[:1500]):
            for x in db[t]['q']:
                if x.get('rx') is None:
                    v = reaction(rows, x['d'], x.get('tm'))
                    if v is not None:
                        x['rx'] = v
                    elif rows and rows[-1][0] > x['d'] and (TODAY - dt.date.fromisoformat(x['d'])).days > 7:
                        x['rxno'] = 1
            if time.time() - t0 > 1500:
                break
    for i, t in enumerate(need_rev[:1500]):
        try:
            cik = json.load(open(os.path.join(STOCKS, t + '.json'))).get('cik')
            qm = quarters(cik) if cik else {}
        except Exception:
            qm = {}
        for x in db[t]['q']:
            if x.get('rev') is None:
                v = match(qm, x.get('q') or '')
                if v:
                    x['rev'] = v
                    x['revly'] = match(qm, x.get('q') or '', 1)
                elif (TODAY - dt.date.fromisoformat(x['d'])).days > 75:
                    x['revno'] = 1
        if time.time() - t0 > 3000:
            break

    # EPS a year ago from our own history when the calendar did not give it
    for t, e in db.items():
        by = {x.get('q'): x for x in e['q']}
        for x in e['q']:
            if x.get('ly') is None and x.get('q') and '/' in x['q']:
                mon, yr = x['q'].split('/')
                prev = by.get('%s/%d' % (mon, int(yr) - 1)) if yr.isdigit() else None
                if prev and prev.get('act') is not None:
                    x['ly'] = prev['act']
    n = 0
    for t, e in db.items():
        e['q'] = sorted(e['q'], key=lambda x: x['d'], reverse=True)[:KEEP]
        json.dump(e, open(os.path.join(OUT, 'e', t + '.json'), 'w'), separators=(',', ':'))
        n += 1
    state['days'] = sorted(done)[-BACK_DAYS:]
    state['as_of'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    json.dump(state, open(os.path.join(OUT, 'state.json'), 'w'))
    print('companies with earnings history: %d' % n)


if __name__ == '__main__':
    main()
