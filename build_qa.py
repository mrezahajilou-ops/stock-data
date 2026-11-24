"""Question pages for the Farsi site (added 2026-11-24): the short questions people type into Google about one stock,
each answered on its own page with real data, then linked from the stock page and the home page.

- <t>-earnings-date        گزارش فصلی بعدی X کی است؟ + نتایج و تحلیل آخرین گزارش (largest companies with a date on the calendar)
- <t>-dividend-date        سود نقدی X کی پرداخت می‌شود؟ (dividend payers with an ex-dividend/payment date)
- <t>-why-stock-moved      چرا سهام X ریخت / بالا رفت؟ (every company with a written Farsi explanation of a 10%+ day)

Every page carries enough of its own data to stand alone; companies with too little data get no page.
Returned to build_seo_more.build(), which appends them to pages/guides.json for sync_guides.py.
"""
import json, os, glob, datetime as dt

from build_pages import fa, pct, FA_SECTOR
from build_guides import (DIS, TOOLS, TODAY, date_fa, e, nm_html, table, signed, faq_block, chips, git_json, short_usd)

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
EARN_MIN = 10e9      # earnings-date pages: companies worth $10B+
DIV_MIN = 10e9       # dividend pages: $10B+


def iso(x):
    """Name for plain text: an English name is isolated so it cannot break the right-to-left order."""
    return x.get('fa') or ('⁦%s⁩' % (x.get('en') or x['t']))


def nmh(x):
    return nm_html(x.get('fa'), x.get('en') or x['t'])


def d_fa(s):
    try:
        return date_fa(dt.date.fromisoformat(str(s)[:10]))
    except Exception:
        return ''


def ts_date(v):
    try:
        return dt.datetime.utcfromtimestamp(int(v)).date()
    except Exception:
        return None


def month_of(d):
    from build_pages import MONTHS
    part = 'اوایل' if d.day <= 10 else ('اواسط' if d.day <= 20 else 'اواخر')
    return '%s %s %s' % (part, MONTHS[d.month - 1], fa(d.year))


def money(v):
    return short_usd(v) + ' دلار' if v else '—'


def usd(v, d=2):
    return '—' if v is None else fa(('%.' + str(d) + 'f') % v) + ' دلار'


def paras(lst):
    if isinstance(lst, str):
        lst = [lst]
    return ''.join('<p>%s</p>' % e(p) for p in (lst or []) if p)


def stock_links(x, extra=()):
    t = x['t'].lower()
    return chips([('/pages/stocks/%s' % t, 'تحلیل کامل سهام ' + nmh(x))] + list(extra)
                 + [('/pages/earnings', 'تقویم گزارش‌های فصلی'), ('/pages/market-movers', 'بیشترین رشد و افت امروز')])


def page(handle, title, seo_title, seo_desc, body, qa, x, extra=()):
    from build_guides import CSS
    html = (CSS + '<div class="rzg" dir="rtl"><p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY) + body
            + (faq_block(qa) if qa else '') + '<h2>صفحه‌های مرتبط</h2>' + stock_links(x, extra) + DIS + '</div>')
    return dict(handle=handle, title=title, seo_title=seo_title[:70], seo_desc=seo_desc[:320], html=html)


# ------------------------------------------------------------------------------------------- data
def _notes(kind):
    out = {}
    base = os.path.join(ROOT, 'data', 'earnings_notes' if kind == 'earn' else 'movers', 'fa')
    for f in glob.glob(os.path.join(base, '*.json')):
        if f.endswith('index.json'):
            continue
        try:
            j = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        lst = j.get('notes' if kind == 'earn' else 'moves') or []
        if lst:
            out[j.get('t') or os.path.basename(f)[:-5]] = sorted(lst, key=lambda n: n.get('d') or '', reverse=True)
    return out


def _calendar():
    cal = (git_json('origin/calendar', 'earnings.json') or {}).get('days') or {}
    nxt = {}
    for day in sorted(cal):
        if day >= TODAY.isoformat():
            for row in cal[day]:
                nxt.setdefault(row['t'], dict(row, day=day))
    return nxt


TIME_FA = {'before': 'پیش از باز شدن بازار', 'bmo': 'پیش از باز شدن بازار', 'after': 'پس از بسته شدن بازار', 'amc': 'پس از بسته شدن بازار'}


def news_lines(t, earn, moves):
    """Short dated lines for the top of the stock page summary (build_pages imports this)."""
    out = []
    for m in (moves.get(t) or [])[:2]:
        out.append('📰 %s: %s. %s' % (d_fa(m['d']), m['headline'], m.get('summary') or ''))
    n = (earn.get(t) or [None])[0]
    if n:
        out.append('📊 آخرین گزارش فصلی (%s): %s. %s' % (d_fa(n['d']), n['headline'], n.get('takeaway') or ''))
    return out


# ------------------------------------------------------------------------------------ earnings date
def earnings_pages(U, earn, nxt):
    pages, links = [], []
    for x in sorted(U, key=lambda x: -x['mcap']):
        t = x['t']
        if x['mcap'] < EARN_MIN:
            continue
        hist = (git_json('origin/earnings', 'e/%s.json' % t) or {}).get('q') or []
        hist = [q for q in hist if q.get('act') is not None][:6]
        if len(hist) < 3 and t not in earn:
            continue
        nm = iso(x)
        n = nxt.get(t)
        est = None
        if not n:
            kd = (git_json('origin/keystats', t + '.json') or {}).get('dates') or {}
            for v in kd.get('earnings') or []:
                k = ts_date(v)
                if k and k >= TODAY:
                    if kd.get('earnings_est'):
                        est = k
                    else:
                        n = {'day': k.isoformat(), 'time': ''}
                    break
        if not n and not est and hist:
            try:
                est = dt.date.fromisoformat(hist[0]['d']) + dt.timedelta(days=91)
            except Exception:
                est = None
            if est and est <= TODAY:
                est = None
        body = ''
        if est:
            body += ('<p><b>تاریخ گزارش فصلی بعدی %s هنوز اعلام نشده؛ با توجه به فاصله‌ی گزارش‌های قبلی، احتمالاً حدود %s منتشر می‌شود.</b> '
                     'شرکت معمولاً چند هفته قبل تاریخ دقیق را اعلام می‌کند و این صفحه همان روز به‌روز می‌شود.</p>' % (nmh(x), month_of(est)))
        if n:
            dd = dt.date.fromisoformat(n['day'])
            when = TIME_FA.get(n.get('time') or '', '')
            body += ('<p><b>گزارش فصلی بعدی %s حدود %s%s منتشر می‌شود.</b> تاریخ دقیق را خود شرکت اعلام می‌کند و ممکن است چند روز جابه‌جا شود.</p>'
                     % (nmh(x), date_fa(dd), (' و ' + when) if when else ''))
            if n.get('f') is not None:
                body += '<p>میانگین پیش‌بینی تحلیلگرها برای سود هر سهم در این گزارش %s است%s.</p>' % (
                    usd(n['f']), ('، در برابر %s در همین فصل سال قبل' % usd(n['ly'])) if n.get('ly') is not None else '')
        if hist:
            last = hist[0]
            body += ('<p>در آخرین گزارش (%s) سود هر سهم %s بود، در برابر پیش‌بینی %s%s.</p>'
                     % (d_fa(last['d']), usd(last['act']), usd(last.get('f')),
                        ('؛ واکنش قیمت سهم در روز بعد %s بود' % signed(last['rx'], 1)) if last.get('rx') is not None else ''))
            rows = [[d_fa(q['d']), usd(q['act']), usd(q.get('f')),
                     signed(q['sur'] / 100.0, 1) if q.get('sur') is not None else '—',
                     money(q.get('rev')), signed(q['rx'], 1) if q.get('rx') is not None else '—'] for q in hist]
            body += '<h2>گزارش‌های فصلی اخیر %s</h2>' % nmh(x) + table(['تاریخ', 'سود هر سهم', 'پیش‌بینی', 'غافلگیری', 'درآمد', 'واکنش قیمت'], rows)
            beats = sum(1 for q in hist if q.get('f') is not None and q['act'] >= q['f'])
            withf = sum(1 for q in hist if q.get('f') is not None)
            if withf >= 3:
                body += '<p>%s در %s گزارش از %s گزارش اخیر، سودی برابر یا بیشتر از پیش‌بینی تحلیلگرها اعلام کرده است.</p>' % (nmh(x), fa(beats), fa(withf))
        note = (earn.get(t) or [None])[0]
        if note:
            body += '<h2>تحلیل آخرین گزارش: %s</h2><p><b>%s</b></p>' % (e(d_fa(note['d'])), e(note['headline']))
            body += '<p>%s</p>' % e(note.get('takeaway') or '')
            if note.get('results'):
                body += '<h3>نتایج</h3>' + paras(note['results'])
            if note.get('mgmt'):
                body += '<h3>حرف‌های مدیریت و پیش‌بینی</h3>' + paras(note['mgmt'])
            if note.get('view'):
                body += '<h3>تحلیل</h3>' + paras(note['view'])
            if note.get('watch'):
                body += '<h3>چه چیزی را دنبال کنیم؟</h3>' + paras(note['watch'])
        qa = []
        if est:
            qa.append(('گزارش فصلی بعدی %s کی است؟' % nm, 'هنوز اعلام نشده؛ احتمالاً حدود %s.' % month_of(est)))
        if n:
            qa.append(('گزارش فصلی بعدی %s کی است؟' % nm, 'حدود %s%s.' % (date_fa(dt.date.fromisoformat(n['day'])),
                       (' و ' + TIME_FA[n['time']]) if TIME_FA.get(n.get('time') or '') else '')))
        if hist:
            qa.append(('در آخرین گزارش، سود %s بیشتر از انتظار بود؟' % nm,
                       ('بله؛ ' if hist[0].get('f') is not None and hist[0]['act'] >= hist[0]['f'] else 'نه؛ ')
                       + 'سود هر سهم %s در برابر پیش‌بینی %s.' % (usd(hist[0]['act']), usd(hist[0].get('f')))))
        qa.append(('گزارش فصلی چه اهمیتی برای قیمت سهم دارد؟', 'بازار بیش از خود عدد، فاصله‌ی آن با پیش‌بینی و چشم‌انداز فصل بعد را قیمت‌گذاری می‌کند؛ '
                   'به همین دلیل گاهی سهمی با نتایج خوب هم افت می‌کند.'))
        h = '%s-earnings-date' % t.lower().replace('.', '-')
        when_s = ('حدود ' + date_fa(dt.date.fromisoformat(n['day']))) if n else (('احتمالاً ' + month_of(est)) if est else '')
        title = 'گزارش فصلی بعدی %s کی است؟%s' % (nm, (' (' + when_s + ')') if when_s else '')
        desc = ('گزارش فصلی %s: تاریخ گزارش بعدی%s، پیش‌بینی تحلیلگرها، نتایج و غافلگیری فصل‌های اخیر و واکنش قیمت سهم%s.'
                % (nm, (' ' + when_s) if n else '', ' به‌همراه تحلیل کامل آخرین گزارش' if note else ''))
        pages.append(page(h, title, 'گزارش فصلی بعدی %s | تاریخ و پیش‌بینی' % nm, desc, body, qa, x))
        links.append(('/pages/' + h, nmh(x)))
    return pages, links


# ----------------------------------------------------------------------------------------- dividend
def dividend_pages(U):
    pages, links = [], []
    for x in sorted(U, key=lambda x: -x['mcap']):
        r = x.get('r') or {}
        if x['mcap'] < DIV_MIN or not (r.get('div_yield') or 0) > 0:
            continue
        try:
            d = json.load(open(os.path.join(ROOT, 'data', 'stocks', x['t'] + '.json')))
        except Exception:
            continue
        if (d.get('reported_currency') or 'USD') != 'USD':
            continue
        a = [y for y in d.get('annual') or [] if y.get('div_per_share')][-10:]
        if len(a) < 3:
            continue
        ks = git_json('origin/keystats', x['t'] + '.json') or {}
        dts = ks.get('dates') or {}
        exd, pay = ts_date(dts.get('exdiv')), ts_date(dts.get('divpay'))
        if not exd and not pay:
            continue
        nm, t = iso(x), x['t']
        future = lambda v: v and v >= TODAY
        lead = []
        if future(exd):
            lead.append('آخرین روزی که باید سهم را داشته باشی تا سود نقدی بعدی به تو برسد، روز معاملاتی قبل از %s است (تاریخ بدون سود)' % date_fa(exd))
        elif exd:
            lead.append('تاریخ بدون سود آخرین پرداخت %s بود' % date_fa(exd))
        if future(pay):
            lead.append('پول %s به حساب سهامداران واریز می‌شود' % date_fa(pay))
        elif pay:
            lead.append('آخرین پرداخت در %s انجام شد' % date_fa(pay))
        y = r['div_yield']
        last = a[-1]
        body = '<p><b>%s.</b></p>' % '؛ '.join(lead)
        body += ('<p>بازده سود نقدی %s با قیمت فعلی حدود %s در سال است. در سال مالی %s شرکت برای هر سهم %s سود نقدی پرداخت کرد'
                 % (nmh(x), pct(y, 2), fa(last['fy']), usd(last['div_per_share'])))
        po = lambda z: (z['dividends'] / z['net_income']) if z.get('dividends') and (z.get('net_income') or 0) > 0 else None
        if po(last) is not None and po(last) < 3:
            body += ' که %s سود خالص آن سال بود' % pct(po(last))
        body += '.</p>'
        if len(a) >= 5 and a[-5]['div_per_share'] > 0:
            g = (last['div_per_share'] / a[-5]['div_per_share']) ** (1 / 4.0) - 1
            body += '<p>سود نقدی هر سهم در چهار سال گذشته سالانه حدود %s %s.</p>' % (pct(abs(g), 1), 'رشد کرده است' if g >= 0 else 'کم شده است')
        rows = [[fa(z['fy']), usd(z['div_per_share']), pct(po(z)) if po(z) is not None and po(z) < 3 else '—',
                 money(z.get('dividends'))] for z in reversed(a)]
        body += '<h2>سود نقدی %s در سال‌های اخیر</h2>' % nmh(x) + table(['سال مالی', 'سود نقدی هر سهم', 'نسبت پرداخت', 'کل پرداخت'], rows)
        body += ('<h2>تاریخ بدون سود یعنی چه؟</h2><p>برای گرفتن سود نقدی باید سهم را پیش از «تاریخ بدون سود» خریده باشی. '
                 'اگر در خود این تاریخ یا بعد از آن بخری، این دوره سود به فروشنده می‌رسد. در روز بدون سود معمولاً قیمت سهم به اندازه‌ی سود نقدی پایین‌تر باز می‌شود.</p>')
        qa = [('سود نقدی %s کی پرداخت می‌شود؟' % nm, '؛ '.join(lead) + '.'),
              ('بازده سود نقدی %s چقدر است؟' % nm, 'حدود %s در سال با قیمت فعلی.' % pct(y, 2)),
              ('برای گرفتن سود نقدی %s کی باید سهم را بخرم؟' % nm, 'پیش از تاریخ بدون سود؛ یعنی حداکثر یک روز معاملاتی قبل از آن.')]
        h = '%s-dividend-date' % t.lower().replace('.', '-')
        when = date_fa(pay) if future(pay) else (date_fa(exd) if exd else '')
        title = 'سود نقدی %s کی پرداخت می‌شود؟%s' % (nm, (' (' + when + ')') if future(pay) or future(exd) else '')
        desc = ('سود نقدی %s: تاریخ بدون سود و تاریخ پرداخت بعدی، بازده سود نقدی %s، سود هر سهم و نسبت پرداخت در ۱۰ سال اخیر.' % (nm, pct(y, 2)))
        pages.append(page(h, title, 'سود نقدی %s کی پرداخت می‌شود؟' % nm, desc, body, qa, x))
        links.append(('/pages/' + h, nmh(x)))
    return pages, links


# ------------------------------------------------------------------------------------------- moves
def why_pages(U, earn, moves):
    by = {x['t']: x for x in U}
    pages, links = [], []
    for t, lst in sorted(moves.items(), key=lambda kv: -(by.get(kv[0], {}).get('mcap') or 0)):
        x = by.get(t)
        if not x:
            continue
        m = lst[0]
        nm = iso(x)
        up = (m.get('pct') or 0) >= 0
        verb = 'بالا رفت' if up else 'ریخت'
        body = '<p><b>%s</b></p><p>%s</p>' % (e(m['headline']), e(m.get('summary') or ''))
        body += '<p>روز %s سهم %s %s و به %s رسید (قیمت قبل: %s).</p>' % (
            d_fa(m['d']), nmh(x), signed((m.get('pct') or 0) / 100.0, 1), usd(m.get('close')), usd(m.get('prev')))
        if m.get('why'):
            body += '<h2>چرا %s؟</h2>' % verb + paras(m['why'])
        if m.get('context'):
            body += '<h2>وضعیت بازار در همان روز</h2>' + paras(m['context'])
        if len(lst) > 1:
            body += '<h2>حرکت‌های بزرگ قبلی %s</h2>' % nmh(x) + ''.join(
                '<h3>%s · %s</h3><p>%s</p>' % (e(d_fa(o['d'])), signed((o.get('pct') or 0) / 100.0, 1), e(o['headline'] + '. ' + (o.get('summary') or '')))
                for o in lst[1:6])
        note = (earn.get(t) or [None])[0]
        extra = []
        if note:
            body += '<h2>آخرین گزارش فصلی</h2><p><b>%s</b></p><p>%s</p>' % (e(note['headline']), e(note.get('takeaway') or ''))
            extra.append(('/pages/%s-earnings-date' % t.lower().replace('.', '-'), 'گزارش فصلی ' + nmh(x)))
        srcs = [s for s in (m.get('src') or []) if s.get('url')]
        if srcs:
            body += '<p class="upd">منبع: %s</p>' % '، '.join('<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (e(s['url']), 'منبع ' + fa(i + 1))
                                                             for i, s in enumerate(srcs[:3]))
        qa = [('چرا سهام %s %s؟' % (nm, verb), m['headline'] + '.'),
              ('سهام %s چقدر %s؟' % (nm, 'بالا رفت' if up else 'افت کرد'), 'روز %s حدود %s.' % (d_fa(m['d']), pct(abs(m.get('pct') or 0) / 100.0, 1)))]
        h = '%s-why-stock-moved' % t.lower().replace('.', '-')
        title = 'چرا سهام %s %s؟ (%s)' % (nm, verb, d_fa(m['d']))
        desc = '%s. %s' % (m['headline'], m.get('summary') or '')
        pages.append(page(h, title, 'چرا سهام %s %s؟' % (nm, verb), desc, body, qa, x, extra))
        links.append(('/pages/' + h, 'چرا سهام %s %s؟' % (nmh(x), verb)))
    return pages, links


def build(U):
    earn, moves, nxt = _notes('earn'), _notes('move'), _calendar()
    ep, el = earnings_pages(U, earn, nxt)
    dp, dl = dividend_pages(U)
    wp, wl = why_pages(U, earn, moves)
    print('qa pages: earnings %d, dividend %d, why %d' % (len(ep), len(dp), len(wp)))
    return ep + dp + wp, {'earn': el, 'div': dl, 'why': wl}
