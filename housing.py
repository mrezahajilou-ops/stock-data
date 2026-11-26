#!/usr/bin/env python3
"""US housing market data for the housing pages (stockanaliz.com/housing/). Free, public, keyless sources only.

Sources
  FRED (fredgraph.csv)   S&P CoreLogic Case-Shiller national index, median sales price of houses sold, Freddie Mac 30/15-year
                         mortgage rates, 10-year Treasury, housing starts, permits, completions, new home sales, months' supply,
                         homeownership and vacancy rates, CPI rent / shelter / all items, median household income,
                         mortgage delinquency, unemployment, mortgage debt service
  Zillow Research CSVs   ZHVI (typical home value: all homes, single-family, condo/co-op) by state and metro, monthly since 2000;
                         ZORI (typical asking rent) by metro and the US, monthly since 2015
  Census ACS 1-year API  per state and year: median gross rent (all, 1/2/3 bedrooms), median home value, median household
                         income, median real-estate taxes, owner/renter households, vacant for rent / for sale
  Realtor.com research   active listings, median listing price, days on market, price cuts, by state and nationally

Output housing.json (published to the orphan branch "housing" by .github/workflows/housing.yml; the site build reads it):
  as_of, src{...dates}
  f{SERIES: [[date, value], ...]}              FRED series (monthly / weekly / quarterly as published)
  z{us: {all, sfr, condo: [[YYYY-MM, v]]}, zori_us: [[YYYY-MM, v]]}
  st{XX: {n, all, sfr, condo: [[YYYY-MM, v]] (monthly, since 2000)}}           Zillow by state
  mt[{n, st, rank, all, sfr, condo, zori: [[YYYY-MM, v]]}]                     Zillow, 60 largest metros
  acs{XX|US: {YEAR: {rent, r1, r2, r3, value, inc, tax, own, rent_hh, vac_rent, vac_sale}}}
  rdc{XX|US: [[YYYY-MM, listings, median_list_price, days_on_market, price_reduced, pending]]}
A failing source keeps its block from the previous published file, so one bad day never empties a section.
"""
import csv, io, json, os, re, sys, time, datetime as dt, urllib.request, concurrent.futures as cf

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
OUT = os.environ.get('OUT', os.path.join(ROOT, 'housing.json'))
TODAY = dt.date.today()
LOG = []

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

FRED = {
    'CSUSHPINSA': 'Case-Shiller US national home price index (NSA, Jan 2000 = 100)',
    'CSUSHPISA': 'Case-Shiller US national (SA)',
    'SPCS20RSA': 'Case-Shiller 20-city composite (SA)',
    'MSPUS': 'Median sales price of houses sold, quarterly',
    'MSPNHSUS': 'Median sales price of new houses sold, monthly',
    'MORTGAGE30US': 'Freddie Mac 30-year fixed mortgage rate, weekly',
    'MORTGAGE15US': 'Freddie Mac 15-year fixed mortgage rate, weekly',
    'DGS10': '10-year Treasury yield, daily',
    'FEDFUNDS': 'Effective federal funds rate, monthly',
    'HOUST': 'Housing starts, total, SAAR thousands',
    'HOUST1F': 'Housing starts, single-family',
    'PERMIT': 'Building permits, total',
    'COMPUTSA': 'Housing completions',
    'HSN1F': 'New one-family houses sold, SAAR thousands',
    'MSACSR': "Months' supply of new houses",
    'RHORUSQ156N': 'Homeownership rate, quarterly',
    'RRVRUSQ156N': 'Rental vacancy rate, quarterly',
    'RHVRUSQ156N': 'Homeowner vacancy rate, quarterly',
    'CUUR0000SEHA': 'CPI rent of primary residence (NSA)',
    'CUUR0000SAH1': 'CPI shelter (NSA)',
    'CPIAUCNS': 'CPI all items (NSA)',
    'MEHOINUSA646N': 'Median household income, nominal, annual',
    'DRSFRMACBS': 'Delinquency rate on single-family mortgages, quarterly',
    'UNRATE': 'Unemployment rate',
    'MDSP': 'Mortgage debt service payments, % of disposable income',
    'ACTLISCOUUS': 'Active listings (Realtor.com)',
    'MEDDAYONMARUS': 'Median days on market (Realtor.com)',
    'MEDLISPRIUS': 'Median listing price (Realtor.com)',
}
# daily / weekly series are thinned to weekly / monthly before saving (the page never needs more)
THIN = {'DGS10': 'w', 'MORTGAGE30US': None, 'MORTGAGE15US': None}


class Slow(Exception):
    pass


T0 = time.time()


def say(*a):
    print('[%4ds]' % (time.time() - T0), *a, flush=True)


def get(url, timeout=60, tries=3):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.9'})
            return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(3 * (a + 1))
    raise last


def num(x):
    try:
        v = float(str(x).replace(',', ''))
        return v if v == v else None
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ FRED
def fred(sid):
    txt = get('https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + sid, timeout=45, tries=2)
    say('fred', sid)
    rows = []
    for r in csv.reader(io.StringIO(txt)):
        if len(r) >= 2 and re.match(r'\d{4}-\d\d-\d\d$', r[0]):
            v = num(r[1])
            if v is not None:
                rows.append([r[0], round(v, 4)])
    if not rows:
        raise ValueError('empty ' + sid)
    if THIN.get(sid) == 'w':
        wk = {}
        for d, v in rows:
            y, w, _ = dt.date.fromisoformat(d).isocalendar()
            wk[(y, w)] = [d, v]
        rows = [wk[k] for k in sorted(wk)]
    return rows


# ------------------------------------------------------------------ Zillow
ZBASE = 'https://files.zillowstatic.com/research/public_csvs/'
ZHVI = {'all': 'uc_sfrcondo', 'sfr': 'uc_sfr', 'condo': 'uc_condo'}


def zillow(path):
    txt = get(ZBASE + path, timeout=90, tries=2)
    say('zillow', path)
    rd = csv.reader(io.StringIO(txt))
    head = next(rd)
    dcols = [(i, h[:7]) for i, h in enumerate(head) if re.match(r'\d{4}-\d\d-\d\d$', h)]
    meta = [i for i, h in enumerate(head) if not re.match(r'\d{4}-\d\d', h)]
    out = []
    for r in rd:
        if len(r) < len(head):
            continue
        m = {head[i]: r[i] for i in meta}
        s = [[ym, round(num(r[i]))] for i, ym in dcols if num(r[i])]
        out.append((m, s))
    return out


def zillow_all(prev):
    z = {'us': {}, 'zori_us': []}
    st = {}
    mt = {}
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
            key = m.get('RegionID')
            e = mt.setdefault(key, {'n': m.get('RegionName'), 'st': m.get('StateName'), 'rank': rank})
            e[k] = s
    for m, s in zillow('zori/Metro_zori_uc_sfrcondomfr_sm_month.csv'):
        if (m.get('RegionType') or '').lower() == 'country':
            z['zori_us'] = s
            continue
        key = m.get('RegionID')
        if key in mt:
            mt[key]['zori'] = s
    metros = sorted((v for v in mt.values() if v.get('all')), key=lambda v: v['rank'])[:60]
    return z, st, metros


# ------------------------------------------------------------------ Census ACS
ACSV = {'B25064_001E': 'rent', 'B25031_003E': 'r1', 'B25031_004E': 'r2', 'B25031_005E': 'r3', 'B25077_001E': 'value',
        'B19013_001E': 'inc', 'B25103_001E': 'tax', 'B25003_002E': 'own', 'B25003_003E': 'rent_hh',
        'B25004_002E': 'vac_rent', 'B25004_003E': 'vac_sale'}
CORE = ['B25064_001E', 'B25077_001E', 'B19013_001E', 'B25003_002E', 'B25003_003E', 'B25004_002E', 'B25004_003E']


def acs_year(y, geo):
    for vs in (list(ACSV), CORE + ['B25031_003E', 'B25031_004E', 'B25031_005E'], CORE):
        url = 'https://api.census.gov/data/%d/acs/acs1?get=NAME,%s&for=%s' % (y, ','.join(vs), geo)
        try:
            j = json.loads(get(url, timeout=45, tries=1))
        except Exception as e:
            last = e
            continue
        head, rows = j[0], j[1:]
        out = {}
        for r in rows:
            m = dict(zip(head, r))
            key = 'US' if geo.startswith('us') else FIPS.get(m.get('state'))
            if not key:
                continue
            rec = {}
            for v in vs:
                x = num(m.get(v))
                if x is not None and x >= 0:
                    rec[ACSV[v]] = round(x)
            out[key] = rec
        return out
    raise last


def acs_all():
    acs = {}
    jobs = [(y, geo) for y in range(TODAY.year - 1, 2011, -1) for geo in ('state:*', 'us:1') if y != 2020]   # 2020: no standard 1-year release
    try:
        get('https://api.census.gov/data/2023/acs/acs1?get=NAME&for=us:1', timeout=30, tries=1)
    except Exception as e:
        LOG.append('acs unreachable: %s' % str(e)[:80])
        return acs
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(acs_year, y, geo): (y, geo) for y, geo in jobs}
        for fu in cf.as_completed(futs):
            y, geo = futs[fu]
            try:
                for k, rec in fu.result().items():
                    acs.setdefault(k, {})[str(y)] = rec
            except Exception as e:
                LOG.append('acs %d %s: %s' % (y, geo, str(e)[:80]))   # the newest year may not be out yet
    say('acs done', len(acs))
    return acs


# ------------------------------------------------------------------ Realtor.com
RDC = 'https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_%s_History.csv'


def rdc(level):
    txt = get(RDC % level, timeout=90, tries=2)
    say('realtor', level)
    rd = csv.DictReader(io.StringIO(txt))
    out = {}
    for r in rd:
        ym = str(r.get('month_date_yyyymm') or '').strip()
        if not re.match(r'\d{6}$', ym):
            continue
        if level == 'Country':
            key = 'US'
        else:
            key = (r.get('state_id') or '').strip().upper()
            if key not in STATES:
                key = BYNAME.get((r.get('state') or '').strip().lower())
        if not key:
            continue
        row = [ym[:4] + '-' + ym[4:], num(r.get('active_listing_count')), num(r.get('median_listing_price')),
               num(r.get('median_days_on_market')), num(r.get('price_reduced_count')), num(r.get('pending_listing_count'))]
        row = [row[0]] + [None if v is None else round(v) for v in row[1:]]
        out.setdefault(key, []).append(row)
    for k in out:
        out[k].sort()
    return out


# ------------------------------------------------------------------ main
def prev_json():
    try:
        return json.load(open(OUT))
    except Exception:
        pass
    try:
        return json.loads(get('https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/housing/housing.json', timeout=60))
    except Exception:
        return {}


def main():
    prev = prev_json()
    out = {'as_of': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), 'src': {}}
    # FRED: a few at a time (it answers slowly from cloud runners)
    f = dict(prev.get('f') or {})
    with cf.ThreadPoolExecutor(5) as ex:
        futs = {ex.submit(fred, s): s for s in FRED}
        for fu in cf.as_completed(futs):
            s = futs[fu]
            try:
                f[s] = fu.result()
            except Exception as e:
                LOG.append('fred %s FAILED (%s), kept %s' % (s, str(e)[:60], 'previous' if s in f else 'nothing'))
    out['f'] = f
    out['src']['fred'] = {s: (v[-1][0] if v else None) for s, v in f.items()}
    say('fred done', len(f))
    try:
        z, st, mt = zillow_all(prev)
        say('zillow done')
        if len(st) < 45 or len(mt) < 40:
            raise ValueError('too few rows: %d states, %d metros' % (len(st), len(mt)))
        out['z'], out['st'], out['mt'] = z, st, mt
    except Exception as e:
        LOG.append('zillow FAILED: %s' % str(e)[:120])
        for k in ('z', 'st', 'mt'):
            if prev.get(k):
                out[k] = prev[k]
    acs = acs_all()
    if len(acs) >= 45:
        out['acs'] = acs
    elif prev.get('acs'):
        out['acs'] = prev['acs']
        LOG.append('acs kept previous')
    r = {}
    for level in ('Country', 'State'):
        try:
            r.update(rdc(level))
        except Exception as e:
            LOG.append('realtor %s FAILED: %s' % (level, str(e)[:100]))
    out['rdc'] = r if len(r) >= 40 else (prev.get('rdc') or r)
    out['log'] = LOG
    json.dump(out, open(OUT, 'w'), separators=(',', ':'))
    print('\n'.join(LOG))
    print('fred %d series, states %d, metros %d, acs %d, realtor %d, %d KB' % (
        len(out['f']), len(out.get('st') or {}), len(out.get('mt') or []), len(out.get('acs') or {}), len(out.get('rdc') or {}),
        os.path.getsize(OUT) // 1024))
    # must-haves for the page: fail the job (and keep yesterday's file live) without them
    need = ['CSUSHPINSA', 'MORTGAGE30US', 'MSPUS']
    if not all(out['f'].get(s) for s in need) or not out.get('st'):
        sys.exit('missing core data')


PROBE = [
    'https://www.census.gov/construction/nrc/xls/starts_cust.xlsx',
    'https://www.census.gov/construction/nrc/xls/permits_cust.xlsx',
    'https://www.census.gov/construction/nrc/xls/co_cust.xlsx',
    'https://www.census.gov/construction/nrs/xls/sold_cust.xlsx',
    'https://www.census.gov/construction/nrs/xls/monthssupply_cust.xlsx',
    'https://www.census.gov/construction/nrs/xls/newressales.xlsx',
    'https://www.census.gov/construction/nrc/xls/newresconst.xlsx',
    'https://www.census.gov/econ/currentdata/export/csv?programCode=RESCONST&timeSlotType=12&startYear=2024&endYear=2026&categories=STARTS&dataType=TOTAL&geoLevel=US&adjusted=1&notAdjusted=0&errorData=0',
    'https://www.census.gov/housing/hvs/data/histtab1.xlsx',
    'https://www.census.gov/housing/hvs/data/histtab14.xlsx',
    'https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b25064.dat',
    'https://www2.census.gov/programs-surveys/acs/summary_file/2025/table-based-SF/data/1YRData/acsdt1y2025-b25064.dat',
    'https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/h08.xlsx',
    'https://www.federalreserve.gov/releases/chargeoff/delallsa.htm',
]


def probe():
    for u in PROBE:
        t = time.time()
        try:
            req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': '*/*'})
            r = urllib.request.urlopen(req, timeout=25)
            b = r.read()
            print('OK %3d %5.1fs %7d %s\n    %r' % (r.status, time.time() - t, len(b), u, b[:160]), flush=True)
            if b[:2] == b'PK':
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
                    for ws in wb.worksheets[:2]:
                        print('    sheet', ws.title)
                        for i, row in enumerate(ws.iter_rows(values_only=True)):
                            if i < 14 or i % 150 == 0:
                                print('     ', i, [c for c in row[:14]])
                        print('     last', [c for c in row[:14]])
                except Exception as e:
                    print('    xlsx', e)
            elif u.endswith('.dat'):
                L = b.decode('utf-8', 'replace').splitlines()
                print('    lines', len(L), L[0][:300])
                print('   ', [x[:200] for x in L if x.startswith('0400000US06') or x.startswith('0100000US')][:2])
            elif u.endswith('.htm'):
                txt = b.decode('utf-8', 'replace')
                i = txt.find('Residential')
                print('    ', re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', txt[i:i + 3000]))[:900])
        except Exception as e:
            print('XX       %5.1fs %s\n    %s' % (time.time() - t, u, str(e)[:200]), flush=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['probe']:
        probe()
    else:
        main()
