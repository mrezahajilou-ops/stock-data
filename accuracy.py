#!/usr/bin/env python3
"""Accuracy & freshness guard (built for stockanaliz.com, protects sahamanaliz.com too).

Independent of build.py: for the largest US companies it downloads the SEC companyfacts and recomputes the trailing
12 months (TTM) of revenue, net income and diluted EPS on its own (last annual + current year-to-date - prior
year-to-date), then compares them with data/stocks/<T>.json.

Checks
  stale      SEC has a newer 10-Q/10-K period than our TTM -> the ticker is queued for the fast lane (auto-heal)
  mismatch   our TTM differs from the independent SEC value beyond tolerance (revenue 1%, net income 2%, EPS 3%)
  estimates  analyst consensus file (estimates branch) older than 36 h on a weekday
  closes     official closes not from the last trading day
Writes accuracy/accuracy.json (published to the branch "accuracy"); prints ::error:: lines and exits 1 when the
problems pass the alert thresholds, so the workflow run fails and GitHub notifies the owner.
Env: SEC_USER_AGENT, N (companies, default 300), HEAL_OUT (file that receives the stale tickers).
"""
import gzip, json, os, sys, time, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'accuracy')
UA = os.environ.get('SEC_USER_AGENT') or 'Stock Analiz data check info@stockanaliz.com'
N = int(os.environ.get('N') or 1000)
TOL = {'revenue': 0.01, 'net_income': 0.02, 'eps': 0.03}
REV_TAGS = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax',
            'SalesRevenueNet', 'RevenuesNetOfInterestExpense', 'TotalRevenuesAndOtherIncome']
NI_TAGS = ['NetIncomeLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic', 'ProfitLoss']
EPS_TAGS = ['EarningsPerShareDiluted', 'EarningsPerShareBasicAndDiluted']

_last = [0.0]
def get(url, tries=4):
    for i in range(tries):
        dt = time.time() - _last[0]
        if dt < 0.12:
            time.sleep(0.12 - dt)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                return gzip.decompress(b) if r.headers.get('Content-Encoding') == 'gzip' else b
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return None

def days(a, b):
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days

def duration_facts(facts, tags, unit):
    """Best tag: the one whose duration facts reach the latest period end. Returns {(start, end): (val, filed, form)}."""
    best, best_end = None, ''
    for tag in tags:
        node = (facts.get('us-gaap') or {}).get(tag)
        if not node:
            continue
        rows = (node.get('units') or {}).get(unit) or []
        D = {}
        for r in rows:
            if not r.get('start') or r.get('form') not in ('10-Q', '10-K', '10-Q/A', '10-K/A'):
                continue
            k = (r['start'], r['end'])
            # a full-year value comes from a 10-K; a 10-Q sometimes mis-tags a quarter with a 12-month period (Comfort Systems)
            if k in D and days(*k) >= 350 and D[k][2].startswith('10-K') != r['form'].startswith('10-K'):
                if r['form'].startswith('10-K'):
                    D[k] = (r['val'], r['filed'], r['form'])
                continue
            if k not in D or r['filed'] > D[k][1]:
                D[k] = (r['val'], r['filed'], r['form'])
        if not D:
            continue
        end = max(k[1] for k in D)
        if end > best_end:
            best, best_end = D, end
    return best or {}

def ttm(D):
    """(value, period_end, method) from duration facts: annual if the latest end is a fiscal year end, else
    last annual + current YTD - prior-year YTD of the same length."""
    if not D:
        return None
    end = max(k[1] for k in D)
    cur = [k for k in D if k[1] == end]
    ann = [k for k in cur if 350 <= days(k[0], k[1]) <= 380]
    if ann:
        return D[ann[0]][0], end, 'annual'
    q = [k for k in cur if 80 <= days(k[0], k[1]) <= 100]
    ytd = sorted(cur, key=lambda k: days(k[0], k[1]))[-1]
    L = days(*ytd)
    if L > 300:
        return None
    prior = [k for k in D if abs(days(k[1], end) - 365) <= 12 and abs(days(*k) - L) <= 12]
    fy = [k for k in D if 350 <= days(*k) <= 380 and 0 <= days(k[1], ytd[0]) <= 12]
    pv = D[prior[0]][0] if prior else None
    if pv is None and fy:
        # prior-year YTD not tagged on its own: a longer prior YTD minus its last quarter (CrowdStrike)
        for lk in D:
            if lk[0] == fy[0][0] and 70 <= days(*lk) - L <= 110:
                qk = [k for k in D if k[1] == lk[1] and 80 <= days(*k) <= 100]
                if qk:
                    pv = D[lk][0] - D[qk[0]][0]
                    break
    if pv is not None and fy:
        return D[fy[0]][0] + D[ytd][0] - pv, end, 'fy+ytd-prior'
    # fallback: sum of the last four 3-month quarters
    qs = sorted([k for k in D if 80 <= days(*k) <= 100], key=lambda k: k[1])[-4:]
    # four distinct, back-to-back quarters only (52/53-week filers tag overlapping periods)
    chain = len(qs) == 4 and all(0 < days(qs[i][1], qs[i + 1][0]) <= 7 for i in range(3))
    vals = sorted(abs(D[k][0]) for k in qs) if len(qs) == 4 else []
    # a full year mis-tagged as a quarter (L3Harris) is ~4x the other quarters
    if chain and vals and vals[-1] > 2.5 * max(vals[1], 1):
        chain = False
    if chain and qs[-1][1] == end:
        return sum(D[k][0] for k in qs), end, '4q'
    return None

def ours(d):
    T = d.get('ttm') or {}
    L = d.get('latest') or {}
    if T.get('end'):
        return {'end': T['end'], 'revenue': T.get('revenue'), 'net_income': T.get('net_income'), 'eps': T.get('eps')}
    return {'end': L.get('fy_end'), 'revenue': L.get('revenue'), 'net_income': L.get('net_income'), 'eps': L.get('eps_diluted')}

SPLITS = [2, 3, 4, 5, 6, 8, 10, 13, 15, 20, 25, 50, 100]
_EST = {}

def yeps_of(t):
    """Independent trailing diluted EPS (Yahoo, estimates branch) - already restated for splits and per ADS."""
    if not _EST:
        try:
            _EST.update(json.loads(os.popen('git show origin/estimates:est.json 2>/dev/null').read() or '{}').get('est') or {})
        except Exception:
            pass
        _EST.setdefault('_', 1)
    v = ((_EST.get(t) or {}).get('ref') or {}).get('teps')
    return v if isinstance(v, (int, float)) else None

def agree(x, v, tol, k):
    if x is None or v is None:
        return False
    if k == 'eps' and abs(x - v) <= 0.02:
        return True
    return abs(x - v) / max(abs(v), abs(x), 1e-9) <= tol

def check(t, d, facts, yeps=None):
    """-> ('ok'|'bad'|'stale'|'skip', payload). Every SEC revenue / net-income tag is tried on its own: our figure is
    confirmed when it equals the TTM of any tag the company reports (banks, brokers and REITs use different revenue
    lines). EPS is also confirmed by the independent split-adjusted trailing EPS, or by a clean split / ADS ratio."""
    o = ours(d)
    refs = {}
    for k, tags, unit in (('revenue', REV_TAGS, 'USD'), ('net_income', NI_TAGS, 'USD'), ('eps', EPS_TAGS, 'USD/shares')):
        for tag in tags:
            v = ttm(duration_facts(facts, [tag], unit))
            if v and v[0] is not None:
                refs.setdefault(k, []).append(v + (tag,))
    if not refs:
        return 'skip', 'no comparable facts'
    sec_end = max(v[1] for L in refs.values() for v in L)
    if o['end'] and sec_end > o['end'] and days(o['end'], sec_end) >= 60:
        return 'stale', {'t': t, 'ours': o['end'], 'sec': sec_end}
    bad = []
    for k, L in refs.items():
        x = o.get(k)
        same = [v for v in L if o['end'] and abs(days(v[1], o['end'])) <= 10]
        if x is None or not same:
            continue
        if any(agree(x, v[0], TOL[k], k) for v in same):
            continue
        if k == 'eps':
            if yeps is not None and agree(x, yeps, TOL[k], k):
                continue
            if (d.get('split_adj') or d.get('share_factor')) and any(
                    v[0] and x and any(abs((v[0] / x) / F - 1) < 0.06 or abs((x / v[0]) / F - 1) < 0.06 for F in SPLITS) for v in same):
                continue
        v = min(same, key=lambda v: abs(v[0] - x))
        bad.append({'k': k, 'ours': x, 'sec': v[0], 'diff': round(abs(x - v[0]) / max(abs(v[0]), abs(x), 1e-9), 4),
                    'how': v[2], 'tag': v[3], 'end': v[1], 'yahoo': yeps if k == 'eps' else None})
    if bad:
        return 'bad', {'t': t, 'items': bad}
    return 'ok', None

def last_trading_day(now):
    d = now.date()
    if now.hour < 21:          # before ~4pm New York the official close is yesterday's
        d -= datetime.timedelta(days=1)
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d.isoformat()

def main():
    os.makedirs(OUT, exist_ok=True)
    now = datetime.datetime.utcnow()
    sc = json.load(open(os.path.join(ROOT, 'data', 'screener.json')))
    ci = {c: i for i, c in enumerate(sc['cols'])}
    rows = sorted(sc['rows'], key=lambda r: -(r[ci['mcap']] or 0))
    report = {'as_of': now.strftime('%Y-%m-%dT%H:%MZ'), 'checked': 0, 'stale': [], 'mismatch': [], 'ok': 0, 'skipped': [], 'feeds': {}}
    seen_cik = set()
    for r in rows:
        if report['checked'] >= N:
            break
        t = r[ci['t']]
        p = os.path.join(ROOT, 'data', 'stocks', t + '.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        if d.get('foreign') or (d.get('reported_currency') or 'USD') != 'USD' or not d.get('cik'):
            continue
        if d['cik'] in seen_cik:
            continue   # second ticker of the same filer (class B, preferred, baby bond): same filings
        seen_cik.add(d['cik'])
        b = get('https://data.sec.gov/api/xbrl/companyfacts/CIK%010d.json' % int(d['cik']))
        if not b:
            report['skipped'].append([t, 'no companyfacts']); continue
        facts = json.loads(b).get('facts') or {}
        report['checked'] += 1
        st, payload = check(t, d, facts, yeps_of(t))
        if st == 'skip':
            report['skipped'].append([t, payload])
        elif st == 'stale':
            report['stale'].append(payload)
        elif st == 'bad':
            payload['mcap'] = r[ci['mcap']]
            report['mismatch'].append(payload)
        else:
            report['ok'] += 1
    # feed freshness
    try:
        est = json.loads(os.popen('git show origin/estimates:est.json 2>/dev/null').read() or '{}')
        a = est.get('as_of')
        if a:
            age = (now - datetime.datetime.strptime(a, '%Y-%m-%dT%H:%MZ')).total_seconds() / 3600
            report['feeds']['estimates'] = {'as_of': a, 'age_h': round(age, 1), 'ok': age <= 36 or now.weekday() >= 5 or (now.weekday() == 0 and age <= 84)}
    except Exception as e:
        report['feeds']['estimates'] = {'error': str(e)[:120], 'ok': False}
    try:
        cl = json.loads(os.popen('git show origin/closes:closes.json 2>/dev/null').read() or '{}')
        want = last_trading_day(now)
        report['feeds']['closes'] = {'d': cl.get('d'), 'want': want, 'ok': (cl.get('d') or '') >= want}
    except Exception as e:
        report['feeds']['closes'] = {'error': str(e)[:120], 'ok': False}

    json.dump(report, open(os.path.join(OUT, 'accuracy.json'), 'w'), separators=(',', ':'))
    heal = [s['t'] for s in report['stale']]
    if os.environ.get('HEAL_OUT'):
        open(os.environ['HEAL_OUT'], 'w').write(' '.join(heal[:60]))
    c = report['checked'] or 1
    print('checked %d, ok %d, stale %d, mismatch %d, skipped %d' % (report['checked'], report['ok'], len(report['stale']), len(report['mismatch']), len(report['skipped'])))
    for s in report['stale'][:30]:
        print('stale %s: ours %s, SEC %s' % (s['t'], s['ours'], s['sec']))
    for m in report['mismatch'][:40]:
        print('mismatch %s: %s' % (m['t'], '; '.join('%s ours %s vs SEC %s (%.1f%%, %s)' % (i['k'], i['ours'], i['sec'], i['diff'] * 100, i['how']) for i in m['items'])))
    fail = []
    if len(report['mismatch']) / c > 0.03:
        fail.append('%d TTM mismatches vs SEC among the %d largest companies' % (len(report['mismatch']), report['checked']))
    if len(report['stale']) > 15:
        fail.append('%d stocks behind the latest SEC filing' % len(report['stale']))
    for k, f in report['feeds'].items():
        if not f.get('ok'):
            fail.append('feed %s not fresh: %s' % (k, f))
    for f in fail:
        print('::error::' + f)
    return 1 if fail else 0

if __name__ == '__main__':
    sys.exit(main())
