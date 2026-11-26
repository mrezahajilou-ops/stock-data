#!/usr/bin/env python3
"""One-off: which international housing sources answer GitHub's runners (python housing_probe.py)."""
import io, sys, time, urllib.request, zipfile
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
P = [
 'https://publicdata.landregistry.gov.uk/market-trend-data/house-price-index-data/UK-HPI-full-file-2026-09.csv',
 'https://publicdata.landregistry.gov.uk/market-trend-data/house-price-index-data/UK-HPI-full-file-2026-08.csv',
 'https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7g7/mm23/data',
 'https://api.beta.ons.gov.uk/v1/datasets',
 'https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/2020&Dateto=now&SeriesCodes=IUMBV34,IUMBEDR&CSVF=TN&UsingCodes=Y',
 'https://www150.statcan.gc.ca/n1/tbl/csv/18100205-eng.zip',
 'https://www150.statcan.gc.ca/n1/tbl/csv/34100133-eng.zip',
 'https://www.bankofcanada.ca/valet/observations/V80691335/json?recent=3',
 'https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HPM09/JSON-stat/2.0/en',
 'https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HPM04/JSON-stat/2.0/en',
 'https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIQ02/JSON-stat/2.0/en',
 'https://data.api.abs.gov.au/rest/data/ABS,RES_DWELL_ST,1.0.0/all?startPeriod=2024-Q1&format=csvfilewithlabels',
 'https://data.api.abs.gov.au/rest/dataflow/ABS',
 'https://www.rba.gov.au/statistics/tables/csv/f5-data.csv',
 'https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/all?startPeriod=2024-Q1&format=csvfilewithlabels',
 'https://data.bis.org/static/bulk/WS_SPP_csv_flat.zip',
 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hpi_q?geo=DE&unit=I15_Q&purchase=TOTAL&sinceTimePeriod=2024-Q1',
 'https://api.statistiken.bundesbank.de/rest/data/BBK01/?format=csv',
 'https://data.snb.ch/api/cube/plimoinreq/data/csv/en',
 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/3?formato=json',
 'https://www.reit.or.jp/',
]
for u in P:
    t = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': '*/*'}), timeout=40)
        b = r.read()
        head = b[:250]
        if b[:2] == b'PK':
            z = zipfile.ZipFile(io.BytesIO(b)); n = z.namelist()[0]; head = (n + ' :: ').encode() + z.open(n).read(600)
        print('OK %3d %5.1fs %9d %s\n    %r' % (r.status, time.time() - t, len(b), u, head[:600]), flush=True)
    except Exception as e:
        print('XX       %5.1fs %s\n    %s' % (time.time() - t, u, str(e)[:200]), flush=True)
