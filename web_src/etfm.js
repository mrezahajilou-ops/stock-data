/* ETF pages: the return ranking (switch period, show all), the fund finder (search + sort), the long
   intro and the holdings list (show all). Shared by all five editions: etf_pages.py puts it on each page;
   the Persian loader (etf.js) calls ETFM(box) after it drops a fragment in. Safe to run more than once. */
(function () {
  function $$(r, s) { return [].slice.call(r.querySelectorAll(s)) }
  function ETFM(root) {
    root = root || document;
    $$(root, '.sa-etf').forEach(function (art) {
      if (art.__etfm) return;
      art.__etfm = 1;

      // return ranking: period buttons re-order the list and redraw the bars
      $$(art, '.erk').forEach(function (box) {
        var ol = box.querySelector('ol.erk-l'), more = box.querySelector('.erk-more');
        function draw(k) {
          var li = $$(ol, 'li'), mx = 0;
          li.forEach(function (x) { var v = parseFloat(x.getAttribute('data-' + k)); if (isFinite(v)) mx = Math.max(mx, Math.abs(v)) });
          li.sort(function (a, b) {
            var va = parseFloat(a.getAttribute('data-' + k)), vb = parseFloat(b.getAttribute('data-' + k));
            return (isFinite(vb) ? vb : -9) - (isFinite(va) ? va : -9);
          });
          li.forEach(function (x, i) {
            var v = parseFloat(x.getAttribute('data-' + k)), bar = x.querySelector('.erk-b i');
            x.querySelector('.erk-n').textContent = i + 1;
            x.querySelector('em').innerHTML = x.getAttribute('data-' + k + 'f') || '—';
            bar.style.width = (isFinite(v) && mx ? Math.max(2, Math.abs(v) / mx * 100) : 0) + '%';
            bar.className = isFinite(v) && v < 0 ? 'n' : '';
            ol.appendChild(x);
          });
        }
        $$(box, '.erk-p button').forEach(function (b) {
          b.addEventListener('click', function () {
            $$(box, '.erk-p button').forEach(function (o) { o.classList.toggle('on', o === b); o.setAttribute('aria-pressed', o === b) });
            draw(b.getAttribute('data-p'));
          });
        });
        if (more) more.addEventListener('click', function () {
          var cut = ol.classList.toggle('cut');
          more.textContent = more.getAttribute(cut ? 'data-all' : 'data-less');
          if (cut) box.scrollIntoView({ block: 'start', behavior: 'smooth' });
        });
      });

      // fund finder: type to filter, buttons to sort
      $$(art, '.etfbox').forEach(function (box) {
        var tb = box.querySelector('.etftbl tbody'), q = box.querySelector('input.etfq'), cnt = box.querySelector('.etfcnt'), none = box.querySelector('.etfnone');
        if (!tb) return;
        var rows = $$(tb, 'tr');
        function filter() {
          var s = (q && q.value || '').trim().toLowerCase(), n = 0;
          rows.forEach(function (r) {
            var hit = !s || (r.getAttribute('data-s') || '').indexOf(s) >= 0;
            if (hit) { r.removeAttribute('hidden'); n++ } else r.setAttribute('hidden', '');
          });
          if (cnt) cnt.textContent = (cnt.getAttribute('data-f') || '%n').replace('%n', n);
          if (none) none.hidden = n > 0;
        }
        if (q) {
          q.addEventListener('input', filter);
          q.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter') {
              var first = rows.filter(function (r) { return !r.hasAttribute('hidden') });
              if (first.length === 1) { var a = first[0].querySelector('a'); if (a) location.href = a.getAttribute('href') }
              q.blur();
            }
          });
        }
        $$(box, '.etfsort button').forEach(function (b) {
          b.addEventListener('click', function () {
            var k = b.getAttribute('data-k'), asc = k === 'k' || k === 'pe';
            $$(box, '.etfsort button').forEach(function (o) { o.classList.toggle('on', o === b); o.setAttribute('aria-pressed', o === b) });
            rows.sort(function (a, c) {
              var va = parseFloat(a.getAttribute('data-' + k)), vc = parseFloat(c.getAttribute('data-' + k));
              var fa = isFinite(va), fc = isFinite(vc);
              if (!fa || !fc) return fa ? -1 : fc ? 1 : 0;        // a fund without the number goes last
              return asc ? va - vc : vc - va;
            });
            rows.forEach(function (r) { tb.appendChild(r) });
          });
        });
      });

      // long intro: three lines and a 'read more' on phones
      $$(art, '.etfintro').forEach(function (p) {
        var b = p.nextElementSibling;
        if (!b || !b.classList.contains('etfmore')) return;
        if (innerWidth > 700 || p.scrollHeight <= p.clientHeight + 4) { p.classList.remove('clip'); b.remove(); return }
        b.hidden = false;
        b.addEventListener('click', function () {
          var c = p.classList.toggle('clip');
          b.textContent = b.getAttribute(c ? 'data-more' : 'data-less');
        });
      });

      // holdings: the first ten, then all
      $$(art, '.hold-more').forEach(function (b) {
        var t = b.parentNode.querySelector('table.hold');
        if (!t) return;
        b.addEventListener('click', function () {
          var cut = t.classList.toggle('cut');
          b.textContent = b.getAttribute(cut ? 'data-all' : 'data-less');
        });
      });
    });
  }
  window.ETFM = ETFM;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { ETFM() }); else ETFM();
})();
