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
    m = re.match(r'^(\d{4})(\d\d)$', p)          # CSO monthly: 202609
    if m:
        return m.group(1) + '-' + m.group(2)
    m = re.match(r'^(\d{4})([1-4])$', p)           # CSO quarterly: 20254
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


def dims_debug(url, rows):
    seen = {}
    for k, _ in rows:
        for d, c in k.items():
            if not d.startswith('TLIST'):
                seen.setdefault(d, set()).add(c[1])
    say('DIMS', url.split('/')[-4], {d: sorted(v)[:14] + (['... %d' % len(v)] if len(v) > 14 else []) for d, v in seen.items()})


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
    cen = {}
    for r in statcan('34100133'):
        if r.get('Type of unit') != 'Two bedroom units' or r.get('Type of structure') != 'Row and apartment structures of three units and over':
            continue
        v = num(r.get('VALUE'))
        if v is None:
            continue
        pv = r['GEO'].split(',')[-1].strip()
        pv = next((p for p in CA_PROV if pv.startswith(p) or pv.split('/')[0].strip() == p), None)
        if pv:
            cen.setdefault(pv, {}).setdefault(r['REF_DATE'][:4] + '-10', []).append(v)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    rent = {p: {k: med(v) for k, v in d.items()} for p, d in cen.items()}
    allc = {}
    for d in cen.values():
        for k, v in d.items():
            allc.setdefault(k, []).extend(v)
    rent['Canada'] = {k: med(v) for k, v in allc.items()}
    say('ca statcan', len(prov), len(rent), sorted(nh.items())[-1:], sorted(rent['Canada'].items())[-1:])
    starts = {}
    try:
        for r in statcan('34100158'):
            if r.get('GEO') == 'Canada':
                v = num(r.get('VALUE'))
                if v is not None:
                    starts[r['REF_DATE'][:7]] = v
    except Exception as e:
        say('ca starts', str(e)[:80])
    return {'code': 'ca', 'name': 'Canada', 'cur': 'CAD', 'sym': 'C$', 'oecd_code': 'CAN',
            'idx': {'n': 'New Housing Price Index', 's': srt(nh)},
            'rent': {'n': 'Typical 2-bedroom rent (median of CMHC centres, October)', 's': srt(rent.get('Canada', {}))},
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


def ie_debug():
    for t in ('HPM02', 'HPM03', 'HPM05', 'HPM06', 'HPM07', 'HPM08', 'HPA02', 'HPA06'):
        try:
            dims_debug('x/%s/a/b' % t, jsonstat('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/%s/JSON-stat/2.0/en' % t))
        except Exception as e:
            say(t, str(e)[:80])


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
    try:   # HPM07: moving 12-month median sale price by county, monthly (all buyers, existing + new, executions)
        raw = {}
        for k, v in jsonstat('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HPM07/JSON-stat/2.0/en'):
            labs = {d: c[1] for d, c in k.items()}
            if 'Median' not in labs.get('STATISTIC', ''):
                continue
            if any(c in ('Filings', 'Existing', 'New') or (c.startswith('Household Buyer')) for c in labs.values()):
                continue
            t = next(c for d, c in k.items() if d.startswith('TLIST'))
            area = next((c for d, c in labs.items() if not d.startswith('TLIST') and d != 'STATISTIC' and c not in ('Executions', 'All Dwelling Statuses', 'All Buyer Types')), None)
            if area:
                raw.setdefault(area, {})[qm(t[0])] = v
        for c in IE_COUNTIES + ['All']:
            src = raw.get(c) or raw.get(c + ' County') or raw.get('County ' + c)
            if src:
                med['Ireland' if c == 'All' else c] = src
        say('ie hpm07 areas', sorted(raw)[:50])
    except Exception as e:
        say('ie median', str(e)[:100])
    rent = {}
    try:
        rows = jsonstat('https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIQ02/JSON-stat/2.0/en')
        for k, v in rows:
            labs = {d: c[1] for d, c in k.items()}
            t = next(c for d, c in k.items() if d.startswith('TLIST'))
            loc = next((c for d, c in labs.items() if c in IE_COUNTIES or c in ('Ireland', 'State', 'National')), None)
            if not loc:
                continue
            if any(('All' not in c) for d, c in labs.items() if d not in ('STATISTIC',) and not d.startswith('TLIST') and c != loc):
                continue
            rent.setdefault('Ireland' if loc in ('State', 'National') else loc, {})[qm(t[0])] = v
    except Exception as e:
        say('ie rent', str(e)[:100])
    say('ie', len(med), len(rent), sorted((med.get('Ireland') or {}).items())[-1:], sorted((rent.get('Ireland') or {}).items())[-1:])
    return {'code': 'ie', 'name': 'Ireland', 'cur': 'EUR', 'sym': '€', 'oecd_code': 'IRL',
            'idx': {'n': 'Residential Property Price Index', 's': srt(nat)},
            'price': {'n': 'Median sale price (12 months)', 's': srt(med.get('Ireland', {}))},
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
        d0 = r[0].strip() if r else ''
        if re.match(r'\d{1,2}-[A-Za-z]{3}-\d{4}$', d0):
            m = dt.datetime.strptime(d0, '%d-%b-%Y').strftime('%Y-%m')
        elif re.match(r'\d{1,2}/\d{1,2}/\d{4}$', d0):
            m = dt.datetime.strptime(d0, '%d/%m/%Y').strftime('%Y-%m')
        else:
            continue
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
    rates = rba('f5', {'Discounted variable mortgage (owner-occupier)': 'Lending rates; Housing loans; Banks; Variable; Discounted; Owner-occupier',
                       '3-year fixed mortgage (owner-occupier)': 'Lending rates; Housing loans; Banks; 3-year fixed; Owner-occupier'})
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


# ------------------------------------------------------------------ other countries (national data; regions where a keyless source exists)
BIS = {}


def bis_load():
    if BIS:
        return BIS
    z = zipfile.ZipFile(io.BytesIO(getb('https://data.bis.org/static/bulk/WS_SPP_csv_flat.zip', timeout=180)))
    for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='utf-8-sig')):
        area, val, unit = r['REF_AREA:Reference area'][:2], r['VALUE:Value'][:1], r['UNIT_MEASURE:Unit of measure'][:3]
        v = num(r.get('OBS_VALUE:Observation Value'))
        if v is None or unit != '628' or (r.get('FREQ:Frequency') or '')[:1] != 'Q':
            continue
        BIS.setdefault(area, {}).setdefault('nom' if val == 'N' else 'real' if val == 'R' else '?', {})[qm(r['TIME_PERIOD:Time period or range'])] = v
    z = zipfile.ZipFile(io.BytesIO(getb('https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip', timeout=180)))
    for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='utf-8-sig')):
        if (r.get('FREQ:Frequency') or '')[:1] != 'M':
            continue
        v = num(r.get('OBS_VALUE:Observation Value'))
        if v is not None:
            BIS.setdefault(r['REF_AREA:Reference area'][:2], {}).setdefault('pol', {})[r['TIME_PERIOD:Time period or range'][:7]] = v
    try:   # detailed series for areas missing from the selected set (UAE, Saudi Arabia ...)
        z = zipfile.ZipFile(io.BytesIO(getb('https://data.bis.org/static/bulk/WS_DPP_csv_flat.zip', timeout=240)))
        cand = {}
        for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='utf-8-sig')):
            area = (r.get('REF_AREA:Reference area') or '')[:2]
            if area not in ('AE', 'SA') or (BIS.get(area) or {}).get('nom'):
                continue
            v = num(r.get('OBS_VALUE:Observation Value'))
            if v is None:
                continue
            key = r.get('KEY') or '|'.join(r.get(c, '')[:40] for c in r if c and c.split(':')[0] not in ('TIME_PERIOD', 'OBS_VALUE', 'OBS_STATUS', 'OBS_CONF', 'OBS_PRE_BREAK', 'STRUCTURE', 'STRUCTURE_ID', 'ACTION'))
            cand.setdefault(area, {}).setdefault(key, {})[qm(r['TIME_PERIOD:Time period or range'])] = v
        for area, ser in cand.items():
            say('bis dpp', area, [(k[:160], len(v)) for k, v in ser.items()][:12])
            idx = [(k, v) for k, v in ser.items() if 'ndex' in k and 'year' not in k.lower() and 'change' not in k.lower()]
            if idx:
                k, v = max(idx, key=lambda kv: len(kv[1]))
                BIS[area]['nom'] = v
                say('bis dpp pick', area, k[:200], len(v))
    except Exception as e:
        say('bis dpp', str(e)[:100])
    say('bis', len(BIS))
    return BIS


def eurostat(geo):
    out = {}
    for typ in ('TOTAL', 'DW_NEW', 'DW_EXST'):
        j = json.loads(get('https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hpi_q?geo=%s&unit=I15_Q&purchase=%s' % (geo, typ)))
        idx = j['dimension']['time']['category']['index']
        rev = {v: k for k, v in idx.items()}
        out[typ] = srt({qm(rev[int(i)]): v for i, v in j['value'].items()})
    return out


INE_Q = {19: 3, 20: 6, 21: 9, 22: 12}


def es_regions():
    j = json.loads(get('https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/25171?nult=120', timeout=120))
    out = {}
    for s in j:
        n = s.get('Nombre') or ''
        parts = [p.strip() for p in n.split('.') if p.strip()]
        if len(parts) < 3 or parts[1] != 'General' or not parts[2].startswith('Índice'):
            continue
        d = {}
        for o in s.get('Data') or []:
            m = INE_Q.get(o.get('FK_Periodo'))
            if m and o.get('Valor') is not None:
                d['%d-%02d' % (o['Anyo'], m)] = o['Valor']
        out[parts[0]] = srt(d)
    say('es ine', len(out), list(out)[:20])
    return out


def pt_regions():
    j = json.loads(get('https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0009490&lang=EN', timeout=120))
    dados = j[0].get('Dados') or {}
    out = {}
    for per, rows in dados.items():
        m = re.search(r'(\d)\w* Quarter (\d{4})', per) or re.search(r'(\d)T(\d{4})', per) or re.search(r'Q(\d) (\d{4})', per)
        if not m:
            continue
        k = '%s-%02d' % (m.group(2), int(m.group(1)) * 3)
        for row in rows:
            v = num(row.get('valor'))
            if v is not None:
                out.setdefault(row.get('geodsg'), {})[k] = v
    say('pt ine', len(out), list(dados)[:3], list(out)[:30], str(j[0])[:300] if not out else '')
    return {k: srt(v) for k, v in out.items()}


def br_fipezap():
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(getb('https://downloads.fipe.org.br/indices/fipezap/fipezap-serieshistoricas.xlsx', timeout=180)), read_only=True, data_only=True)
    say('fipezap sheets', [w.title for w in wb.worksheets][:70])
    out = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 6:
            continue
        hdr = None
        for i, r in enumerate(rows[:8]):
            if r and any(isinstance(c, str) and ('R$/m' in c or 'Preço médio' in c or 'Preco medio' in c) for c in r):
                hdr = i
        if ws.title in ('Resumo', 'Índice FipeZap') or hdr is None:
            if len(out) < 2:
                say('fipezap sample', ws.title, [list(r)[:12] for r in rows[:6]])
            continue
        head = [str(c or '') for c in rows[hdr]]
        sub = [str(c or '') for c in rows[hdr + 1]] if hdr + 1 < len(rows) else []
        blocks, cur = {}, None
        for i, c in enumerate(head):
            if c.strip():
                cur = c
            blocks[i] = cur or ''
        pcols = [i for i in range(len(sub)) if 'Preço médio' in blocks.get(i, '') and sub[i].strip() == 'Total']
        dcol = next((i for i, c in enumerate(sub) if c.strip() == 'Data'), 1)
        if len(out) < 1:
            say('fipezap cols', ws.title, [(i, blocks[i]) for i in pcols], [c for c in head if c][:12], dcol)
        sale, rent = {}, {}
        for r in rows[hdr + 2:]:
            if not r or len(r) <= dcol or not isinstance(r[dcol], dt.datetime):
                continue
            k = r[dcol].strftime('%Y-%m')
            if len(pcols) >= 1 and num(r[pcols[0]]):
                sale[k] = num(r[pcols[0]])
            if len(pcols) >= 2 and num(r[pcols[1]]):
                rent[k] = num(r[pcols[1]])
        if sale:
            out[ws.title] = {'sale': srt(sale), 'rent': srt(rent)}
    say('fipezap cities', len(out), list(out)[:60])
    return out


def ecb_mir_try(cc):
    try:
        return ecb_mir(cc)
    except Exception:
        return []


GEN = {
    'de': ('Germany', 'EUR', '€', 'DEU', 'DE', '^GDAXI', 'EURUSD=X', 'eu'),
    'at': ('Austria', 'EUR', '€', 'AUT', 'AT', '^ATX', 'EURUSD=X', 'eu'),
    'ch': ('Switzerland', 'CHF', 'CHF', 'CHE', 'CH', '^SSMI', 'CHFUSD=X', None),
    'fr': ('France', 'EUR', '€', 'FRA', 'FR', '^FCHI', 'EURUSD=X', 'eu'),
    'it': ('Italy', 'EUR', '€', 'ITA', 'IT', 'FTSEMIB.MI', 'EURUSD=X', 'eu'),
    'es': ('Spain', 'EUR', '€', 'ESP', 'ES', '^IBEX', 'EURUSD=X', 'eu'),
    'pt': ('Portugal', 'EUR', '€', 'PRT', 'PT', 'PSI20.LS', 'EURUSD=X', 'eu'),
    'br': ('Brazil', 'BRL', 'R$', 'BRA', 'BR', '^BVSP', 'BRLUSD=X', None),
    'id': ('Indonesia', 'IDR', 'Rp', 'IDN', 'ID', '^JKSE', 'IDRUSD=X', None),
    'kr': ('South Korea', 'KRW', '₩', 'KOR', 'KR', '^KS11', 'KRWUSD=X', None),
    'jp': ('Japan', 'JPY', '¥', 'JPN', 'JP', '^N225', 'JPYUSD=X', None),
    'ae': ('United Arab Emirates', 'AED', 'AED', 'ARE', 'AE', 'DFMGI.AE', 'AEDUSD=X', None),
    'sa': ('Saudi Arabia', 'SAR', 'SAR', 'SAU', 'SA', '^TASI.SR', 'SARUSD=X', None),
    'tr': ('Turkey', 'TRY', '₺', 'TUR', 'TR', 'XU100.IS', 'TRYUSD=X', None),
}


def generic(cc):
    name, cur, sym, o3, a2, idx_sym, fx, zone = GEN[cc]
    b = bis_load().get(a2) or {}
    out = {'code': cc, 'name': name, 'cur': cur, 'sym': sym, 'oecd_code': o3, 'src': []}
    if zone == 'eu':
        e = eurostat(a2)
        out['idx'] = {'n': 'House price index (Eurostat)', 's': e['TOTAL']}
        out['types'] = {'New dwellings': e['DW_NEW'], 'Existing dwellings': e['DW_EXST']}
        out['src'].append('Eurostat')
        out['rates'] = {'New mortgage lending rate': ecb_mir_try(a2), 'ECB deposit rate': ecb_rate()}
        out['src'].append('European Central Bank')
    else:
        if b.get('nom'):
            out['idx'] = {'n': 'Residential property price index (BIS)', 's': srt(b['nom'])}
            out['src'].append('Bank for International Settlements')
        out['rates'] = {'Central bank policy rate': srt(b.get('pol') or {})}
        if 'Bank for International Settlements' not in out['src']:
            out['src'].append('Bank for International Settlements')
    if b.get('real'):
        out['bis_real'] = srt(b['real'])
    regions = []
    if cc == 'es':
        for n, s in es_regions().items():
            if n != 'Nacional':
                regions.append({'id': n, 'n': n, 'idx': s})
        out['src'].insert(0, 'Instituto Nacional de Estadística (INE)')
    if cc == 'pt':
        pr = pt_regions()
        for n, s in pr.items():
            regions.append({'id': n, 'n': n, 'price': s})
        nat = pr.get('Portugal')
        if nat:
            out['price'] = {'n': 'Median sale price per m²', 's': nat}
        out['src'].insert(0, 'Statistics Portugal (INE)')
    if cc == 'br':
        fz = br_fipezap()
        nat = next((v for k, v in fz.items() if 'ndice' in k or 'FipeZap' in k or 'Brasil' in k), None)
        if nat:
            out['price'] = {'n': 'Average asking price per m² (FipeZap, 50 cities)', 's': nat['sale']}
            if nat.get('rent'):
                out['rent'] = {'n': 'Average asking rent per m² (FipeZap)', 's': nat['rent']}
        for k, v in fz.items():
            if v is not nat:
                regions.append({'id': k, 'n': k, 'price': v['sale'], 'rent': v.get('rent') or []})
        out['src'].insert(0, 'FipeZap')
    out['regions'] = [r for r in regions if r['n'] != 'Portugal']
    out['mkt'] = market(idx_sym, fx)
    out['src'] += ['OECD', 'Yahoo Finance']
    return out


COUNTRIES = {'gb': gb, 'ca': ca, 'ie': ie, 'au': au}
COUNTRIES.update({c: (lambda c=c: generic(c)) for c in GEN})


def main():
    only = sys.argv[1:] or list(COUNTRIES)
    try:
        oecd = oecd_all()
    except Exception as e:
        say('OECD FAILED', e)
        oecd = {}
    ok = 0
    if any(c in GEN for c in only):
        try:
            bis_load()
        except Exception as e:
            say('BIS FAILED', e)
    with cf.ThreadPoolExecutor(6) as ex:
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
