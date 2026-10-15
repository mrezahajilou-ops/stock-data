#!/usr/bin/env python3
"""Generate web/compare.html, web/watchlist.html, web/calendar.html from one shared block
(the Shopify loader only executes inline scripts, so shared code is inlined into each page).
Run after editing:  python gen_web.py
Also keeps the tool navigation bar identical on every tool page (stock, screener, dcf too).
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, 'web')

TABS = [('stock', '/pages/stock', 'تحلیل سهم'), ('screener', '/pages/screener', 'غربالگر سهام'),
        ('dcf', '/pages/dcf', 'ماشین‌حساب DCF'), ('compare', '/pages/compare', 'مقایسه'),
        ('watchlist', '/pages/watchlist', 'واچ‌لیست'), ('calendar', '/pages/earnings', 'تقویم گزارش‌ها'), ('pulse', '/pages/pulse', 'نبض جامعه'), ('superinvestors', '/pages/superinvestors', 'سوپر سرمایه‌گذارها'),
        ('myportfolio', '/pages/my-portfolio', 'دفترچه سهام من'), ('calc', '/pages/return-calculator', 'ماشین‌حساب بازده'), ('portfolio', '/pages/portfolio', 'پورتفوی رضا')]


def nav(on):
    return '<div class="nav">' + ''.join('<a%s href="%s">%s</a>' % (' class="on"' if k == on else '', u, l) for k, u, l in TABS) + '</div>'


THEME = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_src", "theme.css"), encoding="utf-8").read()

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;800;900&display=swap');
#ID{--bg:#0b1726;--card:#13233a;--card2:#182c47;--line:#25405f;--ink:#eef3f9;--mut:#93a7bf;--ac:#4FA37A;--lime:#8FB07A;--red:#C8534F;--gold:#C9A961;
  font-family:'Vazirmatn',Tahoma,sans-serif;color:var(--ink);background:var(--bg);max-width:1500px;margin:0 auto;padding:16px 18px 36px;border-radius:22px;line-height:1.7;box-sizing:border-box}
#ID *{box-sizing:border-box;font-family:inherit}
#ID a{color:var(--ac)}
#ID .nav{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
#ID .nav a{padding:6px 14px;border-radius:999px;border:1px solid var(--line);color:var(--mut)!important;text-decoration:none!important;font-weight:800;font-size:14px}
#ID .nav a.on{background:var(--lime);color:#0b1726!important;border-color:var(--lime)}
#ID h1{font-size:26px;font-weight:900;margin:0 0 2px;color:#fff}
#ID h3{font-size:17px;font-weight:900;margin:0 0 10px;color:#fff}
#ID .sub{color:var(--mut);margin:0 0 14px;font-size:14.5px}
#ID .card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:14px}
#ID .mut{color:var(--mut)}
#ID .up{color:var(--ac)}#ID .dn{color:var(--red)}
#ID .tk{direction:ltr;unicode-bidi:isolate;font-weight:900;color:var(--ac)}
#ID .num{direction:ltr;unicode-bidi:isolate;white-space:nowrap}
#ID .btn{display:inline-block;background:var(--lime);color:#0b1726!important;font-weight:900;padding:9px 16px;border-radius:12px;text-decoration:none!important;border:0;cursor:pointer;font-size:14px}
#ID .btn.ghost{background:transparent;color:#fff!important;border:1.5px solid var(--line)}
#ID .btn.sm{padding:5px 10px;font-size:12.5px;border-radius:9px}
#ID input,#ID select{background:var(--bg);border:1.5px solid var(--line);border-radius:10px;color:#fff;font-size:15px;padding:8px 10px;outline:none}
#ID input:focus{border-color:var(--ac)}
#ID .search{position:relative}
#ID .sugg{position:absolute;top:100%;right:0;left:0;background:var(--card2);border:1px solid var(--line);border-radius:12px;margin-top:6px;z-index:20;max-height:280px;overflow:auto;display:none}
#ID .sugg div{padding:8px 12px;cursor:pointer;display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid var(--line)}
#ID .sugg div:hover{background:#21395a}
#ID .sugg b{direction:ltr;color:var(--ac)}
#ID .tw{overflow-x:auto;-webkit-overflow-scrolling:touch}
#ID table{border-collapse:collapse;width:100%;font-size:14px}
#rzq .grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}#rzq .pl{margin:0;padding:0 18px 0 0}#rzq .pl li{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid #1A1E26}
#rzq .vb{display:inline-block;width:70px;height:6px;border-radius:99px;background:rgba(200,83,79,.35);overflow:hidden;vertical-align:middle}#rzq .vb b{display:block;height:100%;background:#4FA37A}#rzq .ctm{font-size:11.5px;color:var(--ac);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:0 6px;margin-right:4px;white-space:nowrap}#rzq-contest .bw{width:34%}#rzq .cb{display:block;width:100%;min-width:90px;height:8px;border-radius:99px;background:var(--line);overflow:hidden}#rzq .cb b{display:block;height:100%;background:var(--ac);border-radius:99px}@media(max-width:640px){#rzq .hm{display:none}#rzq .tw td,#rzq .tw th{padding-left:5px;padding-right:5px}#rzq .vb{width:44px}#rzq .cb{min-width:40px;width:40px}#rzq-contest .bw{width:auto}#rzq-contest .tw table{width:100%}#rzq-contest td,#rzq-contest th{padding-left:5px;padding-right:5px;font-size:13.5px}}#rzq .chips{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#rzk table{table-layout:fixed}#rzk th:first-child,#rzk td:first-child{width:200px}
@media (max-width:760px){#rzk th:first-child,#rzk td:first-child{width:120px;white-space:normal}}
#ID th{color:var(--mut);font-size:12.5px;font-weight:800;padding:8px;border-bottom:1px solid var(--line);white-space:nowrap}
#ID td{padding:8px;border-bottom:1px solid #1c3150;white-space:nowrap}
#ID .sc{display:inline-block;min-width:34px;text-align:center;border-radius:8px;padding:1px 6px;color:#0b1726;font-weight:900;direction:ltr}
#ID .empty{color:var(--mut);text-align:center;padding:22px}
#ID .note{color:var(--mut);font-size:12px;margin-top:10px}
#ID .chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
#ID .chip{background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:3px 12px;font-size:13px;cursor:pointer;direction:ltr;color:var(--mut)}
#ID .chip:hover{color:#fff;border-color:var(--ac)}
""" + "\n" + THEME

# ---------------------------------------------------------------- anonymous usage events (events/worker.js)
EVENTS_URL = 'https://rz-events.mreza-hajilou.workers.dev'   # workers.dev URL after `events/deploy.sh`; empty = the beacon is a no-op
EVENTS_JS = (r"""
/* EVENTS:START */
window.RZ_EVENTS=window.RZ_EVENTS||'%s';
window.rzUid=function(){try{var u=localStorage.getItem('rz_uid');if(!u){u=Math.random().toString(36).slice(2,10)+Math.random().toString(36).slice(2,10);localStorage.setItem('rz_uid',u)}return u}catch(e){return ''}};
window.rzE=function(k,t,v){try{var U=window.RZ_EVENTS;if(!U||!t)return;var u=rzUid();if(!u)return;var b=JSON.stringify({k:k,t:String(t).toUpperCase(),v:v||'',u:u});
  if(navigator.sendBeacon)navigator.sendBeacon(U+'/e',new Blob([b],{type:'text/plain'}));else fetch(U+'/e',{method:'POST',body:b,keepalive:true,mode:'cors'}).catch(function(){})}catch(e){}};
window.rzContest=function(){if(window._rzC)return window._rzC;var P=location.hostname.indexOf('rezahajiloubooks')>=0||location.hostname.indexOf('myshopify')>=0;
  var gj=function(h,id){try{var el=new DOMParser().parseFromString(h,'text/html').getElementById(id);return el?JSON.parse(el.textContent):null}catch(e){return null}};
  var tx=function(u){return fetch(u,{credentials:'same-origin'}).then(function(r){return r.ok?r.text():''})};
  var U='/blogs/contest-entries/picks?view=contest&page=',TRE=/^[A-Z][A-Z0-9.\-]{0,8}$/,DL=Date.parse('2026-10-29T22:59:59Z');
  window._rzC=(!P?Promise.resolve(null):Promise.all([tx(U+1).then(function(h){var j=gj(h,'rzk-c');if(!j)return [];var all=j.c||[],n=parseInt(j.p,10)||1,ps=[];for(var i=2;i<=n&&i<=40;i++)ps.push(tx(U+i).then(function(h){var k=gj(h,'rzk-c');return k&&k.c?k.c:[]}));return Promise.all(ps).then(function(L){L.forEach(function(x){all=all.concat(x)});return all})}).catch(function(){return []}),
    tx('/pages/contest-data').then(function(h){return gj(h,'rzk-data')||{}}).catch(function(){return {}})]).then(function(R){var X=R[1]||{},ex={};(X.x||[]).forEach(function(n){ex[String(n).toLowerCase()]=1});
    var raw=R[0].map(function(c){var m=String(c.b||'').split('|');return {n:String(c.a||'').trim().slice(0,24),t:String(m[0]||'').trim().toUpperCase(),p:parseFloat(m[1]),ts:(+c.t)*1000,h:String(c.h||'')}}).concat((X.e||[]).map(function(e){return {n:String(e.n||''),t:String(e.t||'').toUpperCase(),p:+e.p,ts:Date.parse(e.ts),h:String(e.h||'')}}));
    raw=raw.filter(function(e){return e.n.length>=2&&TRE.test(e.t)&&isFinite(e.p)&&e.p>=-100&&e.p<=1000&&!(e.ts>DL+120000)&&!ex[e.n.toLowerCase()]&&!(e.h&&ex[e.h])}).sort(function(a,b){return a.ts-b.ts});
    var sh={},sn={},E=raw.filter(function(e){var k=e.n.toLowerCase();if(sn[k]||(e.h&&sh[e.h]))return false;sn[k]=1;if(e.h)sh[e.h]=1;return true});
    if(!E.length)return null;var by={};E.forEach(function(e){var b=by[e.t]||(by[e.t]={t:e.t,n:0,sum:0});b.n++;b.sum+=e.p});
    var L=Object.keys(by).map(function(t){var b=by[t];b.avg=b.sum/b.n;return b}).sort(function(a,b){return b.n-a.n||a.avg-b.avg});
    return {entries:E,by:by,list:L,total:E.length}}).catch(function(){return null}));return window._rzC};
/* EVENTS:END */
""" % EVENTS_URL)

JS = r"""
var API=window.RZS_API||'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/main/data';
var RAW='https://raw.githubusercontent.com/mrezahajilou-ops/stock-data';
var $=function(i){return document.getElementById(i)};
function esc(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function big(v){if(v==null||!isFinite(v))return '—';var a=Math.abs(v),s=v<0?'-':'';if(a>=1e12)return s+'$'+(a/1e12).toFixed(2)+'T';if(a>=1e9)return s+'$'+(a/1e9).toFixed(1)+'B';if(a>=1e6)return s+'$'+(a/1e6).toFixed(0)+'M';return s+'$'+a.toFixed(0)}
function pct(v,d){if(v==null||!isFinite(v))return '—';if(Math.abs(v)>10)return 'n/m';return (v*100).toFixed(d==null?1:d)+'%'}
function x1(v){return v==null||!isFinite(v)?'—':v.toFixed(1)}
function scol(v){return v>=4?'#4FA37A':v>=3?'#8FB07A':v>=2?'#C9A961':'#C8534F'}
function sc(v){return v==null?'—':'<span class="sc" style="background:'+scol(v)+'">'+(Math.round(v*10)/10)+'</span>'}
/* live quotes */
var RZQ=null,RZQ_P=null,RZQ_ST={'Open':'قیمت لحظه‌ای','Pre Market':'پیش‌بازار','After Hours':'پس از بسته‌شدن بازار','Closed':'قیمت پایانی'};
function liveQuotes(){if(!RZQ_P){var p=fetch(RAW+'/quotes/quotes.json?v='+Math.floor(Date.now()/120000)).then(function(r){return r.ok?r.json():null}).then(function(j){RZQ=j&&j.q?j:null;return RZQ}).catch(function(){return null});
  RZQ_P=Promise.race([p,new Promise(function(res){setTimeout(function(){res(null)},3500)})]);p.then(function(){RZQ_P=Promise.resolve(RZQ)})}return RZQ_P}
function liveWhen(iso){try{var d=new Date(iso);if(isNaN(d))return '';return d.toLocaleString('fa-IR-u-ca-gregory',{timeZone:'America/New_York',day:'numeric',month:'long',hour:'2-digit',minute:'2-digit',hour12:false})+' به وقت نیویورک'}catch(e){return ''}}
/* compact screener rows (+ browser cache), rescaled to live prices */
function decodeMin(m){var cols=m.cols,D=m.dict||{},S=m.scale||{},idx=cols.map(function(c){return D[c]?['d',D[c]]:S[c]?['s',S[c]]:null});
  return {cols:cols,as_of:m.as_of,rows:m.rows.map(function(r){return r.map(function(v,i){var x=idx[i];if(!x||v==null)return v;return x[0]==='d'?x[1][v]:v*x[1]})})}}
function loadScreener(){var full=function(){return fetch(API+'/screener.json').then(function(r){return r.json()})};
  return fetch(API+'/meta.json?v='+Math.floor(Date.now()/600000)).then(function(r){return r.json()}).catch(function(){return {}}).then(function(meta){var key=meta&&meta.built||'';
    try{var c=JSON.parse(localStorage.getItem('rzc2_data')||'null');if(c&&key&&c.k===key&&c.m)return decodeMin(c.m)}catch(e){}
    return fetch(API+'/screener.min.json?v='+encodeURIComponent(key)).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(m){try{localStorage.removeItem('rzc2_data');if(key)localStorage.setItem('rzc2_data',JSON.stringify({k:key,m:m}))}catch(e){}return decodeMin(m)}).catch(full)}).catch(full)}
var C={},ROWS=[],BY={},SPE={};
function liveRow(r){var I=function(k){return C[k]},Q=RZQ&&RZQ.q[r[I('t')]],p0=r[I('price')];if(!Q||!(Q[0]>0)||!p0)return;var f=Q[0]/p0;
  var o={pe:r[I('pe')],pf:r[I('pfcf')],pg:r[I('peg')],fu:r[I('fair_up')],sv:r[I('s_value')]};
  r[I('price')]=Q[0];r.chg=Q[1];if(r[I('mcap')]!=null)r[I('mcap')]*=f;
  ['pe','pfcf','ps','pb','peg','fwd_pe','fwd_ps','fwd_pfcf'].forEach(function(k){if(I(k)!=null&&r[I(k)]!=null)r[I(k)]*=f});
  ['divy','fcf_yield','shy'].forEach(function(k){if(I(k)!=null&&r[I(k)]!=null)r[I(k)]/=f});
  if(r[I('ev_ebitda')]!=null){var nd=r[I('nd_ebitda')];r[I('ev_ebitda')]=nd!=null?(r[I('ev_ebitda')]-nd)*f+nd:r[I('ev_ebitda')]*f}
  if(r[I('fair_up')]!=null)r[I('fair_up')]=(1+r[I('fair_up')])/f-1;
  if(o.sv!=null){var c4=function(pe,pf,pg,fu){return (pe!=null&&pe<25?1:0)+(pf!=null&&pf<20?1:0)+(fu!=null&&fu>0?1:0)+(pg!=null&&pg<1.5?1:0)},spe=SPE[r[I('sector')]];
    var cs=Math.max(0,Math.min(1,o.sv-c4(o.pe,o.pf,o.pg,o.fu))),pe=r[I('pe')];if(spe!=null&&pe!=null&&o.pe!=null&&((o.pe<spe)!==(pe<spe)))cs=pe<spe?1:0;
    r[I('s_value')]=c4(pe,r[I('pfcf')],r[I('peg')],r[I('fair_up')])+cs;
    var parts=['s_value','s_future','s_past','s_health','s_capital'].map(function(k){return r[I(k)]}).filter(function(x){return x!=null});if(parts.length)r[I('s_total')]=Math.round(parts.reduce(function(a,b){return a+b},0)/parts.length*10)/10}}
function loadAll(){return Promise.all([loadScreener(),liveQuotes(),fetch(API+'/sectors.json').then(function(r){return r.ok?r.json():{}}).catch(function(){return {}})]).then(function(x){
  var j=x[0];j.cols.forEach(function(c,i){C[c]=i});Object.keys(x[2]||{}).forEach(function(k){if(x[2][k]&&x[2][k].pe)SPE[k]=x[2][k].pe});
  ROWS=j.rows;ROWS.forEach(function(r){liveRow(r);BY[r[C.t]]=r});return j})}
function g(r,k){return r&&C[k]!=null?r[C[k]]:null}
/* ticker search box */
function picker(inp,box,onPick){inp.addEventListener('input',function(){var q=inp.value.trim().toUpperCase();if(!q){box.style.display='none';return}
  var res=ROWS.filter(function(r){return r[C.t].indexOf(q)===0}).slice(0,6).concat(ROWS.filter(function(r){return r[C.t].indexOf(q)!==0&&String(r[C.n]).toUpperCase().indexOf(q)>=0}).slice(0,4));
  box.innerHTML=res.map(function(r){return '<div data-t="'+esc(r[C.t])+'"><span>'+esc(r[C.n])+'</span><b>'+esc(r[C.t])+'</b></div>'}).join('');box.style.display=res.length?'block':'none'});
  box.addEventListener('click',function(e){var d=e.target.closest('div[data-t]');if(!d)return;box.style.display='none';inp.value='';onPick(d.dataset.t)});
  inp.addEventListener('keydown',function(e){if(e.key==='Enter'){var t=inp.value.trim().toUpperCase();if(BY[t]){box.style.display='none';inp.value='';onPick(t)}}})}
/* watchlist storage (this device) */
function wlGet(){try{return JSON.parse(localStorage.getItem('rz_watch')||'[]')}catch(e){return []}}
function wlSet(a){try{localStorage.setItem('rz_watch',JSON.stringify(a))}catch(e){}}
function alGet(){try{return JSON.parse(localStorage.getItem('rz_alerts')||'{}')}catch(e){return {}}}
function alSet(o){try{localStorage.setItem('rz_alerts',JSON.stringify(o))}catch(e){}}
"""


# ---------------------------------------------------------------- community pulse (events worker aggregates)
PULSE_BODY = r"""
<div class="card" id="rzq-head"><div class="chips"><span class="chip on" data-d="7">۷ روز</span><span class="chip" data-d="30">۳۰ روز</span><span class="mut" id="rzq-asof" style="font-size:13px;margin-right:auto"></span></div></div>
<div id="rzq-main"><div class="card empty">در حال بارگذاری…</div></div>
<p class="note">این آمار از رفتار بازدیدکننده‌های همین سایت ساخته میشه (بدون نام، ایمیل یا آی‌پی)؛ فقط یک شناسه‌ی تصادفی در مرورگر تا هر نفر یک بار شمرده بشه. سهمی که کمتر از ۳ نفر دیده باشن نشون داده نمیشه. آموزشی است و توصیه‌ی خرید یا فروش نیست.</p>
"""
PULSE_JS = r"""
var DAYS=7,ST=null,CT=null;
function faN(n){return Number(n).toLocaleString('fa-IR')}
rzContest().then(function(c){CT=c;draw()});
function arrow(c,p,ct){if(ct&&c-ct<3)return '';if(!p)return '<span class="mut" style="font-size:12px">جدید</span>';var d=c/p-1;if(Math.abs(d)<0.1)return '<span class="mut">≈</span>';return '<span class="'+(d>0?'up':'dn')+'" style="font-size:12.5px">'+(d>0?'▲':'▼')+' '+Math.round(Math.abs(d)*100)+'%</span>'}
function row(x,i){var r=BY[x.t]||null,n=r?String(g(r,'n')).slice(0,28):'',tot=x.bull+x.bear,pb=tot?Math.round(x.bull/tot*100):null,net=x.watch_add-x.watch_remove;
  return '<tr><td class="num mut">'+(i+1)+'</td><td><a class="tk" href="/pages/stock#'+esc(x.t)+'">'+esc(x.t)+'</a> <bdi dir="ltr" class="mut hm" style="font-size:12.5px">'+esc(n)+'</bdi>'+(x.ct?' <a href="/pages/contest" class="ctm" title="'+x.ct+' نفر در مسابقه‌ی نوامبر این سهم رو انتخاب کردن (میانگین پیش‌بینی '+(x.avg>=0?'+':'')+x.avg.toFixed(1)+'٪)">🏆'+x.ct+'</a>':'')+'</td>'+
    '<td class="num"><b>'+x.uniq+'</b> <span class="mut" style="font-size:12px">نفر</span> '+arrow(x.uniq,x.prev_uniq,x.ct)+'</td>'+
    '<td class="num '+(net>0?'up':net<0?'dn':'mut')+'">'+(net>0?'+':'')+net+'</td>'+
    '<td>'+(tot>=5?'<span class="vb"><b style="width:'+pb+'%"></b></span> <span class="num" style="font-size:12.5px">'+pb+'٪</span>':'<span class="mut" style="font-size:12px">—</span>')+'</td>'+
    '<td class="hm" style="text-align:center">'+(r?sc(g(r,'s_total')):'—')+'</td><td class="hm num">'+(r&&g(r,'pe')?x1(g(r,'pe')):'—')+'</td>'+
    (x.pw?'<td class="hm mut num" style="font-size:12px">'+x.pw+'</td>':'<td class="hm"></td>')+'</tr>'}
function merged(){var S=ST?JSON.parse(JSON.stringify(ST)):{as_of:'',days:DAYS,totals:{events:0,uniq:0,tickers:0},top:[],searches:[],compares:[],watch_in:[],watch_out:[]};if(!CT)return S;
  var by={},sb={},wb={};S.top.forEach(function(r){by[r.t]=r});S.searches.forEach(function(r){sb[r.t]=r});S.watch_in.forEach(function(r){wb[r.t]=r});
  CT.list.forEach(function(c){var r=by[c.t]||(by[c.t]={t:c.t,views:0,uniq:0,prev_uniq:0,pw:0,watch_add:0,watch_remove:0,bull:0,bear:0});r.uniq+=c.n;r.views+=c.n;r.prev_uniq+=c.n;r.ct=c.n;r.avg=c.avg;
    var q=sb[c.t]||(sb[c.t]={t:c.t,n:0});q.n+=c.n});
  S.top=Object.keys(by).map(function(t){return by[t]}).sort(function(a,b){return b.uniq-a.uniq||b.views-a.views}).map(function(r,i){r.rank=i+1;return r});
  S.searches=Object.keys(sb).map(function(t){return sb[t]}).sort(function(a,b){return b.n-a.n});
  S.watch_in=Object.keys(wb).map(function(t){return wb[t]}).filter(function(r){return r.net>0}).sort(function(a,b){return b.net-a.net});
  var T=S.totals||{};S.totals={events:(T.events||0)+CT.total,uniq:(T.uniq||0)+CT.total,tickers:Object.keys(by).length};S._ct=1;return S}
function draw(){var box=$('rzq-main');var S=merged();if(!ST&&!CT){box.innerHTML='<div class="card empty">'+(window.RZ_EVENTS?'آمار بازدید هنوز در حال جمع شدنه؛ چند روز دیگه سر بزن.':'جمع‌آوری آمار هنوز فعال نشده.')+'</div>';return}
  var ST0=ST;ST=S;try{draw2()}finally{ST=ST0}}
function draw2(){var box=$('rzq-main');
  var h='';
  h+='<div class="card"><h3>پربازدیدترین سهم‌ها در '+(DAYS===7?'۷ روز':'۳۰ روز')+' گذشته</h3>'+(ST.top.length?'<div class="tw"><table><thead><tr><th></th><th style="text-align:right">سهم</th><th>بازدیدکننده</th><th>واچ‌لیست ±</th><th>خوش‌بین‌ها</th><th class="hm">امتیاز ما</th><th class="hm">P/E</th><th class="hm" title="بازدیدهایی که به دیوار اشتراک خوردن">🔒</th></tr></thead><tbody>'+ST.top.slice(0,30).map(row).join('')+'</tbody></table></div>':'<p class="mut">هنوز سهمی به حد نصاب ۳ بازدیدکننده نرسیده.</p>')+'</div>';
  if(!ST.searches.length&&!ST.watch_in.length&&!ST.watch_out.length&&!ST.compares.length){var t0=ST.totals||{};h+='<p class="note">جستجوها، ورود و خروج از واچ‌لیست‌ها و مقایسه‌های محبوب هم به‌زودی اینجا اضافه میشن (هر بخش بعد از رسیدن به حد نصاب ۳ نفر). تا حالا '+(t0.uniq||0)+' بازدیدکننده‌ی یکتا و '+(t0.tickers||0)+' سهم مختلف ثبت شده.</p>';h+=ctNote();box.innerHTML=h;return}
  var two='<div class="grid2">';
  two+='<div class="card"><h3>بیشترین جستجو</h3>'+(ST.searches.length?'<ol class="pl">'+ST.searches.slice(0,12).map(function(x){return '<li><a class="tk" href="/pages/stock#'+esc(x.t)+'">'+esc(x.t)+'</a><span class="num mut">'+x.n+' نفر</span></li>'}).join('')+'</ol>':'<p class="mut">—</p>')+'</div>';
  two+='<div class="card"><h3>ورود به واچ‌لیست‌ها</h3>'+(ST.watch_in.length?'<ol class="pl">'+ST.watch_in.slice(0,8).map(function(x){return '<li><a class="tk" href="/pages/stock#'+esc(x.t)+'">'+esc(x.t)+'</a><span class="num up">+'+x.net+'</span></li>'}).join('')+'</ol>':'<p class="mut">—</p>')+
    (ST.watch_out.length?'<h3 style="margin-top:12px">خروج از واچ‌لیست‌ها</h3><ol class="pl">'+ST.watch_out.slice(0,6).map(function(x){return '<li><a class="tk" href="/pages/stock#'+esc(x.t)+'">'+esc(x.t)+'</a><span class="num dn">'+x.net+'</span></li>'}).join('')+'</ol>':'')+'</div>';
  two+='<div class="card"><h3>مقایسه‌های محبوب</h3>'+(ST.compares.length?'<ol class="pl">'+ST.compares.slice(0,10).map(function(x){return '<li><a class="tk" href="/pages/compare#'+esc(x.pair)+'">'+esc(x.pair.replace(/,/g,' vs '))+'</a><span class="num mut">'+x.n+'</span></li>'}).join('')+'</ol>':'<p class="mut">—</p>')+'</div>';
  two+='</div>';
  var t=ST.totals||{};
  h+=two+'<p class="note">در این بازه '+(t.uniq||0)+' بازدیدکننده‌ی یکتا، '+(t.tickers||0)+' سهم مختلف را دیده‌اند.</p>';
  h+=ctNote();box.innerHTML=h}
function ctNote(){return (CT&&ST&&ST._ct)?'<p class="note">🏆 انتخاب‌های '+faN(CT.total)+' شرکت‌کننده‌ی <a href="/pages/contest">مسابقه‌ی سهام برتر نوامبر</a> هم در این آمار حساب شده (هر انتخاب = یک بازدیدکننده و یک جستجو؛ واچ‌لیست و رأی‌ها فقط از رفتار واقعی کاربران).</p>':''}
function load(){if(!window.RZ_EVENTS){ST=null;draw();return}fetch(RZ_EVENTS+'/stats?days='+DAYS).then(function(r){return r.ok?r.json():null}).then(function(j){ST=j&&j.top?j:null;if(j&&j.as_of)$('rzq-asof').textContent='به‌روزرسانی: '+liveWhen(j.as_of.replace('Z',':00Z'));draw()}).catch(function(){ST=null;draw()})}
document.addEventListener('click',function(e){var c=e.target.closest('#rzq-head .chip');if(c){DAYS=+c.dataset.d;[].forEach.call(document.querySelectorAll('#rzq-head .chip'),function(x){x.classList.toggle('on',x===c)});load()}});
loadAll().then(load).catch(load);
"""

def page(pid, rid, title, sub, body, js):
    return ('<div id="%s" dir="rtl">\n<style>%s</style>\n%s\n<h1>%s</h1>\n<p class="sub">%s</p>\n%s\n'
            '<script>\n(function(){\n%s\n%s\n})();\n</script>\n</div>\n') % (
        rid, CSS.replace('#ID', '#' + rid), nav(pid), title, sub, body, EVENTS_JS + JS, js)


# ---------------------------------------------------------------- compare
COMPARE_BODY = r"""
<div class="card"><div class="search"><input id="rzk-q" placeholder="نماد یا اسم شرکت رو بنویس و اضافه کن (تا ۴ سهم)…" autocomplete="off" style="width:100%"><div class="sugg" id="rzk-s"></div></div>
<div class="chips" id="rzk-ch"></div>
<div class="chips"><span class="mut" style="font-size:13px">مقایسه‌های محبوب:</span><span class="chip" data-p="AAPL,MSFT">AAPL vs MSFT</span><span class="chip" data-p="NVDA,AMD">NVDA vs AMD</span><span class="chip" data-p="GOOGL,META">GOOGL vs META</span><span class="chip" data-p="KO,PEP">KO vs PEP</span><span class="chip" data-p="V,MA">V vs MA</span><span class="chip" data-p="AMZN,MELI,SE">AMZN vs MELI vs SE</span></div></div>
<div id="rzk-main"><div class="card empty">در حال بارگذاری…</div></div>
<p class="note">قیمت‌ها حدود ۱۵ تا ۳۰ دقیقه تأخیر دارن و نسبت‌ها با قیمت فعلی دوباره حساب میشن. سبز = بهترین مقدار در هر ردیف. ابزار آموزشیه و پیشنهاد خرید یا فروش نیست.</p>
"""
COMPARE_JS = r"""
var SEL=[];
var ROWDEF=[['امتیازها',[['s_total','امتیاز کلی',1,'sc'],['s_value','ارزش',1,'sc'],['s_future','آینده',1,'sc'],['s_past','گذشته',1,'sc'],['s_health','سلامت مالی',1,'sc'],['s_capital','بازگشت سرمایه',1,'sc']]],
 ['قیمت و ارزش‌گذاری',[['price','قیمت',0,'px'],['mcap','ارزش بازار',0,'big'],['pe','P/E',-1,'x'],['fwd_pe','P/E آینده',-1,'x'],['fwd_ps','P/S آینده',-1,'x'],['tgt_up','تا هدف تحلیلگرها',1,'pct'],['pfcf','P/FCF',-1,'x'],['ps','P/S',-1,'x'],['pb','P/B',-1,'x'],['ev_ebitda','EV/EBITDA',-1,'x'],['peg','PEG',-1,'x'],['fair_up','فاصله تا ارزش ذاتی',1,'pct'],['fcf_yield','بازده جریان نقد آزاد',1,'pct']]],
 ['رشد',[['revg1','رشد درآمد ۱ ساله',1,'pct'],['revg3','رشد درآمد ۳ ساله',1,'pct'],['revg5','رشد درآمد ۵ ساله',1,'pct'],['epsg5','رشد EPS ۵ ساله',1,'pct'],['fcfg3','رشد FCF ۳ ساله',1,'pct']]],
 ['کیفیت و سودآوری',[['gm','حاشیه ناخالص',1,'pct'],['om','حاشیه عملیاتی',1,'pct'],['nm','حاشیه خالص',1,'pct'],['fm','حاشیه FCF',1,'pct'],['roic','ROIC',1,'pct'],['roe','ROE',1,'pct']]],
 ['سلامت مالی',[['de','بدهی / حقوق صاحبان سهام',-1,'x'],['nd_ebitda','بدهی خالص / EBITDA',-1,'x'],['int_cov','پوشش بهره',1,'x']]],
 ['بازگشت به سهامدار',[['divy','بازده سود نقدی',1,'pct'],['shy','بازده کل سهامدار',1,'pct'],['sh_chg3','تغییر تعداد سهام ۳ ساله',-1,'pct'],['div_yrs','سال‌های سود نقدی',1,'n']]]];
function fmt(v,f,r){if(v==null||!isFinite(v))return '—';if(f==='sc')return sc(v);if(f==='px')return '<span class="num">$'+v.toFixed(2)+'</span>'+(r&&r.chg!=null?' <small class="'+(r.chg>=0?'up':'dn')+'">'+(r.chg>=0?'+':'')+r.chg.toFixed(2)+'%</small>':'');
  if(f==='big')return '<span class="num">'+big(v)+'</span>';if(f==='pct')return '<span class="num">'+pct(v)+'</span>';if(f==='n')return v;return '<span class="num">'+x1(v)+'</span>'}
function sync(){try{history.replaceState(null,'','#'+SEL.join(','))}catch(e){}if(SEL.length>=2)rzE('compare',SEL[0],SEL.slice().sort().join(',').slice(0,24));
  $('rzk-ch').innerHTML=SEL.map(function(t){return '<span class="chip" data-x="'+t+'">✕ '+t+'</span>'}).join('');draw()}
function add(t){t=t.toUpperCase();if(!BY[t]||SEL.indexOf(t)>=0)return;if(SEL.length>=4)SEL.shift();SEL.push(t);sync()}
function draw(){var m=$('rzk-main');if(!SEL.length){m.innerHTML='<div class="card empty">دو تا چهار سهم انتخاب کن تا کنار هم مقایسه بشن.</div>';return}
  var rs=SEL.map(function(t){return BY[t]});
  var h='<div class="card"><div class="tw"><table><thead><tr><th style="text-align:right">معیار</th>'+rs.map(function(r){return '<th><a class="tk" href="/pages/stocks/'+esc(g(r,'t').toLowerCase())+'">'+esc(g(r,'t'))+'</a><div class="mut" style="font-weight:600;max-width:160px;white-space:normal">'+esc(g(r,'n'))+'</div></th>'}).join('')+'</tr></thead><tbody>';
  ROWDEF.forEach(function(G){h+='<tr><td colspan="'+(rs.length+1)+'" style="color:#fff;font-weight:900;padding-top:16px">'+G[0]+'</td></tr>';
    G[1].forEach(function(R){var vals=rs.map(function(r){return g(r,R[0])}),best=null;
      if(R[2]&&rs.length>1){var ok=vals.filter(function(v){return v!=null&&isFinite(v)});if(ok.length>1){best=R[2]>0?Math.max.apply(null,ok):Math.min.apply(null,ok);if(R[0]==='pe'||R[0]==='fwd_pe'||R[0]==='fwd_ps'||R[0]==='pfcf'||R[0]==='ps'||R[0]==='pb'||R[0]==='ev_ebitda'||R[0]==='peg'){var pos=ok.filter(function(v){return v>0});best=pos.length?Math.min.apply(null,pos):null}}}
      h+='<tr><td>'+R[1]+'</td>'+vals.map(function(v,i){var w=best!=null&&v===best;return '<td style="text-align:center'+(w?';background:rgba(46,196,182,.14)':'')+'">'+fmt(v,R[3],rs[i])+'</td>'}).join('')+'</tr>'})});
  h+='</tbody></table></div><div class="chips">'+SEL.map(function(t){return '<a class="btn ghost sm" href="/pages/stock#'+t+'">تحلیل کامل '+t+'</a>'}).join('')+'</div></div>';
  var tots=rs.map(function(r){return [g(r,'t'),g(r,'s_total')]}).filter(function(x){return x[1]!=null}).sort(function(a,b){return b[1]-a[1]});
  if(tots.length>1)h+='<div class="card"><h3>جمع‌بندی</h3><p style="margin:0">در امتیاز کلی <b class="tk">'+tots[0][0]+'</b> با '+tots[0][1]+' از ۵ جلوتره'+(tots[1]?' و <b class="tk">'+tots[1][0]+'</b> با '+tots[1][1]+' بعدیه':'')+'. امتیاز بالاتر یعنی معیارهای بیشتری رو پاس کرده، نه اینکه حتماً خرید بهتریه؛ ردیف‌های بالا رو با هم ببین.</p></div>';
  m.innerHTML=h}
document.addEventListener('click',function(e){var c=e.target.closest('#rzk .chip');if(!c)return;if(c.dataset.x){SEL=SEL.filter(function(t){return t!==c.dataset.x});sync()}else if(c.dataset.p){SEL=[];c.dataset.p.split(',').forEach(add);sync()}});
loadAll().then(function(){picker($('rzk-q'),$('rzk-s'),add);var h=decodeURIComponent((location.hash||'').slice(1));(h?h.split(','):['AAPL','MSFT']).forEach(add);sync()})
  .catch(function(){$('rzk-main').innerHTML='<div class="card empty">بارگذاری داده‌ها ناموفق بود؛ صفحه رو دوباره باز کن.</div>'});
"""

# ---------------------------------------------------------------- watchlist
WATCH_BODY = r"""
<div class="card"><div class="search"><input id="rzw-q" placeholder="نماد یا اسم شرکت رو بنویس تا به واچ‌لیست اضافه بشه…" autocomplete="off" style="width:100%"><div class="sugg" id="rzw-s"></div></div>
<div class="note" style="margin-top:8px">واچ‌لیست و هشدارها روی همین دستگاه ذخیره میشن. هر بار که سایت رو باز کنی، هشدارهایی که فعال شدن بالای صفحه نشون داده میشن؛ اگه اجازه‌ی اعلان بدی، وقتی صفحه باز باشه اعلان هم می‌گیری.</div>
<div id="rzw-perm"></div></div>
<div id="rzw-hit"></div>
<div id="rzw-main"><div class="card empty">در حال بارگذاری…</div></div>
<div class="card" id="rzw-dlg" style="display:none"></div>
<p class="note">قیمت‌ها هر ۱۵ دقیقه در ساعات بازار آمریکا به‌روز میشن (حدود ۱۵ تا ۳۰ دقیقه تأخیر). ابزار آموزشیه و پیشنهاد خرید یا فروش نیست.</p>
"""
WATCH_JS = r"""
var CAL=null;
function nextEarn(t){if(!CAL)return null;var today=new Date().toISOString().slice(0,10),ds=Object.keys(CAL.days).sort();for(var i=0;i<ds.length;i++){if(ds[i]<today)continue;var e=CAL.days[ds[i]].filter(function(x){return x.t===t})[0];if(e)return {d:ds[i],e:e}}return null}
function hits(){var A=alGet(),out=[];Object.keys(A).forEach(function(t){var a=A[t],r=BY[t];if(!r)return;var p=g(r,'price'),fu=g(r,'fair_up');
  if(a.above&&p>=a.above)out.push([t,'قیمت به $'+p.toFixed(2)+' رسید (بالای هدف $'+a.above+')']);
  if(a.below&&p<=a.below)out.push([t,'قیمت به $'+p.toFixed(2)+' رسید (زیر هدف $'+a.below+')']);
  if(a.fair&&fu!=null&&fu>0)out.push([t,'قیمت زیر ارزش ذاتی رفت ('+pct(fu,0)+' فاصله تا ارزش ذاتی)']);
  if(a.earn){var n=nextEarn(t);if(n){var days=Math.round((new Date(n.d)-new Date(new Date().toISOString().slice(0,10)))/864e5);if(days<=3)out.push([t,'گزارش مالی '+(days===0?'امروز':days+' روز دیگه')+' ('+n.d+')'])}}});return out}
function draw(){var W=wlGet(),m=$('rzw-main');
  if(!W.length){m.innerHTML='<div class="card empty">واچ‌لیستت خالیه. از جستجوی بالا یا دکمه‌ی ☆ در صفحه‌ی تحلیل هر سهم، سهم اضافه کن.<div class="chips" style="justify-content:center">'+['AAPL','MSFT','NVDA','GOOGL','AMZN','META'].map(function(t){return '<span class="chip" data-add="'+t+'">+ '+t+'</span>'}).join('')+'</div></div>';return}
  var A=alGet();
  var h='<div class="card"><div class="tw"><table><thead><tr><th style="text-align:right">سهم</th><th>قیمت</th><th>تغییر روز</th><th>امتیاز</th><th>ارزش</th><th>تا ارزش ذاتی</th><th>P/E</th><th>گزارش بعدی</th><th>هشدار</th><th></th></tr></thead><tbody>';
  W.forEach(function(t){var r=BY[t];if(!r){h+='<tr><td class="tk">'+esc(t)+'</td><td colspan="9" class="mut">داده‌ای نیست</td></tr>';return}
    var ch=r.chg,n=nextEarn(t),a=A[t]||{},on=a.above||a.below||a.fair||a.earn;
    h+='<tr><td><a class="tk" href="/pages/stock#'+esc(t)+'">'+esc(t)+'</a><div class="mut" style="font-size:12px;max-width:170px;overflow:hidden;text-overflow:ellipsis">'+esc(g(r,'n'))+'</div></td>'+
      '<td class="num">$'+(g(r,'price')||0).toFixed(2)+'</td><td class="num '+(ch>=0?'up':'dn')+'">'+(ch==null?'—':(ch>=0?'+':'')+ch.toFixed(2)+'%')+'</td>'+
      '<td style="text-align:center">'+sc(g(r,'s_total'))+'</td><td style="text-align:center">'+sc(g(r,'s_value'))+'</td>'+
      '<td class="num '+((g(r,'fair_up')||0)>=0?'up':'dn')+'">'+(g(r,'fair_up')==null?'—':pct(g(r,'fair_up'),0))+'</td><td class="num">'+x1(g(r,'pe'))+'</td>'+
      '<td class="num">'+(n?n.d.slice(5).replace('-','/'):'—')+'</td>'+
      '<td><button class="btn '+(on?'':'ghost ')+'sm" data-al="'+esc(t)+'">'+(on?'فعال':'تنظیم')+'</button></td><td><button class="btn ghost sm" data-rm="'+esc(t)+'">✕</button></td></tr>'});
  m.innerHTML=h+'</tbody></table></div><div class="chips"><a class="btn ghost sm" href="/pages/compare#'+W.slice(0,4).join(',')+'">مقایسه‌ی '+Math.min(4,W.length)+' سهم اول</a></div></div>';
  var H=hits();$('rzw-hit').innerHTML=H.length?'<div class="card" style="border-color:var(--gold)"><h3>🔔 هشدارهای فعال‌شده</h3>'+H.map(function(x){return '<div style="padding:4px 0"><b class="tk">'+x[0]+'</b> · '+esc(x[1])+'</div>'}).join('')+'</div>':''}
function dlg(t){var A=alGet(),a=A[t]||{},r=BY[t],p=r?g(r,'price'):0,d=$('rzw-dlg');d.style.display='block';
  d.innerHTML='<h3>هشدار برای <span class="tk">'+esc(t)+'</span> <span class="mut num" style="font-size:14px">(الان $'+(p||0).toFixed(2)+')</span></h3>'+
   '<div style="display:grid;gap:10px;max-width:420px"><label>اگه قیمت بالاتر رفت از ($)<input id="rzw-ab" inputmode="decimal" value="'+(a.above||'')+'" style="width:100%;direction:ltr"></label>'+
   '<label>اگه قیمت پایین‌تر اومد از ($)<input id="rzw-be" inputmode="decimal" value="'+(a.below||'')+'" style="width:100%;direction:ltr"></label>'+
   '<label><input type="checkbox" id="rzw-fa"'+(a.fair?' checked':'')+'> وقتی قیمت زیر ارزش ذاتی (DCF با فرض متوسط) رفت</label>'+
   '<label><input type="checkbox" id="rzw-ea"'+(a.earn?' checked':'')+'> ۳ روز قبل از گزارش مالی</label>'+
   '<div class="chips"><button class="btn" id="rzw-ok">ذخیره</button><button class="btn ghost" id="rzw-off">حذف هشدار</button><button class="btn ghost" id="rzw-x">بستن</button></div></div>';
  d.scrollIntoView({behavior:'smooth',block:'center'});
  $('rzw-ok').onclick=function(){var A=alGet(),ab=parseFloat($('rzw-ab').value),be=parseFloat($('rzw-be').value);A[t]={above:isFinite(ab)&&ab>0?ab:null,below:isFinite(be)&&be>0?be:null,fair:$('rzw-fa').checked,earn:$('rzw-ea').checked};alSet(A);d.style.display='none';askNotify();draw()};
  $('rzw-off').onclick=function(){var A=alGet();delete A[t];alSet(A);d.style.display='none';draw()};$('rzw-x').onclick=function(){d.style.display='none'}}
function askNotify(){if(!('Notification' in window)||Notification.permission!=='default')return;$('rzw-perm').innerHTML='<div class="chips"><button class="btn sm" id="rzw-np">🔔 اجازه‌ی اعلان در مرورگر</button></div>';$('rzw-np').onclick=function(){Notification.requestPermission().then(function(){$('rzw-perm').innerHTML=''})}}
function notify(){if(!('Notification' in window)||Notification.permission!=='granted')return;var seen={};try{seen=JSON.parse(sessionStorage.getItem('rzw_seen')||'{}')}catch(e){}
  hits().forEach(function(x){var k=x[0]+x[1];if(seen[k])return;seen[k]=1;try{new Notification('هشدار '+x[0],{body:x[1]})}catch(e){}});try{sessionStorage.setItem('rzw_seen',JSON.stringify(seen))}catch(e){}}
document.addEventListener('click',function(e){var b=e.target.closest('#rzw [data-rm],#rzw [data-al],#rzw [data-add]');if(!b)return;
  if(b.dataset.rm){wlSet(wlGet().filter(function(t){return t!==b.dataset.rm}));rzE('watch_remove',b.dataset.rm);draw()}else if(b.dataset.al)dlg(b.dataset.al);else if(b.dataset.add){var W=wlGet();if(W.indexOf(b.dataset.add)<0){W.push(b.dataset.add);rzE('watch_add',b.dataset.add)}wlSet(W);draw()}});
Promise.all([loadAll(),fetch(RAW+'/calendar/earnings.json?v='+Math.floor(Date.now()/3600000)).then(function(r){return r.ok?r.json():null}).catch(function(){return null})]).then(function(x){CAL=x[1];
  picker($('rzw-q'),$('rzw-s'),function(t){var W=wlGet();if(W.indexOf(t)<0){W.push(t);wlSet(W);rzE('watch_add',t)}draw()});draw();if(Object.keys(alGet()).length)askNotify();notify()})
  .catch(function(){$('rzw-main').innerHTML='<div class="card empty">بارگذاری داده‌ها ناموفق بود؛ صفحه رو دوباره باز کن.</div>'});
"""

# ---------------------------------------------------------------- earnings calendar
CAL_BODY = r"""
<div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:space-between">
<div class="chips" id="rze-f" style="margin:0"><span class="chip" data-f="all" style="color:#fff;border-color:var(--ac)">همه</span><span class="chip" data-f="big">فقط شرکت‌های بزرگ (بالای ۱۰ میلیارد)</span><span class="chip" data-f="watch">⭐ فقط واچ‌لیست من</span></div>
<span class="mut" id="rze-asof" style="font-size:12.5px"></span></div></div>
<div id="rze-main"><div class="card empty">در حال بارگذاری…</div></div>
<p class="note">پیش‌بینی EPS = میانگین پیش‌بینی تحلیلگرها. «قبل از بازار» یعنی قبل از شروع معاملات نیویورک (۱۵:۳۰ به وقت اروپای مرکزی) و «بعد از بازار» یعنی بعد از بسته شدن آن (۲۲:۰۰ به وقت اروپای مرکزی). منبع: Nasdaq.</p>
"""
CAL_JS = r"""
var CAL=null,F='all',WD=['یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه','جمعه','شنبه'];
var TM={pre:'قبل از بازار',after:'بعد از بازار',na:'—'};
function eps(v){return v==null?'—':'<span class="num">$'+v.toFixed(2)+'</span>'}
function draw(){if(!CAL){$('rze-main').innerHTML='<div class="card empty">تقویم هنوز آماده نیست؛ کمی بعد دوباره سر بزن.</div>';return}
  var W=wlGet(),today=new Date().toISOString().slice(0,10),ds0=Object.keys(CAL.days).sort(),h='',any=0;
  /* upcoming first (today at the top), then the recent results newest-first, so nobody has to scroll past a week of history */
  var ds=ds0.filter(function(d){return d>=today}).concat(ds0.filter(function(d){return d<today}).reverse()),pastHead=0;
  ds.forEach(function(d){
    if(d<today&&!pastHead){pastHead=1;h+='<h2 style="font-size:19px;margin:26px 0 10px;color:var(--mut);font-weight:500">نتیجه‌ی گزارش‌های اخیر</h2>'}var rows=CAL.days[d].filter(function(e){return F==='big'?e.mcap>=1e10:F==='watch'?W.indexOf(e.t)>=0:true});if(!rows.length)return;any=1;
    var dt=new Date(d+'T12:00:00Z'),past=d<today||rows.some(function(e){return e.act!=null}),lbl=WD[dt.getUTCDay()]+' '+dt.toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',timeZone:'UTC'});
    h+='<div class="card"'+(d===today?' style="border-color:var(--lime)"':'')+(past?' data-past="1"':'')+'><h3>'+lbl+(d===today?' · امروز':'')+' <span class="mut" style="font-size:13px;font-weight:600">('+rows.length+' شرکت)</span></h3><div class="tw"><table><thead><tr><th style="text-align:right">شرکت</th><th>زمان</th><th>ارزش بازار</th><th>'+(past?'EPS واقعی':'پیش‌بینی EPS')+'</th><th>'+(past?'پیش‌بینی':'EPS سال قبل')+'</th>'+(past?'<th>غافلگیری</th>':'')+'<th>امتیاز ما</th><th></th></tr></thead><tbody>'+
      rows.slice(0,60).map(function(e){var inW=W.indexOf(e.t)>=0;return '<tr><td><a class="tk" href="/pages/stock#'+esc(e.t)+'">'+esc(e.t)+'</a> <bdi dir="ltr" class="mut" style="font-size:12.5px">'+esc(e.n).slice(0,34)+'</bdi></td><td>'+TM[e.time]+'</td><td class="num">'+big(e.mcap)+'</td>'+
        (past?'<td>'+eps(e.act)+'</td><td>'+eps(e.f)+'</td><td class="num '+((e.sur||0)>=0?'up':'dn')+'">'+(e.sur==null?'—':(e.sur>=0?'+':'')+e.sur.toFixed(1)+'%')+'</td>':'<td>'+eps(e.f)+'</td><td>'+eps(e.ly)+'</td>')+
        '<td style="text-align:center">'+sc(e.s)+'</td><td><button class="btn '+(inW?'':'ghost ')+'sm" data-w="'+esc(e.t)+'">'+(inW?'⭐':'☆')+'</button></td></tr>'}).join('')+'</tbody></table></div>'+(rows.length>60?'<div class="note">'+(rows.length-60)+' شرکت کوچک‌تر دیگه هم گزارش میدن.</div>':'')+'</div>'});
  $('rze-main').innerHTML=any?h:'<div class="card empty">'+(F==='watch'?'هیچ‌کدوم از سهم‌های واچ‌لیستت در این بازه گزارش نمیدن.':'موردی نیست.')+'</div>';
}
document.addEventListener('click',function(e){var f=e.target.closest('#rze-f .chip');if(f){F=f.dataset.f;[].forEach.call(document.querySelectorAll('#rze-f .chip'),function(c){c.style.color=c===f?'#fff':'';c.style.borderColor=c===f?'var(--ac)':''});draw();return}
  var w=e.target.closest('#rze [data-w]');if(w){var W=wlGet(),t=w.dataset.w,i=W.indexOf(t);if(i>=0)W.splice(i,1);else W.push(t);wlSet(W);rzE(i>=0?'watch_remove':'watch_add',t);draw()}});
fetch(RAW+'/calendar/earnings.json?v='+Math.floor(Date.now()/1800000)).then(function(r){return r.ok?r.json():null}).then(function(j){CAL=j;if(j)$('rze-asof').textContent='به‌روزرسانی: '+liveWhen(j.as_of.replace('Z',':00Z'));draw()}).catch(function(){draw()});
"""


def portfolio_page():
    src = os.path.join(ROOT, 'web_src')
    css = CSS + open(os.path.join(src, 'portfolio.css'), encoding='utf-8').read()
    js = open(os.path.join(src, 'portfolio.js'), encoding='utf-8').read()
    return ('<div id="rzp" dir="rtl">\n<style>%s</style>\n%s\n<div class="card" id="rzp-head"></div>\n<div id="rzp-main"></div>\n'
            '<script>\n(function(){\n%s\n%s\n})();\n</script>\n</div>\n') % (css.replace('#ID', '#rzp'), nav('portfolio'), JS, js)


def superinvestors_page():
    src = os.path.join(ROOT, 'web_src')
    css = CSS + open(os.path.join(src, 'superinvestors.css'), encoding='utf-8').read()
    js = open(os.path.join(src, 'superinvestors.js'), encoding='utf-8').read()
    return ('<div id="rzi" dir="rtl">\n<style>%s</style>\n%s\n<h1>🦈 سوپر سرمایه‌گذارها</h1>\n'
            '<p class="sub">پورتفوی و خرید و فروش هر فصل وارن بافت، بیل اکمن، مایکل بری، لی لو، تری اسمیت و بیش از ۵۰ مدیر صندوق افسانه‌ای، از روی گزارش‌های رسمی 13F به SEC.</p>\n'
            '<div id="rzi-main"><div class="card empty">در حال بارگذاری…</div></div>\n'
            '<script>\n(function(){\n%s\n%s\n})();\n</script>\n</div>\n') % (css.replace('#ID', '#rzi'), nav('superinvestors'), JS, js)


def myportfolio_page():
    src = os.path.join(ROOT, 'web_src')
    css = CSS + open(os.path.join(src, 'myportfolio.css'), encoding='utf-8').read()
    js = open(os.path.join(src, 'myportfolio.js'), encoding='utf-8').read()
    return ('<div id="rzm" dir="rtl">\n<style>%s</style>\n%s\n<h1>📒 دفترچه سهام من</h1>\n'
            '<p class="sub">سهم‌هایی که خودت داری رو اضافه کن تا ارزش لحظه‌ای، سود و زیان، ترکیب صنعت‌ها، چکاپ ریسک، درآمد سود نقدی و سوپرسرمایه‌گذارهای هم‌مسیرت رو ببینی.</p>\n'
            '<div id="rzm-main"><div class="card empty">در حال بارگذاری…</div></div>\n'
            '<script>\n(function(){\n%s\n%s\n})();\n</script>\n</div>\n') % (css.replace('#ID', '#rzm'), nav('myportfolio'), JS, js)


def main():
    pages = {
        'my-portfolio.html': myportfolio_page(),
        'superinvestors.html': superinvestors_page(),
        'portfolio.html': portfolio_page(),
        'compare.html': page('compare', 'rzk', 'مقایسه‌ی سهم‌ها کنار هم', 'دو تا چهار سهم آمریکایی رو در امتیاز، ارزش‌گذاری، رشد، سودآوری، سلامت مالی و سود نقدی کنار هم ببین.', COMPARE_BODY, COMPARE_JS),
        'watchlist.html': page('watchlist', 'rzw', 'واچ‌لیست و هشدار قیمت', 'سهم‌هایی که دنبال می‌کنی، با قیمت لحظه‌ای، امتیاز، فاصله تا ارزش ذاتی و تاریخ گزارش بعدی؛ و هشدار وقتی به قیمت هدفت رسید.', WATCH_BODY, WATCH_JS),
        'pulse.html': page('pulse', 'rzq', 'نبض جامعه', 'این هفته ایرانی‌ها بیشتر از همه کدوم سهم‌ها رو زیر نظر داشتن؟ پربازدیدترین‌ها، جستجوها، ورود و خروج از واچ‌لیست‌ها و نظر بازدیدکننده‌ها؛ از رفتار واقعی کاربران همین سایت.', PULSE_BODY, PULSE_JS),
        'calendar.html': page('calendar', 'rze', 'تقویم گزارش‌های مالی', 'کدوم شرکت‌ها این هفته و هفته‌های بعد گزارش فصلی میدن، پیش‌بینی تحلیلگرها، و نتیجه‌ی گزارش‌های چند روز اخیر.', CAL_BODY, CAL_JS),
    }
    for f, html in pages.items():
        open(os.path.join(WEB, f), 'w', encoding='utf-8').write(html)
    # same tab bar on the existing tools
    for f, pid, root in (('stock.html', 'stock', 'rzs'), ('screener.html', 'screener', 'rzc2'), ('dcf.html', 'dcf', 'rzd')):
        p = os.path.join(WEB, f)
        s = open(p, encoding='utf-8').read()
        s2 = re.sub(r'<div class="nav">.*?</div>', lambda m: nav(pid), s, count=1, flags=re.S)
        block = '\n/* THEME:START */\n' + THEME.replace('#ID', '#' + root) + '\n/* THEME:END */\n'
        if '/* THEME:START */' in s2:
            s2 = re.sub(r'\n/\* THEME:START \*/.*?/\* THEME:END \*/\n', lambda m: block, s2, count=1, flags=re.S)
        else:
            s2 = s2.replace('</style>', block + '</style>', 1)
        if '/* EVENTS:START */' in s2:
            s2 = re.sub(r'\n/\* EVENTS:START \*/.*?/\* EVENTS:END \*/\n', lambda m: EVENTS_JS, s2, count=1, flags=re.S)
        else:
            s2 = s2.replace('<script>', '<script>' + EVENTS_JS, 1)
        open(p, 'w', encoding='utf-8').write(s2)
    print('ok')


if __name__ == '__main__':
    main()
