# -*- coding: utf-8 -*-
"""One ETF page builder, shared by all five sites.

The English, Spanish, Turkish, Arabic and Farsi editions show the same thing and differ only in the
words, the URLs and the countries a reader is likely to be in. Keeping five copies of this file
would guarantee that four of them fall behind, so there is one builder and a language pack per site.

A language pack supplies: UI strings, the per-fund text, the URL for a stock page in that edition,
the country list that edition should answer for, and — for the right-to-left editions — a wrapper
that keeps Latin tickers from flipping the sentence around them.
"""
import json, os, re, datetime as dt, html as H

import etf_country

# A run of Latin letters, digits and the punctuation that belongs inside a name or a figure.
_LAT = re.compile(r"[A-Za-z0-9][A-Za-z0-9&.,'’\-/%+]*(?:\s+[A-Za-z0-9][A-Za-z0-9&.,'’\-/%+]*)*")


def make_iso():
    """Isolate Latin runs inside right-to-left prose.

    Written with the Unicode isolate characters rather than <bdi> markup because this text is HTML
    escaped after it comes back: any tag would be printed instead of applied. A full stop that ends
    the Arabic or Persian sentence is pushed back outside the isolate, otherwise it jumps to the
    wrong side of the line.
    """
    def iso(s):
        if not s:
            return s

        def wrap(m):
            run, tail = m.group(0), ''
            while run and run[-1] in ".-'’,":
                tail = run[-1] + tail
                run = run[:-1]
            return '\u2068' + run + '\u2069' + tail if run else m.group(0)
        return _LAT.sub(wrap, s)
    return iso

TODAY = dt.date.today()
e = lambda s: H.escape(str(s if s is not None else ''), quote=True)


def _num(v, d=1):
    if v is None:
        return '—'
    return ('%.' + str(d) + 'f') % v


def _pct(v, d=0):
    return '—' if v is None else ('%.' + str(d) + 'f%%') % (v * 100)


class Pack:
    """Everything that differs between the five editions."""

    def __init__(self, lang, ui, text, base, stock_url, site, rtl=False, iso=None,
                 countries=None, fdate=None, shariah=False, ucits=None, tool_url=None):
        self.lang = lang
        # labels carry {N} for the number of funds covered (it grows); Persian prints its own digits
        import etf_list as _el
        _n = str(len(_el.ETFS))
        if lang == 'fa':
            _n = _n.translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
        ui = {k: (v.replace('{N}', _n) if isinstance(v, str) else v) for k, v in ui.items()}
        self.ui = ui                 # dict of labels
        self.text = text             # {ticker: (idea, strategy)}
        self.base = base             # '/etfs/' or the localised path
        self.stock_url = stock_url   # fn(ticker) -> url of our page for that company
        self.tool_url = tool_url or stock_url   # fn(ticker) -> interactive stock analysis (holdings tables link here)
        self.site = site
        self.rtl = rtl
        self.iso = iso or (lambda s: s)   # isolate Latin runs inside RTL text
        self.countries = countries or etf_country.GROUPS.get(lang, [])
        self.fdate = fdate or (lambda s: str(s or ''))
        self.shariah = shariah
        # the European-alternative notes are written in etf_list.py in English; each edition
        # supplies its own wording for them, keyed by the English string
        self.ucits = ucits or {}

    def u(self, t=None):
        return self.base if not t else '%s%s/' % (self.base, t.lower())

    def L(self, k, **kw):
        """A label, with named fields.

        Named rather than positional because translations reorder: Turkish puts the total before the
        count where English puts it after, and a positional '%d' then lands on a string.
        """
        s = self.ui.get(k, k)
        return (s % kw) if kw else s


# ---------------------------------------------------------------- pieces of a page

_WS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_src')


def _asset(n):
    try:
        return open(os.path.join(_WS, n), encoding='utf-8').read()
    except Exception:
        return ''


ETFM_CSS, ETFM_JS = _asset('etfm.css'), _asset('etfm.js')


def assets(p):
    """The ranking, finder and phone layout (web_src/etfm.*), on the page itself. The Persian edition loads pages as
    fragments into a shell that already carries them (gen_web.py), so it sets inline_assets = False."""
    if not getattr(p, 'inline_assets', True):
        return ''
    return '<style>%s</style><script>%s</script>' % (ETFM_CSS.replace('#ID ', ''), ETFM_JS)


QK_HOME = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9v12h13V9"/><path d="M10 21v-6h4v6"/></svg>'
QK_LIST = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></svg>'
QK_FIND = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>'


def quick_keys(p, keys, etf_home=False):
    """The sticky four-key bar (web_src/qk.js): jump to a part of the fund page, go home, search for a stock."""
    su = p.tool_url('QKT')
    url = getattr(p, 'qk_url', None) or su.replace('QKT', '{t}').replace('qkt', '{l}')
    idx = getattr(p, 'qk_idx', None) or '/assets/search.json'
    return ('<nav class="qkb" aria-label="%s" data-ph="%s" data-none="%s" data-idx="%s" data-url="%s">'
            '<a class="qkb-i qkb-home" href="%s" aria-label="%s" title="%s">%s</a>%s<div class="qkb-k">%s</div>'
            '<button class="qkb-i qkb-find" type="button" aria-label="%s">%s</button></nav>'
            % (e(p.L('k_sec')), e(p.L('k_ph')), e(p.L('k_none')), e(idx), e(url), e(getattr(p, 'home_url', None) or '/'), e(p.L('home')), e(p.L('home')), QK_HOME,
               '' if etf_home else '<a class="qkb-i qkb-list" href="%s" aria-label="%s" title="%s">%s</a>' % (e(p.u()), e(p.L('etfs')), e(p.L('etfs')), QK_LIST),
               ''.join('<a href="#%s">%s</a>' % (i, e(l)) for i, l in keys), e(p.L('k_find')), QK_FIND))


def sret(v, p):
    if v is None:
        return '<span class="mut">—</span>'
    cls = 'up' if v >= 0 else 'dn'
    body = ('+' if v >= 0 else '-') + _pct(abs(v), 1)
    return '<span class="%s"><bdi dir="ltr">%s</bdi></span>' % (cls, body) if p.rtl \
        else '<span class="%s">%s</span>' % (cls, body)


def ltr(s, p):
    """A ticker, a price or anything else Latin, kept from reordering the line around it."""
    return '<bdi dir="ltr" class="ltr">%s</bdi>' % e(s) if p.rtl else e(s)


def ranking(rows, p):
    """Every fund ranked by return, in large readable rows: the top ten, then all; past year or yearly average."""
    rows = [r for r in rows if r.get('y1') is not None]
    if not rows:
        return ''
    rows = sorted(rows, key=lambda r: -r['y1'])
    mx = max(abs(r['y1']) for r in rows) or 1.0
    li = []
    for i, r in enumerate(rows):
        v = r['y1']
        li.append('<li data-y1="%s" data-cagr="%s" data-y1f="%s" data-cagrf="%s"><a href="%s"><span class="erk-n">%d</span>'
                  '<span class="erk-t"><b>%s</b><small>%s</small></span><span class="erk-b"><i style="width:%.1f%%"%s></i></span><em>%s</em></a></li>'
                  % ('%.4f' % v, ('%.4f' % r['cagr']) if r.get('cagr') is not None else '', e(sret(v, p)), e(sret(r.get('cagr'), p)),
                     p.u(r['t']), i + 1, e(r['t']), ltr(r['name'], p), max(2.0, abs(v) / mx * 100), ' class="n"' if v < 0 else '', sret(v, p)))
    return ('<section class="card erk" id="e-rank"><div class="erk-h"><h2>%s</h2><div class="erk-p">'
            '<button type="button" data-p="y1" class="on" aria-pressed="true">%s</button><button type="button" data-p="cagr" aria-pressed="false">%s</button></div></div>'
            '<ol class="erk-l cut">%s</ol><button type="button" class="erk-more" data-all="%s" data-less="%s">%s</button><p class="note">%s</p></section>'
            % (e(p.L('rank_h')), e(p.L('y1')), e(p.L('avg_yr')), ''.join(li),
               e(p.L('rank_all', n=len(rows))), e(p.L('rank_less')), e(p.L('rank_all', n=len(rows))), e(p.L('rank_note'))))


def bars(rows, p):
    rows = [r for r in rows if r.get('y1') is not None]
    if not rows:
        return ''
    rows = sorted(rows, key=lambda r: -(r['y1'] or 0))
    lo, hi = min(0.0, min(r['y1'] for r in rows)), max(0.0, max(r['y1'] for r in rows))
    span = (hi - lo) or 1.0
    rh, pad, lw = 19, 8, 56
    w, h = 760, pad * 2 + rh * len(rows)
    zero = lw + (0 - lo) / span * (w - lw - 70)
    out = ['<svg viewBox="0 0 %d %d" class="etfbars" dir="ltr" role="img" aria-label="%s">'
           % (w, h, e(p.L('chartcap')))]
    out.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="ax"/>' % (zero, pad, zero, h - pad))
    for i, r in enumerate(rows):
        y, v = pad + i * rh, r['y1']
        x2 = lw + (v - lo) / span * (w - lw - 70)
        x1, x2 = (zero, x2) if v >= 0 else (x2, zero)
        out.append('<a href="%s"><rect x="%.1f" y="%d" width="%.1f" height="%d" rx="2" class="%s"/>'
                   '<text x="2" y="%d" class="tk">%s</text><text x="%.1f" y="%d" class="vl">%s%s</text></a>'
                   % (p.u(r['t']), x1, y + 3, max(x2 - x1, 1.0), rh - 7, 'bp' if v >= 0 else 'bn',
                      y + rh - 6, e(r['t']), (x2 + 5) if v >= 0 else (x1 - 5), y + rh - 6,
                      '+' if v >= 0 else '-', _pct(abs(v), 1)))
    out.append('</svg>')
    return '<figure class="etfchart">%s<figcaption>%s</figcaption></figure>' % (''.join(out), e(p.L('chartcap')))


def line(series, p, h=170):
    """The price since launch; a second, taller drawing for phones, where the wide one shrinks to a sliver."""
    d = _line(series, p, h=h)
    if not d:
        return ''
    m = _line(series, p, h=250, w=430, every=3)
    pts = [x for x in (series or []) if x and x[1]]
    return ('<figure class="etfline">%s%s<figcaption>%s</figcaption></figure>'
            % (d.replace('<svg ', '<svg class="dsk" ', 1), m.replace('<svg ', '<svg class="mob" ', 1), e(p.L('linecap', year=pts[0][0][:4]))))


def _line(series, p, h=170, w=760, every=6):
    pts = [x for x in (series or []) if x and x[1]]
    if len(pts) < 4:
        return ''
    vals = [x[1] for x in pts]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    step = (w - 54) / (len(pts) - 1)
    d = ' '.join('%s%.1f,%.1f' % ('M' if i == 0 else 'L', 46 + i * step, h - 20 - (v - lo) / span * (h - 42))
                 for i, v in enumerate(vals))
    area = d + ' L%.1f,%.1f L46,%.1f Z' % (46 + (len(pts) - 1) * step, h - 20, h - 20)
    ticks = ''.join('<text x="40" y="%.1f" class="yl">$%s</text>' % (y + 4, _num(v, 0))
                    for y, v in ((h - 20, lo), (h - 20 - (h - 42) / 2, (lo + hi) / 2), (21, hi)))
    yrs, seen = [], set()
    for i, x in enumerate(pts):
        if x[0][:4] not in seen:
            seen.add(x[0][:4])
            yrs.append((i, x[0][:4]))
    xl = ''.join('<text x="%.1f" y="%d" class="xl">%s</text>' % (46 + i * step, h - 5, y)
                 for i, y in yrs[::max(1, len(yrs) // every)])
    return ('<svg viewBox="0 0 %d %d" dir="ltr" role="img"><path d="%s" class="ar"/><path d="%s" class="ln"/>%s%s</svg>'
            % (w, h, area, d, ticks, xl))


def sectors(sd, holds, p, labels=None):
    agg = {}
    for hld in holds:
        t = hld.get('t')
        if not t:
            continue
        try:
            d = json.load(open(os.path.join(sd, 'data', 'stocks', t + '.json')))
        except Exception:
            continue
        s = (d.get('market') or {}).get('sector') or 'Other'
        agg[s] = agg.get(s, 0) + (hld.get('pct') or 0)
    if not agg:
        return ''
    tot = sum(agg.values()) or 1
    rows = sorted(agg.items(), key=lambda x: -x[1])[:10]
    lab = labels or {}
    return ('<h3>%s</h3><div class="secbars">%s</div>'
            % (e(p.L('made')),
               ''.join('<div><span>%s</span><i><b style="width:%.1f%%"></b></i><em>%s</em></div>'
                       % (e(lab.get(s, s)), min(100.0, v / tot * 100), _pct(v / 100, 1)) for s, v in rows)))


def where(rec, p):
    u = rec.get('ucits') or {}
    tr = p.ucits
    alt = u.get('ticker')
    nm = tr.get(u.get('name') or '', u.get('name') or '')
    note = tr.get(u.get('note') or '', u.get('note') or '')
    body = '<p>%s</p>' % p.L('priips', fund=ltr(rec['t'], p))
    if (alt or nm) and not p.ui.get('skip_ucits'):
        # the ticker is Latin and must not reorder the line; the description is in the page's own
        # language and must not be forced into a Latin run, which is what broke the Arabic layout
        bits = []
        if alt:
            bits.append(ltr(alt, p))
        if nm:
            bits.append(e(p.iso(nm)) if p.rtl else e(nm))
        body += '<p><b>%s</b> %s %s</p>' % (e(p.L('in_europe')), ' — '.join(bits), e(p.iso(note)) if p.rtl else e(note))
    rows = []
    for c in p.countries:
        info = etf_country.COUNTRIES.get(c)
        if not info:
            continue
        cls = {'blocked': 'no', 'sanctions': 'no', 'hard': 'mid'}.get(info['status'], 'yes')
        rows.append('<tr><th>%s</th><td class="%s">%s</td><td>%s</td></tr>'
                    % (e(p.L('c_' + c, ) if ('c_' + c) in p.ui else c), cls,
                       e(p.L('s_' + info['status']) if ('s_' + info['status']) in p.ui
                         else etf_country.LABEL[info['status']]),
                       e(p.L('w_' + c) if ('w_' + c) in p.ui else info['why'])))
    if rows:
        body += ('<div class="tw"><table class="ctry"><tbody>%s</tbody></table></div>'
                 '<p class="note">%s</p>' % (''.join(rows), e(p.L('note_ctry'))))
    if p.shariah:
        s = etf_country.SHARIAH.get(rec['t'])
        if s:
            tick, why = s
            body += ('<h3>%s</h3><p>%s %s</p>'
                     % (e(p.L('shariah')), ltr(tick, p) if tick else '', e(why)))
    return '<section class="card"><h2>%s</h2>%s</section>' % (e(p.L('where')), body)


def detail(sd, rec, spy, p, sector_labels=None):
    t, nm = rec['t'], rec['name']
    w, r = rec.get('weighted') or {}, rec.get('returns') or {}
    idea, strat = (p.text.get(t) or (rec['idea'], rec['strategy']))

    head = ('<nav class="crumbs"><a href="/">%s</a> › <a href="%s">%s</a> › %s</nav>'
            '<div class="top"><div><h1>%s <span class="tk">%s</span></h1>'
            '<p class="sub">%s · %s · %s</p></div>'
            '<div class="px"><b>$%s</b><span>%s %s</span></div></div>'
            % (e(p.L('home')), p.u(), e(p.L('etfs')), ltr(t, p),
               ltr(nm, p), ltr(t, p), ltr(rec['issuer'], p), ltr(rec['index'], p), rec['since'],
               _num(rec.get('price'), 2), e(p.L('y1')), sret(r.get('y1'), p)))

    about = ('<section class="card" id="e-idea"><h2>%s</h2><p class="lead">%s</p><p>%s</p></section>'
             % (e(p.L('idea')), e(p.iso(idea)), e(p.iso(strat))))

    kv = [(p.L('y1'), sret(r.get('y1'), p)), (p.L('ytd'), sret(r.get('ytd'), p)),
          (p.L('y3'), sret(r.get('y3'), p)), (p.L('y5'), sret(r.get('y5'), p)),
          (p.L('m3'), sret(r.get('m3'), p)), (p.L('m1'), sret(r.get('m1'), p))]
    perf = ('<section class="card" id="e-ret"><h2>%s</h2><div class="kv">%s</div>%s<p class="note">%s</p></section>'
            % (e(p.L('ret')), ''.join('<div><span>%s</span><b>%s</b></div>' % (e(a), b) for a, b in kv),
               line(rec.get('chart'), p), e(p.L('note_ret'))))

    fund = ''
    if w.get('not_equity'):
        fund = ('<section class="card" id="e-val"><h2>%s</h2><p>%s</p></section>'
                % (e(p.L('no_pe_h')), e(p.L('no_pe_bond', n=_num(w.get('holdings_n'), 0)))))
    elif w.get('thin'):
        fund = ('<section class="card" id="e-val"><h2>%s</h2><p>%s</p></section>'
                % (e(p.L('no_pe_h')),
                   e(p.L('no_pe_thin', n=_num(w.get('holdings_n'), 0),
                         cov=_pct((w.get('covered_pct') or 0) / 100, 0)))))
    elif w.get('pe'):
        cmpr = ''
        if spy and (spy.get('weighted') or {}).get('pe') and t != 'SPY':
            sp = spy['weighted']['pe']
            diff = w['pe'] / sp - 1
            cmpr = '<p>%s</p>' % p.L('vs_sp', sp=_num(sp, 1), diff=_pct(abs(diff), 0),
                                     dir=p.L('more_exp') if diff > 0 else p.L('cheaper'))
        rows = [(p.L('pe'), _num(w.get('pe'), 1)), (p.L('ps'), _num(w.get('ps'), 2)),
                (p.L('growth'), _pct(w['revenue_growth'], 1) if w.get('revenue_growth') is not None else '—'),
                (p.L('margin'), _pct(w['net_margin'], 1) if w.get('net_margin') is not None else '—'),
                (p.L('score'), (_num(w.get('score'), 1) + ' / 5') if w.get('score') else '—'),
                (p.L('holdings'), _num(w.get('holdings_n'), 0))]
        fund = ('<section class="card" id="e-val"><h2>%s</h2><div class="kv">%s</div>%s<p class="note">%s</p></section>'
                % (e(p.L('fund')),
                   ''.join('<div><span>%s</span><b>%s</b></div>' % (e(a), b) for a, b in rows), cmpr,
                   e(p.L('note_pe', cov=_pct((w.get('covered_pct') or 0) / 100, 1),
                         n=_num(w.get('covered_n'), 0), total=_num(w.get('holdings_n'), 0)))))

    holds = rec.get('holdings') or []
    tbl = ''
    if holds:
        top = holds[:40]
        mx = max((h['pct'] for h in top), default=1) or 1
        rows = ''.join(
            '<tr%s><td class="hn">%s</td><td class="hw"><i><b style="width:%.1f%%"></b></i>%s</td></tr>'
            % (' class="hx"' if i >= 10 else '',
               ('<a href="%s">%s</a> <span class="tk2">%s</span>'
                % (p.tool_url(h['t']), ltr(h['name'], p), ltr(h['t'], p))) if h.get('t') else ltr(h['name'], p),
               min(100.0, h['pct'] / mx * 100), _pct(h['pct'] / 100, 2)) for i, h in enumerate(top))
        more = ('<button type="button" class="hold-more" data-all="%s" data-less="%s">%s</button>'
                % (e(p.L('holds_all', n=len(top))), e(p.L('holds_less')), e(p.L('holds_all', n=len(top))))) if len(top) > 10 else ''
        tbl = ('<section class="card" id="e-hold"><h2>%s</h2><div class="tw"><table class="hold%s">'
               '<thead><tr><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>%s%s'
               '<p class="note">%s</p></section>'
               % (e(p.L('holds')), ' cut' if more else '', e(p.L('company')), e(p.L('weight')), rows, more,
                  sectors(sd, holds, p, sector_labels),
                  e(p.L('note_holds', n=len(top), total=_num(w.get('holdings_n'), 0),
                        asof=(' · ' + p.fdate(rec['holdings_as_of'])) if rec.get('holdings_as_of') else ''))))

    qk = quick_keys(p, [('e-idea', p.L('k_idea')), ('e-val', p.L('k_val')), ('e-ret', p.L('k_ret')), ('e-hold', p.L('k_hold'))])
    body = ('<article class="sa-list sa-etf">%s%s%s%s%s%s%s<p class="dis">%s</p>%s</article>'
            % (head, qk, about, fund, perf, tbl, where(rec, p), e(p.L('dis')), assets(p)))
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': p.L('home'), 'item': p.site + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': p.L('etfs'), 'item': p.site + p.u()},
        {'@type': 'ListItem', 'position': 3, 'name': '%s (%s)' % (nm, t), 'item': p.site + p.u(t)}]}]
    return dict(url=p.u(t), title=p.L('d_title', t=t)[:62],
                desc=p.L('d_desc', name=nm, t=t, idea=idea)[:300],
                html=body, ld=ld)


def _dv(v):
    """A number for a data- attribute (sorting); empty when missing."""
    return '' if v is None else '%.4f' % v


def index_page(idx, recs, p):
    """One box holding all fifty funds, each row clickable through to its own page."""
    rows = idx.get('etfs') or []
    rank = {r['t']: i for i, r in enumerate(rows)}          # the list comes largest fund first
    rows = sorted(rows, key=lambda r: -(r.get('y1') if r.get('y1') is not None else -9))
    focus = p.ui.get('focus_labels') or {}
    # A fund's name is its issuer plus the index it tracks, and both are proper nouns. Rather than
    # invent translations of brand names, each edition supplies the grammar that joins them.
    pat = p.ui.get('name_pattern') or '%(issuer)s %(index)s'
    since = next((r.get('pe_since') for r in rows if r.get('pe_since')), None)

    def cell_pct(v):
        return sret(v, p)

    body_rows = []
    for r in rows:
        w = (recs.get(r['t']) or {}).get('weighted') or {}
        idea = (p.text.get(r['t']) or (r.get('idea'), ''))[0]
        rec = recs.get(r['t']) or {}
        local = pat % dict(issuer=rec.get('issuer') or r.get('issuer') or '',
                           index=rec.get('index') or '')
        ty = focus.get(r.get('focus'), r.get('focus') or '')
        srch = ' '.join(x for x in (r['t'], r.get('name'), local, ty, idea) if x).lower()
        body_rows.append(
            '<tr onclick="location.href=\'%s\'" data-k="%d" data-y1="%s" data-cagr="%s" data-pe="%s" data-s="%s">'
            '<td class="nm"><a href="%s"><b>%s</b><span>%s</span></a>%s</td>'
            '<td class="ty">%s</td>'
            '<td class="y1" data-l="%s">%s</td><td class="cg" data-l="%s">%s</td>'
            '<td class="ho" data-l="%s">%s</td><td class="pe" data-l="%s">%s</td><td class="pa">%s</td></tr>'
            % (p.u(r['t']), rank.get(r['t'], 99), _dv(r.get('y1')), _dv(r.get('cagr')), _dv(w.get('pe')), e(srch),
               p.u(r['t']), e(r['t']), ltr(r['name'], p),
               ('<i>%s</i>' % e(p.iso(local))) if local else ('<i>%s</i>' % e(p.iso(idea))),
               e(ty),
               e(p.L('l_y1')), cell_pct(r.get('y1')), e(p.L('l_avg')), cell_pct(r.get('cagr')),
               e(p.L('l_hold')), _num(r.get('holdings_n'), 0) if r.get('holdings_n') else '—',
               e(p.L('l_pe')), _num(w.get('pe'), 1) if w.get('pe') else '—',
               _num(r.get('pe_avg'), 1) if r.get('pe_avg') else '—'))

    find = ('<div class="etfbar"><label class="etfq-w"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>'
            '<input class="etfq" type="search" placeholder="%s" aria-label="%s" autocomplete="off" spellcheck="false" enterkeyhint="search" dir="auto"></label>'
            '<div class="etfsort"><button type="button" data-k="y1" class="on" aria-pressed="true">%s</button><button type="button" data-k="cagr" aria-pressed="false">%s</button>'
            '<button type="button" data-k="k" aria-pressed="false">%s</button><button type="button" data-k="pe" aria-pressed="false">%s</button></div>'
            '<span class="etfcnt" data-f="%s">%s</span></div>'
            % (e(p.L('find_ph')), e(p.L('find_ph')), e(p.L('l_y1')), e(p.L('l_avg')), e(p.L('sort_big')), e(p.L('sort_pe')),
               e(p.ui.get('n_funds', '%n')), e(p.ui.get('n_funds', '%n').replace('%n', str(len(rows))))))
    box = ('<section class="card etfbox" id="e-all">%s<div class="tw"><table class="etftbl">'
           '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>'
           '<tbody>%s</tbody></table></div><p class="etfnone" hidden>%s</p><p class="note">%s</p>'
           '<p class="note">%s</p></section>'
           % (find, e(p.L('fundcol')), e(p.L('type')), e(p.L('y1')), e(p.L('avg_yr')),
              e(p.L('holdings')), e(p.ui.get('pe_short') or p.L('pe')), e(p.L('pe_avg')),
              ''.join(body_rows), e(p.L('no_fund')), e(p.L('note_tbl')),
              e(p.L('note_peavg', since=p.fdate(since)) if since else p.L('note_peavg_none'))))

    # a search box right under the title: type a ticker or a name and jump straight to that fund
    import json as _json
    jl = _json.dumps([[r['t'], r.get('name') or '', p.u(r['t']),
                       ' '.join(x for x in (r['t'], r.get('name'), (recs.get(r['t']) or {}).get('index'),
                                            focus.get(r.get('focus'), r.get('focus') or '')) if x).lower()]
                      for r in sorted(rows, key=lambda r: rank.get(r['t'], 99))], ensure_ascii=False).replace('</', '<\\/')
    jump = ('<div class="ejump"><label class="ejump-w"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>'
            '<input id="ejq" type="search" placeholder="%s" aria-label="%s" autocomplete="off" spellcheck="false" enterkeyhint="go" dir="auto"></label>'
            '<ul id="ejr" class="ejr" role="listbox" hidden></ul></div>'
            '<style>.ejump{position:relative;margin:14px 0 6px}.ejump-w{display:flex;align-items:center;gap:8px;border:1px solid var(--line,#2a3340);'
            'border-radius:12px;padding:10px 12px;background:var(--card,#141a22)}.ejump-w svg{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:2;opacity:.6}'
            '.ejump-w input{flex:1;min-width:0;border:0!important;outline:0!important;box-shadow:none!important;padding:0!important;background:transparent!important;color:inherit;font:inherit;font-size:16px}'
            '.ejr{position:absolute;z-index:30;left:0;right:0;top:100%%;margin:4px 0 0;padding:4px;list-style:none;border:1px solid var(--line,#2a3340);'
            'border-radius:12px;background:var(--card,#141a22);box-shadow:0 10px 30px rgba(0,0,0,.35);max-height:60vh;overflow:auto}'
            '.ejr a{display:flex;gap:10px;align-items:baseline;padding:9px 10px;border-radius:8px;color:inherit;text-decoration:none}'
            '.ejr a b{min-width:52px}.ejr a span{opacity:.75;font-size:.92em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
            '.ejr li.on a,.ejr a:hover{background:rgba(127,127,127,.15)}</style>'
            '<script>(function(){var D=%s,q=document.getElementById("ejq"),u=document.getElementById("ejr"),k=-1,m=[];'
            'function esc(s){return s.replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c]})}'
            'function show(){var v=q.value.trim().toLowerCase();k=-1;if(!v){u.hidden=true;return}'
            'm=D.filter(function(d){return d[0].toLowerCase().indexOf(v)===0}).concat(D.filter(function(d){return d[0].toLowerCase().indexOf(v)!==0&&d[3].indexOf(v)>-1})).slice(0,8);'
            'u.innerHTML=m.length?m.map(function(d){return \'<li><a href="\'+d[2]+\'"><b dir="ltr">\'+d[0]+\'</b><span dir="ltr">\'+esc(d[1])+\'</span></a></li>\'}).join(""):\'<li><a>%s</a></li>\';u.hidden=false}'
            'q.addEventListener("input",show);q.addEventListener("focus",show);'
            'q.addEventListener("keydown",function(e){var l=u.querySelectorAll("li");if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();if(!l.length)return;'
            'k=(k+(e.key==="ArrowDown"?1:-1)+l.length)%%l.length;l.forEach(function(x,i){x.classList.toggle("on",i===k)})}'
            'else if(e.key==="Enter"&&m.length){e.preventDefault();location.href=m[k<0?0:k][2]}else if(e.key==="Escape"){u.hidden=true}});'
            'document.addEventListener("click",function(e){if(!e.target.closest(".ejump"))u.hidden=true})})();</script>'
            % (e(p.L('find_ph')), e(p.L('find_ph')), jl, e(p.L('no_fund'))))
    qk = quick_keys(p, [('e-rank', p.L('rank_h')), ('e-all', p.ui.get('n_funds', '%n').replace('%n', str(len(rows))))], etf_home=True)
    body = (('<article class="sa-list sa-etf">' + qk.replace('%', '%%') + '<h1>%s</h1>' + jump.replace('%', '%%') + '<p class="sub">%s %s</p>'
            '<p class="lead">%s</p><p class="etfintro clip">%s</p><button type="button" class="etfmore" hidden data-more="%s" data-less="%s">%s</button>'
            '%s%s<p class="dis">%s</p>%s</article>')
            % (e(p.L('h1')), e(p.L('sub')), ltr(p.fdate(TODAY.strftime('%Y-%m')), p), e(p.L('lead')), e(p.L('intro')),
               e(p.L('more')), e(p.L('less')), e(p.L('more')),
               ranking(rows, p), box, e(p.L('dis')), assets(p)))
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': p.L('home'), 'item': p.site + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': p.L('etfs'), 'item': p.site + p.u()}]},
        {'@context': 'https://schema.org', '@type': 'ItemList',
         'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': '%s (%s)' % (r['name'], r['t']),
                              'url': p.site + p.u(r['t'])} for i, r in enumerate(rows)]}]
    return dict(url=p.u(), title=p.L('i_title')[:62], desc=p.L('i_desc')[:300], html=body, ld=ld)


# ---------------------------------------------------------------- comparisons and "which ETFs hold X"
# Pairs people search for ("VOO vs QQQ"), plus each fund against its closest peers of the same type.
PAIRS = [('VOO', 'QQQ'), ('VOO', 'VTI'), ('SPY', 'VOO'), ('VOO', 'IVV'), ('SPY', 'QQQ'), ('SCHD', 'VYM'),
         ('SCHD', 'JEPI'), ('JEPI', 'JEPQ'), ('QQQ', 'VGT'), ('VGT', 'XLK'), ('SMH', 'SOXX'), ('VTI', 'VT'),
         ('VXUS', 'VEA'), ('VWO', 'IEMG'), ('BND', 'AGG'), ('GLD', 'IAU'), ('GLD', 'GLDM'), ('IBIT', 'FBTC'),
         ('VUG', 'VTV'), ('QQQ', 'SCHG'), ('VOO', 'SCHD'), ('VTI', 'SCHB'), ('RSP', 'VOO'), ('TLT', 'IEF'),
         ('SGOV', 'BIL'), ('HYG', 'JNK'), ('VIG', 'SCHD'), ('DGRO', 'VIG'), ('IWM', 'VB'), ('XBI', 'IBB'),
         ('MTUM', 'QUAL'), ('USMV', 'QUAL'), ('EEM', 'VWO'), ('MCHI', 'FXI'), ('VOO', 'VUG'), ('ARKK', 'QQQ'),
         ('XLE', 'XOP'), ('GDX', 'GLD'), ('SLV', 'GLD'), ('ACWI', 'VT'), ('IXUS', 'VXUS'), ('SCHF', 'VEA'),
         ('VCIT', 'LQD'), ('VCSH', 'BSV'), ('MUB', 'VTEB'), ('SHY', 'SGOV'), ('TIP', 'IEF'), ('XLU', 'XLP'),
         ('QQQ', 'QQQM'), ('QQQ', 'TQQQ'), ('SMH', 'SOXL'), ('VIG', 'NOBL'), ('SCHD', 'HDV'), ('SCHD', 'DVY'),
         ('JEPI', 'DIVO'), ('JEPQ', 'QYLD'), ('VBR', 'AVUV'), ('TLT', 'VGLT'), ('XLE', 'VDE'), ('XLF', 'VFH'),
         ('VUG', 'SPYG'), ('VTV', 'SPYV'), ('IGV', 'VGT'), ('SHY', 'VGSH'), ('TIP', 'SCHP'), ('IJH', 'MDY'), ('IWM', 'IWN')]


def _overlap(a, b):
    """Share of a's weight (top holdings) in companies b also holds, and the shared names."""
    ha = {h['t']: h for h in a.get('holdings') or [] if h.get('t')}
    hb = {h['t']: h for h in b.get('holdings') or [] if h.get('t')}
    common = [t for t in ha if t in hb]
    ov = sum(min(ha[t]['pct'], hb[t]['pct']) for t in common)
    common.sort(key=lambda t: -min(ha[t]['pct'], hb[t]['pct']))
    return ov, [(ha[t]['name'], t, ha[t]['pct'], hb[t]['pct']) for t in common]


def pairs(recs):
    out, seen = [], set()
    def add(a, b):
        if a in recs and b in recs and a != b and frozenset((a, b)) not in seen:
            seen.add(frozenset((a, b))); out.append((a, b))
    for a, b in PAIRS:
        add(a, b)
    by = {}
    for t, r in recs.items():
        by.setdefault(r.get('focus'), []).append(t)
    for f, ts in by.items():
        for i, a in enumerate(ts):
            for b in ts[i + 1:i + 3]:
                add(a, b)
    return out


def cmp_slug(a, b):
    return '%s-vs-%s' % (a.lower(), b.lower())


def compare_page(a, b, recs, p):
    A, B = recs[a], recs[b]
    ra, rb = A.get('returns') or {}, B.get('returns') or {}
    wa, wb = A.get('weighted') or {}, B.get('weighted') or {}
    focus = p.ui.get('focus_labels') or {}
    ia = (p.text.get(a) or (A.get('idea'), ''))[0]
    ib = (p.text.get(b) or (B.get('idea'), ''))[0]
    rows = [(p.L('c_issuer'), ltr(A.get('issuer') or '', p), ltr(B.get('issuer') or '', p)),
            (p.L('c_index'), ltr(A.get('index') or '', p), ltr(B.get('index') or '', p)),
            (p.L('type'), e(focus.get(A.get('focus'), A.get('focus') or '')), e(focus.get(B.get('focus'), B.get('focus') or ''))),
            (p.L('price'), '$' + _num(A.get('price'), 2), '$' + _num(B.get('price'), 2))]
    for k in ('ytd', 'y1', 'y3', 'y5'):
        rows.append((p.L(k), sret(ra.get(k), p), sret(rb.get(k), p)))
    rows.append((p.L('pe'), _num(wa.get('pe'), 1) if wa.get('pe') and not wa.get('thin') else '—',
                 _num(wb.get('pe'), 1) if wb.get('pe') and not wb.get('thin') else '—'))
    rows.append((p.L('holdings'), _num(wa.get('holdings_n'), 0), _num(wb.get('holdings_n'), 0)))
    tbl = ('<div class="tw"><table class="hold cmpt"><thead><tr><th></th><th><a href="%s">%s</a></th><th><a href="%s">%s</a></th></tr></thead><tbody>%s</tbody></table></div>'
           % (p.u(a), ltr(a, p), p.u(b), ltr(b, p),
              ''.join('<tr><td class="hn">%s</td><td>%s</td><td>%s</td></tr>' % (e(k), x, y) for k, x, y in rows)))
    # what the numbers say, in sentences
    say = []
    y1a, y1b = ra.get('y1'), rb.get('y1')
    if y1a is not None and y1b is not None and abs(y1a - y1b) > 0.005:
        w, x, y = (a, y1a, y1b) if y1a > y1b else (b, y1b, y1a)
        say.append(p.L('v_ret', w=w, x=_pct(x, 1), y=_pct(y, 1)))
    pa = wa.get('pe') if not (wa.get('thin') or wa.get('not_equity')) else None
    pb = wb.get('pe') if not (wb.get('thin') or wb.get('not_equity')) else None
    if pa and pb and abs(pa / pb - 1) > 0.05:
        w, x, y = (a, pa, pb) if pa < pb else (b, pb, pa)
        say.append(p.L('v_pe', w=w, x=_num(x, 1), y=_num(y, 1)))
    ov, common = _overlap(A, B)
    if A.get('holdings') and B.get('holdings'):
        say.append(p.L('v_ov', a=a, b=b, ov=_pct(ov / 100, 0)) if ov >= 1 else p.L('v_noov', a=a, b=b))
    shared = ''
    if common:
        shared = ('<h3>%s</h3><div class="tw"><table class="hold"><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>'
                  % (e(p.L('c_shared')), e(p.L('company')), ltr(a, p), ltr(b, p),
                     ''.join('<tr><td class="hn"><a href="%s">%s</a> <span class="tk2">%s</span></td><td>%s</td><td>%s</td></tr>'
                             % (p.tool_url(t), ltr(n, p), ltr(t, p), _pct(x / 100, 2), _pct(y / 100, 2)) for n, t, x, y in common[:10])))
    head = ('<nav class="crumbs"><a href="/">%s</a> › <a href="%s">%s</a> › %s</nav><h1>%s</h1><p class="sub">%s</p>'
            % (e(p.L('home')), p.u(), e(p.L('etfs')), e(p.L('c_crumb', a=a, b=b)), e(p.L('c_h1', a=a, b=b)), e(p.L('c_sub'))))
    ideas = ('<section class="card"><h2>%s</h2><p><b><a href="%s">%s</a></b> — %s</p><p><b><a href="%s">%s</a></b> — %s</p></section>'
             % (e(p.L('c_what')), p.u(a), ltr(a, p), e(p.iso(ia or '')), p.u(b), ltr(b, p), e(p.iso(ib or ''))))
    body = ('<article class="sa-list sa-etf">%s%s%s<section class="card" id="e-side"><h2>%s</h2>%s%s</section>'
            '<section class="card" id="e-says"><h2>%s</h2>%s%s</section><p class="dis">%s</p>%s</article>'
            % (quick_keys(p, [('e-side', p.L('c_side')), ('e-says', p.L('c_says'))]), head, ideas, e(p.L('c_side')), tbl, '<p class="note">%s</p>' % e(p.L('note_ret')),
               e(p.L('c_says')), ''.join('<p>%s</p>' % e(x) for x in say), shared, e(p.L('dis')), assets(p)))
    url = p.u(cmp_slug(a, b))
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': p.L('home'), 'item': p.site + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': p.L('etfs'), 'item': p.site + p.u()},
        {'@type': 'ListItem', 'position': 3, 'name': p.L('c_crumb', a=a, b=b), 'item': p.site + url}]}]
    return dict(url=url, title=p.L('c_title', a=a, b=b)[:62], desc=(' '.join(say) or (p.L('c_h1', a=a, b=b) + ': ' + p.L('c_sub')))[:300], html=body, ld=ld)


def holders(recs):
    """ticker -> (name, [(fund, weight)]) for companies among the published top holdings of 2+ funds."""
    out = {}
    for f, r in recs.items():
        for h in r.get('holdings') or []:
            if h.get('t') and h.get('pct'):
                out.setdefault(h['t'], [h['name'], []])[1].append((f, h['pct']))
    # ETF_MIN_HOLDERS: an edition short on room (Cloudflare's per-deploy file limit) can keep only the companies more funds hold
    least = max(2, int(os.environ.get('ETF_MIN_HOLDERS', '2')))
    return {t: (n, sorted(L, key=lambda x: -x[1])) for t, (n, L) in out.items() if len(L) >= least}


def hold_url(p, t):
    return p.u(p.L('hold_slug') % t.lower())


def holders_page(t, name, rows, recs, p):
    focus = p.ui.get('focus_labels') or {}
    trs = ''.join('<tr><td class="hn"><a href="%s">%s</a> <span class="tk2">%s</span></td><td>%s</td><td>%s</td><td>%s</td></tr>'
                  % (p.u(f), ltr(recs[f]['name'], p), ltr(f, p), e(focus.get(recs[f].get('focus'), recs[f].get('focus') or '')),
                     _pct(w / 100, 2), sret((recs[f].get('returns') or {}).get('y1'), p)) for f, w in rows)
    n_all = len(recs)
    head = ('<nav class="crumbs"><a href="/">%s</a> › <a href="%s">%s</a> › %s</nav><h1>%s</h1><p class="sub">%s</p>'
            % (e(p.L('home')), p.u(), e(p.L('etfs')), ltr(t, p), e(p.L('h_h1', name=name, t=t)),
               e(p.L('h_lead', n=len(rows), N=n_all, name=name))))
    top = rows[0]
    say = p.L('h_top', f=top[0], w=_pct(top[1] / 100, 1), name=name)
    body = ('<article class="sa-list sa-etf">' + quick_keys(p, []).replace('%', '%%') + '%s<section class="card"><p>%s</p><p><a href="%s"><strong>%s</strong></a></p></section>'
            '<style>@media(max-width:620px){table.hold th:nth-child(4),table.hold td:nth-child(4){display:none}}</style><section class="card"><div class="tw"><table class="hold"><thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">%s</p></section><p class="dis">%s</p>%s</article>'
            % (head, e(say), p.stock_url(t), e(p.L('h_stock', name=name)), e(p.L('fundcol')), e(p.L('type')), e(p.L('weight')),
               e(p.L('y1')), trs, e(p.L('h_note', N=n_all)), e(p.L('dis')), assets(p)))
    url = hold_url(p, t)
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': p.L('home'), 'item': p.site + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': p.L('etfs'), 'item': p.site + p.u()},
        {'@type': 'ListItem', 'position': 3, 'name': p.L('h_h1', name=name, t=t), 'item': p.site + url}]}]
    return dict(url=url, title=p.L('h_title', name=name, t=t)[:62],
                desc=(p.L('h_lead', n=len(rows), N=n_all, name=name) + ' ' + say)[:300], html=body, ld=ld)


def related_links(t, prs, p):
    """'Compare with' links for a fund's own page."""
    ls = [(b if a == t else a) for a, b in prs if t in (a, b)][:6]
    if not ls:
        return ''
    return ('<section class="card"><h2>%s</h2><p class="cmpl">%s</p></section>'
            % (e(p.L('c_with', t=t)), ' · '.join('<a href="%s">%s</a>' % (p.u(cmp_slug(*((t, o) if (t, o) in prs else (o, t)))), e(p.L('c_crumb', a=t, b=o))) for o in ls)))


def load(sd):
    d = os.path.join(sd, 'data', 'etfs')
    try:
        idx = json.load(open(os.path.join(d, 'index.json')))
    except Exception:
        return None, {}
    recs = {}
    for row in idx.get('etfs') or []:
        try:
            recs[row['t']] = json.load(open(os.path.join(d, row['t'] + '.json')))
        except Exception:
            continue
    return idx, recs


def build(sd, p, sector_labels=None):
    idx, recs = load(sd)
    if not idx or not recs:
        return []
    spy = recs.get('SPY') or recs.get('VOO')
    pages = [index_page(idx, recs, p)]
    prs = pairs(recs) if 'c_title' in p.ui else []
    for row in idx.get('etfs') or []:
        rec = recs.get(row['t'])
        if rec:
            d = detail(sd, rec, spy, p, sector_labels)
            if prs:
                d['html'] = d['html'].replace('<p class="dis">', related_links(row['t'], prs, p) + '<p class="dis">', 1)
            pages.append(d)
    for a, b in prs:
        pages.append(compare_page(a, b, recs, p))
    if 'h_title' in p.ui:
        try:   # our own company names, not the fund filings' upper-case legal names
            names = {r['t']: r.get('n') for r in json.load(open(os.path.join(sd, 'data', 'index.json')))}
        except Exception:
            names = {}
        local = getattr(p, 'stock_name', None)   # an edition may name companies in its own language
        for t, (name, rows) in sorted(holders(recs).items()):
            nm = local(t) if local else (names.get(t) or name)
            if nm:          # no local name -> no page (the Arabic site only covers companies it profiles)
                pages.append(holders_page(t, nm, rows, recs, p))
    return pages
