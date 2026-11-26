#!/usr/bin/env python3
"""Housing market country pages for the language sites (aktienadler, boursefaucon, borsafalco, bolsacondor, bolsagaviao,
sahamelang, jusikmae, kabutaka, saqr, borsakartal). One renderer, text per language in housing_i18n.py, data from the
branch "housing" (housing_<cc>.json, housing_intl.py). Same look and tools as stockanaliz.com/housing/.

A site calls:
    import housing_page
    for p in housing_page.build_all(SD, lang, countries, chrome_html, flip=None, base='/immobilienmarkt/', slugs={...}):
        write(p['url'], shell(p['url'], p['title'], p['desc'], p['html'], 'housing', p['seo'], p['ld']))
"""
import datetime as dt, html, json, os, re, subprocess
import housing_i18n as I18N

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, 'web_src', 'housing.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'web_src', 'housing.js'), encoding='utf-8').read()

FLAG = {
    'us': '<svg viewBox="0 0 19 10" width="19" height="10"><rect width="19" height="10" fill="#B22234"/><g fill="#fff"><rect y="1.5" width="19" height=".8"/><rect y="3.1" width="19" height=".8"/><rect y="4.6" width="19" height=".8"/><rect y="6.2" width="19" height=".8"/><rect y="7.7" width="19" height=".8"/></g><rect width="8" height="5.4" fill="#3C3B6E"/></svg>',
    'de': '<svg viewBox="0 0 5 3" width="17" height="10"><rect width="5" height="1" fill="#000"/><rect y="1" width="5" height="1" fill="#D00"/><rect y="2" width="5" height="1" fill="#FFCE00"/></svg>',
    'at': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="2" fill="#ED2939"/><rect y=".667" width="3" height=".667" fill="#fff"/></svg>',
    'ch': '<svg viewBox="0 0 32 32" width="10" height="10"><rect width="32" height="32" fill="#D52B1E"/><path d="M13 6h6v7h7v6h-7v7h-6v-7H6v-6h7z" fill="#fff"/></svg>',
    'fr': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="1" height="2" fill="#002395"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#ED2939"/></svg>',
    'it': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="1" height="2" fill="#009246"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#CE2B37"/></svg>',
    'es': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="2" fill="#AA151B"/><rect y=".5" width="3" height="1" fill="#F1BF00"/></svg>',
    'pt': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="2" fill="#FF0000"/><rect width="1.2" height="2" fill="#006600"/><circle cx="1.2" cy="1" r=".35" fill="#FFCC00"/></svg>',
    'br': '<svg viewBox="0 0 20 14" width="15" height="10"><rect width="20" height="14" fill="#009C3B"/><path d="M10 2l8 5-8 5-8-5z" fill="#FFDF00"/><circle cx="10" cy="7" r="3" fill="#002776"/></svg>',
    'id': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="1" fill="#CE1126"/><rect y="1" width="3" height="1" fill="#fff"/></svg>',
    'kr': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="2" fill="#fff"/><circle cx="1.5" cy="1" r=".5" fill="#CD2E3A"/><path d="M1 1a.5.5 0 0 0 1 0a.25.25 0 0 0-.5 0a.25.25 0 0 1-.5 0" fill="#0047A0"/></svg>',
    'jp': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="2" fill="#fff"/><circle cx="1.5" cy="1" r=".6" fill="#BC002D"/></svg>',
    'ae': '<svg viewBox="0 0 12 6" width="20" height="10"><rect width="12" height="6" fill="#00732F"/><rect y="2" width="12" height="2" fill="#fff"/><rect y="4" width="12" height="2" fill="#000"/><rect width="3" height="6" fill="#FF0000"/></svg>',
    'sa': '<svg viewBox="0 0 3 2" width="15" height="10"><rect width="3" height="2" fill="#006C35"/><rect x=".7" y="1.35" width="1.6" height=".12" fill="#fff"/></svg>',
    'tr': '<svg viewBox="0 0 30 20" width="15" height="10"><rect width="30" height="20" fill="#E30A17"/><circle cx="11" cy="10" r="5" fill="#fff"/><circle cx="12.3" cy="10" r="4" fill="#E30A17"/><path d="M16.5 10l3.8-1.2-2.3 3.2V8l2.3 3.2z" fill="#fff"/></svg>',
}
INDEX_NAME = {'us': 'S&P 500', 'ca': 'S&P/TSX', 'gb': 'FTSE 100', 'ie': 'ISEQ', 'au': 'ASX 200', 'de': 'DAX', 'at': 'ATX', 'ch': 'SMI', 'fr': 'CAC 40', 'it': 'FTSE MIB', 'es': 'IBEX 35', 'pt': 'PSI', 'br': 'Ibovespa',
              'id': 'IDX Composite', 'kr': 'KOSPI', 'jp': 'Nikkei 225', 'ae': 'DFM', 'sa': 'TASI', 'tr': 'BIST 100'}
TERM = {'us': 30, 'ca': 25, 'gb': 25, 'ie': 30, 'au': 30, 'de': 25, 'at': 25, 'ch': 25, 'fr': 20, 'it': 25, 'es': 25, 'pt': 30, 'br': 30, 'id': 15, 'kr': 30, 'jp': 35, 'ae': 25, 'sa': 25, 'tr': 10}
SEP = ', '
COLS = ['#C9A961', '#6FA8DC', '#8A8F99', '#4FA37A', '#C8534F']


# ------------------------------------------------------------------ helpers
def back(series, months):
    if not series:
        return None
    y, m = int(series[-1][0][:4]), int(series[-1][0][5:7])
    m -= months
    while m <= 0:
        m += 12
        y -= 1
    idx = {k[:7]: v for k, v in series}
    for i in range(3):
        mm, yy = m - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        if idx.get('%04d-%02d' % (yy, mm)) is not None:
            return idx['%04d-%02d' % (yy, mm)]
    return None


def chg(a, b):
    return (a / b - 1) * 100 if a and b else None


def yoy(s):
    d = dict(s)
    out = []
    for k, v in s:
        p = d.get('%04d-%s' % (int(k[:4]) - 1, k[5:7]))
        if p:
            out.append([k, round((v / p - 1) * 100, 2)])
    return out


def dec_values(series, years):
    d = dict(series)
    out = {}
    for y in years:
        for m in ('12', '11', '10', '09'):
            if d.get('%d-%s' % (y, m)) is not None:
                out[y] = d['%d-%s' % (y, m)]
                break
    return out


def esc(s):
    return html.escape(str(s), quote=True)


def r(v, n=1):
    return None if v is None else round(v, n)


class Fmt:
    """Numbers, money and dates in the site's language."""
    def __init__(self, L, sym, cur):
        self.L, self.sym, self.cur = L, sym, cur
        self.dec, self.grp = L['_dec'], L['_grp']
        self.rtl = L.get('_dir') == 'rtl'

    def iso(self, s):
        """Right-to-left pages: keep a number with its sign and % together (Unicode isolate, invisible)."""
        return '\u2066' + s + '\u2069' if self.rtl and s != '—' else s

    def n(self, v, d=0, wrap=True):
        if v is None:
            return '—'
        s = format(abs(v), ',.%df' % d).replace(',', '\x01').replace('.', '\x02').replace('\x01', self.grp).replace('\x02', self.dec)
        s = ('−' if v < 0 else '') + s
        return self.iso(s) if wrap else s

    def money(self, v, d=0):
        if v is None:
            return '—'
        s = self.n(abs(v), d, False)
        s = self.L['_cur'].format(n=s, s=self.sym)
        return self.iso(('−' if v < 0 else '') + s)

    def pc(self, v, d=1, sign=True):
        if v is None:
            return '—'
        if round(v, d) == 0:
            v = 0.0
        s = ('%' + self.n(abs(v), d, False)) if self.L.get('_pctpre') else self.n(abs(v), d, False) + self.L['_pct']
        return self.iso((('+' if v > 0 else '−' if v < 0 else '') if sign else ('−' if v < 0 else '')) + s)

    def rate(self, v):
        return '—' if v is None else self.iso(('%' + self.n(v, 2, False)) if self.L.get('_pctpre') else self.n(v, 2, False) + self.L['_pct'])

    def month(self, k):
        return '%s %s' % (self.L['_mon'][int(k[5:7]) - 1], k[:4])

    def monthl(self, k):
        return '%s %s' % (self.L['_monl'][int(k[5:7]) - 1], k[:4])

    def q(self, k):
        return self.L['_q'].format(q=(int(k[5:7]) - 1) // 3 + 1, y=k[:4])


def TODAY_YM():
    return dt.date.today().strftime('%Y-%m')


def mid(tpl, n):
    """A name placed after an article ('Le {n}', 'El {n}') starts in lower case, unless it is an abbreviation."""
    if n and not tpl.startswith(('{n}', 'Der ', 'Die ', 'Das ')) and len(n) > 1 and n[0].isupper() and not n[1].isupper():
        return n[0].lower() + n[1:]
    return n


def cls(v):
    return '' if v is None or abs(v) < 0.05 else ('up' if v > 0 else 'dn')


def load(sd, cc):
    lp = os.path.join(os.environ.get('HOUSING_DIR', ''), 'housing_%s.json' % cc) if os.environ.get('HOUSING_DIR') else ''
    if lp and os.path.exists(lp):
        return json.load(open(lp))
    for ref in ('origin/housing', 'housing'):
        try:
            return json.loads(subprocess.run(['git', '-C', sd, 'show', '%s:housing_%s.json' % (ref, cc)], capture_output=True, timeout=60, check=True).stdout)
        except Exception:
            continue
    return None


def theme_css(sd):
    src = open(os.path.join(sd, 'gen_web.py'), encoding='utf-8').read()
    theme = open(os.path.join(sd, 'web_src', 'theme.css'), encoding='utf-8').read()
    m = re.search(r'CSS = r"""(.*?)""" \+ "\\n" \+ THEME', src, flags=re.S)
    css = ((m.group(1) if m else '') + '\n' + theme).replace('#ID', '#hs')
    css = re.sub(r"@import url\('https://fonts\.googleapis\.com[^']*'\);\n?", '', css)
    return css


# ------------------------------------------------------------------ data
def prepare(cc, X, L):
    oe = X.get('oecd') or {}
    D = {'sym': X['sym'], 'cur': X['cur'], 'as_of': X['as_of'][:10]}
    price = (X.get('price') or {}).get('s') or []
    price_n = L['n_' + (X.get('price') or {}).get('n', '')] if (X.get('price') or {}).get('n') and ('n_' + X['price']['n']) in L else (X.get('price') or {}).get('n')
    idx = (X.get('idx') or {}).get('s') or []
    idx_n = L.get('n_' + ((X.get('idx') or {}).get('n') or ''), (X.get('idx') or {}).get('n'))
    if not idx:
        idx, idx_n = (oe.get('nom') or [], L['n_oecd_idx']) if oe.get('nom') else (price, price_n)
    D.update(idx=idx, idx_n=idx_n, idxy=yoy(idx), price=price, price_n=price_n)
    D['real'] = oe.get('real') or X.get('bis_real') or []
    D['realy'] = yoy(D['real'])
    D['pti'], D['ptr'] = oe.get('pti') or [], oe.get('ptr') or []
    D['rentx'] = oe.get('rent') or []
    D['renty'] = yoy(D['rentx'])
    rent = (X.get('rent') or {}).get('s') or []
    D['rent'] = rent
    D['rent_n'] = L.get('n_' + ((X.get('rent') or {}).get('n') or ''), (X.get('rent') or {}).get('n'))
    D['rents_y'] = yoy(rent) if len(rent) > 12 else []
    D['tys'] = [{'n': L.get('t_' + n, n), 'c': COLS[i % 5], 'd': s} for i, (n, s) in enumerate((X.get('types') or {}).items()) if s]
    D['tysm'] = bool(D['tys']) and (min(t['d'][-1][1] for t in D['tys']) > 2000 or all('m²' in n for n in (X.get('types') or {})))
    D['rates'] = [{'n': L.get('r_' + n, n), 'c': COLS[i % 5], 'd': [p for p in s if p[0] >= '2003'] if max(v for _, v in s) > 100 else s, 'pol': 'mortgage' not in n.lower()} for i, (n, s) in enumerate((X.get('rates') or {}).items()) if s]
    nom, real = dict(oe.get('nom') or []), dict(oe.get('real') or [])
    cpi = [[k, round(nom[k] / real[k] * 100, 3)] for k in sorted(nom) if real.get(k)]
    D['_cpiy'] = yoy(cpi)
    mk = X.get('mkt') or {}
    start = (mk.get('index') or [['2006-01']])[0][0] if len(mk.get('index') or []) > 24 else '2006-01'
    cut = lambda s: [p for p in s if p[0] >= start]
    D['cmp'] = {'home': cut(idx), 'index': cut(mk.get('index') or []), 'gold': cut(mk.get('gold') or []), 'cpi': cut(cpi), 'rent': cut(D['rentx'] or rent)}
    D['vol'], D['starts'] = [], []
    D['maxk'] = max([p[-1][0] for p in (idx, price, D['real'], D['rentx']) if p] + [s['d'][-1][0] for s in D['rates']] + ['2000-01'])
    N = {}
    if idx:
        N['i_m'], N['i'] = idx[-1]
        N['i_y1'], N['i_y5'], N['i_y10'] = chg(idx[-1][1], back(idx, 12)), chg(idx[-1][1], back(idx, 60)), chg(idx[-1][1], back(idx, 120))
    if price:
        N['p_m'], N['p'] = price[-1]
        N['p_y1'], N['p_y10'] = chg(price[-1][1], back(price, 12)), chg(price[-1][1], back(price, 120))
    mort = [x for x in D['rates'] if not x['pol']]
    pol = [x for x in D['rates'] if x['pol']]
    if mort:
        N['rate_n'], N['rate'], N['rate_m'], N['rate_1y'] = mort[0]['n'], mort[0]['d'][-1][1], mort[0]['d'][-1][0], back(mort[0]['d'], 12)
    if pol:
        N['pol_n'], N['pol'], N['pol_m'], N['pol_1y'] = pol[0]['n'], pol[0]['d'][-1][1], pol[0]['d'][-1][0], back(pol[0]['d'], 12)
    if D['renty']:
        N['ry_m'], N['ry'] = D['renty'][-1]
    elif D['rents_y']:
        N['ry_m'], N['ry'] = D['rents_y'][-1]
    if rent:
        N['rent_m'], N['rent'], N['rent_y1'] = rent[-1][0], rent[-1][1], chg(rent[-1][1], back(rent, 12))
    for k in ('pti', 'ptr'):
        s = D[k]
        if s:
            avg = sum(v for _, v in s) / len(s)
            N[k], N[k + '_vs'], N[k + '_m'] = s[-1][1], (s[-1][1] / avg - 1) * 100, s[-1][0]
    if D['real']:
        pk = max(D['real'], key=lambda x: x[1])
        N['real_peak'], N['real_vs_peak'] = pk, (D['real'][-1][1] / pk[1] - 1) * 100
    D['N'] = N
    # regions
    rows = []
    cy = int(D['maxk'][:4])
    years = list(range(cy - 11, cy + 1))
    for g in X.get('regions') or []:
        row = {'ab': g['id'], 'n': (L.get('rg_' + cc) or {}).get(g['id']) or g.get('n_' + L.get('_code', '')) or g['n']}
        ps, ix, rs = g.get('price') or [], g.get('idx') or [], g.get('rent') or []
        main = ps or ix
        if main:
            row['v'], row['m'] = main[-1][1], main[-1][0]
            row['y1'], row['y5'], row['y10'] = r(chg(main[-1][1], back(main, 12))), r(chg(main[-1][1], back(main, 60))), r(chg(main[-1][1], back(main, 120)))
        if rs:
            row['rent'], row['ry1'] = rs[-1][1], r(chg(rs[-1][1], back(rs, 12)))
            if ps:
                row['yld'] = r(rs[-1][1] * 12 / ps[-1][1] * 100, 2)
        dv, dr = dec_values(main, years), dec_values(rs, years)
        row['yr'] = [[y, dv.get(y), None, None, dr.get(y)] for y in years]
        rows.append(row)
    rows.sort(key=lambda x: (-(x.get('v') or 0) if ps else 0, x['n']))
    for i, x in enumerate(rows):
        x['o'] = i
    D['states'], D['metros'] = rows, []
    # national year by year
    yrs = []
    for y in range(cy, cy - 11, -1):
        def ch_y(s):
            if not s:
                return None, None
            if y == cy:
                cur = [(k, v) for k, v in s if k[:4] == str(y)]
                a, m = cur[-1][1] if cur else None, cur[-1][0] if cur else None
            else:
                a, m = dec_values(s, [y]).get(y), None
            b = dec_values(s, [y - 1]).get(y - 1)
            return (r(chg(a, b)) if a and b else None), m
        row = {'y': y}
        row['idx'], row['idx_m'] = ch_y(idx)
        row['price'], _ = ch_y(price)
        row['pv'] = ([v for k, v in price if k[:4] == str(y)] or [None])[-1]
        for i, t in enumerate(D['tys'][:4]):
            row['t%d' % i], _ = ch_y(t['d'])
        row['rent'], _ = ch_y(rent if rent else D['rentx'])
        for key, lst in (('rate', mort), ('pol', pol)):
            if lst:
                vals = [v for k, v in lst[0]['d'] if k[:4] == str(y)]
                row[key] = r(sum(vals) / len(vals), 2) if vals else None
        yrs.append(row)
    D['years'] = yrs
    return D


def drivers(D, L, F):
    N = D['N']
    D['sp'] = {}
    tiles = []
    y5 = '%d' % (int(D['maxk'][:4]) - 5)

    def tile(key, label, val, sub, why, tone, series):
        tiles.append((key, label, val, sub, why, tone))
        D['sp'][key] = [p for p in series if p[0] >= y5]
    for i, rt in enumerate(D['rates'][:2]):
        s = rt['d']
        d = s[-1][1] - (back(s, 12) or s[-1][1])
        tile('r%d' % i, rt['n'], F.rate(s[-1][1]), L['d_rate_sub'].format(m=F.month(s[-1][0]), d=('+' if d > 0 else '−' if d < 0 else '') + F.n(abs(d), 2)),
             L['why_pol'] if rt['pol'] else L['why_mort'], 'pos' if d < -0.1 else 'neg' if d > 0.1 else 'neu', s)
    if N.get('pti') is not None:
        tile('pti', L['k_pti'], F.pc(N['pti_vs'], 0), L['d_vsavg'].format(q=F.q(N['pti_m'])), L['why_pti'],
             'neg' if N['pti_vs'] > 15 else 'pos' if N['pti_vs'] < 0 else 'neu', D['pti'])
    if N.get('ptr') is not None:
        tile('ptr', L['k_ptr'], F.pc(N['ptr_vs'], 0), L['d_vsavg'].format(q=F.q(N['ptr_m'])), L['why_ptr'],
             'neg' if N['ptr_vs'] > 15 else 'pos' if N['ptr_vs'] < 0 else 'neu', D['ptr'])
    ry = D['renty'] or D['rents_y']
    if ry:
        k, v = ry[-1]
        tile('ry', L['k_rentg'], F.pc(v), L['d_yoy'].format(m=F.q(k) if D['renty'] else F.month(k)), L['why_rent'], 'pos' if v > 3 else 'neu', ry)
    if D['realy']:
        k, v = D['realy'][-1]
        tile('real', L['k_real'], F.pc(v), L['d_real'].format(q=F.q(k), p=F.pc(N.get('real_vs_peak'), 0), y=N['real_peak'][0][:4]), L['why_real'], 'neu', D['realy'])
    if D['_cpiy']:
        k, v = D['_cpiy'][-1]
        tile('cpi', L['k_infl'], F.pc(v), L['d_yoy'].format(m=F.q(k)), L['why_infl'], 'neu', D['_cpiy'])
    if D['idxy']:
        k, v = D['idxy'][-1]
        tile('iy', L['k_pg'], F.pc(v), L['d_yoy'].format(m=F.month(k)), L['why_mom'], 'pos' if v > 2 else 'neg' if v < 0 else 'neu', D['idxy'])
    if len(tiles) > 4:
        tiles = tiles[:len(tiles) // 4 * 4]
    return tiles


def chart_cfg(D, L):
    j = json.dumps
    t = {}
    pv = ["{s:function(D){return [{n:%s,c:'#C9A961',d:D.idx,f:'i'}]},note:%s}" % (j(D['idx_n']), j(D['idx_n'] + '. ' + L['shaded']))]
    labs = [L['tab_index']]
    if D['real']:
        pv.append("{s:function(D){return [{n:%s,c:'#C9A961',d:D.real,f:'i'}]},note:%s}" % (j(L['s_real']), j(L['note_real'])))
        labs.append(L['tab_real'])
    if D['price']:
        pv.append("{s:function(D){return [{n:%s,c:'#C9A961',d:D.price,f:'$'}]},note:''}" % j(D['price_n']))
        labs.append(L['tab_price'].format(s=D['sym']))
    pv.append("{s:function(D){return [{n:%s,c:'#C9A961',d:D.idxy,f:'+%%'}]},zero0:1,note:%s}" % (j(L['s_yoy']), j(L['note_yoy'])))
    labs.append(L['tab_yoy'])
    t['price'] = (pv, labs)
    if D['tys']:
        t['types'] = (["{s:function(D){return D.tys.map(function(x){return {n:x.n,c:x.c,d:x.d,f:D.tysm?'$':'i'}})},note:''}"], ['-'])
    t['cmp'] = (["{s:function(D){var c=D.cmp;return [{n:%s,c:'#C9A961',d:c.home},{n:%s,c:'#6FA8DC',d:c.index},{n:%s,c:'#E8C77A',d:c.gold,dash:1},{n:%s,c:'#4FA37A',d:c.rent},{n:%s,c:'#8A8F99',d:c.cpi}]},norm:1,note:%s}" % (
        j(L['s_home']), j(D['index_name']), j(L['s_gold']), j(L['s_rents']), j(L['s_infl']), j(L['note_cmp']))], ['-'])
    rv = ["{s:function(D){return D.rates.map(function(x){return {n:x.n,c:x.c,d:x.d,f:'%2'}})},note:''}"]
    rl = [L['tab_rates']]
    if D['pti']:
        rv.append("{s:function(D){return [{n:%s,c:'#C9A961',d:D.pti,f:'i'},{n:%s,c:'#6FA8DC',d:D.ptr,f:'i'}]},note:%s}" % (j(L['s_pti']), j(L['s_ptr']), j(L['note_aff'])))
        rl.append(L['tab_aff'])
    if D['rates']:
        rv.append("{s:function(D){return [{n:%s,c:'#C9A961',d:D.idxy,f:'+%%'},{n:D.rates[0].n,c:'#6FA8DC',d:D.rates[0].d,f:'%%2',ax:1}]},zero0:1,note:%s}" % (j(L['s_yoy']), j(L['note_pvr'])))
        rl.append(L['tab_pvr'])
    t['rates'] = (rv, rl)
    ren, rnl = [], []
    ry = 'D.renty' if D['renty'] else 'D.rents_y' if D['rents_y'] else None
    if ry:
        ren.append("{s:function(D){return [{n:%s,c:'#4FA37A',d:%s,f:'+%%'},{n:%s,c:'#C9A961',d:D.idxy,f:'+%%',w:1.5}]},zero0:1,note:''}" % (j(L['s_rents_y']), ry, j(L['s_yoy'])))
        rnl.append(L['tab_rentg'])
    if D['rent']:
        ren.append("{s:function(D){return [{n:%s,c:'#4FA37A',d:D.rent,f:'$'}]},note:''}" % j(D['rent_n'] or ''))
        rnl.append(L['tab_rentl'])
    if ren:
        t['rent'] = (ren, rnl)
    js = 'window.HS_CFG={' + ','.join('%s:{y:%d,v:[%s]}' % (k, 20 if k in ('cmp', 'rent') else 0, ','.join(v[0])) for k, v in t.items()) + '};'
    return js, {k: v[1] for k, v in t.items()}


def ranges(L, default):
    return ''.join('<button data-y="%d"%s>%s</button>' % (y, ' class="on"' if y == default else '', l)
                   for y, l in ((5, L['y5']), (10, L['y10']), (20, L['y20']), (0, L['all'])))


def chart_card(L, key, title, sub, tabs, default_y, src):
    tb = ''.join('<button data-t="%d"%s>%s</button>' % (i, ' class="on"' if i == 0 else '', esc(l)) for i, l in enumerate(tabs)) if len(tabs) > 1 else ''
    return ('<div class="card" data-chart="%s"><h3>%s</h3><p class="sub">%s</p><div class="bar">%s<span class="sp"></span>%s</div>'
            '<div class="ch"></div><div class="lg"></div><p class="src cn"></p><p class="src">%s</p></div>') % (key, title, sub, tb, ranges(L, default_y), src)


DETAIL_JS = r"""window.HS_STDETAIL=function(r){var D=JSON.parse(document.getElementById('hs-data').textContent),T=D.tx,LOC=D.loc;
 function fmv(v){if(v==null)return '—';return D.yfmt==='i'?v.toLocaleString(LOC,{maximumFractionDigits:1,minimumFractionDigits:1}):new Intl.NumberFormat(LOC,{style:'currency',currency:D.cur,currencyDisplay:D.narrow?'narrowSymbol':'symbol',maximumFractionDigits:0}).format(v)}
 function cc(a,b){if(a==null||b==null)return '<td>—</td>';var v=(a/b-1)*100;return '<td class="'+(v>0?'up':'dn')+'">'+(v>0?'+':v<0?'−':'')+Math.abs(v).toLocaleString(LOC,{maximumFractionDigits:1,minimumFractionDigits:1})+'%</td>'}
 var use=[1,4].filter(function(j){return r.yr.some(function(x){return x[j]!=null})}),L=[,D.ylab,,,T.rent];
 var h='<b style="font-weight:600">'+r.n+' – '+T.ybyy+'</b><p class="mut" style="margin:2px 0 6px;font-size:12.5px">'+T.ynote+'</p><div class="tw"><table class="yt"><thead><tr><th>'+T.year+'</th>'+use.map(function(j){return '<th>'+L[j]+'</th><th>'+T.change+'</th>'}).join('')+'</tr></thead><tbody>';
 for(var i=r.yr.length-1;i>=1;i--){var a=r.yr[i],p=r.yr[i-1];if(a[1]==null&&a[4]==null)continue;h+='<tr><td>'+a[0]+(i===r.yr.length-1?' <small class="mut">('+T.latest+')</small>':'')+'</td>'+use.map(function(j){return '<td>'+(j===4?(a[j]==null?'—':new Intl.NumberFormat(LOC,{style:'currency',currency:D.cur,currencyDisplay:D.narrow?'narrowSymbol':'symbol',maximumFractionDigits:D.rdec||0}).format(a[j])):fmv(a[j]))+'</td>'+cc(a[j],p[j])}).join('')+'</tr>'}
 return h+'</tbody></table></div>'};"""


def build(sd, lang, cc, countries, chrome_html, urlf, flip=None, root='https://example.com', brand=''):
    X = load(sd, cc)
    if not X:
        print('housing %s: no data' % cc)
        return None
    L = I18N.lang(lang)
    L['_code'] = lang
    C = L['c'][cc]
    global SEP
    SEP = L.get('_sep', ', ')
    curn = (L.get('_curn') or {}).get(X['cur'], X['cur'])
    X['sym'] = (L.get('_syms') or {}).get(X['cur'], X['sym'])
    X['src'] = [L.get('src_' + x, x) for x in X.get('src') or []]          # {name, adj, in_, of}
    D = prepare(cc, X, L)
    alt = (X.get('mkt') or {}).get('alt')
    D['index_name'] = (alt and L.get('ix_%s_%s' % (cc, alt))) or L.get('ix_' + cc) or INDEX_NAME.get(cc, '')
    N, F = D['N'], Fmt(L, X['sym'], X['cur'])
    tiles = drivers(D, L, F)
    cfg_js, tabs = chart_cfg(D, L)
    geo = None
    gp = os.path.join(HERE, 'web_src', 'geo', '%s-paths.json' % cc)
    if D['states'] and os.path.exists(gp):
        geo = json.load(open(gp))
        if cc in ('es', 'gb'):
            geo['merged'] = 1
        known = set(geo['s'])
        D['states'] = [s for s in D['states'] if s['ab'] in known] + [s for s in D['states'] if s['ab'] not in known]
    states = D['states']
    nav = '<nav class="cty" aria-label="%s">' % L['country'] + ''.join(
        '<a%s href="%s">%s %s</a>' % (' class="on"' if c == cc else '', urlf(c), FLAG.get(c, ''), esc(L['c'][c]['name'])) for c in countries) + '</nav>' if len(countries) > 1 else ''
    # lead
    lead = []
    if N.get('i_y1') is not None:
        lead.append(L['lead_p'].format(in_=C['in_'], name=C['name'], adj=C['adj'], dir=L['up'] if N['i_y1'] >= 0 else L['down'], v=F.pc(abs(N['i_y1']), 1, False), src=D['idx_n'], m=F.monthl(N['i_m'])))
    if N.get('p') is not None:
        lead.append(L['lead_price'].format(n=D['price_n'], v=F.money(N['p'])))
    if N.get('rate') is not None and N.get('rate_1y') is not None:
        lead.append(L['lead_rate'].format(n=mid(L['lead_rate'], N['rate_n']), v=F.rate(N['rate']), dir=L['from_down'] if N['rate'] < N['rate_1y'] else L['from_up'], p=F.rate(N['rate_1y'])))
    elif N.get('pol') is not None and N.get('pol_1y') is not None:
        lead.append(L['lead_rate'].format(n=mid(L['lead_rate'], N['pol_n']), v=F.rate(N['pol']), dir=L['from_down'] if N['pol'] < N['pol_1y'] else L['from_up'], p=F.rate(N['pol_1y'])))
    if N.get('ry') is not None:
        lead.append(L['lead_rent'].format(dir=L['up'] if N['ry'] >= 0 else L['down'], v=F.pc(abs(N['ry']), 1, False)))
    rk = sorted([s for s in states if s.get('y1') is not None], key=lambda s: s['y1'])
    if len(rk) > 2:
        lead.append(L['lead_reg'].format(k=len([s for s in rk if s['y1'] > 0]), n=len(rk), top=rk[-1]['n'], tv=F.pc(rk[-1]['y1']), low=rk[0]['n'], lv=F.pc(rk[0]['y1'])))
    # KPIs
    def kp(label, val, sub):
        return '<div><div class="k"><span>%s</span></div><div class="v">%s</div><div class="s">%s</div></div>' % (label, val, sub)
    ch = lambda v, d=1: '<b class="%s">%s</b>' % (cls(v), F.pc(v, d))
    kps = []
    if N.get('p') is not None:
        kps.append(kp(D['price_n'], F.money(N['p']), '%s %s · %s %s · %s' % (ch(N.get('p_y1')), L['y1s'], ch(N.get('p_y10'), 0), L['y10s'], F.month(N['p_m']))))
    if N.get('i_y1') is not None:
        kps.append(kp(L['k_p1'], F.pc(N['i_y1']), '%s %s · %s %s · %s' % (ch(N.get('i_y5'), 0), L['y5s'], ch(N.get('i_y10'), 0), L['y10s'], F.month(N['i_m']))))
    if N.get('rate') is not None:
        kps.append(kp(N['rate_n'], F.rate(N['rate']), '%s · %s %s' % (F.month(N['rate_m']), L['ago'], F.rate(N.get('rate_1y')))))
    if N.get('pol') is not None:
        kps.append(kp(N['pol_n'], F.rate(N['pol']), '%s %s' % (L['ago'], F.rate(N.get('pol_1y')))))
    if N.get('rent') is not None:
        kps.append(kp(D['rent_n'] or L['k_rent'], F.money(N['rent']) if N['rent'] > 200 else F.money(N['rent'], 2), '%s · %s' % (ch(N.get('rent_y1')), F.month(N['rent_m']))))
    if N.get('ry') is not None:
        kps.append(kp(L['k_rentg'], F.pc(N['ry']), L['d_yoy'].format(m=F.q(N['ry_m']) if D['renty'] else F.month(N['ry_m']))))
    for k, lab in (('pti', 'k_pti'), ('ptr', 'k_ptr')):
        if N.get(k) is not None:
            kps.append(kp(L[lab], F.pc(N[k + '_vs'], 0), L['vs_avg_oecd']))
    if N.get('real_vs_peak') is not None:
        kps.append(kp(L['k_realpeak'].format(y=N['real_peak'][0][:4]), F.pc(N['real_vs_peak'], 0), L['after_infl']))
    if X.get('sales'):        # transaction-level sources (Dubai): sales per month and off-plan share
        m_, n_ = X['sales'][-1]
        if m_ == TODAY_YM() and len(X['sales']) > 1:
            m_, n_ = X['sales'][-2]   # the running month is not complete yet
        kps.append(kp(L['k_sales'], F.n(n_), F.monthl(m_)))
    if X.get('offplan'):
        kps.append(kp(L['k_off'], F.pc(X['offplan'][-1][1], 0, False), F.monthl(X['offplan'][-1][0])))
    for t in D['tys'][:2] if len(kps) < 4 and D.get('tysm') else []:
        kps.append(kp(t['n'], F.money(t['d'][-1][1]), F.month(t['d'][-1][0])))
    kps = kps[:6] if len(kps) >= 6 else kps[:4] if len(kps) >= 4 else kps
    # year table
    tys = D['tys'][:4]
    mort = [x for x in D['rates'] if not x['pol']]
    pol = [x for x in D['rates'] if x['pol']]
    head = '<th>%s</th><th>%s</th>' % (L['year'], L['h_idx']) + ('<th>%s</th>' % esc(D['price_n'] if len(D['price_n'] or '') <= 26 else L['h_price']) if D['price'] else '') + \
        ''.join('<th class="hm">%s</th>' % esc(t['n']) for t in tys) + '<th>%s</th>' % L['rents'] + \
        ('<th>%s<br><small class="mut">%s</small></th>' % (esc(mort[0]['n']), L['avg']) if mort else '') + \
        ('<th>%s<br><small class="mut">%s</small></th>' % (esc(pol[0]['n']), L['avg']) if pol else '')
    yrows = []
    for y in D['years']:
        if all(y.get(k) is None for k in ('idx', 'price', 'rent', 'rate', 'pol')):
            continue
        lbl = str(y['y']) + (' <small class="mut">%s</small>' % L['to'].format(m=L['_mon'][int(y['idx_m'][5:7]) - 1]) if y.get('idx_m') else '')
        c = lambda v, extra='': '<td class="%s%s">%s</td>' % (extra, cls(v), F.pc(v))
        yrows.append('<tr><td>%s</td>%s%s%s%s%s%s</tr>' % (
            lbl, c(y.get('idx')), ('<td>%s <small class="%s">%s</small></td>' % (F.money(y.get('pv')), cls(y.get('price')), F.pc(y.get('price')))) if D['price'] else '',
            ''.join(c(y.get('t%d' % i), 'hm ') for i in range(len(tys))), c(y.get('rent')),
            ('<td>%s</td>' % F.rate(y.get('rate'))) if mort else '', ('<td>%s</td>' % F.rate(y.get('pol'))) if pol else ''))
    year_tbl = '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (head, ''.join(yrows))
    # comparison
    cmp = D['cmp']
    crow = []
    for lbl, key in ((L['s_home'], 'home'), ('%s (%s)' % (D['index_name'], L['price_only']), 'index'), (L['s_gold'], 'gold'), (L['s_rents'], 'rent'), (L['s_infl'], 'cpi')):
        s = cmp.get(key) or []
        if s:
            crow.append((lbl, [chg(s[-1][1], back(s, y * 12)) for y in (1, 5, 10, 20)]))
    best = [max((v[i] for _, v in crow if v[i] is not None), default=None) for i in range(4)]
    cmp_tbl = ('<div class="tw"><table><thead><tr><th></th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>' % (L['y1l'], L['y5l'], L['y10l'], L['y20l']) +
               ''.join('<tr><td class="nm">%s</td>%s</tr>' % (esc(l), ''.join('<td class="%s"%s>%s</td>' % (cls(v), ' style="background:rgba(79,163,122,.12)"' if v is not None and v == best[i] else '', F.pc(v, 0 if i else 1)) for i, v in enumerate(vals))) for l, vals in crow) +
               '</tbody></table></div>')
    base = {'KRW': 10000000, 'JPY': 1000000, 'IDR': 100000000, 'TRY': 100000, 'BRL': 10000}.get(X['cur'], 10000)
    grow = ''.join('<div><small>%s</small><b>%s</b></div>' % (esc(l), F.money(base * (1 + v[2] / 100))) for l, v in crow if v[2] is not None)
    if grow:
        cmp_tbl += '<h3 style="margin:16px 0 8px">%s</h3><div class="dg">%s</div><p class="src">%s</p>' % (L['became'].format(v=F.money(base)), grow, L['price_only_note'])
    dv = ''.join('<div class="dc"><div class="k"><span>%s</span><em class="%s">%s</em></div><div class="v">%s</div><div class="s">%s</div><svg data-sp="%s"></svg><div class="why">%s</div></div>' % (
        esc(label), tone, L['tone_' + tone], val, sub, key, why) for key, label, val, sub, why, tone in tiles)
    # types card
    types_html = ''
    if D['tys']:
        trs = ''.join('<tr><td class="nm">%s</td><td>%s</td><td class="%s">%s</td><td class="%s">%s</td><td class="%s">%s</td></tr>' % (
            esc(t['n']), F.money(t['d'][-1][1]) if D.get('tysm') else F.n(t['d'][-1][1], 1), cls(chg(t['d'][-1][1], back(t['d'], 12))), F.pc(chg(t['d'][-1][1], back(t['d'], 12))),
            cls(chg(t['d'][-1][1], back(t['d'], 60))), F.pc(chg(t['d'][-1][1], back(t['d'], 60)), 0), cls(chg(t['d'][-1][1], back(t['d'], 120))), F.pc(chg(t['d'][-1][1], back(t['d'], 120)), 0)) for t in D['tys'])
        types_html = '<div class="two">%s<div class="card"><h3>%s</h3><p class="sub">%s</p><div class="tw"><table><thead><tr><th></th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div></div></div>' % (
            chart_card(L, 'types', L['types_t'], L['types_s'], ['-'], 0, L['src'] + ': ' + SEP.join(X['src'][:1])), L['types_t2'], L['types_s2'], L['h_price'] if D.get('tysm') else L['h_idx'], L['y1l'], L['y5l'], L['y10l'], trs)
    # regions
    regions_html = ''
    if states:
        rn, rns = L['rn_' + cc] if ('rn_' + cc) in L else (L['region'], L['regions'])
        has_rent = any(s.get('rent') is not None for s in states)
        pricecol = bool(X.get('regions') and X['regions'][0].get('price'))
        cols = [('v', L['h_price'] if pricecol else L['h_idx'], '$' if pricecol else 'i', ''), ('y1', L['y1l'], '+%', ''), ('y5', L['y5l'], '+%', 'hm'), ('y10', L['y10l'], '+%', '')]
        if has_rent:
            cols += [('rent', L['rents'], 'r', ''), ('ry1', L['rent1y'], '+%', 'hm')]
            if pricecol:
                cols.append(('yld', L['yield'], '%2', 'hm'))
        cols = [c for c in cols if any(s.get(c[0]) is not None for s in states)]

        def fv(v, f):
            return F.money(v) if f == '$' else F.pc(v) if f == '+%' else F.rate(v) if f == '%2' else ('—' if v is None else F.money(v, 2) if v < 200 else F.money(v)) if f == 'r' else F.n(v, 1)
        srows = ''.join('<tr class="rw" data-k="%s"><td class="nm">%s</td>%s</tr>' % (esc(s['ab']), esc(s['n']), ''.join(
            '<td class="%s %s">%s</td>' % (hm, cls(s.get(k)) if f == '+%' else '', fv(s.get(k), f)) for k, l, f, hm in cols)) for s in states)
        thead = '<th>%s</th>' % rn + ''.join('<th class="%s">%s</th>' % (hm, l) for k, l, f, hm in cols)
        sort_opts = [('def', L['sort_def']), ('n:a', L['sort_az'])] + [('%s:d' % k, L['sort_hi'].format(l=l)) for k, l, f, _ in cols if f != '+%'] + \
            [('%s:a' % k, L['sort_lo'].format(l=l)) for k, l, f, _ in cols if f in ('$', 'r')] + [('%s:d' % k, L['sort_up'].format(l=l)) for k, l, f, _ in cols if f == '+%'] + \
            [('y1:a', L['sort_down'].format(l=L['y1l']))]
        sel = '<select class="srt" id="hs-st-sort" aria-label="%s">%s</select>' % (L['sort'], ''.join('<option value="%s">%s</option>' % kv for kv in sort_opts))
        mapm = [(k, l, {'$': '$', 'i': 'i', '+%': '+%', '%2': '%2', 'r': '$'}[f], 1 if f == '+%' and k in ('y1', 'ry1') else 0) for k, l, f, _ in cols if k != 'y5']
        D['mapm'] = {k: [l, f, d] for k, l, f, d in mapm}
        D['map0'] = mapm[0][0]
        D['tip'] = [[l, k, {'r': '$'}.get(f, f)] for k, l, f, _ in cols[:4]]
        D['small'] = {k: 1 for k in (geo or {}).get('s', {}) if len(geo['s']) > 20 or len(k) > 4}
        D['nshow'] = 5
        D['moreS'] = L['show_all'].format(n=len(states), w=rns)
        D['lessS'] = L['show_5']
        D['ylab'] = cols[0][1]
        D['yfmt'] = '$' if pricecol else 'i'
        D['rdec'] = 2 if has_rent and states[0].get('rent', 999) < 200 else 0
        D['geo'] = geo or {'w': 10, 'h': 10, 's': {}}
        mb = ''.join('<button data-m="%s"%s>%s</button>' % (k, ' class="on"' if i == 0 else '', esc(l)) for i, (k, l, f, d) in enumerate(mapm))
        mapblock = ('<div class="card"><div class="bar">%s</div><div class="map" id="hs-map" style="max-width:%dpx"><svg viewBox="0 0 %d %d" role="img" aria-label="%s"></svg><div class="tip"></div></div><div class="scale"></div></div>' % (
            mb, min(900, geo['w']), geo['w'], geo['h'], esc(L['map_aria'].format(c=C['name']))) if geo else '')
        regions_html = '<h2 id="regions" class="ac">%s</h2><p class="sub">%s</p>%s<div class="card"><div class="bar"><b style="font-weight:600">%s</b><span class="sp"></span>%s</div><div class="tw"><table><thead><tr>%s</tr></thead><tbody id="hs-st">%s</tbody></table></div><button class="more" id="hs-st-more"></button><p class="src">%s</p></div>' % (
            L['h_regions'].format(w=rn), L['regions_sub'].format(w=rn), mapblock, L['all_regions'].format(w=rns), sel, thead, srows, L['dash_note'].format(w=rn) + ' ' + L['src'] + ': ' + esc(X['src'][0]) + '.')
    D['narrow'] = L.get('_narrow')
    D['pctpre'] = L.get('_pctpre')
    D['loc'], D['tx'] = L['_loc'], {'year': L['year'], 'change': L['change'], 'latest': L['latest'], 'ybyy': L['ybyy'], 'ynote': L['ynote'], 'rent': L['rents'],
                                    'nodata': L['nodata'], 'q': L['_qjs'], 'mo': L['_mo']}
    pdata = {k: D.get(k) for k in ('idx', 'idxy', 'real', 'price', 'pti', 'ptr', 'renty', 'rents_y', 'rent', 'tys', 'rates', 'cmp', 'vol', 'starts', 'sp', 'maxk',
                                   'tysm', 'states', 'metros', 'geo', 'sym', 'cur', 'narrow', 'pctpre', 'loc', 'tx', 'mapm', 'map0', 'tip', 'small', 'nshow', 'moreS', 'lessS', 'ylab', 'yfmt', 'rdec')}
    if not states:
        pdata['states'], pdata['geo'] = [], {'w': 10, 'h': 10, 's': {}}
    pdata['rec'] = [['2008-04', '2009-06'], ['2020-02', '2020-06']]
    blob = json.dumps(pdata, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
    srcs = SEP.join(s for s in X['src'] if s != L.get('src_Yahoo Finance', 'Yahoo Finance'))
    has_years, has_drv, has_rates = bool(yrows), bool(tiles), bool(D['rates'])
    toc_items = [('prices', L['toc_prices'])] + ([('years', L['toc_years'])] if has_years else []) + [('vs', L['toc_vs'])] + \
        ([('drivers', L['toc_drivers'])] if has_drv else []) + ([('rates', L['toc_rates'])] if has_rates else []) + \
        ([('regions', L['toc_regions'].format(w=(L['rn_' + cc] if ('rn_' + cc) in L else (L['region'],))[0]))] if states else []) + ([('rents', L['toc_rents'])] if 'rent' in tabs else [])
    toc = '<nav class="toc">' + ''.join('<a href="#%s">%s</a>' % kv for kv in toc_items) + '</nav>'
    stamp = L['stamp'].format(d=F.monthl(D['as_of'][:7]).split(' ')[0] + ' ' + D['as_of'][8:10].lstrip('0') + ', ' + D['as_of'][:4] if lang == 'en' else dt.date.fromisoformat(D['as_of']).strftime('%d.%m.%Y'), c=curn)
    body = f"""
<h1>🏠 {L['h1'].format(**C)}</h1>
<p class="sub">{L['sub'].format(idx=D['index_name'], **C)}</p>
{nav}
<p class="stamp">{stamp}</p>
<div class="lead">{' '.join(lead)}<small>{L['auto']}</small></div>
<div class="kp n{len(kps)}">{''.join(kps)}</div>
{toc}
<div id="prices" class="ac">{chart_card(L, 'price', L['ch_price'].format(**C), L['ch_price_s'], tabs['price'], 0, L['src'] + ': ' + srcs + '.')}</div>
{types_html}
{('<h2 id="years" class="ac">' + L['h_years'].format(**C) + '</h2><p class="sub">' + L['years_sub'] + '</p><div class="card">' + year_tbl + '</div>') if has_years else ''}
<h2 id="vs" class="ac">{L['h_vs'].format(idx=D['index_name'], **C)}</h2>
<div class="two">
{chart_card(L, 'cmp', L['growth100'], L['prices_only_in'].format(c=curn), ['-'], 20, L['src'] + ': ' + SEP.join([D['idx_n'], L.get('src_Yahoo Finance', 'Yahoo Finance'), L.get('src_OECD', 'OECD')]) + '.')}
<div class="card"><h3>{L['total_change']}</h3><p class="sub">{L['best']}</p>{cmp_tbl}</div>
</div>
{('<h2 id="drivers" class="ac">' + L['h_drivers'].format(**C) + '</h2><p class="sub">' + L['drivers_sub'] + '</p><div class="drv">' + dv + '</div>') if has_drv else ''}
{('<h2 id="rates" class="ac">' + L['h_rates'] + '</h2>' + chart_card(L, 'rates', L['h_rates'], '', tabs['rates'], 0, L['src'] + ': ' + srcs + '.')) if has_rates else ''}
{regions_html}
{('<h2 id="rents" class="ac">' + L['h_rents'] + '</h2>' + chart_card(L, 'rent', L['h_rents'], '', tabs['rent'], 20, L['src'] + ': ' + srcs + '.')) if 'rent' in tabs else ''}
{('<div class="card" style="margin-top:22px"><h3>' + L['more_markets'] + '</h3>' + nav + '</div>') if nav else ''}
<script type="application/json" id="hs-data">{blob}</script>
<script>{cfg_js}</script>
<script>{DETAIL_JS}</script>
<script>{JS}</script>
"""
    css = theme_css(sd)
    if flip:
        css = flip(css)
    if L['_dir'] == 'rtl':   # charts, map scale and numbers keep left-to-right order inside a right-to-left page
        css += '\n#hs svg,#hs .scale{direction:ltr}'
    page = '<div id="hs" dir="%s"><style>' % L['_dir'] + css + CSS + '</style>' + chrome_html + body + '</div>'
    title = L['title'].format(**C)
    desc = L['desc'].format(dir=L['up'] if (N.get('i_y1') or 0) >= 0 else L['down'], v=F.pc(abs(N.get('i_y1') or 0), 1, False), **C)
    faq = []
    if N.get('i_y1') is not None:
        faq.append((L['q_dir'].format(**C), L['a_dir'].format(in_=C['in_'], name=C['name'], adj=C['adj'], dir=L['up'] if N['i_y1'] >= 0 else L['down'], v=F.pc(abs(N['i_y1']), 1, False), src=D['idx_n'], m=F.monthl(N['i_m']), t=F.pc(N.get('i_y10'), 0))))
    if N.get('p') is not None:
        faq.append((L['q_price'].format(**C), L['a_price'].format(n=D['price_n'], v=F.money(N['p']), m=F.month(N['p_m']))))
    if N.get('rate') is not None or N.get('pol') is not None:
        faq.append((L['q_rate'].format(**C), L['a_rate'].format(n=N.get('rate_n') or N.get('pol_n'), v=F.rate(N.get('rate') if N.get('rate') is not None else N.get('pol')))))
    if N.get('pti') is not None:
        faq.append((L['q_over'].format(**C), L['a_over'].format(pti=F.pc(N['pti_vs'], 0), ptr=F.pc(N.get('ptr_vs'), 0))))
    up = sorted([s for s in states if s.get('y1') is not None], key=lambda s: -s['y1'])
    paras = [L['p1'].format(src=D['idx_n'], **C)]
    if len(up) > 3:
        paras.append(L['p_reg'].format(top=SEP.join('%s (%s)' % (s['n'], F.pc(s['y1'])) for s in up[:3]), low=SEP.join('%s (%s)' % (s['n'], F.pc(s['y1'])) for s in up[-3:][::-1])))
    paras.append(L['p_drivers'])
    seo = '<section class="sa-seo cv"><div><h2>%s</h2>%s<h3>%s</h3>%s</div></section>' % (
        L['seo_h'].format(**C), ''.join('<p>%s</p>' % p for p in paras), L['faq'], ''.join('<details><summary>%s</summary><p>%s</p></details>' % qa for qa in faq))
    u = urlf(cc)
    ld = [{'@context': 'https://schema.org', '@type': 'Dataset', 'name': title, 'url': root + u, 'dateModified': D['as_of'], 'isAccessibleForFree': True,
           'spatialCoverage': C['name'], 'description': desc, 'creator': {'@type': 'Organization', 'name': brand or root}},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in faq]}]
    return {'url': u, 'title': title, 'desc': desc, 'html': page, 'seo': seo, 'ld': ld, 'date': D['as_of']}


def build_all(sd, lang, countries, chrome_html, urlf, flip=None, root='', brand=''):
    out = []
    for cc in countries:
        try:
            p = build(sd, lang, cc, countries, chrome_html, urlf, flip, root, brand)
            if p:
                out.append(p)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            print('housing page %s/%s skipped: %s' % (lang, cc, ex))
    return out
