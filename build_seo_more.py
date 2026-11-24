"""More programmatic SEO pages (added 2026-11-18), appended to pages/guides.json by build_guides.py:

- market-movers            بیشترین رشد و افت سهام آمریکا امروز (rebuilt every day from the live-quotes branch)
- <t>-financial-history    درآمد و سود X از ۲۰۱۵ تا ۲۰۲۶ (300 largest companies, annual SEC figures + year-end prices)
- <a>-vs-<b>               X یا Y؟ مقایسه‌ی سهام (100 pairs: the largest companies of the same industry)
- all-stocks, stocks-<l>   A–Z index of every stock page (internal links for Google)
"""
import itertools, re, json, os

def _fc_link(t, label='پیش‌بینی تحلیلگرها'):
    """Link the forecast page only when it exists (forecast pages cover the larger stocks only)."""
    global _FC
    if _FC is None:
        try:
            _FC = {p['handle'] for p in json.load(open(os.path.join(os.environ.get('GITHUB_WORKSPACE', os.getcwd()), 'pages', 'forecasts.json')))}
        except Exception:
            _FC = set()
    h = t.lower().replace('.', '-') + '-forecast'
    return (' · <a href="/pages/%s">%s</a>' % (h, label)) if h in _FC else ''
_FC = None

from build_pages import fa, pct, FA_SECTOR
from build_guides import (CSS, DIS, TOOLS, TODAY, date_fa, e, nm_html, label, table, signed, faq_block, chips, git_json,
                          short_usd, score)

ANY = '<bdi dir="ltr">%s</bdi>'


def nm(x):
    return nm_html(x.get('fa'), x.get('en') or x['t'])


def plain(x):
    return x.get('fa') or x.get('en') or x['t']


def stock_a(x):
    return '<a href="/pages/stocks/%s">%s</a>' % (e(x['t'].lower()), nm(x))


def page(handle, title, seo_title, seo_desc, body, qa, related):
    html = (CSS + '<div class="rzg" dir="rtl"><p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY) + body
            + (faq_block(qa) if qa else '') + '<h2>صفحه‌ها و ابزارهای دیگر</h2>' + chips(related + TOOLS) + DIS + '</div>')
    return dict(handle=handle, title=title, seo_title=seo_title[:70], seo_desc=seo_desc[:320], html=html)


def num(v, d=1):
    return '—' if v is None else fa(('%.' + str(d) + 'f') % v)


# ------------------------------------------------------------------------------------------- market movers
def movers_page(U):
    q = (git_json('origin/quotes', 'quotes.json') or {}).get('q') or {}
    rows = []
    for x in U:
        r = q.get(x['t'])
        if not r or x['mcap'] < 2e9 or not isinstance(r[1], (int, float)):
            continue
        rows.append((r[1] / 100.0, r[0], r[3] if len(r) > 3 else None, x))
    if len(rows) < 50:
        return None
    stamp = max((r[2] or '') for r in rows)[:10]
    up = sorted(rows, key=lambda r: -r[0])[:20]
    dn = sorted(rows, key=lambda r: r[0])[:20]
    big = sorted(rows, key=lambda r: -r[3]['mcap'])[:15]
    def t(L):
        return table(['#', 'شرکت', 'تغییر', 'قیمت (دلار)', 'ارزش بازار (دلار)'],
                     [[fa(i), stock_a(x) + '<span class="tk">%s</span>' % e(x['t']), signed(c, 1), num(p, 2), short_usd(x['mcap'])]
                      for i, (c, p, _, x) in enumerate(L, 1)])
    adv = sum(1 for r in rows if r[0] > 0)
    try:
        import datetime as dt
        day = date_fa(dt.date.fromisoformat(stamp))
    except Exception:
        day = date_fa(TODAY)
    body = ('<p>کدام سهم‌های بورس آمریکا در آخرین روز معاملاتی (%s) بیشترین رشد و بیشترین افت را داشتند؟ این صفحه هر روز بعد از بسته شدن بازار خودکار به‌روز می‌شود '
            'و فقط شرکت‌های بالای ۲ میلیارد دلار ارزش بازار را نشان می‌دهد تا سهم‌های خیلی کوچک و پرنوسان فهرست را پر نکنند.</p>' % day
            + '<p>از %s شرکت بررسی‌شده، %s سهم بالا رفتند و %s سهم پایین آمدند.</p>' % (fa(len(rows)), fa(adv), fa(len(rows) - adv))
            + '<h2>بیشترین رشد امروز</h2>' + t(up) + '<h2>بیشترین افت امروز</h2>' + t(dn)
            + '<h2>بزرگ‌ترین شرکت‌ها امروز چه کردند؟</h2>' + t(big)
            + '<p>تغییر بزرگ یک روزه معمولاً دلیل مشخصی دارد: گزارش فصلی، خبر ادغام، تغییر پیش‌بینی تحلیلگرها یا خبر کلان. '
              'قبل از هر تصمیم، روی نام شرکت بزنید و تحلیل کامل آن را ببینید.</p>')
    qa = [('امروز کدام سهم آمریکا بیشترین رشد را داشت؟', 'در آخرین روز معاملاتی %s با %s بیشترین رشد را بین شرکت‌های بالای ۲ میلیارد دلار داشت.'
           % (plain(up[0][3]), pct(up[0][0], 1))),
          ('کدام سهم امروز بیشترین افت را داشت؟', '%s با %s افت.' % (plain(dn[0][3]), pct(abs(dn[0][0]), 1))),
          ('این فهرست کی به‌روز می‌شود؟', 'هر روز معاملاتی بعد از بسته شدن بازار آمریکا (حدود ساعت ۲۲ به وقت ایران/اروپا) و در ساعت معاملات هر چند دقیقه.')]
    return page('market-movers', 'بیشترین رشد و افت سهام آمریکا امروز',
                'بیشترین رشد و افت سهام آمریکا امروز | سهام آنالیز',
                'سهام آمریکا امروز: ۲۰ سهم با بیشترین رشد و ۲۰ سهم با بیشترین افت در آخرین روز معاملاتی، به‌همراه تغییر قیمت بزرگ‌ترین شرکت‌ها؛ هر روز به‌روز.',
                body, qa, [('/pages/largest-us-companies', 'بزرگ‌ترین شرکت‌های آمریکا'), ('/pages/pulse', 'نبض بازار'),
                           ('/pages/all-stocks', 'فهرست همه‌ی سهام')])


# ------------------------------------------------------------------------- dated market days (archive)
WD_FA = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
DAY_KEEP = 60     # trading days kept as pages (about three months)


def _moves_fa():
    """Farsi 'why it moved' notes by day: {day: [move, ...]} from data/movers/fa."""
    import glob
    by = {}
    for f in glob.glob(os.path.join(os.environ.get('GITHUB_WORKSPACE', os.getcwd()), 'data', 'movers', 'fa', '*.json')):
        if f.endswith('index.json'):
            continue
        try:
            for m in json.load(open(f)).get('moves') or []:
                if m.get('headline') and m.get('d'):
                    by.setdefault(m['d'], []).append(m)
        except Exception:
            pass
    return by


def sp(v, d=1):
    """Signed percent as plain text (for descriptions and FAQ answers, where HTML is not allowed)."""
    return ('+' if v >= 0 else '−') + pct(abs(v), d)


def iso(x):
    """Name for plain text (descriptions, FAQ): an English name is isolated so it cannot break the right-to-left order."""
    return x.get('fa') or ('\u2066%s\u2069' % (x.get('en') or x['t']))


def day_handle(day):
    return 'stock-market-' + day


def day_pages(U):
    """One page per trading day: /pages/stock-market-YYYY-MM-DD, from data/daily (every $2B+ company's close)."""
    import glob, datetime as dt
    root = os.path.join(os.environ.get('GITHUB_WORKSPACE', os.getcwd()), 'data', 'daily')
    days = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(root, '20*.json')))[-DAY_KEEP:]
    if not days:
        return [], []
    by_t = {x['t']: x for x in U}
    notes = _moves_fa()
    out = []
    for i, day in enumerate(days):
        try:
            d = json.load(open(os.path.join(root, day + '.json')))
        except Exception:
            continue
        rows = []
        for t, close, ch, mc in d.get('rows') or []:
            if ch is None or not mc or mc < 2e9 or t not in by_t:
                continue
            rows.append((ch, close, by_t[t], mc))
        if len(rows) < 100:
            continue
        D = dt.date.fromisoformat(day)
        dfa = '%s %s' % (WD_FA[D.weekday()], date_fa(D))
        up = sorted(rows, key=lambda r: -r[0])[:20]
        dn = sorted(rows, key=lambda r: r[0])[:20]
        big = sorted(rows, key=lambda r: -r[3])[:15]
        adv = sum(1 for r in rows if r[0] > 0)
        ten_up = sum(1 for r in rows if r[0] >= 0.10)
        ten_dn = sum(1 for r in rows if r[0] <= -0.10)
        tot0 = sum(r[3] / (1 + r[0]) for r in rows)
        tot1 = sum(r[3] for r in rows)
        mkt = tot1 / tot0 - 1 if tot0 else 0
        def t(L):
            return table(['#', 'شرکت', 'تغییر', 'قیمت (دلار)', 'ارزش بازار (دلار)'],
                         [[fa(k), stock_a(x) + '<span class="tk">%s</span>' % e(x['t']), signed(c, 1), num(p, 2), short_usd(m)]
                          for k, (c, p, x, m) in enumerate(L, 1)])
        # sector moves, weighted by market value
        sec = {}
        for c, p, x, m in rows:
            k = x.get('sector') or ''
            if not k:
                continue
            a = sec.setdefault(k, [0.0, 0.0])
            a[0] += m / (1 + c); a[1] += m
        secs = sorted(((v[1] / v[0] - 1, k) for k, v in sec.items() if v[0] > 0), reverse=True)
        lead = ('<p>در %s، ارزش مجموع %s شرکت بالای ۲ میلیارد دلار بورس آمریکا %s تغییر کرد. %s سهم بالا رفتند و %s سهم پایین آمدند؛ '
                '%s سهم بیش از ۱۰٪ رشد و %s سهم بیش از ۱۰٪ افت داشتند. بیشترین رشد را %s با %s و بیشترین افت را %s با %s داشت.</p>'
                % (dfa, fa(len(rows)), signed(mkt, 2), fa(adv), fa(len(rows) - adv), fa(ten_up), fa(ten_dn),
                   stock_a(up[0][2]), signed(up[0][0], 1), stock_a(dn[0][2]), signed(dn[0][0], 1)))
        why = ''
        ns = sorted(notes.get(day) or [], key=lambda m: -abs(m.get('pct') or 0))
        if ns:
            items = []
            for m in ns[:12]:
                x = by_t.get(m['t'])
                if not x:
                    continue
                items.append('<li><b>%s</b> (%s): %s%s</li>' % (stock_a(x), signed((m.get('pct') or 0) / 100.0, 1), e(m['headline']),
                             ('<br>' + e(m['summary'])) if m.get('summary') else ''))
            if items:
                why = '<h2>چرا این سهم‌ها تکان خوردند؟</h2><ul class="mvw">%s</ul>' % ''.join(items)
        sect = ''
        if len(secs) >= 4:
            sect = '<h2>صنعت‌ها</h2>' + table(['صنعت', 'تغییر'], [[e(FA_SECTOR.get(k, k)), signed(c, 2)] for c, k in secs])
        nav = []
        if i > 0:
            nav.append(('/pages/' + day_handle(days[i - 1]), 'روز معاملاتی قبل'))
        if i < len(days) - 1:
            nav.append(('/pages/' + day_handle(days[i + 1]), 'روز معاملاتی بعد'))
        body = (lead + why + '<h2>بیشترین رشد</h2>' + t(up) + '<h2>بیشترین افت</h2>' + t(dn) + sect
                + '<h2>بزرگ‌ترین شرکت‌ها چه کردند؟</h2>' + t(big) + (chips(nav) if nav else ''))
        qa = [('در %s کدام سهم آمریکا بیشترین رشد را داشت؟' % dfa, '%s با %s بیشترین رشد را میان شرکت‌های بالای ۲ میلیارد دلار داشت.' % (iso(up[0][2]), sp(up[0][0], 1))),
              ('کدام سهم بیشترین افت را داشت؟', '%s با %s.' % (iso(dn[0][2]), sp(dn[0][0], 1))),
              ('بازار در این روز چقدر تغییر کرد؟', 'ارزش مجموع شرکت‌های بالای ۲ میلیارد دلار %s تغییر کرد؛ %s سهم بالا و %s سهم پایین بسته شدند.' % (sp(mkt, 2), fa(adv), fa(len(rows) - adv)))]
        title = 'بورس آمریکا در %s: بیشترین رشد و افت سهام' % dfa
        pg = page(day_handle(day), title, ('بورس آمریکا %s | رشد و افت سهام' % date_fa(D)),
                  'بورس آمریکا در %s: %s با %s بیشترین رشد و %s با %s بیشترین افت را داشت. دلیل حرکت‌های بزرگ، ۲۰ سهم پررشد و ۲۰ سهم پرافت و تغییر صنعت‌ها.'
                  % (dfa, iso(up[0][2]), sp(up[0][0], 1), iso(dn[0][2]), sp(dn[0][0], 1)),
                  body, qa, [('/pages/market-movers', 'بیشترین رشد و افت امروز')])
        pg['html'] = pg['html'].replace('<p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY), '<p class="upd">روز معاملاتی: %s</p>' % dfa, 1)
        out.append(pg)
    links = [('/pages/' + day_handle(dd), date_fa(dt.date.fromisoformat(dd))) for dd in reversed(days[-10:])]
    return out, links


# ------------------------------------------------------------------------------------- financial history
def _year_end_prices(t):
    d = git_json('origin/prices', t + '.json') or {}
    w = d.get('w') or []
    out = {}
    for day, p in w:
        out[day[:4]] = p          # last weekly close of each calendar year (split-adjusted)
    return out, (w[-1][1] if w else None)


def history_pages(U, recs, n=300):
    pages, have = [], set()
    cand = [x for x in sorted(U, key=lambda x: -x['mcap']) if x['t'] in recs]
    for x in cand:
        if len(pages) >= n:
            break
        d = recs[x['t']]
        if (d.get('reported_currency') or 'USD') != 'USD':
            continue
        A = [a for a in d.get('annual') or [] if a.get('revenue')][-12:]
        if len(A) < 5:
            continue
        yp, _ = _year_end_prices(x['t'])
        rows, prev_p = [], None
        for a in A:
            y = str(a['fy'])
            p = yp.get(y)
            ret = (p / prev_p - 1) if (p and prev_p) else None
            prev_p = p or prev_p
            rows.append([fa(y), short_usd(a.get('revenue')), signed(a.get('revenue_growth'), 0) if a.get('revenue_growth') is not None else '—',
                         short_usd(a.get('net_income')), num(a.get('eps_diluted'), 2), num(a.get('div_per_share'), 2) if a.get('div_per_share') else '—',
                         num(p, 2) if p else '—'])
        a0, a1 = A[0], A[-1]
        yrs = a1['fy'] - a0['fy']
        cagr = ((a1['revenue'] / a0['revenue']) ** (1 / yrs) - 1) if yrs > 0 and a0['revenue'] > 0 and a1['revenue'] > 0 else None
        t, fan, lo, hi = x['t'], plain(x), fa(a0['fy']), fa(a1['fy'])
        head = ['سال مالی', 'درآمد (دلار)', 'رشد درآمد', 'سود خالص (دلار)', 'سود هر سهم', 'سود نقدی هر سهم', 'قیمت پایان سال']
        best = max(A, key=lambda a: a.get('net_income') or -1e30)
        txt = ['%s در سال مالی %s حدود %s دلار درآمد و %s دلار سود خالص داشت.' % (nm(x), hi, short_usd(a1['revenue']), short_usd(a1.get('net_income')))]
        if cagr is not None:
            txt.append('درآمد از %s تا %s به‌طور میانگین سالانه %s %s.' % (lo, hi, pct(abs(cagr), 1), 'رشد کرد' if cagr >= 0 else 'کاهش یافت'))
        if best.get('net_income') and best is not a1:
            txt.append('بیشترین سود این دوره مربوط به سال %s بود (%s دلار).' % (fa(best['fy']), short_usd(best['net_income'])))
        if a1.get('div_per_share'):
            txt.append('شرکت در سال آخر %s دلار سود نقدی برای هر سهم پرداخت کرد.' % num(a1['div_per_share'], 2))
        body = ('<p>%s</p>' % ' '.join(txt)
                + '<h2>درآمد، سود و سود هر سهم %s در %s سال</h2>' % (e(fan), fa(len(A)))
                + table(head, rows)
                + '<p class="upd">عددها از گزارش‌های سالانه‌ی رسمی شرکت (فرم 10-K) و به دلار آمریکاست؛ قیمت پایان سال برای تقسیم سهام تعدیل شده است.</p>'
                + '<p><a href="/pages/stocks/%s">تحلیل کامل و امتیاز %s</a>%s</p>'
                % (t.lower(), e(fan), _fc_link(t)))
        qa = [('درآمد %s در سال %s چقدر بود؟' % (fan, hi), '%s دلار.' % short_usd(a1['revenue'])),
              ('سود %s در سال %s چقدر بود؟' % (fan, hi), 'سود خالص %s دلار و سود هر سهم %s دلار.' % (short_usd(a1.get('net_income')), num(a1.get('eps_diluted'), 2)))]
        if cagr is not None:
            qa.append(('درآمد %s در %s سال اخیر چقدر رشد کرده است؟' % (fan, fa(yrs)), 'به‌طور میانگین سالانه %s.' % pct(cagr, 1)))
        pages.append(dict(_t=t, _ind=x.get('industry'), **page(
            '%s-financial-history' % t.lower().replace('.', '-'),
            'درآمد و سود %s (%s) از %s تا %s' % (fan, t, lo, hi),
            'درآمد و سود %s %s تا %s | تاریخچه مالی %s' % (fan, lo, hi, t),
            'تاریخچه‌ی مالی %s (%s): درآمد، سود خالص، سود هر سهم، سود نقدی و قیمت سهم در %s سال گذشته از %s تا %s، از گزارش‌های رسمی شرکت.'
            % (fan, t, fa(len(A)), lo, hi), body, qa,
            [('/pages/stocks/%s' % t.lower(), 'تحلیل سهام %s' % fan), ('/pages/all-stocks', 'فهرست همه‌ی سهام')])))
        have.add(t)
    return pages, have


# ----------------------------------------------------------------------------------------------- compare
def compare_pages(U, recs, n=100):
    top = [x for x in sorted(U, key=lambda x: -x['mcap']) if x['t'] in recs][:400]
    by_ind = {}
    for x in top:
        by_ind.setdefault(x.get('industry') or x.get('sector'), []).append(x)
    pairs = []
    for ind, L in by_ind.items():
        for a, b in itertools.combinations(L[:5], 2):
            pairs.append((min(a['mcap'], b['mcap']), a, b))
    pairs.sort(key=lambda p: -p[0])
    out, links = [], {}
    for _, a, b in pairs[:n]:
        ra, rb = a['r'], b['r']
        sa, sb = a['s'], b['s']
        rows = [
            ['ارزش بازار (دلار)', short_usd(a['mcap']), short_usd(b['mcap'])],
            ['امتیاز کلی از ۵', score(a['tot']), score(b['tot'])],
            ['نسبت قیمت به سود', num(ra.get('pe'), 1) if ra.get('pe') and ra['pe'] < 500 else '—', num(rb.get('pe'), 1) if rb.get('pe') and rb['pe'] < 500 else '—'],
            ['رشد سالانه‌ی درآمد ۳ ساله', pct(sa['rev_cagr_3y'], 0) if sa.get('rev_cagr_3y') is not None else '—', pct(sb['rev_cagr_3y'], 0) if sb.get('rev_cagr_3y') is not None else '—'],
            ['حاشیه‌ی سود خالص (میانگین ۳ ساله)', pct(sa['net_margin_avg_3y'], 0) if sa.get('net_margin_avg_3y') is not None else '—', pct(sb['net_margin_avg_3y'], 0) if sb.get('net_margin_avg_3y') is not None else '—'],
            ['بازده سرمایه‌ی به‌کاررفته (میانگین ۳ ساله)', pct(sa['roic_avg_3y'], 0) if sa.get('roic_avg_3y') is not None else '—', pct(sb['roic_avg_3y'], 0) if sb.get('roic_avg_3y') is not None else '—'],
            ['بازده سود نقدی', pct(ra['div_yield'], 1) if ra.get('div_yield') else '—', pct(rb['div_yield'], 1) if rb.get('div_yield') else '—'],
            ['فاصله تا ارزش ذاتی', signed(a['gap'], 0) if a['gap'] is not None else '—', signed(b['gap'], 0) if b['gap'] is not None else '—'],
        ]
        for k, l in (('value', 'امتیاز ارزش'), ('future', 'امتیاز آینده'), ('past', 'امتیاز گذشته'), ('health', 'امتیاز سلامت مالی'), ('capital', 'امتیاز بازگشت سرمایه')):
            rows.append([l, fa(a['sc'].get(k, '—')), fa(b['sc'].get(k, '—'))])
        hd = ('<div class="tw"><table><thead><tr><th>شاخص</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>'
              % (nm(a), nm(b), ''.join('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % tuple(r) for r in rows)))
        pa, pb = plain(a), plain(b)
        win = []
        def cmp(lab, va, vb, high=True):
            if va is None or vb is None or va == vb:
                return
            w = (pa if (va > vb) == high else pb)
            win.append('%s: %s' % (lab, w))
        cmp('امتیاز کلی بالاتر', a['tot'], b['tot'])
        cmp('رشد درآمد سریع‌تر', sa.get('rev_cagr_3y'), sb.get('rev_cagr_3y'))
        cmp('ارزان‌تر بر اساس نسبت قیمت به سود', ra.get('pe') if (ra.get('pe') or 0) > 0 else None, rb.get('pe') if (rb.get('pe') or 0) > 0 else None, high=False)
        cmp('سودآوری بالاتر (حاشیه‌ی سود)', sa.get('net_margin_avg_3y'), sb.get('net_margin_avg_3y'))
        cmp('بازده نقدی بیشتر', ra.get('div_yield') or 0, rb.get('div_yield') or 0)
        ind = FA_SECTOR.get(a.get('sector'), '') if FA_SECTOR else ''
        body = ('<p>%s و %s هر دو از بزرگ‌ترین شرکت‌های صنعت خود در بورس آمریکا هستند. در این صفحه عددهای اصلی دو شرکت را کنار هم گذاشته‌ایم تا ببینید '
                'کدام ارزان‌تر است، کدام سریع‌تر رشد می‌کند و کدام سودآورتر است. همه‌ی عددها هر روز از گزارش‌های رسمی و قیمت روز به‌روز می‌شوند.</p>' % (stock_a(a), stock_a(b))
                + '<h2>مقایسه‌ی %s و %s در یک نگاه</h2>' % (e(pa), e(pb)) + hd
                + ('<h2>جمع‌بندی عددها</h2><ul>%s</ul>' % ''.join('<li>%s</li>' % w for w in win) if win else '')
                + '<p>کدام بهتر است؟ جواب به هدف شما بستگی دارد: رشد، سود نقدی یا قیمت مناسب. این مقایسه توصیه‌ی خرید نیست؛ '
                  'برای جزئیات <a href="/pages/stocks/%s">تحلیل %s</a> و <a href="/pages/stocks/%s">تحلیل %s</a> را ببینید یا با <a href="/pages/compare">ابزار مقایسه</a> سهم‌های دیگر را کنار هم بگذارید.</p>'
                  % (a['t'].lower(), e(pa), b['t'].lower(), e(pb)))
        h = '%s-vs-%s' % (a['t'].lower().replace('.', '-'), b['t'].lower().replace('.', '-'))
        qa = [('%s بهتر است یا %s؟' % (pa, pb), 'از نظر عددها: ' + ('؛ '.join(win) if win else 'دو شرکت نزدیک به هم هستند') + '. انتخاب نهایی به هدف شما بستگی دارد.'),
              ('ارزش بازار %s و %s چقدر است؟' % (pa, pb), '%s حدود %s دلار و %s حدود %s دلار.' % (pa, short_usd(a['mcap']), pb, short_usd(b['mcap'])))]
        out.append(page(h, '%s یا %s؟ مقایسه‌ی سهام %s و %s' % (pa, pb, a['t'], b['t']),
                        '%s یا %s؟ مقایسه سهام %s و %s' % (pa, pb, a['t'], b['t']),
                        'مقایسه‌ی سهام %s (%s) و %s (%s): ارزش بازار، نسبت قیمت به سود، رشد درآمد، حاشیه‌ی سود، سود نقدی، ارزش ذاتی و امتیاز؛ هر روز به‌روز.'
                        % (pa, a['t'], pb, b['t']), body, qa,
                        [('/pages/stocks/%s' % a['t'].lower(), 'تحلیل %s' % pa), ('/pages/stocks/%s' % b['t'].lower(), 'تحلیل %s' % pb),
                         ('/pages/compare', 'ابزار مقایسه‌ی سهام')]))
        links.setdefault(a['t'], []).append((h, pb))
        links.setdefault(b['t'], []).append((h, pa))
    return out, links


# --------------------------------------------------------------------------------------------- A-Z index
def az_pages(U, hist, cmp_links):
    by = {}
    for x in U:
        k = x['t'][0].upper()
        by.setdefault(k if k.isalpha() else '0', []).append(x)
    letters = sorted(by)
    nav = '<div class="chips">' + ''.join('<a href="/pages/stocks-%s">%s</a>' % (l.lower(), ANY % (l if l != '0' else '0-9')) for l in letters) + '</div>'
    pages = []
    for l in letters:
        L = sorted(by[l], key=lambda x: x['t'])
        rows = []
        for x in L:
            extra = []
            if x['t'] in hist:
                extra.append('<a href="/pages/%s-financial-history">تاریخچه‌ی مالی</a>' % x['t'].lower().replace('.', '-'))
            for h, other in (cmp_links.get(x['t']) or [])[:2]:
                extra.append('<a href="/pages/%s">در برابر %s</a>' % (h, e(other)))
            rows.append('<li><a href="/pages/stocks/%s"><span class="tk">%s</span> %s</a>%s</li>'
                        % (e(x['t'].lower()), e(x['t']), nm(x), (' · ' + ' · '.join(extra)) if extra else ''))
        lab = l if l != '0' else '0-9'
        body = ('<p>فهرست همه‌ی %s سهم بورس آمریکا که نمادشان با «%s» شروع می‌شود. روی هر سهم بزنید تا تحلیل کامل فارسی، امتیاز، ارزش ذاتی و صورت‌های مالی ۱۰ ساله‌اش را ببینید.</p>'
                % (fa(len(L)), ANY % lab) + nav + '<ul class="azl">%s</ul>' % ''.join(rows))
        pages.append(page('stocks-%s' % l.lower(), 'سهام آمریکا با حرف %s' % lab, 'فهرست سهام آمریکا با حرف %s | سهام آنالیز' % lab,
                          'فهرست %s سهم بورس آمریکا با نماد شروع‌شده با %s، هر کدام با تحلیل فارسی، امتیاز و ارزش ذاتی.' % (fa(len(L)), lab),
                          body, None, [('/pages/all-stocks', 'فهرست همه‌ی سهام')]))
    big = sorted(U, key=lambda x: -x['mcap'])[:100]
    body = ('<p>سهام آنالیز برای %s سهم بورس آمریکا تحلیل فارسی دارد. حرف اول نماد سهم را انتخاب کنید یا از فهرست ۱۰۰ شرکت بزرگ پایین شروع کنید.</p>' % fa(len(U))
            + nav + '<h2>۱۰۰ شرکت بزرگ</h2><ul class="azl">%s</ul>' % ''.join(
                '<li><a href="/pages/stocks/%s"><span class="tk">%s</span> %s</a></li>' % (e(x['t'].lower()), e(x['t']), nm(x)) for x in big)
            + '<h2>صفحه‌های تازه</h2>' + chips([('/pages/market-movers', 'بیشترین رشد و افت امروز')]))
    pages.append(page('all-stocks', 'فهرست همه‌ی سهام بورس آمریکا', 'فهرست همه سهام بورس آمریکا به فارسی | سهام آنالیز',
                      'فهرست کامل %s سهم بورس آمریکا به ترتیب حروف الفبا، با تحلیل فارسی، امتیاز و ارزش ذاتی هر سهم.' % fa(len(U)), body, None, []))
    return pages


AZ_CSS = ('<style>.rzg ul.azl{list-style:none;padding:0;columns:2;column-gap:24px}.rzg ul.azl li{break-inside:avoid;padding:4px 0;border-bottom:1px solid rgba(127,127,127,.15);font-size:14px}'
          '@media(max-width:640px){.rzg ul.azl{columns:1}}</style>')


def build(U):
    import json, os, glob
    from build_guides import SRC
    recs = {}
    keep = {x['t'] for x in sorted(U, key=lambda x: -x['mcap'])[:450]}
    for t in keep:
        try:
            recs[t] = json.load(open(os.path.join(SRC, t + '.json')))
        except Exception:
            pass
    out = []
    mv = movers_page(U)
    try:
        dpages, dlinks = day_pages(U)
    except Exception as ex:
        print('day pages:', ex); dpages, dlinks = [], []
    if mv:
        if dlinks:
            mv['html'] = mv['html'].replace('<h2>صفحه‌ها و ابزارهای دیگر</h2>', '<h2>روزهای معاملاتی قبل</h2>' + chips(dlinks) + '<h2>صفحه‌ها و ابزارهای دیگر</h2>', 1)
        out.append(mv)
    out += dpages
    try:
        import build_qa
        qp, _ = build_qa.build(U)
        out += qp
    except Exception as ex:
        print('qa pages:', ex)
    hist_pages, hist = history_pages(U, recs)
    cmp_pages, cmp_links = compare_pages(U, recs)
    out += hist_pages + cmp_pages + az_pages(U, hist, cmp_links)
    for p in out:
        p.pop('_t', None); p.pop('_ind', None)
        p['html'] = AZ_CSS + p['html']
    return out
