#!/usr/bin/env python3
"""One-off: which housing sources answer GitHub's runners (python housing_probe.py)."""
import io, time, urllib.request, zipfile
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
P = [
 'https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip',
 'https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/25171?nult=4',
 'https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/010567059',
 'https://www.genesis.destatis.de/genesisWS/rest/2020/data/tablefile?username=GAST&password=GAST&name=61262-0001&format=ffcsv',
 'https://api.statistiken.bundesbank.de/rest/data/BBK01/A.DE.N.ETW?format=csv',
 'https://api.statistiken.bundesbank.de/rest/dataflow/BBK',
 'https://esploradati.istat.it/SDMXWS/rest/data/150_929/A..',
 'https://sdmx.istat.it/SDMXWS/rest/data/150_929?startPeriod=2024',
 'https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0009490&lang=EN',
 'https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0904010000_101/px-x-0904010000_101.px',
 'https://data.snb.ch/api/cube/plkopr/data/csv/en',
 'https://downloads.fipe.org.br/indices/fipezap/fipezap-serieshistoricas.xlsx',
 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.25419/dados/ultimos/3?formato=json',
 'https://www.dubaipulse.gov.ae/',
 'https://query2.finance.yahoo.com/v8/finance/chart/%5ETASI.SR?range=5d&interval=1d',
 'https://query2.finance.yahoo.com/v8/finance/chart/DFMGI.AE?range=5d&interval=1d',
 'https://query2.finance.yahoo.com/v8/finance/chart/XU100.IS?range=5d&interval=1d',
 'https://query2.finance.yahoo.com/v8/finance/chart/PSI20.LS?range=5d&interval=1d',
 'https://query2.finance.yahoo.com/v8/finance/chart/FTSEMIB.MI?range=5d&interval=1d',
 'https://www.oenb.at/isawebstat/stabfrage/createReport?lang=EN&report=6.6',
 'https://www.reinfolib.mlit.go.jp/',
]
for u in P:
    t = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': '*/*'}), timeout=40)
        b = r.read()
        head = b[:400]
        if b[:2] == b'PK' and u.endswith('.zip'):
            z = zipfile.ZipFile(io.BytesIO(b)); n = z.namelist()[0]; head = (n + ' :: ').encode() + z.open(n).read(400)
        print('OK %3d %5.1fs %9d %s\n    %r' % (r.status, time.time() - t, len(b), u, head), flush=True)
    except Exception as e:
        print('XX       %5.1fs %s\n    %s' % (time.time() - t, u, str(e)[:200]), flush=True)
