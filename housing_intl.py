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
    acc = yahoo_series(sym, years, '1wk')
    if len(acc) < 24:          # some Gulf indexes answer only the last bar for weekly data: monthly instead
        for iv in ('1mo', 'range'):
            try:
                acc2 = yahoo_series(sym, years, iv)
                if len(acc2) > len(acc):
                    acc = acc2
            except Exception:
                pass
    return acc


def yahoo_series(sym, years, iv):
    now = int(time.time())
    if iv == 'range':
        j = json.loads(get('https://query1.finance.yahoo.com/v8/finance/chart/%s?range=max&interval=1mo' % urllib.request.quote(sym)))
    else:
        j = json.loads(get('https://query2.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=%s'
                           % (urllib.request.quote(sym), now - int(years * 365.25 * 86400), now, iv)))
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
            BIS.setdefault(area, {})['dpp'] = {('country' if 'Whole country' in k else 'capital' if 'Capital city' in k else 'cities' if 'Big cities' in k else k[:40]): v for k, v in ser.items()}
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


EN_MON = {m: i + 1 for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])}


def pt_regions():
    """INE indicator 0012248: median bank valuation of housing, EUR/m2, monthly, by NUTS region (total / apartments / houses)."""
    j = json.loads(get('https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0012248&Dim1=T&lang=EN', timeout=180))
    dados = j[0].get('Dados') or {}
    out, geos, types = {}, {}, set()
    for per, rows in dados.items():
        m = re.match(r'([A-Za-z]+) (\d{4})', per.strip())
        if not m or m.group(1).lower() not in EN_MON:
            continue
        k = '%s-%02d' % (m.group(2), EN_MON[m.group(1).lower()])
        for row in rows:
            v = num(row.get('valor'))
            gc = str(row.get('geocod') or '')
            t = str(row.get('dim_3_t') or 'Total')
            types.add(t)
            if v is None or not (gc == 'PT' or len(gc) == 2):
                continue
            geos[gc] = row.get('geodsg')
            out.setdefault(gc, {}).setdefault(t, {})[k] = v
    say('pt ine', len(dados), sorted(geos.items()), types)
    return {gc: {'n': geos[gc], 's': {t: srt(d) for t, d in v.items()}} for gc, v in out.items()}


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


# ---------------------------------------------------------------- Dubai Land Department (open data, transaction by transaction)
DLD_URL = 'https://gateway.dubailand.gov.ae/open-data/transactions'
DLD_FIRST = '2026-01'   # the open data answers only the current calendar year; older months stay in housing_ae.json as they are collected


def dld_window(d0, d1):
    body = json.dumps({'P_FROM_DATE': d0.strftime('%m/%d/%Y'), 'P_TO_DATE': d1.strftime('%m/%d/%Y'), 'P_GROUP_ID': '1', 'P_IS_OFFPLAN': '',
                       'P_IS_FREE_HOLD': '', 'P_AREA_ID': '', 'P_USAGE_ID': '', 'P_PROP_TYPE_ID': '', 'P_TAKE': '-1', 'P_SKIP': '',
                       'P_SORT': 'TRANSACTION_NUMBER_ASC'}).encode()
    last = None
    for a in range(3):
        try:
            req = urllib.request.Request(DLD_URL, data=body, headers={'User-Agent': UA, 'Content-Type': 'application/json', 'Accept': 'application/json',
                                                                     'Origin': 'https://dubailand.gov.ae', 'Referer': 'https://dubailand.gov.ae/'})
            j = json.loads(urllib.request.urlopen(req, timeout=120).read())
            return ((j.get('response') or {}).get('result')) or []
        except Exception as e:
            last = e
            time.sleep(4 * (a + 1))
    raise last


def med(v):
    v = sorted(v)
    n = len(v)
    return None if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


def dld_month(ym):
    """Residential sales in one month: median price per m² (all, flats, villas), count, off-plan share, by area."""
    y, m = int(ym[:4]), int(ym[5:7])
    start = dt.date(y, m, 1)
    end = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
    end = min(end, TODAY)
    vals = {'all': [], 'flat': [], 'villa': []}
    areas, off = {}, 0
    wins, d = [], start
    while d <= end:
        e = min(d + dt.timedelta(days=4), end)
        wins.append((d, e))
        d = e + dt.timedelta(days=1)
    with cf.ThreadPoolExecutor(4) as ex:
        rows = [r for part in ex.map(lambda w: dld_window(*w), wins) for r in part]
    if True:
        for r in rows:
            sub = (r.get('PROP_SB_TYPE_EN') or '').lower()
            kind = 'flat' if 'flat' in sub or 'apartment' in sub else 'villa' if 'villa' in sub or 'town' in sub else None
            if not kind:
                continue
            v, a = r.get('TRANS_VALUE') or 0, r.get('ACTUAL_AREA') or r.get('PROCEDURE_AREA') or 0
            if v < 100000 or a < 15:
                continue
            ppm = v / a
            if not 1500 <= ppm <= 150000:
                continue
            vals['all'].append(ppm)
            vals[kind].append(ppm)
            off += 1 if r.get('IS_OFFPLAN') == 1 else 0
            an = r.get('AREA_EN') or ''
            if an:
                x = areas.setdefault(an, [[], r.get('AREA_AR') or an])
                x[0].append(ppm)
    n = len(vals['all'])
    return {'n': n, 'off': round(off / n * 100, 1) if n else None, 'm': {k: round(med(v)) if len(v) >= 30 else None for k, v in vals.items()},
            'a': {k: [round(med(v[0])), len(v[0]), v[1]] for k, v in areas.items() if len(v[0]) >= 5}}


def dld_stats(prev):
    """Month table kept in housing_ae.json: each run redoes the last two months and fills older months a few at a time."""
    st = dict((prev or {}).get('dld') or {})
    cur = TODAY.strftime('%Y-%m')
    pm = (TODAY.replace(day=1) - dt.timedelta(days=1)).strftime('%Y-%m')
    todo = [cur] + ([pm] if TODAY.day <= 10 or pm not in st else [])
    y, m = int(DLD_FIRST[:4]), int(DLD_FIRST[5:7])
    missing = []
    while '%04d-%02d' % (y, m) < pm:
        k = '%04d-%02d' % (y, m)
        if k not in st:
            missing.append(k)
        m += 1
        if m > 12:
            y, m = y + 1, 1
    todo += missing[::-1][:14]          # newest gaps first
    t0, fails = time.time(), 0
    st = {k: v for k, v in st.items() if v.get('n')}
    for k in todo:
        if time.time() - t0 > 480:
            break
        try:
            x = dld_month(k)
            say('dld', k, x['n'], x['m'])
            if x['n']:
                st[k] = x
            elif k < pm:
                fails += 1          # an empty older month: the open data does not go back that far (or the gateway is limiting us)
                if fails >= 2:
                    break
        except Exception as e:
            say('dld', k, 'failed', str(e)[:100])
    return st


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
    dpp = b.get('dpp') or {}
    regions = []
    if cc == 'ae':
        try:
            prev = json.loads(get('https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/housing/housing_ae.json', tries=1))
        except Exception:
            prev = {}
        try:
            st = dld_stats(prev)
        except Exception as e:
            say('dld failed', str(e)[:120])
            st = (prev or {}).get('dld') or {}
        out['dld'] = st
        ks = sorted(k for k in st if st[k].get('n', 0) >= 300)
        if len(ks) >= 3:
            ser = lambda key: [[k, st[k]['m'][key]] for k in ks if st[k]['m'].get(key)]
            out.pop('idx', None)
            out['price'] = {'n': 'Dubai median sale price per m² (DLD)', 's': ser('all')}
            out['types'] = {'Apartments in Dubai, per m²': ser('flat'), 'Villas and townhouses in Dubai, per m²': ser('villa')}
            out['sales'] = [[k, st[k]['n']] for k in ks]
            out['offplan'] = [[k, st[k]['off']] for k in ks if st[k].get('off') is not None]
            names, hist = {}, {}
            for k in ks:
                for an, (v, n, ar) in st[k].get('a', {}).items():
                    names[an] = ar
                    hist.setdefault(an, []).append([k, v, n])
            last12 = ks[-12:]
            vol = {an: sum(n for k, v, n in h if k in last12) for an, h in hist.items()}
            for an in sorted(vol, key=lambda a: -vol[a])[:40]:
                if vol[an] < 150:
                    continue
                regions.append({'id': an, 'n': an.title(), 'n_ar': names[an], 'price': [[k, v] for k, v, n in hist[an] if n >= 10]})
            out['src'].insert(0, 'Dubai Land Department')
    if cc == 'ae' and dpp.get('country') and not out.get('price'):
        out['price'] = {'n': 'Average price per m², whole country (BIS)', 's': srt(dpp['country'])}
        out['types'] = {'Whole country, per m²': srt(dpp['country'])}
        if dpp.get('capital'):
            out['types']['Main financial centre, per m²'] = srt(dpp['capital'])
        if dpp.get('cities'):
            out['types']['Big cities, per m²'] = srt(dpp['cities'])
    if cc == 'sa' and dpp.get('country'):
        out['idx'] = {'n': 'Real estate price index (GASTAT via BIS)', 's': srt(dpp['country'])}
        if dpp.get('capital'):
            out['types'] = {'Whole country': srt(dpp['country']), 'Riyadh': srt(dpp['capital'])}
    if cc == 'es':
        for n, s in es_regions().items():
            if n != 'Nacional':
                regions.append({'id': n, 'n': n, 'idx': s})
        out['src'].insert(0, 'Instituto Nacional de Estadística (INE)')
    if cc == 'pt':
        try:
            pr = pt_regions()
            tot = lambda d: d.get('Total') or next(iter(d.values()))
            nat = pr.pop('PT', None)
            if nat:
                out['price'] = {'n': 'Median bank valuation per m²', 's': tot(nat['s'])}
                tt = {k: v for k, v in nat['s'].items() if k != 'Total'}
                if tt:
                    out['types'] = {('Apartments' if 'part' in k.lower() or 'flat' in k.lower() else 'Houses' if 'ouse' in k.lower() or 'orad' in k.lower() or 'villa' in k.lower() else k) + ', per m²': v for k, v in tt.items()}
            for gc, g in pr.items():
                regions.append({'id': gc, 'n': g['n'], 'price': tot(g['s'])})
            out['src'].insert(0, 'Statistics Portugal (INE)')
        except Exception as e:
            say('pt regions', str(e)[:120])
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
    if len(out['mkt'].get('index') or []) < 24 and cc in ('ae', 'sa'):
        # Yahoo has no history for the Dubai and Tadawul indexes: the iShares MSCI country fund instead (dollars; the
        # dirham and the riyal are pegged, so the percentage moves are the same in local money)
        try:
            alt = srt(yahoo_weekly({'ae': 'UAE', 'sa': 'KSA'}[cc]))
            if len(alt) > 24:
                out['mkt']['index'], out['mkt']['alt'] = alt, 'msci'
        except Exception as e:
            say(cc, 'msci fund', str(e)[:80])
    out['src'] += ['OECD', 'Yahoo Finance']
    return out


US_ST = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
         'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
         'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
         'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
         'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
         'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
         'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
         'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}


def us():
    """US in the shared schema, for the non-English sites. Built from housing.json, which housing.py writes earlier in the
    same job (FHFA, Freddie Mac, Zillow, Census ACS); the Fed policy rate comes from BIS."""
    path = os.path.join(OUTDIR, 'housing.json')
    H = json.load(open(path)) if os.path.exists(path) else json.loads(get('https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/housing/housing.json'))
    f, z = H.get('f') or {}, H.get('z') or {}
    mon = lambda s: [[k[:7], v] for k, v in s or []]

    def monthly(s):
        acc = {}
        for k, v in s or []:
            acc.setdefault(k[:7], []).append(v)
        return [[k, round(sum(v) / len(v), 3)] for k, v in sorted(acc.items())]
    out = {'code': 'us', 'name': 'United States', 'cur': 'USD', 'sym': '$', 'oecd_code': 'USA',
           'src': ['FHFA', 'Zillow', 'Freddie Mac', 'U.S. Census Bureau']}
    out['idx'] = {'n': 'House price index (FHFA)', 's': mon(f.get('HPI_SA') or f.get('HPI'))}
    zu = z.get('us') or {}
    if zu.get('all'):
        out['price'] = {'n': 'Typical home value (Zillow)', 's': zu['all']}
    ty = {}
    if zu.get('sfr'):
        ty['Single-family homes'] = zu['sfr']
    if zu.get('condo'):
        ty['Condos and apartments'] = zu['condo']
    if ty:
        out['types'] = ty
    if z.get('zori_us'):
        out['rent'] = {'n': 'Typical rent (Zillow)', 's': z['zori_us']}
    b = {}
    try:
        b = bis_load().get('US') or {}
    except Exception as e:
        say('us bis', e)
    out['rates'] = {'30-year fixed mortgage rate': monthly(f.get('MORTGAGE30US')), '15-year fixed mortgage rate': monthly(f.get('MORTGAGE15US')),
                    'Federal Reserve policy rate': srt(b.get('pol') or {})}
    if b.get('real'):
        out['bis_real'] = srt(b['real'])
    acs = H.get('acs') or {}
    regions = []
    for ab, s in (H.get('st') or {}).items():
        rs = [['%s-12' % y, v['rent']] for y, v in sorted((acs.get(ab) or {}).items()) if v.get('rent')]
        regions.append({'id': ab, 'n': US_ST.get(ab, s.get('n') or ab), 'price': s.get('all') or [], 'rent': rs})
    out['regions'] = regions
    out['mkt'] = market('^GSPC', None)
    out['src'] += ['Bank for International Settlements', 'OECD', 'Yahoo Finance']
    return out


COUNTRIES = {'us': us, 'gb': gb, 'ca': ca, 'ie': ie, 'au': au}
COUNTRIES.update({c: (lambda c=c: generic(c)) for c in GEN})


def main():
    only = sys.argv[1:] or list(COUNTRIES)
    try:
        oecd = oecd_all()
    except Exception as e:
        say('OECD FAILED', e)
        oecd = {}
    ok = 0
    if any(c in GEN or c == 'us' for c in only):
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
            # a source that timed out this run must not empty the page: keep the previous run's block
            try:
                prev = json.loads(get('https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/housing/housing_%s.json' % c, tries=2))
            except Exception:
                prev = {}
            for k in ('idx', 'price', 'rent', 'types', 'regions', 'mkt'):
                new, old_ = d.get(k), prev.get(k)
                empty = (not new) or (isinstance(new, dict) and 's' in new and not new['s']) or (k == 'mkt' and len((new or {}).get('index') or []) < 24)
                if empty and old_:
                    d[k] = old_
                    say(c, 'kept previous', k)
            for rk, rs in list((d.get('rates') or {}).items()):
                if not rs and (prev.get('rates') or {}).get(rk):
                    d['rates'][rk] = prev['rates'][rk]
                    say(c, 'kept previous rate', rk)
            for src in prev.get('src') or []:
                if src not in d.get('src', []) and any(k in d and d[k] == prev.get(k) for k in ('price', 'regions')):
                    d.setdefault('src', []).insert(0, src)
            d['oecd'] = oecd.get(d['oecd_code']) or {}
            if not d['oecd'] and prev.get('oecd'):
                d['oecd'] = prev['oecd']
                say(c, 'kept previous oecd')
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
