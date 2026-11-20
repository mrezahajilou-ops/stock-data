#!/usr/bin/env python3
"""Probe which public sources actually serve ETF holdings.

Round 1: SSGA xlsx works, SEC works, Nasdaq quote endpoints work.
Round 2: iShares, Invesco and Vanguard all serve a bot wall or refuse. The Nasdaq-100 list works.
Round 3: the SEC's own fund-ticker map and N-PORT filings, which every US fund must file, plus a
         look inside the two payloads that did work to see whether they carry weights.
"""
import json, re, sys, time, io, zipfile, urllib.request, urllib.error

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36')
SEC_HDR = {'User-Agent': 'stockanaliz.com research contact@stockanaliz.com', 'Accept-Encoding': 'gzip, deflate'}
NASDAQ_HDR = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*',
              'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}


def get(url, hdr=None, timeout=90):
    req = urllib.request.Request(url, headers=hdr or {'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            import gzip
            body = gzip.decompress(body)
        return r.status, body


def probe(label, url, hdr=None, show=160):
    try:
        st, body = get(url, hdr)
    except urllib.error.HTTPError as ex:
        print('  [%-28s] HTTP %s' % (label, ex.code)); return None
    except Exception as ex:
        print('  [%-28s] FAIL %s' % (label, (type(ex).__name__ + ': ' + str(ex))[:90])); return None
    print('  [%-28s] %s %9d b  %s' % (label, st, len(body),
                                      body[:show].decode('utf-8', 'replace').replace('\n', ' | ')))
    return body


def main():
    print('=== 1. The SEC fund-ticker map: ticker -> CIK, series, class ===')
    b = probe('company_tickers_mf', 'https://www.sec.gov/files/company_tickers_mf.json', SEC_HDR, show=150)
    mf = {}
    if b:
        d = json.loads(b)
        f = d['fields']
        ix = {k: f.index(k) for k in f}
        print('      fields:', f)
        for row in d['data']:
            sym = str(row[ix['symbol']]).upper()
            mf[sym] = dict(cik=row[ix['cik']], series=row[ix['seriesId']], cls=row[ix['classId']])
        print('      rows:', len(d['data']))
        for t in ('VOO', 'IVV', 'QQQ', 'VTI', 'IWM', 'SCHD', 'VGT', 'SMH', 'SPY', 'XLK', 'IBIT', 'GLD'):
            print('      %-5s %s' % (t, mf.get(t)))
    time.sleep(1)

    print()
    print('=== 2. N-PORT for one Vanguard and one iShares fund ===')
    for t in ('VOO', 'IVV'):
        m = mf.get(t)
        if not m:
            print('  [%s] not in the fund map' % t); continue
        cik = int(m['cik'])
        b = probe('submissions %s' % t, 'https://data.sec.gov/submissions/CIK%010d.json' % cik, SEC_HDR, show=70)
        if not b:
            continue
        rec = json.loads(b).get('filings', {}).get('recent', {})
        forms = rec.get('form') or []
        hits = [(rec['filingDate'][i], rec['accessionNumber'][i], rec['primaryDocument'][i])
                for i in range(len(forms)) if forms[i].startswith('NPORT-P')]
        print('      NPORT-P filings:', len(hits), '| newest:', hits[0] if hits else None)
        if hits:
            dte, acc, doc = hits[0]
            a = acc.replace('-', '')
            idx = probe('  index %s' % t, 'https://www.sec.gov/Archives/edgar/data/%d/%s/index.json' % (cik, a), SEC_HDR, show=80)
            if idx:
                items = (json.loads(idx).get('directory') or {}).get('item') or []
                for x in items[:10]:
                    print('        %-40s %s b' % (x['name'], x['size']))
                xmls = [x for x in items if x['name'].endswith('.xml') and int(x['size']) > 100000]
                if xmls:
                    big = max(xmls, key=lambda x: int(x['size']))
                    body = probe('  %s %s' % (t, big['name']),
                                 'https://www.sec.gov/Archives/edgar/data/%d/%s/%s' % (cik, a, big['name']),
                                 SEC_HDR, show=0)
                    if body:
                        s = body.decode('utf-8', 'replace')
                        ser = re.search(r'<seriesId>(S\d+)</seriesId>', s)
                        print('        seriesId in file:', ser.group(1) if ser else None,
                              '| wanted', m['series'])
                        print('        <invstOrSec> blocks:', s.count('<invstOrSec>'))
                        one = re.search(r'<invstOrSec>(.{0,900}?)</invstOrSec>', s, re.S)
                        if one:
                            print('        first holding:', re.sub(r'\s+', ' ', one.group(1))[:520])
        time.sleep(1)

    print()
    print('=== 3. Inside the SSGA workbook: does it carry weights? ===')
    b = probe('ssga XLK xlsx',
              'https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-xlk.xlsx',
              show=0)
    if b:
        z = zipfile.ZipFile(io.BytesIO(b))
        shared = re.findall(r'<t[^>]*>(.*?)</t>', z.read('xl/sharedStrings.xml').decode('utf-8', 'replace'), re.S)
        sheet = z.read('xl/worksheets/sheet1.xml').decode('utf-8', 'replace')
        rows = re.findall(r'<row[^>]*>(.*?)</row>', sheet, re.S)
        print('      rows in sheet:', len(rows))
        def cells(r):
            out = []
            for c in re.findall(r'<c[^>]*?(?: t="(\w+)")?[^>]*>(?:<v>(.*?)</v>|<is><t[^>]*>(.*?)</t></is>)?</c>', r):
                ty, v, inline = c
                if inline:
                    out.append(inline)
                elif ty == 's' and v != '':
                    out.append(shared[int(v)] if int(v) < len(shared) else v)
                else:
                    out.append(v)
            return out
        for r in rows[:12]:
            print('       ', cells(r)[:8])

    print()
    print('=== 4. Nasdaq-100 list: does it carry weights? ===')
    b = probe('nasdaq100', 'https://api.nasdaq.com/api/quote/list-type/nasdaq100', NASDAQ_HDR, show=0)
    if b:
        d = json.loads(b)
        inner = ((d.get('data') or {}).get('data') or {})
        print('      keys:', list(inner.keys()))
        rows = (inner.get('rows') or inner.get('data') or [])
        print('      rows:', len(rows), '| first:', rows[0] if rows else None)

    print()
    print('=== done ===')


if __name__ == '__main__':
    sys.exit(main())
