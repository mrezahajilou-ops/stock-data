#!/usr/bin/env python3
"""Key statistics, quarterly statements and analyst detail for the stock pages' financials section.

  python keystats.py NVDA,AAPL      -> keystats/<T>.json

Sources (public data):
  Yahoo Finance quoteSummary: ownership (insiders, institutions), float, short interest, beta, 52-week range,
    analyst estimate ranges (low/avg/high), monthly recommendation trend, analyst rating changes, earnings dates.
  Yahoo Finance fundamentals time series: quarterly income statement, balance sheet and cash flow (last ~8 quarters)
    and the annual line items SEC's companyfacts feed does not give us cleanly.
  Yahoo Finance chart: one year of daily prices and volumes -> 50/200-day averages, RSI, average volume.
Published by .github/workflows/keystats.yml to the orphan branch `keystats`.
"""
import json, os, sys, time, urllib.parse, datetime as dt
from estimates import get, crumb, CRUMB, raw

ROOT = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'keystats')

INC = ['TotalRevenue', 'CostOfRevenue', 'GrossProfit', 'ResearchAndDevelopment', 'SellingGeneralAndAdministration', 'OperatingExpense',
       'OperatingIncome', 'InterestExpense', 'InterestIncome', 'PretaxIncome', 'TaxProvision', 'NetIncome', 'NetIncomeCommonStockholders',
       'BasicEPS', 'DilutedEPS', 'BasicAverageShares', 'DilutedAverageShares', 'EBITDA', 'EBIT', 'TaxRateForCalcs']
BAL = ['CashAndCashEquivalents', 'OtherShortTermInvestments', 'CashCashEquivalentsAndShortTermInvestments', 'AccountsReceivable', 'Inventory',
       'OtherCurrentAssets', 'CurrentAssets', 'NetPPE', 'Goodwill', 'OtherIntangibleAssets', 'TotalAssets', 'AccountsPayable',
       'CurrentDebt', 'CurrentLiabilities', 'LongTermDebt', 'TotalDebt', 'TotalLiabilitiesNetMinorityInterest', 'StockholdersEquity',
       'RetainedEarnings', 'WorkingCapital', 'TangibleBookValue', 'OrdinarySharesNumber']
CF = ['NetIncomeFromContinuingOperations', 'DepreciationAndAmortization', 'StockBasedCompensation', 'ChangeInWorkingCapital',
      'OperatingCashFlow', 'CapitalExpenditure', 'PurchaseOfBusiness', 'InvestingCashFlow', 'RepurchaseOfCapitalStock', 'CashDividendsPaid',
      'IssuanceOfDebt', 'RepaymentOfDebt', 'FinancingCashFlow', 'FreeCashFlow', 'EndCashPosition']


def timeseries(t, types, freq):
    sym = t.replace('.', '-')
    out = {}
    for i in range(0, len(types), 12):
        chunk = [freq + x for x in types[i:i + 12]]
        url = ('https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/%s?symbol=%s&type=%s&period1=%d&period2=%d&crumb=%s'
               % (urllib.parse.quote(sym), urllib.parse.quote(sym), ','.join(chunk), int(time.time()) - 9 * 365 * 86400,
                  int(time.time()) + 86400, urllib.parse.quote(CRUMB[0] or '')))
        for a in range(3):
            try:
                j = json.loads(get(url))
                for r in ((j.get('timeseries') or {}).get('result')) or []:
                    ty = ((r.get('meta') or {}).get('type') or [None])[0]
                    pts = [p for p in (r.get(ty) or []) if p and isinstance(p.get('reportedValue'), dict)]
                    if ty and pts:
                        out[ty[len(freq):]] = {p['asOfDate']: p['reportedValue'].get('raw') for p in pts}
                break
            except Exception as e:
                time.sleep(4 * (a + 1))
    # pivot: {date: {field: value}}
    piv = {}
    for k, ser in out.items():
        for d, v in ser.items():
            piv.setdefault(d, {})[k] = v
    return [dict(end=d, **piv[d]) for d in sorted(piv)]


def summary(t):
    mods = 'defaultKeyStatistics,summaryDetail,majorHoldersBreakdown,earningsTrend,recommendationTrend,upgradeDowngradeHistory,calendarEvents,financialData,price'
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/%s?modules=%s&crumb=%s' % (urllib.parse.quote(t.replace('.', '-')), mods, urllib.parse.quote(CRUMB[0] or ''))
    for a in range(3):
        try:
            j = json.loads(get(url))
            return ((j.get('quoteSummary') or {}).get('result') or [None])[0]
        except Exception:
            time.sleep(4 * (a + 1))
            crumb()
    return None


def chart(t):
    url = 'https://query2.finance.yahoo.com/v8/finance/chart/%s?range=1y&interval=1d' % urllib.parse.quote(t.replace('.', '-'))
    try:
        r = ((json.loads(get(url)).get('chart') or {}).get('result') or [None])[0] or {}
        q = ((r.get('indicators') or {}).get('quote') or [{}])[0]
        rows = [(ts, c, v) for ts, c, v in zip(r.get('timestamp') or [], q.get('close') or [], q.get('volume') or []) if c]
        return rows
    except Exception:
        return []


def rsi(closes, n=14):
    if len(closes) <= n:
        return None
    g = l = 0.0
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        g += max(d, 0); l += max(-d, 0)
    ag, al = g / n, l / n
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (n - 1) + max(d, 0)) / n
        al = (al * (n - 1) + max(-d, 0)) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)


def one(t):
    s = summary(t) or {}
    ks, sd, mh, fd = (s.get('defaultKeyStatistics') or {}), (s.get('summaryDetail') or {}), (s.get('majorHoldersBreakdown') or {}), (s.get('financialData') or {})
    o = {'t': t, 'updated': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}
    o['stats'] = {k: raw(v) for k, v in {
        'float': ks.get('floatShares'), 'shares_out': ks.get('sharesOutstanding'), 'insiders': mh.get('insidersPercentHeld') or ks.get('heldPercentInsiders'),
        'institutions': mh.get('institutionsPercentHeld') or ks.get('heldPercentInstitutions'), 'inst_count': mh.get('institutionsCount'),
        'short': ks.get('sharesShort'), 'short_float': ks.get('shortPercentOfFloat'), 'short_ratio': ks.get('shortRatio'),
        'short_date': ks.get('dateShortInterest'), 'beta': ks.get('beta') or sd.get('beta'), 'chg52': ks.get('52WeekChange'),
        'lo52': sd.get('fiftyTwoWeekLow'), 'hi52': sd.get('fiftyTwoWeekHigh'), 'avgvol': sd.get('averageVolume'),
        'avgvol10': sd.get('averageVolume10days'), 'exdiv': sd.get('exDividendDate'), 'divrate': sd.get('dividendRate'),
        'tgt_median': fd.get('targetMedianPrice'), 'tgt_mean': fd.get('targetMeanPrice'), 'tgt_lo': fd.get('targetLowPrice'), 'tgt_hi': fd.get('targetHighPrice'),
        'n_analysts': fd.get('numberOfAnalystOpinions')}.items() if raw(v) is not None}
    ce = s.get('calendarEvents') or {}
    er = (ce.get('earnings') or {})
    o['dates'] = {'earnings': [raw(x) for x in (er.get('earningsDate') or [])], 'earnings_est': bool(er.get('isEarningsDateEstimate')),
                  'exdiv': raw(ce.get('exDividendDate')), 'divpay': raw(ce.get('dividendDate'))}
    o['trend'] = [{'p': x.get('period'), 'end': x.get('endDate'), 'g': raw(x.get('growth')),
                   'eps': {k: raw((x.get('earningsEstimate') or {}).get(k)) for k in ('avg', 'low', 'high', 'yearAgoEps', 'numberOfAnalysts', 'growth')},
                   'rev': {k: raw((x.get('revenueEstimate') or {}).get(k)) for k in ('avg', 'low', 'high', 'yearAgoRevenue', 'numberOfAnalysts', 'growth')}}
                  for x in ((s.get('earningsTrend') or {}).get('trend') or []) if x.get('period') in ('0q', '+1q', '0y', '+1y')]
    o['recs'] = [{k: x.get(k) for k in ('period', 'strongBuy', 'buy', 'hold', 'sell', 'strongSell')} for x in ((s.get('recommendationTrend') or {}).get('trend') or [])]
    hist = ((s.get('upgradeDowngradeHistory') or {}).get('history') or [])
    o['actions'] = [{'d': x.get('epochGradeDate'), 'firm': x.get('firm'), 'to': x.get('toGrade'), 'from': x.get('fromGrade'), 'act': x.get('action'),
                     'pt': x.get('currentPriceTarget'), 'ppt': x.get('priorPriceTarget'), 'pta': x.get('priceTargetAction')} for x in hist[:25]]
    rows = chart(t)
    if rows:
        c = [r[1] for r in rows]; v = [r[2] or 0 for r in rows]
        o['price'] = {'ma50': sum(c[-50:]) / min(50, len(c)), 'ma200': sum(c[-200:]) / min(200, len(c)) if len(c) >= 150 else None,
                      'rsi': rsi(c[-120:]), 'vol20': sum(v[-20:]) / min(20, len(v)), 'lo1y': min(c), 'hi1y': max(c), 'first': c[0], 'last': c[-1],
                      'asof': dt.datetime.utcfromtimestamp(rows[-1][0]).strftime('%Y-%m-%d')}
    o['q_inc'] = timeseries(t, INC, 'quarterly')
    o['q_bal'] = timeseries(t, BAL, 'quarterly')
    o['q_cf'] = timeseries(t, CF, 'quarterly')
    o['a_inc'] = timeseries(t, INC, 'annual')
    o['a_bal'] = timeseries(t, BAL, 'annual')
    o['a_cf'] = timeseries(t, CF, 'annual')
    return o


def all_tickers():
    import glob
    out = []
    for f in glob.glob(os.path.join(ROOT, 'data', 'stocks', '*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get('annual'):
            out.append((-(((d.get('market') or {}).get('mcap')) or 0), d['ticker']))
    return [t for _, t in sorted(out)]


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    if arg.upper() == 'ALL':
        ts = all_tickers()
        shard, n = int(os.environ.get('SHARD', '0')), int(os.environ.get('SHARDS', '1'))
        ts = ts[shard::n]
    else:
        ts = [x.strip().upper() for x in arg.split(',') if x.strip()]
    os.makedirs(OUT, exist_ok=True)
    print('crumb:', bool(crumb()), 'tickers:', len(ts))
    t0 = time.time()
    for t in ts:
        if time.time() - t0 > float(os.environ.get('MAX_SEC', '1e9')):
            print('time budget reached'); break
        try:
            o = one(t)
        except Exception as e:
            print(t, 'failed', e); continue
        json.dump(o, open(os.path.join(OUT, t + '.json'), 'w'), separators=(',', ':'))
        print(t, 'stats', len(o['stats']), 'q_inc', len(o['q_inc']), 'q_bal', len(o['q_bal']), 'q_cf', len(o['q_cf']),
              'a_inc', len(o['a_inc']), 'trend', len(o['trend']), 'recs', len(o['recs']), 'actions', len(o['actions']), 'price', bool(o.get('price')))
        time.sleep(0.3)


if __name__ == '__main__':
    main()
