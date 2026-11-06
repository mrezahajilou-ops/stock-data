/* ۳۰ سهم برتر — biggest upside to the analysts' average price target. Data: RAW/top30/top30.json (top30.py).
   Candidates are re-ranked with live prices, so the 30 shown are always against the current price.
   Visitors see rank, upside and analyst count; tickers, names and prices are for Stock Pro only. */
var ACC=!!window.RZS_ACCESS,SUB=window.RZS_SUB_URL||'/products/stock-data-pro',SUBY=window.RZS_SUB_Y||'/products/stock-data-pro-yearly';
var REC={strong_buy:'خرید قوی',buy:'خرید',hold:'نگه‌داشتن',underperform:'ضعیف',sell:'فروش'};
var SEC={'Technology':'تکنولوژی','Health Care':'سلامت','Healthcare':'سلامت','Finance':'مالی','Financial Services':'مالی','Industrials':'صنعتی','Energy':'انرژی','Utilities':'خدمات عمومی','Consumer Discretionary':'کالاهای غیرضروری','Consumer Staples':'کالاهای ضروری','Real Estate':'املاک','Basic Materials':'مواد اولیه','Telecommunications':'مخابرات','Communication Services':'ارتباطات','Miscellaneous':'سایر'};
function n2(v){return v==null||!isFinite(v)?'—':v.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}
function usd(v){return '<span class="num">$'+n2(v)+'</span>'}
function upv(v){return '+'+(v*100).toFixed(1)+'%'}
function day(s){try{var d=new Date(s);if(isNaN(d))return '';return d.toLocaleDateString('fa-IR-u-ca-gregory',{day:'numeric',month:'long',year:'numeric'})}catch(e){return ''}}
function cta(){return '<div class="cta-box"><h3>🔒 اسم این ۳۰ سهم مخصوص مشترکین Stock Pro است</h3><p>رتبه و درصد رشد تا قیمت هدف رو همه می‌بینن؛ اسم سهم، قیمت فعلی، قیمت هدف و بازه‌ی نظر تحلیلگرها فقط برای مشترکین باز است. لیست هر روز به‌روز می‌شه.</p>'
  +'<div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap"><a class="btn" href="'+esc(SUB)+'">ماهانه <span class="num">€7.99</span></a><a class="btn" href="'+esc(SUBY)+'">سالانه <span class="num">€47.94</span>، ۵۰٪ تخفیف</a></div>'+'<p style="margin:8px 0 0;font-size:12px;opacity:.75">🔄 تمدید خودکار؛ هر وقت خواستی با یک کلیک لغو کن</p>'
  +(window.RZS_LOGGED?'':'<p style="margin:12px 0 0;font-size:13px">قبلاً مشترک شدی؟ <a href="/account/login?return_url=%2Fpages%2Ftop-30">وارد حسابت شو</a></p>')+'</div>'}
function rng(r){var lo0=r.tlo||r.tgt,hi0=r.thi||r.tgt,lo=Math.min(lo0,r.px,r.tgt),hi=Math.max(hi0,r.px,r.tgt);if(!(hi>lo))return '';
  var pad=(hi-lo)*0.04;lo-=pad;hi+=pad;
  var P=function(x){return (x-lo)/(hi-lo)*100},S=function(x){return P(x).toFixed(1)+'%'},
      side=function(x){var v=P(x);return v<14?' l':v>86?' r':''};
  var gap=r.px<lo0?'<span class="gap" style="left:'+S(r.px)+';width:'+(P(lo0)-P(r.px)).toFixed(1)+'%"></span>':
          r.px>hi0?'<span class="gap" style="left:'+S(hi0)+';width:'+(P(r.px)-P(hi0)).toFixed(1)+'%"></span>':'';
  return '<div class="rg2" dir="ltr"><div class="trk">'+gap+
    '<span class="band" style="left:'+S(lo0)+';width:'+(P(hi0)-P(lo0)).toFixed(1)+'%"></span>'+
    '<span class="end" style="left:'+S(lo0)+'"></span><span class="end" style="left:'+S(hi0)+'"></span>'+
    '<span class="mk px'+side(r.px)+'" style="left:'+S(r.px)+'"><i></i><em dir="rtl">قیمت فعلی <b><bdi dir="ltr">$'+n2(r.px)+'</bdi></b></em></span>'+
    '<span class="mk tg'+side(r.tgt)+'" style="left:'+S(r.tgt)+'"><i></i><em dir="rtl">میانگین هدف <b><bdi dir="ltr">$'+n2(r.tgt)+'</bdi></b></em></span>'+
    '</div><div class="ends"><span dir="rtl">کمترین هدف <b><bdi dir="ltr">$'+n2(lo0)+'</bdi></b></span><span dir="rtl">بیشترین هدف <b><bdi dir="ltr">$'+n2(hi0)+'</bdi></b></span></div></div>'}
function row(r,i){var warn=r.c20!=null&&r.c20<=-0.25?'<span class="warn">⚠️ افت <span class="num">'+Math.round(-r.c20*100)+'%</span> در یک ماه اخیر؛ ممکنه قیمت هدف‌ها هنوز به‌روز نشده باشن</span>':'';
  var sec=SEC[r.sec]||r.sec||'';
  var who=ACC?'<a class="tk" href="/pages/stock#'+esc(r.t)+'">'+esc(r.t)+'</a> <span class="nm">'+esc(r.n)+'</span>'
               :'<span class="locktk">🔒 <span class="lockname"></span></span>';
  var meta='<div class="meta">'+(ACC?'<span>قیمت فعلی '+usd(r.px)+'</span><span>میانگین هدف <b>'+usd(r.tgt)+'</b></span>':'')
    +'<span><b class="num">'+r.na+'</b> تحلیلگر</span>'+(sec?'<span>'+esc(sec)+'</span>':'')+(r.rec&&REC[r.rec]?'<span class="rec">'+REC[r.rec]+'</span>':'')+'</div>';
  return '<div class="row"><div class="rk">'+(i+1)+'</div><div class="who">'+who+'</div>'
    +'<div class="upb"><span class="v">'+upv(r.up)+'</span><span class="l">تا قیمت هدف</span></div>'
    +'<div class="det">'+meta+(ACC?rng(r):'')+(warn?'<div style="margin-top:8px">'+warn+'</div>':'')+'</div></div>'}
function render(D){var L=D.rows.map(function(r){var q=RZQ&&RZQ.q&&RZQ.q[r.t],px=q&&q[0]>0?q[0]:r.px;var o={};for(var k in r)o[k]=r[k];o.px=px;o.up=r.tgt/px-1;return o})
    .filter(function(r){return r.up>0}).sort(function(a,b){return b.up-a.up}).slice(0,30);
  var R=D.rules||{};
  var h='<div class="lead"><span class="rule">ارزش بازار بالای <b class="num">$'+(R.mcap/1e9||2)+'B</b></span><span class="rule">حداقل <b class="num">'+(R.analysts||8)+'</b> تحلیلگر</span><span class="rule">قیمت سهم بالای <b class="num">$'+(R.price||5)+'</b></span><span class="rule">به‌روزرسانی روزانه</span></div>'
    +'<p class="stamp">قیمت هدف تحلیلگرها: '+esc(day(D.est_as_of||D.as_of))+' &nbsp;|&nbsp; قیمت‌ها: '+(RZQ&&RZQ.as_of?esc(liveWhen(RZQ.as_of)):'آخرین قیمت پایانی')+'</p>';
  if(!ACC)h+=cta();
  h+='<div class="list">'+L.map(row).join('')+'</div>';
  h+='<p class="disc">«درصد رشد» فاصله‌ی قیمت فعلی تا <b>میانگین قیمت هدف تحلیلگرهای وال‌استریت</b> برای ۱۲ ماه آینده است. قیمت هدف پیش‌بینی تحلیلگرهاست و اغلب اشتباه از آب درمیاد؛ سهم‌هایی که سقوط تند داشتن معمولاً بالای این لیست میان چون تحلیلگرها دیرتر هدفشون رو پایین میارن. این لیست نقطه‌ی شروع تحقیقه، نه توصیه‌ی خرید.</p>';
  $('rzt-main').innerHTML=h}
Promise.all([fetch(RAW+'/top30/top30.json?v='+Math.floor(Date.now()/1800000)).then(function(r){if(!r.ok)throw 0;return r.json()}),liveQuotes()])
  .then(function(x){render(x[0])}).catch(function(){$('rzt-main').innerHTML='<div class="card empty">بارگذاری لیست ناموفق بود؛ چند لحظه بعد دوباره امتحان کن.</div>'});
