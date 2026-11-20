/* ETF section. Index: every fund in one scrollable box. Click a row -> that fund's own deep page.
   Free on the Persian site: the S&P 500 funds. Everything else needs Stock Pro. */
var EAPI = (window.RZS_API || 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data/main/data') + '/etfs';
var FREE = {VOO: 1, IVV: 1, SPY: 1, SPLG: 1, RSP: 1};
var ACC = !!window.RZS_ACCESS;
var SUB = window.RZS_SUB_URL || '/products/stock-data-pro';
var SUBY = window.RZS_SUB_Y || '/products/stock-data-pro-yearly';
var IDX = null, SORT = 'd_cagr', DIR = -1, Q = '', CACHE = {};

function open_(t) { return ACC || !!FREE[t]; }
function fa(t, k) { var o = FA[t]; return o && o[k] ? o[k] : ''; }
function cls_(c) { return FA_CLS[c] || c || '—'; }
function foc(f) { return FA_FOCUS[f] || f || ''; }
function sgn(v, d) { if (v == null || !isFinite(v)) return '—'; var s = (v * 100).toFixed(d == null ? 1 : d) + '%'; return v > 0 ? '+' + s : s; }
function cl(v) { return v == null || !isFinite(v) ? '' : (v > 0 ? ' style="color:#4FA37A"' : (v < 0 ? ' style="color:#C8534F"' : '')); }
function ltr(s) { return '<span class="ltr">' + esc(s) + '</span>'; }

/* ------------------------------------------------------------------ index */
var COLS = [
  ['d_name', 'صندوق', 0],
  ['d_cls', 'نوع', 1],
  ['d_y1', 'بازدهی یک سال', 0],
  ['d_cagr', 'میانگین سالانه', 0],
  ['d_n', 'تعداد سهام', 1],
  ['d_pe', 'P/E امروز', 0],
  ['d_peavg', 'میانگین P/E تاریخی', 1]
];

function val(e, k) {
  if (k === 'd_name') return e.t;
  if (k === 'd_cls') return cls_(e.cls);
  if (k === 'd_y1') return e.y1 == null ? -99 : e.y1;
  if (k === 'd_cagr') return e.cagr == null ? -99 : e.cagr;
  if (k === 'd_n') return e.holdings_n == null ? -1 : e.holdings_n;
  if (k === 'd_pe') return e.pe == null ? -1 : e.pe;
  if (k === 'd_peavg') return e.pe_avg == null ? -1 : e.pe_avg;
  return 0;
}

function rows() {
  var l = (IDX.etfs || []).slice();
  if (Q) {
    var q = Q.toLowerCase();
    l = l.filter(function (e) {
      return e.t.toLowerCase().indexOf(q) >= 0 || (e.name || '').toLowerCase().indexOf(q) >= 0 ||
        fa(e.t, 'n').indexOf(Q) >= 0 || cls_(e.cls).indexOf(Q) >= 0 || foc(e.focus).indexOf(Q) >= 0;
    });
  }
  l.sort(function (a, b) {
    var x = val(a, SORT), y = val(b, SORT);
    if (typeof x === 'string') return DIR * x.localeCompare(y);
    return DIR * (x - y);
  });
  return l;
}

function drawIndex() {
  var l = rows(), h = '';
  h += '<div class="card etfbox"><div class="etfhd">' +
    '<div><b style="font-size:15px">' + (IDX.etfs || []).length + ' صندوق بزرگ دنیا</b>' +
    '<div class="mut" style="font-size:12.5px">روی هر ردیف بزن تا صفحه‌ی کامل همان صندوق باز شود</div></div>' +
    '<div class="f"><input id="rzf-q" placeholder="جستجو: نماد، اسم یا نوع…" value="' + esc(Q) + '" autocomplete="off"></div>' +
    '</div><div class="etfscroll"><table class="etftbl"><thead><tr>';
  COLS.forEach(function (c) {
    h += '<th data-k="' + c[0] + '" class="' + (SORT === c[0] ? 'on' : '') + (c[2] ? ' hm' : '') + '">' + c[1] +
      (SORT === c[0] ? (DIR < 0 ? ' ↓' : ' ↑') : '') + '</th>';
  });
  h += '</tr></thead><tbody>';
  if (!l.length) h += '<tr><td colspan="7" class="empty">چیزی پیدا نشد.</td></tr>';
  l.forEach(function (e) {
    var op = open_(e.t);
    h += '<tr data-t="' + e.t + '"' + (op ? '' : ' class="lk"') + '>' +
      '<td><div class="nm"><b>' + e.t + (op ? '' : ' <span class="lock">🔒</span>') + '</b>' +
      '<span>' + esc(fa(e.t, 'n') || e.name) + '</span></div></td>' +
      '<td class="hm"><span class="tag">' + esc(cls_(e.cls)) + '</span> <span class="mut" style="font-size:12px">' + esc(foc(e.focus)) + '</span></td>' +
      '<td class="n"' + cl(e.y1) + '>' + sgn(e.y1) + '</td>' +
      '<td class="n"' + cl(e.cagr) + '>' + sgn(e.cagr) + '</td>' +
      '<td class="n hm">' + (e.holdings_n == null ? '—' : e.holdings_n) + '</td>' +
      '<td class="n">' + (e.pe == null ? '—' : x1(e.pe)) + '</td>' +
      '<td class="n hm">' + (e.pe_avg == null ? '—' : x1(e.pe_avg)) + '</td>' +
      '</tr>';
  });
  h += '</tbody></table></div></div>';
  h += '<p class="note">ستون P/E را خودمان از شرکت‌های داخل هر صندوق حساب می‌کنیم، با همان وزن‌هایی که خود صندوق دارد و همان اعدادی که در صفحه‌ی تحلیل سهم می‌بینی. وقتی صندوق سهام ندارد یا بیشتر شرکت‌هایش خارج از آمریکا هستند، این ستون خالی می‌ماند. ستون میانگین P/E تاریخی از روزی که شروع به ثبت کرده‌ایم پر می‌شود؛ هیچ‌جای دنیا این عدد برای ETF منتشر نمی‌شود چون به ترکیب صندوق در همان روز بستگی دارد.</p>';
  if (!ACC) h += lockNote();
  $('rzf-main').innerHTML = h;
  var q = $('rzf-q');
  if (q) q.oninput = function () { Q = this.value.trim(); var p = this.selectionStart; drawIndex(); var n = $('rzf-q'); if (n) { n.focus(); try { n.setSelectionRange(p, p) } catch (e) {} } };
}

function lockNote() {
  return '<div class="card" style="border-color:var(--ac)"><h3>🔒 صندوق‌های اس‌اند‌پی ۵۰۰ برای همه باز است</h3>' +
    '<p class="mut" style="font-size:14px;margin:0 0 12px">صفحه‌ی کامل بقیه‌ی صندوق‌ها — ترکیب سهام و وزن‌ها، نمودار قیمت، بازدهی دوره‌ای و نسبت‌های محاسبه‌شده — برای مشترکین استاک پرو باز است.</p>' +
    '<a class="btn" href="' + SUB + '">اشتراک ماهانه</a> <a class="btn ghost" href="' + SUBY + '">اشتراک سالانه</a></div>';
}

/* ----------------------------------------------------------------- detail */
function spark(ch) {
  if (!ch || ch.length < 3) return '';
  var v = ch.map(function (p) { return p[1] }), mn = Math.min.apply(null, v), mx = Math.max.apply(null, v), W = 600, H = 120, pad = 6;
  if (mx - mn < 1e-9) mx = mn + 1;
  var d = v.map(function (y, i) {
    var x = pad + i * (W - 2 * pad) / (v.length - 1), yy = H - pad - (y - mn) / (mx - mn) * (H - 2 * pad);
    return (i ? 'L' : 'M') + x.toFixed(1) + ' ' + yy.toFixed(1);
  }).join(' ');
  var up = v[v.length - 1] >= v[0], c = up ? '#4FA37A' : '#C8534F';
  return '<svg class="spark" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" aria-hidden="true">' +
    '<path d="' + d + '" fill="none" stroke="' + c + '" stroke-width="2.5" stroke-linejoin="round"/></svg>';
}

function barRow(lb, v, mx) {
  var w = (v == null || !isFinite(v) || !mx) ? 0 : Math.max(0, Math.min(100, v / mx * 100));
  return '<div class="r"><div class="lb">' + esc(lb) + '</div><div class="tr"><b style="width:' + w.toFixed(1) + '%"></b></div>' +
    '<div class="vl">' + (v == null ? '—' : v.toFixed(2) + '%') + '</div></div>';
}

function detail(t, d) {
  var w = d.weighted || {}, r = d.returns || {}, h = '';
  h += '<button class="back" id="rzf-back">◀ برگشت به فهرست ۵۰ صندوق</button>';
  h += '<div class="card"><div class="dhead"><div>' +
    '<h1 style="margin:0 0 2px"><span class="ltr">' + esc(t) + '</span> — ' + esc(fa(t, 'n') || d.name) + '</h1>' +
    '<p class="sub" style="margin:0">' + ltr(d.name) + ' · ' + esc(cls_(d.cls)) + ' · ' + esc(foc(d.focus)) +
    (d.issuer ? ' · ' + ltr(d.issuer) : '') + (d.since ? ' · از سال ' + d.since : '') + '</p></div>' +
    '<div style="text-align:left"><div class="px">$' + (d.price == null ? '—' : d.price.toFixed(2)) + '</div>' +
    '<div class="mut" style="font-size:12.5px;direction:ltr;unicode-bidi:isolate">' + esc(d.price_date || '') + '</div></div></div>';
  if (fa(t, 'i')) h += '<p style="font-size:15.5px;margin:12px 0 0">' + esc(fa(t, 'i')) + '</p>';
  h += '</div>';

  if (d.chart && d.chart.length > 2) h += '<div class="card"><h3>نمودار قیمت</h3>' + spark(d.chart) +
    '<p class="note">از ' + esc(d.chart[0][0]) + ' تا ' + esc(d.chart[d.chart.length - 1][0]) + '</p></div>';

  h += '<div class="card"><h3>بازدهی</h3><div class="kv">' +
    kvi('یک ماه', sgn(r.m1), r.m1) + kvi('سه ماه', sgn(r.m3), r.m3) + kvi('از ابتدای سال', sgn(r.ytd), r.ytd) +
    kvi('یک سال', sgn(r.y1), r.y1) + kvi('سه سال', sgn(r.y3), r.y3) + kvi('پنج سال', sgn(r.y5), r.y5) +
    kvi('میانگین سالانه' + (d.cagr_years ? ' (' + d.cagr_years + ' سال)' : ''), sgn(d.cagr), d.cagr) +
    '</div><p class="note">بازدهی‌ها بر اساس قیمت است و سود نقدی پرداخت‌شده در آن حساب نشده؛ برای صندوق‌های پرسود نقدی بازدهی کل از این عدد بیشتر است.</p></div>';

  if (w.covered_pct != null && w.pe != null) {
    h += '<div class="card"><h3>شرکت‌های داخل صندوق، روی هم</h3><div class="kv">' +
      kvi('P/E وزنی', x1(w.pe)) + kvi('قیمت به فروش', x1(w.ps)) +
      kvi('رشد فروش یک سال', sgn(w.revenue_growth)) + kvi('حاشیه سود خالص', sgn(w.net_margin)) +
      kvi('میانگین امتیاز ما', x1(w.score)) + kvi('وزن شرکت‌های سودده', w.profitable_weight == null ? '—' : w.profitable_weight.toFixed(1) + '%') +
      '</div><p class="note">این اعداد از روی ' + (w.covered_n || 0) + ' شرکت از ' + (w.holdings_n || 0) +
      ' شرکت داخل صندوق حساب شده، که روی هم ' + (w.covered_pct == null ? '—' : w.covered_pct.toFixed(1)) +
      ' درصد وزن صندوق را می‌سازند' + (d.pe_history_n && d.pe_history_n < 20 ? '؛ میانگین تاریخی P/E از ' + esc(d.pe_since || '') + ' در حال جمع شدن است' : '') + '.</p></div>';
  } else if (w.not_equity) {
    h += '<div class="card"><h3>چرا اینجا P/E نیست</h3><p class="mut" style="font-size:14px;margin:0">این صندوق سهام شرکت نگه نمی‌دارد، پس نسبت قیمت به سود برایش معنا ندارد. بازدهی‌اش از قیمت خود دارایی پشت صندوق می‌آید، نه از سود شرکت‌ها.</p></div>';
  } else if (w.thin) {
    h += '<div class="card"><h3>چرا اینجا P/E نیست</h3><p class="mut" style="font-size:14px;margin:0">بیشتر شرکت‌های داخل این صندوق خارج از آمریکا هستند و ما آن‌ها را پوشش نمی‌دهیم، پس عددی که در می‌آمد فقط بخش کوچکی از صندوق را نشان می‌داد. ترجیح دادیم عدد نادرست ندهیم.</p></div>';
  }

  if (fa(t, 's')) h += '<div class="card"><h3>چطور کار می‌کند</h3><p style="font-size:15px;margin:0">' + esc(fa(t, 's')) + '</p></div>';

  if (d.holdings && d.holdings.length) {
    var mx = d.holdings[0].pct || 1;
    h += '<div class="card"><h3>بزرگ‌ترین دارایی‌های صندوق</h3><div class="holdwrap"><table class="hold"><thead><tr>' +
      '<th>شرکت</th><th>نماد</th><th>وزن</th></tr></thead><tbody>';
    d.holdings.forEach(function (x) {
      h += '<tr><td class="ltr">' + esc(x.name) + '</td><td class="n">' +
        (x.t ? '<a href="/pages/stock#' + esc(x.t) + '">' + esc(x.t) + '</a>' : '—') + '</td>' +
        '<td class="n">' + (x.pct == null ? '—' : x.pct.toFixed(2) + '%') + '</td></tr>';
    });
    h += '</tbody></table></div><p class="note">ترکیب صندوق از گزارش رسمی ' +
      (d.holdings_as_of ? 'تاریخ ' + esc(d.holdings_as_of) : '') + ' به کمیسیون بورس آمریکا؛ روی نماد هر شرکتی که پوشش می‌دهیم بزن تا تحلیل کاملش را ببینی.</p></div>';
    void mx;
  }

  if (d.ucits && d.ucits.ticker) {
    h += '<div class="card"><h3>اگر در اروپا هستی</h3><p style="font-size:14.5px;margin:0 0 6px">' +
      ltr(d.name) + ' در آمریکا ثبت شده و صندوق‌های آمریکایی آن برگه‌ی اطلاعاتی را که قانون اروپا می‌خواهد منتشر نمی‌کنند، پس سفارش خرید یک سرمایه‌گذار خرد در اتحادیه‌ی اروپا یا بریتانیا رد می‌شود — با هر کارگزاری. معادل اروپایی‌اش این است:</p>' +
      '<p style="margin:0"><b>' + ltr(d.ucits.ticker) + '</b> — ' + ltr(d.ucits.name) + '</p>' +
      (d.ucits.note ? '<p class="mut" style="font-size:13.5px;margin:6px 0 0">' + ltr(d.ucits.note) + '</p>' : '') +
      '<p class="note">در ترکیه، خاورمیانه و بیشتر آسیا معمولاً می‌شود همان صندوق آمریکایی را از طریق کارگزار بین‌المللی خرید، با قوانین هر کشور.</p></div>';
  }
  h += '<p class="note">این صفحه آموزشی است و توصیه‌ی خرید یا فروش نیست. قیمت‌ها به دلار آمریکاست.</p>';
  return h;
}

function kvi(k, v, col) {
  return '<div><span class="k">' + esc(k) + '</span><span class="v"' + (col === undefined ? '' : cl(col)) + '>' + v + '</span></div>';
}

function showDetail(t) {
  if (!open_(t)) { showLocked(t); return; }
  $('rzf-main').innerHTML = '<div class="card empty">در حال بارگذاری…</div>';
  if (CACHE[t]) { paint(t, CACHE[t]); return; }
  fetch(EAPI + '/' + t + '.json').then(function (r) { if (!r.ok) throw 0; return r.json() })
    .then(function (d) { CACHE[t] = d; paint(t, d) })
    .catch(function () { $('rzf-main').innerHTML = '<div class="card empty">اطلاعات این صندوق الان در دسترس نیست. چند لحظه بعد دوباره امتحان کن.<br><br><button class="btn ghost" id="rzf-back">برگشت به فهرست</button></div>'; bind(); });
}

function paint(t, d) { $('rzf-main').innerHTML = detail(t, d); bind(); try { window.scrollTo({top: $('rzf').offsetTop - 20, behavior: 'smooth'}) } catch (e) {} }

function showLocked(t) {
  var e = (IDX.etfs || []).filter(function (x) { return x.t === t })[0] || {t: t, name: t};
  var fake = {name: e.name, cls: e.cls, focus: e.focus, issuer: e.issuer, price: e.price,
    returns: {y1: e.y1, y3: e.y3, ytd: e.ytd}, cagr: e.cagr, cagr_years: e.cagr_years,
    weighted: {pe: e.pe, covered_pct: e.covered, covered_n: 0, holdings_n: e.holdings_n}};
  $('rzf-main').innerHTML = '<button class="back" id="rzf-back">◀ برگشت به فهرست ۵۰ صندوق</button>' +
    '<div class="plk"><div class="plk-b">' + detail(t, fake).replace(/<button class="back"[^<]*<\/button>/, '') + '</div>' +
    '<div class="plk-c"><div class="plk-box"><h3>🔒 ' + esc(fa(t, 'n') || e.name) + '</h3>' +
    '<p>صفحه‌ی کامل این صندوق — ترکیب سهام و وزن‌ها، نمودار قیمت، بازدهی دوره‌ای و نسبت‌های محاسبه‌شده — برای مشترکین استاک پرو باز است. صندوق‌های اس‌اند‌پی ۵۰۰ برای همه باز است.</p>' +
    '<a class="btn" href="' + SUB + '">اشتراک ماهانه</a> <a class="btn ghost" href="' + SUBY + '">اشتراک سالانه</a></div></div></div>';
  bind();
}

function bind() { var b = $('rzf-back'); if (b) b.onclick = function () { location.hash = '#etf'; go() }; }

/* ------------------------------------------------------------------- wire */
document.addEventListener('click', function (ev) {
  var th = ev.target.closest && ev.target.closest('#rzf .etftbl th');
  if (th && th.dataset.k) { if (SORT === th.dataset.k) DIR = -DIR; else { SORT = th.dataset.k; DIR = th.dataset.k === 'd_name' ? 1 : -1 } drawIndex(); return; }
  var tr = ev.target.closest && ev.target.closest('#rzf .etftbl tbody tr');
  if (tr && tr.dataset.t) { location.hash = '#etf/' + tr.dataset.t; }
});

function go() {
  if (!IDX) return;
  var m = (location.hash || '').match(/#etf\/([A-Za-z.]+)/);
  if (m) showDetail(m[1].toUpperCase()); else drawIndex();
}
window.addEventListener('hashchange', go);

fetch(EAPI + '/index.json').then(function (r) { return r.json() }).then(function (j) {
  IDX = j;
  var a = $('rzf-asof'); if (a && j.built) a.textContent = 'به‌روزرسانی: ' + j.built;
  go();
}).catch(function () { $('rzf-main').innerHTML = '<div class="card empty">فهرست صندوق‌ها الان در دسترس نیست؛ چند لحظه بعد صفحه رو دوباره باز کن.</div>' });
