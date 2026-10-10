#!/usr/bin/env python3
"""Checks that the DCF page (web/dcf.html, JavaScript) and dcf_model.py give identical values.
Usage: python test_dcf.py [blocks.json]   (needs node)"""
import json, os, re, subprocess, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dcf_model as M

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'dcf.html')).read()
js = src[src.index('var K_NEAR='):src.index('/* buy-and-hold')]
blocks = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
if not blocks:
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stocks')
    for f in sorted(os.listdir(d))[:3000]:
        r = json.load(open(os.path.join(d, f)))
        if r.get('dcf'):
            blocks[r['ticker']] = r['dcf']
random.seed(1)
cases = []
for t, b in list(blocks.items())[:1500]:
    for i in range(3):
        for N in (5, 10):
            for cash in (False, True):
                cases.append([t, M.bvals(b, cash), b['d'], i, N])
js_in = json.dumps([[c[1], c[2], c[3], c[4]] for c in cases])
prog = js + '''
var C = JSON.parse(require('fs').readFileSync(0, 'utf8'));
var out = C.map(function(c){var b=c[0],d=c[1],i=c[2],N=c[3],p=function(k){return d[k][i]/100};
  var v=value(b,N,p('g1'),p('g2'),p('pm'),p('fm'),d.pe[i],d.pf[i],p('ret'),p('sh'),p('tg'));
  return v?[v.fair,v.pe,v.pf,v.dcf]:null});
process.stdout.write(JSON.stringify(out));'''
res = json.loads(subprocess.run(['node', '-e', prog], input=js_in, capture_output=True, text=True, check=True).stdout)
bad = 0
for c, r in zip(cases, res):
    v = M.scen(c[1], c[2], c[3], c[4])
    py = [v['fair'], v['pe'], v['pf'], v['dcf']] if v else None
    if (py is None) != (r is None):
        bad += 1
        continue
    if py is None:
        continue
    for a, b in zip(py, r):
        if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-6 * max(1, abs(a))):
            bad += 1
            if bad < 5:
                print('MISMATCH', c[0], c[3], c[4], py, r)
            break
print('cases', len(cases), 'mismatches', bad)
sys.exit(1 if bad else 0)
