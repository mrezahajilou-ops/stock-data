/* ---- contest ranking (replaces the weekly-price version) ----
   start price = official close of START (2026-10-30) from the price-history branch ('d' = daily closes)
   current     = live quote while the US market is open, otherwise the latest official close
   final       = official close of END (2026-11-30); a manual override can be put into contest-data as "final": {T: price}
   order       = return desc, then |prediction - actual| asc, then entry time asc (rules: only #1 wins) */
var RAW='https://raw.githubusercontent.com/mrezahajilou-ops/stock-data',XF=null;
function getJ(u){return fetch(u,{cache:'no-store'}).then(function(r){return r.ok?r.json():null}).catch(function(){return null})}
function bust(){return '?t='+Math.floor(Date.now()/300000)}
function series(t){return getJ(RAW+'/prices/'+encodeURIComponent(t)+'.json'+bust())}
function quotes(){return getJ(RAW+'/quotes/quotes.json'+bust())}
function closeOn(j,day,exact){var a=(j&&j.d&&j.d.length)?j.d:((j&&j.w)||[]),r=null;for(var i=0;i<a.length;i++){if(a[i][0]<=day)r=a[i]}if(exact&&r&&r[0]!==day)return null;return r}
function nyDate(iso){try{return new Date(iso).toLocaleDateString('en-CA',{timeZone:'America/New_York'})}catch(e){return String(iso).slice(0,10)}}
function faDate(d){try{return new Date(d+'T12:00:00Z').toLocaleDateString('fa-IR',{day:'numeric',month:'long'})}catch(e){return d}}
function faTime(iso){try{return new Date(iso).toLocaleString('fa-IR',{day:'numeric',month:'long',hour:'2-digit',minute:'2-digit',timeZone:'Europe/Berlin'})+' به وقت آلمان'}catch(e){return iso}}
var ROWS=[],SHOW=30,LAST='',MODE='',STOCKS=[];
function renderRank(E){var box=$('rzk-b-rank');
  if(Date.now()<STARTMS){box.innerHTML='<div class="empty">رتبه‌بندی بعد از بسته‌شدن بازار در روز جمعه ۳۰ اکتبر شروع میشه. ⏳</div>';return}
  if(!E.length){box.innerHTML='<div class="empty">شرکت‌کننده‌ای وجود نداره.</div>';return}
  box.innerHTML='<div class="empty">در حال محاسبه‌ی بازده‌ها…</div>';
  var T={};E.forEach(function(x){T[x.t]=1});var S={};
  Promise.all([quotes()].concat(Object.keys(T).map(function(t){return series(t).then(function(j){S[t]=j})}))).then(function(R){
    var Q=R[0]||{},q=Q.q||{},live=(Q.status==='Open'||Q.status==='After Hours')&&Q.as_of&&(Date.now()-Date.parse(Q.as_of))<6*3600e3;
    var lastClose='';Object.keys(S).forEach(function(t){var c=closeOn(S[t],'9999-12-31');if(c&&c[0]>lastClose)lastClose=c[0]});
    var session=live?nyDate(Q.as_of):lastClose, fin=(XF&&Object.keys(XF).length)||lastClose>=END;
    var P={},st={};
    Object.keys(T).forEach(function(t){var s=closeOn(S[t],START,true);if(!s||!(s[1]>0))return;st[t]=s[1];var c=null;
      if(fin){c=XF&&XF[t]?XF[t]:(closeOn(S[t],END,true)||[])[1]}
      else if(live&&q[t]&&q[t][0]>0){c=q[t][0]}
      else{var l=closeOn(S[t],'9999-12-31');c=l&&l[0]>START?l[1]:(Q.close&&Q.close>START&&q[t]?q[t][0]:s[1])}
      if(c>0)P[t]={s:s[1],c:c,r:c/s[1]-1}});
    MODE=fin?'final':(session<=START?'pre':live?'live':'close');
    LAST=fin?('قیمت‌های پایانی رسمی '+faDate(END)):live?('قیمت لحظه‌ای · '+faTime(Q.as_of)):('قیمت پایانی رسمی '+faDate(session>START?session:START));
    ROWS=E.map(function(x){var p=P[x.t];return {n:x.n,t:x.t,p:x.p,ts:x.ts,h:x.h,s:p?p.s:st[x.t],c:p?p.c:null,r:p?p.r:null,d:p?Math.abs(x.p-p.r*100):1e9}})
      .sort(function(a,b){if(a.r==null&&b.r==null)return a.ts-b.ts;if(a.r==null)return 1;if(b.r==null)return -1;return b.r-a.r||a.d-b.d||a.ts-b.ts});
    var g={};ROWS.forEach(function(r){var k=g[r.t]||(g[r.t]={t:r.t,n:0,r:r.r,s:r.s,c:r.c});k.n++});
    STOCKS=Object.keys(g).map(function(k){return g[k]}).sort(function(a,b){return (b.r==null?-9:b.r)-(a.r==null?-9:a.r)||b.n-a.n});
    if(MODE==='pre')drawPre();else drawRank('')
  }).catch(function(){box.innerHTML='<div class="empty">بارگذاری قیمت‌ها ممکن نشد؛ صفحه رو دوباره باز کن.</div>'})}
function sgn(v){return (v>=0?'+':'')+(v*100).toFixed(2)+'%'}
function usd(v){return v==null?'—':'$'+(v>=1000?v.toLocaleString('en-US',{maximumFractionDigits:0}):v.toFixed(2))}
function drawPre(){var box=$('rzk-b-rank');
  box.innerHTML='<div class="kp"><b>همه از صفر شروع کردن 🏁</b><span>قیمت شروع = قیمت پایانی رسمی جمعه ۳۰ اکتبر. بازار آمریکا دوشنبه ۲ نوامبر ساعت ۱۵:۳۰ به وقت آلمان باز میشه و از همون لحظه رتبه‌بندی زنده اینجا نمایش داده میشه.</span></div>'+
  '<div class="sg2">'+STOCKS.map(function(k){var who=ROWS.filter(function(r){return r.t===k.t}).sort(function(a,b){return a.ts-b.ts});return '<div class="sc"><div class="h"><b class="l">'+esc(k.t)+'</b><span>'+esc(SP[k.t]||'')+'</span></div><div class="pz2">قیمت شروع <b class="l">'+usd(k.s)+'</b></div><div class="nm">'+who.map(function(r){return '<span'+(ME&&ME.h&&r.h===ME.h?' class="you"':'')+'>'+esc(r.n)+' <i class="l">'+(r.p>=0?'+':'')+esc(r.p)+'%</i></span>'}).join('')+'</div></div>'}).join('')+'</div>'+
  '<div class="meta">'+fa(ROWS.length)+' شرکت‌کننده · '+fa(STOCKS.length)+' سهم · '+esc(LAST)+'</div>'}
function bars(){var R=ROWS.filter(function(r){return r.r!=null});if(!R.length)return '';var mx=Math.max.apply(null,R.map(function(r){return Math.abs(r.r)}))||0.01,mh=ME&&ME.h;
  return '<div class="ch"><h4>بازده هر شرکت‌کننده</h4>'+R.map(function(r,i){var w=Math.max(1.5,Math.abs(r.r)/mx*50);
    return '<div class="br'+(i===0?' lead':'')+(mh&&r.h===mh?' you':'')+'"><span class="rk">'+fa(i+1)+'</span><span class="nm">'+esc(r.n)+' <i class="l">'+esc(r.t)+'</i></span><span class="tr"><span class="z"></span><b class="'+(r.r>=0?'pos':'neg')+'" style="width:'+w.toFixed(1)+'%"></b></span><span class="v l '+(r.r>=0?'up':'dn')+'">'+sgn(r.r)+'</span></div>'}).join('')+'</div>'}
function podium(){var R=ROWS.filter(function(r){return r.r!=null}).slice(0,3);if(!R.length)return '';var m=['🥇','🥈','🥉'];
  return '<div class="pod">'+R.map(function(r,i){var gap=i===0&&R[1]?'<small>'+((r.r-R[1].r)*100).toFixed(2)+' واحد درصد جلوتر از نفر دوم</small>':i>0?'<small>'+((R[0].r-r.r)*100).toFixed(2)+' واحد درصد تا نفر اول</small>':'';
    return '<div class="pd p'+(i+1)+'"><div class="md">'+m[i]+'</div><b class="pn">'+esc(r.n)+'</b><span class="l pt">'+esc(r.t)+'</span><b class="l pr '+(r.r>=0?'up':'dn')+'">'+sgn(r.r)+'</b><small>پیش‌بینی: <span class="l">'+(r.p>=0?'+':'')+esc(r.p)+'%</span></small>'+gap+'</div>'}).join('')+'</div>'}
function stockLine(){return '<div class="stk">'+STOCKS.filter(function(k){return k.r!=null}).map(function(k){return '<span><b class="l">'+esc(k.t)+'</b> <i class="l '+(k.r>=0?'up':'dn')+'">'+sgn(k.r)+'</i> <small>'+fa(k.n)+' نفر</small></span>'}).join('')+'</div>'}
function drawRank(q){var box=$('rzk-b-rank'),Q=q.trim().toLowerCase(),lead=ROWS[0]&&ROWS[0].r,mh=ME&&ME.h;
  var list=ROWS.map(function(r,i){r.i=i;return r}).filter(function(r){return !Q||String(r.n).toLowerCase().indexOf(Q)>=0||r.t.toLowerCase()===Q});
  var shown=Q?list:list.slice(0,SHOW),med=['🥇','🥈','🥉'];var mine=mh?ROWS.filter(function(r){return r.h===mh})[0]:null;
  var head=(MODE==='final'?'<div class="kp fin"><b>🏆 نتیجه‌ی نهایی با قیمت‌های پایانی رسمی ۳۰ نوامبر</b><span>برنده بعد از بررسی ثبت‌نام‌ها تا ۷ دسامبر اعلام میشه.</span></div>':MODE==='live'?'<div class="kp live"><b>● زنده</b><span>قیمت‌ها حین باز بودن بازار هر ۱۵ دقیقه به‌روز میشن؛ رتبه‌ی رسمی فقط با قیمت پایانی ۳۰ نوامبر.</span></div>':'');
  box.innerHTML=head+(Q?'':podium())+(mine?'<div class="meta" style="font-size:14.5px;font-weight:800;color:var(--ink);margin:4px 0 10px">📍 رتبه‌ی تو: '+fa(mine.i+1)+' از '+fa(ROWS.length)+' · '+esc(mine.t)+' · '+(mine.r==null?'—':sgn(mine.r))+'</div>':'')+
    (Q?'':bars()+stockLine())+
    '<input class="find" id="rzk-find" placeholder="اسم نمایشی یا نماد سهم رو جستجو کن…" value="'+esc(q)+'">'+
    '<div class="tw"><table><thead><tr><th>رتبه</th><th>شرکت‌کننده</th><th>سهم</th><th>بازده</th><th class="hm">شروع ← الان</th><th>پیش‌بینی</th><th class="hm">فاصله تا نفر اول</th></tr></thead><tbody>'+
    (shown.length?shown.map(function(r){var g=r.r==null?'—':(r.i===0?'نفر اول 👑':(((lead-r.r)*100).toFixed(2)+'٪'));
      return '<tr class="'+(mh&&r.h===mh?'you':(r.i<1?'me':''))+'"><td>'+(med[r.i]||fa(r.i+1))+'</td><td>'+esc(r.n)+'</td><td class="l">'+esc(r.t)+'</td><td class="l '+(r.r>=0?'up':'dn')+'">'+(r.r==null?'—':sgn(r.r))+'</td><td class="l hm">'+usd(r.s)+' → '+usd(r.c)+'</td><td class="l">'+(r.p>=0?'+':'')+esc(r.p)+'%</td><td class="hm">'+g+'</td></tr>'}).join(''):'<tr><td colspan="7" style="text-align:center">پیدا نشد</td></tr>')+
    '</tbody></table></div>'+(!Q&&list.length>SHOW?'<div style="text-align:center;margin-top:10px"><button type="button" class="btn ghost" id="rzk-more">نمایش بیشتر</button></div>':'')+
    '<div class="meta">'+fa(ROWS.length)+' شرکت‌کننده · '+esc(LAST)+' · اگه چند نفر یک سهم داشته باشن، کسی بالاتره که پیش‌بینیش به بازده واقعی نزدیک‌تر باشه.</div>';
  var f=$('rzk-find');f.addEventListener('input',function(){var v=f.value;drawRank(v);var g=$('rzk-find');g.focus();g.setSelectionRange(v.length,v.length)});
  var m=$('rzk-more');if(m)m.addEventListener('click',function(){SHOW+=50;drawRank('')})}
setInterval(function(){if(MODE==='live'&&ENT.length&&document.visibilityState==='visible')renderRank(ENT)},5*60e3);
