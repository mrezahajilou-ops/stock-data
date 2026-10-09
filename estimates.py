#!/usr/bin/env python3
"""Analyst consensus estimates (forward P/E, forward P/S, price targets).

Source: Yahoo Finance quoteSummary (earningsTrend, financialData, defaultKeyStatistics), public consensus data.
Output ./estimates/est.json (branch "estimates"):
  {t: {"cur": currency, "fy0": fiscal year end (current year), "e0","e1": EPS estimate current / next fiscal year,
       "r0","r1": revenue estimate current / next fiscal year, "n": analysts, "tgt": mean price target,
       "tlo","thi": low/high target, "rec": recommendation (strong_buy..sell), "rm": recommendation mean 1-5}}
"""
import json, os, sys, time, http.cookiejar, urllib.request, urllib.parse, concurrent.futures as cf, datetime as dt

ROOT = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'estimates')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
CJ = http.cookiejar.CookieJar()
OP = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CJ))
CRUMB = [None]


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.9'})
    with OP.open(req, timeout=timeout) as r:
        return r.read()


def crumb():
    for u in ('https://fc.yahoo.com', 'https://finance.yahoo.com/quote/AAPL'):
        try:
            get(u)
        except Exception:
            pass
    for host in ('query2', 'query1'):
        try:
            c = get('https://%s.finance.yahoo.com/v1/test/getcrumb' % host).decode().strip()
            if c and '<' not in c:
                CRUMB[0] = c
                return c
        except Exception as e:
            print('crumb failed', host, e)
    return None


def raw(x):
    return x.get('raw') if isinstance(x, dict) else x


def one(t):
    sym = t.replace('.', '-')
    url = ('https://query2.finance.yahoo.com/v10/finance/quoteSummary/%s?modules=earningsTrend,financialData,defaultKeyStatistics,summaryDetail&crumb=%s'
           % (urllib.parse.quote(sym), urllib.parse.quote(CRUMB[0] or '')))
    for a in range(3):
        try:
            j = json.loads(get(url))
            res = ((j.get('quoteSummary') or {}).get('result') or [None])[0]
            if not res:
                return t, None
            tr = (res.get('earningsTrend') or {}).get('trend') or []
            fd = res.get('financialData') or {}
            ks = res.get('defaultKeyStatistics') or {}
            sd = res.get('summaryDetail') or {}
            by = {x.get('period'): x for x in tr}
            y0, y1 = by.get('0y') or {}, by.get('+1y') or {}
            q0, q1 = by.get('0q') or {}, by.get('+1q') or {}
            o = {'cur': fd.get('financialCurrency'),
                 'fy0': y0.get('endDate'), 'fy1': y1.get('endDate'),
                 'e0': raw((y0.get('earningsEstimate') or {}).get('avg')), 'e1': raw((y1.get('earningsEstimate') or {}).get('avg')),
                 'r0': raw((y0.get('revenueEstimate') or {}).get('avg')), 'r1': raw((y1.get('revenueEstimate') or {}).get('avg')),
                 'n': raw((y0.get('earningsEstimate') or {}).get('numberOfAnalysts')),
                 'q0': q0.get('endDate'), 'q1': q1.get('endDate'),
                 'qe0': raw((q0.get('earningsEstimate') or {}).get('avg')), 'qe1': raw((q1.get('earningsEstimate') or {}).get('avg')),
                 'qr0': raw((q0.get('revenueEstimate') or {}).get('avg')), 'qr1': raw((q1.get('revenueEstimate') or {}).get('avg')),
                 'tgt': raw(fd.get('targetMeanPrice')), 'tlo': raw(fd.get('targetLowPrice')), 'thi': raw(fd.get('targetHighPrice')),
                 'nt': raw(fd.get('numberOfAnalystOpinions')), 'rec': fd.get('recommendationKey'), 'rm': raw(fd.get('recommendationMean')),
                 'fpe': raw(ks.get('forwardPE')), 'feps': raw(ks.get('forwardEps'))}
            # reference values for the nightly data check (verify_all.py); not shown on the site
            o['ref'] = {k: v for k, v in {
                'mcap': raw(sd.get('marketCap')), 'pe': raw(sd.get('trailingPE')), 'fpe': raw(sd.get('forwardPE')),
                'ps': raw(sd.get('priceToSalesTrailing12Months')), 'divy': raw(sd.get('dividendYield')),
                'pb': raw(ks.get('priceToBook')), 'evebitda': raw(ks.get('enterpriseToEbitda')), 'ev': raw(ks.get('enterpriseValue')),
                'sh': raw(ks.get('sharesOutstanding')), 'rev': raw(fd.get('totalRevenue')), 'ebitda': raw(fd.get('ebitda')),
                'fcf': raw(fd.get('freeCashflow')), 'cfo': raw(fd.get('operatingCashflow')), 'debt': raw(fd.get('totalDebt')),
                'cash': raw(fd.get('totalCash')), 'gm': raw(fd.get('grossMargins')), 'om': raw(fd.get('operatingMargins')),
                'nm': raw(fd.get('profitMargins')), 'roe': raw(fd.get('returnOnEquity')), 'price': raw(fd.get('currentPrice')),
                'teps': raw(ks.get('trailingEps')), 'ni': raw(ks.get('netIncomeToCommon'))}.items() if v is not None}
            if not any(o.get(k) for k in ('e0', 'e1', 'r0', 'tgt')) and not o['ref']:
                return t, None
            return t, {k: v for k, v in o.items() if v not in (None, '', {})}
        except urllib.error.HTTPError as e:
            if e.code == 401 and a == 0:
                crumb(); continue
            if e.code == 429:
                time.sleep(20 * (a + 1)); continue
            return t, None
        except Exception:
            time.sleep(2)
    return t, None


def main():
    os.makedirs(OUT, exist_ok=True)
    sc = json.load(open(os.path.join(ROOT, 'data', 'screener.json')))
    ci = {c: i for i, c in enumerate(sc['cols'])}
    tickers = [r[ci['t']] for r in sc['rows'] if (r[ci['mcap']] or 0) >= 2e8]
    if len(sys.argv) > 1:
        tickers = sys.argv[1:] if not sys.argv[1].isdigit() else tickers[:int(sys.argv[1])]
    print('crumb:', bool(crumb()), 'tickers:', len(tickers))
    out, ok = {}, 0
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for i, (t, o) in enumerate(ex.map(one, tickers)):
            if o:
                out[t] = o; ok += 1
            if i % 500 == 0:
                print(i, ok, round(time.time() - t0), flush=True)
    if ok < max(10, len(tickers) // 4):
        sys.exit('too few estimates (%d of %d) - not publishing' % (ok, len(tickers)))
    json.dump({'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'est': out},
              open(os.path.join(OUT, 'est.json'), 'w'), separators=(',', ':'))
    print('estimates:', ok, 'of', len(tickers))
    for t in ('AAPL', 'CRDO', 'TSM', 'BRK-B'):
        print(t, out.get(t))


if __name__ == '__main__':
    main()
