/* ---- Reza's portfolio (data injected by the Shopify page template as window.RZP) ----
   RZP = {access, logged, sub, login, meta, hist:[[date, idx, spyIdx]], live:{...}, trades:[{d,a,t,n,p,m,x}], posts:[{h,u,d,c}]}
   trades/vals/posts bodies are only present for subscribers (the template decides server-side). */
var P=window.RZP||{},ACC=!!P.access,META=P.meta||{},HIST=(P.hist||[]).filter(function(r){return r&&r[0]&&r[1]>0});
var TR=(P.trades||[]).slice().sort(function(a,b){return a.d<b.d?-1:a.d>b.d?1:0});
var NAMES={},TAB='port',RANGE='MAX',MODE='total',CMP=true;
var COLORS={up:['#bfe8dc','#8fd6c2','#5cc2a5','#2ea886'],dn:['#f6cfd2','#efa7ad','#e67c85','#d6505c']};
function money(v,d){if(v==null||!isFinite(v))return '—';var s=v<0?'-':'',a=Math.abs(v);if(d==='k'&&a>=1000)return s+'$'+(a/1000).toFixed(2)+'K';return s+'$'+a.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}
function sg(v,d){return v==null||!isFinite(v)?'—':(v>=0?'+':'')+(v*100).toFixed(d==null?2:d)+'%'}
function L(x,c){return '<bdi dir="ltr"'+(c?' class="'+c+'"':'')+' style="font-weight:800">'+x+'</bdi>'}
function cls(v){return v==null?'':v>=0?'up':'dn'}
function nyDate(t){return new Date(t||Date.now()).toLocaleDateString('en-CA',{timeZone:'America/New_York'})}
function fdate(s){try{return new Date(typeof s==='number'?s*1000:s).toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',year:'numeric'})}catch(e){return s}}
function shares(n){return (Math.round(n*10000)/10000).toLocaleString('en-US')}

/* imported past trades (Savvy Trader): shown in the feed only; their effect is already in the opening balance */
function hist(t){var e={a:t.a,d:t.d,t:(t.t||'').toUpperCase(),n:+t.n||0,p:+t.p||0,x:t.x,h:1},m=t.m==null?null:+t.m;
  if(t.a==='SELL')e.gp=m==null?null:m/100;else if(t.a==='BUY')e.inc=m==null?null:m/100;else e.m=m||0;if(t.a==='DIVIDEND')e.ps=+t.p||null;return e}
/* ---- ledger: holdings, cash, realized gains and a readable event feed ---- */
function book(trades){var pos={},cash=0,real=0,div=0,ev=[];
  trades.forEach(function(t){if(t.h){ev.push(hist(t));return}var a=t.a,k=(t.t||'').toUpperCase(),n=+t.n||0,p=+t.p||0,m=+t.m||0,o=k?(pos[k]||(pos[k]={n:0,cost:0,div:0,real:0,first:t.d})):null;
    if(a==='OPEN'){if(o){o.n+=n;o.cost+=n*p}else cash+=m;ev.push({a:a,d:t.d,t:k,n:n,p:p,m:m,x:t.x});return}
    if(a==='BUY'&&o){var before=o.n;o.n+=n;o.cost+=n*p;cash-=n*p;ev.push({a:a,d:t.d,t:k,n:n,p:p,inc:before>0?n/before:null,x:t.x});return}
    if(a==='SELL'&&o&&o.n>0){var q=Math.min(n,o.n),avg=o.cost/o.n,g=(p-avg)*q,frac=q/o.n;o.real+=g;real+=g;o.cost-=avg*q;o.n-=q;cash+=q*p;if(o.n<1e-6){o.n=0;o.cost=0}
      ev.push({a:a,d:t.d,t:k,n:q,p:p,frac:frac,gp:avg>0?p/avg-1:null,g:g,x:t.x});return}
    if(a==='DIVIDEND'&&o){var amt=m||(p&&o.n?p*o.n:0);o.div+=amt;div+=amt;cash+=amt;ev.push({a:a,d:t.d,t:k,m:amt,ps:p||(o.n?amt/o.n:null),x:t.x});return}
    if(a==='DEPOSIT'){cash+=m;ev.push({a:a,d:t.d,m:m,x:t.x});return}
    if(a==='WITHDRAW'){cash-=m;ev.push({a:a,d:t.d,m:m,x:t.x});return}
    if(t.x)ev.push({a:'NOTE',d:t.d,t:k,x:t.x})});
  return {pos:pos,cash:cash,real:real,div:div,ev:ev}}

/* ---- current holdings valued at live prices ---- */
var B=null,H=[],V=0,DAY=0,COST=0;
function value(){H=[];V=B?B.cash:0;DAY=0;COST=0;if(!B)return;
  Object.keys(B.pos).forEach(function(k){var o=B.pos[k];if(!(o.n>0))return;var q=RZQ&&RZQ.q[k],px=q&&q[0]>0?q[0]:(o.cost/o.n),prev=q&&q[2]>0?q[2]:px;
    var h={t:k,n:o.n,px:px,prev:prev,val:o.n*px,cost:o.cost,avg:o.cost/o.n,day:o.n*(px-prev),dayp:prev?px/prev-1:0,div:o.div,real:o.real};
    h.gain=h.val-h.cost;h.gainp=h.cost?h.gain/h.cost:0;H.push(h);V+=h.val;DAY+=h.day;COST+=h.cost});
  H.forEach(function(h){h.w=V?h.val/V:0});H.sort(function(a,b){return b.val-a.val})}

/* ---- performance index: stored daily history (+ today's live point for subscribers) ---- */
function quoteDay(){var c={},best=null;if(!RZQ)return null;H.forEach(function(h){var q=RZQ.q[h.t];if(q&&q[3]){var d=String(q[3]).slice(0,10);c[d]=(c[d]||0)+1;if(!best||c[d]>c[best])best=d}});return best}
function series(){var s=HIST.map(function(r){return [r[0],r[1],r[2]]}),today=quoteDay()||'0000';
  if(s.length&&today<=s[s.length-1][0]&&s[s.length-1][0]!==today)today='0000';
  if(ACC&&B&&V>0&&s.length&&today>s[0][0]&&(today>s[s.length-1][0]||(s.length>1&&today===s[s.length-1][0]&&!(META.savvy&&META.savvy.as_of>=today)))){var last=s[s.length-1],base=last[0]===today&&s.length>1?s[s.length-2]:last,dp=(V-DAY)>0?DAY/(V-DAY):0;
    var sq=RZQ&&RZQ.q.SPY,pt=[today,base[1]*(1+dp),sq&&sq[0]>0&&META.spy0?sq[0]/META.spy0:(last[0]===today?last[2]:base[2])];if(last[0]===today)s[s.length-1]=pt;else s.push(pt)}
  else if(P.live&&P.live.idx&&s.length){var l=P.live,lt=s[s.length-1];if(l.date&&l.date>=lt[0]){if(l.date===lt[0])s[s.length-1]=[l.date,l.idx,l.spy||lt[2]];else s.push([l.date,l.idx,l.spy||lt[2]])}}
  return s}
function at(s,date){var v=null;for(var i=0;i<s.length;i++){if(s[i][0]<=date)v=s[i];else break}return v||s[0]}
function back(days){var d=new Date();d.setDate(d.getDate()-days);return nyDate(d)}
function stats(s){var o={};if(!s.length)return o;var now=s[s.length-1],sv=META.savvy||{},first=s[0];
  var prev=s.length>1?s[s.length-2]:null;o.d1=ACC&&V>DAY?DAY/(V-DAY):(P.live&&P.live.day!=null?P.live.day:(prev?now[1]/prev[1]-1:null));
  var r=function(p){return p?now[1]/p[1]-1:null},long=s.length>=40&&first[0]<=back(300);
  if(long){o.m1=r(at(s,back(30)));o.ytd=r(at(s,(+now[0].slice(0,4)-1)+'-12-31'));o.y1=r(at(s,back(365)));o.tot=now[1]/first[1]-1;
    var yrs=(new Date(now[0])-new Date(first[0]))/31557600000;o.cagr=yrs>0.2?Math.pow(now[1]/first[1],1/yrs)-1:null}
  else{/* until the full history is imported: Savvy Trader's figures, rolled forward with our own daily changes */
    var a=sv.as_of?at(s,sv.as_of):first,f=a?now[1]/a[1]:1,ch=function(v){return v==null?null:(1+v/100)*f-1};
    o.m1=ch(sv.m1);o.ytd=ch(sv.ytd);o.y1=ch(sv.y1);o.tot=ch(sv.total);
    if(sv.total!=null&&sv.cagr!=null){var y0=Math.log(1+sv.total/100)/Math.log(1+sv.cagr/100),yy=y0+((new Date(now[0])-new Date(sv.as_of))/31557600000);o.cagr=Math.pow((1+sv.total/100)*f,1/yy)-1}}
  return o}

/* ---- chart ---- */
function drawChart(){var el=$('rzp-ch');if(!el)return;var s=series();if(s.length<2){el.innerHTML='<div class="empty">نمودار از اولین روز معاملاتی بعد از انتقال پر میشه.</div>';return}
  var from={'1M':back(31),'3M':back(92),'6M':back(183),'YTD':(new Date().getFullYear()-1)+'-12-31','1Y':back(366),'MAX':'0'}[RANGE];
  var pts=s.filter(function(r){return r[0]>=from});if(pts.length<2)pts=s.slice(-2);var b0=pts[0][1],s0=pts[0][2];
  var A=pts.map(function(r){return r[1]/b0-1}),Bm=pts.map(function(r){return s0&&r[2]?r[2]/s0-1:null}),useB=CMP&&Bm.every(function(v){return v!=null});
  var W=640,Ht=250,pl=44,pr=26,pt=10,pb=24,all=A.concat(useB?Bm:[]),mn=Math.min.apply(null,all.concat([0])),mx=Math.max.apply(null,all.concat([0])),pad=(mx-mn)*0.08||0.01;mn-=pad;mx+=pad;
  var X=function(i){return pl+(W-pl-pr)*i/(pts.length-1)},Y=function(v){return pt+(Ht-pt-pb)*(mx-v)/(mx-mn)};
  var path=function(arr){return arr.map(function(v,i){return (i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)}).join('')};
  var up=A[A.length-1]>=0,col=up?'#2ec4b6':'#ff5a5f',grid='',step=(mx-mn)>0.6?0.25:(mx-mn)>0.25?0.1:(mx-mn)>0.1?0.05:0.02;
  for(var g=Math.ceil(mn/step)*step;g<=mx;g+=step){grid+='<line x1="'+pl+'" x2="'+(W-pr)+'" y1="'+Y(g)+'" y2="'+Y(g)+'" stroke="'+(Math.abs(g)<1e-9?'#3c5a7d':'#1c3150')+'"/><text x="'+(pl-6)+'" y="'+(Y(g)+4)+'" fill="#93a7bf" font-size="11" text-anchor="end">'+Math.round(g*100)+'%</text>'}
  var lab='',nL=Math.min(5,pts.length);for(var j=0;j<nL;j++){var ii=Math.round((pts.length-1)*j/(nL-1||1));lab+='<text x="'+X(ii)+'" y="'+(Ht-6)+'" fill="#93a7bf" font-size="11" text-anchor="'+(j===0?'start':j===nL-1?'end':'middle')+'">'+new Date(pts[ii][0]).toLocaleDateString('en-US',{month:'short',year:'2-digit'})+'</text>'}
  el.innerHTML='<div class="chart"><svg viewBox="0 0 '+W+' '+Ht+'" width="100%" style="display:block;touch-action:pan-y"><defs><linearGradient id="rzpg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+col+'" stop-opacity=".35"/><stop offset="1" stop-color="'+col+'" stop-opacity="0"/></linearGradient></defs>'+grid+lab+
    '<path d="'+path(A)+'L'+X(A.length-1)+' '+Y(mn)+'L'+X(0)+' '+Y(mn)+'Z" fill="url(#rzpg)"/>'+(useB?'<path d="'+path(Bm)+'" fill="none" stroke="#f5b700" stroke-width="1.6" stroke-dasharray="4 3"/>':'')+
    '<path d="'+path(A)+'" fill="none" stroke="'+col+'" stroke-width="2.2"/><line id="rzp-cx" y1="'+pt+'" y2="'+(Ht-pb)+'" stroke="#93a7bf" stroke-dasharray="3 3" style="display:none"/></svg><div class="tip" id="rzp-tip"></div></div>'+
    '<div class="leg"><span><i style="background:'+col+'"></i>پورتفوی رضا <b class="'+cls(A[A.length-1])+'" style="direction:ltr;display:inline-block">'+sg(A[A.length-1])+'</b></span>'+(useB?'<span><i style="background:#f5b700"></i>S&amp;P 500 (SPY) <b style="direction:ltr;display:inline-block">'+sg(Bm[Bm.length-1])+'</b></span>':'')+'</div>';
  var svg=el.querySelector('svg'),tip=$('rzp-tip'),cx=$('rzp-cx');
  var mv=function(e){var r=svg.getBoundingClientRect(),xx=((e.touches?e.touches[0].clientX:e.clientX)-r.left)*W/r.width,i=Math.max(0,Math.min(pts.length-1,Math.round((xx-pl)/(W-pl-pr)*(pts.length-1))));
    cx.setAttribute('x1',X(i));cx.setAttribute('x2',X(i));cx.style.display='';tip.style.display='block';tip.innerHTML=fdate(pts[i][0])+'<br>پورتفوی: <b class="'+cls(A[i])+'" style="direction:ltr;display:inline-block">'+sg(A[i])+'</b>'+(useB?'<br>S&amp;P 500: <b style="direction:ltr;display:inline-block">'+sg(Bm[i])+'</b>':'');
    var left=X(i)/W*r.width;tip.style.left=Math.min(Math.max(left-70,0),r.width-150)+'px'};
  svg.addEventListener('mousemove',mv);svg.addEventListener('touchmove',mv,{passive:true});svg.addEventListener('mouseleave',function(){tip.style.display='none';cx.style.display='none'})}

/* ---- allocation treemap (squarified) ---- */
function squarify(items,x,y,w,h,out){if(!items.length)return;if(items.length===1){out.push([items[0],x,y,w,h]);return}
  var total=items.reduce(function(a,b){return a+b.v},0),row=[],rest=items.slice(),short=Math.min(w,h),best=Infinity;
  var worst=function(r){var s=r.reduce(function(a,b){return a+b.v},0),area=s/total*w*h,side=area/short;return Math.max.apply(null,r.map(function(it){var a=it.v/total*w*h,o=a/side;return Math.max(side/o,o/side)}))};
  while(rest.length){var cand=row.concat([rest[0]]),wr=worst(cand);if(wr<=best||!row.length){row=cand;best=wr;rest.shift()}else break}
  var s=row.reduce(function(a,b){return a+b.v},0),frac=s/total;
  if(w>=h){var rw=w*frac,yy=y;row.forEach(function(it){var hh=h*it.v/s;out.push([it,x,yy,rw,hh]);yy+=hh});squarify(rest,x+rw,y,w-rw,h,out)}
  else{var rh=h*frac,xx=x;row.forEach(function(it){var ww=w*it.v/s;out.push([it,xx,y,ww,rh]);xx+=ww});squarify(rest,x,y+rh,w,h-rh,out)}}
function shade(v){var a=Math.abs(v),l=a<0.005?0:a<0.015?1:a<0.04?2:3;return (v>=0?COLORS.up:COLORS.dn)[l]}
function drawTree(){var el=$('rzp-tm');if(!el)return;var items=H.map(function(h){return {v:h.val,h:h}});if(B&&B.cash>1)items.push({v:B.cash,cash:1});
  items.sort(function(a,b){return b.v-a.v});var out=[];squarify(items,0,0,100,100,out);
  el.innerHTML=out.map(function(o){var it=o[0],h=it.h,big=o[3]*o[4]>40,mid=o[3]*o[4]>14,tiny=o[3]*o[4]<4,ch=h?(MODE==='today'?h.dayp:h.gainp):null;
    var bg=it.cash?'#7fa6c9':shade(ch),lab=it.cash?'Cash':h.t,fs=big?15:mid?12:10;
    return '<a '+(h?'href="/pages/stock#'+encodeURIComponent(h.t)+'" ':'')+'style="left:'+o[1]+'%;top:'+o[2]+'%;width:'+o[3]+'%;height:'+o[4]+'%;background:'+bg+';font-size:'+fs+'px" title="'+lab+'">'+(tiny?'':lab)+(mid?'<small>'+(it.cash?((it.v/V)*100).toFixed(2)+'%':sg(ch))+'</small>':'')+'</a>'}).join('')}

/* ---- positions ---- */
function drawPos(){var el=$('rzp-pos');if(!el)return;var rows=H.slice();
  var html=rows.map(function(h,i){var ch=MODE==='today'?h.day:h.gain,cp=MODE==='today'?h.dayp:h.gainp;
    return '<a class="pc" href="/pages/stock#'+encodeURIComponent(h.t)+'"><span class="rk">#'+(i+1)+'</span><span class="lg">'+esc(h.t)+'</span><span class="nm"><b>'+esc(h.t)+'</b><span>'+(h.w*100).toFixed(2)+'% · '+shares(h.n)+' سهم</span></span>'+
      '<span class="vl"><b>$'+h.px.toFixed(2)+'</b><small class="'+cls(ch)+'">'+money(ch,'k')+' ('+sg(cp)+')</small></span></a>'}).join('');
  if(B&&B.cash>0)html+='<div class="pc"><span class="rk">#'+(rows.length+1)+'</span><span class="lg" style="color:var(--lime)">$</span><span class="nm"><b>Cash</b><span>'+((B.cash/V)*100).toFixed(2)+'%</span></span><span class="vl"><b>'+money(B.cash)+'</b></span></div>';
  el.innerHTML=html;
  $('rzp-sum').innerHTML='ارزش پورتفوی: '+L(money(V))+' · امروز: '+L(money(DAY)+' ('+sg(V>DAY?DAY/(V-DAY):0)+')',cls(DAY))+' · سود و زیان باز: '+L(money(V-B.cash-COST),cls(V-B.cash-COST))+(B.real?' · سود محقق‌شده: '+L(money(B.real),cls(B.real)):'')+(B.div?' · سود نقدی دریافتی: '+L(money(B.div),'up'):'')}

/* ---- history feed ---- */
var ACT={BUY:'خرید',SELL:'فروش',DIVIDEND:'سود نقدی',DEPOSIT:'واریز',WITHDRAW:'برداشت',NOTE:'یادداشت'};
function evText(e){var t='<span class="tk">'+esc(e.t||'')+'</span>';
  if(e.a==='BUY')return t+' — خرید '+L(shares(e.n))+' سهم'+(e.inc!=null?' ('+L(sg(e.inc,0))+' افزایش)':' (موقعیت جدید)')+' به قیمت '+L('$'+e.p.toFixed(2));
  if(e.a==='SELL')return t+' — فروش '+L(shares(e.n))+' سهم'+(e.frac!=null?' ('+(e.frac>=0.999?'کل موقعیت':L(sg(e.frac,0))+' از موقعیت')+')':'')+' به قیمت '+L('$'+e.p.toFixed(2))+(e.gp!=null?' با '+L(sg(e.gp),cls(e.gp))+' '+(e.gp>=0?'سود':'زیان'):'');
  if(e.a==='DIVIDEND')return t+' — دریافت سود نقدی '+L(money(e.m),'up')+(e.ps?' (<span class="num">$'+e.ps.toFixed(3)+'</span> برای هر سهم)':'');
  if(e.a==='DEPOSIT')return 'واریز پول نقد '+L(money(e.m));if(e.a==='WITHDRAW')return 'برداشت پول نقد '+L(money(e.m));return t+' — یادداشت'}
function drawFeed(){var el=$('rzp-feed');if(!el)return;var open=B.ev.filter(function(e){return e.a==='OPEN'}),ev=B.ev.filter(function(e){return e.a!=='OPEN'});
  if(open.length)ev.push({a:'XFER',d:open[0].d,n:open.filter(function(e){return e.t}).length,m:open.filter(function(e){return !e.t}).reduce(function(a,b){return a+b.m},0)});
  ev.sort(function(a,b){return b.d-a.d});
  el.innerHTML=ev.map(function(e){if(e.a==='XFER')return '<div class="ev"><b>📦 انتقال پورتفوی از <bdi>Savvy Trader</bdi></b><span class="when">'+fdate(e.d)+'</span><p>'+e.n+' سهم و '+L(money(e.m))+' پول نقد با همون قیمت خرید قبلی منتقل شد. از اینجا به بعد همه‌ی معاملات همین‌جا ثبت میشه. معاملات قبل از این تاریخ از تاریخچه‌ی <bdi>Savvy Trader</bdi> آورده شده.</p></div>';
    return '<div class="ev '+({BUY:'buy',SELL:'sell',DIVIDEND:'div'}[e.a]||'')+'"><b>'+evText(e)+'</b><span class="when">'+fdate(e.d)+(e.h?' · Savvy Trader':'')+'</span>'+(e.x?'<p>'+esc(e.x)+'</p>':'')+'</div>'}).join('')||'<div class="empty">هنوز معامله‌ای ثبت نشده.</div>'}

/* ---- community (blog posts with subscriber-only comments) ---- */
function drawPosts(){var el=$('rzp-posts');if(!el)return;var ps=P.posts||[];
  el.innerHTML=(ps.length?ps.map(function(p){return '<a class="post" href="'+esc(p.u)+'"><b>'+esc(p.h)+'</b><small>'+fdate(p.d)+' · 💬 '+(p.c||0)+' نظر</small></a>'}).join(''):'<div class="empty">اولین یادداشت به‌زودی منتشر میشه.</div>')+
    '<p class="note">فقط رضا یادداشت جدید می‌نویسه؛ مشترکین زیر هر یادداشت نظر و سؤالشون رو می‌نویسن. هر یادداشت جدید برای مشترکین ایمیل هم میشه.</p>'}

/* ---- page ---- */
function cta(){var login=P.logged?'':'<p class="note" style="margin-top:12px">قبلاً مشترک شدی؟ <a href="'+esc(P.login||'/account/login?return_url=/pages/portfolio')+'">وارد حسابت شو</a></p>';
  return '<div class="cta-box"><h3>🔒 پورتفوی کامل رضا، فقط برای مشترکین</h3><ul><li>همه‌ی سهم‌ها با وزن، قیمت خرید و سود و زیان دقیق</li><li>هر خرید و فروش، همون روز، با دلیلش</li><li>جامعه‌ی مشترکین: زیر هر تصمیم نظر و سؤالت رو بنویس</li><li>ایمیل فوری هر معامله و یادداشت جدید</li></ul>'+
    '<div class="pr">$300</div> <span class="mut">/ سال</span><br><a class="btn" style="margin-top:12px;font-size:16px;padding:11px 26px" href="'+esc(P.sub||'/products/portfolio-pro')+'">عضویت سالانه</a>'+login+'</div>'}
function header(){var s=series(),o=stats(s),cell=function(l,v){return '<div><small>'+l+'</small><b class="'+cls(v)+'">'+sg(v)+'</b></div>'};
  $('rzp-head').innerHTML='<div class="ph"><div class="av">'+(P.avatar?'<img src="'+esc(P.avatar)+'" alt="">':'ر')+'</div><div class="who"><b>پورتفوی رضا حاجیلو</b><span>سرمایه‌گذاری بلندمدت در سهام آمریکا · از آوریل ۲۰۲۵</span></div></div>'+
    '<div class="stats">'+cell('۱ روز',o.d1)+cell('۱ ماه',o.m1)+cell('از ابتدای سال',o.ytd)+cell('۱ سال',o.y1)+cell('کل',o.tot)+cell('رشد سالانه (CAGR)',o.cagr)+
    '<div><small>ارزش پورتفوی</small><b>'+(ACC&&V?money(V,'k'):'🔒')+'</b></div></div>'+
    '<p class="note">'+(RZQ&&RZQ.as_of?(RZQ_ST[RZQ.status]||'قیمت')+' · '+liveWhen(RZQ.as_of):'')+(P.live&&P.live.as_of&&!ACC?'به‌روزرسانی: '+liveWhen(P.live.as_of):'')+'</p>'}
function render(){header();var m=$('rzp-main');
  var tabs='<div class="tabs"><button data-tab="port"'+(TAB==='port'?' class="on"':'')+'>پورتفوی</button><button data-tab="hist"'+(TAB==='hist'?' class="on"':'')+'>تاریخچه‌ی معاملات</button><button data-tab="comm"'+(TAB==='comm'?' class="on"':'')+'>جامعه</button></div>';
  var perf='<div class="card"><div class="chd"><h3>عملکرد</h3><div class="seg" id="rzp-rg">'+['1M','3M','6M','YTD','1Y','MAX'].map(function(r){return '<button data-r="'+r+'"'+(r===RANGE?' class="on"':'')+'>'+r+'</button>'}).join('')+'</div></div><div id="rzp-ch"></div>'+
    '<label class="mut" style="font-size:13px;cursor:pointer"><input type="checkbox" id="rzp-cmp"'+(CMP?' checked':'')+' style="vertical-align:middle;margin-left:4px">مقایسه با S&amp;P 500</label></div>';
  var body='';
  if(TAB==='port'){
    if(ACC)body='<div class="grid2">'+perf+'<div class="card"><div class="chd"><h3>ترکیب پورتفوی</h3><div class="seg" id="rzp-md"><button data-m="today"'+(MODE==='today'?' class="on"':'')+'>امروز</button><button data-m="total"'+(MODE==='total'?' class="on"':'')+'>کل</button></div></div><div class="tm" id="rzp-tm"></div></div></div>'+
      '<div class="card"><div class="chd"><h3>'+H.length+' سهم</h3><div class="seg" id="rzp-md2"><button data-m="today"'+(MODE==='today'?' class="on"':'')+'>امروز</button><button data-m="total"'+(MODE==='total'?' class="on"':'')+'>کل</button></div></div><p class="mut" id="rzp-sum" style="font-size:13.5px;margin:0 0 6px"></p><div class="pos" id="rzp-pos"></div></div>';
    else body=perf+'<div class="lock card"><div class="blur">'+fakePos()+'</div><div class="cta">'+cta()+'</div></div>'}
  else if(TAB==='hist')body=ACC?'<div class="card feed" id="rzp-feed"></div>':'<div class="lock card" style="min-height:420px"><div class="blur">'+fakeFeed()+'</div><div class="cta">'+cta()+'</div></div>';
  else body='<div class="card posts" id="rzp-posts"></div>'+(ACC?'':'<div class="card" style="text-align:center">'+cta()+'</div>');
  m.innerHTML=tabs+body+'<p class="note">این پورتفوی واقعی رضاست و فقط برای آموزش و شفافیت منتشر میشه؛ پیشنهاد خرید یا فروش نیست. قیمت‌ها حدود ۱۵ دقیقه تأخیر دارن.</p>';
  if(TAB==='port'){drawChart();if(ACC){drawTree();drawPos()}}else if(TAB==='hist'&&ACC)drawFeed();else if(TAB==='comm')drawPosts()}
function fakePos(){var t=['SE','MELI','META','NU','KSPI','BRK-B','PODD','HCA','DLO'],h='<div class="pos">';for(var i=0;i<9;i++)h+='<div class="pc"><span class="rk">#'+(i+1)+'</span><span class="lg">???</span><span class="nm"><b>●●●●</b><span>●●%</span></span><span class="vl"><b>$●●●</b><small>●●●</small></span></div>';return h+'</div>'}
function fakeFeed(){var h='';for(var i=0;i<4;i++)h+='<div class="feed"><div class="ev"><b>●●●● — خرید ●● سهم به قیمت $●●●</b><p>دلیل این تصمیم ●●●● ●●●●● ●●● ●●●●●●● ●●●● ●●●●</p></div></div>';return h}
document.getElementById('rzp').addEventListener('click',function(e){var b=e.target.closest('[data-tab]');if(b){TAB=b.dataset.tab;try{history.replaceState(null,'','#'+TAB)}catch(x){}render();return}
  b=e.target.closest('[data-r]');if(b){RANGE=b.dataset.r;[].forEach.call($('rzp-rg').children,function(c){c.classList.toggle('on',c.dataset.r===RANGE)});drawChart();return}
  b=e.target.closest('[data-m]');if(b){MODE=b.dataset.m;render()}});
document.getElementById('rzp').addEventListener('change',function(e){if(e.target.id==='rzp-cmp'){CMP=e.target.checked;drawChart()}});
var h0=(location.hash||'').slice(1);if(h0==='hist'||h0==='comm')TAB=h0;
B=ACC?book(TR):null;value();
liveQuotes().then(function(){value();render()});render();
setInterval(function(){RZQ_P=null;liveQuotes().then(function(){if(ACC){value()}render()})},180000);
