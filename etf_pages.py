# -*- coding: utf-8 -*-
"""One ETF page builder, shared by all five sites.

The English, Spanish, Turkish, Arabic and Farsi editions show the same thing and differ only in the
words, the URLs and the countries a reader is likely to be in. Keeping five copies of this file
would guarantee that four of them fall behind, so there is one builder and a language pack per site.

A language pack supplies: UI strings, the per-fund text, the URL for a stock page in that edition,
the country list that edition should answer for, and — for the right-to-left editions — a wrapper
that keeps Latin tickers from flipping the sentence around them.
"""
import json, os, datetime as dt, html as H

import etf_country

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
                 countries=None, fdate=None, shariah=False):
        self.lang = lang
        self.ui = ui                 # dict of labels
        self.text = text             # {ticker: (idea, strategy)}
        self.base = base             # '/etfs/' or the localised path
        self.stock_url = stock_url   # fn(ticker) -> url of our page for that company
        self.site = site
        self.rtl = rtl
        self.iso = iso or (lambda s: s)   # isolate Latin runs inside RTL text
        self.countries = countries or etf_country.GROUPS.get(lang, [])
        self.fdate = fdate or (lambda s: str(s or ''))
        self.shariah = shariah

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

def sret(v, p):
    if v is None:
        return '<span class="mut">—</span>'
    cls = 'up' if v >= 0 else 'dn'
    body = ('+' if v >= 0 else '-') + _pct(abs(v), 1)
    return '<span class="%s"><bdi dir="ltr">%s</bdi></span>' % (cls, body) if p.rtl \
        else '<span class="%s">%s</span>' % (cls, body)


def ltr(s, p):
    """A ticker, a price or anything else Latin, kept from reordering the line around it."""
    return '<bdi dir="ltr">%s</bdi>' % e(s) if p.rtl else e(s)


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
    pts = [x for x in (series or []) if x and x[1]]
    if len(pts) < 4:
        return ''
    vals = [x[1] for x in pts]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    w = 760
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
                 for i, y in yrs[::max(1, len(yrs) // 6)])
    return ('<figure class="etfline"><svg viewBox="0 0 %d %d" dir="ltr" role="img"><path d="%s" class="ar"/>'
            '<path d="%s" class="ln"/>%s%s</svg><figcaption>%s</figcaption></figure>'
            % (w, h, area, d, ticks, xl, e(p.L('linecap', year=pts[0][0][:4]))))


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
    alt, nm, note = u.get('ticker'), u.get('name') or '', u.get('note') or ''
    body = '<p>%s</p>' % p.L('priips', fund=ltr(rec['t'], p))
    if alt or nm:
        body += '<p><b>%s</b> %s %s</p>' % (e(p.L('in_europe')),
                                            ltr('%s — %s' % (alt, nm) if (alt and nm) else (alt or nm), p),
                                            e(note))
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

    about = ('<section class="card"><h2>%s</h2><p class="lead">%s</p><p>%s</p></section>'
             % (e(p.L('idea')), e(p.iso(idea)), e(p.iso(strat))))

    kv = [(p.L('y1'), sret(r.get('y1'), p)), (p.L('ytd'), sret(r.get('ytd'), p)),
          (p.L('y3'), sret(r.get('y3'), p)), (p.L('y5'), sret(r.get('y5'), p)),
          (p.L('m3'), sret(r.get('m3'), p)), (p.L('m1'), sret(r.get('m1'), p))]
    perf = ('<section class="card"><h2>%s</h2><div class="kv">%s</div>%s<p class="note">%s</p></section>'
            % (e(p.L('ret')), ''.join('<div><span>%s</span><b>%s</b></div>' % (e(a), b) for a, b in kv),
               line(rec.get('chart'), p), e(p.L('note_ret'))))

    fund = ''
    if w.get('not_equity'):
        fund = ('<section class="card"><h2>%s</h2><p>%s</p></section>'
                % (e(p.L('no_pe_h')), e(p.L('no_pe_bond', n=_num(w.get('holdings_n'), 0)))))
    elif w.get('thin'):
        fund = ('<section class="card"><h2>%s</h2><p>%s</p></section>'
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
        fund = ('<section class="card"><h2>%s</h2><div class="kv">%s</div>%s<p class="note">%s</p></section>'
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
            '<tr><td class="hn">%s</td><td class="hw"><i><b style="width:%.1f%%"></b></i>%s</td></tr>'
            % (('<a href="%s">%s</a> <span class="tk2">%s</span>'
                % (p.stock_url(h['t']), ltr(h['name'], p), ltr(h['t'], p))) if h.get('t') else ltr(h['name'], p),
               min(100.0, h['pct'] / mx * 100), _pct(h['pct'] / 100, 2)) for h in top)
        tbl = ('<section class="card"><h2>%s</h2><div class="tw"><table class="hold">'
               '<thead><tr><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>%s'
               '<p class="note">%s</p></section>'
               % (e(p.L('holds')), e(p.L('company')), e(p.L('weight')), rows,
                  sectors(sd, holds, p, sector_labels),
                  e(p.L('note_holds', n=len(top), total=_num(w.get('holdings_n'), 0),
                        asof=(' · ' + p.fdate(rec['holdings_as_of'])) if rec.get('holdings_as_of') else ''))))

    body = ('<article class="sa-list sa-etf">%s%s%s%s%s%s<p class="dis">%s</p></article>'
            % (head, about, fund, perf, tbl, where(rec, p), e(p.L('dis'))))
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': p.L('home'), 'item': p.site + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': p.L('etfs'), 'item': p.site + p.u()},
        {'@type': 'ListItem', 'position': 3, 'name': '%s (%s)' % (nm, t), 'item': p.site + p.u(t)}]}]
    return dict(url=p.u(t), title=p.L('d_title', t=t)[:62],
                desc=p.L('d_desc', name=nm, t=t, idea=idea)[:300],
                html=body, ld=ld)


def index_page(idx, recs, p):
    rows = idx.get('etfs') or []

    def card(r):
        w = (recs.get(r['t']) or {}).get('weighted') or {}
        idea = (p.text.get(r['t']) or (r.get('idea'), ''))[0]
        return ('<a class="etfcard" href="%s"><div class="r1"><b>%s</b><span>%s</span></div>'
                '<p>%s</p><div class="r2"><em>$%s</em>%s%s</div></a>'
                % (p.u(r['t']), e(r['t']), ltr(r['name'], p), e(p.iso(idea)),
                   _num(r.get('price'), 2), sret(r.get('y1'), p),
                   ('<i>%s %s</i>' % (e(p.L('pe')), _num(w.get('pe'), 1))) if w.get('pe') else ''))

    secs, seen = [], set()
    for label, focuses in p.ui['groups']:
        part = [r for r in rows if r.get('focus') in focuses]
        seen.update(r['t'] for r in part)
        if not part:
            continue
        part.sort(key=lambda r: -(r.get('y1') if r.get('y1') is not None else -9))
        secs.append('<section class="card"><h2>%s</h2><div class="etfgrid">%s</div></section>'
                    % (e(label), ''.join(card(r) for r in part)))
    rest = [r for r in rows if r['t'] not in seen]
    if rest:
        secs.append('<section class="card"><h2>%s</h2><div class="etfgrid">%s</div></section>'
                    % (e(p.L('other')), ''.join(card(r) for r in rest)))

    tbl = ('<section class="card"><h2>%s</h2><div class="tw"><table class="etftbl">'
           '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>'
           '<tbody>%s</tbody></table></div><p class="note">%s</p></section>'
           % (e(p.L('all50')), e(p.L('fundcol')), e(p.L('price')), e(p.L('y1')), e(p.L('y3')),
              e(p.L('pe')), e(p.L('holdings')),
              ''.join('<tr><td><a href="%s"><b>%s</b> %s</a></td><td>$%s</td><td>%s</td><td>%s</td>'
                      '<td>%s</td><td>%s</td></tr>'
                      % (p.u(r['t']), e(r['t']), ltr(r['name'], p), _num(r.get('price'), 2),
                         sret(r.get('y1'), p), sret(r.get('y3'), p),
                         _num((recs.get(r['t'], {}).get('weighted') or {}).get('pe'), 1)
                         if (recs.get(r['t'], {}).get('weighted') or {}).get('pe') else '—',
                         _num(r.get('holdings_n'), 0) if r.get('holdings_n') else '—')
                      for r in sorted(rows, key=lambda x: -(x.get('y1') if x.get('y1') is not None else -9))),
              e(p.L('note_tbl'))))

    body = ('<article class="sa-list sa-etf"><h1>%s</h1><p class="sub">%s %s</p>'
            '<p class="lead">%s</p><p>%s</p>%s%s%s<p class="dis">%s</p></article>'
            % (e(p.L('h1')), e(p.L('sub')), TODAY.strftime('%Y-%m'), e(p.L('lead')), e(p.L('intro')),
               bars(rows, p), tbl, ''.join(secs), e(p.L('dis'))))
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': p.L('home'), 'item': p.site + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': p.L('etfs'), 'item': p.site + p.u()}]}]
    return dict(url=p.u(), title=p.L('i_title')[:62], desc=p.L('i_desc')[:300], html=body, ld=ld)


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
    for row in idx.get('etfs') or []:
        rec = recs.get(row['t'])
        if rec:
            pages.append(detail(sd, rec, spy, p, sector_labels))
    return pages
