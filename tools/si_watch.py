"""Fast 13F watcher for the super-investors page.

Runs every ~20 minutes. For every manager it asks SEC (one small JSON per manager) for the latest
13F-HR / 13F-HR/A filing and compares it with what the site currently shows (index.json on the
"superinvestors" branch). If anything is newer, it starts the full rebuild (superinvestors.yml).
Prints a short list of who filed. Exit code 0 always; writes NEW=1 to $GITHUB_OUTPUT when a rebuild
is needed.
"""
import importlib.util, json, os, sys, time, urllib.request

UA = {'User-Agent': os.environ.get('SEC_USER_AGENT', 'SahamAnaliz research contact@sahamanaliz.com')}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get(url, tries=4):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except Exception:
            time.sleep(1.5 + a * 2)
    return None


def main():
    spec = importlib.util.spec_from_file_location('si', os.path.join(ROOT, 'superinvestors.py'))
    si = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(si)
    try:
        idx = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'index.json'))
        shown = {m['id']: (m.get('period') or '', m.get('filed') or '') for m in idx['managers']}
    except Exception as e:
        print('no current index (%s) -> rebuild' % e)
        shown = {}
    new = []
    for m in si.MANAGERS:
        mid, ciks = m[0], m[1] if isinstance(m[1], (list, tuple)) else (m[1],)
        if mid not in shown:
            new.append((mid, 'not on site yet', ''))
            continue
        best = ('', '')
        for cik in ciks:
            b = get('https://data.sec.gov/submissions/CIK%010d.json' % cik)
            time.sleep(0.12)  # SEC asks for <= 10 requests/second
            if not b:
                continue
            r = json.loads(b)['filings']['recent']
            for i, f in enumerate(r['form']):
                if f in ('13F-HR', '13F-HR/A'):
                    cand = (r['reportDate'][i] or '', r['filingDate'][i] or '')
                    if cand > best:
                        best = cand
                    break  # newest first; first 13F is the latest one
        per, filed = shown[mid]
        if best[0] > per or (best[0] == per and best[1] > filed):
            new.append((mid, best[0], best[1]))
    for x in new:
        print('NEW 13F: %s period %s filed %s' % x)
    print('%d managers checked, %d with newer filings' % (len(si.MANAGERS), len(new)))
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        with open(out, 'a') as fh:
            fh.write('NEW=%d\n' % (1 if new else 0))
            fh.write('WHO=%s\n' % ', '.join(x[0] for x in new)[:900])


if __name__ == '__main__':
    main()
