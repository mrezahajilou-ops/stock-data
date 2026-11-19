#!/usr/bin/env python3
"""Extended screener data: one row per stock with every number the sites can filter on.

Inputs  : data/stocks/*.json (engine, SEC based), a folder with the "keystats" branch, a folder with the "prices" branch
Outputs : <out>/core.json (columns of the default views, loaded first) and <out>/more.json (everything else)

Rules that keep the numbers right:
- money amounts, margins, returns and growth come from the engine files (already in US dollars for foreign filers)
- the keystats files are used only for currency-independent facts: beta, ownership, short interest, 52-week range,
  moving averages, RSI, volume, analyst counts and dates
- a ratio is left empty when its denominator is missing, zero or negative where that makes the ratio meaningless
Usage: python scrx.py <keystats_dir> <prices_dir> <out_dir>
"""
import json, os, re, sys, glob, datetime, math

ROOT = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.abspath(__file__)))

CORE = ['t', 'n', 'sector', 'industry', 'country', 'price', 'chg1d', 'mcap', 'pe', 'fwd_pe', 'ps', 'pb', 'pfcf', 'divy',
        'revg1', 'nm', 'roic', 'rec', 'tgt_up', 's_total', 's_value', 's_future', 's_past', 's_health', 's_capital',
        'rev', 'ni', 'fcf', 'eps', 'peg', 'ev_ebitda', 'fcf_yield', 'fair_up', 'r1m', 'rytd', 'r1y', 'vol', 'beta']
DICT_COLS = ('sector', 'industry', 'country', 'cur', 'rec')
MONEY = {'mcap', 'ev', 'rev', 'gp', 'opi', 'ni', 'ebitda', 'ebit', 'ocf', 'capex', 'fcf', 'rnd', 'sbc', 'da', 'intexp',
         'div_paid', 'buybacks', 'cash', 'debt', 'netcash', 'equity', 'assets', 'liab', 'wc', 'tbv', 'goodwill', 'dvol',
         'fcf_sbc', 'ppe', 'inventory', 'recv'}


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def div(a, b, pos=False):
    a, b = num(a), num(b)
    if a is None or b is None or b == 0 or (pos and b < 0):
        return None
    return a / b


def growth(new, old):
    new, old = num(new), num(old)
    if new is None or old is None or old <= 0:
        return None
    return new / old - 1


def cagr(new, old, years):
    new, old = num(new), num(old)
    if new is None or old is None or old <= 0 or new <= 0 or years <= 0:
        return None
    return (new / old) ** (1.0 / years) - 1


def day(s):
    try:
        return datetime.date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def price_at(series, target):
    """Last close on or before the target date (series is sorted [date, close])."""
    best = None
    for dt, px in series:
        if dt <= target:
            best = px
        else:
            break
    return best


def perf(P, price, asof):
    out = {}
    if not P or not price or not asof:
        return out
    ser = {}
    for dt, px in (P.get('w') or []) + (P.get('d') or []):
        d_ = day(dt)
        if d_ and num(px) and px > 0:
            ser[d_] = px
    ser = sorted(ser.items())
    if not ser:
        return out
    first = ser[0][0]
    prev = [x for x in ser if x[0] < asof]
    if prev and (asof - prev[-1][0]).days <= 5:
        out['chg1d'] = price / prev[-1][1] - 1
    spans = {'r1w': 7, 'r1m': 30, 'r3m': 91, 'r6m': 182, 'r1y': 365, 'r3y': 365 * 3, 'r5y': 365 * 5, 'r10y': 3650}
    for k, n in spans.items():
        tgt = asof - datetime.timedelta(days=n)
        if tgt < first - datetime.timedelta(days=10):
            continue
        p0 = price_at(ser, tgt) or (ser[0][1] if (first - tgt).days <= 10 else None)
        if p0:
            out[k] = price / p0 - 1
    p0 = price_at(ser, datetime.date(asof.year - 1, 12, 31))
    if p0 and first <= datetime.date(asof.year - 1, 12, 31):
        out['rytd'] = price / p0 - 1
    for k, yrs in (('cagr3', 3), ('cagr5', 5), ('cagr10', 10)):
        r = out.get('r%dy' % yrs)
        if r is not None and r > -1:
            out[k] = (1 + r) ** (1.0 / yrs) - 1
    hi = max(px for _, px in ser)
    if hi > 0:
        out['off_ath'] = min(0.0, price / hi - 1)
    # volatility of weekly returns over the last year, annualised
    wk = [px for dt, px in ser if (asof - dt).days <= 372]
    if len(wk) >= 30:
        rets = [math.log(wk[i] / wk[i - 1]) for i in range(1, len(wk))]
        m = sum(rets) / len(rets)
        var = sum((x - m) ** 2 for x in rets) / (len(rets) - 1)
        out['volat'] = math.sqrt(var) * math.sqrt(len(rets) * 365.0 / max(1, (asof - [dt for dt, _ in ser if (asof - dt).days <= 372][0]).days))
    return out


def piotroski(a, b):
    """9-point F-score from the last two fiscal years (a = latest, b = the year before)."""
    need = [a.get('net_income'), a.get('cfo'), a.get('assets'), b.get('assets'), b.get('net_income')]
    if any(num(x) is None for x in need) or not a['assets'] or not b['assets']:
        return None
    pts, known = 0, 0

    def add(cond):
        nonlocal pts, known
        if cond is None:
            return
        known += 1
        pts += 1 if cond else 0
    roa_a, roa_b = a['net_income'] / a['assets'], b['net_income'] / b['assets']
    add(a['net_income'] > 0)
    add(a['cfo'] > 0)
    add(roa_a > roa_b)
    add(a['cfo'] > a['net_income'])
    da_, db_ = div(a.get('debt'), a['assets']), div(b.get('debt'), b['assets'])
    add(None if da_ is None or db_ is None else da_ <= db_)
    ca, cb = num(a.get('current_ratio')), num(b.get('current_ratio'))
    add(None if ca is None or cb is None else ca > cb)
    sa, sb = num(a.get('shares_diluted')), num(b.get('shares_diluted'))
    add(None if not sa or not sb else sa <= sb * 1.001)
    ga, gb = num(a.get('gross_margin')), num(b.get('gross_margin'))
    add(None if ga is None or gb is None else ga > gb)
    ta, tb = div(a.get('revenue'), a['assets']), div(b.get('revenue'), b['assets'])
    add(None if ta is None or tb is None else ta > tb)
    return pts if known == 9 else None


def row(d, K, P, today):
    m, r, a_ = d.get('market') or {}, d.get('ratios') or {}, d.get('annual') or []
    a = a_[-1] if a_ else {}
    b = a_[-2] if len(a_) > 1 else {}
    ttm, bs, sm, an, sc = d.get('ttm') or {}, d.get('bs') or {}, d.get('summary') or {}, d.get('analyst') or {}, d.get('scores') or {}
    st, kp, kd = (K or {}).get('stats') or {}, (K or {}).get('price') or {}, (K or {}).get('dates') or {}
    price, mcap = num(m.get('price')), num(m.get('mcap'))
    o = {'t': d.get('ticker'), 'n': re.sub(r'\s*\\.*$', '', d.get('name') or '').strip() or d.get('ticker'), 'sector': m.get('sector'), 'industry': m.get('industry'), 'country': m.get('country'),
         'cur': d.get('reported_currency') or d.get('currency'), 'price': price, 'mcap': mcap}
    try:
        o['ipo'] = int(str(m.get('ipo'))[:4]) if m.get('ipo') else None
    except Exception:
        o['ipo'] = None
    o['years'] = sm.get('years')
    # ---------------- valuation
    for k, s in (('pe', 'pe'), ('fwd_pe', 'fwd_pe'), ('ps', 'ps'), ('fwd_ps', 'fwd_ps'), ('pb', 'pb'), ('pfcf', 'pfcf'), ('fwd_pfcf', 'fwd_pfcf'),
                 ('peg', 'peg'), ('ev', 'ev'), ('ev_ebitda', 'ev_ebitda'), ('fcf_yield', 'fcf_yield'), ('earn_yield', 'earnings_yield'),
                 ('divy', 'div_yield'), ('bby', 'buyback_yield'), ('shy', 'shareholder_yield')):
        o[k] = num(r.get(s))
    for k in ('pe', 'fwd_pe', 'pfcf', 'fwd_pfcf', 'peg', 'ev_ebitda', 'pb'):
        if o[k] is not None and o[k] <= 0:
            o[k] = None
    rev = num(ttm.get('revenue')) or num(a.get('revenue'))
    ni = num(ttm.get('net_income')) if num(ttm.get('net_income')) is not None else num(a.get('net_income'))
    ocf = num(ttm.get('cfo')) if num(ttm.get('cfo')) is not None else num(a.get('cfo'))
    capex = num(ttm.get('capex')) if num(ttm.get('capex')) is not None else num(a.get('capex'))
    fcf = num(ttm.get('fcf')) if num(ttm.get('fcf')) is not None else num(a.get('fcf'))
    ebitda = num(ttm.get('ebitda')) if num(ttm.get('ebitda')) is not None else num(a.get('ebitda'))
    opi = num(ttm.get('op_income')) if num(ttm.get('op_income')) is not None else num(a.get('op_income'))
    ev = o['ev']
    o['ev_sales'] = div(ev, rev, True) if ev and ev > 0 else None
    o['ev_ebit'] = div(ev, opi, True) if ev and ev > 0 and opi and opi > 0 else None
    o['ev_fcf'] = div(ev, fcf, True) if ev and ev > 0 and fcf and fcf > 0 else None
    o['fair_up'] = (r['fair_mcap'] / mcap - 1) if num(r.get('fair_mcap')) and mcap else None
    # ---------------- income (trailing twelve months, falling back to the last fiscal year)
    o.update(rev=rev, ni=ni, ocf=ocf, capex=capex, fcf=fcf, ebitda=ebitda, opi=opi)
    o['gp'] = num(ttm.get('gross_profit')) if num(ttm.get('gross_profit')) is not None else num(a.get('gross_profit'))
    o['eps'] = num(ttm.get('eps')) if num(ttm.get('eps')) is not None else num(a.get('eps_diluted'))
    o['rnd'], o['sbc'], o['da'], o['intexp'] = num(a.get('rnd')), num(a.get('sbc')), num(a.get('da')), num(a.get('interest_exp'))
    o['div_paid'], o['buybacks'] = num(a.get('dividends')), num(a.get('buybacks'))
    o['fcf_sbc'] = fcf - o['sbc'] if fcf is not None and o['sbc'] is not None else None
    o['dps'] = num(ttm.get('dps')) if num(ttm.get('dps')) is not None else num(a.get('div_per_share'))
    o['fcfps'], o['revps'], o['bvps'] = num(a.get('fcf_per_share')), num(a.get('revenue_per_share')), num(a.get('book_value_per_share'))
    # ---------------- margins (last fiscal year; 5-year averages from the summary)
    o['gm'], o['om'], o['nm'], o['fm'], o['ebitda_m'] = (num(a.get(k)) for k in ('gross_margin', 'op_margin', 'net_margin', 'fcf_margin', 'ebitda_margin'))
    o['ptm'] = div(a.get('pretax'), a.get('revenue'), True)
    o['rnd_pct'] = div(a.get('rnd'), a.get('revenue'), True)
    o['sbc_pct'] = num(a.get('sbc_pct'))
    o['gm5'], o['om5'], o['nm5'], o['fm5'], o['roic5'] = (num(sm.get(k)) for k in ('gross_margin_avg_5y', 'op_margin_avg_5y', 'net_margin_avg_5y', 'fcf_margin_avg_5y', 'roic_avg_5y'))
    o['nm_trend'], o['om_trend'] = num(sm.get('nm_trend')), num(sm.get('om_trend'))
    # ---------------- returns and efficiency
    o['roic'], o['roe'], o['roa'] = num(a.get('roic')), num(a.get('roe')), num(a.get('roa'))
    cap_emp = (num(a.get('assets')) or 0) - (num(a.get('current_liabilities')) or 0) if num(a.get('assets')) and num(a.get('current_liabilities')) is not None else None
    o['roce'] = div(a.get('op_income'), cap_emp, True) if cap_emp and cap_emp > 0 else None
    o['asset_turn'] = div(a.get('revenue'), a.get('assets'), True)
    o['fcf_conv'] = num(a.get('fcf_conv'))
    # ---------------- growth
    o['revg1'], o['nig1'], o['epsg1'], o['fcfg1'], o['divg1'] = (num(a.get(k)) for k in ('revenue_growth', 'net_income_growth', 'eps_diluted_growth', 'fcf_growth', 'dividends_growth'))
    o['sh_chg1'] = num(a.get('shares_diluted_growth'))
    for k, s in (('revg3', 'rev_cagr_3y'), ('revg5', 'rev_cagr_5y'), ('revg10', 'rev_cagr_10y'), ('nig3', 'ni_cagr_3y'), ('nig5', 'ni_cagr_5y'),
                 ('epsg3', 'eps_cagr_3y'), ('epsg5', 'eps_cagr_5y'), ('epsg10', 'eps_cagr_10y'), ('fcfg3', 'fcf_cagr_3y'), ('fcfg5', 'fcf_cagr_5y'),
                 ('sh_chg3', 'sh_cagr_3y'), ('sh_chg5', 'sh_cagr_5y')):
        o[k] = num(sm.get(s))
    dp = [(x.get('fy'), num(x.get('div_per_share'))) for x in a_]
    if len(dp) >= 4:
        o['divg3'] = cagr(dp[-1][1], dp[-4][1], 3)
    if len(dp) >= 6:
        o['divg5'] = cagr(dp[-1][1], dp[-6][1], 5)
    q = [x for x in (d.get('quarterly') or []) if isinstance(x, list) and len(x) >= 3]
    if len(q) >= 5 and day(q[-1][0]) and day(q[-5][0]) and 350 <= (day(q[-1][0]) - day(q[-5][0])).days <= 380:
        o['revg_q'] = growth(q[-1][1], q[-5][1])
        o['nig_q'] = growth(q[-1][2], q[-5][2])
    if len(q) >= 2 and day(q[-1][0]) and day(q[-2][0]) and 80 <= (day(q[-1][0]) - day(q[-2][0])).days <= 100:
        o['revg_qoq'] = growth(q[-1][1], q[-2][1])
    o['epsg_fy0'], o['epsg_fy1'], o['epsg_q0'] = num(an.get('ge0')), num(an.get('ge1')), num(an.get('gq0'))
    o['revg_fy1'] = growth(an.get('r1'), an.get('r0'))
    o['rule40'] = (o['revg1'] + o['fm']) if o['revg1'] is not None and o['fm'] is not None else None
    # ---------------- balance sheet (latest quarter, falling back to the last fiscal year)
    # one source per pair: the latest quarter when it is a full balance sheet, otherwise the last fiscal year
    full = num(bs.get('assets')) is not None and num(bs.get('equity')) is not None

    def B(k):
        v = num(bs.get(k)) if full else None
        return v if v is not None else (num(a.get(k)) if not full or k in ('goodwill', 'intangibles', 'ppe') else None)
    part = (not full) and num(bs.get('cash')) is not None and num(bs.get('debt')) is not None and num(bs.get('equity')) is not None
    cash, debt, eq = (num(bs.get('cash')), num(bs.get('debt')), num(bs.get('equity'))) if part else (B('cash'), B('debt'), B('equity'))
    assets, liab, ca, cl = B('assets'), B('liabilities'), B('current_assets'), B('current_liabilities')
    eq_a, debt_a = (num(a.get('equity')), num(a.get('debt'))) if part else (eq, debt)   # partners of assets / goodwill
    o.update(cash=cash, debt=debt, equity=eq, assets=assets, liab=liab, goodwill=B('goodwill'), ppe=B('ppe'))
    o['inventory'], o['recv'] = num(a.get('inventory')), num(a.get('recv'))
    o['netcash'] = cash - debt if cash is not None and debt is not None else None
    o['netcash_mc'] = div(o['netcash'], mcap, True)
    o['wc'] = ca - cl if ca is not None and cl is not None else None
    o['cur_ratio'] = div(ca, cl, True)
    inv = num(a.get('inventory')) or 0
    o['quick'] = div(ca - inv, cl, True) if ca is not None else None
    gw, it = B('goodwill') or 0, B('intangibles') or 0
    o['tbv'] = eq_a - gw - it if eq_a is not None else None
    o['ptbv'] = div(mcap, o['tbv'], True) if o['tbv'] and o['tbv'] > 0 else None
    o['de'] = div(debt, eq, True) if eq and eq > 0 else None
    o['debt_assets'] = div(debt_a, assets, True)
    o['debt_ebitda'] = div(debt, ebitda, True) if ebitda and ebitda > 0 else None
    o['nd_ebitda'] = div(-o['netcash'], ebitda, True) if o['netcash'] is not None and ebitda and ebitda > 0 else None
    o['int_cov'] = num(a.get('interest_cov'))
    o['cash_mc'] = div(cash, mcap, True)
    # Altman Z (not meaningful for banks and insurers)
    if m.get('sector') not in ('Finance', 'Financial Services', 'Financials') and assets and liab and mcap and rev and o['wc'] is not None \
            and num(a.get('retained')) is not None and opi is not None:
        o['altman'] = 1.2 * o['wc'] / assets + 1.4 * a['retained'] / assets + 3.3 * opi / assets + 0.6 * mcap / liab + 1.0 * rev / assets
    o['fscore'] = piotroski(a, b) if a and b else None
    # ---------------- dividends
    o['payout'] = num(a.get('payout'))
    if o['payout'] is not None and (o['payout'] < 0 or o['payout'] > 10):
        o['payout'] = None
    o['div_yrs'], o['profit_yrs'], o['fcf_yrs'] = sm.get('div_years'), sm.get('profit_years'), sm.get('fcf_pos_years')
    # ---------------- analysts
    o['rec'] = an.get('rec') if an.get('rec') not in (None, '', 'none') else None
    o['rm'] = num(an.get('rm'))
    o['n_an'] = num(an.get('nt')) or num(st.get('n_analysts'))
    if price and num(an.get('tgt')):
        fx = num(an.get('fx')) or 1.0
        o['tgt_up'] = num(an.get('up')) if num(an.get('up')) is not None else an['tgt'] / price - 1
        if fx == 1.0:
            o['tgt_lo_up'] = an['tlo'] / price - 1 if num(an.get('tlo')) else None
            o['tgt_hi_up'] = an['thi'] / price - 1 if num(an.get('thi')) else None
    rt = an.get('rt')
    if isinstance(rt, list) and len(rt) == 5 and sum(rt) > 0:
        o['buy_pct'] = (rt[0] + rt[1]) / sum(rt)
    r30 = an.get('rev30') or {}
    if num(r30.get('upLast30days')) is not None and num(r30.get('downLast30days')) is not None:
        o['rev30'] = r30['upLast30days'] - r30['downLast30days']
    # ---------------- price, volume, technicals (currency independent)
    asof = day(m.get('as_of'))
    if price and asof:
        o.update(perf(P, price, asof))
    hi, lo = num(st.get('hi52')), num(st.get('lo52'))
    if price and hi and lo and hi >= lo > 0:
        hi, lo = max(hi, price), min(lo, price)
        o['hi52'], o['lo52'] = hi, lo
        o['off_hi'], o['off_lo'] = price / hi - 1, price / lo - 1
        o['range_pos'] = (price - lo) / (hi - lo) if hi > lo else None
    if price and num(kp.get('ma50')):
        o['ma50'] = price / kp['ma50'] - 1
    if price and num(kp.get('ma200')):
        o['ma200'] = price / kp['ma200'] - 1
    if num(kp.get('ma50')) and num(kp.get('ma200')):
        o['ma_cross'] = kp['ma50'] / kp['ma200'] - 1
    o['rsi'] = num(kp.get('rsi'))
    o['beta'] = num(st.get('beta'))
    o['vol'] = num(st.get('avgvol'))
    o['relvol'] = div(st.get('avgvol10'), st.get('avgvol'), True)
    o['dvol'] = o['vol'] * price if o['vol'] and price else None
    # ---------------- ownership and short interest
    sh = num(st.get('shares_out')) or num(a.get('shares_out'))
    o['shares'] = sh / 1e6 if sh else None
    fl = num(st.get('float'))
    if fl and sh and fl > sh * 1.02:
        fl = None   # float reported in ordinary shares for an ADR: not comparable
    o['float'] = fl / 1e6 if fl else None
    o['float_pct'] = fl / sh if fl and sh else None
    o['insiders'], o['inst'] = num(st.get('insiders')), num(st.get('institutions'))
    if o['inst'] is not None:
        o['inst'] = min(o['inst'], 1.0)
    o['short_float'], o['short_ratio'] = num(st.get('short_float')), num(st.get('short_ratio'))
    # ---------------- dates (days from today; the page turns them into dates)
    e = kd.get('earnings') or []
    if e and num(e[0]):
        o['earn_in'] = (datetime.date.fromtimestamp(e[0]) - today).days
        if o['earn_in'] < -3:
            o['earn_in'] = None
    if num(kd.get('exdiv')):
        o['exdiv_in'] = (datetime.date.fromtimestamp(kd['exdiv']) - today).days
        if o['exdiv_in'] < -370:
            o['exdiv_in'] = None
    fy = day(a.get('fy_end'))
    o['fy_month'] = fy.month if fy else None
    # ---------------- scores
    for k in ('total', 'value', 'future', 'past', 'health', 'capital'):
        o['s_' + k] = sc.get(k)
    # ---------------- values that can only be bad data are left empty rather than shown
    for k in ('pe', 'fwd_pe', 'pfcf', 'fwd_pfcf', 'ev_ebitda', 'ev_ebit', 'ev_fcf', 'peg', 'ps', 'fwd_ps', 'pb', 'ptbv', 'ev_sales'):
        if o.get(k) is not None and o[k] > 100000:
            o[k] = None
    # P/E and EPS must agree with the profit they are built from (reverse splits leave stale per-share figures behind)
    if o.get('ni') is not None and o['ni'] <= 0:
        o['pe'] = None
    if o.get('pe') is not None and o['pe'] < 1:
        chk = div(o.get('mcap'), o.get('ni'), True)
        if chk is None or not (0.4 < o['pe'] / chk < 2.5):
            o['pe'] = None
    if o.get('eps') is not None and ((o.get('ni') is not None and o['eps'] * o['ni'] < 0) or (o.get('price') and abs(o['eps']) > 50 * o['price'])):
        o['eps'] = None
    if o.get('beta') is not None and abs(o['beta']) > 10:
        o['beta'] = None
    if o.get('insiders') is not None and o['insiders'] > 1:
        o['insiders'] = None
    if o.get('short_float') is not None and o['short_float'] > 1:
        o['short_float'] = None
    if o.get('float_pct') is not None:
        o['float_pct'] = min(1.0, o['float_pct'])
    if not o.get('mcap') or o['mcap'] <= 0:
        o['mcap'] = None
    return o


def rnd(k, v):
    if v is None or isinstance(v, str):
        return v
    if isinstance(v, bool):
        return int(v)
    if not math.isfinite(v):
        return None
    if k in MONEY:
        x = v / 1e6
        return int(round(x)) if abs(x) >= 100 else round(x, 2)
    if isinstance(v, int):
        return v
    a = abs(v)
    return int(round(v)) if a >= 10000 else round(v, 1) if a >= 100 else round(v, 2) if a >= 10 else round(v, 4)


def pack(rows, cols, as_of, built=''):
    dicts, pos, out = {c: [] for c in DICT_COLS if c in cols}, {}, []
    for o in rows:
        line = []
        for c in cols:
            v = o.get(c)
            if c in dicts:
                if v is None:
                    line.append(None)
                    continue
                key = (c, v)
                if key not in pos:
                    pos[key] = len(dicts[c])
                    dicts[c].append(v)
                line.append(pos[key])
            else:
                line.append(rnd(c, v))
        while line and line[-1] is None:
            line.pop()
        out.append(line)
    return {'v': 1, 'as_of': as_of, 'built': built, 'cols': cols, 'dict': dicts, 'money': sorted(MONEY & set(cols)), 'rows': out}


def main():
    kdir, pdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    today = datetime.date.today()
    rows, as_of = [], ''
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'stocks', '*.json'))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        t = d.get('ticker')
        if not t or not d.get('annual'):
            continue

        def side(folder):
            p = os.path.join(folder, t + '.json')
            try:
                return json.load(open(p)) if os.path.exists(p) else None
            except Exception:
                return None
        o = row(d, side(kdir), side(pdir), today)
        as_of = max(as_of, (d.get('market') or {}).get('as_of') or '')
        rows.append(o)
    rows.sort(key=lambda o: -(o.get('mcap') or 0))
    allc = []
    for o in rows:
        for k in o:
            if k not in allc:
                allc.append(k)
    core = [c for c in CORE if c in allc]
    more = ['t'] + [c for c in allc if c not in core]
    os.makedirs(out, exist_ok=True)
    for name, cols in (('core', core), ('more', more)):
        p = os.path.join(out, name + '.json')
        json.dump(pack(rows, cols, as_of, today.isoformat()), open(p, 'w'), separators=(',', ':'), ensure_ascii=False)
        print(name, len(cols), 'columns', os.path.getsize(p), 'bytes')
    fill = {c: sum(1 for o in rows if o.get(c) is not None) for c in allc}
    json.dump({'built': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'as_of': as_of, 'rows': len(rows), 'fill': fill},
              open(os.path.join(out, 'meta.json'), 'w'), separators=(',', ':'))
    print(len(rows), 'stocks,', len(allc), 'columns')


if __name__ == '__main__':
    main()
