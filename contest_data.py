#!/usr/bin/env python3
"""Data for the portfolio contest (events/contest.js), published on the orphan branch `contest-data`.

  universe.json  {"as_of", "t": [allowed tickers], "etf": {ticker: name}}
                 US stocks with market cap >= $1B and price >= $5 (data/screener.json) plus the ETF list below.
  corp.json      {"as_of", "events": [{"t", "type": "div"|"split", "d": ex-date, "v": cash per share | split ratio}]}
                 for tickers currently held in the contest (worker GET /c/tickers), last 21 days, from Yahoo chart events.
The worker credits each dividend / applies each split once (idempotent), so re-publishing old events is harmless.

  python contest_data.py <screener.json> <outdir> [worker_url]
"""
import json, os, sys, time, datetime as dt, urllib.request

ETFS = {
    'SPY': 'S&P 500', 'VOO': 'S&P 500 (Vanguard)', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones', 'IWM': 'Russell 2000',
    'VTI': 'Total US market', 'VT': 'Total world', 'VXUS': 'World ex-US', 'EFA': 'Developed markets', 'EEM': 'Emerging markets',
    'GLD': 'Gold', 'IAU': 'Gold (iShares)', 'SLV': 'Silver', 'GDX': 'Gold miners', 'IBIT': 'Bitcoin', 'FBTC': 'Bitcoin (Fidelity)',
    'ETHA': 'Ethereum', 'TLT': 'US Treasuries 20y+', 'IEF': 'US Treasuries 7-10y', 'SHY': 'US Treasuries 1-3y', 'BND': 'US bonds',
    'AGG': 'US bonds (iShares)', 'LQD': 'Corporate bonds', 'HYG': 'High-yield bonds', 'VNQ': 'Real estate (REITs)',
    'XLK': 'Technology sector', 'XLF': 'Financial sector', 'XLE': 'Energy sector', 'XLV': 'Health care sector',
    'XLY': 'Consumer discretionary', 'XLP': 'Consumer staples', 'XLI': 'Industrials', 'XLU': 'Utilities', 'XLB': 'Materials',
    'XLC': 'Communication services', 'XLRE': 'Real estate sector', 'SMH': 'Semiconductors', 'SOXX': 'Semiconductors (iShares)',
    'ARKK': 'ARK Innovation', 'SCHD': 'US dividend', 'VIG': 'Dividend growth', 'VYM': 'High dividend', 'JEPI': 'Equity premium income',
    'USO': 'Oil', 'UNG': 'Natural gas', 'DBC': 'Commodities',
}
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def universe(screener_path):
    s = json.load(open(screener_path))
    c = {k: i for i, k in enumerate(s['cols'])}
    out = set(ETFS)
    for r in s['rows']:
        px, mc = r[c['price']], r[c['mcap']]
        if px and mc and px >= 5 and mc >= 1e9:
            out.add(r[c['t']])
    return sorted(out)


def corp_events(tickers):
    """Yahoo chart events (dividends, splits) for the last 21 days."""
    ev, end = [], int(time.time()) + 86400
    start = end - 22 * 86400
    for t in tickers:
        url = ('https://query2.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d&events=div%%7Csplit'
               % (t.replace('.', '-'), start, end))
        try:
            j = get_json(url)
            e = ((j.get('chart') or {}).get('result') or [{}])[0].get('events') or {}
        except Exception as x:
            print('corp', t, 'failed', x)
            continue
        for d in (e.get('dividends') or {}).values():
            if d.get('amount'):
                ev.append({'t': t, 'type': 'div', 'd': dt.datetime.utcfromtimestamp(d['date']).strftime('%Y-%m-%d'), 'v': round(d['amount'], 6)})
        for s in (e.get('splits') or {}).values():
            num, den = s.get('numerator'), s.get('denominator')
            if num and den and num != den:
                ev.append({'t': t, 'type': 'split', 'd': dt.datetime.utcfromtimestamp(s['date']).strftime('%Y-%m-%d'), 'v': round(num / den, 6)})
        time.sleep(0.3)
    return ev


def main():
    screener, out = sys.argv[1], sys.argv[2]
    worker = sys.argv[3] if len(sys.argv) > 3 else ''
    os.makedirs(out, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    u = universe(screener)
    json.dump({'as_of': now, 't': u, 'etf': ETFS}, open(os.path.join(out, 'universe.json'), 'w'), separators=(',', ':'))
    held = []
    if worker:
        try:
            held = get_json(worker.rstrip('/') + '/c/tickers').get('t') or []
        except Exception as x:
            print('held tickers failed', x)
    ev = corp_events(held)
    json.dump({'as_of': now, 'events': ev}, open(os.path.join(out, 'corp.json'), 'w'), separators=(',', ':'))
    print('universe', len(u), 'held', len(held), 'corp events', len(ev))


if __name__ == '__main__':
    main()
