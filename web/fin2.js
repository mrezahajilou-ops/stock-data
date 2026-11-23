/* Financials v2 for every stock, rendered in the browser (no extra files on the server).
   Data: the public stock-data engine — data/stocks/<T>.json (SEC annual + market + analysts), keystats/<T>.json
   (key stats, quarterly statements, estimate ranges), prices/<T>.json (weekly closes for historical valuation).
   Inside the stock analysis tool (#rzs-main) it replaces the stat cards with compact key statistics and the
   10-year table with a statements bar (Income statement · Balance sheet · Cash flow · Ratios · Forecast) and an
   Annual / Quarterly / TTM switch. Language: window.FIN2_CFG = {lang:'en'|'es'|'tr'|'fa'|'ar', raw:'https://raw...'}. */
(function () {
  var CFG = window.FIN2_CFG || {};
  var LANG = CFG.lang || 'en';
  var RAW = CFG.raw || 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data';
  var I18N = (window.FIN2_I18N || {})[LANG] || {};
  function T(s) { return I18N[s] || s; }
  var RTL = LANG === 'fa' || LANG === 'ar';
  // numbers inside right-to-left text: keep "$3.64T", "-$1.2B", "+5.0%" in their own left-to-right island
  function B(x) {
    x = String(x);
    if (!RTL || !/[\d$%]/.test(x) || x.indexOf('<bdi') >= 0) return x;
    // "a · b" pairs follow the label's right-to-left order, so isolate each value on its own
    if (x.indexOf(' · ') >= 0 && x.indexOf('<') < 0) return x.split(' · ').map(B).join(' · ');
    if (!/[\u0600-\u06FF]/.test(x) && x.indexOf('<') < 0) return '<bdi dir="ltr">' + x + '</bdi>';
    // mixed text: isolate each number only
    return x.replace(/(<[^>]*>)|([-−+]?\$?\d[\d.,]*(?:\s?[%TBMK])?(?:\s?–\s?\$?\d[\d.,]*[%TBMK]?)?)/g, function (m, tag, num) { return tag ? tag : '<bdi dir="ltr">' + num + '</bdi>'; });
  }
  function F(s) { var a = arguments, i = 0; return T(s).replace(/%(\d)\$s|%s/g, function (_, n) { return B(n ? a[+n] : a[++i]); }); }
  var LOC = { en: 'en-US', es: 'es-ES', tr: 'tr-TR', fa: 'fa-IR-u-ca-gregory-nu-latn', ar: 'ar-u-ca-gregory-nu-latn' }[LANG] || 'en-US';

  // ---------------------------------------------------------------- formatting (same rules as the server pages)
  var D = '—';
  function nn(v) { return v === null || v === undefined || (typeof v === 'number' && !isFinite(v)); }
  function usd(v, d) {
    if (nn(v)) return D; d = d === undefined ? 1 : d;
    var a = Math.abs(v), s = v < 0 ? '-' : '';
    if (a >= 1e12) return s + '$' + (a / 1e12).toFixed(2) + 'T';
    if (a >= 1e9) return s + '$' + (a / 1e9).toFixed(d) + 'B';
    if (a >= 1e6) return s + '$' + (a / 1e6).toFixed(0) + 'M';
    return s + '$' + a.toFixed(0);
  }
  // 23 Nov 2026: ±1000% and beyond comes from a near-zero base (an acquisition year, a tiny prior figure) and is shown
  // as >999%; a value that rounds to zero carries no sign; sub-cent EPS keeps its digits instead of reading $0.00.
  function pct(v, d) { if (nn(v)) return D; if (Math.abs(v) >= 10) return v > 0 ? '>999%' : '<−999%'; var s = (v * 100).toFixed(d || 0); if (+s === 0) s = (0).toFixed(d || 0); return s + '%'; }
  function sp(v) { if (nn(v)) return D; if (Math.abs(v) >= 10) return v > 0 ? '>+999%' : '<−999%'; var a = Math.abs(v * 100).toFixed(1); return (+a === 0 ? '' : (v >= 0 ? '+' : '−')) + a + '%'; }
  function eps(v) { if (nn(v)) return D; var a = Math.abs(v), dg = (a > 0 && a < 0.005) ? (a >= 0.0005 ? 3 : 4) : 2, s = a.toFixed(dg); return (v < 0 && +s !== 0 ? '−$' : '$') + s; }
  function x2(v, d) { if (nn(v)) return D; var s = v.toFixed(d === undefined ? 1 : d); return +s === 0 ? (0).toFixed(d === undefined ? 1 : d) : s; }
  function shr(v) { return nn(v) ? D : (Math.abs(v) >= 1e9 ? (v / 1e9).toFixed(2) + 'B' : (v / 1e6).toFixed(0) + 'M'); }
  function dol(v, d) { return nn(v) ? D : '$' + v.toFixed(d === undefined ? 2 : d); }
  function esc(s) { return String(s === undefined || s === null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function dd(s) { if (!s) return null; var m = String(s).slice(0, 10).match(/^(\d{4})-(\d{2})-(\d{2})$/); return m ? new Date(Date.UTC(+m[1], +m[2] - 1, +m[3])) : null; }
  function ep(ts) { return ts ? new Date(+ts * 1000) : null; }
  function days(a, b) { return (a - b) / 864e5; }
  function newer(end, fyEnd) { var a = dd(end), b = dd(fyEnd); return !!a && (!b || days(a, b) > 20); }
  var fmtM = new Intl.DateTimeFormat(LOC, { month: 'short', timeZone: 'UTC' });
  var fmtL = new Intl.DateTimeFormat(LOC, { month: 'long', timeZone: 'UTC' });
  var fmtD = new Intl.DateTimeFormat(LOC, { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
  var fmtF = new Intl.DateTimeFormat(LOC, { month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
  // English-style "Sep ’26"; in Persian/Arabic the apostrophe breaks right-to-left reading, so write "سپتامبر 2026"
  function mon(x) { if (!x) return ''; return LANG === 'fa' || LANG === 'ar' ? fmtM.format(x) + ' ' + x.getUTCFullYear() : fmtM.format(x).replace('.', '') + ' ’' + String(x.getUTCFullYear()).slice(2); }
  function fdate(s) { var x = dd(s); return x ? fmtF.format(x) : ''; }
  function sdate(x) { return x ? fmtD.format(x) : D; }

  // ---------------------------------------------------------------- data helpers
  function match(rows, end, n) {
    var de = dd(end); if (!de) return {};
    var best = null; n = n || 16;
    (rows || []).forEach(function (r) { var x = dd(r.end); if (x && Math.abs(days(x, de)) <= n) best = r; });
    return best || {};
  }
  function sum4(Q) {
    var out = [];
    for (var i = 3; i < Q.length; i++) {
      var w = Q.slice(i - 3, i + 1);
      if (days(dd(w[3].end), dd(w[0].end)) >= 300) continue;
      var r = { end: w[3].end }, keys = {};
      w.forEach(function (x) { Object.keys(x).forEach(function (k) { if (k !== 'end') keys[k] = 1; }); });
      Object.keys(keys).forEach(function (k) {
        var ok = true, s = 0;
        w.forEach(function (x) { if (nn(x[k])) ok = false; else s += x[k]; });
        if (ok) r[k] = s;
      });
      out.push(r);
    }
    return out;
  }
  function byEnd(a) { return (a || []).slice().sort(function (x, y) { return x.end < y.end ? -1 : 1; }); }
  function ttmInc(k) {
    // a quarter the source lists before its statement is out has only a few fields: leave it out of the sums
    var Q = byEnd(k.q_inc).filter(function (r) { return !nn(r.TotalRevenue); }), out = sum4(Q), cf = {}, last = {};
    sum4(qcf(k)).forEach(function (r) { cf[r.end] = r; });
    Q.forEach(function (r) { last[r.end] = r; });
    out.forEach(function (r) {
      var rv = r.TotalRevenue, c = cf[r.end] || {};
      r._sh = last[r.end].DilutedAverageShares;
      r.StockBasedCompensation = c.StockBasedCompensation;
      r.EBITDA = (!nn(r.OperatingIncome) && !nn(c.DepreciationAndAmortization)) ? r.OperatingIncome + c.DepreciationAndAmortization : null;
      if (!nn(r.GrossProfit) && !nn(r.OperatingIncome)) r._oth = r.GrossProfit - r.OperatingIncome - (r.ResearchAndDevelopment || 0);
      if (rv) [['_gm', 'GrossProfit'], ['_om', 'OperatingIncome'], ['_nm', 'NetIncome'], ['_em', 'EBITDA']].forEach(function (p) { if (!nn(r[p[1]])) r[p[0]] = r[p[1]] / rv; });
      if (r.PretaxIncome && !nn(r.TaxProvision)) r._tr = r.TaxProvision / r.PretaxIncome;
    });
    return out;
  }
  function qcf(k) { return byEnd(k.q_cf).filter(function (r) { return !nn(r.OperatingCashFlow); }); }
  function latest(k) {
    var I = ttmInc(k), C = sum4(qcf(k)), B = byEnd(k.q_bal).filter(function (r) { return !nn(r.TotalAssets); });
    return [I[I.length - 1] || {}, C[C.length - 1] || {}, B[B.length - 1] || {}];
  }
  function pxAt(W, end) {
    var e = String(end || '').slice(0, 10), best = null;
    for (var i = 0; i < W.length; i++) { if (W[i][0] <= e) best = W[i][1]; else break; }
    return best;
  }
  function histVal(W, a) {
    var p = pxAt(W, a.fy_end), sh = a.shares_diluted || a.shares_out;
    if (!p || !sh) return {};
    var mc = p * sh, ev = mc + (a.debt || 0) - (a.cash || 0), o = { price: p, mcap: mc, ev: ev };
    if (a.eps_diluted > 0) o.pe = p / a.eps_diluted;
    if (a.revenue) o.ps = mc / a.revenue;
    if (a.equity > 0) o.pb = mc / a.equity;
    if (a.fcf > 0) o.pfcf = mc / a.fcf;
    if (a.ebitda > 0) o.ev_ebitda = ev / a.ebitda;
    if (!nn(a.net_income)) o.ey = a.net_income / mc;
    if (!nn(a.fcf)) o.fy = a.fcf / mc;
    if (a.div_per_share) o.dy = a.div_per_share / p;
    return o;
  }

  // ---------------------------------------------------------------- table
  function table(cols, sub, rows, first) {
    // hide lines with no number in any column (e.g. inventory for a bank), and section titles left empty
    rows = rows.filter(function (r) { return r[2] === 'sec' || r[1].some(function (v) { return v !== D && v !== ''; }); });
    rows = rows.filter(function (r, i) { return r[2] !== 'sec' || (rows[i + 1] && rows[i + 1][2] !== 'sec'); });
    var th = cols.map(function (c) { return '<th>' + B(c) + '</th>'; }).join('');
    var ts = sub.map(function (c) { return '<th>' + B(c) + '</th>'; }).join('');
    var body = rows.map(function (r) {
      if (r[2] === 'sec') return '<tr class="sec"><td colspan="' + (cols.length + 1) + '">' + T(r[0]) + '</td></tr>';
      return '<tr class="' + (r[2] || '') + '"><td>' + T(r[0]) + '</td>' + r[1].map(function (v) { return '<td>' + B(v) + '</td>'; }).join('') + '</tr>';
    }).join('');
    var pe = sub.some(function (x) { return x; }) ? '<tr class="pe"><th>' + T('Period ending') + '</th>' + ts + '</tr>' : '';
    return '<div class="fb-tw"><table class="fb-t"><thead><tr><th>' + T(first || 'Fiscal year') + '</th>' + th + '</tr>' + pe + '</thead><tbody>' + body + '</tbody></table></div>';
  }
  function qtable(rows, spec, first) {
    // drop periods the source lists without any numbers
    rows = rows.filter(function (r) { return spec.some(function (sp_) { return sp_[1] && !nn(r[sp_[1]]); }); });
    if (!rows.length) return '<p class="xnote">' + T('Not available yet.') + '</p>';
    return table(rows.map(function (r) { return mon(dd(r.end)); }), rows.map(function () { return ''; }),
      spec.map(function (s) { return [s[0], s[3] === 'sec' ? [] : rows.map(function (r) { return s[2](r[s[1]]); }), s[3]]; }), first || 'Quarter ending');
  }
  function prepend(rows, vals) {
    return rows.map(function (r) { return [r[0], r[2] === 'sec' ? [] : [vals.hasOwnProperty(r[0]) ? vals[r[0]] : D].concat(r[1]), r[2]]; });
  }
  function note(s) { return s ? '<p class="xnote">' + s + '</p>' : ''; }
  function sec(p, html, hidden) { return '<section data-pv="' + p + '"' + (hidden ? ' hidden' : '') + '>' + html + '</section>'; }
  var P1 = function (x) { return pct(x, 1); };

  // ---------------------------------------------------------------- context
  var PS_KEYS = { DilutedEPS: 1, BasicEPS: 1 }, SH_KEYS = { DilutedAverageShares: 1, BasicAverageShares: 1, OrdinarySharesNumber: 1, ShareIssued: 1 };
  function median(a) { a = a.filter(function (x) { return x > 0 && isFinite(x); }).sort(function (x, y) { return x - y; }); return a.length ? a[Math.floor(a.length / 2)] : null; }
  /* Companies that report in another currency (TSMC, Toyota, Alibaba, Novo…): the SEC history is already in USD per listed share,
     but the quarterly statements and analyst estimates arrive in the home currency (and sometimes per ordinary share).
     Scale them onto the same basis; when no reliable scale exists, leave those parts out instead of showing wrong numbers. */
  function normalize(d, k, A) {
    var an = d.analyst || {}, out = { k: k || {}, an: an };
    var foreign = !!d.foreign || (d.reported_currency && d.reported_currency !== 'USD') || (an.cur && an.cur !== 'USD');
    if (!foreign) return out;
    var ai = (k && k.a_inc) || [], mm = [], pp = [], ss = [];
    A.forEach(function (a) {
      var y = match(ai, a.fy_end);
      if (y.TotalRevenue > 0 && a.revenue > 0) mm.push(a.revenue / y.TotalRevenue);
      if (y.DilutedEPS > 0 && a.eps_diluted > 0) pp.push(a.eps_diluted / y.DilutedEPS);
      if (y.DilutedAverageShares > 0 && a.shares_diluted > 0) ss.push(a.shares_diluted / y.DilutedAverageShares);
    });
    var cal = median(mm), fx = an.fx > 0 ? 1 / an.fx : null, m = null;
    if (fx && cal) m = (cal / fx > 0.7 && cal / fx < 1.4) ? fx : cal;
    else m = cal || ((an.cur && an.cur !== 'USD') ? fx : null);
    if (m && m > 0.9 && m < 1.1 && !fx) m = 1;
    var ps = median(pp), sh = median(ss);
    if (sh && sh > 0.98 && sh < 1.02) sh = 1;
    if (!sh) sh = 1;
    if (!ps && m) ps = m / sh;
    function conv(rows) {
      return (rows || []).map(function (r) {
        var o = {};
        Object.keys(r).forEach(function (key) {
          var v = r[key];
          if (key === 'end' || key === 'TaxRateForCalcs' || typeof v !== 'number') o[key] = v;
          else if (PS_KEYS[key]) o[key] = ps ? v * ps : null;
          else if (SH_KEYS[key]) o[key] = v * sh;
          else o[key] = v * m;
        });
        // per-share figures on the same basis as the SEC history: converted profit / listed-share count
        if (!nn(o.NetIncome) && o.DilutedAverageShares > 0) o.DilutedEPS = o.NetIncome / o.DilutedAverageShares;
        if (!nn(o.NetIncome) && o.BasicAverageShares > 0) o.BasicEPS = o.NetIncome / o.BasicAverageShares;
        return o;
      });
    }
    var kk = {};
    Object.keys(k || {}).forEach(function (key) { kk[key] = k[key]; });
    ['q_inc', 'q_bal', 'q_cf', 'a_inc', 'a_bal', 'a_cf'].forEach(function (key) { kk[key] = m ? conv(k && k[key]) : []; });
    // guard: if the converted last-four-quarters revenue is nowhere near the last fiscal year, the scale is not trustworthy
    if (m && m !== 1) {
      var qq = kk.q_inc.filter(function (r) { return !nn(r.TotalRevenue); }).sort(function (x, y) { return x.end < y.end ? -1 : 1; }).slice(-4);
      var lastA = A[A.length - 1] || {};
      if (qq.length === 4 && lastA.revenue > 0) {
        var tr = qq.reduce(function (t0, r) { return t0 + r.TotalRevenue; }, 0) / lastA.revenue;
        if (tr < 0.45 || tr > 2.3) ['q_inc', 'q_bal', 'q_cf'].forEach(function (key) { kk[key] = []; });
      }
    }
    // analyst estimates: the currency label is not reliable for foreign filers, so pick the scale that lands next to the
    // last reported year (revenue: x0.5-2.2, EPS: x0.3-3.5); when none does, leave the estimate out
    var last = A[A.length - 1] || {};
    function pick(val, ref, cands, lo, hi) {
      if (nn(val) || !(ref > 0)) return null;
      var best = null, bd = 9;
      cands.forEach(function (c) { if (!(c > 0)) return; var q = val * c / ref; if (q >= lo && q <= hi) { var dd_ = Math.abs(Math.log(q / 1.1)); if (dd_ < bd) { bd = dd_; best = c; } } });
      return best;
    }
    var rm = pick(an.r0, last.revenue, [1, fx, cal], 0.5, 2.2), em = pick(an.e0, last.eps_diluted, [1, an.ads, fx, ps], 0.3, 3.5);
    var a2 = {};
    Object.keys(an).forEach(function (key) { a2[key] = an[key]; });
    ['r0', 'r1', 'qr0', 'qr1'].forEach(function (key) { if (!nn(an[key])) a2[key] = rm ? an[key] * rm : null; });
    ['e0', 'e1', 'qe0', 'qe1'].forEach(function (key) { if (!nn(an[key])) a2[key] = em ? an[key] * em : null; });
    kk.trend = ((k && k.trend) || []).map(function (x) {
      var o = {}; Object.keys(x).forEach(function (key) { o[key] = x[key]; });
      ['rev', 'eps'].forEach(function (g) {
        if (!x[g]) return; var f = g === 'rev' ? rm : em, y = {};
        Object.keys(x[g]).forEach(function (key) { var v = x[g][key]; y[key] = (key === 'low' || key === 'avg' || key === 'high' || key === 'yearAgo') ? (f && !nn(v) ? v * f : null) : v; });
        o[g] = y;
      });
      return o;
    });
    out.k = kk; out.an = a2; out.fx = (m && m !== 1);
    return out;
  }
  function ctx(d, k, W) {
    var A = (d.annual || []).slice(-10), n = normalize(d, k, A);
    return { t: d.ticker, m: d.market || {}, A: A, R: A.slice().reverse(), tt: d.ttm || {}, an: n.an, fx: !!n.fx, r: d.ratios || {},
      q: (d.quarterly || []).filter(function (x) { return x && x.length >= 3; }), k: n.k, W: W || [], d: d, nm: shortName(d) };
  }
  function shortName(d) {
    var n = String(d.name || d.ticker).replace(/\s*\/[a-z]+\/?$/i, '').replace(/[\/,]+$/, '').trim();
    var s = n.replace(/,?\s+(Inc\.?|Corporation|Corp\.?|Company|Co\.?|Ltd\.?|Limited|plc|PLC|N\.V\.|S\.A\.|AG|SE|Holdings?|Group|Incorporated|L\.P\.|LP)$/i, '').trim();
    s = s.replace(/,?\s+(Inc\.?|Corp\.?|Holdings?)$/i, '').replace(/\s*&$/, '').trim();
    return s || n;
  }
  function ycols(c) {
    return [c.R.map(function (a) { return 'FY' + a.fy; }), c.R.map(function (a) { return mon(dd(a.fy_end)); })];
  }

  // ---------------------------------------------------------------- income statement
  function income(c) {
    var A = c.A, R = c.R, q = c.q, tt = c.tt, k = c.k;
    var KA = k.a_inc || [], KQ = k.q_inc || [];
    var YT = ttmInc(k), Tt = YT[YT.length - 1] || {};
    var lastA = A[A.length - 1] || {};
    var has = !!Tt.TotalRevenue && newer(Tt.end, lastA.fy_end);
    // some companies define revenue differently in the two sources (banks and brokers net of interest, excise taxes, pass-through costs):
    // a TTM column next to the SEC years would not be comparable, so it stays in the TTM view only
    var yl = match(KA, lastA.fy_end);
    if (has && yl.TotalRevenue > 0 && lastA.revenue > 0 && Math.abs(yl.TotalRevenue / lastA.revenue - 1) > (c.fx ? 0.2 : 0.06)) has = false;
    var lag = !!Tt.end && tt.end && days(dd(tt.end), dd(Tt.end)) > 20;
    var yc = ycols(c), cols = (has ? ['TTM'] : []).concat(yc[0]), sub = (has ? [mon(dd(Tt.end))] : []).concat(yc[1]);
    function ser(fn, tv) { return (has ? [tv === undefined ? D : tv] : []).concat(R.map(function (a, i) { return fn(a, R[i + 1]); })); }
    function g(key) { return function (a, p) { return (p && !nn(a[key]) && p[key] > 0) ? sp(a[key] / p[key] - 1) : D; }; }
    function v(key, f) { f = f || usd; return function (a) { return f(a[key]); }; }
    var P = {};
    if (Tt.end) {
      for (var j = YT.length - 1; j >= 0; j--) { var dy = days(dd(Tt.end), dd(YT[j].end)); if (dy > 330 && dy < 400) { P = YT[j]; break; } }
      if (!P.TotalRevenue) {
        P = {};
        for (var i = 3; i < q.length; i++) {
          var w = q.slice(i - 3, i + 1);
          if (Math.abs(days(dd(Tt.end), dd(w[3][0])) - 365) < 25 && days(dd(w[3][0]), dd(w[0][0])) < 300 && w.every(function (x) { return x[1]; })) {
            P.TotalRevenue = w.reduce(function (s, x) { return s + x[1]; }, 0);
            P.NetIncome = w.every(function (x) { return !nn(x[2]); }) ? w.reduce(function (s, x) { return s + x[2]; }, 0) : null;
            P._sh = match(KQ, w[3][0]).DilutedAverageShares;
            if (!nn(P.NetIncome) && P._sh && Tt._sh && Tt.NetIncome && Tt.DilutedEPS) P.DilutedEPS = P.NetIncome / P._sh * (Tt.DilutedEPS / (Tt.NetIncome / Tt._sh));
          }
        }
      }
    }
    function tg(key) { return (!nn(Tt[key]) && P[key] > 0) ? sp(Tt[key] / P[key] - 1) : D; }
    function tv(key, f) { return (f || usd)(Tt[key]); }
    function ka(key, f, alt) { return function (a) { var x = match(KA, a.fy_end)[key]; if (nn(x) && alt) x = typeof alt === 'function' ? alt(a) : a[alt]; return (f || usd)(x); }; }
    var rows = [
      ['Revenue', ser(v('revenue'), tv('TotalRevenue')), ''],
      ['Revenue growth', ser(g('revenue'), tg('TotalRevenue')), 'g'],
      ['Cost of revenue', ser(function (a) { return (!nn(a.revenue) && !nn(a.gross_profit)) ? usd(a.revenue - a.gross_profit) : D; }, tv('CostOfRevenue')), ''],
      ['Gross profit', ser(v('gross_profit'), tv('GrossProfit')), 'b'],
      ['Research & development', ser(v('rnd'), tv('ResearchAndDevelopment')), ''],
      ['SG&A and other operating expenses', ser(function (a) { return (!nn(a.gross_profit) && !nn(a.op_income)) ? usd(a.gross_profit - a.op_income - (a.rnd || 0)) : D; }, tv('_oth')), ''],
      ['Operating income', ser(v('op_income'), tv('OperatingIncome')), 'b'],
      ['Interest expense', ser(v('interest_exp'), tv('InterestExpense')), ''],
      ['Interest & investment income', ser(ka('InterestIncome'), tv('InterestIncome')), ''],
      ['Pretax income', ser(ka('PretaxIncome', usd, 'pretax'), tv('PretaxIncome')), ''],
      ['Income tax', ser(ka('TaxProvision', usd, 'tax'), tv('TaxProvision')), ''],
      ['Net income', ser(v('net_income'), tv('NetIncome')), 'b'],
      ['Net income growth', ser(g('net_income'), tg('NetIncome')), 'g'],
      ['Shares outstanding (diluted)', ser(function (a) { return a.shares_diluted ? (a.shares_diluted / 1e9).toFixed(2) + 'B' : D; }, tv('_sh', shr)), ''],
      ['Shares change', ser(g('shares_diluted'), tg('_sh')), 'g'],
      ['EPS (basic)', ser(ka('BasicEPS', eps), tv('BasicEPS', eps)), ''],
      ['EPS (diluted)', ser(v('eps_diluted', eps), tv('DilutedEPS', eps)), 'b'],
      ['EPS growth', ser(g('eps_diluted'), tg('DilutedEPS')), 'g'],
      ['Margins', [], 'sec'],
      ['Gross margin', ser(v('gross_margin', P1), tv('_gm', P1)), ''],
      ['Operating margin', ser(v('op_margin', P1), tv('_om', P1)), ''],
      ['Net margin', ser(v('net_margin', P1), tv('_nm', P1)), ''],
      ['EBITDA', ser(v('ebitda'), tv('EBITDA')), ''],
      ['EBITDA margin', ser(v('ebitda_margin', P1), tv('_em', P1)), ''],
      ['Effective tax rate', ser(function (a) { var yk = match(KA, a.fy_end), pt = !nn(yk.PretaxIncome) ? yk.PretaxIncome : a.pretax, tx = !nn(yk.TaxProvision) ? yk.TaxProvision : a.tax; return (pt > 0 && !nn(tx) && Math.abs(tx / pt) < 1) ? P1(tx / pt) : D; }, tv('_tr', P1)), ''],
      ['Stock-based compensation', ser(v('sbc'), tv('StockBasedCompensation')), '']
    ];
    // quarterly: revenue / net income from SEC, other lines from the quarterly statements
    var Q = q.slice(-20).reverse(), M = Q.map(function (x) { return match(KQ, x[0]); });
    function qy(i, j) { if (i + 4 >= Q.length) return D; var a = Q[i], b = Q[i + 4]; return (!b[j] || b[j] <= 0 || nn(a[j])) ? D : sp(a[j] / b[j] - 1); }
    function mq(key, f) { return M.map(function (x) { return (f || usd)(x[key]); }); }
    function mg(key) { return M.map(function (x, i) { return (!nn(x[key]) && Q[i][1]) ? pct(x[key] / Q[i][1], 1) : D; }); }
    var qrows = [
      ['Revenue', Q.map(function (x) { return usd(x[1]); }), 'b'], ['Revenue growth (vs. year earlier)', Q.map(function (x, i) { return qy(i, 1); }), 'g'],
      ['Cost of revenue', mq('CostOfRevenue'), ''], ['Gross profit', mq('GrossProfit'), 'b'], ['Research & development', mq('ResearchAndDevelopment'), ''],
      ['Selling, general & admin', mq('SellingGeneralAndAdministration'), ''], ['Operating income', mq('OperatingIncome'), 'b'],
      ['Pretax income', mq('PretaxIncome'), ''], ['Income tax', mq('TaxProvision'), ''],
      ['Net income', Q.map(function (x) { return usd(x[2]); }), 'b'], ['Net income growth (vs. year earlier)', Q.map(function (x, i) { return qy(i, 2); }), 'g'],
      ['EPS (diluted)', mq('DilutedEPS', eps), 'b'], ['Shares (diluted)', mq('DilutedAverageShares', shr), ''],
      ['Margins', [], 'sec'], ['Gross margin', mg('GrossProfit'), ''], ['Operating margin', mg('OperatingIncome'), ''],
      ['Net margin', Q.map(function (x) { return x[1] ? pct(x[2] / x[1], 1) : D; }), '']
    ];
    var lq = q[q.length - 1];
    var lagnote = (lag && lq) ? F('TTM = the four quarters to %s, the latest quarter with a full statement. The %s quarter (revenue %s, net income %s) is in the Quarterly view and joins TTM once its full statement is published.',
      fdate(Tt.end), mon(dd(lq[0])), usd(lq[1]), usd(lq[2])) : '';
    return sec('a', table(cols, sub, rows) + note(lagnote)) +
      sec('q', table(Q.map(function (x) { return mon(dd(x[0])); }), Q.map(function () { return ''; }), qrows, 'Quarter ending') +
        note(F('Last %s quarters. Revenue and net income from SEC filings; other lines from Yahoo Finance for the quarters it covers (— = not yet available).', Q.length)), 1) +
      sec('t', qtable(YT.slice().reverse().slice(0, 12), INCROWS, 'Twelve months ending') +
        note(T('Each column adds up the four quarters ending on that date (EPS = sum of quarterly EPS; shares = latest quarter).') + ' ' + lagnote), 1);
  }
  var INCROWS = [['Revenue', 'TotalRevenue', usd, 'b'], ['Cost of revenue', 'CostOfRevenue', usd, ''], ['Gross profit', 'GrossProfit', usd, 'b'],
    ['Research & development', 'ResearchAndDevelopment', usd, ''], ['SG&A and other operating expenses', '_oth', usd, ''],
    ['Operating income', 'OperatingIncome', usd, 'b'], ['Interest expense', 'InterestExpense', usd, ''], ['Interest & investment income', 'InterestIncome', usd, ''],
    ['Pretax income', 'PretaxIncome', usd, ''], ['Income tax', 'TaxProvision', usd, ''], ['Net income', 'NetIncome', usd, 'b'],
    ['Shares outstanding (diluted)', '_sh', shr, ''], ['EPS (basic)', 'BasicEPS', eps, ''], ['EPS (diluted)', 'DilutedEPS', eps, 'b'],
    ['Margins', null, null, 'sec'], ['Gross margin', '_gm', P1, ''], ['Operating margin', '_om', P1, ''], ['Net margin', '_nm', P1, ''],
    ['EBITDA', 'EBITDA', usd, ''], ['EBITDA margin', '_em', P1, ''], ['Effective tax rate', '_tr', P1, ''], ['Stock-based compensation', 'StockBasedCompensation', usd, '']];

  // ---------------------------------------------------------------- balance sheet
  var BALQ = [['Cash & equivalents', 'CashAndCashEquivalents', usd, ''], ['Short-term investments', 'OtherShortTermInvestments', usd, ''],
    ['Accounts receivable', 'AccountsReceivable', usd, ''], ['Inventory', 'Inventory', usd, ''], ['Total current assets', 'CurrentAssets', usd, 'b'],
    ['Property, plant & equipment', 'NetPPE', usd, ''], ['Goodwill', 'Goodwill', usd, ''], ['Total assets', 'TotalAssets', usd, 'b'],
    ['Accounts payable', 'AccountsPayable', usd, ''], ['Total current liabilities', 'CurrentLiabilities', usd, ''], ['Total debt', 'TotalDebt', usd, ''],
    ['Total liabilities', 'TotalLiabilitiesNetMinorityInterest', usd, 'b'], ['Retained earnings', 'RetainedEarnings', usd, ''],
    ["Shareholders’ equity", 'StockholdersEquity', usd, 'b'], ['Working capital', 'WorkingCapital', usd, ''], ['Shares outstanding', 'OrdinarySharesNumber', shr, '']];
  function balance(c) {
    var A = c.A, R = c.R, k = c.k, KA = k.a_bal || [], KQ = byEnd(k.q_bal);
    function S(fn) { return R.map(fn); }
    function v(key) { return S(function (a) { return usd(a[key]); }); }
    function y(key, alt) { return S(function (a) { var x = match(KA, a.fy_end)[key]; if (nn(x) && alt) x = a[alt]; return usd(x); }); }
    // the SEC "cash" figure includes short-term investments when the company reports them
    function cashOnly(a) { var x = match(KA, a.fy_end).CashAndCashEquivalents; return !nn(x) ? x : (nn(a.cash) ? null : a.cash - (a.st_inv || 0)); }
    // the SEC tags miss part of the borrowings for some filers (IFRS bond lines, bank funding): when the second source shows
    // more than twice as much, use it
    function debtOf(a) { var x = match(KA, a.fy_end).TotalDebt; return (!nn(x) && (nn(a.debt) || a.debt < 0.5 * x)) ? x : a.debt; }
    function cashAll(a) { var yb = match(KA, a.fy_end), x = yb.CashCashEquivalentsAndShortTermInvestments; return !nn(x) ? Math.max(x, a.cash || 0) : a.cash; }
    var rows = [
      ['Assets', [], 'sec'], ['Cash & equivalents', S(function (a) { return usd(cashOnly(a)); }), ''], ['Short-term investments', y('OtherShortTermInvestments', 'st_inv'), ''],
      ['Accounts receivable', y('AccountsReceivable', 'recv'), ''], ['Inventory', y('Inventory', 'inventory'), ''], ['Total current assets', v('current_assets'), ''],
      ['Property, plant & equipment', S(function (a) { return usd(!nn(a.ppe) ? a.ppe : match(KA, a.fy_end).NetPPE); }), ''], ['Goodwill', v('goodwill'), ''], ['Other intangible assets', v('intangibles'), ''],
      ['Total assets', v('assets'), 'b'], ['Liabilities', [], 'sec'], ['Accounts payable', y('AccountsPayable', 'payables'), ''],
      ['Total current liabilities', v('current_liabilities'), ''], ['Total debt', S(function (a) { return usd(debtOf(a)); }), ''], ['Total liabilities', v('liabilities'), 'b'],
      ['Equity', [], 'sec'], ['Retained earnings', y('RetainedEarnings', 'retained'), ''], ["Shareholders’ equity", v('equity'), 'b'],
      ['Total liabilities & equity', v('assets'), ''],
      ['Key figures', [], 'sec'],
      ['Net cash (debt)', S(function (a) { var c0 = cashAll(a); var db = debtOf(a); return (nn(db) || nn(c0)) ? (nn(a.net_debt) ? D : usd(-a.net_debt)) : usd(c0 - db); }), ''],
      ['Working capital', S(function (a) { return (!nn(a.current_assets) && !nn(a.current_liabilities)) ? usd(a.current_assets - a.current_liabilities) : D; }), ''],
      ['Book value per share', S(function (a) { return eps(a.book_value_per_share); }), ''], ['Tangible book value', y('TangibleBookValue'), ''],
      ['Shares outstanding', S(function (a) { return a.shares_out ? (a.shares_out / 1e9).toFixed(2) + 'B' : D; }), ''],
      ['Current ratio', S(function (a) { return x2(a.current_ratio, 2); }), ''], ['Debt / equity', S(function (a) { return x2(a.debt_to_equity, 2); }), '']
    ];
    var yc = ycols(c), cols = yc[0], sub = yc[1];
    var L = latest(k)[2], lastA = A[A.length - 1] || {};
    if (L.end && newer(L.end, lastA.fy_end)) {
      var eq = L.StockholdersEquity, debt = L.TotalDebt, cs = L.CashAndCashEquivalents, sh = L.OrdinarySharesNumber, tl = L.TotalLiabilitiesNetMinorityInterest;
      var csAll = !nn(L.CashCashEquivalentsAndShortTermInvestments) ? L.CashCashEquivalentsAndShortTermInvestments : cs;
      rows = prepend(rows, {
        'Cash & equivalents': usd(cs), 'Short-term investments': usd(L.OtherShortTermInvestments), 'Accounts receivable': usd(L.AccountsReceivable),
        'Inventory': usd(L.Inventory), 'Total current assets': usd(L.CurrentAssets), 'Property, plant & equipment': usd((c.d.bs && !nn(c.d.bs.ppe) && Math.abs(days(dd(c.d.bs.end), dd(L.end))) < 16 && R.some(function (a) { return !nn(a.ppe); })) ? c.d.bs.ppe : L.NetPPE), 'Goodwill': usd(L.Goodwill),
        'Other intangible assets': usd(L.OtherIntangibleAssets), 'Total assets': usd(L.TotalAssets), 'Accounts payable': usd(L.AccountsPayable),
        'Total current liabilities': usd(L.CurrentLiabilities), 'Total debt': usd(debt), 'Total liabilities': usd(tl), 'Retained earnings': usd(L.RetainedEarnings),
        "Shareholders’ equity": usd(eq), 'Total liabilities & equity': usd(L.TotalAssets),
        'Net cash (debt)': (!nn(csAll) && !nn(debt)) ? usd(csAll - debt) : D, 'Working capital': usd(L.WorkingCapital),
        'Book value per share': (eq && sh) ? eps(eq / sh) : D, 'Tangible book value': usd(L.TangibleBookValue), 'Shares outstanding': shr(sh),
        'Current ratio': (L.CurrentAssets && L.CurrentLiabilities) ? x2(L.CurrentAssets / L.CurrentLiabilities, 2) : D,
        'Debt / equity': (!nn(debt) && eq) ? x2(debt / eq, 2) : D
      });
      cols = [T('Latest quarter')].concat(cols); sub = [mon(dd(L.end))].concat(sub);
    }
    var qt = qtable(KQ.slice().reverse(), BALQ);
    return sec('a', table(cols, sub, rows)) + sec('q', qt + note(T('Quarter-end balance sheets from Yahoo Finance.')), 1) +
      sec('t', qt + note(T('A balance sheet is a snapshot at one date, so the TTM view shows the latest quarter-end balance sheets.')), 1);
  }

  // ---------------------------------------------------------------- cash flow
  var CFROWS = [['Net income', 'NetIncomeFromContinuingOperations', usd, ''], ['Depreciation & amortization', 'DepreciationAndAmortization', usd, ''],
    ['Stock-based compensation', 'StockBasedCompensation', usd, ''], ['Change in working capital', 'ChangeInWorkingCapital', usd, ''],
    ['Operating cash flow', 'OperatingCashFlow', usd, 'b'], ['Capital expenditures', 'CapitalExpenditure', usd, ''],
    ['Acquisitions', 'PurchaseOfBusiness', usd, ''], ['Investing cash flow', 'InvestingCashFlow', usd, 'b'],
    ['Dividends paid', 'CashDividendsPaid', usd, ''], ['Share buybacks', 'RepurchaseOfCapitalStock', usd, ''],
    ['Financing cash flow', 'FinancingCashFlow', usd, 'b'], ['Free cash flow', 'FreeCashFlow', usd, 'b']];
  function cash(c) {
    var A = c.A, R = c.R, k = c.k, KA = k.a_cf || [], KQ = byEnd(k.q_cf);
    function S(fn) { return R.map(fn); }
    function v(key) { return S(function (a) { return usd(a[key]); }); }
    function y(key) { return S(function (a) { return usd(match(KA, a.fy_end)[key]); }); }
    function yf(key, alt, neg) { return S(function (a) { var x = match(KA, a.fy_end)[key]; if (!nn(x)) return usd(x); var z = a[alt]; return nn(z) ? D : usd(neg ? -Math.abs(z) : z); }); }
    function ng(key) { return S(function (a) { return a[key] ? usd(-Math.abs(a[key])) : D; }); }
    var rows = [
      ['Operating activities', [], 'sec'], ['Net income', v('net_income'), ''], ['Depreciation & amortization', v('da'), ''],
      ['Stock-based compensation', v('sbc'), ''], ['Change in working capital', y('ChangeInWorkingCapital'), ''], ['Operating cash flow', v('cfo'), 'b'],
      ['Operating cash flow growth', S(function (a, i) { var p = R[i + 1]; return (p && !nn(a.cfo) && p.cfo > 0) ? sp(a.cfo / p.cfo - 1) : D; }), 'g'],
      ['Investing & financing', [], 'sec'], ['Capital expenditures', ng('capex'), ''], ['Acquisitions', yf('PurchaseOfBusiness', 'acq', 1), ''],
      ['Investing cash flow', yf('InvestingCashFlow', 'icf'), 'b'], ['Dividends paid', ng('dividends'), ''], ['Share buybacks', ng('buybacks'), ''],
      ['Debt issued', y('IssuanceOfDebt'), ''], ['Debt repaid', yf('RepaymentOfDebt', 'debt_repaid', 1), ''], ['Financing cash flow', yf('FinancingCashFlow', 'fincf'), 'b'],
      ['Free cash flow', [], 'sec'], ['Free cash flow', v('fcf'), 'b'], ['Free cash flow growth', S(function (a) { return sp(a.fcf_growth); }), 'g'],
      ['Free cash flow margin', S(function (a) { return pct(a.fcf_margin, 1); }), ''], ['Free cash flow per share', S(function (a) { return eps(a.fcf_per_share); }), ''],
      ['FCF / net income', S(function (a) { return x2(a.fcf_conv, 2); }), '']
    ];
    var yc = ycols(c), cols = yc[0], sub = yc[1], LT = latest(k), TI = LT[0], TC = LT[1], lastA = A[A.length - 1] || {};
    if (TC.end && newer(TC.end, lastA.fy_end)) {
      var same = TI.end === TC.end, fcf = TC.FreeCashFlow, rv = same ? TI.TotalRevenue : null, ni = TC.NetIncomeFromContinuingOperations, sh = same ? TI._sh : null;
      rows = prepend(rows, {
        'Net income': usd(ni), 'Depreciation & amortization': usd(TC.DepreciationAndAmortization), 'Stock-based compensation': usd(TC.StockBasedCompensation),
        'Change in working capital': usd(TC.ChangeInWorkingCapital), 'Operating cash flow': usd(TC.OperatingCashFlow), 'Capital expenditures': usd(TC.CapitalExpenditure),
        'Acquisitions': usd(TC.PurchaseOfBusiness), 'Investing cash flow': usd(TC.InvestingCashFlow), 'Dividends paid': usd(TC.CashDividendsPaid),
        'Share buybacks': usd(TC.RepurchaseOfCapitalStock), 'Debt issued': usd(TC.IssuanceOfDebt), 'Debt repaid': usd(TC.RepaymentOfDebt),
        'Financing cash flow': usd(TC.FinancingCashFlow), 'Free cash flow': usd(fcf), 'Free cash flow margin': (!nn(fcf) && rv) ? pct(fcf / rv, 1) : D,
        'Free cash flow per share': (!nn(fcf) && sh) ? eps(fcf / sh) : D, 'FCF / net income': (!nn(fcf) && ni > 0) ? x2(fcf / ni, 2) : D
      });
      cols = ['TTM'].concat(cols); sub = [mon(dd(TC.end))].concat(sub);
    }
    return sec('a', table(cols, sub, rows)) + sec('q', qtable(KQ.slice().reverse(), CFROWS) + note(T('Quarterly cash flow from Yahoo Finance.')), 1) +
      sec('t', qtable(sum4(qcf(k)).reverse(), CFROWS, 'Twelve months ending') + note(T('Each column adds up the four quarters ending on that date.')), 1);
  }

  // ---------------------------------------------------------------- ratios
  function qratios(k, ttm) {
    var B = {}, C = {}, I;
    (k.q_bal || []).forEach(function (r) { B[r.end] = r; });
    if (ttm) { I = ttmInc(k); sum4(qcf(k)).forEach(function (r) { C[r.end] = r; }); }
    else {
      I = byEnd(k.q_inc).map(function (r0) {
        var r = {}; Object.keys(r0).forEach(function (x) { r[x] = r0[x]; });
        if (r.TotalRevenue) [['_gm', 'GrossProfit'], ['_om', 'OperatingIncome'], ['_nm', 'NetIncome']].forEach(function (p) { if (!nn(r[p[1]])) r[p[0]] = r[p[1]] / r.TotalRevenue; });
        return r;
      });
      (k.q_cf || []).forEach(function (r) { C[r.end] = r; });
    }
    return I.map(function (r) {
      var b = B[r.end] || {}, c = C[r.end] || {}, o = { end: r.end, _gm: r._gm, _om: r._om, _nm: r._nm };
      var rv = r.TotalRevenue, ni = r.NetIncome, op = r.OperatingIncome, eq = b.StockholdersEquity, debt = b.TotalDebt, cs = !nn(b.CashCashEquivalentsAndShortTermInvestments) ? b.CashCashEquivalentsAndShortTermInvestments : b.CashAndCashEquivalents;
      if (!nn(c.FreeCashFlow) && rv) o._fm = c.FreeCashFlow / rv;
      if (b.CurrentAssets && b.CurrentLiabilities) o._cr = b.CurrentAssets / b.CurrentLiabilities;
      if (!nn(debt) && eq > 0) o._de = debt / eq;
      if (ttm) {
        var tr = (!nn(r._tr) && r._tr >= 0 && r._tr < 0.6) ? r._tr : 0.21;
        if (!nn(ni) && eq > 0) o._roe = ni / eq;
        if (!nn(ni) && b.TotalAssets) o._roa = ni / b.TotalAssets;
        if (!nn(op) && eq && eq + (debt || 0) > 0) o._roic = op * (1 - tr) / (eq + (debt || 0));
        if (!nn(debt) && !nn(cs) && r.EBITDA > 0) o._nde = (debt - cs) / r.EBITDA;
        if (!nn(op) && r.InterestExpense > 0) o._ic = op / r.InterestExpense;
      }
      return o;
    });
  }
  var X2 = function (x) { return x2(x, 2); }, X1 = function (x) { return x2(x, 1); };
  var RROWS_Q = [['Margins', null, null, 'sec'], ['Gross margin', '_gm', P1, ''], ['Operating margin', '_om', P1, ''], ['Net margin', '_nm', P1, ''],
    ['FCF margin', '_fm', P1, ''], ['Financial health', null, null, 'sec'], ['Current ratio', '_cr', X2, ''], ['Debt / equity', '_de', X2, '']];
  var RROWS = [['Returns', null, null, 'sec'], ['Return on equity (ROE)', '_roe', P1, ''], ['Return on assets (ROA)', '_roa', P1, ''],
    ['Return on invested capital (ROIC)', '_roic', P1, '']].concat(RROWS_Q, [['Net debt / EBITDA', '_nde', X2, ''], ['Interest coverage', '_ic', X1, '']]);
  function ratios(c) {
    var R = c.R, m = c.m, r = c.r, k = c.k;
    var HV = R.map(function (a) { return histVal(c.W, a); });
    function S(fn) { return R.map(fn); }
    function h(cur, key, f) { return [cur].concat(HV.map(function (x) { return nn(x[key]) ? D : f(x[key]); })); }
    function p(key) { return [D].concat(S(function (a) { return pct(a[key], 1); })); }
    function xx(key, d) { return [D].concat(S(function (a) { return x2(a[key], d === undefined ? 2 : d); })); }
    function cur(val) { return [val].concat(R.map(function () { return D; })); }
    var P2 = function (x) { return pct(x, 2); };
    var rows = [
      ['Valuation', [], 'sec'],
      ['Share price (at year end)', h(dol(m.price), 'price', dol), ''], ['Market capitalization', h(usd(m.mcap), 'mcap', usd), 'b'],
      ['Enterprise value', h(usd(r.ev), 'ev', usd), ''], ['P/E ratio', h(x2(r.pe), 'pe', x2), ''], ['Forward P/E', cur(x2(r.fwd_pe)), ''],
      ['P/S ratio', h(x2(r.ps), 'ps', x2), ''], ['P/B ratio', h(x2(r.pb), 'pb', x2), ''], ['P/FCF ratio', h(x2(r.pfcf), 'pfcf', x2), ''],
      ['EV/EBITDA', h(x2(r.ev_ebitda), 'ev_ebitda', x2), ''], ['PEG ratio', cur(x2(r.peg, 2)), ''],
      ['Earnings yield', h(P2(r.earnings_yield), 'ey', P2), ''], ['FCF yield', h(P2(r.fcf_yield), 'fy', P2), ''], ['Dividend yield', h(P2(r.div_yield), 'dy', P2), ''],
      ['Returns', [], 'sec'], ['Return on equity (ROE)', p('roe'), ''], ['Return on assets (ROA)', p('roa'), ''], ['Return on invested capital (ROIC)', p('roic'), ''],
      ['Margins', [], 'sec'], ['Gross margin', p('gross_margin'), ''], ['Operating margin', p('op_margin'), ''], ['Net margin', p('net_margin'), ''], ['FCF margin', p('fcf_margin'), ''],
      ['Financial health', [], 'sec'], ['Current ratio', xx('current_ratio'), ''], ['Debt / equity', xx('debt_to_equity'), ''],
      ['Net debt / EBITDA', xx('nd_ebitda'), ''], ['Interest coverage', xx('interest_cov', 1), ''],
      ['Shareholders', [], 'sec'],
      ['Dividend payout ratio', [D].concat(S(function (a) { return (a.dividends && a.net_income > 0) ? pct(a.dividends / a.net_income, 1) : D; })), ''],
      ['Stock-based comp. / revenue', p('sbc_pct'), ''],
      ['Buyback yield', [P2(r.buyback_yield)].concat(S(function (a, i) { return (!nn(a.buybacks) && HV[i].mcap) ? P2(a.buybacks / HV[i].mcap) : D; })), ''],
      ['Shareholder yield', [P2(r.shareholder_yield)].concat(S(function (a, i) { return (!nn(a.buybacks) && HV[i].mcap) ? P2(((a.buybacks || 0) + (a.dividends || 0)) / HV[i].mcap) : D; })), '']
    ];
    var LT = latest(k), TI = LT[0], TC = LT[1], L = LT[2];
    if (TI.end) {
      var rv = TI.TotalRevenue, ni = TI.NetIncome, op = TI.OperatingIncome, eq = L.StockholdersEquity, debt = L.TotalDebt, cs = !nn(L.CashCashEquivalentsAndShortTermInvestments) ? L.CashCashEquivalentsAndShortTermInvestments : L.CashAndCashEquivalents;
      var fcf = TC.end === TI.end ? TC.FreeCashFlow : null, tr = (!nn(TI._tr) && TI._tr >= 0 && TI._tr < 0.6) ? TI._tr : 0.21;
      var ie = TI.InterestExpense, eb = TI.EBITDA, dv = TC.end === TI.end ? Math.abs(TC.CashDividendsPaid || 0) : null;
      var fill = {
        'Return on equity (ROE)': (!nn(ni) && eq > 0) ? P1(ni / eq) : D, 'Return on assets (ROA)': (!nn(ni) && L.TotalAssets) ? P1(ni / L.TotalAssets) : D,
        'Return on invested capital (ROIC)': (!nn(op) && eq && eq + (debt || 0) > 0) ? P1(op * (1 - tr) / (eq + (debt || 0))) : D,
        'Gross margin': P1(TI._gm), 'Operating margin': P1(TI._om), 'Net margin': P1(TI._nm), 'FCF margin': (!nn(fcf) && rv) ? P1(fcf / rv) : D,
        'Current ratio': (L.CurrentAssets && L.CurrentLiabilities) ? X2(L.CurrentAssets / L.CurrentLiabilities) : D,
        'Debt / equity': (!nn(debt) && eq > 0) ? X2(debt / eq) : D, 'Net debt / EBITDA': (!nn(debt) && !nn(cs) && eb > 0) ? X2((debt - cs) / eb) : D,
        'Interest coverage': (!nn(op) && ie > 0) ? X1(op / ie) : D, 'Dividend payout ratio': (!nn(dv) && ni > 0) ? P1(dv / ni) : D,
        'Stock-based comp. / revenue': (TI.StockBasedCompensation && rv) ? P1(TI.StockBasedCompensation / rv) : D
      };
      rows = rows.map(function (x) { return (fill.hasOwnProperty(x[0]) && x[1].length && x[1][0] === D) ? [x[0], [fill[x[0]]].concat(x[1].slice(1)), x[2]] : x; });
    }
    var yc = ycols(c), asof = dd(m.as_of);
    return sec('a', table([T('Current')].concat(yc[0]), [asof ? mon(asof) : ''].concat(yc[1]), rows) +
        note(T('“Current” uses the latest price and the last twelve months. Past years use the share price at each fiscal year-end and that year’s annual report.'))) +
      sec('q', qtable(qratios(k, false).reverse(), RROWS_Q) + note(T('Margins for each quarter; balance-sheet ratios at each quarter end.')), 1) +
      sec('t', qtable(qratios(k, true).reverse(), RROWS, 'Twelve months ending') + note(T('Returns and margins over the four quarters ending on each date; balance-sheet ratios at that date.')), 1);
  }

  // ---------------------------------------------------------------- key statistics summary
  var REC = { strong_buy: 'Strong buy', buy: 'Buy', hold: 'Hold', sell: 'Sell', strong_sell: 'Strong sell', underperform: 'Underperform', outperform: 'Outperform' };
  function recName(x) { if (!x || x === 'none') return D; return T(REC[x] || (x.charAt(0).toUpperCase() + x.slice(1))); }
  function grp(title, rows, lead) {
    return '<section class="ks-g"><h3>' + T(title) + '</h3>' + (lead ? '<p>' + lead + '</p>' : '') + rows.filter(function (x) { return x[1] !== null && x[1] !== D && x[1] !== '' && x[1] !== D + ' · ' + D; }).map(function (x) {
      return '<div class="ks-r"><span>' + T(x[0]) + '</span><b' + (x[2] ? ' class="' + x[2] + '"' : '') + '>' + B(x[1]) + (x[3] ? '<small>' + x[3] + '</small>' : '') + '</b></div>';
    }).join('') + '</section>';
  }
  function summary(c) {
    var m = c.m, r = c.r, d = c.d, s = d.summary || {}, sc = d.scores || {}, dcf = d.dcf || {}, an = c.an, A = c.A, L = A[A.length - 1] || {}, k = c.k, nm = esc(c.nm);
    function good(v) { return (v || 0) >= 0 ? 'up' : 'dn'; }
    var nc = dcf.nc, sh = c.tt.shares_diluted || L.shares_diluted;
    var fair = (r.fair_mcap && m.mcap) ? r.fair_mcap / m.mcap - 1 : null;
    var peNote = (r.pe && r.sector_pe) ? F('sector %s', r.sector_pe.toFixed(1)) + ' · ' + (r.pe < r.sector_pe ? '<em class="up">' + T('Better') + '</em>' : '<em class="dn">' + T('Weaker') + '</em>') : '';
    var rt = an.rt || [], st = k.stats || {}, pr = k.price || {}, dt_ = k.dates || {}, MED = st.tgt_median;
    var c1 = grp('Total valuation', [['Market cap', usd(m.mcap)], ['Enterprise value', usd(r.ev)], ['Shares outstanding', sh ? (sh / 1e9).toFixed(2) + 'B' : D],
        ['Stock price', dol(m.price), '', fdate(m.as_of)]], F('%s is worth about %s.', nm, usd(m.mcap))) +
      grp('Valuation ratios', [['P/E (TTM)', x2(r.pe), '', peNote], ['Forward P/E', x2(r.fwd_pe)], ['P/S · forward P/S', x2(r.ps) + ' · ' + x2(r.fwd_ps)],
        ['P/FCF · forward P/FCF', x2(r.pfcf) + ' · ' + x2(r.fwd_pfcf)], ['P/B', x2(r.pb)], ['EV/EBITDA', x2(r.ev_ebitda)], ['PEG', x2(r.peg, 2)],
        ['FCF yield · earnings yield', pct(r.fcf_yield, 1) + ' · ' + pct(r.earnings_yield, 1)], ['Fair value (DCF) vs price', sp(fair), good(fair)]]);
    var c2 = grp('Growth & profitability', [['Revenue growth (1 yr)', sp(s.rev_cagr_1y), good(s.rev_cagr_1y)], ['Revenue growth (3 · 5 yr / yr)', sp(s.rev_cagr_3y) + ' · ' + sp(s.rev_cagr_5y)],
        ['EPS growth (5 yr / yr)', sp(s.eps_cagr_5y)], ['Gross · operating margin', pct(L.gross_margin, 1) + ' · ' + pct(L.op_margin, 1)],
        ['Net · FCF margin', pct(L.net_margin, 1) + ' · ' + pct(L.fcf_margin, 1)], ['ROIC · ROE', pct(L.roic, 1) + ' · ' + pct(L.roe, 1)],
        ['Net margin trend (3 yr)', nn(s.nm_trend) ? D : F('%s pts', (s.nm_trend >= 0 ? '+' : '') + (s.nm_trend * 100).toFixed(1)), good(s.nm_trend)],
        ['Profitable years', nn(s.profit_years) ? D : F('%s of %s', s.profit_years, Math.min(10, s.years || 10))]]) +
      grp('Balance sheet & health', [['Cash & investments', usd(dcf.cash)], ['Total debt', usd(dcf.debt)], ['Net cash (debt)', usd(nc), good(nc)],
        ['Debt / equity', x2(L.debt_to_equity, 2)], ['Current ratio', x2(L.current_ratio, 2)], ['Interest coverage', x2(L.interest_cov, 1)],
        ['Goodwill / assets', L.assets ? pct((L.goodwill || 0) / L.assets, 1) : D]], nc > 0 ? F('More cash than debt: net cash of %s.', usd(nc)) : '');
    var c3 = grp('Dividends & shareholder return', [['Dividend yield', pct(r.div_yield, 2)], ['Payout ratio', (L.dividends && L.net_income > 0) ? pct(L.dividends / L.net_income, 1) : D],
        ['Buyback yield', pct(r.buyback_yield, 2)], ['Shareholder yield', pct(r.shareholder_yield, 2)], ['Years paying dividends', s.div_years ? String(s.div_years) : D]]) +
      grp('Analysts', [['Consensus', recName(an.rec), (an.rec === 'buy' || an.rec === 'strong_buy') ? 'up' : '', an.n ? F('%s analysts', an.n) : ''],
        ['Price target', an.tgt ? dol(an.tgt) : D, '', (an.tgt && an.tlo && m.price) ? sp(an.tgt / m.price - 1) + ' · ' + F('range %s – %s', dol(an.tlo, 0), dol(an.thi, 0)) : ''],
        ['Median target', MED ? dol(MED) : D], ['Ratings: strong buy / buy / hold / sell', rt.length ? rt.slice(0, 4).join(' / ') : D],
        ['Revenue estimate (this FY · next)', usd(an.r0) + ' · ' + usd(an.r1)], ['EPS estimate (this FY · next)', eps(an.e0) + ' · ' + eps(an.e1)]]) +
      grp('Score', [['Overall', nn(sc.total) ? D : sc.total.toFixed(1) + ' / 5'], ['Value · future · past', [sc.value, sc.future, sc.past].map(function (x) { return nn(x) ? D : x; }).join(' · ')],
        ['Health · capital return', [sc.health, sc.capital].map(function (x) { return nn(x) ? D : x; }).join(' · ')]]);
    if (Object.keys(st).length) {
      c2 += grp('Ownership & short interest', [['Insider ownership', pct(st.insiders, 2)],
        ['Institutional ownership', pct(st.institutions, 1), '', st.inst_count ? F('%s institutions', st.inst_count.toLocaleString(LOC)) : ''],
        ['Float', shr(st.float)], ['Short interest', pct(st.short_float, 2), '', (st.short && st.short_ratio) ? F('%s shares · %s days to cover', shr(st.short), st.short_ratio.toFixed(1)) : '']],
        (!nn(st.insiders) && !nn(st.institutions)) ? F('Insiders own %s of %s; institutions own %s.', pct(st.insiders, 1), nm, pct(st.institutions, 0)) : '');
      var rsiN = (pr.rsi || 50) < 30 ? T('oversold') : (pr.rsi || 50) > 70 ? T('overbought') : '';
      c3 = grp('Stock price', [['52-week change', sp(st.chg52), good(st.chg52)], ['52-week range', (st.lo52 && st.hi52) ? dol(st.lo52) + ' – ' + dol(st.hi52) : D],
        ['50-day · 200-day average', (pr.ma50 && pr.ma200) ? dol(pr.ma50) + ' · ' + dol(pr.ma200) : D], ['RSI (14 days)', x2(pr.rsi, 1), '', rsiN],
        ['Beta (5 yr)', x2(st.beta, 2), '', (st.beta || 0) > 1.2 ? T('moves more than the market') : ''], ['Average volume (3 months)', shr(st.avgvol)]]) + c3;
      var today = new Date(), ne = (dt_.earnings || []).map(ep).filter(Boolean), nx = ne.filter(function (x) { return x >= today; });
      var xd = ep(dt_.exdiv), pd = ep(dt_.divpay), fe = dd(L.fy_end);
      c3 += grp('Key dates', [[nx.length ? 'Next earnings' : 'Last earnings', ne.length ? sdate((nx[0] || ne[0])) + (nx.length && dt_.earnings_est ? ' ' + T('(est.)') : '') : D],
        [xd && xd >= today ? 'Ex-dividend date' : 'Last ex-dividend date', sdate(xd)], [pd && pd >= today ? 'Dividend payment' : 'Last dividend paid', sdate(pd)],
        ['Fiscal year ends', fe ? fmtL.format(fe) : D]]);
    }
    return '<div class="ks-grid"><div>' + c1 + '</div><div>' + c2 + '</div><div>' + c3 + '</div></div>';
  }

  // ---------------------------------------------------------------- forecast
  var ACT = { up: 'Upgrades', down: 'Downgrades', main: 'Maintains', init: 'Initiates', reit: 'Reiterates' };
  function forecast(c) {
    var m = c.m, an = c.an, k = c.k, st = k.stats || {}, nm = esc(c.nm), A = c.A;
    var px = m.price, tgt = an.tgt, lo = an.tlo, hi = an.thi;
    if (!(px && tgt)) return '<p class="xnote">' + T('No analyst forecast is available for this stock.') + '</p>';
    var med = st.tgt_median, up = tgt / px - 1, rt = an.rt || [], rec = recName(an.rec), n = an.n || an.nt || 0;
    var TR = {}; (k.trend || []).forEach(function (x) { TR[x.p] = x; });
    var y0 = TR['0y'] || {}, y1 = TR['+1y'] || {};
    var lead = '<p class="lead"><strong>' + (rec !== D ? F('%s analysts rate %s a %s, with an average 12-month price target of %s, %s %s the current price of %s.', n, nm, rec, dol(tgt), pct(Math.abs(up), 1), T(up >= 0 ? 'above' : 'below'), dol(px))
      : F('The average 12-month analyst price target for %s is %s, %s %s the current price of %s.', nm, dol(tgt), pct(Math.abs(up), 1), T(up >= 0 ? 'above' : 'below'), dol(px))) + '</strong> ' +
      ((lo && hi) ? F('Targets range from %s (%s) to %s (%s).', dol(lo, 0), sp(lo / px - 1), dol(hi, 0), sp(hi / px - 1)) : '') +
      ((an.r0 && an.r1) ? ' ' + F('Analysts expect revenue of %s this fiscal year and %s next year.', usd(an.r0), usd(an.r1)) : '') + '</p>';
    var span = (lo && hi && hi > lo) ? hi - lo : null;
    function pos(v) { return Math.max(0, Math.min(100, (v - lo) / span * 100)); }
    var tbar = span ? '<div class="trange"><i style="left:' + pos(px).toFixed(1) + '%" class="cur" title="' + T('Current price') + '"></i><i style="left:' + pos(tgt).toFixed(1) + '%" class="avg" title="' + T('Average target') + '"></i></div>' +
      '<div class="tlab"><span>' + T('Low') + ' ' + B(dol(lo, 0)) + '</span><span>' + T('Average') + ' ' + B(dol(tgt, 0)) + '</span><span>' + T('High') + ' ' + B(dol(hi, 0)) + '</span></div>' : '';
    var ptab = table([T('Low'), T('Median'), T('Average'), T('High')], ['', '', '', ''], [
      ['Price target', [lo ? dol(lo) : D, med ? dol(med) : D, dol(tgt), hi ? dol(hi) : D], 'b'],
      ['vs. current price', [lo ? sp(lo / px - 1) : D, med ? sp(med / px - 1) : D, sp(up), hi ? sp(hi / px - 1) : D], '']], 'Target');
    var priceCard = '<section class="card"><h2>' + T('Price target') + '</h2>' + tbar + ptab + note(F('White marker: today’s price (%s) · gold marker: average target.', dol(px))) + '</section>';
    var RT = ['Strong buy', 'Buy', 'Hold', 'Sell', 'Strong sell'], COL = ['#2F7D5B', '#4FA37A', '#8A8F99', '#C46A55', '#9E3B33'], FL = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell'];
    var recs = k.recs || [], r0 = recs[0] || {};
    if (r0.period === '0m') rt = FL.map(function (f) { return r0[f] || 0; });
    var tot = rt.reduce(function (s, x) { return s + (x || 0); }, 0), mx = Math.max.apply(null, rt.concat([0]));
    var rbars = tot ? rt.slice(0, 5).map(function (x, i) { return '<div class="rt-r"><span>' + T(RT[i]) + '</span><i style="width:' + (mx ? x / mx * 100 : 0).toFixed(0) + '%;background:' + COL[i] + '"></i><b>' + x + '</b></div>'; }).join('') : '';
    var now = new Date(), lab = {};
    for (var i = 0; i < 4; i++) lab[i ? '-' + i + 'm' : '0m'] = mon(new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - i, 1)));
    var trend = recs.length ? table(recs.map(function (x) { return lab[x.period] || x.period; }), recs.map(function () { return ''; }),
      FL.map(function (f, i) { return [RT[i], recs.map(function (x) { return String(x[f] || 0); }), '']; }).concat([['Total', recs.map(function (x) { return String(FL.reduce(function (s, f) { return s + (x[f] || 0); }, 0)); }), 'b']]), 'Rating') : '';
    var rev30 = an.rev30 || {};
    var rateCard = '<section class="card"><h2>' + T('Analyst ratings') + (rec !== D ? ': ' + rec : '') + '</h2><div class="rt-bars">' + rbars + '</div>' +
      (tot ? note(F('%s ratings. In the last 30 days estimates were raised %s times and lowered %s times.', tot, rev30.upLast30days || 0, rev30.downLast30days || 0)) : '') +
      (trend ? '<h3>' + T('Recommendation trend') + '</h3>' + trend : '') + '</section>';
    // financial forecast
    var H = A.slice(-4).filter(function (x) { return x.revenue; }), E = [];
    [['fy0', 'r0', 'e0'], ['fy1', 'r1', 'e1']].forEach(function (z) {
      var fy = dd(an[z[0]]);
      if (fy && an[z[1]] && H.length && fy.getUTCFullYear() > H[H.length - 1].fy) E.push({ fy: fy.getUTCFullYear(), revenue: an[z[1]], eps: an[z[2]] });
    });
    var cols = H.map(function (x) { return ['FY' + x.fy, x.revenue, x.eps_diluted, false, x]; }).concat(E.map(function (x) { return ['FY' + x.fy + ' E', x.revenue, x.eps, true]; }));
    function mini(title, j, fmt) {
      var vv = cols.map(function (x) { return x[j]; }).filter(function (v) { return v > 0; }), mx2 = vv.length ? Math.max.apply(null, vv) : 1;
      return '<div class="card"><h3>' + T(title) + '</h3><div class="fc-chart" role="img" aria-label="' + T(title) + '">' + cols.map(function (x) {
        var v = x[j]; return '<div class="fc-c' + (x[3] ? ' f' : '') + '"><span>' + (nn(v) ? D : fmt(v)) + '</span><i style="height:' + (v ? Math.max(v, 0) / mx2 * 100 : 0).toFixed(0) + '%"></i><em>' + x[0] + '</em></div>';
      }).join('') + '</div></div>';
    }
    function gr(i, j) { if (!i) return D; var a = cols[i][j], b = cols[i - 1][j]; return (!nn(a) && b > 0) ? sp(a / b - 1) : D; }
    var peRow = cols.map(function (x) { if (x[3]) return x[2] > 0 ? x2(px / x[2]) : D; var hv = histVal(c.W, x[4]); return hv.pe ? x2(hv.pe) : D; });
    var chart = E.length ? '<section class="card"><h2>' + T('Financial forecast') + '</h2><div class="fc-2">' + mini('Revenue', 1, usd) + mini('Earnings per share (EPS)', 2, eps) + '</div>' +
      table(cols.map(function (x) { return x[0]; }), cols.map(function () { return ''; }), [
        ['Revenue', cols.map(function (x) { return usd(x[1]); }), 'b'], ['Revenue growth', cols.map(function (x, i) { return gr(i, 1); }), ''],
        ['EPS', cols.map(function (x) { return eps(x[2]); }), 'b'], ['EPS growth', cols.map(function (x, i) { return gr(i, 2); }), ''],
        ['P/E (forward for estimates)', peRow, '']]) +
      note(F('Dashed bars and “E” columns are the average analyst estimate. Past P/E uses the share price at each fiscal year-end; forward P/E divides today’s price (%s) by the estimated EPS. Forecast EPS is adjusted (non-GAAP).', dol(px))) + '</section>' : '';
    function estRows(tr, key, f) { var x = tr[key] || {}; return [f(x.low), f(x.avg), f(x.high), sp(x.growth), String(x.numberOfAnalysts || D)]; }
    var ann = [];
    [[y0.end ? 'FY' + dd(y0.end).getUTCFullYear() : T('This year'), y0], [y1.end ? 'FY' + dd(y1.end).getUTCFullYear() : T('Next year'), y1]].forEach(function (z) {
      if (z[1].p) { ann.push([F('%s revenue', z[0]), estRows(z[1], 'rev', usd), 'b']); ann.push([F('%s EPS', z[0]), estRows(z[1], 'eps', eps), '']); }
    });
    var qs = [];
    [['0q', 'Next quarter'], ['+1q', 'Quarter after']].forEach(function (z) {
      var tr = TR[z[0]]; if (!tr) return;
      var e = dd(tr.end), lb = T(z[1]) + (e ? ' (' + F('ends %s', fmtM.format(e).replace('.', '') + ' ' + e.getUTCFullYear()) + ')' : '');
      qs.push([F('%s revenue', lb), estRows(tr, 'rev', usd), 'b']); qs.push([F('%s EPS', lb), estRows(tr, 'eps', eps), '']);
    });
    var hdr = [T('Low'), T('Average'), T('High'), T('Growth'), T('Analysts')];
    var est = ann.length ? '<section class="card"><h2>' + T('Revenue and earnings estimates') + '</h2>' + table(hdr, ['', '', '', '', ''], ann) +
      '<h3>' + T('Next two quarters') + '</h3>' + table(hdr, ['', '', '', '', ''], qs, 'Quarter') +
      note(T('Growth compares the average estimate with the same period a year earlier. EPS estimates are adjusted (non-GAAP).')) + '</section>' : '';
    var acts = (k.actions || []).slice(0, 15).map(function (a) {
      var dte = ep(a.d), ptxt = (a.ppt && a.pt) ? dol(a.ppt, 0) + ' → ' + dol(a.pt, 0) : a.pt ? dol(a.pt, 0) : D;
      var rating = (a.from && a.from !== a.to) ? a.from + ' → ' + a.to : (a.to || D);
      return '<tr><td>' + esc(a.firm || D) + '</td><td>' + esc(rating) + '</td><td>' + T(ACT[a.act] || (a.act || '')) + '</td><td>' + B(ptxt) + '</td><td>' + B(a.pt ? sp(a.pt / px - 1) : D) + '</td><td>' + sdate(dte) + '</td></tr>';
    });
    var actions = acts.length ? '<section class="card"><h2>' + T('Latest analyst actions') + '</h2><div class="fb-tw"><table class="fb-t"><thead><tr><th>' + T('Firm') + '</th><th>' + T('Rating') + '</th><th>' + T('Action') + '</th><th>' + T('Price target') + '</th><th>' + T('Upside') + '</th><th>' + T('Date') + '</th></tr></thead><tbody>' + acts.join('') + '</tbody></table></div></section>' : '';
    return '<div class="fc-root">' + lead + '<div class="fc-2">' + priceCard + rateCard + '</div>' + chart + est + actions + '</div>';
  }

  // ---------------------------------------------------------------- data loading
  var DATA = {};
  function getJSON(u) { return fetch(u).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function load(t) {
    if (DATA[t]) return DATA[t];
    var api = window.RZS_API || (RAW + '/main/data');
    DATA[t] = Promise.all([
      getJSON(api + '/stocks/' + encodeURIComponent(t) + '.json'),
      getJSON(RAW + '/keystats/' + encodeURIComponent(t) + '.json').catch(function () { return {}; }),
      getJSON(RAW + '/prices/' + encodeURIComponent(t) + '.json').then(function (j) { return j.w || []; }).catch(function () { return []; })
    ]).then(function (x) { return ctx(x[0], x[1], x[2]); });
    DATA[t].catch(function () { delete DATA[t]; });
    return DATA[t];
  }
  window.FIN2 = { load: load, summary: summary, income: income, balance: balance, cash: cash, ratios: ratios, forecast: forecast };

  // ---------------------------------------------------------------- the tool page (#rzs-main)
  var SUBS = [['income', 'Income statement'], ['balance', 'Balance sheet'], ['cash', 'Cash flow'], ['ratios', 'Ratios'], ['forecast', 'Forecast']];
  var STMT_RE = CFG.stmtRe || /10-year financial statements|Estados financieros de 10|10 yıllık mali tablolar|صورت‌های مالی ۱۰ ساله/i;
  var cur = '';
  var FIXED = null;
  function tk() { return FIXED || decodeURIComponent((location.hash || '').slice(1)).toUpperCase().split(/[?&\/]/)[0]; }
  function statCards(main) { return [].slice.call(main.querySelectorAll('.card')).filter(function (c) { return c.querySelector(':scope > .stats'); }); }
  function stmtCard(main) {
    if (CFG.stmtSel) { var s = main.querySelector(CFG.stmtSel); if (s) return s.closest('.card') || s; }
    var hs = main.querySelectorAll('h3,h2');
    for (var i = 0; i < hs.length; i++) if (STMT_RE.test(hs[i].textContent)) return hs[i].closest('.card');
    return null;
  }
  function fail(el) { if (el) el.innerHTML = '<p class="xnote">' + T('Could not load this section.') + '</p>'; }
  function show(t, u) {
    cur = u;
    var box = document.getElementById('v2'), body = document.getElementById('v2-body');
    if (!box) return;
    box.querySelectorAll('.fb-tabs button').forEach(function (b) { var on = b.getAttribute('data-u') === u; b.classList.toggle('on', on); b.setAttribute('aria-selected', on); });
    var per = box.querySelector('.fb-per');
    per.style.visibility = u === 'forecast' ? 'hidden' : 'visible';
    per.querySelectorAll('button').forEach(function (b, i) { b.classList.toggle('on', i === 0); });
    load(t).then(function (c) {
      if (cur !== u || tk() !== t) return;
      try { body.innerHTML = window.FIN2[u](c); } catch (e) { console.error(e); fail(body); }
    }).catch(function () { fail(body); });
  }
  function putSummary(t, cards) {
    var old = document.getElementById('v2s');
    if (old && old.getAttribute('data-t') === t) return;
    if (old) old.remove();
    var box = document.createElement('div');
    box.id = 'v2s'; box.setAttribute('data-t', t); box.className = 'card sa-stk fb v2' + (RTL ? ' fb-rtl' : '');
    box.innerHTML = '<div class="v2-head"><h3 style="margin:0">' + F('%s key statistics', t) + '</h3></div><div id="v2s-body"><p class="xnote">' + T('Loading…') + '</p></div>';
    cards[0].parentNode.insertBefore(box, cards[0]);
    cards.forEach(function (c) { c.classList.add('v2-hide'); });
    var nx = cards[cards.length - 1].nextElementSibling;
    if (nx && nx.classList.contains('xnote')) nx.classList.add('v2-hide');
    load(t).then(function (c) { var b = document.getElementById('v2s-body'); if (b && tk() === t) b.innerHTML = summary(c); })
      .catch(function () { fail(document.getElementById('v2s-body')); });
  }
  function putStatements(t, sc) {
    var old = document.getElementById('v2');
    if (old && old.getAttribute('data-t') === t) return;
    if (old) old.remove();
    var box = document.createElement('div');
    box.id = 'v2'; box.setAttribute('data-t', t); box.className = 'card sa-stk fb v2' + (RTL ? ' fb-rtl' : '');
    box.innerHTML = '<div class="v2-head"><h3 style="margin:0">' + F('%s financial statements & forecast', t) + '</h3></div>' +
      '<div class="fb-bar"><div class="fb-tabs" role="tablist">' + SUBS.map(function (s) { return '<button type="button" role="tab" data-u="' + s[0] + '">' + T(s[1]) + '</button>'; }).join('') + '</div>' +
      '<div class="fb-per" role="group"><button type="button" class="on" data-p="a">' + T('Annual') + '</button><button type="button" data-p="q">' + T('Quarterly') + '</button><button type="button" data-p="t">TTM</button></div></div>' +
      '<div id="v2-body"><p class="xnote">' + T('Loading…') + '</p></div>';
    sc.parentNode.insertBefore(box, sc);
    sc.classList.add('v2-hide');
    box.addEventListener('click', function (ev) {
      var b = ev.target.closest('button'); if (!b) return;
      if (b.hasAttribute('data-u')) { show(t, b.getAttribute('data-u')); return; }
      if (b.hasAttribute('data-p')) {
        b.parentNode.querySelectorAll('button').forEach(function (x) { x.classList.toggle('on', x === b); });
        box.querySelectorAll('[data-pv]').forEach(function (s) { s.hidden = s.getAttribute('data-pv') !== b.getAttribute('data-p'); });
      }
    });
    show(t, 'income');
  }
  function inject() {
    var t = tk(), main = document.getElementById('rzs-main');
    if (!main || !t) return;
    var cards = statCards(main), sc = stmtCard(main);
    if (!cards.length && !sc) return;
    document.body.classList.add('v2on');
    if (cards.length) putSummary(t, cards);
    if (sc) putStatements(t, sc);
  }
  var obsMain = null, mo = null;
  function bind() {
    var main = document.getElementById('rzs-main');
    if (!main || main === obsMain) return;
    obsMain = main;
    if (mo) mo.disconnect();
    var busy = 0;
    mo = new MutationObserver(function () { if (busy) return; busy = 1; setTimeout(function () { busy = 0; inject(); }, 30); });
    mo.observe(main, { childList: true, subtree: false });
    inject();
  }
  function start() {
    window.addEventListener('hashchange', function () { setTimeout(inject, 50); });
    bind();
    setInterval(bind, 1000);   // the tool page can be re-rendered as a whole (cached copy first, then the fresh one)
  }
  // static stock pages: <div data-fin2="AAPL"></div> gets the key statistics and the statements bar; [data-fin2-hide] is the no-JS fallback it replaces
  function mountAll() {
    var el = document.querySelector('[data-fin2]');
    if (!el) return false;
    FIXED = el.getAttribute('data-fin2').toUpperCase();
    var a = document.createElement('div'), b = document.createElement('div');
    el.appendChild(a); el.appendChild(b);
    if (el.getAttribute('data-fin2-summary') !== '0') putSummary(FIXED, [a]); else a.remove();
    putStatements(FIXED, b);
    [].forEach.call(document.querySelectorAll('[data-fin2-hide]'), function (x) { x.classList.add('v2-hide'); });
    return true;
  }
  function boot() { if (!mountAll()) start(); }
  if (!CFG.noTool) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot(); }
})();
