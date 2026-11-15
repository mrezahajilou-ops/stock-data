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
N = int(os.environ.get('N') or 300)
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
    if prior and fy:
        return D[fy[0]][0] + D[ytd][0] - D[prior[0]][0], end, 'fy+ytd-prior'
    # fallback: sum of the last four 3-month quarters
    qs = sorted([k for k in D if 80 <= days(*k) <= 100], key=lambda k: k[1])[-4:]
    if len(qs) == 4 and days(qs[0][1], end) < 300:
        return sum(D[k][0] for k in qs), end, '4q'
    return None

def ours(d):
    T = d.get('ttm') or {}
    L = d.get('latest') or {}
    if T.get('end'):
        return {'end': T['end'], 'revenue': T.get('revenue'), 'net_income': T.get('net_income'), 'eps': T.get('eps')}
    return {'end': L.get('fy_end'), 'revenue': L.get('revenue'), 'net_income': L.get('net_income'), 'eps': L.get('eps_diluted')}

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
        b = get('https://data.sec.gov/api/xbrl/companyfacts/CIK%010d.json' % int(d['cik']))
        if not b:
            report['skipped'].append([t, 'no companyfacts']); continue
        facts = json.loads(b).get('facts') or {}
        report['checked'] += 1
        o = ours(d)
        ref = {}
        for k, tags, unit in (('revenue', REV_TAGS, 'USD'), ('net_income', NI_TAGS, 'USD'), ('eps', EPS_TAGS, 'USD/shares')):
            v = ttm(duration_facts(facts, tags, unit))
            if v:
                ref[k] = v
        if not ref:
            report['skipped'].append([t, 'no comparable facts']); continue
        sec_end = max(v[1] for v in ref.values())
        if o['end'] and sec_end > o['end'] and days(o['end'], sec_end) >= 60:
            report['stale'].append({'t': t, 'ours': o['end'], 'sec': sec_end}); continue
        bad = []
        for k, (v, end, how) in ref.items():
            x = o.get(k)
            if end != o['end'] or x is None or v is None:
                continue
            base = max(abs(v), abs(x), 1e-9)
            diff = abs(x - v) / base
            if k == 'eps' and abs(x - v) <= 0.02:
                continue
            if diff > TOL[k]:
                bad.append({'k': k, 'ours': x, 'sec': v, 'diff': round(diff, 4), 'how': how, 'end': end})
        if bad:
            report['mismatch'].append({'t': t, 'mcap': r[ci['mcap']], 'items': bad})
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
