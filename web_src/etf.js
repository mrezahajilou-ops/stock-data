/* Thin loader for the ETF section. Each page is an HTML fragment built by etf_fa_web.py with
   etf_pages.py (the builder the English site uses), under web/etf/. Address: #etf/ = the list,
   #etf/voo/ = one fund. Free on the Persian site: the S&P 500 funds; the rest needs Stock Pro. */
var FBASE = 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/main/web/etf/';
var FREE = {VOO: 1, IVV: 1, SPY: 1, SPYM: 1, RSP: 1};
var ACC = !!window.RZS_ACCESS;
var SUB = window.RZS_SUB_URL || '/products/stock-data-pro', SUBY = window.RZS_SUB_Y || '/products/stock-data-pro-yearly';
var FCACHE = {};
function tick() { var m = (location.hash || '').match(/#etf\/([A-Za-z.]+)/); return m ? m[1].toUpperCase() : ''; }
function lockBox(t) {
  return '<button class="back" data-back>◀ برگشت به فهرست ۵۰ صندوق</button><div class="lockbox"><h3>🔒 ' + esc(NAMES[t] || t) +
    ' <bdi dir="ltr">(' + esc(t) + ')</bdi></h3><p>صفحه‌ی کامل این صندوق — ترکیب سهام و وزن‌ها، نمودار قیمت، بازدهی دوره‌ای، ' +
    'ارزش‌گذاری شرکت‌های داخلش و اینکه از کدام کشور می‌شود خریدش — برای مشترکین استاک پرو باز است. صندوق‌های اس‌اند‌پی ۵۰۰ برای همه باز است.</p>' +
    '<a class="btn" href="' + SUB + '">اشتراک ماهانه</a> <a class="btn ghost" href="' + SUBY + '">اشتراک سالانه</a></div>';
}
function mark(box) {
  if (ACC) return;
  [].forEach.call(box.querySelectorAll('.etftbl tbody tr'), function (tr) {
    var a = tr.querySelector('a[href^="#etf/"]'); if (!a) return;
    var t = a.getAttribute('href').replace('#etf/', '').replace('/', '').toUpperCase();
    if (!FREE[t]) { tr.className = 'lk'; var b = tr.querySelector('b'); if (b && b.textContent.indexOf('🔒') < 0) b.insertAdjacentText('beforeend', ' 🔒'); }
  });
}
function show(html, isIndex) {
  var box = $('rzf-main'); box.innerHTML = html;
  if (isIndex) mark(box);
  if (window.ETFM) window.ETFM(box);                                   // ranking, fund finder, holdings toggle
  if (window.QK) window.QK(box.querySelector('nav.qkb'));              // the four-key bar on a fund page
  [].forEach.call(box.querySelectorAll('[data-back]'), function (b) { b.onclick = function () { location.hash = '#etf/' } });
}
function go() {
  var t = tick(), name = t ? t.toLowerCase() : 'index';
  if (t && !ACC && !FREE[t]) { show(lockBox(t)); window.scrollTo(0, $('rzf').offsetTop - 10); return; }
  if (FCACHE[name]) { show(FCACHE[name], !t); if (t) window.scrollTo(0, $('rzf').offsetTop - 10); return; }
  $('rzf-main').innerHTML = '<div class="card empty">در حال بارگذاری…</div>';
  fetch(FBASE + name + '.html?v=' + Math.floor(Date.now() / 300000)).then(function (r) { if (!r.ok) throw 0; return r.text() })
    .then(function (h) { FCACHE[name] = h; if (name === (tick() ? tick().toLowerCase() : 'index')) { show(h, !t); if (t) window.scrollTo(0, $('rzf').offsetTop - 10); } })
    .catch(function () { show('<div class="card empty">این صفحه الان در دسترس نیست؛ چند لحظه بعد دوباره امتحان کن.<br><br><button class="btn ghost" data-back>برگشت به فهرست</button></div>') });
}
window.addEventListener('hashchange', go);
go();
