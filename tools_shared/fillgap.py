"""Fill table gaps that we can compute ourselves, and give a word instead of a bare dash
where a number does not exist (a loss, no dividend, an unchanged position).
Shared by all language sites: copy of stock-data/tools_shared/fillgap.py."""

L = {
    #       0 back to profit, 1 swung to loss, 2 loss narrowed, 3 loss widened,
    #       4 turned positive, 5 turned negative, 6 less negative, 7 more negative,
    #       8 P/E loss, 9 no dividend, 10 unchanged, 11 no revenue, 12 net income growth (row label)
    'en': ['Back to profit', 'Swung to loss', 'Loss narrowed', 'Loss widened',
           'Turned positive', 'Turned negative', 'Less negative', 'More negative',
           'Loss', 'None', 'Unchanged', 'No revenue', 'Net income growth'],
    'es': ['Vuelve a ganancias', 'Pasa a pérdidas', 'Pérdida menor', 'Pérdida mayor',
           'Pasa a positivo', 'Pasa a negativo', 'Menos negativo', 'Más negativo',
           'Pérdidas', 'No paga', 'Sin cambios', 'Sin ingresos', 'Crecimiento del beneficio neto'],
    'pt': ['Volta ao lucro', 'Passa a prejuízo', 'Prejuízo menor', 'Prejuízo maior',
           'Fica positivo', 'Fica negativo', 'Menos negativo', 'Mais negativo',
           'Prejuízo', 'Não paga', 'Sem alteração', 'Sem receita', 'Crescimento do lucro líquido'],
    'de': ['Wieder Gewinn', 'In die Verlustzone', 'Verlust kleiner', 'Verlust größer',
           'Wieder positiv', 'Ins Minus', 'Weniger negativ', 'Stärker negativ',
           'Verlust', 'Keine', 'Unverändert', 'Kein Umsatz', 'Gewinnwachstum'],
    'fr': ['Retour au bénéfice', 'Passe en perte', 'Perte réduite', 'Perte creusée',
           'Redevient positif', 'Devient négatif', 'Moins négatif', 'Plus négatif',
           'Perte', 'Aucun', 'Inchangée', 'Pas de CA', 'Croissance du résultat net'],
    'it': ['Torna in utile', 'Passa in perdita', 'Perdita ridotta', 'Perdita ampliata',
           'Torna positivo', 'Diventa negativo', 'Meno negativo', 'Più negativo',
           'In perdita', 'Nessuno', 'Invariata', 'Nessun ricavo', "Crescita dell'utile netto"],
    'tr': ['Kâra döndü', 'Zarara geçti', 'Zarar azaldı', 'Zarar büyüdü',
           'Pozitife döndü', 'Negatife döndü', 'Eksi azaldı', 'Eksi büyüdü',
           'Zarar', 'Yok', 'Değişmedi', 'Gelir yok', 'Net kâr büyümesi'],
    'ja': ['黒字転換', '赤字転落', '赤字縮小', '赤字拡大',
           'プラス転換', 'マイナス転落', 'マイナス縮小', 'マイナス拡大',
           '赤字', '無配', '変化なし', '売上なし', '純利益成長率'],
    'ko': ['흑자 전환', '적자 전환', '적자 축소', '적자 확대',
           '플러스 전환', '마이너스 전환', '마이너스 축소', '마이너스 확대',
           '적자', '무배당', '변동 없음', '매출 없음', '순이익 성장률'],
    'id': ['Kembali laba', 'Berbalik rugi', 'Rugi menyempit', 'Rugi melebar',
           'Berbalik positif', 'Berbalik negatif', 'Negatif menyempit', 'Negatif melebar',
           'Rugi', 'Tidak ada', 'Tetap', 'Tanpa pendapatan', 'Pertumbuhan laba bersih'],
    'vi': ['Có lãi trở lại', 'Chuyển sang lỗ', 'Lỗ thu hẹp', 'Lỗ mở rộng',
           'Chuyển dương', 'Chuyển âm', 'Âm ít hơn', 'Âm nhiều hơn',
           'Lỗ', 'Không trả', 'Không đổi', 'Chưa có doanh thu', 'Tăng trưởng lợi nhuận ròng'],
    'ar': ['عودة إلى الربح', 'تحوّل إلى خسارة', 'تقلّص الخسارة', 'اتساع الخسارة',
           'تحوّل إلى موجب', 'تحوّل إلى سالب', 'سالب أقل', 'سالب أكبر',
           'خسارة', 'لا توزيعات', 'دون تغيير', 'لا إيرادات', 'نمو صافي الربح'],
}

PROFIT_KEYS = ('net_income', 'eps_diluted', 'eps', 'op_income', 'pretax')


def lbl(lang, i):
    return (L.get(lang) or L['en'])[i]


def mut(s):
    return '<span class="mut">%s</span>' % s


def sign_change(lang, a, b, key='net_income'):
    """Word for a change where a percentage is meaningless (the base is zero or negative).
    Returns None when an ordinary percentage works (b > 0) or a value is missing."""
    if a is None or b is None or b > 0:
        return None
    o = 0 if key in PROFIT_KEYS else 4
    if b == 0:
        return None
    if a >= 0:
        return lbl(lang, o)
    # both negative
    ch = (abs(b) - abs(a)) / abs(b)
    if ch >= 0:
        return '%s %.0f%%' % (lbl(lang, o + 2), ch * 100)
    return '%s %.0f%%' % (lbl(lang, o + 3), -ch * 100)


def neg_to(lang, a, b, key='net_income'):
    """Positive base, negative result: the ordinary % would read e.g. -180%; add the word."""
    if a is None or b is None or not (b > 0 and a < 0):
        return None
    return lbl(lang, 1 if key in PROFIT_KEYS else 5)


def pe_cell(lang, r, ttm=None, digits=1):
    """P/E text: the number, or 'Loss' when trailing earnings are negative."""
    r = r or {}
    pe = r.get('pe')
    if pe and pe > 0:
        return ('%.' + str(digits) + 'f') % pe
    ey = r.get('earnings_yield')
    ni = (ttm or {}).get('net_income')
    if (ey is not None and ey < 0) or (ni is not None and ni < 0) or (pe is not None and pe <= 0):
        return mut(lbl(lang, 8))
    return '—'


def div_cell(lang, r, fmt):
    dy = (r or {}).get('div_yield')
    if dy:
        return fmt(dy)
    if dy is not None:  # 0.0 = pays no dividend
        return mut(lbl(lang, 9))
    return '—'


def growth(a, b):
    if a is None or b is None or b <= 0:
        return None
    return a / b - 1


def enrich_fin(d, a, tt):
    """Return (rows, ttm) copies with computed revenue growth, net income growth,
    and TTM balance-sheet / return figures from the latest quarterly balance sheet."""
    full = d.get('annual') or []
    byfy = {x.get('fy'): x for x in full}
    rows = []
    for x in a:
        x = dict(x)
        p = byfy.get((x.get('fy') or 0) - 1)
        if x.get('revenue_growth') is None and p:
            x['revenue_growth'] = growth(x.get('revenue'), p.get('revenue'))
        x['_ni_prev'] = p.get('net_income') if p else None
        rows.append(x)
    t = dict(tt or {})
    bs = d.get('bs') or {}
    if t and bs.get('end') and bs.get('end') >= (t.get('end') or '')[:7]:
        for k in ('cash', 'debt', 'equity', 'assets'):
            if t.get(k) is None and bs.get(k) is not None:
                t[k] = bs[k]
    last = full[-1] if full else {}
    for k in ('dividends', 'buybacks'):
        if t and t.get(k) is None and last.get(k) == 0:
            t[k] = 0.0
    if t.get('assets') is None and last.get('fy_end') and bs.get('end') == last.get('fy_end'):
        t['assets'] = last.get('assets')
    # TTM growth vs the four quarters before (quarterly rows: [end, revenue, net income])
    q = [x for x in (d.get('quarterly') or []) if x and len(x) >= 3]
    if len(q) >= 8 and t.get('end') and q[-1][0][:7] == t['end'][:7]:
        r1, r0 = [x[1] for x in q[-4:]], [x[1] for x in q[-8:-4]]
        n1, n0 = [x[2] for x in q[-4:]], [x[2] for x in q[-8:-4]]
        if None not in r1 + r0 and t.get('revenue_growth') is None:
            t['revenue_growth'] = growth(sum(r1), sum(r0))
        if None not in n0:
            t['_ni_prev'] = sum(n0)
    elif last:
        t.setdefault('_ni_prev', None)
    eq, debt = t.get('equity'), t.get('debt')
    ni, op = t.get('net_income'), t.get('op_income')
    if t.get('roe') is None and ni is not None and eq and eq > 0:
        t['roe'] = ni / eq
    if debt is None and eq is not None and last.get('debt') is not None:
        debt = last['debt']   # latest 10-Q gave no debt line: carry the last annual figure (mostly leases)
    if t.get('roic') is None and op is not None and eq is not None and debt is not None and eq + debt > 0:
        tax, pre = t.get('tax'), t.get('pretax_income')
        tr = tax / pre if (tax is not None and pre) else None
        if tr is None or tr < 0 or tr > 0.5:
            tr = 0.21
        t['roic'] = op * (1 - tr) / (eq + debt)
    return rows, t


def ni_growth_cell(lang, x, spct):
    a, b = x.get('net_income'), x.get('_ni_prev')
    if a is None or b is None:
        return '—'
    w = sign_change(lang, a, b)
    if w:
        return mut(w)
    nw = neg_to(lang, a, b)
    if nw:
        return mut(nw)
    return spct(growth(a, b))


W = {  # 0 negative, 1 PEG without EPS growth, 2 not applicable (banks), 3 short history, 4 '%d yrs', 5 no DCF model
    'en': ['Negative', 'EPS not growing', 'n/a for banks', 'Short history', '%d yrs', 'No model (FCF < 0)', 'Negative base year', '— = not reported by the company in that period’s filing.', 'First year'],
    'es': ['Negativo', 'BPA sin crecimiento', 'No aplica a bancos', 'Historial corto', '%d años', 'Sin modelo (FCF < 0)', 'Año base negativo', '— = la empresa no publicó esta cifra en el informe de ese periodo.', 'Primer año'],
    'pt': ['Negativo', 'LPA sem crescimento', 'Não se aplica a bancos', 'Histórico curto', '%d anos', 'Sem modelo (FCL < 0)', 'Ano-base negativo', '— = a empresa não divulgou este número no relatório desse período.', 'Primeiro ano'],
    'de': ['Negativ', 'Kein EPS-Wachstum', 'Entfällt bei Banken', 'Zu kurze Historie', '%d J.', 'Kein Modell (FCF < 0)', 'Basisjahr negativ', '— = vom Unternehmen im Bericht dieses Zeitraums nicht ausgewiesen.', 'Erstes Jahr'],
    'fr': ['Négatif', 'BPA sans croissance', 'Sans objet (banque)', 'Historique court', '%d ans', 'Pas de modèle (FCF < 0)', 'Année de base négative', '— = chiffre non publié par l’entreprise dans le rapport de cette période.', 'Première année'],
    'it': ['Negativo', 'Utile per azione non in crescita', 'Non applicabile alle banche', 'Storico breve', '%d anni', 'Nessun modello (FCF < 0)', 'Anno base negativo', '— = dato non riportato dalla società nel bilancio di quel periodo.', 'Primo anno'],
    'tr': ['Negatif', 'HBK büyümüyor', 'Bankalarda uygulanmaz', 'Kısa geçmiş', '%d yıl', 'Model yok (FCF < 0)', 'Baz yıl negatif', '— = şirket bu rakamı o dönemin raporunda açıklamadı.', 'İlk yıl'],
    'ja': ['マイナス', 'EPS成長なし', '銀行は対象外', '履歴不足', '%d年', '算出不可(FCF赤字)', '基準年マイナス', '— = その期の決算書で会社が開示していない項目です。', '初年度'],
    'ko': ['마이너스', 'EPS 성장 없음', '은행은 해당 없음', '이력 부족', '%d년', '산출 불가(FCF 적자)', '기준연도 마이너스', '— = 해당 기간 보고서에서 회사가 공시하지 않은 항목입니다.', '첫 해'],
    'id': ['Negatif', 'EPS tidak tumbuh', 'Tidak berlaku untuk bank', 'Riwayat pendek', '%d thn', 'Tanpa model (FCF < 0)', 'Tahun dasar negatif', '— = perusahaan tidak melaporkan angka ini dalam laporan periode tersebut.', 'Tahun pertama'],
    'vi': ['Âm', 'EPS không tăng', 'Không áp dụng cho ngân hàng', 'Lịch sử ngắn', '%d năm', 'Không định giá (FCF âm)', 'Năm gốc âm', '— = công ty không công bố số liệu này trong báo cáo kỳ đó.', 'Năm đầu'],
    'ar': ['سالب', 'ربحية السهم لا تنمو', 'لا ينطبق على البنوك', 'تاريخ قصير', '%d سنوات', 'لا نموذج (تدفق نقدي حر سالب)', 'سنة الأساس سالبة', '— = لم تُفصح الشركة عن هذا الرقم في تقرير تلك الفترة.', 'السنة الأولى'],
}


def w(lang, i):
    return (W.get(lang) or W['en'])[i]


def _n(x):
    try:
        return None if x is None else float(x)
    except Exception:
        return None


def vcells(lang, d, gap, num, pct):
    """Valuation and growth tiles with a reason in place of a dash."""
    r, s, tt = d.get('ratios') or {}, d.get('summary') or {}, d.get('ttm') or {}
    A = d.get('annual') or []
    a = A[-1] if A else {}
    m = d.get('market') or {}
    bank = m.get('sector') in ('Finance', 'Financial Services', 'Financials') and any(
        k in (m.get('industry') or '').lower() for k in ('bank', 'insur', 'investment', 'brokers', 'finance:', 'savings'))

    def base(k):
        v = _n(tt.get(k))
        return v if v is not None else _n(a.get(k))
    neg = mut(w(lang, 0))
    loss = mut(lbl(lang, 8))
    V = {}

    def ratio(key, bk, word, dg=None):
        b = base(bk) if bk != 'equity' else _n((d.get('bs') or {}).get('equity') if (d.get('bs') or {}).get('equity') is not None else a.get('equity'))
        v = _n(r.get(key))
        if v is not None and v > 0:
            return num(v, dg) if dg else num(v)
        if b is not None and b <= 0:
            return word
        return '—'
    V['pe'] = ratio('pe', 'net_income', loss)
    fe = _n(r.get('fwd_pe'))
    e0 = _n((d.get('analyst') or {}).get('e0'))
    V['fwd_pe'] = num(fe) if fe and fe > 0 else (loss if (e0 is not None and e0 < 0) or (fe is not None and fe <= 0) else '—')
    V['pfcf'] = mut(w(lang, 2)) if bank else ratio('pfcf', 'fcf', neg)
    V['pb'] = ratio('pb', 'equity', neg)
    V['ev_ebitda'] = ratio('ev_ebitda', 'ebitda', neg)
    pg = _n(r.get('peg'))
    if pg and pg > 0:
        V['peg'] = num(pg, 2)
    elif base('net_income') is not None and base('net_income') <= 0:
        V['peg'] = loss
    else:
        eg = s.get('eps_cagr_5y') if s.get('eps_cagr_5y') is not None else s.get('ni_cagr_5y')
        b5 = _n(A[-6].get('net_income')) if len(A) >= 6 else None
        V['peg'] = mut(w(lang, 1)) if (eg is not None and eg <= 0) else (
            mut(w(lang, 6)) if (eg is None and b5 is not None and b5 <= 0) else mut(w(lang, 3)) if eg is None else '—')
    dy = _n(r.get('div_yield'))
    V['div'] = pct(dy, 2) if dy else mut(lbl(lang, 9)) if (dy == 0 or s.get('div_years') == 0) else '—'
    V['fcfy'] = mut(w(lang, 2)) if bank else pct(r.get('fcf_yield'), 1)
    f = base('fcf')
    V['gap'] = mut(w(lang, 2)) if bank else (mut(w(lang, 5)) if (f is not None and f <= 0) else '—')

    def span(keys, negk=None):
        for n, k in keys:
            v = _n(s.get(k))
            if v is not None:
                return pct(v, 1) + ('' if n == keys[0][0] else ' <span class="mut">(%s)</span>' % (w(lang, 4) % n))
        if negk:
            b = base(negk)
            if b is not None and b <= 0:
                return loss if negk == 'net_income' else neg
        # compute from the annual rows we have (needs a positive start and end)
        for n, _ in keys:
            k2 = {'rev': 'revenue', 'eps': 'eps_diluted', 'fcf': 'fcf'}[keys[0][1].split('_')[0]]
            if len(A) > n:
                x0, x1 = _n(A[-1 - n].get(k2)), _n(A[-1].get(k2))
                if x0 and x1 and x0 > 0 and x1 > 0:
                    return pct((x1 / x0) ** (1.0 / n) - 1, 1) + ('' if n == keys[0][0] else ' <span class="mut">(%s)</span>' % (w(lang, 4) % n))
        if len(A) < keys[-1][0] + 1:
            return mut(w(lang, 3))
        k2 = {'rev': 'revenue', 'eps': 'eps_diluted', 'fcf': 'fcf'}[keys[0][1].split('_')[0]]
        if any((_n(A[-1 - n].get(k2)) or 0) <= 0 for n, _ in keys if len(A) > n):
            return mut(w(lang, 6))
        return '—'
    V['rev5'] = span([(5, 'rev_cagr_5y'), (3, 'rev_cagr_3y')])
    V['eps5'] = span([(5, 'eps_cagr_5y'), (3, 'eps_cagr_3y')], 'net_income')
    V['fcf3'] = mut(w(lang, 2)) if bank else span([(3, 'fcf_cagr_3y'), (5, 'fcf_cagr_5y')], 'fcf')
    V['nm5'] = span([(5, 'net_margin_avg_5y'), (3, 'net_margin_avg_3y'), (1, 'net_margin_avg_1y')]) if False else (
        pct(s['net_margin_avg_5y'], 1) if _n(s.get('net_margin_avg_5y')) is not None else
        (pct(s['net_margin_avg_3y'], 1) + ' <span class="mut">(%s)</span>' % (w(lang, 4) % 3)) if _n(s.get('net_margin_avg_3y')) is not None else
        (pct(a['net_margin'], 1) + ' <span class="mut">(%s)</span>' % (w(lang, 4) % 1)) if _n(a.get('net_margin')) is not None else '—')
    V['roic5'] = (pct(s['roic_avg_5y'], 1) if _n(s.get('roic_avg_5y')) is not None else
                  (pct(a['roic'], 1) + ' <span class="mut">(%s)</span>' % (w(lang, 4) % 1)) if _n(a.get('roic')) is not None else
                  mut(w(lang, 2)) if bank else '—')
    dv = s.get('div_years')
    V['divy'] = str(dv) if dv else (mut(lbl(lang, 9)) if dv == 0 or dy == 0 else '—')
    v1 = _n(s.get('rev_cagr_1y'))
    if v1 is None and len(A) >= 2 and _n(A[-2].get('revenue')) and A[-2]['revenue'] > 0 and _n(A[-1].get('revenue')) is not None:
        v1 = A[-1]['revenue'] / A[-2]['revenue'] - 1
    V['rev1'] = pct(v1, 1) if v1 is not None else (mut(lbl(lang, 11)) if not base('revenue') else mut(w(lang, 3)))
    return V


def note_if_dash(lang, html):
    """Card html: add the one-line meaning of a dash when the table still has one."""
    if '<td>—</td>' not in html:
        return html
    if '</div></section>' in html:
        return html.replace('</div></section>', '</div><p class="note">%s</p></section>' % w(lang, 7), 1)
    i = html.rfind('</section>')
    return html[:i] + '<p class="note">%s</p>' % w(lang, 7) + html[i:] if i >= 0 else html
