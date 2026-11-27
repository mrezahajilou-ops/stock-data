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
import glob, json, os, sys, time, datetime as dt, urllib.request, urllib.error, gzip, concurrent.futures as cf

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


def yahoo_actuals(tickers):
    """Reported EPS (and the quarter's revenue) from Yahoo, which has them hours after the earnings release;
    Nasdaq's calendar often fills the actual EPS only the next day.
    -> {ticker: {"YYYY-MM": {"act", "f", "rev"}}} keyed by quarter-end month."""
    if not tickers:
        return {}
    try:
        sys.path.insert(0, ROOT)
        import estimates as Y
        Y.crumb()
    except Exception as e:
        print('yahoo unavailable', e)
        return {}
    import urllib.parse
    out = {}
    for t in tickers:
        url = ('https://query2.finance.yahoo.com/v10/finance/quoteSummary/%s?modules=earningsHistory,earnings&crumb=%s'
               % (urllib.parse.quote(t.replace('.', '-')), urllib.parse.quote(Y.CRUMB[0] or '')))
        try:
            res = ((json.loads(Y.get(url)).get('quoteSummary') or {}).get('result') or [None])[0] or {}
        except Exception:
            continue
        hist = [h for h in (res.get('earningsHistory') or {}).get('history') or [] if Y.raw(h.get('epsActual')) is not None
                and isinstance(Y.raw(h.get('quarter')), (int, float))]
        hist.sort(key=lambda h: Y.raw(h['quarter']))
        chart = (((res.get('earnings') or {}).get('financialsChart') or {}).get('quarterly')) or []
        d = {}
        for i, h in enumerate(hist):
            qe = dt.datetime.utcfromtimestamp(Y.raw(h['quarter'])).date()
            rec = {'act': Y.raw(h['epsActual']), 'f': Y.raw(h.get('epsEstimate'))}
            if i == len(hist) - 1 and chart and Y.raw((chart[-1].get('revenue') or {})):
                rec['rev'] = Y.raw(chart[-1]['revenue'])   # newest quarter of the chart = newest reported quarter
            for k in (qe, qe - dt.timedelta(days=8)):       # 52/53-week years end a few days into the next month
                d.setdefault('%04d-%02d' % (k.year, k.month), rec)
        if d:
            out[t] = d
        time.sleep(0.4)
    print('yahoo actuals:', len(out), 'of', len(tickers))
    return out


def qkey(qlabel):
    try:
        mon, yr = qlabel.split('/')
        return '%04d-%02d' % (int(yr), dt.datetime.strptime(mon[:3], '%b').month)
    except Exception:
        return None


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
    pending = []   # reported in the last days but Nasdaq has no actual EPS yet
    # Nasdaq gives the time of day of a report (before the open / after the close) only until the report is out; afterwards
    # the field is empty. Without it the reaction cannot tell the first trading day after the report, so the time is kept
    # here from the days before the report (state['tm'], "TICKER|date" -> pre|after) and reused once Nasdaq drops it.
    tmk = state.setdefault('tm', {})
    for k in range(1, 4):
        d2 = TODAY + dt.timedelta(days=k)
        if d2.weekday() >= 5:
            continue
        for r in cal_day(d2.isoformat()) or []:
            t2 = (r.get('symbol') or '').strip().upper().replace('.', '-').replace('/', '-')
            if TIME.get(r.get('time')):
                tmk['%s|%s' % (t2, d2.isoformat())] = TIME[r['time']]
        time.sleep(0.35)
    old_keys = [k2 for k2 in tmk if k2.split('|')[1] < (TODAY - dt.timedelta(days=30)).isoformat()]
    for k2 in old_keys:
        del tmk[k2]

    def when(t, ds, r):
        v = TIME.get(r.get('time'))
        if v:
            tmk['%s|%s' % (t, ds)] = v
            return v
        return tmk.get('%s|%s' % (t, ds), 'na')

    for ds in want:
        rows = cal_day(ds)
        if rows is None:
            continue
        for r in rows:
            t = (r.get('symbol') or '').strip().upper().replace('.', '-').replace('/', '-')
            mc = num(r.get('marketCap'))
            act = num(r.get('eps'))
            if t not in cover or not mc or mc < 1e9:
                continue
            if act is None:
                if (TODAY - dt.date.fromisoformat(ds)).days <= 4 and ds <= TODAY.isoformat():
                    pending.append((ds, t, r))
                continue
            rec = {'d': ds, 'tm': when(t, ds, r), 'q': r.get('fiscalQuarterEnding'), 'act': act,
                   'f': num(r.get('epsForecast')), 'sur': num(r.get('surprise')), 'ly': num(r.get('lastYearEPS'))}
            e = db.setdefault(t, {'t': t, 'q': []})
            old = [x for x in e['q'] if x.get('q') == rec['q']]
            if old:
                for k2 in ('act', 'f', 'sur', 'ly', 'tm', 'd'):
                    if rec.get(k2) is None or (k2 == 'tm' and rec[k2] == 'na' and old[0].get('tm') in ('pre', 'after')):
                        continue      # a known time of day is never replaced by "unknown"
                    if k2 in ('tm', 'd') and old[0].get(k2) != rec[k2]:
                        old[0].pop('rx', None)      # the reaction depends on both: work it out again
                    old[0][k2] = rec[k2]
            else:
                e['q'].append(rec)
            touched.add(t)
        if (TODAY - dt.date.fromisoformat(ds)).days > 10:
            done.add(ds)
        time.sleep(0.35)
    # Yahoo fallback for today's / the last days' reports Nasdaq hasn't filled yet
    ya = yahoo_actuals(sorted({t for _, t, _ in pending}))
    nya = 0
    for ds, t, r in pending:
        k = qkey(r.get('fiscalQuarterEnding') or '')
        y = (ya.get(t) or {}).get(k)
        if not y or y.get('act') is None:
            continue
        f = num(r.get('epsForecast'))
        if f is None:
            f = y.get('f')
        rec = {'d': ds, 'tm': when(t, ds, r), 'q': r.get('fiscalQuarterEnding'), 'act': y['act'], 'f': f,
               'sur': round((y['act'] - f) / abs(f) * 100, 2) if f else None, 'ly': num(r.get('lastYearEPS')), 'src': 'yahoo'}
        if y.get('rev'):
            rec['rev'] = y['rev']
        e = db.setdefault(t, {'t': t, 'q': []})
        old = [x for x in e['q'] if x.get('q') == rec['q']]
        if old:
            if old[0].get('act') is None or old[0].get('src') == 'yahoo':
                if rec.get('tm') == 'na' and old[0].get('tm') in ('pre', 'after'):
                    rec.pop('tm')
                elif rec.get('tm') != old[0].get('tm'):
                    old[0].pop('rx', None)
                old[0].update({k2: v for k2, v in rec.items() if v is not None})
        else:
            e['q'].append(rec)
        touched.add(t)
        nya += 1
    print('calendar days read: %d, companies updated: %d (yahoo fallback: %d of %d pending)' % (len(want), len(touched), nya, len(pending)))

    # 1b) quarters the calendar run missed. 94 of the 500 largest companies had no record for the Jan-Feb 2026
    # reports (the job was not running every day then), so a stock page jumped from October to April. Nasdaq's
    # per-company earnings-surprise table has the last four reports; a missing one is added from it.
    def surprise_rows(t):
        b = get('https://api.nasdaq.com/api/company/%s/earnings-surprise' % t.replace('.', '%2E'), NHDR, tries=2)
        try:
            return (((json.loads(b).get('data') or {}).get('earningsSurpriseTable') or {}).get('rows')) or []
        except Exception:
            return []

    def has_gap(e):
        ds = sorted((x['d'] for x in e['q'] if x.get('d')), reverse=True)[:6]
        return any((dt.date.fromisoformat(a2) - dt.date.fromisoformat(b2)).days > 135 for a2, b2 in zip(ds, ds[1:]))

    try:
        mcap = {}
        for f in glob.glob(os.path.join(STOCKS, '*.json')):
            try:
                mcap[os.path.basename(f)[:-5]] = (json.load(open(f)).get('market') or {}).get('mcap') or 0
            except Exception:
                pass
        gap_t = [t for t in sorted(db, key=lambda t: -mcap.get(t, 0))[:int(os.environ.get('GAP_TOP') or 1500)] if has_gap(db[t])]
    except Exception as ex:
        print('gap check failed:', ex)
        gap_t = []
    nadd = 0
    for t in gap_t[:int(os.environ.get('GAP_PER_RUN') or 250)]:
        e = db[t]
        have = {x.get('q') for x in e['q']}
        for r in surprise_rows(t):
            qq = (r.get('fiscalQtrEnd') or '').replace(' ', '/')
            act = num(r.get('eps'))
            try:
                mo, da, yr = (r.get('dateReported') or '').split('/')
                d0 = '%04d-%02d-%02d' % (int(yr), int(mo), int(da))
            except Exception:
                continue
            if not qq or qq in have or act is None:
                continue
            f = num(r.get('consensusForecast'))
            e['q'].append({'d': d0, 'tm': 'na', 'q': qq, 'act': act, 'f': f,
                           'sur': round((act - f) / abs(f) * 100, 2) if f else None, 'ly': None, 'src': 'nasdaq-surprise'})
            have.add(qq)
            nadd += 1
        time.sleep(0.35)
    print('missing quarters added from the earnings-surprise table: %d (companies with a gap: %d)' % (nadd, len(gap_t)))

    # 2) price reaction + revenue for records that miss them (recent ones keep trying for 75 days)
    # time of day from the SEC: once a report is out Nasdaq no longer says whether it came before the open or after the
    # close, and without that the reaction would have to span two trading days. The moment the SEC accepted the company's
    # 8-K with its results (item 2.02) tells it. A few hundred companies per run; each report is looked up once.
    def filed_when(cik):
        b = sec('https://data.sec.gov/submissions/CIK%010d.json' % int(cik))
        try:
            rec = (json.loads(b).get('filings') or {}).get('recent') or {}
        except Exception:
            return None
        from zoneinfo import ZoneInfo
        ny, out = ZoneInfo('America/New_York'), []
        forms, items, acc = rec.get('form') or [], rec.get('items') or [], rec.get('acceptanceDateTime') or []
        for i, f in enumerate(forms):
            if f != '8-K' or i >= len(items) or i >= len(acc) or '2.02' not in (items[i] or ''):
                continue
            try:
                u = dt.datetime.fromisoformat(acc[i].replace('Z', '+00:00')).astimezone(ny)
            except Exception:
                continue
            out.append((u.date(), 'after' if (u.hour, u.minute) >= (16, 0) else 'pre'))
        return out

    def need_tm(x):
        return x.get('tm', 'na') == 'na' and not x.get('tmno') and (TODAY - dt.date.fromisoformat(x['d'])).days <= 400
    ntm, t1 = 0, time.time()
    for t in [t for t, e in db.items() if any(need_tm(x) for x in e['q'])][:int(os.environ.get('TM_PER_RUN') or 400)]:
        try:
            cik = json.load(open(os.path.join(STOCKS, t + '.json'))).get('cik')
        except Exception:
            cik = None
        fl = filed_when(cik) if cik else None
        if fl is None and cik:
            continue                      # the SEC did not answer: try again next run
        for x in db[t]['q']:
            if not need_tm(x):
                continue
            d0, tm = dt.date.fromisoformat(x['d']), None
            for fd, w in fl or []:
                gap = (fd - d0).days
                if gap == 0:
                    tm = w
                elif -3 <= gap < 0 and w == 'after':
                    tm = 'pre'            # released after the close of the trading day before: the reaction is on the report date
                elif 0 < gap <= 3 and w == 'pre':
                    tm = 'after'
                if tm:
                    break
            if tm:
                x['tm'] = tm
                x.pop('rx', None)
                x.pop('rxno', None)
                ntm += 1
            else:
                x['tmno'] = 1
        if time.time() - t1 > 600:
            break
    print('time of day found from SEC filings: %d reports' % ntm)
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
    # revenue a year earlier, from the company's own quarterly table, where the quarter's revenue came from Yahoo
    # (so the SEC step above never ran): the earnings tables showed a dash under "revenue growth" for the newest quarter
    MON = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
    for t, e in db.items():
        miss = [x for x in e['q'] if x.get('rev') and not x.get('revly') and '/' in (x.get('q') or '')]
        if not miss:
            continue
        try:
            qs = json.load(open(os.path.join(STOCKS, t + '.json'))).get('quarterly') or []
        except Exception:
            continue
        for x in miss:
            mo, yr = x['q'].split('/')[:2]
            if mo[:3] not in MON or not yr.isdigit():
                continue
            k = int(yr) * 12 + MON[mo[:3]] - 12   # same quarter, one year earlier
            for row in qs:
                try:
                    km = int(row[0][:4]) * 12 + int(row[0][5:7])
                except Exception:
                    continue
                if len(row) >= 2 and row[1] and abs(km - k) <= 1:
                    x['revly'] = row[1]
                    break

    # one basis for actual vs expected EPS: Nasdaq sometimes pairs the GAAP result with the adjusted consensus
    # (Credo: GAAP 0.78 vs adjusted forecast 0.93 = a fake "miss"). Yahoo's earnings history has both on the
    # analysts' (adjusted) basis, so use it wherever it has the quarter.
    try:
        E = json.load(open(os.path.join(ROOT, 'estimates', 'est.json'))).get('est') or {}
    except Exception:
        E = {}
    nfix = 0
    for t, e in db.items():
        eh = (E.get(t) or {}).get('eh') or []
        by = {}
        for qd, a, f in eh:
            d0 = dt.date.fromisoformat(qd)
            for k in (d0, d0 - dt.timedelta(days=8)):
                by.setdefault('%04d-%02d' % (k.year, k.month), (a, f))
        for x in e['q']:
            y = by.get(qkey(x.get('q') or ''))
            if not y or y[0] is None:
                continue
            a, f = y
            if f is None:
                f = x.get('f')
            if x.get('act') != a or x.get('f') != f:
                nfix += 1
            x['act'], x['f'] = a, f
            x['sur'] = round((a - f) / abs(f) * 100, 2) if f else None
            x['eb'] = 'adj'        # analysts' basis
    print('EPS put on one basis (Yahoo):', nfix)

    # EPS a year ago from our own history when the calendar did not give it
    for t, e in db.items():
        by = {x.get('q'): x for x in e['q']}
        for x in e['q']:
            if (x.get('ly') is None or x.get('eb') == 'adj') and x.get('q') and '/' in x['q']:
                mon, yr = x['q'].split('/')
                prev = by.get('%s/%d' % (mon, int(yr) - 1)) if yr.isdigit() else None
                if prev and prev.get('act') is not None and (x.get('eb') != 'adj' or prev.get('eb') == 'adj' or x.get('ly') is None):
                    x['ly'] = prev['act']
    # corrections checked by hand against the company's own release (data/earnings_fix.json): they win over every feed.
    # {"WSM": {"Oct/2026": {"act": 2.19, "why": "..."}}} - 'act' and 'ly' are EPS, the surprise is worked out again
    try:
        fixes = json.load(open(os.path.join(os.path.dirname(STOCKS), 'earnings_fix.json')))
    except Exception:
        fixes = {}
    nfx = 0
    for t, qs in fixes.items():
        # {"drop_d": "2026-11-16"}: a report that did not happen on that date (a feed booked the quarter before the
        # company published it); only that dated row goes, so the real report replaces it when it comes
        rows = (db.get(t) or {}).get('q') or []
        keep = [x for x in rows if not ((qs.get(x.get('q')) or {}).get('drop_d') == x.get('d'))]
        if len(keep) != len(rows):
            db[t]['q'] = keep
            nfx += len(rows) - len(keep)
        for x in keep:
            fx = qs.get(x.get('q'))
            if not fx or fx.get('drop_d'):
                continue
            for k2 in ('act', 'ly', 'f', 'd'):
                if fx.get(k2) is not None:
                    x[k2] = fx[k2]
            if x.get('act') is not None and x.get('f'):
                x['sur'] = round((x['act'] - x['f']) / abs(x['f']) * 100, 2)
            x['fix'] = fx.get('why', 1)
            nfx += 1
    print('hand-checked corrections applied:', nfx)
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
