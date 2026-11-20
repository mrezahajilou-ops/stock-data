#!/usr/bin/env python3
"""Probe which public sources actually serve ETF holdings, prices and profile data.

Runs in Actions (the container that writes the site has no route to these hosts), prints what each
candidate returned, and writes nothing. The point is to find out which endpoints work before
etf_data.py is written against them, rather than guessing and debugging through the build.
"""
import json, sys, time, urllib.request, urllib.error, csv, io

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124 Safari/537.36')
NASDAQ_HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*',
              'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}
PLAIN_HDR = {'User-Agent': UA, 'Accept': '*/*'}


def get(url, hdr=None, timeout=45):
    req = urllib.request.Request(url, headers=hdr or PLAIN_HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def probe(label, url, hdr=None, show=240):
    try:
        st, body = get(url, hdr)
    except urllib.error.HTTPError as ex:
        print('  [%-28s] HTTP %s' % (label, ex.code))
        return None
    except Exception as ex:
        print('  [%-28s] FAIL %s' % (label, type(ex).__name__ + ': ' + str(ex)[:90]))
        return None
    head = body[:show].decode('utf-8', 'replace').replace('\n', ' | ')
    print('  [%-28s] %s  %d bytes  %s' % (label, st, len(body), head))
    return body


def main():
    print('=== 1. Nasdaq: ETF profile / summary (expense ratio, AUM, returns) ===')
    for t in ('QQQ', 'VOO', 'SPY'):
        print(' ', t)
        probe('summary', 'https://api.nasdaq.com/api/quote/%s/summary?assetclass=etf' % t, NASDAQ_HDR)
        probe('info', 'https://api.nasdaq.com/api/quote/%s/info?assetclass=etf' % t, NASDAQ_HDR)
        probe('etf/holdings', 'https://api.nasdaq.com/api/etf/%s/holdings?limit=50' % t.lower(), NASDAQ_HDR)
        probe('etf/profile', 'https://api.nasdaq.com/api/etf/%s/profile' % t.lower(), NASDAQ_HDR)
        time.sleep(1)

    print()
    print('=== 2. Invesco holdings CSV (QQQ and friends) ===')
    probe('invesco QQQ csv',
          'https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0'
          '?audienceType=Investor&action=download&ticker=QQQ')

    print()
    print('=== 3. State Street / SPDR daily holdings ===')
    probe('ssga SPY xlsx',
          'https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx')
    probe('ssga XLK xlsx',
          'https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-xlk.xlsx')

    print()
    print('=== 4. iShares holdings CSV (product id in the path) ===')
    probe('ishares IVV csv',
          'https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax'
          '?fileType=csv&fileName=IVV_holdings&dataType=fund')
    probe('ishares IWM csv',
          'https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/1467271812596.ajax'
          '?fileType=csv&fileName=IWM_holdings&dataType=fund')

    print()
    print('=== 5. Vanguard ===')
    probe('vanguard VOO profile',
          'https://api.vanguard.com/rs/ire/01/ind/fund/VOO/profile.json')
    probe('vanguard VOO holdings',
          'https://investor.vanguard.com/investment-products/etfs/profile/api/VOO/portfolio-holding/stock')

    print()
    print('=== 6. ARK (plain CSV, useful as a format sanity check) ===')
    b = probe('ark ARKK csv',
              'https://www.ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv')
    if b:
        try:
            rows = list(csv.DictReader(io.StringIO(b.decode('utf-8', 'replace'))))
            print('      parsed rows:', len(rows), '| columns:', list(rows[0].keys()) if rows else None)
        except Exception as ex:
            print('      parse failed:', ex)

    print()
    print('=== 7. SEC N-PORT: every US fund files holdings quarterly, no scraping needed ===')
    probe('sec company_tickers',
          'https://www.sec.gov/files/company_tickers.json',
          {'User-Agent': 'stockanaliz.com research contact@stockanaliz.com'})
    probe('sec submissions QQQ trust',
          'https://data.sec.gov/submissions/CIK0001067839.json',
          {'User-Agent': 'stockanaliz.com research contact@stockanaliz.com'})

    print()
    print('=== done ===')


if __name__ == '__main__':
    sys.exit(main())
