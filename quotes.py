#!/usr/bin/env python3
"""Near-live prices for every stock on the site.

Runs every ~15 min during US market hours (see .github/workflows/quotes.yml).
Source: Nasdaq watchlist API (up to 20 symbols per request, ~300 requests per run).

Output: quotes/quotes.json, published as a single commit on the orphan branch `quotes`
(so the main branch history never grows):
  {"as_of": "2026-10-06T14:45:03Z", "status": "Open",
   "q": {"AAPL": [333.69, 1.02, 330.32, "2026-10-06T10:44:59-04:00"], ...}}
  per ticker: [last price, % change vs previous close, previous close, last trade time]
The site scales market cap, EV and every price-based ratio by (live price / build price).
"""
import json, os, sys, time, datetime as dt, urllib.request, urllib.parse, concurrent.futures as cf

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
STOCKS = os.path.join(ROOT, 'data', 'stocks')
OUT = os.path.join(ROOT, 'quotes')
BATCH = 20  # Nasdaq returns at most ~20 symbols per watchlist call
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.9',
       'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}


def num(s):
    if s is None:
        return None
    try:
        return float(str(s).replace('$', '').replace(',', '').replace('%', '').replace('+', '').strip())
    except ValueError:
        return None


ETFS = ['SPY', 'QQQ', 'VOO', 'DIA', 'IWM', 'VTI', 'VT', 'VXUS', 'EFA', 'EEM', 'GLD', 'IAU', 'SLV', 'GDX', 'IBIT', 'FBTC', 'ETHA',
        'TLT', 'IEF', 'SHY', 'BND', 'AGG', 'LQD', 'HYG', 'VNQ', 'XLK', 'XLF', 'XLE', 'XLV', 'XLY', 'XLP', 'XLI', 'XLU', 'XLB',
        'XLC', 'XLRE', 'SMH', 'SOXX', 'ARKK', 'SCHD', 'VIG', 'VYM', 'JEPI', 'USO', 'UNG', 'DBC']  # benchmarks + contest ETFs (contest_data.py)


def fetch(batch):
    qs = '&'.join('symbol=' + urllib.parse.quote(t.replace('-', '.').lower() + ('|etf' if t in ETFS else '|stocks'))
                  for t in batch)
    url = 'https://api.nasdaq.com/api/quote/watchlist?' + qs
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read()).get('data') or []
        except Exception as e:  # 429/403/timeouts: back off and retry
            time.sleep(3 * (attempt + 1))
    return []


def from_worker():
    """Nasdaq refuses GitHub runners (since 2026-11-10): the Cloudflare worker keeps the whole market's quotes."""
    try:
        req = urllib.request.Request('https://rz-events.mreza-hajilou.workers.dev/c/quotes.json', headers={'User-Agent': 'stock-data-quotes'})
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.loads(r.read())
        if len(j.get('q') or {}) > 3000:
            return j
    except Exception as e:
        print('worker quotes failed', e, flush=True)
    return None


def _utc(d):
    """Stamps arrive both with and without a time zone; a naive one is UTC (comparing the two kinds crashed the job)."""
    return d.replace(tzinfo=dt.timezone.utc) if d.tzinfo is None else d


def official_closes(q):
    """Overlay the official closes (close_fix.py -> branch `closes`) on any quote stamped at or before them.
    The screener's last sale can be the previous day's price stamped with today's close time."""
    try:
        url = 'https://raw.githubusercontent.com/' + os.environ.get('GITHUB_REPOSITORY', 'mrezahajilou-ops/stock-data') + '/closes/closes.json'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'stock-data-quotes'}), timeout=30) as r:
            c = json.loads(r.read())
        cs = _utc(dt.datetime.fromisoformat(c['stamp'].replace('Z', '+00:00')))
    except Exception as e:
        print('official closes unavailable', e, flush=True)
        return 0
    n = 0
    for t, v in (c.get('c') or {}).items():
        o = q.get(t)
        try:
            ts = _utc(dt.datetime.fromisoformat(str(o[3]).replace('Z', '+00:00'))) if o else None
        except Exception:
            ts = None
        if o and ts and ts <= cs and v and v[0]:
            q[t] = [v[0], round((v[0] / v[1] - 1) * 100, 2) if v[1] else None, v[1], c['stamp']]
            n += 1
    print('official closes applied:', n, c.get('d'), flush=True)
    return n


# NYSE full-day holidays: on these days (and weekends) the feed can still say "Pre Market", which put a
# "pre-market" label on the previous close on the sites. The market is closed, so say so.
NYSE_HOLIDAYS = {'2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19', '2026-07-03',
                 '2026-09-07', '2026-11-26', '2026-12-25', '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26',
                 '2027-05-31', '2027-06-18', '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24'}


def fix_status(j):
    try:
        from zoneinfo import ZoneInfo
        ny = dt.datetime.now(ZoneInfo('America/New_York'))
    except Exception:
        ny = dt.datetime.utcnow() - dt.timedelta(hours=5)
    if ny.weekday() >= 5 or ny.strftime('%Y-%m-%d') in NYSE_HOLIDAYS:
        j['status'] = 'Closed'
    return j


def main():
    j = from_worker()
    if j:
        official_closes(j['q'])
        fix_status(j)
        os.makedirs(OUT, exist_ok=True)
        json.dump(j, open(os.path.join(OUT, 'quotes.json'), 'w'), separators=(',', ':'))
        print('quotes from the worker:', len(j['q']), j.get('as_of'), j.get('status'), flush=True)
        return
    tickers = sorted(f[:-5] for f in os.listdir(STOCKS) if f.endswith('.json'))
    if len(sys.argv) > 1 and sys.argv[1]:
        tickers = tickers[:int(sys.argv[1])]
    batches = [tickers[i:i + BATCH] for i in range(0, len(tickers), BATCH)] + [ETFS[i:i + BATCH] for i in range(0, len(ETFS), BATCH)]
    q, status = {}, {}
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for rows in ex.map(fetch, batches):
            for d in rows:
                t = (d.get('symbol') or '').upper().replace('.', '-')
                p = num(d.get('lastSalePrice'))
                if not t or not p:
                    continue
                q[t] = [round(p, 4), num(d.get('percentageChange')), num(d.get('previousClosePrice')),
                        d.get('lastTradeTimestampDateTime') or d.get('lastTradeTimestamp')]
                ms = (d.get('marketStatus') or '').lower()
                ms = ('Pre Market' if 'pre' in ms else 'After Hours' if 'after' in ms else
                      'Closed' if 'close' in ms else 'Open' if 'open' in ms else None)
                if ms:
                    status[ms] = status.get(ms, 0) + 1
    print('quotes', len(q), 'of', len(tickers), 'in %.0fs' % (time.time() - t0), status, flush=True)
    if len(q) < len(tickers) * 0.3:
        sys.exit('too few quotes, keeping the previous file')
    os.makedirs(OUT, exist_ok=True)
    official_closes(q)
    out = {'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'status': max(status, key=status.get) if status else None, 'n': len(q), 'q': q}
    fix_status(out)
    json.dump(out, open(os.path.join(OUT, 'quotes.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
