"""Independent multiples + freshness audit over data/stocks (daily site run, 26 Nov 2026).
Recomputes P/E = price / TTM EPS, P/S, P/FCF and dividend yield from the same file and flags disagreements,
stale prices and TTM periods older than 140 days. Usage: python3 tools/multiples_audit.py [stock-data dir]"""
import json,glob,os,collections,datetime as dt,sys
root=sys.argv[1] if len(sys.argv)>1 else '/home/claude/stock-data'
today=dt.date.today()
bad=collections.defaultdict(list); n=0; big=0
def rel(a,b): return abs(a-b)/abs(b) if b else 0
for f in glob.glob(root+'/data/stocks/*.json'):
    d=json.load(open(f)); t=d['ticker']; m=d.get('market') or {}; r=d.get('ratios') or {}; tt=d.get('ttm') or {}
    mc=m.get('mcap') or 0; p=m.get('price') or 0
    if mc<2e9 or not p: continue
    n+=1; big+= mc>=50e9
    # market date
    if m.get('as_of') and (today-dt.date.fromisoformat(m['as_of'][:10])).days>4: bad['price_old'].append(t)
    # ttm freshness
    end=tt.get('end')
    if end:
        age=(today-dt.date.fromisoformat(end[:10])).days
        if age>140: bad['ttm_old_%s'%('big' if mc>=10e9 else 'mid')].append((t,end))
    else: bad['no_ttm_end'].append(t)
    eps=tt.get('eps'); ni=tt.get('net_income')
    if r.get('pe') and eps and eps>0:
        if rel(r['pe'],p/eps)>0.03: bad['pe_vs_price_eps'].append((t,round(r['pe'],2),round(p/eps,2)))
    if r.get('pe') and ni and ni>0 and rel(r['pe'],mc/ni)>0.15: bad['pe_vs_mcap_ni'].append((t,round(r['pe'],1),round(mc/ni,1)))
    if r.get('ps') and tt.get('revenue') and rel(r['ps'],mc/tt['revenue'])>0.03: bad['ps'].append((t,round(r['ps'],2),round(mc/tt['revenue'],2)))
    if r.get('pfcf') and tt.get('fcf') and tt['fcf']>0 and rel(r['pfcf'],mc/tt['fcf'])>0.03: bad['pfcf'].append((t,round(r['pfcf'],1),round(mc/tt['fcf'],1)))
    if r.get('div_yield') and tt.get('dps') and rel(r['div_yield'],tt['dps']/p)>0.05: bad['div_yield'].append((t,round(r['div_yield'],4),round(tt['dps']/p,4)))
    if r.get('pe') and r['pe']>0 and r['pe']<3 and mc>=10e9: bad['pe_suspicious_low'].append((t,round(r['pe'],2)))
    if eps and ni and tt.get('shares_diluted') and rel(eps, ni/tt['shares_diluted'])>0.1: bad['eps_vs_ni_shares'].append((t,round(eps,2),round(ni/tt['shares_diluted'],2)))
print('checked',n,'stocks >= $2B (%d >= $50B)'%big)
for k,v in sorted(bad.items()):
    print('\n%s: %d'%(k,len(v))); print('  ',v[:25])
