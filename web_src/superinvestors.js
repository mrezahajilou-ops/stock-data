/* Super investors (13F). Data: branch "superinvestors" (built daily by superinvestors.py from SEC filings). */
var ACC=!!window.RZS_ACCESS,SUB=window.RZS_SUB_URL||'/products/stock-data-pro',FREE={buffett:1};
var D=null,M={},BYID={},OWN=null,TAB='mgr',STY='all',SORT='value',Q='',HF='all',HS='w',BS='buys';
var SI=RAW+'/superinvestors/';
var STYLES=[['all','همه'],['ارزشی','ارزشی'],['کیفیت','کیفیت'],['رشد','رشد و تکنولوژی'],['فعال','اکتیویست'],['کلان','کلان']];
var COL=['#2ec4b6','#b5e36b','#f5b700','#7ab8ff','#ff9f6b','#c9a7ff','#5ef0d2','#ffd36b','#9fe39a','#ff8fb1'];
function hc(s){var h=0;for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))>>>0;return COL[h%COL.length]}
function ini(m){var p=String(m.who||m.firm).replace(/[^A-Za-z ]/g,' ').trim().split(/\s+/);return ((p[0]||'?')[0]+(p.length>1?p[p.length-1][0]:'')).toUpperCase()}
function av(m,c){return '<span class="av'+(c?' '+c:'')+'" style="background:'+hc(m.id)+'">'+ini(m)+'</span>'}
function qn(p){if(!p)return '';var m=+p.slice(5,7);return 'Q'+Math.ceil(m/3)+' '+p.slice(0,4)}
function fd(s){try{return new Date(s+'T12:00:00Z').toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'})}catch(e){return s}}
function w(v,d){return v==null?'—':(v*100).toFixed(d==null?1:d)+'%'}
function sgn(v,d){return v==null||!isFinite(v)?'—':(v>=0?'+':'')+(v*100).toFixed(d==null?1:d)+'%'}
function shn(n){if(n==null)return '—';var a=Math.abs(n);return a>=1e9?(n/1e9).toFixed(2)+'B':a>=1e6?(n/1e6).toFixed(2)+'M':a>=1e4?(n/1e3).toFixed(1)+'K':Math.round(n).toLocaleString('en-US')}
function badge(a,c){if(a==='new')return '<span class="b new">خرید جدید</span>';if(a==='add')return '<span class="b add">افزایش '+(c!=null?'<span class="num">'+w(c,0)+'</span>':'')+'</span>';if(a==='cut')return '<span class="b cut">کاهش '+(c!=null?'<span class="num">'+w(c,0)+'</span>':'')+'</span>';if(a==='sold')return '<span class="b sold">فروش کامل</span>';return '<span class="mut" style="font-size:12px">بدون تغییر</span>'}
function tkl(t,u){if(!t)return '<span class="mut">—</span>';return u?'<a class="tk" href="/pages/stock#'+esc(t)+'">'+esc(t)+'</a>':'<span class="tk">'+esc(t)+'</span>'}
function bigv(v){return v!=null&&Math.abs(v)<1e6?'$'+(v/1e3).toFixed(0)+'K':big(v)}
function live(t){var q=RZQ&&RZQ.q&&t?RZQ.q[t]:null;return q&&q[0]>0?q[0]:null}
function can(id){return ACC||FREE[id]}
function cta(t){return '<div class="cta-box"><h3>🔒 '+(t||'این بخش مخصوص مشترکین Stock Pro است')+'</h3><p>پورتفوی کامل و خرید و فروش هر فصل بیش از ۵۰ سرمایه‌گذار افسانه‌ای، پرطرفدارترین سهم‌هاشون و اینکه چه کسی چه سهمی رو داره.</p><a class="btn" href="'+esc(SUB)+'">اشتراک Stock Pro</a>'+(window.RZS_LOGGED?'':'<p style="margin:12px 0 0;font-size:13px">قبلاً مشترک شدی؟ <a href="/account/login?return_url=%2Fpages%2Fsuperinvestors">وارد حسابت شو</a></p>')+'</div>'}
function locked(inner,t){return '<div class="lockw"><div class="blur">'+inner+'</div><div class="cta">'+cta(t)+'</div></div>'}
function mlink(id){var m=BYID[id];return m?'<span data-m="'+id+'">'+av(m)+esc(m.fa)+'</span>':''}

/* ------------------------------------------------------------- list views */
function tabs(){return '<div class="tabs">'+[['mgr','👤 سرمایه‌گذارها'],['pop','🏆 محبوب‌ترین سهم‌ها'],['act','🔄 خرید و فروش فصل'],['who','🔎 این سهم دست کیه؟'],['feed','🗓️ آخرین گزارش‌ها']].map(function(t){return '<button data-tab="'+t[0]+'"'+(TAB===t[0]?' class="on"':'')+'>'+t[1]+'</button>'}).join('')+'</div>'}
function mgrList(){var L=D.managers.filter(function(m){if(STY!=='all'&&String(m.style).indexOf(STY)<0)return false;if(!Q)return true;var s=(m.who+' '+m.firm+' '+m.fa+' '+m.ffa).toLowerCase();return s.indexOf(Q.toLowerCase())>=0});
  L=L.slice().sort(function(a,b){return SORT==='filed'?(b.filed>a.filed?1:-1):SORT==='buys'?((b.nnew+b.nadd)-(a.nnew+a.nadd)):SORT==='conc'?b.top10-a.top10:b.value-a.value});
  var h='<div class="bar"><input id="rzi-q" placeholder="جستجوی اسم سرمایه‌گذار یا صندوق…" value="'+esc(Q)+'"><select id="rzi-sort"><option value="value"'+(SORT==='value'?' selected':'')+'>بزرگ‌ترین پورتفوی</option><option value="filed"'+(SORT==='filed'?' selected':'')+'>تازه‌ترین گزارش</option><option value="buys"'+(SORT==='buys'?' selected':'')+'>بیشترین خرید این فصل</option><option value="conc"'+(SORT==='conc'?' selected':'')+'>متمرکزترین پورتفوی</option></select></div>'+
    '<div class="chips" style="margin:0 0 12px">'+STYLES.map(function(s){return '<span class="chip'+(STY===s[0]?' on':'')+'" data-sty="'+s[0]+'" style="direction:rtl">'+s[1]+'</span>'}).join('')+'</div>';
  if(!L.length)return h+'<div class="card empty">موردی پیدا نشد.</div>';
  return h+'<div class="mgrs">'+L.map(function(m){return '<a class="mg" href="#m='+m.id+'" data-m="'+m.id+'"><div class="hd">'+av(m)+'<div class="who"><b>'+esc(m.fa)+'</b><span>'+esc(m.ffa)+' · <span dir="ltr">'+esc(m.who)+'</span></span></div></div>'+
    '<div><span class="tag">'+esc(m.style)+'</span> '+(m.stale?'<span class="tag old">گزارش قدیمی</span>':'')+(FREE[m.id]&&!ACC?' <span class="tag" style="background:#2a4a1a;color:#b5e36b">رایگان</span>':'')+'</div>'+
    '<div class="kv"><span>ارزش پورتفوی</span><b>'+big(m.value)+'</b></div><div class="kv"><span>تعداد سهم</span><b>'+m.n+'</b></div><div class="kv"><span>آخرین گزارش</span><b>'+qn(m.period)+'</b></div>'+
    '<div class="tops">'+m.top.slice(0,4).map(function(t){return '<span class="tp">'+esc(t[0]||t[1].slice(0,10))+'<i>'+w(t[2],0)+'</i></span>'}).join('')+'</div>'+
    '<div class="acts">'+(m.nnew?'<span class="b new">'+m.nnew+' جدید</span>':'')+(m.nadd?'<span class="b add">'+m.nadd+' افزایش</span>':'')+(m.ncut?'<span class="b cut">'+m.ncut+' کاهش</span>':'')+(m.nsold?'<span class="b sold">'+m.nsold+' فروش کامل</span>':'')+'</div></a>'}).join('')+'</div>'}
function popList(){var L=D.popular.slice(0,60);
  var rows=function(L){return '<div class="card"><div class="tw"><table><thead><tr><th>#</th><th style="text-align:right">سهم</th><th>تعداد سرمایه‌گذار</th><th>میانگین وزن</th><th>قیمت</th><th style="text-align:right">چه کسانی دارن</th></tr></thead><tbody>'+
    L.map(function(r,i){var p=live(r.t);return '<tr><td class="mut">'+(i+1)+'</td><td>'+tkl(r.t,r.u)+'<div class="nm">'+esc(r.n)+'</div></td><td style="text-align:center"><b style="font-size:16px">'+r.k+'</b></td><td class="num" style="text-align:center">'+w(r.sw/r.k)+'</td><td class="num">'+(p?'$'+p.toFixed(2):'—')+'</td>'+
      '<td><div class="own">'+r.o.slice(0,6).map(function(o){var m=BYID[o[0]];return m?'<span data-m="'+o[0]+'" title="'+esc(m.fa)+'">'+av(m)+'<b class="num">'+w(o[1])+'</b></span>':''}).join('')+(r.o.length>6?'<span class="mut" style="cursor:default">+'+(r.o.length-6)+'</span>':'')+'</div></td></tr>'}).join('')+'</tbody></table></div></div>'};
  var h='<div class="info" style="margin-bottom:12px">سهم‌هایی که بیشترین تعداد از '+D.managers.filter(function(m){return !m.stale}).length+' سرمایه‌گذار در آخرین گزارش‌شون داشتن. وزن = درصدی از پورتفوی هر سرمایه‌گذار که به این سهم اختصاص داده.</div>';
  return h+(ACC?rows(L):rows(L.slice(0,5))+locked(rows(L.slice(5,15)),'۵۵ سهم بعدی مخصوص مشترکین است'))}
function actList(){var L=(BS==='buys'?D.buys:D.sells).slice(0,50),buy=BS==='buys';
  var rows=function(L){return '<div class="card"><div class="tw"><table><thead><tr><th>#</th><th style="text-align:right">سهم</th><th>تعداد سرمایه‌گذار</th><th>'+(buy?'خرید جدید':'فروش کامل')+'</th><th>قیمت</th><th style="text-align:right">چه کسانی</th></tr></thead><tbody>'+
    L.map(function(r,i){var p=live(r.t);return '<tr><td class="mut">'+(i+1)+'</td><td>'+tkl(r.t,r.u)+'<div class="nm">'+esc(r.n)+'</div></td><td style="text-align:center"><b style="font-size:16px">'+r.k+'</b></td><td style="text-align:center">'+(buy?r['new']:r.sold)+'</td><td class="num">'+(p?'$'+p.toFixed(2):'—')+'</td>'+
      '<td><div class="own">'+r.o.slice(0,6).map(function(o){var m=BYID[o[0]];return m?'<span data-m="'+o[0]+'" title="'+esc(m.fa)+'">'+av(m)+'<small class="'+(buy?'up':'dn')+'">'+({'new':'جدید','add':'افزایش','cut':'کاهش','sold':'فروش کامل'})[o[1]]+'</small></span>':''}).join('')+(r.o.length>6?'<span class="mut" style="cursor:default">+'+(r.o.length-6)+'</span>':'')+'</div></td></tr>'}).join('')+'</tbody></table></div></div>'};
  var h='<div class="bar"><div class="seg"><button data-bs="buys"'+(buy?' class="on"':'')+'>🟢 بیشترین خرید</button><button data-bs="sells"'+(!buy?' class="on"':'')+'>🔴 بیشترین فروش</button></div><span class="mut" style="font-size:13px">بر اساس آخرین گزارش فصلی هر سرمایه‌گذار (بیشتر '+qn(D.latest)+')</span></div>';
  return h+(ACC?rows(L):rows(L.slice(0,3))+locked(rows(L.slice(3,13)),'لیست کامل مخصوص مشترکین است'))}
function whoView(){var h='<div class="card"><h3>کدوم سوپرسرمایه‌گذارها این سهم رو دارن؟</h3><div class="search"><input id="rzi-t" placeholder="نماد سهم، مثلاً AAPL یا META" autocomplete="off" style="width:100%;direction:ltr;text-align:right"></div><div class="chips">'+D.popular.slice(0,8).map(function(r){return '<span class="chip" data-who="'+esc(r.t)+'">'+esc(r.t)+'</span>'}).join('')+'</div></div><div id="rzi-wr"></div>';return h}
function whoRes(t){t=String(t||'').trim().toUpperCase();var el=$('rzi-wr');if(!el||!t)return;
  var go=function(){var L=(OWN&&OWN[t])||[];if(!L.length){el.innerHTML='<div class="card empty">هیچ‌کدوم از سرمایه‌گذارهای این بخش در آخرین گزارش‌شون <b class="tk">'+esc(t)+'</b> نداشتن.</div>';return}
    var body='<div class="card"><h3><span class="tk">'+esc(t)+'</span> در پورتفوی '+L.length+' سرمایه‌گذار</h3><div class="tw"><table><thead><tr><th style="text-align:right">سرمایه‌گذار</th><th>وزن در پورتفوی</th><th>آخرین فعالیت</th></tr></thead><tbody>'+
      L.map(function(o){var m=BYID[o[0]];if(!m)return '';return '<tr style="cursor:pointer" data-m="'+o[0]+'"><td><div style="display:flex;gap:8px;align-items:center">'+av(m)+'<div><b style="color:#fff">'+esc(m.fa)+'</b><div class="nm">'+esc(m.ffa)+'</div></div></div></td><td class="num" style="text-align:center"><b>'+w(o[1])+'</b></td><td style="text-align:center">'+badge(o[2])+'</td></tr>'}).join('')+'</tbody></table></div></div>';
    el.innerHTML=ACC?body:'<div class="card"><h3><span class="tk">'+esc(t)+'</span> در پورتفوی '+L.length+' سرمایه‌گذار</h3></div>'+locked(body,'اسم‌ها مخصوص مشترکین است')};
  if(OWN)go();else{el.innerHTML='<div class="card empty">در حال بارگذاری…</div>';fetch(SI+'owners.json?v='+encodeURIComponent(D.as_of)).then(function(r){return r.json()}).then(function(j){OWN=j;go()}).catch(function(){el.innerHTML='<div class="card empty">بارگذاری ناموفق بود.</div>'})}}
function feedView(){var L=D.managers.slice().sort(function(a,b){return b.filed>a.filed?1:-1}).slice(0,30);
  return '<div class="card feed">'+L.map(function(m){return '<div class="ev" data-m="'+m.id+'">'+av(m)+'<div class="who"><b>'+esc(m.fa)+'</b> <span class="mut">· '+esc(m.ffa)+'</span><div class="acts" style="margin-top:3px">گزارش '+qn(m.period)+' · '+(m.nnew?'<span class="b new">'+m.nnew+' جدید</span>':'')+(m.nadd?'<span class="b add">'+m.nadd+' افزایش</span>':'')+(m.ncut?'<span class="b cut">'+m.ncut+' کاهش</span>':'')+(m.nsold?'<span class="b sold">'+m.nsold+' فروش</span>':'')+'</div></div><span class="mut" style="font-size:12.5px;white-space:nowrap">'+fd(m.filed)+'</span></div>'}).join('')+'</div>'}

/* ------------------------------------------------------------- one manager */
function spark(h){var v=h.slice().reverse(),mx=Math.max.apply(null,v)||1,W=74,H=22,n=v.length;if(n<2)return '';
  var pts=v.map(function(x,i){return (i*(W-2)/(n-1)+1).toFixed(1)+','+(H-2-(x/mx)*(H-4)).toFixed(1)}).join(' ');
  return '<svg class="sp" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'"><polyline points="'+pts+'" fill="none" stroke="#2ec4b6" stroke-width="1.6"/></svg>'}
function mgrView(id){var m=M[id],s=BYID[id];
  if(!m){$('rzi-main').innerHTML='<div class="card empty">در حال بارگذاری…</div>';fetch(SI+'m/'+id+'.json?v='+encodeURIComponent(D.as_of)).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(j){M[id]=j;mgrView(id)}).catch(function(){$('rzi-main').innerHTML='<div class="card empty">بارگذاری ناموفق بود.</div>'});return}
  var head='<button class="back" data-back="1">→ بازگشت به همه‌ی سرمایه‌گذارها</button><div class="card"><div class="mh">'+av(m,'lg')+'<div class="who"><b>'+esc(m.fa)+'</b><span class="mut">'+esc(m.ffa)+' · <span dir="ltr">'+esc(m.who)+(m.who!==m.firm?' — '+esc(m.firm):'')+'</span></span><div style="margin-top:6px"><span class="tag">'+esc(m.style)+'</span> '+(m.stale?'<span class="tag old">آخرین گزارش قدیمیه</span>':'')+'</div><p>'+esc(m.bio)+'</p></div></div>'+
    '<div class="stats"><div><small>ارزش پورتفوی</small><b>'+big(m.value)+'</b></div><div><small>تعداد سهم</small><b>'+m.n+'</b></div><div><small>تغییر ارزش در فصل</small><b class="'+((m.chg||0)>=0?'up':'dn')+'">'+sgn(m.chg)+'</b></div><div><small>وزن ۱۰ سهم اول</small><b>'+w(m.top10,0)+'</b></div><div><small>گردش پورتفوی</small><b>'+(m.turn==null?'—':w(m.turn,0))+'</b></div><div><small>گزارش فصل</small><b>'+qn(m.period)+'</b></div></div>'+
    '<p class="note">تاریخ ثبت گزارش در SEC: '+fd(m.filed)+' · این‌ها دارایی‌ها در پایان '+qn(m.period)+' هستن، نه امروز.</p></div>';
  if(!can(id)){$('rzi-main').innerHTML=head+locked(holdTable(m,true),'پورتفوی کامل '+esc(m.fa)+' مخصوص مشترکین است');return}
  var top='<div class="card"><h3>۱۰ سهم بزرگ</h3>'+m.hold.slice(0,10).map(function(h){var mx=m.hold[0].w||1;return '<div class="wb"><span class="tk">'+esc(h.t||'—')+'</span><div class="tr"><i style="width:'+(h.w/mx*100).toFixed(1)+'%"></i></div><span class="num">'+w(h.w)+'</span></div>'}).join('')+'</div>';
  var qs=m.q.slice().reverse(),mx=Math.max.apply(null,qs.map(function(q){return q.v}))||1;
  var hist='<div class="card"><h3>ارزش پورتفوی در '+qs.length+' فصل اخیر</h3><div class="qb">'+qs.map(function(q){return '<div><b>'+big(q.v)+'</b><i style="height:'+Math.max(3,q.v/mx*100).toFixed(1)+'%"></i><small>'+qn(q.p)+'</small></div>'}).join('')+'</div><p class="note">تغییر ارزش هم شامل حرکت قیمت سهم‌هاست و هم خرید و فروش؛ این بازده واقعی صندوق نیست.</p></div>';
  $('rzi-main').innerHTML=head+'<div class="grid2">'+top+hist+'</div>'+holdTable(m)+soldTable(m)+optTable(m)}
function holdTable(m,fake){var L=m.hold.slice();
  if(!fake){if(HF!=='all')L=L.filter(function(h){return h.a===HF});
    L.sort(function(a,b){if(HS==='ret'){var ra=live(a.t)&&a.px?live(a.t)/a.px:-9,rb=live(b.t)&&b.px?live(b.t)/b.px:-9;return rb-ra}if(HS==='chg')return Math.abs(b.e||0)-Math.abs(a.e||0);return b.w-a.w})}
  else L=L.slice(0,12);
  var cnt=function(a){return m.hold.filter(function(h){return h.a===a}).length};
  var mxw=m.hold.length?m.hold[0].w:1;
  var h='<div class="card"><div class="chd"><h3>دارایی‌ها ('+m.n+' سهم)</h3><div class="seg" id="rzi-hf">'+[['all','همه'],['new','خرید جدید ('+cnt('new')+')'],['add','افزایش ('+cnt('add')+')'],['cut','کاهش ('+cnt('cut')+')']].map(function(x){return '<button data-hf="'+x[0]+'"'+(HF===x[0]?' class="on"':'')+'>'+x[1]+'</button>'}).join('')+'</div></div>'+
    '<div class="tw"><table><thead><tr><th style="text-align:right">سهم</th><th class="s" data-hs="w">وزن در پورتفوی '+(HS==='w'?'▼':'')+'</th><th class="s" data-hs="chg">فعالیت '+qn(m.period)+' '+(HS==='chg'?'▼':'')+'</th><th>تعداد سهام</th><th>ارزش</th><th>قیمت پایان فصل</th><th>قیمت الان</th><th class="s" data-hs="ret">تغییر از اون موقع '+(HS==='ret'?'▼':'')+'</th><th>روند تعداد سهام</th></tr></thead><tbody>';
  if(!L.length)h+='<tr><td colspan="9" class="empty">موردی نیست.</td></tr>';
  L.forEach(function(x){var p=live(x.t),r=p&&x.px?p/x.px-1:null;
    h+='<tr><td>'+tkl(x.t,x.u)+'<div class="nm">'+esc(x.n)+'</div></td><td><div class="w"><span class="num"><b>'+w(x.w)+'</b></span><i style="width:'+Math.max(2,x.w/mxw*60).toFixed(0)+'px"></i></div></td><td style="text-align:center">'+badge(x.a,x.c)+(x.e?'<div class="mut num" style="font-size:11px">'+sgn(x.e,2)+' پورتفوی</div>':'')+'</td>'+
      '<td class="num" style="text-align:center">'+shn(x.sh)+'</td><td class="num" style="text-align:center">'+bigv(x.v)+'</td><td class="num" style="text-align:center">'+(x.px?'$'+x.px.toFixed(2):'—')+'</td><td class="num" style="text-align:center">'+(p?'$'+p.toFixed(2):'—')+'</td><td class="num '+(r==null?'':r>=0?'up':'dn')+'" style="text-align:center">'+sgn(r)+'</td><td>'+spark(x.h)+'</td></tr>'});
  h+='</tbody></table></div>'+(m.more?'<p class="note">'+m.more+' موقعیت کوچک‌تر دیگه هم هست که اینجا نشون داده نمیشه.</p>':'')+'<p class="note">«قیمت پایان فصل» = ارزش گزارش‌شده تقسیم بر تعداد سهام در آخرین روز فصل؛ قیمت خرید واقعی سرمایه‌گذار نیست.</p></div>';return h}
function soldTable(m){if(!m.sold||!m.sold.length)return '';
  return '<div class="card"><h3>🔴 فروش کامل در '+qn(m.period)+' ('+m.sold.length+')</h3><div class="tw"><table><thead><tr><th style="text-align:right">سهم</th><th>وزن در فصل قبل</th><th>تعداد سهام فروخته‌شده</th><th>قیمت پایان فصل قبل</th><th>قیمت الان</th></tr></thead><tbody>'+
    m.sold.map(function(x){var p=live(x.t);return '<tr><td>'+tkl(x.t,x.u)+'<div class="nm">'+esc(x.n)+'</div></td><td class="num" style="text-align:center">'+w(x.w)+'</td><td class="num" style="text-align:center">'+shn(x.sh)+'</td><td class="num" style="text-align:center">'+(x.px?'$'+x.px.toFixed(2):'—')+'</td><td class="num" style="text-align:center">'+(p?'$'+p.toFixed(2):'—')+'</td></tr>'}).join('')+'</tbody></table></div></div>'}
function optTable(m){if(!m.opt||!m.opt.length)return '';
  return '<div class="card"><h3>قراردادهای اختیار معامله (آپشن)</h3><div class="tw"><table><thead><tr><th style="text-align:right">سهم</th><th>نوع</th><th>ارزش سهام پایه</th><th>تعداد سهام پایه</th></tr></thead><tbody>'+
    m.opt.map(function(x){return '<tr><td>'+tkl(x.t,1)+'<div class="nm">'+esc(x.n)+'</div></td><td style="text-align:center">'+(x.pc==='PUT'?'<span class="b cut">پوت (شرط ریزش)</span>':'<span class="b add">کال (شرط رشد)</span>')+'</td><td class="num" style="text-align:center">'+bigv(x.v)+'</td><td class="num" style="text-align:center">'+shn(x.sh)+'</td></tr>'}).join('')+'</tbody></table></div><p class="note">ارزش آپشن‌ها در 13F ارزش سهام پایه است، نه مبلغ پرداختی برای قرارداد.</p></div>'}

/* ------------------------------------------------------------- router */
function route(){var h=decodeURIComponent((location.hash||'').slice(1)),mm=h.match(/^m=([\w-]+)/),tt=h.match(/^t=([\w.-]+)/);
  if(mm&&BYID[mm[1]]){HF='all';HS='w';mgrView(mm[1]);window.scrollTo({top:Math.max(0,$('rzi').offsetTop-20)});return}
  if(tt){TAB='who'}else if(/^(mgr|pop|act|who|feed)$/.test(h))TAB=h;
  var body=TAB==='pop'?popList():TAB==='act'?actList():TAB==='who'?whoView():TAB==='feed'?feedView():mgrList();
  $('rzi-main').innerHTML=tabs()+body+'<div class="info" style="margin-top:14px"><b>این داده‌ها از کجا میاد؟</b> مدیرانی که بیش از ۱۰۰ میلیون دلار سهام آمریکایی دارن باید هر فصل حداکثر ۴۵ روز بعد از پایان فصل، فرم 13F رو به کمیسیون بورس آمریکا (SEC) بدن. پس این پورتفوی‌ها تا حدود ۴۵ تا ۱۳۵ روز عقب‌تر از امروزن و فقط سهام و آپشن‌های بورس آمریکا رو نشون میدن (بدون پول نقد، فروش استقراضی و سهام خارج از آمریکا). به‌روزرسانی خودکار هر روز. آخرین به‌روزرسانی: '+liveWhen(D.as_of.replace('Z',':00Z'))+'.</div><p class="note">این بخش آموزشیه و پیشنهاد خرید یا فروش نیست؛ کپی کردن کورکورانه‌ی معاملات دیگران با تأخیر ۴۵ روزه می‌تونه پرریسک باشه.</p>';
  if(TAB==='who'&&tt){$('rzi-t').value=tt[1];whoRes(tt[1])}}
document.getElementById('rzi').addEventListener('click',function(e){var x=e.target.closest('[data-tab],[data-m],[data-sty],[data-bs],[data-hf],[data-hs],[data-back],[data-who]');if(!x)return;
  if(x.dataset.m){e.preventDefault();location.hash='m='+x.dataset.m;return}
  if(x.dataset.tab){TAB=x.dataset.tab;try{history.replaceState(null,'','#'+TAB)}catch(_){}route();return}
  if(x.dataset.back){location.hash=TAB;return}
  if(x.dataset.sty){STY=x.dataset.sty;route();return}
  if(x.dataset.bs){BS=x.dataset.bs;route();return}
  if(x.dataset.who){$('rzi-t').value=x.dataset.who;whoRes(x.dataset.who);return}
  var id=(location.hash.match(/m=([\w-]+)/)||[])[1];if(!id)return;
  if(x.dataset.hf){HF=x.dataset.hf;mgrView(id)}else if(x.dataset.hs){HS=x.dataset.hs;mgrView(id)}});
document.getElementById('rzi').addEventListener('input',function(e){if(e.target.id==='rzi-q'){Q=e.target.value;var p=e.target.selectionStart;route();var i=$('rzi-q');i.focus();try{i.setSelectionRange(p,p)}catch(_){}}});
document.getElementById('rzi').addEventListener('change',function(e){if(e.target.id==='rzi-sort'){SORT=e.target.value;route()}});
document.getElementById('rzi').addEventListener('keydown',function(e){if(e.target.id==='rzi-t'&&e.key==='Enter')whoRes(e.target.value)});
window.addEventListener('hashchange',route);
Promise.all([fetch(SI+'index.json?v='+Math.floor(Date.now()/1800000)).then(function(r){if(!r.ok)throw 0;return r.json()}),liveQuotes()]).then(function(x){D=x[0];D.managers.forEach(function(m){BYID[m.id]=m});route()})
  .catch(function(){$('rzi-main').innerHTML='<div class="card empty">داده‌ها هنوز آماده نیست؛ چند دقیقه بعد دوباره سر بزن.</div>'});
