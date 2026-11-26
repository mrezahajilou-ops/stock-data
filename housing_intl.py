#!/usr/bin/env python3
"""Housing market data outside the US, for the country tabs of the housing pages (stockanaliz.com/housing/<cc>/ and the
sister sites). Keyless public sources that answer GitHub's runners. One file per country: housing_<cc>.json.

Shared   OECD analytical house prices (nominal / real price index, rent index, price-to-income, price-to-rent; quarterly),
         Yahoo Finance (local stock index, gold, exchange rate; weekly)
UK  gb   HM Land Registry UK HPI full file (average price by region and property type, sales volume, first-time buyers),
         Bank of England (2- and 5-year fixed mortgage rates, Bank Rate), ONS (CPI annual rate)
CA  ca   Statistics Canada (New Housing Price Index by province / city; CMHC average rent by province, building starts),
         Bank of Canada Valet (5-year conventional mortgage, policy rate)
IE  ie   CSO PxStat (Residential Property Price Index by region, median price by county, RTB average rent by county),
         ECB (new mortgage lending rate)
AU  au   ABS (mean dwelling price and dwelling stock by state), RBA (housing lending rates, cash rate)

Each file: {code, name, cur, as_of, idx{n, s:[[YYYY-MM, v]]}, price{n, s}, types{label: [[YYYY-MM, v]]}, rent{n, s},
            rates{label: [[YYYY-MM, v]]}, oecd{nom, real, rent, pti, ptr}, mkt{index, gold}, regions[{id, n, price, rent, idx, extra}],
            src[...], stamp}
A country whose sources fail keeps its previous file.
"""
import csv, io, json, os, re, sys, time, zipfile, datetime as dt, urllib.request, concurrent.futures as cf

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
OUTDIR = os.environ.get('OUTDIR', os.getcwd())
T0 = time.time()
TODAY = dt.date.today()


def say(*a):
    print('[%4ds]' % (time.time() - T0), *a, flush=True)


def getb(url, timeout=90, tries=3):
    last = None
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'}), timeout=timeout).read()
        except Exception as e:
            last = e
            time.sleep(3 * (a + 1))
    raise last


def get(url, **k):
    return getb(url, **k).decode('utf-8-sig', 'replace')


def num(x):
    try:
        v = float(str(x).replace(',', '').strip())
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def qm(p):
    """'2024-Q3' -> '2024-09' (quarter end month); '2024-07' stays."""
    m = re.match(r'^(\d{4})-?Q([1-4])$', p)
    if m:
        return '%s-%02d' % (m.group(1), int(m.group(2)) * 3)
    m = re.match(r'^(\d{4})-(\d\d)', p)
    if m:
        return m.group(1) + '-' + m.group(2)
    m = re.match(r'^(\d{4})M(\d\d)$', p)
    if m:
        return m.group(1) + '-' + m.group(2)
    m = re.match(r'^(\d{4})Q([1-4])$', p)
    if m:
        return '%s-%02d' % (m.group(1), int(m.group(2)) * 3)
    return p


def srt(d):
    return [[k, round(v, 4)] for k, v in sorted(d.items()) if v is not None]


# ------------------------------------------------------------------ shared
OECD_URL = ('https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/all'
            '?startPeriod=1970-Q1&format=csvfilewithlabels')


def oecd_all():
    rd = csv.DictReader(io.StringIO(get(OECD_URL, timeout=180)))
    out = {}
    for r in rd:
        if (r.get('FREQ') or '') != 'Q':
            continue
        lab = (r.get('Measure') or '').lower()
        key = ('real' if 'real house' in lab else 'nom' if 'nominal house' in lab else 'rent' if 'rent prices' in lab
               else 'pti' if 'income' in lab else 'ptr' if 'price to rent' in lab or 'price-to-rent' in lab else None)
        v = num(r.get('OBS_VALUE'))
        if key and v is not None:
            out.setdefault(r['REF_AREA'], {}).setdefault(key, {})[qm(r['TIME_PERIOD'])] = v
    say('oecd', len(out), sorted(out.get('GBR', {}).keys()))
    return {a: {k: srt(v) for k, v in d.items()} for a, d in out.items()}


def yahoo_weekly(sym, years=21):
    now = int(time.time())
    j = json.loads(get('https://query2.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1wk'
                       % (urllib.request.quote(sym), now - int(years * 365.25 * 86400), now)))
    r = j['chart']['result'][0]
    acc = {}
    for t, c in zip(r.get('timestamp') or [], ((r.get('indicators') or {}).get('quote') or [{}])[0].get('close') or []):
        if c:
            acc[dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m')] = c
    return acc   # month -> last weekly close


def market(index_sym, fx_sym):
    """Local stock index and gold in local currency, monthly."""
    idx = yahoo_weekly(index_sym)
    gold = yahoo_weekly('GC=F')
    fx = yahoo_weekly(fx_sym) if fx_sym else {}
    g = {m: (v / fx[m] if fx_sym else v) for m, v in gold.items() if (not fx_sym or fx.get(m))}
    return {'index': srt(idx), 'gold': srt(g)}


def jsonstat(url):
    """JSON-stat 2.0 -> list of ({dim: category label}, value)."""
    j = json.loads(get(url, timeout=180))
    ids, size, dims = j['id'], j['size'], j['dimension']
    cats = []
    for d in ids:
        c = dims[d]['category']
        idx = c['index']
        order = idx if isinstance(idx, list) else sorted(idx, key=lambda k: idx[k])
        cats.append([(k, (c.get('label') or {}).get(k, k)) for k in order])
    vals = j['value']
    out = []
    n = 1
    for s in size:
        n *= s
    for i in range(n):
        v = vals[i] if isinstance(vals, list) else vals.get(str(i))
        if v is None:
            continue
        rem, key = i, {}
        for d, s, c in zip(reversed(ids), reversed(size), reversed(cats)):
            key[d] = c[rem % s]
            rem //= s
        out.append((key, v))
    return out


# ------------------------------------------------------------------ United Kingdom
UK_REGIONS = ['North East', 'North West', 'Yorkshire and The Humber', 'East Midlands', 'West Midlands', 'East of England', 'London',
              'South East', 'South West', 'Wales', 'Scotland', 'Northern Ireland']


def lr_url():
    for back in range(0, 5):
        d = (TODAY.replace(day=1) - dt.timedelta(days=28 * back + 1))
        u = 'https://publicdata.landregistry.gov.uk/market-trend-data/house-price-index-data/UK-HPI-full-file-%s.csv' % d.strftime('%Y-%m')
        try:
            urllib.request.urlopen(urllib.request.Request(u, method='HEAD', headers={'User-Agent': UA}), timeout=30)
            return u
        except Exception:
            continue
    raise ValueError('no UK HPI file found')


def boe(codes):
    u = ('https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/1995&Dateto=now'
         '&SeriesCodes=%s&CSVF=TN&UsingCodes=Y' % ','.join(codes))
    rd = csv.DictReader(io.StringIO(get(u)))
    out = {c: {} for c in codes}
    for r in rd:
        try:
            m = dt.datetime.strptime(r['DATE'].strip(), '%d %b %Y').strftime('%Y-%m')
        except (KeyError, ValueError):
            continue
        for c in codes:
            v = num(r.get(c))
            if v is not None:
                out[c][m] = v
    return {c: srt(v) for c, v in out.items()}


def ons_series(sid, ds='mm23'):
    j = json.loads(get('https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/%s/%s/data' % (sid, ds)))
    mon = {m['month'][:3]: i + 1 for i, m in enumerate([{'month': x} for x in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']])}
    out = {}
    for r in j.get('months') or []:
        v = num(r.get('value'))
        if v is not None and r.get('year') and r.get('month'):
            out['%s-%02d' % (r['year'], mon.get(r['month'][:3], 0))] = v
    return srt(out)


def gb():
    rd = csv.DictReader(io.StringIO(get(lr_url(), timeout=240)))
    regions, uk = {}, {}
    cols = {'price': 'AveragePrice', 'idx': 'Index', 'det': 'DetachedPrice', 'semi': 'SemiDetachedPrice', 'ter': 'TerracedPrice',
            'flat': 'FlatPrice', 'vol': 'SalesVolume', 'ftb': 'FTBPrice', 'new': 'NewPrice', 'old': 'OldPrice'}
    for r in rd:
        name = (r.get('RegionName') or '').strip()
        if name not in UK_REGIONS and name != 'United Kingdom':
            continue
        try:
            m = dt.datetime.strptime(r['Date'].strip(), '%d/%m/%Y').strftime('%Y-%m')
        except ValueError:
            try:
                m = r['Date'][:7]
            except Exception:
                continue
        tgt = uk if name == 'United Kingdom' else regions.setdefault(name, {})
        for k, c in cols.items():
            v = num(r.get(c))
            if v is not None:
                tgt.setdefault(k, {})[m] = v
    say('gb land registry', len(regions), sorted(uk.get('price', {}).items())[-1:])
    rates = boe(['IUMBV34', 'IUMBV42', 'IUMBEDR'])
    out = {'code': 'gb', 'name': 'United Kingdom', 'cur': 'GBP', 'sym': '£', 'oecd_code': 'GBR',
           'idx': {'n': 'UK House Price Index', 's': srt(uk['idx'])},
           'price': {'n': 'Average house price', 's': srt(uk['price'])},
           'types': {'Detached': srt(uk.get('det', {})), 'Semi-detached': srt(uk.get('semi', {})), 'Terraced': srt(uk.get('ter', {})), 'Flat': srt(uk.get('flat', {}))},
           'extra': {'ftb': srt(uk.get('ftb', {})), 'vol': srt(uk.get('vol', {})), 'new': srt(uk.get('new', {})), 'old': srt(uk.get('old', {}))},
           'rates': {'2-year fixed mortgage (75% LTV)': rates['IUMBV34'], '5-year fixed mortgage (75% LTV)': rates['IUMBV42'], 'Bank Rate': rates['IUMBEDR']},
           'regions': [{'id': n, 'n': n, 'price': srt(d.get('price', {})), 'types': {'Detached': srt(d.get('det', {})), 'Semi-detached': srt(d.get('semi', {})),
                        'Terraced': srt(d.get('ter', {})), 'Flat': srt(d.get('flat', {}))}, 'vol': srt(d.get('vol', {}))[-24:]} for n, d in regions.items()],
           'mkt': market('^FTSE', 'GBPUSD=X'),
           'src': ['HM Land Registry, UK House Price Index', 'Bank of England', 'OECD', 'Yahoo Finance']}
    try:
        out['cpi_rate'] = ons_series('d7g7')
    except Exception as e:
        say('ons cpi', e)
    return out


# ------------------------------------------------------------------ Canada
CA_PROV = {'Newfoundland and Labrador': 'NL', 'Prince Edward Island': 'PE', 'Nova Scotia': 'NS', 'New Brunswick': 'NB', 'Quebec': 'QC',
           'Ontario': 'ON', 'Manitoba': 'MB', 'Saskatchewan': 'SK', 'Alberta': 'AB', 'British Columbia': 'BC', 'Yukon': 'YT',
           'Northwest Territories': 'NT', 'Nunavut': 'NU'}


def statcan(pid):
    z = zipfile.ZipFile(io.BytesIO(getb('https://www150.statcan.gc.ca/n1/tbl/csv/%s-eng.zip' % pid, timeout=240)))
    name = [n for n in z.namelist() if n.startswith(pid) and n.endswith('.csv') and 'MetaData' not in n][0]
    return csv.DictReader(io.TextIOWrapper(z.open(name), encoding='utf-8-sig'))


def valet(series):
    j = json.loads(get('https://www.bankofcanada.ca/valet/observations/%s/json?start_date=1990-01-01' % series))
    out = {}
    for o in j.get('observations') or []:
        v = num((o.get(series) or {}).get('v'))
        if v is not None:
            out[o['d'][:7]] = v
    return srt(out)


def ca():
    nh, prov = {}, {}
    for r in statcan('18100205'):
        if r.get('New housing price indexes') != 'Total (house and land)':
            continue
        geo = r['GEO'].split(',')[0].strip()
        v = num(r.get('VALUE'))
        if v is None:
            continue
        if geo == 'Canada':
            nh[r['REF_DATE'][:7]] = v
        elif geo in CA_PROV:
            prov.setdefault(geo, {})[r['REF_DATE'][:7]] = v
    rent = {}
    for r in statcan('34100133'):
        geo = r['GEO'].strip()
        if r.get('Type of unit') != 'Two bedroom units' or 'three units and over' not in (r.get('Type of structure') or ''):
            continue
        v = num(r.get('VALUE'))
        if v is None:
            continue
        key = 'Canada' if geo == 'Canada' else geo if geo in CA_PROV else None
        if key:
            rent.setdefault(key, {})[r['REF_DATE'][:4] + '-10'] = v   # CMHC survey: October
    say('ca statcan', len(prov), len(rent), sorted(nh.items())[-1:])
    starts = {}
    try:
        for r in statcan('34100158'):
            if r.get('GEO') == 'Canada' and 'Total units' in (r.get('Type of unit') or '') and 'Seasonally adjusted at annual rates' in (r.get('Seasonal adjustment') or r.get('Adjustments') or ''):
                v = num(r.get('VALUE'))
                if v is not None:
                    starts[r['REF_DATE'][:7]] = v / 1000 if v > 5000 else v
    except Exception as e:
        say('ca starts', str(e)[:80])
    return {'code': 'ca', 'name': 'Canada', 'cur': 'CAD', 'sym': 'C$', 'oecd_code': 'CAN',
            'idx': {'n': 'New Housing Price Index', 's': srt(nh)},
            'rent': {'n': 'Average rent, 2-bedroom apartment (CMHC, October)', 's': srt(rent.get('Canada', {}))},
            'rates': {'5-year conventional mortgage': valet('V80691335'), 'Bank of Canada policy rate': valet('V39079')},
            'starts': srt(starts),
            'regions': [{'id': CA_PROV[p], 'n': p, 'idx': srt(prov.get(p, {})), 'rent': srt(rent.get(p, {}))} for p in CA_PROV if prov.get(p) or rent.get(p)],
            'mkt': market('^GSPTSE', 'CADUSD=X'),
            'src': ['Statistics Canada', 'CMHC Rental Market Survey', 'Bank of Canada', 'OECD', 'Yahoo Finance']}


# ------------------------------------------------------------------ Ireland
IE_COUNTIES = ['Carlow', 'Cavan', 'Clare', 'Cork', 'Donegal', 'Dublin', 'Galway', 'Kerry', 'Kildare', 'Kilkenny', 'Laois', 'Leitrim', 'Limerick',
               'Longford', 'Louth', 'Mayo', 'Meath', 'Monaghan', 'Offaly', 'Roscommon', 'Sligo', 'Tipperary', 'Waterford', 'Westmeath', 'Wexford', 'Wicklow']


def ecb_mir(cc):
    for key in ('M.%s.B.A2C.AM.R.A.2250.EUR.N' % cc, 'M.%s.B.A2C.A.R.A.2250.EUR.N' % cc):
        try:
            rd = csv.DictReader(io.StringIO(get('https://data-api.ecb.europa.eu/service/data/MIR/%s?format=csvdata' % key, tries=2)))
            out = {r['TIME_PERIOD'][:7]: num(r['OBS_VALUE']) for r in rd if num(r.get('OBS_VALUE')) is not None}
            if out:
                return srt(out)
        except Exception as e:
            say('ecb', key, str(e)[:60])
    return []


def ecb_rate():
    rd = csv.DictReader(io.StringIO(get('https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.4F.KR.DFR.LEV?format=csvdata', tries=2)))
    out = {}
    for r in rd:
        v = num(r.get('OBS_VALUE'))
        if v is not None:
            out[r['TIME_PERIOD'][:7]] = v
    return srt(out)


def ie():
    idx, reg = {}, {}
    for k, v in jsonstat('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HPM09/JSON-stat/2.0/en'):
        if not k['STATISTIC'][1].startswith('Residential Property Price Index'):
            continue
        t = next(c for d, c in k.items() if d.startswith('TLIST'))
        m = qm(t[0])
        other = [c[1] for d, c in k.items() if d not in ('STATISTIC',) and not d.startswith('TLIST')]
        lab = ' | '.join(other)
        reg.setdefault(lab, {})[m] = v
    nat = next((s for l, s in reg.items() if l.lower().startswith('national') and 'all residential' in l.lower()), None) or next(
        (s for l, s in reg.items() if 'national' in l.lower()), {})
    say('ie rppi', len(reg), list(reg)[:8])
    med = {}
    try:
        for k, v in jsonstat('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HPM04/JSON-stat/2.0/en'):
            if 'Median' not in k['STATISTIC'][1]:
                continue
            labs = {d: c[1] for d, c in k.items()}
            t = next(c for d, c in k.items() if d.startswith('TLIST'))
            area = next((c for d, c in labs.items() if c.replace('Co. ', '').strip() in IE_COUNTIES or c == 'Ireland' or c.startswith('Dublin')), None)
            if not area:
                continue
            if any(('All' not in c and ('Dwelling' in d or 'Buyer' in d or 'Stamp' in d or 'Type' in d)) for d, c in labs.items() if not d.startswith('TLIST') and d != 'STATISTIC' and c != area):
                continue
            med.setdefault(area.replace('Co. ', '').strip(), {})[qm(t[0])] = v
    except Exception as e:
        say('ie median', str(e)[:100])
    rent = {}
    try:
        for k, v in jsonstat('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIQ02/JSON-stat/2.0/en'):
            labs = {d: c[1] for d, c in k.items()}
            t = next(c for d, c in k.items() if d.startswith('TLIST'))
            loc = next((c for d, c in labs.items() if c in IE_COUNTIES or c == 'Ireland'), None)
            if not loc:
                continue
            if any(('All' not in c) for d, c in labs.items() if d not in ('STATISTIC',) and not d.startswith('TLIST') and c != loc):
                continue
            rent.setdefault(loc, {})[qm(t[0])] = v
    except Exception as e:
        say('ie rent', str(e)[:100])
    say('ie', len(med), len(rent), sorted((med.get('Ireland') or {}).items())[-1:], sorted((rent.get('Ireland') or {}).items())[-1:])
    return {'code': 'ie', 'name': 'Ireland', 'cur': 'EUR', 'sym': '€', 'oecd_code': 'IRL',
            'idx': {'n': 'Residential Property Price Index', 's': srt(nat)},
            'price': {'n': 'Median sale price', 's': srt(med.get('Ireland', {}))},
            'rent': {'n': 'Average monthly rent (RTB, new tenancies)', 's': srt(rent.get('Ireland', {}))},
            'rates': {'New mortgage lending rate': ecb_mir('IE'), 'ECB deposit rate': ecb_rate()},
            'rindex': {l: srt(s) for l, s in reg.items()},
            'regions': [{'id': c, 'n': c, 'price': srt(med.get(c, {})), 'rent': srt(rent.get(c, {}))} for c in IE_COUNTIES if med.get(c) or rent.get(c)],
            'mkt': market('^ISEQ', 'EURUSD=X'),
            'src': ['Central Statistics Office (CSO)', 'Residential Tenancies Board', 'European Central Bank', 'OECD', 'Yahoo Finance']}


# ------------------------------------------------------------------ Australia
AU_ST = {'New South Wales': 'NSW', 'Victoria': 'VIC', 'Queensland': 'QLD', 'South Australia': 'SA', 'Western Australia': 'WA',
         'Tasmania': 'TAS', 'Northern Territory': 'NT', 'Australian Capital Territory': 'ACT', 'Australia': 'AUS'}


def rba(table, want):
    txt = get('https://www.rba.gov.au/statistics/tables/csv/%s-data.csv' % table)
    rows = list(csv.reader(io.StringIO(txt)))
    title = next(r for r in rows if r and r[0] == 'Title')
    cols = {lab: next((i for i, t in enumerate(title) if t.strip().lower() == w.lower()), None) for lab, w in want.items()}
    out = {lab: {} for lab in want}
    for r in rows:
        if not r or not re.match(r'\d{1,2}-[A-Za-z]{3}-\d{4}$', r[0].strip()):
            continue
        m = dt.datetime.strptime(r[0].strip(), '%d-%b-%Y').strftime('%Y-%m')
        for lab, i in cols.items():
            if i is not None and i < len(r) and num(r[i]) is not None:
                out[lab][m] = num(r[i])
    return {k: srt(v) for k, v in out.items()}


def au():
    rd = csv.DictReader(io.StringIO(get('https://data.api.abs.gov.au/rest/data/ABS,RES_DWELL_ST,1.0.0/all?startPeriod=2002-Q1&format=csvfilewithlabels', timeout=180)))
    price, count = {}, {}
    for r in rd:
        meas = (r.get('Measure') or '').lower()
        reg = (r.get('Region') or '').strip()
        reg = next((k for k in AU_ST if reg.lower().startswith(k.lower())), None)
        v = num(r.get('OBS_VALUE'))
        if not reg or v is None:
            continue
        mult = 10 ** int(num(r.get('UNIT_MULT')) or 0)
        if 'mean price' in meas:
            price.setdefault(reg, {})[qm(r['TIME_PERIOD'])] = v * mult if v < 10000 else v
        elif 'number' in meas:
            count.setdefault(reg, {})[qm(r['TIME_PERIOD'])] = v * mult
    say('au abs', len(price), sorted(price.get('Australia', {}).items())[-1:])
    rates = rba('f5', {'Standard variable mortgage (owner-occupier)': 'Lending rates; Housing loans; Banks; Variable; Standard; Owner-occupier',
                       'Discounted variable mortgage (owner-occupier)': 'Lending rates; Housing loans; Banks; Variable; Discounted; Owner-occupier'})
    try:
        rates.update(rba('f1.1', {'RBA cash rate target': 'Cash Rate Target'}))
    except Exception as e:
        say('rba cash', str(e)[:60])
    return {'code': 'au', 'name': 'Australia', 'cur': 'AUD', 'sym': 'A$', 'oecd_code': 'AUS',
            'price': {'n': 'Mean price of residential dwellings', 's': srt(price.get('Australia', {}))},
            'rates': rates,
            'regions': [{'id': AU_ST[s], 'n': s, 'price': srt(price.get(s, {})), 'count': srt(count.get(s, {}))[-1:]} for s in AU_ST if s != 'Australia' and price.get(s)],
            'mkt': market('^AXJO', 'AUDUSD=X'),
            'src': ['Australian Bureau of Statistics', 'Reserve Bank of Australia', 'OECD', 'Yahoo Finance']}


COUNTRIES = {'gb': gb, 'ca': ca, 'ie': ie, 'au': au}


def main():
    only = sys.argv[1:] or list(COUNTRIES)
    try:
        oecd = oecd_all()
    except Exception as e:
        say('OECD FAILED', e)
        oecd = {}
    ok = 0
    with cf.ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(COUNTRIES[c]): c for c in only}
        for fu in cf.as_completed(futs):
            c = futs[fu]
            path = os.path.join(OUTDIR, 'housing_%s.json' % c)
            try:
                d = fu.result()
            except Exception as e:
                import traceback
                traceback.print_exc()
                say('%s FAILED: %s (previous file kept)' % (c, str(e)[:200]))
                try:
                    prev = get('https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/housing/housing_%s.json' % c, tries=1)
                    open(path, 'w').write(prev)
                except Exception:
                    pass
                continue
            d['oecd'] = oecd.get(d['oecd_code']) or {}
            d['as_of'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
            lasts = []
            for k in ('idx', 'price', 'rent'):
                if (d.get(k) or {}).get('s'):
                    lasts.append('%s=%s' % (k, d[k]['s'][-1][0]))
            for k, s in (d.get('rates') or {}).items():
                if s:
                    lasts.append('%s=%s' % (k[:12], s[-1][0]))
            d['stamp'] = '|'.join(lasts)
            json.dump(d, open(path, 'w'), separators=(',', ':'))
            ok += 1
            say(c, 'ok', os.path.getsize(path) // 1024, 'KB', d['stamp'])
    if not ok:
        sys.exit('no country built')


if __name__ == '__main__':
    main()
