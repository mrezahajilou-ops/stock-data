#!/usr/bin/env python3
"""US housing market data for stockanaliz.com/housing/. Free, public, keyless sources that answer GitHub's runners
(FRED and the Census API do not: FRED times out, the Census API now wants a key).

Sources
  FHFA House Price Index   hpi_master.csv: US purchase-only monthly (1991-), states all-transactions quarterly (1975-)
  Freddie Mac PMMS         30- and 15-year fixed mortgage rates, weekly since 1971
  Yahoo Finance            10-year Treasury yield (^TNX), weekly
  BLS API v1               CPI all items, CPI rent of primary residence, CPI shelter, unemployment rate
  Census (xlsx)            housing starts, building permits (SAAR), new houses sold (SAAR), new houses for sale,
                           rental / homeowner vacancy and homeownership (HVS), median household income by state (CPS H-8)
  Census ACS summary files 1-year table-based files (2021-): per state median gross rent (all, 1/2/3 bedrooms), median
                           home value, median household income, median real-estate taxes, tenure, vacant for rent / sale
  Federal Reserve          delinquency rate on residential real-estate loans, all banks, seasonally adjusted, quarterly
  Zillow Research          ZHVI (typical value: all homes, single-family, condo/co-op) by state / metro / US; ZORI rents
  Realtor.com research     active listings, median listing price, days on market, price cuts, pending, by state and US

Output housing.json (orphan branch "housing", .github/workflows/housing.yml):
  as_of, f{KEY: [[YYYY-MM-DD, v], ...]}, z{us{all,sfr,condo}, zori_us}, st{XX{n, all, sfr, condo}}, mt[{n, st, rank, all, sfr, condo, zori}],
  hpi_st{XX: [[YYYY-MM, v]]} (quarterly), inc{US|XX: {YEAR: v}}, acs{US|XX: {YEAR: {...}}}, rdc{US|XX: [[YYYY-MM, listings, list price, dom, cuts, pending]]}
A source that fails keeps its block from the previously published file, so one bad day never empties a section.
"""
import csv, io, json, os, re, sys, time, datetime as dt, urllib.request, concurrent.futures as cf

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
OUT = os.environ.get('OUT', os.path.join(ROOT, 'housing.json'))
TODAY = dt.date.today()
LOG = []
T0 = time.time()

STATES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado',
          'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia',
          'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky',
          'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
          'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
          'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota',
          'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
          'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
          'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}
BYNAME = {v.lower(): k for k, v in STATES.items()}
FIPS = {'01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
        '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
        '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
        '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
        '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
        '56': 'WY'}


def say(*a):
    print('[%4ds]' % (time.time() - T0), *a, flush=True)


def getb(url, timeout=60, tries=3, data=None, headers=None):
    last = None
    for a in range(tries):
        try:
            h = {'User-Agent': UA, 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.9'}
            h.update(headers or {})
            return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout).read()
        except Exception as e:
            last = e
            time.sleep(3 * (a + 1))
    raise last


def get(url, **k):
    return getb(url, **k).decode('utf-8', 'replace')


def num(x):
    try:
        v = float(str(x).replace(',', '').strip())
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def xlsx(url):
    import openpyxl
    return openpyxl.load_workbook(io.BytesIO(getb(url, timeout=90)), read_only=True, data_only=True)


# ------------------------------------------------------------------ FHFA
def fhfa():
    txt = get('https://www.fhfa.gov/hpi/download/monthly/hpi_master.csv', timeout=120)
    us, us_sa, st = [], [], {}
    for r in csv.DictReader(io.StringIO(txt)):
        t, fl, fq, lv, pid = r.get('hpi_type'), r.get('hpi_flavor'), r.get('frequency'), r.get('level') or '', r.get('place_id') or ''
        try:
            y, p = int(r['yr']), int(r['period'])
        except (KeyError, ValueError, TypeError):
            continue
        v, vs = num(r.get('index_nsa')), num(r.get('index_sa'))
        if t != 'traditional' or v is None:
            continue
        if fl == 'purchase-only' and fq == 'monthly' and pid == 'USA':
            us.append(['%d-%02d-01' % (y, p), v])
            if vs:
                us_sa.append(['%d-%02d-01' % (y, p), vs])
        elif fl == 'all-transactions' and fq == 'quarterly' and lv == 'State' and pid in STATES:
            st.setdefault(pid, []).append(['%d-%02d' % (y, p * 3), v])
    if len(us) < 300 or len(st) < 45:
        raise ValueError('FHFA: %d US months, %d states' % (len(us), len(st)))
    say('fhfa', len(us), us[-1], len(st))
    return sorted(us), sorted(us_sa), {k: sorted(v) for k, v in st.items()}


# ------------------------------------------------------------------ Freddie Mac
def pmms():
    txt = get('https://www.freddiemac.com/pmms/docs/PMMS_history.csv', timeout=60)
    m30, m15 = [], []
    for r in csv.DictReader(io.StringIO(txt)):
        try:
            d = dt.datetime.strptime(r['date'].strip(), '%m/%d/%Y').date().isoformat()
        except (KeyError, ValueError):
            continue
        a, b = num(r.get('pmms30')), num(r.get('pmms15'))
        if a:
            m30.append([d, a])
        if b:
            m15.append([d, b])
    if len(m30) < 2000:
        raise ValueError('PMMS: %d rows' % len(m30))
    say('pmms', len(m30), m30[-1])
    return sorted(m30), sorted(m15)


# ------------------------------------------------------------------ 10-year Treasury (Yahoo ^TNX)
def tnx():
    now = int(time.time())
    j = json.loads(get('https://query2.finance.yahoo.com/v8/finance/chart/%%5ETNX?period1=%d&period2=%d&interval=1wk' % (now - 56 * 365 * 86400, now)))
    r = j['chart']['result'][0]
    out = []
    for t, c in zip(r.get('timestamp') or [], ((r.get('indicators') or {}).get('quote') or [{}])[0].get('close') or []):
        if c:
            out.append([dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(), round(c / 10 if c > 25 else c, 3)])
    if len(out) < 500:
        raise ValueError('TNX: %d rows' % len(out))
    say('tnx', len(out), out[-1])
    return out


# ------------------------------------------------------------------ BLS
BLS = {'CPIAUCNS': 'CUUR0000SA0', 'CUUR0000SEHA': 'CUUR0000SEHA', 'CUUR0000SAH1': 'CUUR0000SAH1', 'UNRATE': 'LNS14000000'}


def bls():
    rev = {v: k for k, v in BLS.items()}
    out = {k: [] for k in BLS}
    for a in range(1977, TODAY.year + 1, 10):
        body = json.dumps({'seriesid': list(BLS.values()), 'startyear': str(a), 'endyear': str(min(a + 9, TODAY.year))}).encode()
        j = json.loads(getb('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=body, headers={'Content-Type': 'application/json'}, timeout=45))
        if j.get('status') != 'REQUEST_SUCCEEDED':
            raise ValueError('BLS: %s' % str(j.get('message'))[:120])
        for sr in (j.get('Results') or {}).get('series') or []:
            k = rev.get(sr.get('seriesID'))
            for row in sr.get('data') or []:
                if k and row.get('period', '').startswith('M') and row['period'] != 'M13':
                    v = num(row.get('value'))
                    if v is not None:
                        out[k].append(['%s-%s-01' % (row['year'], row['period'][1:]), v])
    if len(out['CPIAUCNS']) < 400:
        raise ValueError('BLS: %d CPI rows' % len(out['CPIAUCNS']))
    say('bls', {k: len(v) for k, v in out.items()})
    return {k: sorted(v) for k, v in out.items()}


# ------------------------------------------------------------------ Census construction & HVS & income
def monthly_sheet(wb, want, col):
    """Rows of (datetime, value) from the first sheet whose title matches `want` (column `col`)."""
    ws = next(w for w in wb.worksheets if want(w.title))
    out = []
    for row in ws.iter_rows(values_only=True):
        if row and isinstance(row[0], dt.datetime) and len(row) > col:
            v = num(row[col])
            if v is not None:
                out.append([row[0].date().isoformat(), v])
    return out


def construction():
    sa = lambda t: 'seasonally' in t.lower() and 'not' not in t.lower()
    f = {}
    wb = xlsx('https://www.census.gov/construction/nrc/xls/starts_cust.xlsx')
    say('starts sheets', [w.title for w in wb.worksheets])
    f['HOUST'], f['HOUST1F'] = monthly_sheet(wb, sa, 1), monthly_sheet(wb, sa, 2)
    wb = xlsx('https://www.census.gov/construction/nrc/xls/permits_cust.xlsx')
    f['PERMIT'] = monthly_sheet(wb, sa, 1)
    wb = xlsx('https://www.census.gov/construction/nrs/xls/sold_cust.xlsx')
    f['HSN1F'] = monthly_sheet(wb, lambda t: t.lower().startswith('month'), 6)
    try:   # new houses for sale: seasonally adjusted months' supply is the 7th column of the monthly sheet
        wb = xlsx('https://www.census.gov/construction/nrs/xls/fsale_cust.xlsx')
        f['MSACSR'] = monthly_sheet(wb, lambda t: t.lower().startswith('month'), 6)
    except Exception as e:
        LOG.append('for-sale file: %s' % str(e)[:80])
    for k in ('HOUST', 'PERMIT', 'HSN1F'):
        if len(f[k]) < 200:
            raise ValueError('construction %s: %d rows' % (k, len(f[k])))
    say('construction', {k: (len(v), v[-1] if v else None) for k, v in f.items()})
    return f


Q = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4}


def hvs():
    out = {}
    for key, url in (('RRVRUSQ156N', 'https://www.census.gov/housing/hvs/data/histtab1.xlsx'),
                     ('RHVRUSQ156N', 'https://www.census.gov/housing/hvs/data/histtab2.xlsx')):
        try:
            ws = xlsx(url).worksheets[0]
            y, rows = None, []
            for row in ws.iter_rows(values_only=True):
                c0 = str(row[0] if row and row[0] is not None else '').strip()
                if re.match(r'^(19|20)\d\d', c0) and not re.search(r'[A-Za-z]', c0):
                    y = int(c0[:4])
                    continue
                q = Q.get(c0[:3])
                v = num(row[1]) if len(row) > 1 else None
                if y and q and v is not None:
                    rows.append(['%d-%02d-01' % (y, q * 3 - 2), v])
            out[key] = rows
        except Exception as e:
            LOG.append('hvs %s: %s' % (key, str(e)[:80]))
    try:
        ws = xlsx('https://www.census.gov/housing/hvs/data/histtab14.xlsx').worksheets[0]
        y, rows = None, []
        for row in ws.iter_rows(values_only=True):
            c0 = str(row[0] if row and row[0] is not None else '').strip()
            if re.match(r'^(19|20)\d\d', c0) and not re.search(r'[A-Za-z]', c0):
                y = int(c0[:4])
                continue
            if y and c0.lower().startswith('united states'):
                for i in range(4):
                    v = num(row[1 + i]) if len(row) > 1 + i else None
                    if v is not None:
                        rows.append(['%d-%02d-01' % (y, i * 3 + 1), v])
        out['RHORUSQ156N'] = rows
    except Exception as e:
        LOG.append('hvs own: %s' % str(e)[:80])
    say('hvs', {k: (len(v), v[-1] if v else None) for k, v in out.items()})
    return out


def income():
    ws = xlsx('https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/h08.xlsx').worksheets[0]
    years, out = None, {}
    for row in ws.iter_rows(values_only=True):
        c0 = str(row[0] if row and row[0] is not None else '').strip()
        if c0 == 'State':
            if years is not None:
                break   # second block: constant dollars
            years, seen = [], set()
            for i, c in enumerate(row):
                m = re.match(r'^((19|20)\d\d)', str(c if c is not None else ''))
                if i and m and m.group(1) not in seen:
                    seen.add(m.group(1))
                    years.append((i, m.group(1)))
            continue
        if years:
            key = 'US' if c0.lower() == 'united states' else BYNAME.get(c0.lower())
            if key:
                out[key] = {y: num(row[i]) for i, y in years if i < len(row) and num(row[i])}
    if len(out) < 45:
        raise ValueError('income: %d rows' % len(out))
    say('income', len(out), sorted(out['US'].items())[-1])
    return out


def delinquency():
    txt = get('https://www.federalreserve.gov/releases/chargeoff/delallsa.htm', timeout=60)
    t = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', txt)))
    rows = {}
    for m in re.finditer(r'\b((?:19|20)\d\d):([1-4])\s+([\d.]+)\s+([\d.]+)', t):
        rows.setdefault('%s-%02d-01' % (m.group(1), int(m.group(2)) * 3 - 2), float(m.group(4)))   # 2nd column: residential
    rows = sorted([k, v] for k, v in rows.items())
    if len(rows) < 60:
        raise ValueError('delinquency: %d rows' % len(rows))
    say('delinquency', len(rows), rows[-1], max(rows, key=lambda x: x[1]))
    return rows


# ------------------------------------------------------------------ Census ACS (table-based summary files)
ACS_T = {'b25064': {'E001': 'rent'}, 'b25031': {'E003': 'r1', 'E004': 'r2', 'E005': 'r3'}, 'b25077': {'E001': 'value'},
         'b19013': {'E001': 'inc'}, 'b25103': {'E001': 'tax'}, 'b25003': {'E002': 'own', 'E003': 'rent_hh'},
         'b25004': {'E002': 'vac_rent', 'E004': 'vac_sale'}}


def acs_one(y, tbl):
    url = 'https://www2.census.gov/programs-surveys/acs/summary_file/%d/table-based-SF/data/1YRData/acsdt1y%d-%s.dat' % (y, y, tbl)
    lines = get(url, timeout=90, tries=2).splitlines()
    head = lines[0].split('|')
    want = {i: ACS_T[tbl][h.split('_')[1]] for i, h in enumerate(head) if '_' in h and h.split('_')[1] in ACS_T[tbl]}
    out = {}
    for ln in lines[1:]:
        if not (ln.startswith('0400000US') or ln.startswith('0100000US|')):
            continue
        p = ln.split('|')
        key = 'US' if p[0] == '0100000US' else FIPS.get(p[0][9:11])
        if key:
            out[key] = {k: round(num(p[i])) for i, k in want.items() if i < len(p) and num(p[i]) is not None and num(p[i]) >= 0}
    return out


def acs_all():
    acs = {}
    jobs = [(y, t) for y in range(2021, TODAY.year) for t in ACS_T]
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(acs_one, y, t): (y, t) for y, t in jobs}
        for fu in cf.as_completed(futs):
            y, t = futs[fu]
            try:
                for k, rec in fu.result().items():
                    acs.setdefault(k, {}).setdefault(str(y), {}).update(rec)
            except Exception as e:
                LOG.append('acs %d %s: %s' % (y, t, str(e)[:60]))   # the newest year comes out each September
    if len(acs) < 45:
        raise ValueError('acs: %d' % len(acs))
    say('acs', len(acs), sorted(acs['US'].items())[-1] if acs.get('US') else None)
    return acs


# ------------------------------------------------------------------ Zillow
ZBASE = 'https://files.zillowstatic.com/research/public_csvs/'
ZHVI = {'all': 'uc_sfrcondo', 'sfr': 'uc_sfr', 'condo': 'uc_condo'}


def zillow(path):
    txt = get(ZBASE + path, timeout=90, tries=2)
    rd = csv.reader(io.StringIO(txt))
    head = next(rd)
    dcols = [(i, h[:7]) for i, h in enumerate(head) if re.match(r'\d{4}-\d\d-\d\d$', h)]
    meta = [i for i, h in enumerate(head) if not re.match(r'\d{4}-\d\d', h)]
    out = []
    for r in rd:
        if len(r) < len(head):
            continue
        m = {head[i]: r[i] for i in meta}
        out.append((m, [[ym, round(num(r[i]))] for i, ym in dcols if num(r[i])]))
    return out


def zillow_all():
    z = {'us': {}, 'zori_us': []}
    st, mt = {}, {}
    for k, code in ZHVI.items():
        for m, s in zillow('zhvi/State_zhvi_%s_tier_0.33_0.67_sm_sa_month.csv' % code):
            ab = BYNAME.get((m.get('RegionName') or '').lower())
            if ab:
                st.setdefault(ab, {'n': STATES[ab]})[k] = s
        for m, s in zillow('zhvi/Metro_zhvi_%s_tier_0.33_0.67_sm_sa_month.csv' % code):
            if (m.get('RegionType') or '').lower() == 'country':
                z['us'][k] = s
                continue
            rank = int(num(m.get('SizeRank')) or 9999)
            if rank > 61:
                continue
            e = mt.setdefault(m.get('RegionID'), {'n': m.get('RegionName'), 'st': m.get('StateName'), 'rank': rank})
            e[k] = s
    for m, s in zillow('zori/Metro_zori_uc_sfrcondomfr_sm_month.csv'):
        if (m.get('RegionType') or '').lower() == 'country':
            z['zori_us'] = s
        elif m.get('RegionID') in mt:
            mt[m.get('RegionID')]['zori'] = s
    metros = sorted((v for v in mt.values() if v.get('all')), key=lambda v: v['rank'])[:60]
    if len(st) < 45 or len(metros) < 40:
        raise ValueError('zillow: %d states, %d metros' % (len(st), len(metros)))
    say('zillow', len(st), len(metros), z['us'].get('all', [[0, 0]])[-1])
    return z, st, metros


# ------------------------------------------------------------------ Realtor.com
RDC = 'https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_%s_History.csv'


def rdc_all():
    out = {}
    for level in ('Country', 'State'):
        for r in csv.DictReader(io.StringIO(get(RDC % level, timeout=90, tries=2))):
            ym = str(r.get('month_date_yyyymm') or '').strip()
            if not re.match(r'\d{6}$', ym):
                continue
            sid = (r.get('state_id') or '').strip().upper()
            key = 'US' if level == 'Country' else (sid if sid in STATES else BYNAME.get((r.get('state') or '').strip().lower()))
            if not key:
                continue
            row = [num(r.get(c)) for c in ('active_listing_count', 'median_listing_price', 'median_days_on_market', 'price_reduced_count', 'pending_listing_count')]
            out.setdefault(key, []).append([ym[:4] + '-' + ym[4:]] + [None if v is None else round(v) for v in row])
    for k in out:
        out[k].sort()
    if len(out) < 40:
        raise ValueError('realtor: %d' % len(out))
    say('realtor', len(out), out['US'][-1] if out.get('US') else None)
    return out


# ------------------------------------------------------------------ main
def prev_json():
    try:
        return json.load(open(OUT))
    except Exception:
        pass
    try:
        return json.loads(get('https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/housing/housing.json', timeout=30, tries=1))
    except Exception:
        return {}


def main():
    prev = prev_json()
    pf = prev.get('f') or {}
    out = {'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}
    f = {}
    jobs = {'fhfa': fhfa, 'pmms': pmms, 'tnx': tnx, 'bls': bls, 'cons': construction, 'hvs': hvs, 'inc': income,
            'delq': delinquency, 'acs': acs_all, 'zillow': zillow_all, 'rdc': rdc_all}
    res = {}
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(fn): k for k, fn in jobs.items()}
        for fu in cf.as_completed(futs):
            k = futs[fu]
            try:
                res[k] = fu.result()
            except Exception as e:
                LOG.append('%s FAILED: %s' % (k, str(e)[:160]))
    if 'fhfa' in res:
        f['HPI'], f['HPI_SA'], out['hpi_st'] = res['fhfa']
    if 'pmms' in res:
        f['MORTGAGE30US'], f['MORTGAGE15US'] = res['pmms']
    if 'tnx' in res:
        f['DGS10'] = res['tnx']
    for k in ('bls', 'cons', 'hvs'):
        f.update(res.get(k) or {})
    if 'delq' in res:
        f['DRSFRMACBS'] = res['delq']
    for k, v in pf.items():          # anything missing today: the previous day's series
        if not f.get(k) and v:
            f[k] = v
            LOG.append('kept previous %s' % k)
    out['f'] = f
    out['hpi_st'] = out.get('hpi_st') or prev.get('hpi_st') or {}
    out['inc'] = res.get('inc') or prev.get('inc') or {}
    out['acs'] = res.get('acs') or prev.get('acs') or {}
    if 'zillow' in res:
        out['z'], out['st'], out['mt'] = res['zillow']
    else:
        for k in ('z', 'st', 'mt'):
            out[k] = prev.get(k)
    out['rdc'] = res.get('rdc') or prev.get('rdc') or {}
    out['log'] = LOG
    json.dump(out, open(OUT, 'w'), separators=(',', ':'))
    print('\n'.join(LOG))
    say('series:', {k: (len(v), v[-1]) for k, v in f.items()})
    say('wrote %d KB' % (os.path.getsize(OUT) // 1024))
    if not (f.get('HPI') and f.get('MORTGAGE30US') and out.get('st')):
        sys.exit('missing core data')


if __name__ == '__main__':
    main()
