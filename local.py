#!/usr/bin/env python3
"""End-of-day data for the local exchanges of the language sites (Tokyo, Seoul, São Paulo).

Source: Yahoo Finance (quoteSummary, fundamentals time series, chart) with the same session/crumb as estimates.py.
Prices are end-of-day; all money values are in the company's own trading currency (JPY, KRW, BRL).
Output ./local/<market>.json (branch "local"):
  {"as_of", "market", "cur", "rows": {code: {...}}}  code = the local code without the Yahoo suffix (7203, 005930, PETR4)
"""
import json, os, sys, time, urllib.parse, urllib.error, datetime as dt, concurrent.futures as cf
import estimates as Y
from local_lists import MARKETS

OUT = os.path.join(Y.ROOT, 'local')
CUR = {'jp': 'JPY', 'kr': 'KRW', 'br': 'BRL'}
FLOW = ['TotalRevenue', 'OperatingIncome', 'NetIncomeCommonStockholders', 'OperatingCashFlow', 'CapitalExpenditure',
        'FreeCashFlow', 'DilutedEPS', 'CashDividendsPaid', 'GrossProfit']
BAL = ['CashCashEquivalentsAndShortTermInvestments', 'TotalDebt', 'StockholdersEquity', 'TotalAssets']
QF = ['TotalRevenue', 'OperatingIncome', 'NetIncomeCommonStockholders']
r = Y.raw


def jget(url):
    for a in range(3):
        try:
            return json.loads(Y.get(url, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 401 and a == 0:
                Y.crumb(); continue
            if e.code == 429:
                time.sleep(15 * (a + 1)); continue
            if e.code == 404:
                return None
        except Exception:
            time.sleep(2)
    return None


def timeseries(sym):
    types = ['annual' + x for x in FLOW] + ['quarterly' + x for x in QF] + ['quarterly' + x for x in BAL] + ['trailing' + x for x in FLOW]
    url = ('https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/%s?symbol=%s&type=%s&period1=%d&period2=%d&crumb=%s'
           % (urllib.parse.quote(sym), urllib.parse.quote(sym), ','.join(types), int(time.time()) - 6 * 366 * 86400, int(time.time()) + 86400,
              urllib.parse.quote(Y.CRUMB[0] or '')))
    j = jget(url)
    out = {}
    for s in ((j or {}).get('timeseries') or {}).get('result') or []:
        ty = (s.get('meta') or {}).get('type', [None])[0]
        if not ty:
            continue
        pts = [[p.get('asOfDate'), r(p.get('reportedValue'))] for p in (s.get(ty) or []) if p and r(p.get('reportedValue')) is not None]
        if pts:
            out[ty] = sorted(pts)
    return out


def chart(sym):
    j = jget('https://query2.finance.yahoo.com/v8/finance/chart/%s?range=5y&interval=1wk&includeAdjustedClose=false' % urllib.parse.quote(sym))
    res = (((j or {}).get('chart') or {}).get('result') or [None])[0]
    if not res:
        return None, None
    ts = res.get('timestamp') or []
    cl = ((res.get('indicators') or {}).get('quote') or [{}])[0].get('close') or []
    wk = [[dt.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d'), round(c, 2)] for t, c in zip(ts, cl) if c is not None]
    return wk, res.get('meta') or {}


def one(item):
    sym, name = item
    url = ('https://query2.finance.yahoo.com/v10/finance/quoteSummary/%s?modules=price,summaryDetail,defaultKeyStatistics,financialData,assetProfile,calendarEvents&crumb=%s'
           % (urllib.parse.quote(sym), urllib.parse.quote(Y.CRUMB[0] or '')))
    j = jget(url)
    res = (((j or {}).get('quoteSummary') or {}).get('result') or [None])[0]
    if not res:
        return sym, None
    pr, sd, ks, fd, ap = (res.get(k) or {} for k in ('price', 'summaryDetail', 'defaultKeyStatistics', 'financialData', 'assetProfile'))
    price = r(pr.get('regularMarketPrice'))
    if not price:
        return sym, None
    ce = res.get('calendarEvents') or {}
    ed = [r(x) for x in ((ce.get('earnings') or {}).get('earningsDate') or [])]
    o = {'sym': sym, 'name': name, 'name_en': pr.get('longName') or pr.get('shortName'), 'cur': pr.get('currency'),
         'exch': pr.get('exchangeName'), 'sector': ap.get('sector'), 'industry': ap.get('industry'), 'emp': ap.get('fullTimeEmployees'),
         'web': ap.get('website'), 'city': ap.get('city'),
         'price': price, 'chg': r(pr.get('regularMarketChangePercent')), 'pt': r(pr.get('regularMarketTime')),
         'mcap': r(pr.get('marketCap')) or r(sd.get('marketCap')), 'pe': r(sd.get('trailingPE')), 'fpe': r(sd.get('forwardPE')) or r(ks.get('forwardPE')),
         'pb': r(ks.get('priceToBook')), 'ps': r(sd.get('priceToSalesTrailing12Months')), 'divy': r(sd.get('dividendYield')),
         'dps': r(sd.get('dividendRate')), 'payout': r(sd.get('payoutRatio')), 'beta': r(sd.get('beta')),
         'hi52': r(sd.get('fiftyTwoWeekHigh')), 'lo52': r(sd.get('fiftyTwoWeekLow')), 'ma200': r(sd.get('twoHundredDayAverage')),
         'eveb': r(ks.get('enterpriseToEbitda')), 'sh': r(ks.get('sharesOutstanding')),
         'roe': r(fd.get('returnOnEquity')), 'gm': r(fd.get('grossMargins')), 'om': r(fd.get('operatingMargins')), 'nm': r(fd.get('profitMargins')),
         'rg': r(fd.get('revenueGrowth')), 'eg': r(fd.get('earningsGrowth')), 'de': r(fd.get('debtToEquity')),
         'tgt': r(fd.get('targetMeanPrice')), 'tlo': r(fd.get('targetLowPrice')), 'thi': r(fd.get('targetHighPrice')),
         'nt': r(fd.get('numberOfAnalystOpinions')), 'rec': fd.get('recommendationKey'),
         'fcur': fd.get('financialCurrency'), 'next': [x for x in ed if x][:1]}
    if isinstance(o['pt'], (int, float)):
        o['pt'] = dt.datetime.utcfromtimestamp(o['pt']).strftime('%Y-%m-%d')
    try:
        o['ts'] = timeseries(sym)
    except Exception as e:
        print('ts', sym, e)
    try:
        o['wk'], meta = chart(sym)
    except Exception as e:
        print('chart', sym, e)
    return sym, {k: v for k, v in o.items() if v not in (None, '', [], {})}


def main():
    os.makedirs(OUT, exist_ok=True)
    mk = sys.argv[1:] or list(MARKETS)
    print('crumb:', bool(Y.crumb()))
    for m in mk:
        items = list(MARKETS[m].items())
        rows = {}
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for sym, o in ex.map(one, items):
                if o:
                    rows[sym.split('.')[0]] = o
                else:
                    print('  no data:', sym)
        print(m, len(rows), 'of', len(items))
        if len(rows) < len(items) // 2:
            print('too few rows for', m, '- not written'); continue
        json.dump({'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'market': m, 'cur': CUR[m], 'rows': rows},
                  open(os.path.join(OUT, m + '.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
        k = next(iter(rows))
        print(k, json.dumps({a: b for a, b in rows[k].items() if a not in ('wk', 'ts')}, ensure_ascii=False)[:900])
        print('ts keys', sorted(rows[k].get('ts', {}).keys()))


if __name__ == '__main__':
    main()
