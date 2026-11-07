/* مسابقه‌ی پورتفو — $10,000 virtual portfolios. Server: events/contest.js (rz-events worker, D1).
   Routes (hash): #/ leaderboard | #/me my dashboard | #/new create profile | #/p/<id> public profile | #/rules */
var API_C=(window.RZC_API||'https://rz-events.mreza-hajilou.workers.dev')+'/c',TOK=window.RZC_TOKEN||'',LOGGED=!!window.RZS_LOGGED;
var LOGIN='/account/login?return_url='+encodeURIComponent(location.pathname+'#/me');
var SORTS=[['total','بازده کل'],['cagr','بازده سالانه‌شده (CAGR)'],['y1','یک سال اخیر'],['ytd','از اول سال'],['q','این فصل'],['m','این ماه']];
function STARS(n,c){return (n?'<span class="stars" title="'+FA(n)+' بار برنده‌ی فصل">'+'⭐'.repeat(Math.min(n,8))+'</span>':'')+(c?'<span class="stars" title="برنده‌ی سال">'+'👑'.repeat(c)+'</span>':'')}
var SEC={'Technology':'تکنولوژی','Health Care':'سلامت','Healthcare':'سلامت','Finance':'مالی','Financial Services':'مالی','Industrials':'صنعتی','Energy':'انرژی','Utilities':'خدمات عمومی','Consumer Discretionary':'کالاهای غیرضروری','Consumer Staples':'کالاهای ضروری','Real Estate':'املاک','Basic Materials':'مواد اولیه','Telecommunications':'مخابرات','Communication Services':'ارتباطات','Miscellaneous':'سایر'};
var ETFS={};
var SORT='total',SHOW=10,BOARD=null,UNI=null,NAMES={},ME=null;
var D=function(v,d){if(v==null||!isFinite(v))return '—';return '<bdi dir="ltr">$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:d==null?2:d,maximumFractionDigits:d==null?2:d})+'</bdi>'};
var P=function(v,d){if(v==null||!isFinite(v))return '—';return '<bdi dir="ltr" class="'+(v>=0?'up':'dn')+'">'+(v>=0?'+':'')+(v*100).toFixed(d==null?1:d)+'%</bdi>'};
var PL=function(v,d){if(v==null||!isFinite(v))return '—';return '<bdi dir="ltr">'+(v*100).toFixed(d==null?1:d)+'%</bdi>'};
var N=function(v,d){return '<bdi dir="ltr">'+Number(v).toLocaleString('en-US',{maximumFractionDigits:d==null?4:d})+'</bdi>'};
var FA=function(n){return String(n).replace(/\d/g,function(c){return '۰۱۲۳۴۵۶۷۸۹'[c]})};
var MON=['ژانویه','فوریه','مارس','آوریل','مه','ژوئن','ژوئیه','اوت','سپتامبر','اکتبر','نوامبر','دسامبر'];
function day(s){var d=new Date(typeof s==='number'?s*1000:s);if(isNaN(d))return String(s);return FA(d.getDate())+' '+MON[d.getMonth()]+' '+FA(d.getFullYear())}
function when(ts){var d=new Date(ts*1000);if(isNaN(d))return '';var p=function(n){return FA(String(n).padStart(2,'0'))};return day(ts)+'، '+p(d.getHours())+':'+p(d.getMinutes())}
function api(path,opt){opt=opt||{};var h={'Content-Type':'application/json'};if(TOK)h['X-RZ-Token']=TOK;
  return fetch(API_C+path,{method:opt.method||'GET',headers:h,body:opt.body?JSON.stringify(opt.body):undefined}).then(function(r){return r.json().then(function(j){j._s=r.status;return j})})}
function main(h){$('rzc-main').innerHTML=h}
function bar(active){var a=function(k,href,txt){return '<a href="'+href+'" class="'+(active===k?'on':'')+'">'+txt+'</a>'};
  return '<div class="cbar">'+a('board','#/','🏆 خانه‌ی مسابقه')+a('me','#/me',LOGGED?'👤 پروفایل من':'👤 ورود')+a('new','#/new','➕ ساخت پروفایل')+'<a href="/pages/contest" class="prev">🗓 مسابقه قبلی</a><a href="/" class="back">بازگشت به سهام آنالیز</a></div>'}

/* ---------- leaderboard ---------- */
function board(){
  main(bar('board')+'<div class="hero"><h1>مسابقه‌ی پورتفو <span class="ltr">$10,000</span></h1><p>با ۱۰ هزار دلار فرضی پورتفوی خودت رو بساز؛ قیمت‌ها رو بازار تعیین می‌کنه.</p></div>'+(Date.now()<Date.parse('2026-12-16T00:00:00Z')?'<a class="prevban" href="/pages/contest"><span class="i">🗓</span><span><b>مسابقه قبلی: سهام برتر نوامبر</b><small>'+(Date.now()<Date.parse('2026-12-01T00:00:00Z')?'هنوز در جریانه؛ رتبه‌بندی زنده و اینکه تا پایان ماه چی می‌شه رو ببین.':'تموم شد؛ نتیجه‌ی نهایی و برنده‌ها رو ببین.')+'</small></span><span class="go">دیدن نتایج ←</span></a>':'')+'<div id="rzc-hof"></div>'+
    '<div class="sorts" id="rzc-sorts">'+SORTS.map(function(s){return '<button data-s="'+s[0]+'" class="'+(s[0]===SORT?'on':'')+'">'+s[1]+'</button>'}).join('')+'</div><div id="rzc-list"><div class="card empty">در حال بارگذاری…</div></div>');
  $('rzc-sorts').onclick=function(e){var b=e.target.closest('button');if(!b)return;SORT=b.getAttribute('data-s');SHOW=10;[].forEach.call(this.children,function(x){x.classList.toggle('on',x===b)});list()};
  (BOARD?Promise.resolve(BOARD):api('/board')).then(function(j){BOARD=j;list()}).catch(function(){$('rzc-list').innerHTML='<div class="card empty">بارگذاری ناموفق بود؛ چند لحظه بعد دوباره امتحان کن.</div>'})}
function hof(){var W=BOARD&&BOARD.winners||[],el=$('rzc-hof');if(!el)return;
  var lab=function(w){return w.kind==='y'?'برنده‌ی سال '+FA(w.period):'برنده‌ی فصل '+FA(w.period.split('-Q')[1])+' '+FA(w.period.split('-')[0])};
  el.innerHTML=W.length?'<div class="hof"><b>🏆 تالار برندگان</b>'+W.slice(0,6).map(function(w){return '<a href="#/p/'+w.id+'">'+(w.kind==='y'?'👑':'⭐')+' '+esc(w.name)+'<small>'+lab(w)+(w.ret!=null?' | '+P(w.ret):'')+'</small></a>'}).join('')+'</div>'
    :'<div class="hof empty"><b>🏆 تالار برندگان</b><span>برنده‌ی اولین فصل: پایان مارس ۲۰۲۷ (<bdi dir="ltr">€50</bdi>)</span><span>برنده‌ی سال ۲۰۲۷: <bdi dir="ltr">€300</bdi></span><span>هر بار برنده‌ی فصل = یک ⭐ کنار اسم</span></div>'}
function list(){hof();
  var R=(BOARD.rows||[]).filter(function(r){return r.eligible});
  var waiting=(BOARD.rows||[]).length-R.length;
  var key=SORT;R.sort(function(a,b){var x=a[key],y=b[key];if(x==null&&y==null)return b.total-a.total;if(x==null)return 1;if(y==null)return -1;return y-x});
  var y2027=new Date()>=new Date('2027-01-01');
  var h=R.slice(0,SHOW).map(function(r,i){var v=r[key];
    return '<a class="pcard" href="#/p/'+r.id+'"><div class="rk">'+FA(i+1)+'</div><div class="who"><b>'+esc(r.name)+STARS(r.stars,r.crowns)+'</b>'+(r.strategy?'<small>'+esc(r.strategy)+'</small>':'')+
      '<div class="meta"><span>'+FA(r.n_pos)+' سهم</span><span>'+FA(r.n_trades)+' ترید</span><span>ارزش '+D(r.value,0)+'</span>'+(r.vs_spy!=null?'<span>در برابر S&amp;P 500: '+P(r.vs_spy)+'</span>':'')+(y2027&&!r.prize_y?'<span class="tag">فقط رقابت فصلی</span>':'')+'</div></div>'+
      '<div class="mini">'+[['m','ماه'],['q','فصل'],['ytd','از اول سال'],['total','کل']].filter(function(x){return x[0]!==key}).map(function(x){return '<span><small>'+x[1]+'</small>'+P(r[x[0]])+'</span>'}).join('')+'</div>'+
      '<div class="ret"><span class="v">'+(v==null?'<small>کمتر از ۱ سال</small>':P(v))+'</span><small>'+SORTS.filter(function(s){return s[0]===key})[0][1]+'</small></div></a>'}).join('');
  var ALL=(BOARD.rows||[]).length;
  if(!R.length)h='<div class="card empty"><b class="cnt">'+FA(ALL)+'</b> نفر تا الان پورتفوی خودشون رو ثبت کردن.<br><small>رده‌بندی از وقتی نشون داده می‌شه که هر پورتفو حداقل ۳ سهم بخره (سفارش‌ها با باز شدن بازار آمریکا انجام می‌شن).</small><br><a href="#/new">تو هم پورتفوت رو بساز</a></div>';
  if(R.length>SHOW)h+='<button class="more" id="rzc-more">نمایش بیشتر</button>';
  h+='<p class="note">'+FA(ALL)+' پورتفوی ثبت‌شده، '+FA(R.length)+' تا در رده‌بندی'+(waiting?' ('+FA(waiting)+' تا هنوز کمتر از ۳ سهم دارن)':'')+'. به‌روزرسانی هر ۵ دقیقه.</p>';
  $('rzc-list').innerHTML=h;var m=$('rzc-more');if(m)m.onclick=function(){SHOW+=10;list()}}

/* ---------- rules ---------- */
/* short summary on the create page; the full rules live on #/rules */
var RULES='<ul class="rules">'+
 '<li>هر پروفایل با <b><bdi dir="ltr">$10,000</bdi></b> نقد فرضی شروع می‌کنه و برای حضور در رده‌بندی حداقل <b>۳ سهم</b> لازمه.</li>'+
 '<li><b>قیمت رو بازار تعیین می‌کنه:</b> هر سفارش با اولین قیمتی که بعد از ثبت سفارش منتشر می‌شه انجام می‌شه.</li>'+
 '<li>سهام آمریکا (ارزش بازار بالای ۱ میلیارد و قیمت بالای ۵ دلار) و ETFهای اصلی؛ بدون اهرم و فروش استقراضی؛ هر سهم حداکثر <b>۷۰٪</b> پورتفو.</li>'+
 '<li><b>جایزه‌ها:</b> برترین هر فصل ۵۰ یورو و برترین کل سال ۲۰۲۷ <b>۳۰۰ یورو</b>؛ رقابت رسمی از ۱ ژانویه ۲۰۲۷.</li>'+
 '<li>هر ایمیل هر ۶ ماه یک پروفایل جدید؛ برای جایزه فقط بهترین پروفایل هر نفر حساب می‌شه.</li></ul>'+
 '<p class="note"><a href="#/rules" target="_blank">📜 قوانین کامل مسابقه</a> رو قبل از ساخت پروفایل بخون.</p>';
var FULL=[
 ['۱. درباره‌ی مسابقه',
  ['مسابقه‌ی پورتفوی سهام آنالیز یک رقابت آموزشی و رایگانه که در اون هر شرکت‌کننده با سرمایه‌ی فرضی یک پورتفوی سهام آمریکا می‌سازه و بازدهش با بقیه مقایسه می‌شه.',
   'هیچ پول واقعی‌ای معامله نمی‌شه، هیچ سهم واقعی‌ای خرید و فروش نمی‌شه و هیچ کارگزاری درگیر نیست. هدف، یاد گرفتن سرمایه‌گذاری بلندمدت، ثبت تصمیم‌ها و مقایسه‌ی استراتژی‌هاست.',
   'مسابقه پایان مشخصی نداره و به‌صورت دوره‌ای (فصلی و سالانه) برنده معرفی می‌کنه. دوره‌ی رسمی اول از ۱ ژانویه ۲۰۲۷ شروع می‌شه؛ تا اون موقع ثبت‌نام و ساخت پورتفو آزاده و بازده‌ها جنبه‌ی تمرینی دارن.']],
 ['۲. ثبت‌نام و پروفایل',
  ['شرکت در مسابقه رایگانه. برای ساخت پروفایل باید با ایمیل وارد حساب کاربری سهام آنالیز بشی (کد یک‌بارمصرف به ایمیلت فرستاده می‌شه).',
   'اسم پروفایل عمومی نمایش داده می‌شه. اسم نباید توهین‌آمیز، گمراه‌کننده، تبلیغاتی یا متعلق به شخص یا شرکت دیگه‌ای باشه. اسم تکراری پذیرفته نمی‌شه.',
   'هر ایمیل هر ۶ ماه یک بار می‌تونه یک پروفایل جدید با استراتژی جدید بسازه. پروفایل‌های قبلی فعال می‌مونن و ادامه‌ی کار می‌دن.',
   'ساختن چند حساب کاربری با ایمیل‌های مختلف برای دور زدن این قانون ممنوعه و باعث حذف همه‌ی پروفایل‌های مرتبط می‌شه.',
   'شرکت برای جایزه فقط برای افراد بالای ۱۸ سال مجازه.']],
 ['۳. سرمایه‌ی شروع و دارایی‌های مجاز',
  ['هر پروفایل با <b><bdi dir="ltr">$10,000</bdi></b> نقد فرضی شروع می‌کنه. واریز یا برداشت پول ممکن نیست؛ تنها راه رشد سرمایه، تصمیم‌های سرمایه‌گذاری و سود نقدی سهم‌هاست.',
   'نقد هم یک پوزیشن حساب می‌شه، ولی برای حضور در جدول رده‌بندی باید همزمان حداقل <b>۳ سهم یا ETF</b> در پورتفو باشه.',
   'دارایی‌های مجاز: سهام شرکت‌های فهرست‌شده در بورس‌های آمریکا با ارزش بازار حداقل ۱ میلیارد دلار و قیمت حداقل ۵ دلار، به‌علاوه‌ی فهرستی از ETFهای اصلی (شاخص‌ها، بخش‌ها، اوراق، طلا، نقره، بیت‌کوین، اتریوم، نفت و…). این فهرست هر روز به‌روز می‌شه.',
   'اگه سهمی بعد از خرید از فهرست خارج بشه (مثلاً قیمتش زیر ۵ دلار بیاد)، می‌تونی نگهش داری یا بفروشی، ولی خرید دوباره‌اش ممکن نیست.',
   'خرید کسری از سهم (مثلاً ۰٫۵ سهم) مجازه.']],
 ['۴. سفارش‌ها و قیمت معامله',
  ['همه‌ی سفارش‌ها «به قیمت بازار» هستن. خرید با مبلغ دلاری و فروش با تعداد سهم ثبت می‌شه.',
   '<b>قیمت رو بازار تعیین می‌کنه، نه شرکت‌کننده:</b> هر سفارش با اولین قیمتی انجام می‌شه که <b>بعد از ثبت سفارش</b> منتشر می‌شه. قیمت‌ها در ساعت بازار آمریکا حدوداً هر ۱۵ دقیقه به‌روز می‌شن.',
   'اگه بازار بسته باشه (شب، آخر هفته یا تعطیلات رسمی آمریکا)، سفارش در انتظار می‌مونه و با اولین قیمت روز معاملاتی بعد انجام می‌شه.',
   'تا وقتی سفارش انجام نشده، می‌تونی لغوش کنی. سفارشی که ۶ روز قیمت جدید دریافت نکنه خودکار رد می‌شه.',
   'اگه قیمت تا لحظه‌ی انجام سفارش تغییر کنه و نقد کافی نباشه یا قانون ۷۰٪ نقض بشه، مبلغ خرید خودکار کم می‌شه.',
   'کارمزد معامله و مالیات در مسابقه در نظر گرفته نمی‌شه.',
   'حداکثر ۲۰ سفارش باز و ۴۰ سفارش در هر ۲۴ ساعت برای هر پروفایل مجازه.']],
 ['۵. محدودیت‌ها',
  ['فروش استقراضی (short)، اهرم، وام، مارجین، آپشن و هر نوع مشتقه مجاز نیست.',
   'بعد از هر خرید، ارزش یک سهم نمی‌تونه بیش از <b>۷۰٪</b> ارزش کل پورتفو باشه. اگه سهمی بعد از خرید به‌خاطر رشد قیمت بیش از ۷۰٪ بشه اشکالی نداره، ولی خرید بیشتر از اون سهم ممکن نیست.',
   'سهم‌های خیلی کوچک و ارزان (پنی‌استاک) به‌خاطر امکان دست‌کاری قیمت در مسابقه نیستن.']],
 ['۶. سود نقدی، اسپلیت و رویدادهای شرکتی',
  ['سود نقدی (دیویدند) سهم‌هایی که قبل از تاریخ ex-dividend در پورتفو بودن، به نقدِ پورتفو اضافه می‌شه و جزو بازده حساب می‌شه.',
   'اسپلیت و ریورس‌اسپلیت به‌صورت خودکار روی تعداد سهم‌ها اعمال می‌شه و ارزش پورتفو تغییری نمی‌کنه.',
   'اگه شرکتی ادغام، خریداری یا از بورس خارج بشه، تیم سهام آنالیز معادل منصفانه‌ی نقدی یا سهمی رو اعمال می‌کنه.']],
 ['۷. محاسبه‌ی بازده و رده‌بندی',
  ['ارزش پورتفو = نقد + ارزش روز همه‌ی سهم‌ها. ارزش روزانه بعد از بسته‌شدن بازار ثبت می‌شه.',
   'رده‌بندی بر اساس این بازده‌ها ممکنه: بازده کل از ساخت پروفایل، بازده سالانه‌شده (CAGR؛ برای پروفایل‌های بالای یک سال)، یک سال اخیر، از اول سال، فصل جاری و ماه جاری.',
   'بازده هر دوره نسبت به ارزش پورتفو در آخرین روز قبل از شروع اون دوره حساب می‌شه؛ برای پروفایل‌هایی که وسط دوره ساخته شدن، نسبت به <bdi dir="ltr">$10,000</bdi>.',
   'جدول رده‌بندی حدوداً هر ۵ دقیقه به‌روز می‌شه.']],
 ['۸. جایزه‌ها',
  ['<b>جایزه‌ی فصلی:</b> بالاترین بازده هر فصل (ژانویه تا مارس، آوریل تا ژوئن، ژوئیه تا سپتامبر، اکتبر تا دسامبر) <b>۵۰ یورو</b> دریافت می‌کنه.',
   '<b>جایزه‌ی سالانه:</b> بالاترین بازده کل سال ۲۰۲۷ (۱ ژانویه تا ۳۱ دسامبر) <b>۳۰۰ یورو</b> دریافت می‌کنه.',
   'برای جایزه‌ی سالانه، پروفایل باید <b>قبل از شروع سال</b> ساخته شده باشه. پروفایل‌هایی که وسط سال ساخته می‌شن تا شروع سال بعد فقط در رقابت‌های فصلی شرکت دارن. برای جایزه‌ی هر فصل، پروفایل باید قبل از شروع همون فصل ساخته شده باشه.',
   'برای گرفتن جایزه، پروفایل باید در پایان دوره حداقل ۳ سهم داشته باشه و در طول دوره حداقل یک ترید انجام داده باشه.',
   'هر نفر در هر دوره فقط با بهترین پروفایلش در رقابت جایزه حساب می‌شه.',
   'سهام آنالیز هم ممکنه چند پورتفو با استراتژی‌های خودش در مسابقه داشته باشه؛ این پورتفوها هیچ جایزه‌ای نمی‌گیرن و اگه بالای جدول باشن، جایزه به بهترین شرکت‌کننده‌ی بعدی می‌رسه.',
   'برنده‌ها حداکثر ۱۴ روز بعد از پایان هر دوره از طریق ایمیل حساب کاربری مطلع می‌شن و جایزه از طریق PayPal یا انتقال بانکی پرداخت می‌شه. اگه برنده تا ۳۰ روز پاسخ نده، جایزه به نفر بعدی می‌رسه.',
   'جایزه‌ها قابل تبدیل به چیز دیگه یا انتقال به شخص دیگه نیستن. پرداخت مالیات احتمالی جایزه با برنده است.']],
 ['۹. نمایش پروفایل‌ها و حریم خصوصی',
  ['اسم پروفایل، ارزش پورتفو، بازده، تعداد سهم‌ها و تعداد تریدها برای همه در جدول رده‌بندی نمایش داده می‌شه.',
   'برای عادلانه بودن مسابقه، سهم‌ها، تریدها و کامنت‌های پروفایل‌ها تا ۱ فوریه ۲۰۲۷ برای دیگران نمایش داده نمی‌شه. از اون تاریخ این جزئیات برای مشترکین Stock Pro باز می‌شه.',
   'هر شرکت‌کننده داشبورد و تاریخچه‌ی کامل خودش رو همیشه می‌بینه.',
   'ایمیل شرکت‌کننده‌ها هیچ‌وقت نمایش داده نمی‌شه و فقط برای ورود و تماس درباره‌ی جایزه استفاده می‌شه.',
   'کامنت‌ها نباید توهین‌آمیز، تبلیغاتی یا حاوی لینک باشن. کامنت‌ها بعد از ثبت قابل ویرایش نیستن.']],
 ['۱۰. فعال بودن، تقلب و حذف',
  ['پروفایلی که ۱۲ ماه هیچ تریدی نداشته باشه بررسی می‌شه. اگه بی‌تحرکی بخشی از استراتژی نباشه، ممکنه از جدول حذف بشه.',
   'هر تلاشی برای سوءاستفاده از خطاهای فنی، قیمت‌های اشتباه یا دور زدن قوانین باعث حذف پروفایل و از دست رفتن جایزه می‌شه. اگه خطای فنی‌ای پیدا کردی، از طریق صفحه‌ی تماس گزارشش بده.',
   'سهام آنالیز حق داره در صورت خطای قیمت یا مشکل فنی، معاملات مربوط رو اصلاح یا لغو کنه.']],
 ['۱۱. تغییر قوانین و سلب مسئولیت',
  ['سهام آنالیز ممکنه برای بهتر و عادلانه‌تر شدن مسابقه، قوانین رو تغییر بده. تغییرات مهم قبل از اجرا در همین صفحه اعلام می‌شه و روی دوره‌ی در جریان تأثیر منفی نمی‌ذاره.',
   'این مسابقه آموزشیه و هیچ‌کدوم از پورتفوها، تریدها یا کامنت‌ها توصیه‌ی خرید یا فروش نیست. بازده گذشته تضمینی برای آینده نیست.',
   'در موارد اختلاف، تصمیم نهایی با سهام آنالیزه. شرکت در مسابقه به معنی پذیرش این قوانینه.']]
];
function rules(){main(bar('')+'<div class="card rulesfull"><h2>📜 قوانین کامل مسابقه‌ی پورتفو</h2><p class="note">آخرین به‌روزرسانی: نوامبر ۲۰۲۶</p>'+
  '<nav class="toc">'+FULL.map(function(s,i){return '<a href="#" data-sec="'+i+'">'+s[0]+'</a>'}).join('')+'</nav>'+
  FULL.map(function(s,i){return '<section id="rzc-sec'+i+'"><h3>'+s[0]+'</h3><ol>'+s[1].map(function(x){return '<li>'+x+'</li>'}).join('')+'</ol></section>'}).join('')+'</div>');
  document.querySelectorAll('[data-sec]').forEach(function(a){a.onclick=function(e){e.preventDefault();var el=$('rzc-sec'+a.getAttribute('data-sec'));if(el)el.scrollIntoView({behavior:'smooth'})}})}

/* ---------- create profile ---------- */
function create(){
  if(!LOGGED||!TOK){main(bar('new')+'<div class="card center"><h2>اول وارد حسابت شو</h2><p>با ایمیلت وارد شو (کد یک‌بارمصرف به ایمیلت میاد) تا پروفایل مسابقه‌ات رو بسازی. ثبت‌نام رایگانه.</p><a class="btn" href="'+LOGIN.replace('%23%2Fme','%23%2Fnew')+'">ورود با ایمیل</a></div>');return}
  main(bar('new')+'<div class="card"><h2>ساخت پروفایل مسابقه</h2>'+RULES+
    '<label>اسم پروفایل (عمومی دیده می‌شه)<input id="rzc-n" maxlength="40" placeholder="مثلاً سرمایه‌گذار صبور"></label>'+
    '<label>استراتژی‌ات در یک جمله (اختیاری)<input id="rzc-s" maxlength="200" placeholder="مثلاً سهام باکیفیت با رشد پایدار، نگه‌داری بلندمدت"></label>'+
    '<label class="chk"><input type="checkbox" id="rzc-a"> <a href="#/rules" target="_blank">قوانین کامل</a> رو خوندم و قبول دارم</label>'+
    (ME&&ME.me&&ME.me.admin?'<label class="chk"><input type="checkbox" id="rzc-h"> پورتفوی استراتژی سهام آنالیز (بدون نشان؛ بدون محدودیت ۶ ماه؛ جایزه نمی‌گیره)</label>':'')+
    '<button class="btn" id="rzc-go">ساخت پروفایل و دریافت <bdi dir="ltr">$10,000</bdi></button><p class="err" id="rzc-e"></p></div>');
  $('rzc-go').onclick=function(){var b=this;b.disabled=true;api('/profile',{method:'POST',body:{name:$('rzc-n').value,strategy:$('rzc-s').value,accept:$('rzc-a').checked,house:!!($('rzc-h')&&$('rzc-h').checked)}}).then(function(j){
    if(j.ok){BOARD=null;location.hash='#/me'}else{b.disabled=false;$('rzc-e').textContent=(j.error||'خطا')+(j.next?' (از '+day(j.next)+')':'')}}).catch(function(){b.disabled=false;$('rzc-e').textContent='ارتباط برقرار نشد'})}}

/* ---------- portfolio view (shared by my dashboard and public profile) ---------- */
function holdings(p,mine){
  var pos=p.positions||[],tot=p.cash;pos.forEach(function(x){x.val=x.qty*(x.px||x.cost/x.qty);tot+=x.val});
  var dayT=pos.reduce(function(s,x){return s+(x.chg!=null?x.val*x.chg/(100+x.chg):0)},0),plT=pos.reduce(function(s,x){return s+x.val-x.cost},0);
  var rows=pos.sort(function(a,b){return b.val-a.val}).map(function(x){var avg=x.cost/x.qty,pl=x.val/x.cost-1;
    return '<tr><td><a href="/pages/stock#'+esc(x.t)+'" class="tk">'+esc(x.t)+'</a><small>'+esc(NAMES[x.t]||'')+'</small></td><td>'+N(x.qty,4)+'</td><td class="mh">'+D(avg)+'</td><td class="mh">'+D(x.px)+(x.chg!=null?' <small>'+P(x.chg/100,2)+'</small>':'')+'</td><td>'+D(x.val)+(x.chg!=null?'<small>امروز '+D(x.val*x.chg/(100+x.chg))+'</small>':'')+'</td><td class="mh">'+PL(x.val/tot,0)+'</td><td>'+P(pl)+'<small>'+D(x.val-x.cost)+'</small></td>'+
      (mine?'<td><button class="lnk" data-sell="'+esc(x.t)+'">فروش</button></td>':'')+'</tr>'}).join('');
  rows+='<tr class="cash"><td>💵 نقد</td><td></td><td class="mh"></td><td class="mh"></td><td>'+D(p.cash)+'</td><td class="mh">'+PL(p.cash/tot,0)+'</td><td></td>'+(mine?'<td></td>':'')+'</tr>';
  var alloc=pos.map(function(x,i){return '<span style="width:'+(x.val/tot*100).toFixed(2)+'%;background:hsl('+(i*47%360)+',45%,52%)" title="'+esc(x.t)+'"></span>'}).join('')+'<span style="width:'+(p.cash/tot*100).toFixed(2)+'%;background:#556"></span>';
  return '<div class="alloc">'+alloc+'</div><div class="tw"><table class="ht"><thead><tr><th>سهم</th><th>تعداد</th><th class="mh">میانگین خرید</th><th class="mh">قیمت</th><th>ارزش</th><th class="mh">وزن</th><th>سود/زیان</th>'+(mine?'<th></th>':'')+'</tr></thead><tbody>'+rows+'</tbody></table></div><p class="note">سود/زیان کل: '+P(plT/Math.max(1,tot-p.cash-plT))+' ('+D(plT)+') | تغییر امروز: '+D(dayT)+'. روی هر نماد بزن تا تحلیل کاملش رو ببینی.</p>'}
function history(p,mine){
  var O=(p.orders||[]),I=(p.income||[]).filter(function(x){return x.kind==='div'||x.kind==='split'});
  var ST={pending:'در انتظار قیمت بعدی',filled:'انجام شد',cancelled:'لغو شد',rejected:'رد شد'};
  var ev=O.map(function(o){return {ts:o.ts,h:'<div class="tr '+o.side+' '+o.status+'"><div class="l"><b>'+(o.side==='buy'?'خرید':'فروش')+' <a href="/pages/stock#'+esc(o.t)+'" class="tk">'+esc(o.t)+'</a></b> '+
      (o.status==='filled'?N(o.fill_qty,4)+' سهم × '+D(o.price)+' = '+D(o.fill_amt):(o.side==='buy'?D(o.amount):N(o.qty,4)+' سهم'))+
      '<small>'+when(o.status==='filled'?o.fill_ts:o.ts)+' | '+ST[o.status]+(o.status==='rejected'&&o.reason?' ('+esc(o.reason)+')':'')+'</small>'+(o.note?'<q dir="auto">'+esc(o.note)+'</q>':'')+'</div>'+
      (mine&&o.status==='pending'?'<button class="lnk" data-cancel="'+o.id+'">لغو</button>':'')+'</div>'}})
    .concat(I.map(function(x){return {ts:x.ts,h:'<div class="tr inc"><div class="l"><b>'+(x.kind==='div'?'💰 سود نقدی ':'✂️ اسپلیت ')+esc(x.t)+'</b> '+(x.kind==='div'?D(x.amount):'')+'<small>'+when(x.ts)+'</small></div></div>'}}))
    .sort(function(a,b){return b.ts-a.ts});
  return ev.length?ev.map(function(e){return e.h}).join(''):'<p class="note">هنوز تریدی ثبت نشده.</p>'}
function vsSpy(p,value){var q=RZQ&&RZQ.q&&RZQ.q.SPY;return p.spy0&&q?(value/10000)/(q[0]/p.spy0)-1:null}
function summary(p,value){var r=value/10000-1,vs=vsSpy(p,value);
  return '<div class="sum">'+(vs!=null?'<div><small>در برابر S&amp;P 500</small><b>'+P(vs)+'</b></div>':'')+'<div><small>ارزش پورتفو</small><b>'+D(value)+'</b></div><div><small>بازده کل</small><b>'+P(r)+'</b></div><div><small>نقد</small><b>'+D(p.cash)+'</b></div><div><small>سهم‌ها</small><b>'+FA((p.positions||[]).length)+'</b></div><div><small>تریدها</small><b>'+FA((p.orders||[]).filter(function(o){return o.status==='filled'}).length)+'</b></div></div>'}
function chart(id,box){api('/hist/'+id).then(function(j){if(!j.v||j.v.length<2){$(box).innerHTML='<div class="chh"><span>شروع: <b><bdi dir="ltr">$10,000</bdi></b></span></div><p class="note">نمودار عملکرد از اولین روز معاملاتی بعد از ساخت پروفایل کشیده می‌شه.</p>';return}
  var V=j.v,W=600,H=150,mn=Math.min.apply(null,V.map(function(x){return x[1]}).concat([10000])),mx=Math.max.apply(null,V.map(function(x){return x[1]}).concat([10000]));if(mx===mn)mx=mn+1;
  var X=function(i){return 10+i/(V.length-1)*(W-20)},Y=function(v){return H-10-(v-mn)/(mx-mn)*(H-30)};
  var SP=j.spy||[],s0=j.spy0||(SP[0]&&SP[0][1]),sm={};SP.forEach(function(x){sm[x[0]]=x[1]/s0*10000});
  var SV=V.map(function(x){return sm[x[0]]}),allv=V.map(function(x){return x[1]}).concat(SV.filter(function(v){return v})).concat([10000]);
  mn=Math.min.apply(null,allv);mx=Math.max.apply(null,allv);if(mx===mn)mx=mn+1;
  var pts=V.map(function(x,i){return X(i).toFixed(1)+','+Y(x[1]).toFixed(1)}).join(' '),last=V[V.length-1][1],col=last>=10000?'var(--up)':'var(--dn)';
  var spts=SV.map(function(v,i){return v?X(i).toFixed(1)+','+Y(v).toFixed(1):null}).filter(Boolean).join(' ');
  var spLast=SV.filter(function(v){return v}).pop(),ret=last/10000-1,sret=spLast?spLast/10000-1:null;
  var head='<div class="chh"><span>شروع <b><bdi dir="ltr">$10,000</bdi></b></span><span>الان <b><bdi dir="ltr">'+'$'+Math.round(last).toLocaleString('en-US')+'</bdi></b></span><span>عملکرد <b>'+P(ret)+'</b></span>'+(sret!=null?'<span>S&amp;P 500 در همین مدت <b>'+P(sret)+'</b></span>':'')+'</div>';
  var yl='<text x="'+(W-12)+'" y="'+(Y(mx)+4)+'" class="yl">'+'$'+Math.round(mx).toLocaleString('en-US')+'</text><text x="'+(W-12)+'" y="'+(Y(mn)-3)+'" class="yl">'+'$'+Math.round(mn).toLocaleString('en-US')+'</text>';
  var dot='<circle cx="'+X(V.length-1).toFixed(1)+'" cy="'+Y(last).toFixed(1)+'" r="3.5" fill="'+col+'"/>';
  $(box).innerHTML=head+'<svg viewBox="0 0 '+W+' '+H+'" class="ch">'+yl+dot+'<line x1="10" x2="'+(W-10)+'" y1="'+Y(10000)+'" y2="'+Y(10000)+'" class="base"/>'+(spts?'<polyline points="'+spts+'" fill="none" stroke="#8a8f99" stroke-width="1.6"/>':'')+'<polyline points="'+pts+'" fill="none" stroke="'+col+'" stroke-width="2.5"/></svg>'+
    '<div class="chl"><span><bdi dir="ltr">'+esc(V[0][0])+'</bdi></span><span>'+(spts?'<i class="lg" style="background:'+col+'"></i>پورتفو <i class="lg" style="background:#8a8f99"></i>S&amp;P 500 | ':'')+'خط‌چین = <bdi dir="ltr">$10,000</bdi></span><span><bdi dir="ltr">'+esc(V[V.length-1][0])+'</bdi></span></div>'}).catch(function(){})}

function MKT(){if(MKT.v)return MKT.v;var L=(ROWS||[]).filter(function(r){var m=g(r,'mcap');return m&&isFinite(m)&&!ETFS[g(r,'t')]}).sort(function(a,b){return g(b,'mcap')-g(a,'mcap')}).slice(0,500);
  var cap=0,e=0,fe=0,fcap=0,d=0;L.forEach(function(r){var m=g(r,'mcap'),pe=g(r,'pe'),fp=g(r,'fwd_pe'),dy=g(r,'divy');cap+=m;if(pe&&isFinite(pe))e+=m/pe;if(fp&&isFinite(fp)){fe+=m/fp;fcap+=m}if(dy&&isFinite(dy))d+=m*dy});
  MKT.v={pe:e>0?cap/e:null,fpe:fe>0?fcap/fe:null,dy:cap?d/cap:null};return MKT.v}
function wstars(W){W=W||[];return STARS(W.filter(function(w){return w.kind==='q'}).length,W.filter(function(w){return w.kind==='y'}).length)}

/* ---------- portfolio analysis: fundamentals (screener data), risk (weekly prices), sectors, upcoming earnings ---------- */
function analyze(p,box){var el=$(box);if(!el)return;if(!analyze.ready){el.innerHTML='<h3>📊 تحلیل پورتفو</h3><p class="note">در حال بارگذاری…</p>';DATA.then(function(){analyze.ready=1;analyze(p,box)});return}var pos=(p.positions||[]).slice();
  if(!pos.length){el.innerHTML='<h3>📊 تحلیل پورتفو</h3><p class="note">بعد از اولین خرید، اینجا رشد، ارزش‌گذاری، ریسک و ترکیب صنعتی پورتفوت رو می‌بینی.</p>';return}
  var tot=p.cash;pos.forEach(function(x){x.val=x.qty*(x.px||x.cost/x.qty);tot+=x.val});
  var inv=tot-p.cash,W={};pos.forEach(function(x){W[x.t]=x.val/inv});
  var FR=function(t){return ETFS[t]?null:BY[t]};
  var wavg=function(k,ok){var s=0,ws=0;pos.forEach(function(x){var r=FR(x.t),v=r?g(r,k):null;if(v==null||!isFinite(v)||(ok&&!ok(v)))return;s+=W[x.t]*v;ws+=W[x.t]});return ws>0.3?{v:s/ws,c:ws}:null};
  var ey=0,eyw=0;pos.forEach(function(x){var r=FR(x.t),pe=r?g(r,'pe'):null;if(pe!=null&&isFinite(pe)){eyw+=W[x.t];if(pe>0)ey+=W[x.t]/pe}});var peP=eyw>0.3&&ey>0?eyw/ey:null;
  var M=[['امتیاز کلی سهم‌ها',wavg('s_total'),function(v){return sc(v)},'میانگین وزنی امتیاز ۰ تا ۵ سهام آنالیز'],
    ['رشد درآمد (۱ سال)',wavg('revg1'),function(v){return P(v)},'شرکت‌هات سال گذشته چقدر بزرگ‌تر شدن'],
    ['رشد سالانه‌ی درآمد (۵ سال)',wavg('revg5'),function(v){return P(v)},'سرعت رشد بلندمدت کسب‌وکارها'],
    ['حاشیه سود خالص',wavg('nm'),function(v){return P(v)},'از هر ۱۰۰ دلار فروش چقدر سود می‌مونه'],
    ['بازده سرمایه (ROIC)',wavg('roic'),function(v){return P(v)},'کیفیت کسب‌وکار؛ بالای ۱۵٪ عالیه'],
    ['فاصله تا قیمت هدف تحلیلگرها',wavg('tgt_up'),function(v){return P(v)},'میانگین وزنی پتانسیل رشد از نظر وال‌استریت']];
  var tiles=M.filter(function(m){return m[1]}).map(function(m){return '<div class="mt"><small>'+m[0]+'</small><b>'+m[2](m[1].v)+'</b><i>'+m[3]+'</i></div>'}).join('');
  var etf=pos.filter(function(x){return !FR(x.t)}).reduce(function(s,x){return s+W[x.t]},0);
  var secs={};pos.forEach(function(x){var r=FR(x.t),k=r?(SEC[g(r,'sector')]||g(r,'sector')||'سایر'):'ETF / صندوق';secs[k]=(secs[k]||0)+x.val/tot});secs['💵 نقد']=p.cash/tot;
  var secH=Object.keys(secs).filter(function(k){return secs[k]>0.0005}).sort(function(a,b){return secs[b]-secs[a]}).map(function(k){return '<div class="sb"><span>'+esc(k)+'</span><i style="width:'+(secs[k]*100).toFixed(1)+'%"></i><b>'+PL(secs[k],0)+'</b></div>'}).join('');
  var wsort=pos.map(function(x){return x.val/tot}).sort(function(a,b){return b-a}),hhi=pos.reduce(function(s,x){return s+Math.pow(x.val/inv,2)},0);
  var hp=function(k){var e=0,w=0;pos.forEach(function(x){var r=FR(x.t),v=r?g(r,k):null;if(v==null||!isFinite(v)||v===0)return;w+=W[x.t];e+=W[x.t]/v});return w>0.3&&e>0?w/e:null};
  var dyP=wavg('divy');var mk=MKT();
  var cmpRow=function(lab,pv,mv,fmt,lowGood,hint){if(pv==null)return '';var d=mv?pv/mv-1:null,tag='';
    if(d!=null){var better=lowGood?d<-0.05:d>0.05,worse=lowGood?d>0.05:d<-0.05;tag=better?'<span class="lv up">'+(lowGood?'ارزون‌تر از بازار':'بیشتر از بازار')+'</span>':worse?'<span class="lv '+(lowGood?'dn':'gold')+'">'+(lowGood?'گرون‌تر از بازار':'کمتر از بازار')+'</span>':'<span class="lv gold">نزدیک بازار</span>'}
    return '<tr><th>'+lab+'<small>'+hint+'</small></th><td><b>'+fmt(pv)+'</b>'+tag+'</td><td>'+(mv?fmt(mv):'—')+'</td></tr>'};
  var fx=function(v){return '<bdi dir="ltr">'+v.toFixed(1)+'</bdi>'};
  var cmp=(peP||dyP)?'<h4>🆚 مقایسه با بازار</h4><div class="cmpw"><table class="cmp"><thead><tr><th></th><th>این پورتفو</th><th>بازار <small>(S&amp;P 500)</small></th></tr></thead><tbody>'+
    cmpRow('P/E',peP,mk.pe,fx,true,'قیمت در برابر سود ۱۲ ماه گذشته')+
    cmpRow('P/E فوروارد',hp('fwd_pe'),mk.fpe,fx,true,'قیمت در برابر سود پیش‌بینی‌شده‌ی سال آینده')+
    cmpRow('بازده سود نقدی',dyP?dyP.v:null,mk.dy,function(v){return PL(v,2)},false,'سود نقدی سالانه نسبت به قیمت')+
    '</tbody></table></div><p class="note">بازار = میانگین وزنی ۵۰۰ شرکت بزرگ آمریکا بر اساس ارزش بازار (تقریب S&amp;P 500)، از همون داده‌های سهام آنالیز.</p>':'';
  el.innerHTML='<h3>📊 تحلیل پورتفو</h3><div class="mts">'+tiles+'</div>'+cmp+(etf>0.05?'<p class="note">'+PL(etf,0)+' از سرمایه‌گذاری در ETF/صندوق‌هاست و در عددهای بنیادی بالا حساب نشده.</p>':'')+
    '<h4>⚖️ ریسک</h4><div class="mts"><div class="mt"><small>بزرگ‌ترین سهم</small><b>'+PL(wsort[0],0)+'</b><i>هرچی کمتر، پخش‌تر</i></div><div class="mt"><small>تعداد مؤثر سهم‌ها</small><b>'+N(1/hhi,1)+'</b><i>پورتفوت مثل چند سهم هم‌وزن رفتار می‌کنه</i></div><div class="mt" id="rzc-vol"><small>نوسان سالانه</small><b>…</b><i>در حال محاسبه از قیمت‌های یک سال اخیر</i></div><div class="mt" id="rzc-dd"><small>بیشترین افت (۱ سال)</small><b>…</b><i></i></div></div>'+
    '<h4>🏭 ترکیب صنعتی</h4><div class="secs">'+secH+'</div><h4>📅 گزارش‌های مالی پیش‌رو</h4><div id="rzc-earn"><p class="note">در حال بارگذاری…</p></div>'+
    '<p class="note">برای دیدن صورت‌های مالی، ارزش ذاتی و نظر تحلیلگرها، روی نماد هر سهم بزن.</p>';
  // risk from one year of weekly closes (same weights as today; cash = 0% return)
  Promise.all(pos.slice(0,20).map(function(x){return fetch(RAW+'/prices/'+encodeURIComponent(x.t)+'.json?v='+Math.floor(Date.now()/86400000)).then(function(r){return r.ok?r.json():null}).catch(function(){return null})})).then(function(L){
    var series={},dates=null;L.forEach(function(j,i){if(!j||!j.w)return;var w=j.w.slice(-53);var m={};w.forEach(function(r){m[r[0]]=r[1]});series[pos[i].t]=m;var ds=w.map(function(r){return r[0]});dates=dates?dates.filter(function(d){return m[d]!=null}):ds});
    if(!dates||dates.length<10){$('rzc-vol').querySelector('b').textContent='—';$('rzc-vol').querySelector('i').textContent='داده‌ی کافی نیست';$('rzc-dd').querySelector('b').textContent='—';return}
    var rets=[];for(var k=1;k<dates.length;k++){var r=0;pos.forEach(function(x){var m=series[x.t];if(m&&m[dates[k]]&&m[dates[k-1]])r+=(x.val/tot)*(m[dates[k]]/m[dates[k-1]]-1)});rets.push(r)}
    var mu=rets.reduce(function(a,b){return a+b},0)/rets.length,sd=Math.sqrt(rets.reduce(function(a,b){return a+(b-mu)*(b-mu)},0)/(rets.length-1)),vol=sd*Math.sqrt(52);
    var cum=1,peak=1,dd=0;rets.forEach(function(r){cum*=1+r;peak=Math.max(peak,cum);dd=Math.min(dd,cum/peak-1)});
    var lvl=vol<0.12?['کم','up']:vol<0.22?['متوسط','gold']:['زیاد','dn'];
    $('rzc-vol').innerHTML='<small>نوسان سالانه</small><b>'+PL(vol,0)+' <span class="lv '+lvl[1]+'">ریسک '+lvl[0]+'</span></b><i>S&amp;P 500 معمولاً حدود ۱۵ تا ۱۸٪</i>';
    $('rzc-dd').innerHTML='<small>بیشترین افت (۱ سال)</small><b>'+P(dd,0)+'</b><i>اگه همین ترکیب رو از یک سال پیش داشتی</i>'});
  // upcoming earnings of the holdings
  fetch(RAW+'/calendar/earnings.json?v='+Math.floor(Date.now()/3600000)).then(function(r){return r.ok?r.json():null}).then(function(j){var held={},out=[],today=new Date().toISOString().slice(0,10);pos.forEach(function(x){held[x.t]=1});
    Object.keys(j&&j.days||{}).sort().forEach(function(d){if(d<today)return;j.days[d].forEach(function(e){if(held[e.t])out.push('<a href="/pages/stock#'+esc(e.t)+'" class="ev"><b class="tk">'+esc(e.t)+'</b><span>'+day(d)+(e.time==='pre'?' قبل از بازار':e.time==='after'?' بعد از بازار':'')+'</span>'+(e.f!=null?'<small>پیش‌بینی EPS: <bdi dir="ltr">$'+e.f+'</bdi></small>':'')+'</a>')})});
    $('rzc-earn').innerHTML=out.length?out.join(''):'<p class="note">در ۴ هفته‌ی آینده گزارشی از سهم‌هات نیست.</p>'}).catch(function(){$('rzc-earn').innerHTML=''})}

/* ---------- my dashboard ---------- */
var CUR=0;
function me(){
  if(!LOGGED||!TOK){main(bar('me')+'<div class="card center"><h2>ورود به مسابقه</h2><p>با ایمیلت وارد شو تا پروفایل و داشبوردت رو ببینی. اگه هنوز پروفایل نداری، بعد از ورود می‌سازیش.</p><a class="btn" href="'+LOGIN+'">ورود با ایمیل</a></div>');return}
  main(bar('me')+'<div class="card empty">در حال بارگذاری…</div>');
  api('/me').then(function(j){
    if(j._s===401){main(bar('me')+'<div class="card center"><p>نشست منقضی شده؛ صفحه رو دوباره باز کن.</p><a class="btn" href="'+LOGIN+'">ورود دوباره</a></div>');return}
    ME=j;if(!j.profiles||!j.profiles.length){location.hash='#/new';return}
    if(!j.profiles.some(function(p){return p.id===CUR}))CUR=j.profiles[j.profiles.length-1].id;
    var p=j.profiles.filter(function(x){return x.id===CUR})[0];
    var tabs=j.profiles.length>1?'<div class="sorts">'+j.profiles.map(function(x){return '<button data-p="'+x.id+'" class="'+(x.id===CUR?'on':'')+'">'+esc(x.name)+'</button>'}).join('')+'</div>':'';
    main(bar('me')+tabs+'<div class="card"><div class="phead"><div><h2>'+esc(p.name)+wstars(p.wins)+'</h2>'+(p.strategy?'<p class="strat">'+esc(p.strategy)+'</p>':'')+'<small>از '+day(p.created)+' | <a href="#/p/'+p.id+'">صفحه‌ی عمومی</a> | <a href="#/rules">قوانین</a></small></div></div>'+summary(p,p.value)+
      ((p.positions||[]).length<3?'<p class="warn">برای حضور در رده‌بندی حداقل ۳ سهم لازمه (الان '+FA((p.positions||[]).length)+').</p>':'')+'<div id="rzc-ch"></div></div>'+
      '<div class="card" id="rzc-trade"><h3>خرید و فروش</h3>'+tradeForm(p)+'</div>'+
      '<div class="card"><h3>دارایی‌ها</h3>'+holdings(p,true)+'</div><div class="card" id="rzc-an"></div><div class="card"><h3>تاریخچه‌ی تریدها</h3>'+history(p,true)+'</div>'+
      (j.can_new?'':'<p class="note">پروفایل جدید بعدی از '+day(j.next_new)+'.</p>'));
    chart(p.id,'rzc-ch');bindTrade(p);analyze(p,'rzc-an');
    document.querySelectorAll('[data-p]').forEach(function(b){b.onclick=function(){CUR=+b.getAttribute('data-p');me()}});
    document.querySelectorAll('[data-cancel]').forEach(function(b){b.onclick=function(){b.disabled=true;api('/cancel',{method:'POST',body:{pid:p.id,oid:+b.getAttribute('data-cancel')}}).then(me)}});
    document.querySelectorAll('[data-sell]').forEach(function(b){b.onclick=function(){setSide('sell',b.getAttribute('data-sell'));$('rzc-trade').scrollIntoView({behavior:'smooth'})}});
  }).catch(function(){main(bar('me')+'<div class="card empty">ارتباط با سرور برقرار نشد؛ چند لحظه بعد دوباره امتحان کن.</div>')})}
function tradeForm(p){
  var held=(p.positions||[]).map(function(x){return '<option value="'+esc(x.t)+'">'+esc(x.t)+' ('+Number(x.qty).toLocaleString('en-US',{maximumFractionDigits:4})+')</option>'}).join('');
  return '<div class="side"><button data-side="buy" class="on">خرید</button><button data-side="sell">فروش</button></div>'+
    '<div id="rzc-buy"><label>نماد<div class="pick"><input id="rzc-t" placeholder="نماد یا اسم شرکت، مثلاً AAPL یا GLD" autocomplete="off" dir="ltr"><div class="sugg" id="rzc-sg"></div></div></label>'+
    '<label>مبلغ (دلار) <small>نقد در دسترس: '+D(p.cash)+'</small><input id="rzc-amt" inputmode="decimal" dir="ltr" placeholder="1000"></label><div class="quick" id="rzc-quick"></div></div>'+
    '<div id="rzc-sell" hidden><label>کدوم سهم؟<select id="rzc-st">'+held+'</select></label><label>تعداد سهم<input id="rzc-q" inputmode="decimal" dir="ltr"></label><div class="quick"><button data-frac="0.25">۲۵٪</button><button data-frac="0.5">۵۰٪</button><button data-frac="1">همه</button></div></div>'+
    '<label>چرا؟ (اختیاری، فارسی یا انگلیسی، تا ۵۰۰ حرف)<textarea id="rzc-note" maxlength="500" rows="2" dir="auto"></textarea></label>'+
    '<div class="est" id="rzc-est"></div><button class="btn" id="rzc-send">ثبت سفارش</button><p class="err" id="rzc-err"></p>'+
    '<p class="note">سفارش با <b>اولین قیمتی که بعد از ثبت منتشر می‌شه</b> انجام می‌شه (معمولاً تا ۱۵ دقیقه در ساعت بازار؛ اگه بازار بسته‌ست، شروع روز معاملاتی بعد).</p>'}
var SIDE='buy';
function setSide(s,t){SIDE=s;document.querySelectorAll('[data-side]').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-side')===s)});$('rzc-buy').hidden=s!=='buy';$('rzc-sell').hidden=s!=='sell';if(t&&$('rzc-st'))$('rzc-st').value=t;est()}
function est(){var box=$('rzc-est');if(!box)return;var Q=RZQ&&RZQ.q||{};
  if(SIDE==='buy'){var t=$('rzc-t').value.trim().toUpperCase(),a=parseFloat($('rzc-amt').value),q=Q[t];box.innerHTML=q&&a>0?'قیمت فعلی '+D(q[0])+' ← حدود '+N(a/q[0],4)+' سهم':(t&&!q&&t.length>0?'':'');}
  else{var s=$('rzc-st').value,n=parseFloat($('rzc-q').value),qq=Q[s];box.innerHTML=qq&&n>0?'قیمت فعلی '+D(qq[0])+' ← حدود '+D(n*qq[0]):''}}
function bindTrade(p){
  document.querySelectorAll('[data-side]').forEach(function(b){b.onclick=function(){setSide(b.getAttribute('data-side'))}});
  var inp=$('rzc-t'),box=$('rzc-sg');
  inp.addEventListener('input',function(){var q=inp.value.trim().toUpperCase();est();if(!q||!UNI){box.style.display='none';return}
    var res=rzRank(UNI,q,function(t){return t},function(t){return NAMES[t]||''}).slice(0,8);
    box.innerHTML=res.map(function(t){return '<div data-t="'+esc(t)+'"><span>'+esc(NAMES[t]||'')+'</span><b>'+esc(t)+'</b></div>'}).join('');box.style.display=res.length?'block':'none'});
  box.addEventListener('mousedown',function(e){var d=e.target.closest('[data-t]');if(!d)return;e.preventDefault();inp.value=d.getAttribute('data-t');box.style.display='none';est()});
  inp.addEventListener('blur',function(){setTimeout(function(){box.style.display='none'},150)});
  $('rzc-amt').addEventListener('input',est);$('rzc-q').addEventListener('input',est);$('rzc-st').addEventListener('change',est);
  $('rzc-quick').innerHTML=[0.1,0.25,0.5].map(function(f){return '<button data-amt="'+Math.floor(p.value*f)+'">'+FA(f*100)+'٪ پورتفو</button>'}).join('')+'<button data-amt="'+Math.floor(p.cash*100)/100+'">همه‌ی نقد</button>';
  document.querySelectorAll('[data-amt]').forEach(function(b){b.onclick=function(){$('rzc-amt').value=b.getAttribute('data-amt');est()}});
  document.querySelectorAll('[data-frac]').forEach(function(b){b.onclick=function(){var t=$('rzc-st').value,x=(p.positions||[]).filter(function(y){return y.t===t})[0];if(!x)return;var f=+b.getAttribute('data-frac');$('rzc-q').value=f===1?'all':(Math.floor(x.qty*f*10000)/10000);est()}});
  $('rzc-send').onclick=function(){var b=this,body={pid:p.id,side:SIDE,note:$('rzc-note').value};
    if(SIDE==='buy'){body.t=$('rzc-t').value.trim().toUpperCase();body.amount=parseFloat(String($('rzc-amt').value).replace(/,/g,''))}else{body.t=$('rzc-st').value;var q=$('rzc-q').value.trim();body.qty=q==='all'?'all':parseFloat(q)}
    b.disabled=true;$('rzc-err').textContent='';
    api('/order',{method:'POST',body:body}).then(function(j){b.disabled=false;if(j.ok){BOARD=null;me()}else $('rzc-err').innerHTML=esc(j.error||'خطا')+(j.max!=null?' (حداکثر حدود '+D(j.max,0)+')':'')+(j.cash!=null?' (در دسترس: '+D(j.cash)+')':'')})
      .catch(function(){b.disabled=false;$('rzc-err').textContent='ارتباط برقرار نشد'})}}

/* ---------- public profile ---------- */
function prof(id){
  main(bar('')+'<div class="card empty">در حال بارگذاری…</div>');
  api('/p/'+id).then(function(p){
    if(p._s!==200){main(bar('')+'<div class="card empty">این پروفایل پیدا نشد.</div>');return}
    var h=bar('')+'<div class="card"><div class="phead"><div><h2>'+esc(p.name)+wstars(p.wins)+'</h2>'+(p.strategy?'<p class="strat">'+esc(p.strategy)+'</p>':'')+'<small>از '+day(p.created)+'</small></div></div>'+
      '<div class="sum">'+(vsSpy(p,p.value)!=null?'<div><small>در برابر S&amp;P 500</small><b>'+P(vsSpy(p,p.value))+'</b></div>':'')+'<div><small>ارزش پورتفو</small><b>'+D(p.value)+'</b></div><div><small>بازده کل</small><b>'+P(p.value/10000-1)+'</b></div><div><small>سهم‌ها</small><b>'+FA(p.n_pos)+'</b></div><div><small>تریدها</small><b>'+FA(p.n_trades)+'</b></div></div>';
    if(p.locked){
      h+='<div class="lock">🔒 '+(p.unlock==='feb'?'برای عادلانه بودن مسابقه، سهم‌ها و تریدهای پروفایل‌ها تا <b>۱ فوریه ۲۰۲۷</b> نمایش داده نمی‌شه. از اون تاریخ برای مشترکین Stock Pro باز می‌شه.':
        'سهم‌ها، تریدها و کامنت‌های این پورتفو مخصوص مشترکین Stock Pro است.<div class="btns"><a class="btn" href="/products/stock-data-pro">اشتراک ماهانه <bdi dir="ltr">€7.99</bdi></a><a class="btn alt" href="/products/stock-data-pro-yearly">سالانه <bdi dir="ltr">€47.94</bdi></a></div>')+'</div></div>';
      main(h);return}
    h+='<div id="rzc-ch"></div></div><div class="card"><h3>دارایی‌ها</h3>'+holdings(p,false)+'</div><div class="card" id="rzc-an"></div><div class="card"><h3>تاریخچه‌ی تریدها</h3>'+history(p,false)+'</div>';
    if(ME&&ME.me&&ME.me.admin)h+='<p class="note">مدیر: <button class="lnk" id="rzc-hide">مخفی کردن این پروفایل</button></p>';
    main(h);chart(p.id,'rzc-ch');analyze(p,'rzc-an');var hb=$('rzc-hide');if(hb)hb.onclick=function(){api('/admin',{method:'POST',body:{pid:p.id,status:'hidden'}}).then(function(){BOARD=null;location.hash='#/'})};
  })}

/* ---------- router ---------- */
function route(){var h=location.hash.replace(/^#/,'')||'/';window.scrollTo(0,0);
  if(h==='/me')me();else if(h==='/new')create();else if(h==='/rules')rules();else if(/^\/p\/\d+$/.test(h))prof(+h.split('/')[2]);else board()}
window.addEventListener('hashchange',route);
var DATA=Promise.all([fetch(RAW+'/contest-data/universe.json?v='+Math.floor(Date.now()/3600000)).then(function(r){return r.ok?r.json():null}).catch(function(){return null}),liveQuotes(),loadAll().catch(function(){})]).then(function(x){
  var U=x[0];if(U){UNI=U.t;Object.keys(U.etf||{}).forEach(function(t){NAMES[t]=U.etf[t]+' (ETF)';ETFS[t]=1})}
  (ROWS||[]).forEach(function(r){if(!NAMES[r[C.t]])NAMES[r[C.t]]=r[C.n]});
  if(TOK&&!ME)api('/me').then(function(j){if(j&&j.profiles)ME=j}).catch(function(){});
});
route();
