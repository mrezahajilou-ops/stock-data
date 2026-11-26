"""Data-written company story for the stock pages of all editions (en, es, tr, ar).

Why this exists: on 22 Nov 2026 a typical stock page was only 13-21% unique text; the rest was the same
template sentences on every page with other numbers in them, and Google indexed a few hundred of
several thousand pages per site. This module writes 250-450 words per company that only fit that company:
its own year-by-year record (the years revenue fell, the loss years, the margin peak, dilution), where it
stands against the other companies in its industry (rank, the names just above and below it, margin
and growth against the industry median), its latest quarters, and what analysts have been doing. Every fact
has several phrasings and the choice is fixed per company, so two similar companies still read differently,
and the paragraphs are ordered by what is most notable for that company.

Usage (an edition's stock page builder):
    import story
    ctx = story.context(docs)                        # once per build: industry peer groups
    html = story.html(d, ctx, story.pack('en'), name, ind_name, stock_url, peer_name)
Every number comes from the stock's own data file; a fact whose inputs are missing or implausible is left out.
"""
import hashlib, html as H, os, importlib.util, re, statistics
from collections import defaultdict

_PACKS = {}


def pack(lang):
    if lang not in _PACKS:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content', 'story', '%s.py' % lang)
        sp = importlib.util.spec_from_file_location('story_' + lang, p)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _PACKS[lang] = m
    return _PACKS[lang]


def _mc(d):
    return (d.get('market') or {}).get('mcap') or 0


def _med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if len(xs) >= 3 else None


def _qs(d, idx):
    q = [x for x in (d.get('quarterly') or []) if isinstance(x, list) and len(x) > idx and isinstance(x[idx], (int, float))]
    return q


def ttm_margin(d):
    """Net margin over the trailing twelve months; the latest fiscal year only when there is no TTM."""
    t = d.get('ttm') or {}
    rv, ni = t.get('revenue'), t.get('net_income')
    if isinstance(rv, (int, float)) and rv > 0 and isinstance(ni, (int, float)):
        return ni / rv
    return (d.get('latest') or {}).get('net_margin')


def ttm_op_margin(d):
    t = d.get('ttm') or {}
    rv, op = t.get('revenue'), t.get('op_income')
    if isinstance(rv, (int, float)) and rv > 0 and isinstance(op, (int, float)):
        return op / rv
    return None


def ttm_growth(d):
    """(revenue growth, True) over the trailing twelve months against the twelve before, from the quarterly
    revenue; (last fiscal year's growth, False) when fewer than eight quarters are available."""
    q = _qs(d, 1)
    if len(q) >= 8:
        try:
            import datetime as _dt
            span = (_dt.date.fromisoformat(q[-1][0]) - _dt.date.fromisoformat(q[-8][0])).days
        except Exception:
            span = 0
        a, b = sum(x[1] for x in q[-4:]), sum(x[1] for x in q[-8:-4])
        if 600 <= span <= 800 and b > 0:
            return a / b - 1, True
    return (d.get('summary') or {}).get('rev_cagr_1y'), False


def context(docs):
    """Industry peer groups (largest first) and medians, computed once per build."""
    by = defaultdict(list)
    for d in docs:
        i = (d.get('market') or {}).get('industry')
        if i and _mc(d) > 0:
            by[i].append(d)
    ctx = {}
    for i, ds in by.items():
        ds.sort(key=lambda x: -_mc(x))
        nm = [ttm_margin(x) for x in ds]
        nm = [v for v in nm if v is not None and -3 < v < 1]
        gr = [ttm_growth(x)[0] for x in ds]
        gr = [v for v in gr if v is not None and -0.9 < v < 5]
        pe = [((x.get('ratios') or {}).get('pe')) for x in ds]
        pe = [v for v in pe if v and 0 < v < 300]
        ctx[i] = dict(docs=ds, rank={x['ticker']: k for k, x in enumerate(ds)}, total=sum(_mc(x) for x in ds),
                      med_nm=_med(nm), med_g=_med(gr), med_pe=_med(pe), n_prof=sum(1 for v in nm if v > 0))
    return ctx


def _pick(t, key, n):
    return int(hashlib.md5(('%s|%s' % (t, key)).encode()).hexdigest(), 16) % n


class _W:
    """Collects sentences for one company; picks the phrasing per company and fact."""

    def __init__(self, t, P):
        self.t, self.P, self.out = t, P, []

    def say(self, key, **kw):
        vs = self.P.T.get(key)
        if not vs:
            return
        s = vs[_pick(self.t, key, len(vs))]
        wrap = getattr(self.P.F, 'count', None)          # e.g. Arabic isolates bare counts and years
        if wrap:
            kw = {k: (wrap(v) if isinstance(v, int) else v) for k, v in kw.items()}
        try:
            s = s.format(**kw)
            post = getattr(self.P, 'post', None)            # language grammar pass (Arabic counted nouns)
            if post:
                s = post(s)
            self.out.append(s[:1].upper() + s[1:])
        except (KeyError, IndexError, ValueError):
            pass


def _years(an):
    """Annual rows with revenue, oldest first, one per fiscal year."""
    seen, out = set(), []
    for a in an or []:
        fy = a.get('fy')
        if fy and fy not in seen and a.get('revenue') and a['revenue'] > 0:
            seen.add(fy)
            out.append(a)
    return sorted(out, key=lambda a: a['fy'])[-11:]


def paragraphs(d, ctx, P, name, ind_name, stock_url, peer_name, wrap=lambda x: x):
    """List of (salience, [sentences]) for one company. Empty list when the record is too thin."""
    t = d['ticker']
    m, r, s = d.get('market') or {}, d.get('ratios') or {}, d.get('summary') or {}
    lat, tt, an = d.get('latest') or {}, d.get('ttm') or {}, d.get('analyst') or {}
    F = P.F
    ys = _years(d.get('annual'))
    if len(ys) < 3:
        return []
    mc = _mc(d)
    paras = []

    # --- 1. size and place in its industry
    w = _W(t, P)
    ind = m.get('industry')
    g = ctx.get(ind) if ind else None
    if g and len(g['docs']) >= 3 and t in g['rank'] and mc > 0:
        k, ds, n = g['rank'][t], g['docs'], len(g['docs'])
        iname = ind_name(ind)
        link = lambda x: '<a href="%s">%s</a>' % (stock_url(x['ticker']), wrap(H.escape(peer_name(x))))
        if k == 0:
            nxt = ds[1]
            w.say('size_top', name=name, ind=iname, n=n, mcap=F.money(mc), other=link(nxt), x=F.times(mc / max(_mc(nxt), 1)))
        else:
            w.say('size_rank', name=name, ind=iname, n=n, rank=k + 1, mcap=F.money(mc))
            above = ds[k - 1]
            if k + 1 < n:
                w.say('size_between', bigger=link(above), smaller=link(ds[k + 1]))
            else:
                w.say('size_last', bigger=link(above))
        share = mc / g['total'] if g['total'] else 0
        if share >= 0.15:
            w.say('size_share', share=F.pct(share))
        paras.append((9, w.out))
    elif mc > 0:
        w.say('size_alone', name=name, mcap=F.money(mc))
        paras.append((9, w.out))

    # --- 2. the long record: revenue path, the down years, the best year, record or below peak
    w = _W(t, P)
    revs = [(a['fy'], a['revenue']) for a in ys]
    fy0, r0 = revs[0]
    fy1, r1 = revs[-1]
    nyr = fy1 - fy0
    sal = 5
    if nyr >= 3 and r0 > 0:
        cagr = (r1 / r0) ** (1 / nyr) - 1
        if -0.6 < cagr < 3:
            w.say('hist_cagr_up' if cagr >= 0.005 else ('hist_cagr_flat' if cagr > -0.005 else 'hist_cagr_down'),
                  name=name, fy0=fy0, fy1=fy1, r0=F.money(r0), r1=F.money(r1), g=F.pct(abs(cagr)), n=nyr)
            sal += 1 if abs(cagr) > 0.15 else 0
    chg = [(revs[i][0], revs[i][1] / revs[i - 1][1] - 1) for i in range(1, len(revs)) if revs[i][0] - revs[i - 1][0] == 1]
    chg = [(fy, c) for fy, c in chg if -0.95 < c < 10]
    downs = [(fy, c) for fy, c in chg if c < -0.01]
    if len(chg) >= 3:
        if not downs:
            w.say('hist_no_down', n=len(chg))
            sal += 1
        elif len(downs) == 1:
            fy, c = downs[0]
            w.say('hist_down_one', fy=fy, g=F.pct(-c))
            sal += 2 if c < -0.15 else 1
        else:
            worst = min(downs, key=lambda x: x[1])
            w.say('hist_down_many', n=len(downs), years=F.years([fy for fy, _ in downs]), worst=worst[0], g=F.pct(-worst[1]))
            sal += 1
        best = max(chg, key=lambda x: x[1])
        if best[1] > 0.08 and (not downs or best[0] != downs[0][0]):
            w.say('hist_best', fy=best[0], g=F.pct(best[1]))
    peak_fy, peak = max(revs, key=lambda x: x[1])
    if peak_fy == fy1 and len(revs) >= 4:
        w.say('hist_record', fy=fy1)
    elif peak > 0 and r1 < peak * 0.9:
        w.say('hist_below_peak', fy=peak_fy, peak=F.money(peak), g=F.pct(1 - r1 / peak))
        sal += 1
    if w.out:
        paras.append((sal, w.out))

    # --- 3. profits: loss years, the turn, margin peak, cash flow
    w = _W(t, P)
    sal = 5
    ni = [(a['fy'], a.get('net_income'), a.get('net_income') / a['revenue'] if a.get('net_income') is not None else None) for a in ys]
    ni = [x for x in ni if x[1] is not None]
    if len(ni) >= 3:
        loss = [fy for fy, v, _ in ni if v < 0]
        span = len(ni)
        if not loss:
            w.say('prof_all', n=span, name=name)
        elif len(loss) == span:
            w.say('prof_never', n=span, name=name)
            sal += 2
        else:
            # first profitable year after a loss that has stayed profitable since
            turn = None
            for i in range(len(ni) - 1, 0, -1):
                if ni[i][1] >= 0 and ni[i - 1][1] < 0:
                    turn = ni[i][0]
                    break
            if turn and all(v >= 0 for fy, v, _ in ni if fy >= turn):
                w.say('prof_turn', fy=turn, n=len(loss), years=F.years(loss))
                sal += 2
            elif ni[-1][1] < 0 and ni[-2][1] >= 0:
                w.say('prof_slip', fy=ni[-1][0], loss=F.money(-ni[-1][1]))
                sal += 3
            else:
                w.say('prof_mixed', n=len(loss), span=span, years=F.years(loss))
                sal += 1
        ms = [(fy, mg) for fy, v, mg in ni if mg is not None and -3 < mg < 1]
        if len(ms) >= 4:
            pk = max(ms, key=lambda x: x[1])
            now = ms[-1][1]
            tn = ttm_margin(d)      # "now" is the trailing twelve months when there is one, not the last fiscal year
            if tn is not None and -3 < tn < 1:
                now = tn
            if pk[1] > 0.02 and pk[0] != ms[-1][0] and now < pk[1] - 0.02:
                w.say('prof_margin_off', fy=pk[0], peak=F.mpct(pk[1]), now=F.mpct(now))
                sal += 1
            elif pk[0] == ms[-1][0] and pk[1] > 0.02:
                w.say('prof_margin_best', m=F.mpct(pk[1]), n=len(ms))
                sal += 1
    eps = [(a['fy'], a.get('eps_diluted')) for a in ys if a.get('eps_diluted') is not None]
    if len(eps) >= 4 and eps[0][1] > 0.05 and eps[-1][1] > 0.05 and eps[-1][0] - eps[0][0] >= 3:
        n_ = eps[-1][0] - eps[0][0]
        ec = (eps[-1][1] / eps[0][1]) ** (1 / n_) - 1
        if -0.5 < ec < 2:
            rc = (r1 / r0) ** (1 / nyr) - 1 if nyr >= 3 and r0 > 0 else None
            key = 'eps_up' if ec >= 0.01 else 'eps_down'
            if rc is not None and ec > rc + 0.03 and ec > 0:
                key = 'eps_faster'
            w.say(key, e0=F.price(eps[0][1]), e1=F.price(eps[-1][1]), fy0=eps[0][0], fy1=eps[-1][0], g=F.pct(abs(ec)))
    o1, o5 = s.get('op_margin_avg_1y'), s.get('op_margin_avg_5y')
    ot = ttm_op_margin(d)
    o_ttm = ot is not None and -1 < ot < 1 and bool(P.T.get('opm_up_ttm'))
    if o_ttm:
        o1 = ot
    if o1 is not None and o5 is not None and -1 < o1 < 1 and -1 < o5 < 1 and abs(o1 - o5) >= 0.03 and (o1 > 0 or o5 > 0):
        w.say(('opm_up' if o1 > o5 else 'opm_down') + ('_ttm' if o_ttm else ''), now=F.mpct(o1), avg=F.mpct(o5))
    fcf = [a.get('fcf') for a in ys if a.get('fcf') is not None]
    if len(fcf) >= 4:
        pos = sum(1 for v in fcf if v > 0)
        if pos == len(fcf):
            w.say('fcf_all', n=len(fcf))
        elif pos == 0:
            w.say('fcf_none', n=len(fcf))
        elif pos == 1:
            w.say('fcf_one', n=len(fcf))
        elif pos >= len(fcf) - 2:
            w.say('fcf_most', pos=pos, n=len(fcf))
        else:
            w.say('fcf_some', pos=pos, n=len(fcf))
    if w.out:
        paras.append((sal, w.out))

    # --- 4. the latest quarters
    w = _W(t, P)
    q = [x for x in (d.get('quarterly') or []) if isinstance(x, list) and len(x) >= 2 and x[1]]
    q.sort(key=lambda x: x[0])
    if len(q) >= 5:
        last, ago = q[-1], q[-5]
        if ago[1] and ago[1] > 0:
            yy = last[1] / ago[1] - 1
            if -0.9 < yy < 5:
                w.say('q_up' if yy >= 0.01 else ('q_flat' if yy > -0.01 else 'q_down'), q=P.qdate(last[0]), rev=F.money(last[1]), g=F.pct(abs(yy)))
                ups = 0
                for i in range(len(q) - 1, 4, -1):
                    if q[i - 4][1] and q[i][1] > q[i - 4][1]:
                        ups += 1
                    else:
                        break
                if ups >= 4:
                    w.say('q_streak', n=ups)
        if len(last) >= 3 and last[2] is not None:
            w.say('q_profit' if last[2] >= 0 else 'q_loss', ni=F.money(abs(last[2])))
    if w.out:
        paras.append((6, w.out))

    # --- 5. against its industry: margin, growth, P/E
    w = _W(t, P)
    sal = 4
    if g and len(g['docs']) >= 5:
        iname = ind_name(ind)
        nm, med = ttm_margin(d), g['med_nm']
        if nm is not None and med is not None and -3 < nm < 1 and nm < 0:
            w.say('peer_loss_hi' if nm > med else 'peer_loss_lo', m=F.mpct(nm), med=F.mpct(med), ind=iname)
        elif nm is not None and med is not None and -3 < nm < 1:
            if nm > med + 0.03:
                w.say('peer_margin_hi', m=F.mpct(nm), med=F.mpct(med), ind=iname)
                sal += 1
            elif nm < med - 0.03:
                w.say('peer_margin_lo', m=F.mpct(nm), med=F.mpct(med), ind=iname)
                sal += 1
            else:
                w.say('peer_margin_eq', m=F.mpct(nm), med=F.mpct(med), ind=iname)
        gg, is_t = ttm_growth(d)
        mg = g['med_g']
        if gg is not None and mg is not None and -0.9 < gg < 5:
            k = 'peer_growth_hi' if gg > mg + 0.03 else ('peer_growth_lo' if gg < mg - 0.03 else 'peer_growth_eq')
            w.say(k + ('_ttm' if is_t and P.T.get(k + '_ttm') else ''), g=F.spct(gg), med=F.spct(mg))
        pe, mpe = r.get('pe'), g['med_pe']
        if pe and 0 < pe < 300 and mpe:
            ratio = pe / mpe
            if ratio > 1.3:
                w.say('peer_pe_hi', pe=F.num(pe), med=F.num(mpe), x=F.times(ratio))
                sal += 1
            elif ratio < 0.75:
                w.say('peer_pe_lo', pe=F.num(pe), med=F.num(mpe))
                sal += 1
            else:
                w.say('peer_pe_eq', pe=F.num(pe), med=F.num(mpe))
        elif (not pe or pe <= 0) and g['n_prof']:
            w.say('peer_pe_none', n=g['n_prof'], tot=len(g['docs']))
    roic = lat.get('roic')
    if roic is not None and -2 < roic < 2:
        if roic >= 0.2:
            w.say('roic_hi', roic=F.pct(roic))
        elif 0 <= roic < 0.06 and (lat.get('net_income') or 0) > 0:
            w.say('roic_lo', roic=F.pct(roic))
    if w.out:
        paras.append((sal, w.out))

    # --- 6. balance sheet and shareholders
    w = _W(t, P)
    sal = 4
    cash, debt = lat.get('cash'), lat.get('debt')
    bsq = d.get('bs') or {}
    if bsq.get('cash') is not None and bsq.get('debt') is not None and (bsq.get('end') or '') > (lat.get('fy_end') or ''):
        cash, debt = bsq['cash'], bsq['debt']   # the latest quarterly balance sheet: the same one enterprise value uses
    if cash is not None and debt is not None and mc > 0:
        net = cash - debt
        if net > 0 and 0.05 <= net / mc <= 10:   # beyond 10x the market cap is a broken market cap, not a fact
            w.say('bs_cash', net=F.money(net), p=F.pct(net / mc))
        elif net < 0:
            eb = tt.get('ebitda')
            if eb and eb > 0 and -net / eb < 0.1:
                pass                      # debt and cash roughly cancel out: "0.0 times EBITDA" tells the reader nothing
            elif eb and eb > 0 and -net / eb < 30:
                w.say('bs_debt_x', net=F.money(-net), x=F.num(-net / eb))
                sal += 1 if -net / eb > 4 else 0
            elif 0.2 < -net / mc <= 10:   # above 10x the market cap the percentage ("13811%") stops meaning anything
                w.say('bs_debt_p', net=F.money(-net), p=F.pct(-net / mc))
                sal += 1
    burn = tt.get('fcf')
    if burn is not None and burn < 0 and cash and cash > 0:
        yrs = cash / -burn
        if yrs < 10:
            w.say('bs_runway_short' if yrs < 2 else 'bs_runway', burn=F.money(-burn), x=F.num(yrs))
            sal += 3 if yrs < 2 else 1
    sh3 = s.get('sh_cagr_3y')
    if sh3 is not None:
        if 0.03 <= sh3 <= 1.0:   # >100%/yr is almost always reverse splits or a share-class change, not dilution
            w.say('sh_dilute', p=F.pct(sh3))
            sal += 2 if sh3 > 0.1 else 1
        elif sh3 <= -0.015:
            w.say('sh_buyback', p=F.pct(-sh3))
            sal += 1
    dy, dvy = r.get('div_yield'), s.get('div_years')
    if dy and dy > 0.003 and dvy:
        w.say('div_yes', y=F.pct(dy, 1), n=dvy)
    sbc, f = tt.get('sbc'), tt.get('fcf')
    if sbc and f and f > 0 and 0.4 < sbc / f < 5 and f > 0.03 * (tt.get('revenue') or 0):
        w.say('sbc_heavy', p=F.pct(sbc / f))
        sal += 1
    rev_t = tt.get('revenue') or 0
    if rev_t > 0:
        rnd = tt.get('rnd')
        if rnd and 0.1 <= rnd / rev_t < 3:
            w.say('rnd', p=F.pct(rnd / rev_t), v=F.money(rnd))
        cx = tt.get('capex')
        if cx and 0.12 <= abs(cx) / rev_t < 3:
            w.say('capex', p=F.pct(abs(cx) / rev_t), v=F.money(abs(cx)))
        ie, oi = tt.get('interest_exp'), tt.get('op_income')
        if ie and ie > 0 and oi is not None and ie / rev_t > 0.005:
            cov = oi / ie
            if cov < 2:
                w.say('int_tight', x=F.num(max(cov, 0)) if cov > 0 else F.num(0), ie=F.money(ie))
                sal += 1
            elif cov > 25:
                w.say('int_easy', x=F.num(min(cov, 99)))
    fe = (lat.get('fy_end') or '')[5:7]
    if fe and fe != '12' and fe.isdigit():
        w.say('fy_end', m=P.month(int(fe)))
    if w.out:
        paras.append((sal, w.out))

    # --- 7. analysts
    w = _W(t, P)
    sal = 3
    rv = an.get('rev30') or {}
    up, dn = rv.get('upLast30days') or 0, rv.get('downLast30days') or 0
    if an.get('n') and (an.get('cur') in (None, 'USD')):
        if up + dn >= 2:
            w.say('an_up' if up > dn * 2 else ('an_down' if dn > up * 2 else 'an_mixed'), up=up, dn=dn)
            sal += 1 if dn > up * 2 else 0
        lo, hi, px = an.get('tlo'), an.get('thi'), m.get('price')
        if lo and hi and px and an.get('nt', 0) >= 3 and hi > lo:
            w.say('an_range', lo=F.price(lo), hi=F.price(hi), n=an['nt'])
        if an.get('q0') and an.get('qe0') is not None:
            if an.get('qr0'):
                w.say('an_next', q=P.qdate(an['q0']), eps=F.price(an['qe0']), rev=F.money(an['qr0']))
            else:
                w.say('an_next_eps', q=P.qdate(an['q0']), eps=F.price(an['qe0']))
    if w.out:
        paras.append((sal, w.out))

    order = [paras[0]] + sorted(paras[1:], key=lambda x: (-x[0], _pick(t, 'ord%d' % x[0], 7)))
    return [p for _, p in order if p]


def html(d, ctx, P, name, ind_name, stock_url, peer_name, cls='card story', h2=''):
    wrap = getattr(P, 'wrap_name', None) or (lambda x: x)   # Arabic isolates Latin names inside right-to-left text
    name = wrap(H.escape(name))
    ps = paragraphs(d, ctx, P, name, lambda i: H.escape(ind_name(i)), stock_url, peer_name, wrap)
    if not ps or sum(len(p) for p in ps) < 5:
        return ''
    h = P.T['head'][_pick(d['ticker'], 'head', len(P.T['head']))].format(name=name)
    body = ''.join('<p>%s</p>' % ' '.join(p) for p in ps)
    body = re.sub(r'\.(</a>)\.', r'.\1', body).replace('..', '.')   # names that end in "Corp." or "Inc."
    return '<section class="%s"><h2%s>%s</h2>%s</section>' % (cls, h2, h, body)
