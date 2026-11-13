/* طلا و نقره — gold & silver page. Data: RAW/gold/gold.json (gold.py, every ~30 min). Dollars only.
   Free: prices, note, chart, comparison, calendar, miners, calculators. Stock Pro: drivers (real yield, 10y, dollar)
   and speculator positioning (CFTC). */
var ACC=!!window.RZS_ACCESS,SUB=window.RZS_SUB_URL||'/products/stock-data-pro',SUBY=window.RZS_SUB_Y||'/products/stock-data-pro-yearly';
var OZ=31.1034768,D=null,ST={m:'gold',r:'1y'};
var FA='۰۱۲۳۴۵۶۷۸۹';function fa(s){return String(s).replace(/[0-9]/g,function(c){return FA[c]})}
function n2(v,d){return v==null||!isFinite(v)?'—':v.toLocaleString('en-US',{minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d})}
function usd(v,d){return '<span class="num">$'+n2(v,d)+'</span>'}
function sg(v,d){return v==null||!isFinite(v)?'—':(v>=0?'+':'')+v.toFixed(d==null?2:d)}
function cls(v){return v==null?'':v>=0?'up':'dn'}
function day(s){try{var d=new Date(s);if(isNaN(d))return '';return d.toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',year:'numeric'})}catch(e){return ''}}
function when(s){try{return new Date(s).toLocaleString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Europe/Berlin'})+' به وقت اروپای مرکزی'}catch(e){return ''}}
function lock(inner,title,txt){return '<div class="plk"><div class="plk-b">'+inner+'</div><div class="plk-c"><div class="plk-box"><h3>🔒 '+title+'</h3><p>'+txt+'</p>'
  +'<div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap"><a class="btn" href="'+esc(SUBY)+'">سالانه <span class="num">€47.94</span>، ۵۰٪ تخفیف</a><a class="btn ghost" href="'+esc(SUB)+'">ماهانه <span class="num">€7.99</span></a></div>'
  +(window.RZS_LOGGED?'':'<p style="margin:10px 0 0;font-size:12.5px">قبلاً مشترک شدی؟ <a href="/account/login?return_url=%2Fpages%2Fgold">وارد حسابت شو</a></p>')+'</div></div></div>'}

/* ---------------------------------------------------------------- prices */
function priceCard(k,name,icon){var s=(D.spot||{})[k]||{};var g=s.p?s.p/OZ:null;
  return '<div class="pc"><div class="h"><span>'+icon+' '+name+'</span><span class="ch '+cls(s.chg)+'">'+sg(s.chg)+'%</span></div>'
    +'<div class="v">'+usd(s.p)+'</div><div class="u">هر اونس (۳۱٫۱ گرم)</div>'
    +'<div class="g"><span>هر گرم <b>'+usd(g)+'</b></span><span>دیروز <b>'+usd(s.prev)+'</b></span></div></div>'}
function ratioCard(){var R=D.ratio;if(!R)return '';var lo=R.min20,hi=R.max20,P=function(x){return Math.max(0,Math.min(100,(x-lo)/(hi-lo)*100))};
  var vs=R.now>R.avg20*1.05?'نقره نسبت به طلا <b>ارزان‌تر</b> از میانگین ۲۰ ساله است':R.now<R.avg20*0.95?'نقره نسبت به طلا <b>گران‌تر</b> از میانگین ۲۰ ساله است':'نزدیک میانگین ۲۰ ساله است';
  return '<div class="card"><div class="ratio"><div class="big">'+n2(R.now,1)+'</div><p><b>نسبت طلا به نقره:</b> با پول یک اونس طلا <span class="num">'+n2(R.now,0)+'</span> اونس نقره می‌شود خرید. میانگین ۲۰ ساله <span class="num">'+n2(R.avg20,0)+'</span> است؛ یعنی '+vs+'.</p>'
    +'<div class="rbar" dir="ltr"><div class="t"></div><div class="a" style="left:'+P(R.avg20)+'%"></div><div class="m" style="left:'+P(R.now)+'%"></div>'
    +'<span class="lb" style="left:3%">'+n2(lo,0)+'</span><span class="lb" style="left:'+P(R.avg20)+'%">میانگین '+n2(R.avg20,0)+'</span><span class="lb" style="left:97%">'+n2(hi,0)+'</span></div></div></div>'}

/* ---------------------------------------------------------------- chart */
var RANGES=[['1m','۱ ماه',31],['6m','۶ ماه',183],['1y','۱ سال',366],['5y','۵ سال',1827],['20y','۲۰ سال',7306]];
function series(){var m=ST.m,days=RANGES.filter(function(r){return r[0]===ST.r})[0][2];
  var cut=new Date(Date.now()-days*864e5).toISOString().slice(0,10),S=[];
  if(days<=400){var d=(D.d||{})[m]||[];d.filter(function(r){return r[0]>=cut}).forEach(function(r){S.push(r)});return {daily:true,rows:S}}
  ((D.w||{})[m]||[]).filter(function(r){return r[0]>=cut}).forEach(function(r){S.push(r)});
  var real=m==='gold'&&D.real?D.real.gold.filter(function(r){return r[0]>=cut}):null;
  return {daily:false,rows:S,real:real}}
function path(pts){return pts.map(function(p,i){return (i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)}).join('')}
function drawChart(){var s=series(),R=s.rows;if(R.length<2){$('rzg-ch').innerHTML='<p class="mut">داده کافی نیست.</p>';return}
  var box=$('rzg-ch'),W=Math.max(300,Math.round(box.clientWidth||720)),H=W<500?230:300,pl=4,pr=62,pt=10,pb=24,all=[];
  R.forEach(function(r){all.push(r[1]);if(s.daily){if(r[2])all.push(r[2]);if(r[3])all.push(r[3])}});
  if(s.real)s.real.forEach(function(r){all.push(r[1])});
  var lo=Math.min.apply(null,all),hi=Math.max.apply(null,all),pad=(hi-lo)*0.06||1;lo-=pad;hi+=pad;
  var t0=new Date(R[0][0]).getTime(),t1=new Date(R[R.length-1][0]).getTime();
  var X=function(d){return pl+(new Date(d).getTime()-t0)/(t1-t0||1)*(W-pl-pr)},Y=function(v){return pt+(hi-v)/(hi-lo)*(H-pt-pb)};
  var g='';for(var i=0;i<=4;i++){var v=lo+(hi-lo)*i/4,y=Y(v);g+='<line x1="'+pl+'" x2="'+(W-pr)+'" y1="'+y+'" y2="'+y+'" stroke="#262B36"/><text x="'+(W-pr+6)+'" y="'+(y+4)+'" fill="#8A8F99" font-size="11">$'+n2(v,v>=1000?0:2)+'</text>'}
  var nT=W<500?3:5;for(var j=0;j<=nT;j++){var tt=t0+(t1-t0)*j/nT,dd=new Date(tt);var lb=(ST.r==='5y'||ST.r==='20y')?String(dd.getFullYear()):dd.toLocaleDateString('fa-IR-u-ca-gregory',{month:'short',year:'2-digit'});
    g+='<text x="'+Math.min(W-pr-20,Math.max(pl+20,X(dd.toISOString().slice(0,10))))+'" y="'+(H-6)+'" fill="#8A8F99" font-size="11" text-anchor="middle">'+lb+'</text>'}
  var main=path(R.map(function(r){return [X(r[0]),Y(r[1])]})),ex='';
  if(s.daily){var m5=R.filter(function(r){return r[2]}).map(function(r){return [X(r[0]),Y(r[2])]}),m2=R.filter(function(r){return r[3]}).map(function(r){return [X(r[0]),Y(r[3])]});
    if(m5.length>1)ex+='<path d="'+path(m5)+'" fill="none" stroke="#4FA37A" stroke-width="1.6" stroke-dasharray="5 3"/>';
    if(m2.length>1)ex+='<path d="'+path(m2)+'" fill="none" stroke="#C8534F" stroke-width="1.6" stroke-dasharray="5 3"/>'}
  if(s.real&&s.real.length>1)ex+='<path d="'+path(s.real.map(function(r){return [X(r[0]),Y(r[1])]}))+'" fill="none" stroke="#8A8F99" stroke-width="1.6"/>';
  var area=main+'L'+X(R[R.length-1][0]).toFixed(1)+','+(H-pb)+'L'+X(R[0][0]).toFixed(1)+','+(H-pb)+'Z';
  var col=ST.m==='gold'?'#C9A961':'#C0C6D0';
  $('rzg-ch').innerHTML='<div class="chart" id="rzg-cv"><svg viewBox="0 0 '+W+' '+H+'" dir="ltr"><defs><linearGradient id="rzgG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+col+'" stop-opacity=".25"/><stop offset="1" stop-color="'+col+'" stop-opacity="0"/></linearGradient></defs>'
    +g+'<path d="'+area+'" fill="url(#rzgG)"/>'+ex+'<path d="'+main+'" fill="none" stroke="'+col+'" stroke-width="2.2"/><line id="rzg-x" y1="'+pt+'" y2="'+(H-pb)+'" stroke="#8A8F99" stroke-width="1" style="display:none"/><circle id="rzg-dot" r="4" fill="'+col+'" style="display:none"/></svg><div class="tip" id="rzg-tip"></div></div>'
    +'<div class="legend"><span><i style="background:'+col+'"></i>قیمت '+(ST.m==='gold'?'طلا':'نقره')+'</span>'
    +(s.daily?'<span><i style="background:#4FA37A"></i>میانگین ۵۰ روزه</span><span><i style="background:#C8534F"></i>میانگین ۲۰۰ روزه</span>':'')
    +(s.real?'<span><i style="background:#8A8F99"></i>قیمت با حذف اثر تورم (به دلار امروز)</span>':'')
    +'</div>';
  var cv=$('rzg-cv'),svg=cv.querySelector('svg'),tip=$('rzg-tip'),ln=$('rzg-x'),dot=$('rzg-dot');
  function mv(e){var b=svg.getBoundingClientRect(),cx=((e.touches?e.touches[0].clientX:e.clientX)-b.left)/b.width*W;var best=null,bd=1e9;
    R.forEach(function(r){var d=Math.abs(X(r[0])-cx);if(d<bd){bd=d;best=r}});if(!best)return;
    var x=X(best[0]),y=Y(best[1]);ln.setAttribute('x1',x);ln.setAttribute('x2',x);ln.style.display='';dot.setAttribute('cx',x);dot.setAttribute('cy',y);dot.style.display='';
    tip.innerHTML=day(best[0])+' · <b class="num">$'+n2(best[1])+'</b>';tip.style.display='block';var px=x/W*b.width;tip.style.left=Math.max(0,Math.min(b.width-tip.offsetWidth,px-tip.offsetWidth/2))+'px'}
  function out(){tip.style.display='none';ln.style.display='none';dot.style.display='none'}
  cv.addEventListener('mousemove',mv);cv.addEventListener('touchmove',mv,{passive:true});cv.addEventListener('mouseleave',out);cv.addEventListener('touchend',out);
  plain()}
function plain(){var d=(D.d||{})[ST.m]||[],L=d[d.length-1],nm=ST.m==='gold'?'طلا':'نقره';if(!L||!L[3]){$('rzg-pl').innerHTML='';return}
  var g2=L[1]/L[3]-1,g5=L[2]?L[1]/L[2]-1:null,h='قیمت '+nm+' <b class="num '+cls(g2)+'">'+Math.abs(g2*100).toFixed(1)+'%</b> '+(g2>=0?'بالاتر':'پایین‌تر')+' از میانگین ۲۰۰ روزه'
    +(g5!=null?' و <b class="num '+cls(g5)+'">'+Math.abs(g5*100).toFixed(1)+'%</b> '+(g5>=0?'بالاتر':'پایین‌تر')+' از میانگین ۵۰ روزه است.':' است.');
  // golden / death cross in the last 30 trading days
  for(var i=Math.max(1,d.length-30);i<d.length;i++){var a=d[i-1],b=d[i];if(!a[2]||!a[3]||!b[2]||!b[3])continue;
    if(a[2]<a[3]&&b[2]>=b[3])h+=' <span class="flag" style="background:rgba(79,163,122,.18);color:#4FA37A">تقاطع طلایی در '+day(b[0])+'</span> <small class="mut">(میانگین ۵۰ روزه از ۲۰۰ روزه بالاتر رفت)</small>';
    if(a[2]>a[3]&&b[2]<=b[3])h+=' <span class="flag" style="background:rgba(200,83,79,.18);color:#C8534F">تقاطع مرگ در '+day(b[0])+'</span> <small class="mut">(میانگین ۵۰ روزه از ۲۰۰ روزه پایین‌تر رفت)</small>'}
  $('rzg-pl').innerHTML=h+' <small class="mut">این یک توصیف است، نه پیش‌بینی یا پیشنهاد خرید و فروش.</small>'}
function tabs(){var h='<div class="tabs" id="rzg-m">'+[['gold','🥇 طلا'],['silver','🥈 نقره']].map(function(x){return '<button data-m="'+x[0]+'"'+(ST.m===x[0]?' class="on"':'')+'>'+x[1]+'</button>'}).join('')+'<span class="sp"></span>'
  +RANGES.map(function(r){return '<button data-r="'+r[0]+'"'+(ST.r===r[0]?' class="on"':'')+'>'+r[1]+'</button>'}).join('')+'</div>';return h}

/* ---------------------------------------------------------------- comparison */
function cmpCard(){var C=D.cmp||{},rows=[['gold','طلا'],['silver','نقره'],['spx','شاخص S&amp;P 500'],['btc','بیت‌کوین']],Ys=['1','5','10','20'];
  var best={};Ys.forEach(function(y){var b=null;rows.forEach(function(r){var v=(C[r[0]]||{})[y];if(v!=null&&(b==null||v>b))b=v});best[y]=b});
  var h='<div class="card"><h3>📊 طلا در برابر سهام و بیت‌کوین</h3><div class="tw"><table class="cmp"><thead><tr><th>دارایی</th>'+Ys.map(function(y){return '<th>'+fa(y)+' ساله</th>'}).join('')+'</tr></thead><tbody>';
  rows.forEach(function(r){h+='<tr><td>'+r[1]+'</td>'+Ys.map(function(y){var v=(C[r[0]]||{})[y];if(v==null)return '<td class="mut">—</td>';
    var t=Math.abs(v)>=10?'×'+(1+v).toFixed(0):(v>=0?'+':'')+(v*100).toFixed(0)+'%';return '<td class="'+cls(v)+(v===best[y]?' best':'')+'">'+t+'</td>'}).join('')+'</tr>'});
  return h+'</tbody></table></div><p class="src">تغییر قیمت در هر دوره، بدون سود نقدی سهام. بیت‌کوین ۲۰ سال سابقه ندارد. سبز پررنگ = بهترین بازده آن دوره. بازده گذشته تضمینی برای آینده نیست.</p></div>'}

/* ---------------------------------------------------------------- drivers (Stock Pro) */
function spark(s,col){if(!s||s.length<2)return '';var v=s.map(function(r){return r[1]}),lo=Math.min.apply(null,v),hi=Math.max.apply(null,v),W=200,H=36;
  return '<svg viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" dir="ltr"><path d="'+path(s.map(function(r,i){return [i/(s.length-1)*W,H-2-(r[1]-lo)/((hi-lo)||1)*(H-4)]}))+'" fill="none" stroke="'+col+'" stroke-width="1.6" vector-effect="non-scaling-stroke"/></svg>'}
function dCard(o,k,unit,why,dec){if(!o)return '';var w=o.w1,y=o.y1;
  return '<div class="dc"><div class="k">'+k+'</div><div class="v">'+n2(o.v,dec==null?2:dec)+unit+'</div><div class="s">یک هفته: <span class="num '+cls(w)+'">'+sg(w,dec==null?2:dec)+'</span> · یک سال: <span class="num '+cls(y)+'">'+sg(y,dec==null?2:dec)+'</span></div>'
    +spark(o.s,'#C9A961')+'<div class="why">'+why+'</div></div>'}
function cotCard(k,nm){var L=((D.cot||{})[k])||[];if(L.length<4)return '';var last=L[L.length-1],ns=L.map(function(r){return r.n}),lo=Math.min.apply(null,ns),hi=Math.max.apply(null,ns),pos=hi>lo?(last.n-lo)/(hi-lo):0.5;
  var lvl=pos>0.8?'نزدیک بالاترین سطح یک سال اخیر (خوش‌بینی زیاد؛ گاهی نشانه‌ی شلوغ شدن معامله)':pos<0.2?'نزدیک پایین‌ترین سطح یک سال اخیر (بدبینی زیاد)':'در میانه‌ی دامنه‌ی یک سال اخیر';
  return '<div class="dc"><div class="k">موقعیت خالص سفته‌بازها روی '+nm+' (قراردادهای آتی)</div><div class="v">'+n2(last.n,0)+'</div>'
    +'<div class="s">خرید <span class="num">'+n2(last.l,0)+'</span> · فروش <span class="num">'+n2(last.s,0)+'</span> · گزارش '+day(last.d)+'</div>'
    +spark(L.map(function(r){return [r.d,r.n]}),k==='gold'?'#C9A961':'#C0C6D0')+'<div class="why">'+lvl+'.</div></div>'}
function drvCard(){var V=D.drv||{};
  var inner='<div class="drv">'
    +dCard(V.ry,'بازده واقعی اوراق ۱۰ ساله‌ی آمریکا (بهره منهای تورم)','%','مهم‌ترین عامل قیمت طلا: وقتی این عدد بالا می‌رود، نگه‌داشتن طلا (که سودی نمی‌دهد) پرهزینه‌تر می‌شود و برعکس.')
    +dCard(V.y10,'بازده اوراق ۱۰ ساله‌ی آمریکا','%','نرخ بهره‌ی بلندمدت بازار.')
    +dCard(V.dxy,'شاخص دلار آمریکا','','دلار قوی‌تر معمولاً طلا را برای خریداران خارج از آمریکا گران‌تر می‌کند.',1)
    +cotCard('gold','طلا')+cotCard('silver','نقره')+'</div>'
    +'<p class="src">منابع: خزانه‌داری آمریکا، کمیسیون معاملات آتی کالا (CFTC، گزارش هفتگی جمعه‌ها)، شاخص دلار ICE.</p>';
  var h='<div class="card"><h3>🧭 عوامل اصلی قیمت طلا</h3>';
  return h+(ACC?inner:lock(inner,'عوامل اصلی قیمت طلا مخصوص مشترکین Stock Pro است','بازده واقعی اوراق، شاخص دلار و موقعیت سفته‌بازها در بازار آتی طلا و نقره، با روند یک سال اخیر و توضیح ساده‌ی اثر هر کدام.'))+'</div>'}
function calCard(){var f=(D.cal||{}).fomc;if(!f)return '';var dd=Math.ceil((new Date(f+'T19:00:00Z')-Date.now())/864e5);
  return '<div class="card"><h3>📅 تقویم اقتصادی</h3><div class="cal"><div>جلسه‌ی بعدی فدرال رزرو (تصمیم نرخ بهره)<b>'+(dd<=0?'امروز':fa(dd)+' روز دیگر')+'</b><span class="mut" style="font-size:12.5px">'+day(f)+'</span></div></div>'
    +'<p class="src">تصمیم‌های نرخ بهره معمولاً روی طلا اثر مستقیم دارند. منبع: وب‌سایت فدرال رزرو.</p></div>'}

/* ---------------------------------------------------------------- miners & funds */
var MIN=[['NEM','نیومانت','بزرگ‌ترین معدن‌کار طلا'],['AEM','اگنیکو ایگل','معدن طلا'],['B','بریک','معدن طلا و مس'],['WPM','ویتون پرشس متالز','حق امتیاز طلا و نقره'],['FNV','فرانکو-نوادا','حق امتیاز طلا'],['RGLD','رویال گلد','حق امتیاز طلا'],['KGC','کینروس','معدن طلا'],['AU','انگلوگلد آشانتی','معدن طلا'],['PAAS','پن امریکن سیلور','معدن نقره'],['HL','هکلا','معدن نقره'],['AG','فرست ماجستیک','معدن نقره'],['CDE','کوردالن','معدن طلا و نقره']];
var FUN=[['GLD','صندوق طلای SPDR',1],['IAU','صندوق طلای iShares',1],['SLV','صندوق نقره‌ی iShares',1],['GDX','صندوق معدن‌کاران طلا',0],['GDXJ','صندوق معدن‌کاران کوچک طلا',0],['SIL','صندوق معدن‌کاران نقره',0]];
function minersCard(Q){var q=(Q&&Q.q)||{};
  var h='<div class="card"><h3>⛏️ سهام معدن‌کاران و صندوق‌های طلا و نقره</h3><div class="mn">'+MIN.map(function(m){var x=q[m[0]];
    return '<a href="/pages/stocks/'+m[0].toLowerCase()+'"><span class="tk">'+m[0]+'</span><small>'+m[1]+' · '+m[2]+'</small>'+(x?'<div class="q"><span>$'+n2(x[0])+'</span><span class="'+cls(x[1])+'">'+sg(x[1])+'%</span></div>':'')+'</a>'}).join('')+'</div>'
    +'<h3 style="margin-top:14px;font-size:15px">صندوق‌ها (ETF)</h3><div class="mn">'+FUN.map(function(f){var inner='<span class="tk">'+f[0]+'</span><small>'+f[1]+'</small>';
      return f[2]?'<a href="/pages/stocks/'+f[0].toLowerCase()+'">'+inner+'</a>':'<span class="x">'+inner+'</span>'}).join('')+'</div>'
    +'<p class="src">سهام معدن‌کاران معمولاً تندتر از خود طلا بالا و پایین می‌روند. روی هر نماد بزنی، تحلیل کامل آن سهم باز می‌شود.</p></div>';return h}

/* ---------------------------------------------------------------- calculators */
function jewelCard(){return '<div class="card"><h3>💍 ماشین‌حساب قیمت طلای زینتی (دلار)</h3><div class="calc">'
  +'<label>وزن (گرم)<input id="rzg-jw" type="number" min="0" step="0.01" value="10"></label>'
  +'<label>عیار<select id="rzg-jk"><option value="24">۲۴ عیار (۹۹۹)</option><option value="22">۲۲ عیار (۹۱۶)</option><option value="21">۲۱ عیار (۸۷۵)</option><option value="18" selected>۱۸ عیار (۷۵۰)</option><option value="14">۱۴ عیار (۵۸۵)</option></select></label>'
  +'<label>اجرت ساخت (٪)<input id="rzg-jf" type="number" min="0" step="0.5" value="10"></label>'
  +'<label>مالیات / سود فروشنده (٪)<input id="rzg-jt" type="number" min="0" step="0.5" value="0"></label></div><div class="res" id="rzg-jr"></div>'
  +'<p class="src">بر اساس قیمت جهانی همین لحظه. قیمت واقعی در هر کشور و هر فروشگاه فرق دارد.</p></div>'}
function jewel(){var s=(D.spot||{}).gold||{};if(!s.p)return;var w=+$('rzg-jw').value||0,k=+$('rzg-jk').value,f=+$('rzg-jf').value||0,t=+$('rzg-jt').value||0;
  var metal=w*(k/24)*s.p/OZ,fee=metal*f/100,tax=(metal+fee)*t/100,tot=metal+fee+tax;
  $('rzg-jr').innerHTML='<div class="row2"><span>ارزش طلای خالص</span><b>'+usd(metal)+'</b></div><div class="row2"><span>اجرت ساخت</span><b>'+usd(fee)+'</b></div>'
    +(t?'<div class="row2"><span>مالیات / سود فروشنده</span><b>'+usd(tax)+'</b></div>':'')+'<div class="row2 tot"><span>قیمت تقریبی</span><b>'+usd(tot)+'</b></div>'}
function dcaCard(){var y0=new Date().getFullYear(),o='';for(var y=y0-1;y>=y0-20;y--)o+='<option value="'+y+'"'+(y===y0-10?' selected':'')+'>'+fa(y)+'</option>';
  return '<div class="card"><h3>📅 اگر از … هر ماه خریده بودم</h3><div class="calc">'
  +'<label>هر ماه (دلار)<input id="rzg-da" type="number" min="1" step="10" value="100"></label><label>از سال<select id="rzg-dy">'+o+'</select></label></div><div class="res" id="rzg-dr"></div>'
  +'<p class="src">خرید در اولین هفته‌ی هر ماه با قیمت همان روز، بدون کارمزد و مالیات. بازده گذشته تضمینی برای آینده نیست.</p></div>'}
function dca(){var a=+$('rzg-da').value||0,y=$('rzg-dy').value,A=[['gold','طلا'],['silver','نقره'],['spx','S&amp;P 500'],['btc','بیت‌کوین']],res=[],inv=0;
  A.forEach(function(x){var W=((D.w||{})[x[0]])||[],u=0,n=0,seen={},first=null;W.forEach(function(r){if(r[0]<y+'-01-01')return;var m=r[0].slice(0,7);if(seen[m])return;seen[m]=1;if(!first)first=r[0];u+=a/r[1];n++});
    var last=W[W.length-1];if(!n||!last||first>y+'-02-15'){res.push([x[1],null]);return}inv=Math.max(inv,n*a);res.push([x[1],u*last[1],n*a])});
  $('rzg-dr').innerHTML='<div class="row2"><span>کل پول خرج‌شده</span><b>'+usd(inv,0)+'</b></div>'+res.map(function(r){if(r[1]==null)return '<div class="row2"><span>'+r[0]+'</span><b class="mut">سابقه‌ی کافی ندارد</b></div>';
    var g=r[1]/r[2]-1;return '<div class="row2"><span>'+r[0]+'</span><b>'+usd(r[1],0)+' <small class="'+cls(g)+'">('+(g>=0?'+':'')+(g*100).toFixed(0)+'%)</small></b></div>'}).join('')}

/* ---------------------------------------------------------------- page */
function render(Q){var M=$('rzg-main');
  var h='<p class="stamp">آخرین به‌روزرسانی: '+esc(when(D.as_of))+' · قیمت‌ها حدود ۱۰ تا ۱۵ دقیقه تأخیر دارند</p>'
    +'<div class="px2">'+priceCard('gold','طلا','🥇')+priceCard('silver','نقره','🥈')+'</div>'
    +(D.note?'<div class="note2">'+esc(D.note)+'<small>یادداشت خودکار بر اساس اعداد امروز؛ توصیه‌ی خرید یا فروش نیست.</small></div>':'')
    +'<div class="card"><h3>📈 نمودار قیمت</h3>'+tabs()+'<div id="rzg-ch"></div><p class="plain" id="rzg-pl"></p></div>'
    +'<div class="two2">'+ratioCard()+calCard()+'</div>'+cmpCard()+drvCard()+minersCard(Q)
    +'<div class="two2">'+jewelCard()+dcaCard()+'</div>'
    +'<p class="note">منابع: قیمت طلا و نقره از قرارداد آتی نزدیک بورس کامکس نیویورک، شاخص S&amp;P 500 و بیت‌کوین از بازار جهانی، تورم از اداره‌ی آمار کار آمریکا. همه‌ی قیمت‌ها به دلار. این صفحه آموزشی است و توصیه‌ی سرمایه‌گذاری نیست.</p>';
  M.innerHTML=h;drawChart();jewel();dca();
  $('rzg-m').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;if(b.dataset.m)ST.m=b.dataset.m;if(b.dataset.r)ST.r=b.dataset.r;
    [].forEach.call(this.querySelectorAll('button'),function(x){x.classList.toggle('on',x.dataset.m?x.dataset.m===ST.m:x.dataset.r===ST.r)});drawChart();if(window.rzE)rzE('gold',ST.m,ST.r)});
  ['rzg-jw','rzg-jk','rzg-jf','rzg-jt'].forEach(function(i){$(i).addEventListener('input',jewel)});['rzg-da','rzg-dy'].forEach(function(i){$(i).addEventListener('input',dca)});
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(drawChart,200)})}
Promise.all([fetch(RAW+'/gold/gold.json?v='+Math.floor(Date.now()/300000)).then(function(r){if(!r.ok)throw 0;return r.json()}),liveQuotes().catch(function(){return null})])
  .then(function(a){D=a[0];render(a[1])})
  .catch(function(){$('rzg-main').innerHTML='<div class="card empty">بارگذاری داده‌ها ناموفق بود؛ چند لحظه بعد صفحه رو دوباره باز کن.</div>'});
