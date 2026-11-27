"""نبض بازار (sahamanaliz.com/pages/market-pulse): the Farsi edition of the market pulse the other sites build with
tools/mpulse.py. On Shopify the page is a thin loader (theme/templates/page.market-pulse.liquid -> web/market-pulse.html),
so everything is drawn in the browser from data that is already public: the screener (names, sectors, market values,
rescaled to live prices by liveRow), the worker's quotes (15-second quotes for the 20 largest companies while the market
is open), the calendar branch for earnings, content/fa_names.json for Farsi company names, and the official Fed/BLS
dates in content/macro.json (copied from the site repos; the same file on every edition).
Market news rule: what happened and when, never a forecast or advice."""
import json, os, datetime as dt

ROOT = os.path.dirname(os.path.abspath(__file__))


def macro_events():
    try:
        M = json.load(open(os.path.join(ROOT, 'content', 'macro.json'), encoding='utf-8'))
    except Exception:
        return []
    out = []
    for x in M['events']:
        hh, mm = map(int, x['t'].split(':'))
        d = dt.date.fromisoformat(x['d'])
        mar = dt.date(d.year, 3, 8); mar += dt.timedelta(days=(6 - mar.weekday()) % 7)
        nov = dt.date(d.year, 11, 1); nov += dt.timedelta(days=(6 - nov.weekday()) % 7)
        ts = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=dt.timezone.utc) + dt.timedelta(hours=4 if mar <= d < nov else 5)
        out.append([x['k'], int(ts.timestamp()), x.get('ym') or '', x.get('ref') or ''])
    return out


MP_BODY = r"""
<style>
#ID .pm-stat{display:flex;flex-wrap:wrap;align-items:center;gap:8px 20px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 18px;margin:0 0 14px}
#ID .pm-live{display:flex;align-items:center;gap:8px;font-weight:900}#ID .pm-live i{width:9px;height:9px;border-radius:50%;background:var(--mut)}
#ID .pm-stat.open .pm-live i{background:var(--ac);animation:rzmpp 1.8s infinite}@keyframes rzmpp{0%{box-shadow:0 0 0 0 rgba(79,163,122,.6)}70%{box-shadow:0 0 0 8px rgba(79,163,122,0)}100%{box-shadow:0 0 0 0 rgba(79,163,122,0)}}
#ID .pm-big{font-size:26px;font-weight:900}#ID .pm-stat small,#ID .pm-asof{color:var(--mut);font-size:13px}#ID .pm-asof{margin-inline-start:auto}
#ID h2{font-size:20px;font-weight:900;margin:22px 0 10px;color:#fff}#ID h3{font-size:16px;font-weight:900;margin:14px 0 8px;color:#fff}
#ID .pmh{position:relative;width:100%;border-radius:14px;overflow:hidden;background:#0b1220;direction:ltr}
#ID .hm-sec{position:absolute;box-sizing:border-box;border:1px solid #0b1220;overflow:hidden}
#ID .hm-sn{position:absolute;right:4px;top:0;font-size:11px;line-height:15px;font-weight:800;color:#c9d3e0;white-space:nowrap;overflow:hidden;max-width:calc(100% - 6px);direction:rtl}
#ID .pmh a{position:absolute;box-sizing:border-box;border:1px solid #0b1220;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff!important;text-decoration:none!important;overflow:hidden;text-align:center;line-height:1.1;font-family:Inter,Arial,sans-serif}
#ID .pmh a:hover{filter:brightness(1.25);z-index:2}#ID .pmh a b{font-weight:800;white-space:nowrap}#ID .pmh a span{opacity:.9}
#ID .hm-key{display:flex;align-items:center;gap:3px;flex-wrap:wrap;margin:8px 0 0;font-size:12px;color:var(--mut)}#ID .hm-key i{width:26px;height:10px;border-radius:2px}#ID .hm-key span{margin:0 4px}#ID .hm-key em{font-style:normal;margin-inline-start:auto}
#ID .pm-mv{display:grid;grid-template-columns:1fr 1fr;gap:14px}
#ID .pm-list a{display:grid;grid-template-columns:64px 1fr auto;gap:8px;align-items:center;padding:8px 12px;border:1px solid var(--line);border-radius:12px;background:var(--card);margin-bottom:6px;text-decoration:none!important;color:var(--ink)!important}
#ID .pm-list a:hover{border-color:var(--gold)}#ID .pm-list .nm{color:var(--mut);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#ID .pm-cal{display:grid;gap:8px}#ID .pm-ev{display:grid;grid-template-columns:72px 1fr;gap:14px;align-items:start;background:var(--card);border:1px solid var(--line);border-inline-start:3px solid var(--gold);border-radius:12px;padding:10px 14px}
#ID .pm-ev.k-cpi,#ID .pm-ev.k-ppi{border-inline-start-color:var(--red)}#ID .pm-ev.k-jobs{border-inline-start-color:#5b8def}#ID .pm-ev.k-minutes{border-inline-start-color:var(--mut)}
#ID .pm-ev .d{display:flex;flex-direction:column;align-items:center;text-align:center}#ID .pm-ev .d b{font-size:16px}#ID .pm-ev .d span{color:var(--mut);font-size:12px}
#ID .pm-ev .b{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px}#ID .pm-ev .per{color:var(--mut);font-size:13px}#ID .pm-ev p{flex-basis:100%;margin:2px 0 0;font-size:14px;color:var(--mut)}
#ID .pm-ev .cd{margin-inline-start:auto;font-size:13px;font-weight:800;color:var(--mut)}#ID .pm-ev .cd.soon{color:var(--gold)}#ID .pm-ev .cd.done{color:var(--ac)}
#ID table{width:100%;border-collapse:collapse;font-size:14px}#ID th{color:var(--gold);text-align:start;padding:9px 10px;white-space:nowrap}#ID td{padding:9px 10px;border-top:1px solid var(--line)}#ID td a{color:var(--ink)!important;text-decoration:none!important}
#ID details{border-bottom:1px solid var(--line);padding:10px 0}#ID summary{cursor:pointer;font-weight:800}#ID details p{color:var(--mut);margin:6px 0 0}
@media(max-width:700px){#ID .pm-mv{grid-template-columns:1fr}#ID .pm-asof,#ID .hm-key em,#ID .pm-ev .cd{margin-inline-start:0;flex-basis:100%}}
</style>
<div class="pm-stat" id="rzmp-stat"><div class="pm-live"><i></i><span id="rzmp-sess">در حال بارگذاری…</span></div><div><b class="pm-big" id="rzmp-mkt">—</b> <small>۵۰۰ شرکت بزرگ آمریکا، وزنی بر اساس ارزش بازار · <span id="rzmp-br"></span></small></div><div class="pm-asof" id="rzmp-asof"></div></div>
<h2>نقشه‌ی حرارتی بازار</h2>
<div class="pmh" id="rzmp-hm"><div class="card empty">در حال بارگذاری…</div></div>
<div class="hm-key"><span class="num">−۳٪</span><i style="background:#b8403c"></i><i style="background:#8a3a39"></i><i style="background:#3a3f4b"></i><i style="background:#2c7a51"></i><i style="background:#2f9d63"></i><span class="num">+۳٪</span><em>اندازه‌ی هر خانه = ارزش بازار · برای تحلیل هر شرکت روی آن بزنید</em></div>
<h2>بیشترین حرکت‌ها همین حالا</h2>
<div class="pm-mv"><div><h3>بیشترین رشد</h3><div class="pm-list" id="rzmp-g"></div></div><div><h3>بیشترین افت</h3><div class="pm-list" id="rzmp-l"></div></div></div>
<p class="note">شرکت‌های بالای ۲ میلیارد دلار ارزش بازار.</p>
<h2>گزارش‌های مالی روزهای پیش رو</h2>
<div id="rzmp-earn"><div class="card empty">در حال بارگذاری…</div></div>
<p class="note">شرکت‌های بالای ۵ میلیارد دلار. نتیجه‌ی هر گزارش تا یک ساعت بعد از انتشار اینجا می‌آید. <a href="/pages/earnings">تقویم کامل گزارش‌ها</a></p>
<h2>تقویم اقتصادی آمریکا</h2>
<p class="note">تاریخ‌های رسمی فدرال رزرو و اداره‌ی آمار کار آمریکا؛ ساعت‌ها به وقت نیویورک و به وقت شما.</p>
<div class="pm-cal" id="rzmp-cal"></div>
<h2>این گزارش‌ها چه معنایی دارند؟</h2>
<div class="card" id="rzmp-what"></div>
<h2>سؤال‌های رایج</h2>
<div id="rzmp-faq"></div>
<p class="note">قیمت‌ها از بورس آمریکا؛ ۲۰ شرکت بزرگ در ساعات معامله هر ۱۵ ثانیه و بقیه هر چند دقیقه به‌روز می‌شوند. فقط اطلاع‌رسانی است، نه توصیه‌ی خرید یا فروش.</p>
"""

MP_JS = r"""
var EV=%EVENTS%;
var W='https://rz-events.mreza-hajilou.workers.dev/c';
var SEC={'Technology':'فناوری','Finance':'مالی','Health Care':'سلامت','Consumer Discretionary':'کالاهای غیرضروری','Consumer Staples':'کالاهای اساسی','Industrials':'صنعتی','Energy':'انرژی','Utilities':'خدمات عمومی','Real Estate':'املاک','Basic Materials':'مواد اولیه','Telecommunications':'مخابرات','Miscellaneous':'سایر'};
var SESS={'Open':'بازار باز است','Pre Market':'پیش‌بازار','After Hours':'پس از بسته‌شدن بازار','Closed':'بازار بسته است'};
var MON=['ژانویه','فوریه','مارس','آوریل','مه','ژوئن','ژوئیه','اوت','سپتامبر','اکتبر','نوامبر','دسامبر'];
var K={fomc:['تصمیم نرخ بهره‌ی فدرال رزرو','تصمیم فدرال رزرو','کمیته‌ی بازار باز فدرال نرخ بهره‌ی پایه‌ی آمریکا را تعیین می‌کند که مبنای هزینه‌ی وام در کل اقتصاد است. کاهش نرخ معمولاً به نفع سهام و اوراق قرضه است؛ افزایش غیرمنتظره یا نشانه‌ی کاهش کمتر، بیشتر به سهام رشدی ضربه می‌زند.'],
 cpi:['شاخص قیمت مصرف‌کننده (تورم)','تورم','سرعت بالا رفتن قیمت‌ها برای مصرف‌کننده را می‌سنجد. تورم بالاتر از انتظار احتمال کاهش نرخ بهره را کم می‌کند و معمولاً سهام را پایین می‌کشد؛ تورم پایین‌تر برعکس.'],
 jobs:['گزارش اشتغال آمریکا','گزارش اشتغال','تعداد شغل‌های جدید، نرخ بیکاری و رشد دستمزد ماه قبل. گزارش خیلی قوی می‌تواند انتظار نرخ بهره را بالا ببرد و گزارش ضعیف نگرانی از رکود را بیشتر می‌کند.'],
 ppi:['شاخص قیمت تولیدکننده','قیمت تولیدکننده','قیمتی که شرکت‌ها برای کالا و خدماتشان می‌گیرند؛ نشانه‌ای زودهنگام از تورم و حاشیه‌ی سود شرکت‌ها.'],
 minutes:['صورت‌جلسه‌ی فدرال رزرو','صورت‌جلسه‌ی فدرال رزرو','گزارش کامل آخرین جلسه که سه هفته بعد منتشر می‌شود. بازار آن را می‌خواند تا ببیند چند عضو طرفدار کاهش یا افزایش بیشتر نرخ هستند.']};
var NM={},Q={},LQ={},SES='',ASOF='',LAST=null;
function fa(s){return String(s).replace(/\d/g,function(d){return '۰۱۲۳۴۵۶۷۸۹'[d]}).replace(/\./g,'٫')}
function rp(c){if(c==null)return '—';var a=Math.abs(c*100),f=a.toFixed(a>=99.95?0:1),g=+f===0?'':c>=0?'+':'−';return fa(g+f)+'٪'}
function sp(c){return '<span class="num">'+rp(c)+'</span>'}
function cl(c){return c==null?'':c>=0?'up':'dn'}
function lk(t){return '/pages/stock#'+encodeURIComponent(t)}
function rows(){var o=[];ROWS.forEach(function(r){var t=g(r,'t'),m=g(r,'mcap'),p=g(r,'price');if(!t||!(m>=2e9)||!(p>0))return;var x=LQ[t],c=r.chg!=null?r.chg/100:null;
  if(x&&x[0]>0){m=m*x[0]/p;p=x[0];c=x[1]!=null?x[1]/100:c}o.push({t:t,n:NM[t]||'',s:SEC[g(r,'sector')]||'سایر',p:p,c:c,m:m})});o.sort(function(a,b){return b.m-a.m});return o}
function worst(r,w){var s=0,mx=0,mn=Infinity;r.forEach(function(x){s+=x.a;mx=Math.max(mx,x.a);mn=Math.min(mn,x.a)});var s2=s*s,w2=w*w;return Math.max(w2*mx/s2,s2/(w2*mn))}
function squarify(items,x,y,w,h){var tot=0;items.forEach(function(o){tot+=o.v});var sc=w*h/(tot||1),it=items.map(function(o){return {o:o,a:o.v*sc}}),out=[],row=[];
  function lay(){var s=0;row.forEach(function(r){s+=r.a});if(w>=h){var cw=s/h,yy=y;row.forEach(function(r){var hh=r.a/cw;out.push({o:r.o,x:x,y:yy,w:cw,h:hh});yy+=hh});x+=cw;w-=cw}
    else{var ch=s/w,xx=x;row.forEach(function(r){var ww=r.a/ch;out.push({o:r.o,x:xx,y:y,w:ww,h:ch});xx+=ww});y+=ch;h-=ch}row=[]}
  while(it.length){var side=Math.min(w,h),nx=it[0];if(!row.length||worst(row.concat([nx]),side)<=worst(row,side)){row.push(nx);it.shift()}else lay()}if(row.length)lay();return out}
function color(c){if(c==null)return '#2a2e37';var v=Math.max(-3,Math.min(3,c*100))/3,a=Math.abs(v),n=[58,63,75],t=v>=0?[47,157,99]:[184,64,60];return 'rgb('+[0,1,2].map(function(k){return Math.round(n[k]+(t[k]-n[k])*Math.pow(a,0.8))}).join(',')+')'}
function raw(c){if(c==null)return '—';var a=Math.abs(c*100),f=a.toFixed(a>=99.95?0:1),g2=+f===0?'':c>=0?'+':'−';return g2+f+'%'}
function heat(R){var box=$('rzmp-hm');if(!box||!R.length)return;var mob=window.innerWidth<700,N=mob?120:200,W0=box.clientWidth;if(!W0)return;var H0=mob?640:560,by={};
  R.slice(0,N).forEach(function(r){(by[r.s]=by[r.s]||[]).push(r)});
  var secs=Object.keys(by).map(function(k){var v=0;by[k].forEach(function(r){v+=r.m});return {k:k,v:v,rs:by[k]}}).sort(function(a,b){return b.v-a.v}),h='';
  squarify(secs,0,0,W0,H0).forEach(function(S){var hd=S.w>70&&S.h>40?15:0;h+='<div class="hm-sec" style="left:'+S.x.toFixed(1)+'px;top:'+S.y.toFixed(1)+'px;width:'+S.w.toFixed(1)+'px;height:'+S.h.toFixed(1)+'px">'+(hd?'<span class="hm-sn">'+esc(S.o.k)+'</span>':'');
    squarify(S.o.rs.map(function(r){return {v:r.m,r:r}}),0,hd,S.w,S.h-hd).forEach(function(T){var r=T.o.r,fs=Math.max(9,Math.min(26,Math.sqrt(T.w*T.h)/4.2)),lab='';
      if(T.w>26&&T.h>16)lab='<b style="font-size:'+fs.toFixed(0)+'px">'+esc(r.t)+'</b>'+(T.h>fs*2.3&&T.w>34?'<span style="font-size:'+Math.max(9,fs*.62).toFixed(0)+'px">'+raw(r.c)+'</span>':'');
      h+='<a href="'+lk(r.t)+'" title="'+esc((r.n?r.n+' · ':'')+r.t)+'" style="left:'+T.x.toFixed(1)+'px;top:'+T.y.toFixed(1)+'px;width:'+T.w.toFixed(1)+'px;height:'+T.h.toFixed(1)+'px;background:'+color(r.c)+'">'+lab+'</a>'});h+='</div>'});
  box.style.height=H0+'px';box.innerHTML=h}
function stat(R){var top=R.slice(0,500).filter(function(r){return r.c!=null});if(top.length>100){var w=0,s=0,up=0;top.forEach(function(r){w+=r.m;s+=r.c*r.m;if(r.c>0)up++});var m=s/w;
  $('rzmp-mkt').innerHTML='<span class="'+cl(m)+'">'+sp(m)+'</span>';$('rzmp-br').textContent=fa(up)+' رشد، '+fa(top.length-up)+' افت'}
  $('rzmp-sess').textContent=SESS[SES]||'بازار آمریکا';$('rzmp-stat').classList.toggle('open',SES==='Open');
  if(ASOF){var d=new Date(ASOF);if(!isNaN(d))$('rzmp-asof').textContent='قیمت‌ها: '+d.toLocaleString('fa-IR-u-ca-gregory',{timeZone:'America/New_York',day:'numeric',month:'long',hour:'2-digit',minute:'2-digit',hour12:false})+' به وقت نیویورک · خودکار به‌روز می‌شود'}}
function movers(R){var A=R.filter(function(r){return r.c!=null}),li=function(rs){return rs.map(function(r){return '<a href="'+lk(r.t)+'"><b class="tk">'+esc(r.t)+'</b><span class="nm">'+esc(r.n)+'</span><span class="'+cl(r.c)+'">'+sp(r.c)+'</span></a>'}).join('')};
  $('rzmp-g').innerHTML=li(A.slice().sort(function(a,b){return b.c-a.c}).slice(0,8));$('rzmp-l').innerHTML=li(A.slice().sort(function(a,b){return a.c-b.c}).slice(0,8))}
function usd(v){return '<span class="num">'+(v<0?'−':'')+'$'+Math.abs(v).toFixed(2)+'</span>'}
var CAL=null;
function earn(R){var box=$('rzmp-earn');if(!CAL){return}var P={};R.forEach(function(r){P[r.t]=r});var now=new Date(),lo=new Date(now-864e5).toISOString().slice(0,10),hi=new Date(+now+8*864e5).toISOString().slice(0,10),h='',n=0;
  Object.keys(CAL).sort().forEach(function(d){if(d<lo||d>hi||n>=5)return;var L=(CAL[d]||[]).filter(function(x){return (x.mcap||0)>=5e9}).sort(function(a,b){return (b.mcap||0)-(a.mcap||0)}).slice(0,8);if(!L.length)return;n++;
    var dd=new Date(d+'T12:00:00Z');h+='<h3>'+dd.toLocaleDateString('fa-IR-u-ca-gregory',{weekday:'long',day:'numeric',month:'long',timeZone:'UTC'})+'</h3><div class="card tw" style="padding:0;overflow-x:auto"><table><tr><th>شرکت</th><th>زمان</th><th>پیش‌بینی سود هر سهم</th><th>نتیجه</th><th>سهم امروز</th></tr>';
    L.forEach(function(x){var r=P[x.t],res;if(x.act!=null){var f=x.f,a=x.act;if(f==null)res=usd(a);else{var w=a>f?'بهتر از انتظار':a<f?'ضعیف‌تر از انتظار':'مطابق انتظار',p=a!=f&&x.sur!=null&&Math.abs(f)>=.01&&f*a>0&&Math.abs(x.sur)<100?' '+sp(x.sur/100):'';res=usd(a)+' <span class="'+(a>=f?'up':'dn')+'">('+w+p+')</span>'}}else res='<span class="mut">هنوز اعلام نشده</span>';
      h+='<tr><td><a href="'+lk(x.t)+'"><b class="tk">'+esc(x.t)+'</b> '+esc(NM[x.t]||'')+'</a></td><td>'+({pre:'قبل از بازگشایی',after:'بعد از بسته‌شدن'}[x.time]||'—')+'</td><td>'+(x.f!=null?usd(x.f):'—')+'</td><td>'+res+'</td><td>'+(r&&r.c!=null?'<span class="'+cl(r.c)+'">'+sp(r.c)+'</span>':'—')+'</td></tr>'});h+='</table></div>'});
  box.innerHTML=h||'<div class="card empty">در روزهای پیش رو گزارش شرکت بزرگی نیست.</div>'}
function per(e){if(e[2]){var p=e[2].split('-');return MON[+p[1]-1]+' '+fa(p[0])}var b=new Date(e[3]+'T12:00:00Z'),a=new Date(b-864e5);return 'جلسه‌ی '+fa(a.getUTCDate())+' و '+fa(b.getUTCDate())+' '+MON[b.getUTCMonth()]}
function nyTime(ts){return new Date(ts*1000).toLocaleTimeString('fa-IR',{timeZone:'America/New_York',hour:'2-digit',minute:'2-digit',hour12:false})}
function myTime(ts){return new Date(ts*1000).toLocaleTimeString('fa-IR',{hour:'2-digit',minute:'2-digit',hour12:false})}
function cal(){var now=Date.now()/1000,h='';EV.filter(function(e){return e[1]>now-20*3600}).forEach(function(e){var d=new Date(e[1]*1000),k=K[e[0]];
  h+='<div class="pm-ev k-'+e[0]+'"><div class="d"><b>'+d.toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',timeZone:'America/New_York'})+'</b><span>'+d.toLocaleDateString('fa-IR-u-ca-gregory',{weekday:'long',timeZone:'America/New_York'})+'</span></div>'+
   '<div class="b"><strong>'+k[0]+'</strong><span class="per">'+per(e)+' · ساعت '+nyTime(e[1])+' به وقت نیویورک ('+myTime(e[1])+' به وقت شما)</span>'+(e[0]==='fomc'?'<p>بیانیه و پیش‌بینی‌های اقتصادی ساعت ۱۴:۰۰ و کنفرانس خبری ساعت ۱۴:۳۰ به وقت نیویورک.</p>':'')+'<span class="cd" data-ts="'+e[1]+'"></span></div></div>'});
  $('rzmp-cal').innerHTML=h;countdowns();
  $('rzmp-what').innerHTML=Object.keys(K).map(function(k){return '<p><b>'+K[k][0]+':</b> '+K[k][2]+'</p>'}).join('');
  var nf=EV.filter(function(e){return e[0]==='fomc'&&e[1]>now})[0],nc=EV.filter(function(e){return e[0]==='cpi'&&e[1]>now})[0],nj=EV.filter(function(e){return e[0]==='jobs'&&e[1]>now})[0];
  var D=function(e){return new Date(e[1]*1000).toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',year:'numeric',timeZone:'America/New_York'})};
  var F=[['نبض بازار چیست؟','یک صفحه برای همه‌ی چیزهایی که همین حالا بورس آمریکا را تکان می‌دهد: جهت بازار، نقشه‌ی حرارتی بزرگ‌ترین شرکت‌ها، بیشترین رشد و افت، گزارش‌های مالی پیش رو و گزارش‌های اقتصادی؛ تا وقتی بازار باز است خودش به‌روز می‌شود.'],
    ['نقشه‌ی حرارتی بازار چیست؟','هر خانه یک شرکت است؛ اندازه‌اش ارزش بازار شرکت و رنگش تغییر قیمت امروز: سبز یعنی رشد و قرمز یعنی افت. شرکت‌ها بر اساس صنعت کنار هم هستند تا با یک نگاه ببینید حرکت بازار همه‌گیر است یا فقط چند سهم.']];
  if(nf)F.push(['جلسه‌ی بعدی فدرال رزرو کی است؟','جلسه‌ی بعدی فدرال رزرو '+per(nf)+' است و تصمیم نرخ بهره روز '+D(nf)+' ساعت ۱۴:۰۰ به وقت نیویورک اعلام می‌شود.']);
  if(nc)F.push(['گزارش تورم بعدی آمریکا کی منتشر می‌شود؟','شاخص قیمت مصرف‌کننده‌ی '+per(nc)+' روز '+D(nc)+' ساعت ۸:۳۰ صبح به وقت نیویورک منتشر می‌شود.']);
  if(nj)F.push(['گزارش اشتغال بعدی آمریکا کی است؟','گزارش اشتغال '+per(nj)+' روز '+D(nj)+' ساعت ۸:۳۰ صبح به وقت نیویورک منتشر می‌شود.']);
  $('rzmp-faq').innerHTML=F.map(function(x){return '<details><summary>'+x[0]+'</summary><p>'+x[1]+'</p></details>'}).join('')}
function countdowns(){var now=Date.now()/1000;document.querySelectorAll('#rzmp .cd[data-ts]').forEach(function(s){var d=+s.dataset.ts-now,t;
  if(d<=0)t=d>-6*3600?'امروز منتشر شد':'منتشر شد';else if(d<3600)t=fa(Math.ceil(d/60))+' دقیقه‌ی دیگر';else if(d<86400)t=fa(Math.floor(d/3600))+' ساعت و '+fa(Math.floor(d%3600/60))+' دقیقه‌ی دیگر';else t=fa(Math.floor(d/86400))+' روز و '+fa(Math.floor(d%86400/3600))+' ساعت دیگر';
  s.textContent=t;s.classList.toggle('soon',d>0&&d<86400);s.classList.toggle('done',d<=0)})}
function draw(){var R=rows();if(R.length>50){LAST=R;stat(R);heat(R);movers(R);earn(R)}}
function quotes(){return fetch(W+'/quotes.json?v='+Math.floor(Date.now()/30000)).then(function(r){if(!r.ok)throw 0;return r.json()}).catch(function(){return fetch(RAW+'/quotes/quotes.json?v='+Math.floor(Date.now()/60000)).then(function(r){return r.json()})})}
function refresh(){quotes().then(function(j){RZQ=j;SES=j.status||SES;ASOF=j.as_of||ASOF;ROWS.forEach(function(r){var x=j.q&&j.q[g(r,'t')];if(x&&x[1]!=null)r.chg=x[1]});draw();
  if(SES!=='Open'||!LAST)return;return fetch(W+'/q?t='+LAST.slice(0,20).map(function(r){return r.t}).join(',')).then(function(r){return r.json()}).then(function(k){var q=k.q||{};for(var t in q)LQ[t]=q[t];ASOF=k.at||ASOF;draw()})}).catch(function(){})}
function earnData(){return fetch(RAW+'/calendar/earnings.json?v='+Math.floor(Date.now()/600000)).then(function(r){return r.json()}).then(function(j){CAL=j.days||{};if(LAST)earn(LAST)}).catch(function(){$('rzmp-earn').innerHTML='<div class="card empty">تقویم گزارش‌ها بارگذاری نشد.</div>'})}
cal();setInterval(countdowns,30000);
Promise.all([loadAll(),fetch(RAW+'/main/content/fa_names.json').then(function(r){return r.json()}).catch(function(){return {}})]).then(function(x){NM=x[1]||{};if(RZQ){SES=RZQ.status||'';ASOF=RZQ.as_of||''}draw();earnData();refresh();
  setInterval(function(){if(!document.hidden)refresh()},30000);setInterval(function(){if(!document.hidden)earnData()},600000);
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){if(LAST)heat(LAST)},200)})}).catch(function(){$('rzmp-hm').innerHTML='<div class="card empty">داده‌ها بارگذاری نشد؛ چند لحظه بعد صفحه را دوباره باز کنید.</div>'});
"""


def js():
    return MP_JS.replace('%EVENTS%', json.dumps(macro_events()))
