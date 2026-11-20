#!/usr/bin/env python3
"""Probe which public sources actually serve ETF holdings, prices and profile data.

Runs in Actions (the container that writes the site has no route to these hosts), prints what each
candidate returned, and writes nothing. The point is to find out which endpoints work before
etf_data.py is written against them, rather than guessing and debugging through the build.

Round 1 found: SSGA xlsx works for SPDR funds, SEC works, Nasdaq summary/info work.
iShares and Invesco returned HTML (bot wall), Vanguard refused the TLS handshake.
Round 2 chases those three and tests SEC N-PORT as the universal fallback.
"""
import json, re, sys, time, urllib.request, urllib.error

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124 Safari/537.36')
SEC_HDR = {'User-Agent': 'stockanaliz.com research contact@stockanaliz.com',
           'Accept-Encoding': 'gzip, deflate'}
NASDAQ_HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*',
              'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}


def get(url, hdr=None, timeout=60):
    req = urllib.request.Request(url, headers=hdr or {'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            import gzip
            body = gzip.decompress(body)
        return r.status, body, dict(r.headers)


def probe(label, url, hdr=None, show=200):
    try:
        st, body, h = get(url, hdr)
    except urllib.error.HTTPError as ex:
        print('  [%-30s] HTTP %s' % (label, ex.code))
        return None
    except Exception as ex:
        print('  [%-30s] FAIL %s' % (label, (type(ex).__name__ + ': ' + str(ex))[:100]))
        return None
    txt = body[:show].decode('utf-8', 'replace').replace('\n', ' | ')
    print('  [%-30s] %s %8d b  ct=%s  %s'
          % (label, st, len(body), (h.get('Content-Type') or '?')[:40], txt))
    return body


def main():
    print('=== A. iShares, retried with a browser-like referer and accept ===')
    ish = {'User-Agent': UA, 'Accept': 'text/csv,application/csv,*/*',
           'Referer': 'https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf',
           'Accept-Language': 'en-US,en;q=0.9'}
    probe('ishares IVV csv +referer',
          'https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax'
          '?fileType=csv&fileName=IVV_holdings&dataType=fund', ish)
    probe('ishares IVV csv .csv path',
          'https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax'
          '?fileType=csv&fileName=IVV_holdings&dataType=fund&asOfDate=', ish)

    print()
    print('=== B. Invesco, alternate endpoints ===')
    inv = {'User-Agent': UA, 'Accept': 'text/csv,*/*',
           'Referer': 'https://www.invesco.com/qqq-etf/en/holdings.html'}
    probe('invesco QQQ holdings csv', 'https://www.invesco.com/qqq-etf/en/holdings.html?audienceType=Investor&action=download', inv)
    probe('invesco static csv', 'https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?ticker=QQQ&action=download&audienceType=Investor', inv)

    print()
    print('=== C. Nasdaq-100 constituent list (QQQ holdings by another name) ===')
    for u in ('https://api.nasdaq.com/api/quote/list-type/nasdaq100',
              'https://api.nasdaq.com/api/quote/list-type-extended/nasdaq100'):
        probe(u.rsplit('/', 1)[-1], u, NASDAQ_HDR)

    print()
    print('=== D. Vanguard, alternate hosts ===')
    van = {'User-Agent': UA, 'Accept': 'application/json,*/*',
           'Referer': 'https://investor.vanguard.com/'}
    for lbl, u in (('personal api', 'https://personal1.vanguard.com/ecs-portfolio-holding-service/holdings?portId=0968&issueType=S'),
                   ('investor profile', 'https://investor.vanguard.com/investment-products/etfs/profile/api/voo/profile'),
                   ('corp api', 'https://corporate.vanguard.com/content/dam/corp/research/pdf/VOO.json')):
        probe(lbl, u, van)

    print()
    print('=== E. SEC N-PORT: the universal fallback. Find the filings for a few funds ===')
    # company_tickers_exchange has ETFs too; look a few tickers up
    b = probe('sec company_tickers_exchange', 'https://www.sec.gov/files/company_tickers_exchange.json', SEC_HDR, show=120)
    cik = {}
    if b:
        d = json.loads(b)
        fields = d.get('fields') or []
        ti, ci = fields.index('ticker'), fields.index('cik')
        for row in d.get('data') or []:
            cik[str(row[ti]).upper()] = int(row[ci])
        for t in ('QQQ', 'SPY', 'VOO', 'IVV', 'VTI', 'IWM', 'XLK', 'SCHD', 'VGT', 'SMH'):
            print('      %-5s cik=%s' % (t, cik.get(t)))
    time.sleep(1)

    for t in ('VOO', 'IVV', 'SMH'):
        c = cik.get(t)
        if not c:
            print('  [%s] no cik in the SEC ticker file' % t)
            continue
        b = probe('sec submissions %s' % t, 'https://data.sec.gov/submissions/CIK%010d.json' % c, SEC_HDR, show=90)
        if not b:
            continue
        d = json.loads(b)
        rec = d.get('filings', {}).get('recent', {})
        forms = rec.get('form') or []
        hits = [(forms[i], rec['filingDate'][i], rec['accessionNumber'][i], rec['primaryDocument'][i])
                for i in range(len(forms)) if forms[i].startswith('NPORT')]
        print('      NPORT filings found:', len(hits))
        for h in hits[:3]:
            print('       ', h)
        if hits:
            f, dte, acc, doc = hits[0]
            a = acc.replace('-', '')
            idx = probe('  nport index %s' % t,
                        'https://www.sec.gov/Archives/edgar/data/%d/%s/index.json' % (c, a), SEC_HDR, show=120)
            if idx:
                items = (json.loads(idx).get('directory') or {}).get('item') or []
                print('        files:', [(x['name'], x['size']) for x in items][:12])
        time.sleep(1)

    print()
    print('=== F. SSGA: confirm the xlsx parses and carries weights ===')
    b = probe('ssga SPY xlsx',
              'https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx')
    if b:
        import zipfile, io as _io
        try:
            z = zipfile.ZipFile(_io.BytesIO(b))
            print('      sheets in workbook:', [n for n in z.namelist() if 'sheet' in n][:5])
            shared = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
            strings = re.findall(r'<t[^>]*>(.*?)</t>', shared, re.S)
            print('      first shared strings:', strings[:14])
        except Exception as ex:
            print('      xlsx parse failed:', ex)

    print()
    print('=== done ===')


if __name__ == '__main__':
    sys.exit(main())
