/* Insider trading page (shared by every stock site; config in #ins-cfg, built by tools/insider.py).
   Live feed: worker /c/insider.json (SEC Form 4, refreshed every few minutes), re-read every 30 seconds.
   Tap a trade -> that stock's one-year price chart with every insider buy/sale (insider/<T>.json + prices/<T>.json);
   tap a name -> that person's trades. Facts only, no advice. */
(function () {
  var cfgEl = document.getElementById('ins-cfg');
  var C = cfgEl ? JSON.parse(cfgEl.textContent) : window.INS_CFG; if (!C || !document.getElementById('ins-t')) return;   // Shopify loader: window.INS_CFG
  var S = C.S, R = C.roles || S.roles;
  var TK = {}; (C.tk64 ? atob(C.tk64) : C.tk || '').split(',').forEach(function (t) { if (t) TK[t] = 1; });
  var $ = function (id) { return document.getElementById(id); };
  var tbody = $('ins-t').tBodies[0], tab = 0, shown = 30, rows = [], seen = {}, first = true, asof = null, open = null;
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var sl = function (t) { return C.su.replace('%s', encodeURIComponent(C.lc === false ? t : t.toLowerCase())); };
  var bdi = function (s) { return C.rtl ? '<bdi dir="ltr">' + s + '</bdi>' : s; };
  var nf = function (v, d) { try { return Number(v).toLocaleString(C.loc, { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 }); } catch (e) { return String(v); } };
  function money(v) { var a = Math.abs(v || 0); return '$' + (a >= 1e9 ? nf(a / 1e9, 2) + 'B' : a >= 1e6 ? nf(a / 1e6, 1) + 'M' : a >= 1e3 ? nf(Math.round(a / 1e3)) + 'K' : nf(Math.round(a))); }
  function title(s) { s = String(s || ''); return s === s.toUpperCase() ? s.toLowerCase().replace(/(^|[\s\-&(.\/])([a-z])/g, function (m, a, b) { return a + b.toUpperCase(); }).replace(/\b(Inc|Corp|Co|Ltd|Plc|Llc|Lp|Nv|Sa|Ag)\b/g, function (m) { return m; }) : s; }
  function role(r) {
    var x = String(r || '').toLowerCase(), k;
    if (/chief executive|\bceo\b/.test(x)) k = 'ceo'; else if (/chief financial|\bcfo\b/.test(x)) k = 'cfo'; else if (/chief operating|\bcoo\b/.test(x)) k = 'coo';
    else if (/chair/.test(x)) k = 'chair'; else if (/^president|\bpresident\b(?!.*vice)/.test(x) && !/vice/.test(x)) k = 'pres';
    else if (/general counsel|chief legal/.test(x)) k = 'law'; else if (/vice president|\bevp\b|\bsvp\b|\bvp\b/.test(x)) k = 'vp';
    else if (/director/.test(x)) k = 'dir'; else if (/10%|beneficial owner/.test(x)) k = 'own'; else if (/other/.test(x) || !x) k = 'oth'; else k = 'off';
    if (C.keep && r && k !== 'own' && k !== 'oth' && !/see remarks|^officer$/i.test(r)) return esc(r);
    return '<span title="' + esc(r) + '">' + esc(R[k] || r) + '</span>';
  }
  function ago(iso) {
    var m = Math.round((Date.now() - Date.parse(iso)) / 60000); if (!isFinite(m)) return '';
    if (m < 1) return S.now;
    var v = m < 60 ? m + ' ' + S.min : m < 1440 ? Math.round(m / 60) + ' ' + S.hr : Math.round(m / 1440) + ' ' + S.day;
    return S.ago.replace('%s', v);
  }
  function stamp(iso) { try { return new Date(iso).toLocaleString(C.loc, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); } catch (e) { return iso; } }
  function slink(t) { return TK[t] ? '<a class="tk" href="' + sl(t) + '">' + esc(t) + '</a>' : '<b class="tk">' + esc(t) + '</b>'; }
  function label(r) { var b = r.c === 'P'; return '<span class="ty ' + (b ? 'b' : 's') + (r.x ? 'p' : '') + '"' + (r.x ? ' title="' + esc(S.plan_tip) + '"' : '') + '>' + esc(r.x ? (b ? S.plan_b : S.plan) : (b ? S.buy : S.sell)) + '</span>'; }
  function holdPct(r) {
    if (!r.h || !r.q) return '';
    var before = r.c === 'P' ? r.h - r.q : r.h + r.q; if (before <= 0) return '';
    var p = r.q / before * 100; if (p < 0.5) return '';
    return '<small>' + S.of_hold.replace('%s', bdi((r.c === 'P' ? '+' : '−') + nf(Math.min(p, 999), p < 10 ? 1 : 0) + '%')) + '</small>';
  }

  function view() {
    var wk = Date.now() - 7 * 864e5, L = rows;
    if (tab === 1) L = rows.filter(function (r) { return r.c === 'P'; });
    else if (tab === 2) L = rows.filter(function (r) { return r.c === 'S'; });
    else if (tab === 3 || tab === 4) L = rows.filter(function (r) { return r.c === (tab === 3 ? 'P' : 'S') && Date.parse(r.f) >= wk; }).slice().sort(function (a, b) { return b.v - a.v; });
    return L;
  }
  function render() {
    var L = view(), h = '';
    L.slice(0, shown).forEach(function (r, i) {
      var nw = !first && !seen[r.a + r.c];
      h += '<tr class="r ' + (r.c === 'P' ? 'b' : 's') + (nw ? ' new' : '') + '" data-i="' + rows.indexOf(r) + '">' +
        '<td class="f" title="' + esc(stamp(r.f)) + '">' + esc(ago(r.f)) + '</td>' +
        '<td>' + slink(r.t) + (C.noco ? '' : '<small>' + esc(title(r.co)) + '</small>') + '</td>' +
        '<td><button class="who" type="button">' + bdi(esc(r.n)) + '</button></td>' +
        '<td class="ro">' + role(r.r) + '</td><td>' + label(r) + '</td>' +
        '<td class="n">' + bdi(nf(r.q)) + holdPct(r) + '</td><td class="n">' + bdi(r.p ? '$' + nf(r.p, 2) : '—') + '</td>' +
        '<td class="n v">' + bdi(money(r.v)) + '</td></tr>';
    });
    tbody.innerHTML = h || '<tr><td colspan="8" class="none">' + esc(rows.length ? S.none : S.loading) + '</td></tr>';
    $('ins-more').hidden = L.length <= shown;
    rows.forEach(function (r) { seen[r.a + r.c] = 1; });
    first = false;
    if (open) { var tr = tbody.querySelector('tr[data-i="' + rows.indexOf(open.r) + '"]'); if (tr) show(tr, open.r, open.k, true); else open = null; }
  }
  function summary(W) {
    var wk = Date.now() - 7 * 864e5, b = 0, s = 0, bv = 0, sv = 0;
    if (W) { b = W.b; s = W.s; bv = W.bv; sv = W.sv; } else rows.forEach(function (r) { if (Date.parse(r.f) < wk) return; if (r.c === 'P') { b++; bv += r.v; } else { s++; sv += r.v; } });
    var pct = bv + sv ? bv / (bv + sv) * 100 : 0;
    $('ins-sum').innerHTML = '<div class="k"><span>' + esc(S.wk) + '</span></div>' +
      '<div class="k b"><b>' + bdi(nf(b)) + '</b> ' + esc(S.nb) + '<em>' + bdi(money(bv)) + '</em></div>' +
      '<div class="k s"><b>' + bdi(nf(s)) + '</b> ' + esc(S.ns) + '<em>' + bdi(money(sv)) + '</em></div>' +
      '<div class="k bar"><span>' + esc(S.ratio) + ' ' + bdi(nf(pct, 0) + '%') + '</span><i><u style="width:' + pct.toFixed(1) + '%"></u></i></div>';
  }
  function upd() { if (asof) $('ins-upd').textContent = S.upd + ' ' + ago(asof); }

  function load() {
    fetch(C.feed + '?t=' + Math.floor(Date.now() / 30000)).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j || !j.rows) return;
      rows = j.rows.slice().sort(function (a, b) { return (b.f || '') < (a.f || '') ? -1 : (b.f || '') > (a.f || '') ? 1 : 0; });
      asof = j.as_of || j.checked; summary(j.wk); render(); upd();
    }).catch(function () {});
  }

  /* ---- detail row: stock chart or person history ---- */
  var cache = {};
  function getJ(path) { if (!cache[path]) cache[path] = fetch(C.raw + path + '?v=' + Math.floor(Date.now() / 3600000)).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); return cache[path]; }
  var norm = function (n) { return String(n || '').toLowerCase().replace(/[^a-z ]/g, '').replace(/\s+/g, ' ').trim(); };
  function hist(t, j) {   // 12 months of open-market trades for a stock: nightly file + live feed, de-duplicated
    var out = [], key = {};
    rows.forEach(function (r) { if (r.t !== t) return; var o = { n: r.n, d: r.d, c: r.c, q: r.q, p: r.p, v: r.v, x: r.x, r: r.r }; key[norm(o.n) + o.d + o.c + Math.round(o.q)] = 1; out.push(o); });
    ((j && j.data && j.data.rows) || []).forEach(function (r) {
      var x = String(r.x || '').toLowerCase(), c = x === 'buy' || x === 'automatic buy' ? 'P' : x === 'sell' || x === 'automatic sell' ? 'S' : null;
      if (!c || !r.d || !r.q) return;
      var k = norm(r.n) + r.d + c + Math.round(r.q); if (key[k]) return; key[k] = 1;
      out.push({ n: title(r.n), d: r.d, c: c, q: r.q, p: r.p, v: (r.q || 0) * (r.p || 0), x: x.indexOf('automatic') >= 0 ? 1 : 0, r: r.r });
    });
    var cut = new Date(Date.now() - 372 * 864e5).toISOString().slice(0, 10);
    return out.filter(function (o) { return o.d >= cut; }).sort(function (a, b) { return a.d < b.d ? 1 : -1; });
  }
  function chart(w, H) {
    var W = 720, Ht = 240, pl = 8, pr = 52, pt = 12, pb = 24;
    var cut = new Date(Date.now() - 372 * 864e5).toISOString().slice(0, 10);
    w = (w || []).filter(function (p) { return p[0] >= cut && p[1] > 0; });
    if (w.length < 4) return '';
    var t0 = Date.parse(w[0][0]), t1 = Date.parse(w[w.length - 1][0]), lo = Infinity, hi = 0;
    w.forEach(function (p) { lo = Math.min(lo, p[1]); hi = Math.max(hi, p[1]); });
    var X = function (d) { return pl + (Date.parse(d) - t0) / Math.max(1, t1 - t0) * (W - pl - pr); };
    var Y = function (v) { return pt + (hi - v) / Math.max(1e-9, hi - lo) * (Ht - pt - pb); };
    var path = w.map(function (p, i) { return (i ? 'L' : 'M') + X(p[0]).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join('');
    var price = function (d) { for (var i = 1; i < w.length; i++) if (w[i][0] >= d) return w[i][1]; return w[w.length - 1][1]; };
    var vmax = 1; H.forEach(function (o) { vmax = Math.max(vmax, o.v || 0); });
    var mk = H.filter(function (o) { return o.d >= w[0][0]; }).slice().reverse().map(function (o) {
      var x = X(o.d), y = Y(o.p && o.p >= lo * 0.7 && o.p <= hi * 1.3 ? Math.min(hi, Math.max(lo, o.p)) : price(o.d)), r = 4 + 9 * Math.sqrt((o.v || 0) / vmax), b = o.c === 'P';
      var pts = b ? [x, y - r, x - r, y + r * 0.8, x + r, y + r * 0.8] : [x, y + r, x - r, y - r * 0.8, x + r, y - r * 0.8];
      return '<polygon class="' + (b ? 'mb' : 'ms') + '" points="' + pts.map(function (v) { return v.toFixed(1); }).join(' ') + '"><title>' +
        esc(o.d + ' · ' + o.n + ' · ' + (b ? S.buy : S.sell) + ' ' + nf(o.q) + ' @ $' + nf(o.p || 0, 2) + ' = ' + money(o.v)) + '</title></polygon>';
    }).join('');
    var ticks = [lo, (lo + hi) / 2, hi].map(function (v) { return '<text x="' + (W - pr + 6) + '" y="' + (Y(v) + 4).toFixed(1) + '">$' + nf(v, v < 10 ? 2 : 0) + '</text>'; }).join('');
    var months = '', seenM = {};
    w.forEach(function (p) { var m = p[0].slice(0, 7); if (seenM[m] || p[0].slice(8) > '07') return; seenM[m] = 1;
      try { months += '<text x="' + X(p[0]).toFixed(1) + '" y="' + (Ht - 6) + '" class="m">' + esc(new Date(p[0] + 'T12:00:00Z').toLocaleString(C.loc, { month: 'short' })) + '</text>'; } catch (e) {} });
    return '<svg class="ins-ch" viewBox="0 0 ' + W + ' ' + Ht + '" role="img" dir="ltr"><path class="pl" d="' + path + '"/>' + mk + ticks + months + '</svg>' +
      '<p class="leg"><i class="lp"></i>' + esc(S.p_leg[0]) + '<i class="lb"></i>' + esc(S.p_leg[1]) + '<i class="ls"></i>' + esc(S.p_leg[2]) + '</p>';
  }
  function list(H, withStock) {
    return '<table class="ins-h"><tbody>' + H.slice(0, 25).map(function (o) {
      return '<tr class="' + (o.c === 'P' ? 'b' : 's') + '"><td>' + bdi(esc(o.d)) + '</td>' + (withStock ? '<td>' + slink(o.t) + '</td>' : '') + '<td>' + bdi(esc(o.n)) + '</td><td>' + label(o) + '</td><td class="n">' + bdi(nf(o.q)) + '</td><td class="n">' + bdi(o.p ? '$' + nf(o.p, 2) : '—') + '</td><td class="n v">' + bdi(money(o.v)) + '</td></tr>';
    }).join('') + '</tbody></table>';
  }
  function show(tr, r, k, keep) {
    var nx = tr.nextElementSibling; if (nx && nx.classList.contains('det')) nx.parentNode.removeChild(nx);
    if (!keep && open && open.r === r && open.k === k) { open = null; return; }
    open = { r: r, k: k };
    var d = document.createElement('tr'); d.className = 'det'; d.innerHTML = '<td colspan="8"><div class="ins-p"><button class="x" type="button" aria-label="' + esc(S.close) + '">×</button><div class="b">' + esc(S.loading) + '</div></div></td>';
    tr.parentNode.insertBefore(d, tr.nextSibling);
    var box = d.querySelector('.b');
    d.querySelector('.x').onclick = function () { d.parentNode.removeChild(d); open = null; };
    getJ('/insider/' + encodeURIComponent(r.t) + '.json').then(function (j) {
      var H = hist(r.t, j);
      if (k === 'who') {
        var me = norm(r.n), mine = H.filter(function (o) { return norm(o.n) === me || norm(o.n).split(' ').sort().join(' ') === me.split(' ').sort().join(' '); });
        rows.forEach(function (o) { if (o.t !== r.t && norm(o.n) === me) mine.push({ n: o.n, d: o.d, c: o.c, q: o.q, p: o.p, v: o.v, x: o.x, t: o.t }); });
        mine.forEach(function (o) { if (!o.t) o.t = r.t; });
        box.innerHTML = '<h3>' + esc(S.who_h).replace('%s', bdi(esc(r.n))) + '</h3><p class="note">' + bdi(esc(r.n)) + ' · ' + role(r.r) + ' · ' + esc(S.who_at) + ' ' + slink(r.t) + (C.noco ? '' : ' ' + esc(title(r.co))) + '</p>' + list(mine, true) + '<p class="note">' + esc(S.who_note) + '</p>';
        return;
      }
      return getJ('/prices/' + encodeURIComponent(r.t) + '.json').then(function (p) {
        var b = H.filter(function (o) { return o.c === 'P'; }), s = H.filter(function (o) { return o.c === 'S'; });
        var sum = function (A) { return A.reduce(function (a, o) { return a + (o.v || 0); }, 0); };
        box.innerHTML = '<h3>' + esc(S.p_h.replace('%s', r.t)) + '</h3>' + chart(p && p.w, H) +
          '<p>' + (H.length ? esc(S.p_sum).replace('%d', bdi(nf(b.length))).replace('%s', bdi(money(sum(b)))).replace('%d', bdi(nf(s.length))).replace('%s', bdi(money(sum(s)))) : esc(S.p_none)) + '</p>' +
          list(H, false) + (TK[r.t] ? '<p class="go"><a href="' + sl(r.t) + '">' + esc(S.open.replace('%s', r.t)) + '</a></p>' : '');
      });
    });
  }
  tbody.addEventListener('click', function (ev) {
    var tr = ev.target.closest('tr.r'); if (!tr || ev.target.closest('a')) return;
    var r = rows[+tr.getAttribute('data-i')]; if (!r) return;
    show(tr, r, ev.target.closest('.who') ? 'who' : 'stock');
  });
  [].forEach.call(document.querySelectorAll('.ins-tabs button'), function (b) {
    b.onclick = function () {
      [].forEach.call(document.querySelectorAll('.ins-tabs button'), function (x) { x.classList.remove('on'); x.removeAttribute('aria-selected'); });
      b.classList.add('on'); b.setAttribute('aria-selected', 'true'); tab = +b.getAttribute('data-k'); shown = 30; open = null; render();
    };
  });
  $('ins-more').onclick = function () { shown += 30; render(); };
  load(); setInterval(load, 30000); setInterval(upd, 20000);
})();
