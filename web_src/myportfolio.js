/* My portfolio: subscribers track their own holdings (stored on this device; backup/restore as a file). */
var ACC=!!window.RZS_ACCESS,SUB=window.RZS_SUB_URL||'/products/stock-data-pro',SUBY=window.RZS_SUB_Y||'/products/stock-data-pro-yearly';
var KEY='rz_myport',TAB='h',SORT='val',CAL=null,OWN=null,SIX=null;
var DEMO={h:[{t:'MSFT',n:12,p:310},{t:'GOOGL',n:30,p:120},{t:'AMZN',n:25,p:135},{t:'V',n:15,p:220},{t:'COST',n:5,p:540},{t:'KO',n:40,p:58},{t:'ASML',n:4,p:650},{t:'NVO',n:20,p:95}],cash:1500};
var SEC_FA={'Technology':'تکنولوژی','Consumer Discretionary':'کالای غیرضروری','Industrials':'صنعتی','Health Care':'سلامت','Finance':'مالی','Telecommunications':'ارتباطات','Energy':'انرژی','Consumer Staples':'کالای اساسی','Basic Materials':'مواد اولیه','Utilities':'خدمات عمومی','Real Estate':'املاک','Miscellaneous':'سایر'};
var PAL=['#2ec4b6','#b5e36b','#f5b700','#7ab8ff','#ff9f6b','#c9a7ff','#5ef0d2','#ffd36b','#9fe39a','#ff8fb1','#8fb3ff','#d6e1ee'];
function load(){if(!ACC)return JSON.parse(JSON.stringify(DEMO));try{var o=JSON.parse(localStorage.getItem(KEY)||'null');if(o&&o.h)return o}catch(e){}return {h:[],cash:0}}
function save(){if(!ACC)return;try{localStorage.setItem(KEY,JSON.stringify({h:P.h,cash:P.cash||0}))}catch(e){}}
var P=load();
function usd(v,d){if(v==null||!isFinite(v))return '—';var s=v<0?'-':'',a=Math.abs(v);return s+'$'+a.toLocaleString('en-US',{minimumFractionDigits:d==null?0:d,maximumFractionDigits:d==null?0:d})}
function sg(v){return v==null||!isFinite(v)?'—':(v>=0?'+':'')+(v*100).toFixed(2)+'%'}
function sgu(v){return v==null||!isFinite(v)?'—':(v>=0?'+':'-')+usd(Math.abs(v))}
function cl(v){return v==null?'':v>=0?'up':'dn'}
function bd(x){return '<span class="num">'+x+'</span>'}
function fn(n){return (Math.round(n*10000)/10000).toLocaleString('en-US')}
function rows(){var tot=P.cash||0,out=P.h.map(function(h){var r=BY[h.t],px=r?g(r,'price'):null,ch=r&&r.chg!=null?r.chg/100:null,val=px?h.n*px:h.n*h.p;
    return {h:h,r:r,t:h.t,name:r?g(r,'n'):h.t,px:px,ch:ch,val:val,cost:h.n*h.p,day:ch!=null?val-val/(1+ch):0,sec:r?g(r,'sector'):null,sc:r?g(r,'s_total'):null,fu:r?g(r,'fair_up'):null,dy:r?g(r,'divy'):null,pe:r?g(r,'pe'):null,sh:r?g(r,'s_health'):null}});
  out.forEach(function(x){tot+=x.val});out.forEach(function(x){x.w=tot?x.val/tot:0});return {L:out,tot:tot}}
function totals(R){var o={val:R.tot,cost:0,gain:0,day:0,div:0,ws:0,wsw:0};R.L.forEach(function(x){o.cost+=x.cost;o.day+=x.day;o.div+=(x.dy||0)*x.val;if(x.sc!=null){o.ws+=x.sc*x.val;o.wsw+=x.val}});
  var inv=R.tot-(P.cash||0);o.gain=inv-o.cost;o.gainp=o.cost?o.gain/o.cost:null;o.dayp=(R.tot-o.day)?o.day/(R.tot-o.day):null;o.score=o.wsw?o.ws/o.wsw:null;o.yld=R.tot?o.div/R.tot:null;return o}

/* ---------------------------------------------------------------- views */
function head(R,o){return '<div class="stats"><div><small>ارزش کل</small><b>'+usd(o.val)+'</b></div><div><small>تغییر امروز</small><b class="'+cl(o.day)+'">'+sgu(o.day)+'</b><em class="'+cl(o.day)+'">'+sg(o.dayp)+'</em></div>'+
  '<div><small>سود / زیان کل</small><b class="'+cl(o.gain)+'">'+sgu(o.gain)+'</b><em class="'+cl(o.gain)+'">'+sg(o.gainp)+'</em></div><div><small>سود نقدی سالانه</small><b>'+usd(o.div)+'</b><em class="mut">'+(o.yld!=null?(o.yld*100).toFixed(2)+'%':'')+'</em></div>'+
  '<div><small>امتیاز میانگین</small><b>'+(o.score==null?'—':o.score.toFixed(1)+' / 5')+'</b></div><div><small>تعداد سهم</small><b>'+R.L.length+'</b></div></div>'}
function tabs(){return '<div class="tabs">'+[['h','📋 سهم‌ها'],['mix','🥧 ترکیب'],['health','🩺 چکاپ پورتفوی'],['div','💵 سود نقدی'],['io','💾 پشتیبان و ورود']].map(function(t){return '<button data-tab="'+t[0]+'"'+(TAB===t[0]?' class="on"':'')+'>'+t[1]+'</button>'}).join('')+'</div>'}
function addForm(){if(!ACC)return '';return '<div class="card"><h3>➕ افزودن سهم</h3><div class="add"><label>نماد یا اسم شرکت<div class="search"><input id="rzm-q" placeholder="مثلاً AAPL" autocomplete="off" style="direction:ltr;text-align:right"><div class="sugg" id="rzm-s"></div></div></label>'+
  '<label>تعداد سهم<input id="rzm-n" inputmode="decimal" placeholder="10" style="direction:ltr"></label><label>میانگین قیمت خرید ($)<input id="rzm-p" inputmode="decimal" placeholder="قیمت فعلی" style="direction:ltr"></label><button class="btn" id="rzm-add">افزودن</button></div>'+
  '<div class="note" id="rzm-msg" style="margin-top:6px">اگه همون سهم رو دوباره اضافه کنی، با میانگین‌گیری به موقعیت قبلی اضافه میشه.</div></div>'}
function table(R){var L=R.L.slice();L.sort(function(a,b){return SORT==='gain'?(b.val-b.cost)/(b.cost||1)-(a.val-a.cost)/(a.cost||1):SORT==='day'?(b.ch||0)-(a.ch||0):SORT==='sc'?(b.sc||0)-(a.sc||0):b.val-a.val});
  if(!L.length)return '<div class="card empty">هنوز سهمی اضافه نکردی. از فرم بالا شروع کن، یا از تب «پشتیبان و ورود» لیستت رو یکجا وارد کن.</div>';
  var own=function(t){var x=OWN&&OWN[t==='GOOG'?'GOOGL':t==='BRK-A'?'BRK-B':t];return x?x.length:0};
  var nx=function(t){if(!CAL)return null;var today=new Date().toISOString().slice(0,10),ds=Object.keys(CAL.days).sort();for(var i=0;i<ds.length;i++){if(ds[i]<today)continue;if(CAL.days[ds[i]].some(function(e){return e.t===t}))return ds[i]}return null};
  var th=function(k,l){return '<th'+(k?' class="s" data-sort="'+k+'" style="cursor:pointer"':'')+'>'+l+(SORT===k?' ▼':'')+'</th>'};
  var h='<div class="card"><div class="tw"><table><thead><tr><th style="text-align:right">سهم</th><th>تعداد</th><th>میانگین خرید</th><th>قیمت</th>'+th('day','امروز')+th('val','ارزش')+'<th>وزن</th>'+th('gain','سود / زیان')+th('sc','امتیاز')+'<th>تا ارزش ذاتی</th><th>سود نقدی</th><th>🦈</th><th>گزارش بعدی</th>'+(ACC?'<th></th>':'')+'</tr></thead><tbody>';
  L.forEach(function(x){var gn=x.val-x.cost,gp=x.cost?gn/x.cost:null,o=own(x.t),e=nx(x.t),ed=P.edit===x.t;
    h+='<tr><td><a class="tk" href="/pages/stock#'+esc(x.t)+'">'+esc(x.t)+'</a><div class="mut" style="font-size:12px;max-width:160px;overflow:hidden;text-overflow:ellipsis">'+esc(x.name)+'</div></td>'+
      (ed?'<td><input id="rzm-en" value="'+x.h.n+'"></td><td><input id="rzm-ep" value="'+x.h.p+'"></td>':'<td class="num">'+fn(x.h.n)+'</td><td class="num">'+usd(x.h.p,2)+'</td>')+
      '<td class="num">'+(x.px?usd(x.px,2):'—')+'</td><td class="num '+cl(x.ch)+'">'+sg(x.ch)+'</td><td class="num"><b>'+usd(x.val)+'</b></td><td class="num">'+(x.w*100).toFixed(1)+'%</td>'+
      '<td class="num '+cl(gn)+'">'+sgu(gn)+'<div style="font-size:11.5px">'+sg(gp)+'</div></td><td style="text-align:center">'+sc(x.sc)+'</td><td class="num '+cl(x.fu)+'">'+(x.fu==null?'—':pct(x.fu,0))+'</td><td class="num">'+(x.dy?(x.dy*100).toFixed(2)+'%':'—')+'</td>'+
      '<td style="text-align:center">'+(o?'<a href="/pages/superinvestors#t='+esc(x.t)+'" title="سوپرسرمایه‌گذارهایی که دارن">'+o+'</a>':'<span class="mut">—</span>')+'</td><td class="num">'+(e?e.slice(5).replace('-','/'):'—')+'</td>'+
      (ACC?'<td style="white-space:nowrap">'+(ed?'<button class="ed" data-ok="'+esc(x.t)+'" title="ذخیره">✔️</button><button class="ed" data-cancel="1" title="لغو">✖️</button>':'<button class="ed" data-edit="'+esc(x.t)+'" title="ویرایش">✏️</button><button class="ed" data-del="'+esc(x.t)+'" title="حذف">🗑️</button>')+'</td>':'')+'</tr>'});
  h+='<tr><td><b>💵 نقد</b></td><td colspan="4">'+(ACC?'<input id="rzm-cash" value="'+(P.cash||0)+'" style="width:110px"> <span class="mut" style="font-size:12px">دلار</span>':'')+'</td><td class="num"><b>'+usd(P.cash||0)+'</b></td><td class="num">'+(R.tot?((P.cash||0)/R.tot*100).toFixed(1)+'%':'—')+'</td><td colspan="'+(ACC?7:6)+'"></td></tr>';
  return h+'</tbody></table></div><p class="note">قیمت‌ها با حدود ۱۵ دقیقه تأخیر به‌روز میشن. 🦈 = تعداد سوپرسرمایه‌گذارهایی که این سهم رو دارن. امتیاز و ارزش ذاتی از تحلیل همین سایته.</p></div>'}
function donut(parts){var tot=parts.reduce(function(a,p){return a+p[1]},0)||1,a0=-Math.PI/2,R=70,r=44,cx=80,cy=80,s='';
  parts.forEach(function(p,i){var a1=a0+p[1]/tot*Math.PI*2,lg=a1-a0>Math.PI?1:0;if(p[1]/tot>0.9995){s+='<circle cx="80" cy="80" r="'+((R+r)/2)+'" fill="none" stroke="'+PAL[i%PAL.length]+'" stroke-width="'+(R-r)+'"/>';a0=a1;return}
    s+='<path d="M'+(cx+R*Math.cos(a0))+' '+(cy+R*Math.sin(a0))+' A'+R+' '+R+' 0 '+lg+' 1 '+(cx+R*Math.cos(a1))+' '+(cy+R*Math.sin(a1))+' L'+(cx+r*Math.cos(a1))+' '+(cy+r*Math.sin(a1))+' A'+r+' '+r+' 0 '+lg+' 0 '+(cx+r*Math.cos(a0))+' '+(cy+r*Math.sin(a0))+'Z" fill="'+PAL[i%PAL.length]+'" stroke="#13233a" stroke-width="1.5"/>';a0=a1});
  return '<div class="donut"><svg width="160" height="160" viewBox="0 0 160 160">'+s+'</svg><div class="leg">'+parts.map(function(p,i){return '<div><i style="background:'+PAL[i%PAL.length]+'"></i><span>'+esc(p[0])+'</span><b>'+(p[1]/tot*100).toFixed(1)+'%</b></div>'}).join('')+'</div></div>'}
function mix(R){if(!R.L.length)return '<div class="card empty">اول چند سهم اضافه کن.</div>';var S={};R.L.forEach(function(x){var k=SEC_FA[x.sec]||x.sec||'نامشخص';S[k]=(S[k]||0)+x.val});if(P.cash)S['نقد']=P.cash;
  var sp=Object.keys(S).map(function(k){return [k,S[k]]}).sort(function(a,b){return b[1]-a[1]});
  var L=R.L.slice().sort(function(a,b){return b.val-a.val}),mx=L[0].w||1;
  return '<div class="grid2"><div class="card"><h3>ترکیب بخش‌ها (صنعت)</h3>'+donut(sp)+'</div><div class="card"><h3>وزن هر سهم</h3>'+L.map(function(x,i){return '<div class="hb"><span class="tk">'+esc(x.t)+'</span><div class="tr"><i style="width:'+(x.w/mx*100).toFixed(1)+'%;background:'+PAL[i%PAL.length]+'"></i></div><span class="num">'+(x.w*100).toFixed(1)+'% · '+usd(x.val)+'</span></div>'}).join('')+'</div></div>'}
function health(R,o){var L=R.L,I=[];if(!L.length)return '<div class="card empty">اول چند سهم اضافه کن تا پورتفوت رو چکاپ کنیم.</div>';
  var add=function(k,ic,t){I.push('<div class="ins '+k+'"><span class="ic">'+ic+'</span><div>'+t+'</div></div>')};
  var big1=L.slice().sort(function(a,b){return b.w-a.w})[0];
  if(big1.w>0.25)add('bad','⚠️','<b>تمرکز زیاد:</b> '+bd(esc(big1.t))+' به‌تنهایی '+bd((big1.w*100).toFixed(0)+'%')+' پورتفوته. اگه این یه سهم ۳۰٪ بریزه، کل پورتفو حدود '+bd((big1.w*30).toFixed(0)+'%')+' ضرر می‌کنه.');
  else if(big1.w>0.15)add('warn','👀','بزرگ‌ترین موقعیتت '+bd(esc(big1.t))+' با '+bd((big1.w*100).toFixed(0)+'%')+' وزنه؛ قابل قبوله ولی حواست بهش باشه.');
  else add('good','✅','هیچ سهمی بیشتر از ۱۵٪ پورتفو نیست؛ ریسک تک‌سهم کنترل‌شده‌ست.');
  var S={};L.forEach(function(x){var k=SEC_FA[x.sec]||x.sec||'نامشخص';S[k]=(S[k]||0)+x.w});var ts=Object.keys(S).sort(function(a,b){return S[b]-S[a]})[0];
  if(S[ts]>0.45)add('warn','🏭','<b>'+esc(ts)+'</b> '+bd((S[ts]*100).toFixed(0)+'%')+' پورتفوته. اگه این صنعت دچار مشکل بشه، بیشتر پورتفو با هم آسیب می‌بینه.');
  else add('good','🧩','پورتفو بین '+Object.keys(S).length+' صنعت پخش شده و بزرگ‌ترینش ('+esc(ts)+') '+bd((S[ts]*100).toFixed(0)+'%')+' وزن داره.');
  if(L.length<5)add('warn','🔢','فقط '+L.length+' سهم داری؛ معمولاً ۸ تا ۲۰ سهم تعادل خوبی بین تمرکز و تنوع میده.');else if(L.length>35)add('warn','🔢',L.length+' سهم داری؛ دنبال کردن این تعداد سخته و پورتفو شبیه شاخص میشه. شاید یه ETF ساده‌تر باشه.');
  if(o.score!=null)add(o.score>=3.5?'good':o.score>=2.8?'warn':'bad',o.score>=3.5?'⭐':'📉','امتیاز وزنی پورتفوت: <b>'+bd(o.score.toFixed(1))+' از ۵</b>'+(o.score>=3.5?'؛ ترکیب شرکت‌های باکیفیت.':'.'));
  var low=L.filter(function(x){return x.sc!=null&&x.sc<2.5});if(low.length)add('bad','🔻','سهم‌هایی با امتیاز پایین (زیر ۲.۵): '+low.map(function(x){return '<a class="tk" href="/pages/stock#'+esc(x.t)+'">'+esc(x.t)+'</a> '+bd(x.sc.toFixed(1))}).join('، ')+'. ارزش داره دوباره دلیل نگه‌داشتنشون رو بررسی کنی.');
  var weak=L.filter(function(x){return x.sh!=null&&x.sh<2});if(weak.length)add('warn','🏦','سلامت مالی ضعیف (بدهی بالا یا نقدینگی کم): '+weak.map(function(x){return '<span class="tk">'+esc(x.t)+'</span>'}).join('، ')+'.');
  var exp=L.filter(function(x){return x.fu!=null&&x.fu<-0.35}),chp=L.filter(function(x){return x.fu!=null&&x.fu>0.2});
  if(exp.length)add('warn','💸','گرون‌تر از ارزش ذاتی (بیش از ۳۵٪ بالاتر، با فرض متوسط DCF): '+exp.map(function(x){return '<a class="tk" href="/pages/dcf#'+esc(x.t)+'">'+esc(x.t)+'</a>'}).join('، ')+'.');
  if(chp.length)add('good','🏷️','زیر ارزش ذاتی (بیش از ۲۰٪ ارزون‌تر): '+chp.map(function(x){return '<a class="tk" href="/pages/dcf#'+esc(x.t)+'">'+esc(x.t)+'</a>'}).join('، ')+'.');
  var ey=0,ew=0;L.forEach(function(x){if(x.pe){ey+=x.w/x.pe;ew+=x.w}});if(ew>0.5){var wpe=ew/ey;add(wpe<18?'good':wpe<30?'warn':'bad','📊','P/E وزنی پورتفوت: حدود <b>'+bd(wpe.toFixed(1))+'</b>'+(wpe<18?'؛ نسبتاً ارزون.':wpe<30?'؛ در حد میانگین بازار آمریکا.':'؛ پورتفو گرون قیمت‌گذاری شده و به رشد زیاد وابسته‌ست.'))}
  if(OWN){var pop=L.map(function(x){var k=x.t==='GOOG'?'GOOGL':x.t==='BRK-A'?'BRK-B':x.t;return [x.t,(OWN[k]||[]).length]}).filter(function(a){return a[1]>=5}).sort(function(a,b){return b[1]-a[1]});
    if(pop.length)add('good','🦈','هم‌مسیر با سوپرسرمایه‌گذارها: '+pop.slice(0,6).map(function(a){return '<a class="tk" href="/pages/superinvestors#t='+esc(a[0])+'">'+esc(a[0])+'</a> ('+a[1]+' نفر)'}).join('، ')+'.')}
  if(CAL){var today=new Date().toISOString().slice(0,10),lim=new Date(Date.now()+14*864e5).toISOString().slice(0,10),up=[];Object.keys(CAL.days).forEach(function(d){if(d<today||d>lim)return;CAL.days[d].forEach(function(e){if(P.h.some(function(h){return h.t===e.t}))up.push([e.t,d])})});
    if(up.length)add('warn','📅','گزارش مالی در ۲ هفته‌ی آینده: '+up.map(function(u){return '<span class="tk">'+esc(u[0])+'</span> '+bd(u[1].slice(5).replace('-','/'))}).join('، ')+'. معمولاً روز گزارش نوسان قیمت بیشتره.')}
  var cw=R.tot?(P.cash||0)/R.tot:0;if(cw>0.3)add('warn','💵',bd((cw*100).toFixed(0)+'%')+' پورتفوت نقده.');
  return '<div class="card"><h3>🩺 چکاپ پورتفوی</h3>'+I.join('')+'<p class="note">این چکاپ خودکار و آموزشیه، نه پیشنهاد خرید یا فروش.</p></div>'}
function divs(R,o){var L=R.L.filter(function(x){return x.dy}).sort(function(a,b){return b.dy*b.val-a.dy*a.val});
  if(!L.length)return '<div class="card empty">هیچ‌کدوم از سهم‌هات سود نقدی پرداخت نمی‌کنن (یا هنوز سهمی اضافه نکردی).</div>';var mx=L[0].dy*L[0].val;
  return '<div class="card"><h3>💵 درآمد سود نقدی</h3><div class="stats" style="grid-template-columns:repeat(3,minmax(0,1fr))"><div><small>سالانه</small><b>'+usd(o.div)+'</b></div><div><small>ماهانه (میانگین)</small><b>'+usd(o.div/12)+'</b></div><div><small>بازده سود نقدی پورتفو</small><b>'+(o.yld*100).toFixed(2)+'%</b></div></div>'+
    L.map(function(x,i){var v=x.dy*x.val;return '<div class="hb"><span class="tk">'+esc(x.t)+'</span><div class="tr"><i style="width:'+(v/mx*100).toFixed(1)+'%;background:'+PAL[i%PAL.length]+'"></i></div><span class="num">'+usd(v)+' · '+(x.dy*100).toFixed(2)+'%</span></div>'}).join('')+
    '<p class="note">بر اساس آخرین سود نقدی سالانه‌ی هر شرکت و قیمت فعلی؛ قبل از کسر مالیات. سود نقدی ممکنه تغییر کنه.</p></div>'}
function io(){if(!ACC)return '<div class="card empty">این بخش برای مشترکین فعاله.</div>';
  return '<div class="grid2"><div class="card"><h3>📥 وارد کردن لیست سهم‌ها</h3><p class="mut" style="font-size:13.5px;margin:0 0 8px">هر خط یک سهم: نماد، تعداد، میانگین قیمت خرید. مثلاً از اکسل یا اپ کارگزاریت کپی کن.</p><textarea id="rzm-csv" placeholder="AAPL, 10, 150&#10;MSFT, 5, 320&#10;KO 20 58"></textarea>'+
    '<div class="bar" style="margin-top:8px"><button class="btn" id="rzm-imp">اضافه کن</button><label class="mut" style="font-size:13px"><input type="checkbox" id="rzm-rep"> جایگزین کل لیست فعلی</label></div><div class="note" id="rzm-imsg"></div></div>'+
    '<div class="card"><h3>💾 پشتیبان</h3><p class="mut" style="font-size:13.5px;margin:0 0 10px">پورتفوت روی همین دستگاه و مرورگر ذخیره میشه. برای انتقال به گوشی یا کامپیوتر دیگه، فایل پشتیبان بگیر و اونجا بازش کن.</p>'+
    '<div class="bar"><button class="btn" id="rzm-exp">⬇ دانلود فایل پشتیبان</button><label class="btn ghost" style="cursor:pointer">⬆ بازگردانی از فایل<input type="file" id="rzm-file" accept=".json,application/json" style="display:none"></label><button class="btn ghost" id="rzm-csvx">⬇ خروجی CSV</button></div>'+
    '<hr style="border:0;border-top:1px solid var(--line);margin:16px 0"><button class="btn ghost sm" id="rzm-clear" style="color:var(--red)!important">پاک کردن کل پورتفو</button></div></div>'}
function draw(){var R=rows(),o=totals(R),b='';
  if(TAB==='h')b=addForm()+table(R);else if(TAB==='mix')b=mix(R);else if(TAB==='health')b=health(R,o);else if(TAB==='div')b=divs(R,o);else b=io();
  $('rzm-main').innerHTML=(ACC?'':'<div class="demo"><div><b>👀 این یه دفترچه‌ی نمونه‌ست</b><p>با اشتراک Stock Pro سهم‌های خودت رو اینجا دنبال کن: سود و زیان لحظه‌ای، چکاپ پورتفو، درآمد سود نقدی، و اینکه کدوم سوپرسرمایه‌گذارها همون سهم‌ها رو دارن.</p></div><div class="bar"><a class="btn" href="'+esc(SUB)+'">ماهانه ۷٫۹۹ یورو</a><a class="btn" style="background:#f5b700" href="'+esc(SUBY)+'">سالانه ۴۷٫۹۴ یورو · ۵۰٪ تخفیف</a></div></div>')+
    head(R,o)+tabs()+b;
  if(TAB==='h'&&ACC){picker($('rzm-q'),$('rzm-s'),function(t){$('rzm-q').value=t;var r=BY[t];$('rzm-p').placeholder=r&&g(r,'price')?g(r,'price').toFixed(2):'';$('rzm-n').focus()})}}
function addH(t,n,p,rep){t=String(t||'').trim().toUpperCase().replace('.','-');n=parseFloat(String(n).replace(',','.'));p=parseFloat(String(p||'').replace(',','.'));
  if(!t||!(n>0))return 'نماد یا تعداد درست نیست';var r=BY[t];if(!(p>0))p=r?g(r,'price'):0;if(!(p>0))return t+': قیمت خرید رو بنویس';
  var e=P.h.filter(function(h){return h.t===t})[0];if(e&&!rep){e.p=(e.n*e.p+n*p)/(e.n+n);e.n+=n}else if(e){e.n=n;e.p=p}else P.h.push({t:t,n:n,p:p});return ''}
document.getElementById('rzm').addEventListener('click',function(e){var x=e.target.closest('button,[data-tab],[data-sort]');if(!x)return;
  if(x.dataset.tab){TAB=x.dataset.tab;draw();return}if(x.dataset.sort){SORT=x.dataset.sort;draw();return}
  if(!ACC)return;
  if(x.id==='rzm-add'){var m=addH($('rzm-q').value,$('rzm-n').value,$('rzm-p').value);if(m){$('rzm-msg').textContent=m;return}save();draw();return}
  if(x.dataset.del){if(!confirm('حذف '+x.dataset.del+'؟'))return;P.h=P.h.filter(function(h){return h.t!==x.dataset.del});save();draw();return}
  if(x.dataset.edit){P.edit=x.dataset.edit;draw();return}if(x.dataset.cancel){delete P.edit;draw();return}
  if(x.dataset.ok){var h=P.h.filter(function(h){return h.t===x.dataset.ok})[0],n=parseFloat($('rzm-en').value),p=parseFloat($('rzm-ep').value);if(h&&n>0&&p>0){h.n=n;h.p=p}delete P.edit;save();draw();return}
  if(x.id==='rzm-imp'){var rep=$('rzm-rep').checked,errs=[],ok=0;if(rep)P.h=[];$('rzm-csv').value.split(/\n+/).forEach(function(l){var a=l.trim().split(/[\s,;\t]+/).filter(Boolean);if(a.length<2)return;var m=addH(a[0],a[1],a[2],rep);if(m)errs.push(m);else ok++});save();draw();TAB='io';draw();$('rzm-imsg').textContent=ok+' سهم اضافه شد'+(errs.length?' · خطا: '+errs.join('، '):'');return}
  if(x.id==='rzm-exp'){dl('my-portfolio.json',JSON.stringify({v:1,h:P.h,cash:P.cash||0},null,1),'application/json');return}
  if(x.id==='rzm-csvx'){var R=rows();dl('my-portfolio.csv','﻿ticker,shares,avg_cost,price,value,gain\n'+R.L.map(function(x){return [x.t,x.h.n,x.h.p,x.px||'',x.val.toFixed(2),(x.val-x.cost).toFixed(2)].join(',')}).join('\n'),'text/csv');return}
  if(x.id==='rzm-clear'){if(confirm('کل پورتفو پاک بشه؟ این کار برگشت نداره (مگه فایل پشتیبان داشته باشی).')){P={h:[],cash:0};save();draw()}return}});
document.getElementById('rzm').addEventListener('change',function(e){if(!ACC)return;if(e.target.id==='rzm-cash'){P.cash=Math.max(0,parseFloat(e.target.value)||0);save();draw()}
  if(e.target.id==='rzm-file'&&e.target.files[0]){var fr=new FileReader();fr.onload=function(){try{var o=JSON.parse(fr.result);if(!o.h)throw 0;P={h:o.h.filter(function(h){return h.t&&h.n>0}),cash:+o.cash||0};save();TAB='h';draw()}catch(_){alert('فایل معتبر نیست')}};fr.readAsText(e.target.files[0])}});
document.getElementById('rzm').addEventListener('keydown',function(e){if(e.key==='Enter'&&(e.target.id==='rzm-n'||e.target.id==='rzm-p'))$('rzm-add').click()});
function dl(name,text,type){var b=new Blob([text],{type:type}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(u);a.remove()},500)}
var get=function(u){return fetch(u).then(function(r){return r.ok?r.json():null}).catch(function(){return null})};
loadAll().then(function(){draw();Promise.all([get(RAW+'/calendar/earnings.json?v='+Math.floor(Date.now()/3600000)),get(RAW+'/superinvestors/owners.json?v='+Math.floor(Date.now()/3600000))]).then(function(x){CAL=x[0];OWN=x[1];draw()})})
  .catch(function(){$('rzm-main').innerHTML='<div class="card empty">بارگذاری داده‌ها ناموفق بود؛ صفحه رو دوباره باز کن.</div>'});
setInterval(function(){RZQ_P=null;liveQuotes().then(function(){ROWS.forEach(function(r){liveRow(r)});if(!P.edit&&document.activeElement.tagName!=='INPUT'&&document.activeElement.tagName!=='TEXTAREA')draw()})},300000);
