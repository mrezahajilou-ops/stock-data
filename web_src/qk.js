/* Quick keys: the sticky bar on long pages (stock pages, the stock analysis tool, ETF pages).
   Four keys jump to the parts people look for, the one in view lights up, and a house and a magnifier
   take you home or to another stock from anywhere on the page. Language-free: every word on it is
   in the markup, so the same code serves all five sites.

   <nav class="qkb" data-ph="Search any stock" data-none="No match" data-idx="/assets/search.json"
        data-url="/stocks/{l}/">
     <a class="qkb-i qkb-home" href="/" aria-label="Home">…</a>
     <div class="qkb-k"><a href="#s-ov">Overview</a> … </div>
     <button class="qkb-i qkb-find" type="button" aria-label="Search">…</button>
   </nav>

   data-idx: a JSON list [{t, n, u?}] fetched the first time the search opens. Instead, a page can
   set window.QK_INDEX = function () { return [...] } (the analysis tool already holds its list).
   data-url: where a result goes; {t} = ticker, {l} = ticker in lower case. data-hash="1" makes a
   result set location.hash instead (the analysis tool reads the ticker from the hash).
   The keys never change location.hash, which the analysis tool uses for the ticker. */
(function () {
  function $$(r, s) { return [].slice.call(r.querySelectorAll(s)) }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] }) }

  function QK(nav) {
    if (!nav || nav.__qk) return;
    nav.__qk = 1;
    var keys = $$(nav, '.qkb-k a'), row = nav.querySelector('.qkb-k'), off = 0, ticking = false, cur = -1;

    // a header the host page keeps fixed at the top (the Shopify theme) pushes the bar down
    function hostTop() {
      var o = 0, els = document.elementsFromPoint ? document.elementsFromPoint(innerWidth / 2, 1) : [];
      for (var i = 0; i < els.length; i++) {
        var el = els[i];
        if (nav.contains(el) || el === document.body || el === document.documentElement) continue;
        for (var n = el; n && n !== document.body; n = n.parentElement) {
          if (nav.contains(n)) break;
          var p = getComputedStyle(n).position;
          if (p === 'fixed' || p === 'sticky') {
            var r = n.getBoundingClientRect();
            if (r.top <= 1 && r.bottom > 0 && r.height < innerHeight / 3) o = Math.max(o, r.bottom);
            break;
          }
        }
      }
      return Math.round(o);
    }
    function inpage(a) { return (a.getAttribute('href') || '').charAt(0) === '#' }
    function target(a) {
      if (!inpage(a)) return null;
      var el = document.getElementById(a.getAttribute('href').slice(1));
      return el && el.offsetParent !== null ? el : null;     // hidden (display:none) parts of the page are skipped
    }
    function update() {
      ticking = false;
      if (!nav.isConnected) {            // the analysis tool redraws its page for each stock: drop the old bar
        removeEventListener('scroll', tick); removeEventListener('resize', tick); return;
      }
      var o = hostTop();
      if (o !== off) { off = o; nav.style.top = off + 'px' }
      var nr = nav.getBoundingClientRect();
      nav.classList.toggle('stuck', nr.top <= off + 0.5 && (window.scrollY || 0) > 40);
      var line = nr.bottom + 24, act = -1;
      keys.forEach(function (a, i) {
        if (!inpage(a)) return;          // a key to another page is always available and never 'in view'
        var t = target(a);
        a.classList.toggle('off', !t);
        if (t && t.getBoundingClientRect().top <= line) act = i;
      });
      if (act < 0 && keys.length) act = 0;
      if (act !== cur) {
        cur = act;
        keys.forEach(function (a, i) { a.classList.toggle('on', i === act); if (i === act) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current') });
        var a = keys[act];
        if (a && row.scrollWidth > row.clientWidth + 2) {
          var l = a.offsetLeft - row.offsetLeft, rr = l + a.offsetWidth;
          if (l < row.scrollLeft || rr > row.scrollLeft + row.clientWidth) row.scrollTo({ left: l - 12, behavior: 'smooth' });
        }
      }
    }
    function tick() { if (!ticking) { ticking = true; requestAnimationFrame(update) } }
    addEventListener('scroll', tick, { passive: true });
    addEventListener('resize', tick);
    keys.forEach(function (a) {
      a.addEventListener('click', function (ev) {
        if (!inpage(a)) return;
        ev.preventDefault();
        var t = target(a);
        if (!t) return;
        close();
        var y = t.getBoundingClientRect().top + (window.scrollY || 0) - nav.offsetHeight - off - 10;
        // a short hop glides; a long one (several screens) jumps, so nobody waits for the page to roll past
        var far = Math.abs(y - (window.scrollY || 0)) > innerHeight * 3;
        window.scrollTo({ top: Math.max(0, y), behavior: far ? 'auto' : 'smooth' });
      });
    });

    /* ---- search ---- */
    var find = nav.querySelector('.qkb-find'), box, inp, res, list = null, loading = null, sel = 0, hits = [];
    function load() {
      if (list) return Promise.resolve(list);
      if (typeof window.QK_INDEX === 'function') { var l = window.QK_INDEX(); if (l && l.length) { list = l; return Promise.resolve(list) } }
      if (!loading) loading = fetch(nav.getAttribute('data-idx')).then(function (r) { return r.json() }).then(function (j) { list = j; return j }).catch(function () { loading = null; return [] });
      return loading;
    }
    function url(x) {
      if (x.u) return x.u;
      var p = nav.getAttribute('data-url') || '/stocks/{l}/';
      return p.replace('{t}', x.t).replace('{l}', x.t.toLowerCase());
    }
    // Arabic and Persian spellings vary (alef with or without hamza, Arabic or Persian yeh and kaf, teh marbuta):
    // compare a folded form. Written as \u escapes so this file stays free of right-to-left script.
    function fold(s) {
      return String(s || '').toLowerCase().replace(/[\u064B-\u0652\u0640]/g, '').replace(/[\u0623\u0625\u0622\u0671]/g, '\u0627')
        .replace(/[\u0649\u064A\u06CC]/g, '\u06CC').replace(/[\u0643\u06A9]/g, '\u06A9').replace(/\u0629/g, '\u0647').replace(/\u0624/g, '\u0648').replace(/\u0626/g, '\u06CC');
    }
    function match(q) {
      q = q.trim();
      if (!q || !list) return [];
      var Q = q.toUpperCase(), lq = fold(q), out = [[], [], [], [], []];
      for (var i = 0; i < list.length; i++) {
        var x = list[i], t = (x.t || '').toUpperCase(), n = x.f || (x.f = fold(x.n)), k;
        if (t === Q) k = 0;
        else if (t.indexOf(Q) === 0) k = 1;
        else if (n.indexOf(lq) === 0) k = 2;
        else if (n.indexOf(' ' + lq) >= 0) k = 3;
        else if (lq.length > 1 && n.indexOf(lq) >= 0) k = 4;
        else continue;
        if (out[k].length < 8) out[k].push(x);
      }
      return out[0].concat(out[1], out[2], out[3], out[4]).slice(0, 8);
    }
    function draw() {
      hits = match(inp.value);
      sel = 0;
      if (!inp.value.trim()) { res.innerHTML = ''; return }
      if (!list) { res.innerHTML = '<p class="qkb-m">…</p>'; return }
      res.innerHTML = hits.length ? hits.map(function (x, i) {
        return '<a href="' + esc(url(x)) + '" data-i="' + i + '"' + (i === 0 ? ' class="sel"' : '') + '><b dir="ltr">' + esc(x.t) + '</b><span dir="auto">' + esc(x.n || '') + '</span></a>';
      }).join('') : '<p class="qkb-m">' + esc(nav.getAttribute('data-none') || '—') + '</p>';
    }
    function go(x) {
      if (!x) return;
      if (nav.getAttribute('data-hash') && !x.u) {
        close();
        location.hash = '#' + x.t;
        window.scrollTo({ top: 0 });
        return;
      }
      location.href = url(x);
    }
    function open() {
      if (!box) {
        box = document.createElement('div');
        box.className = 'qkb-s';
        box.innerHTML = '<div class="qkb-sf"><input type="search" autocomplete="off" autocapitalize="characters" spellcheck="false" enterkeyhint="go" dir="auto">' +
          '<button type="button" class="qkb-x" aria-label="×">✕</button></div><div class="qkb-r"></div>';
        nav.appendChild(box);
        inp = box.querySelector('input'); res = box.querySelector('.qkb-r');
        inp.placeholder = nav.getAttribute('data-ph') || '';
        inp.addEventListener('input', function () { load().then(draw) });
        inp.addEventListener('keydown', function (ev) {
          if (ev.key === 'Escape') { close(); find.focus() }
          else if (ev.key === 'Enter') { ev.preventDefault(); go(hits[sel] || hits[0]) }
          else if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
            ev.preventDefault();
            if (!hits.length) return;
            sel = (sel + (ev.key === 'ArrowDown' ? 1 : hits.length - 1)) % hits.length;
            $$(res, 'a').forEach(function (a, i) { a.classList.toggle('sel', i === sel) });
          }
        });
        res.addEventListener('click', function (ev) {
          var a = ev.target.closest('a[data-i]');
          if (!a || !nav.getAttribute('data-hash')) return;
          ev.preventDefault(); go(hits[+a.getAttribute('data-i')]);
        });
        box.querySelector('.qkb-x').addEventListener('click', close);
      }
      nav.classList.add('open');
      find.setAttribute('aria-expanded', 'true');
      inp.value = ''; res.innerHTML = '';
      inp.focus();
      load();
    }
    function close() {
      if (!nav.classList.contains('open')) return;
      nav.classList.remove('open');
      find && find.setAttribute('aria-expanded', 'false');
      if (inp) inp.blur();
    }
    if (find) {
      find.setAttribute('aria-expanded', 'false');
      find.addEventListener('click', function () { nav.classList.contains('open') ? close() : open() });
      document.addEventListener('click', function (ev) { if (!nav.contains(ev.target)) close() });
    }
    update();
    setTimeout(update, 600);
  }
  window.QK = QK;
  function boot() { $$(document, 'nav.qkb').forEach(QK) }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
