#!/usr/bin/env python3
"""Build the question/ranking guide pages ("بهترین سهام سود نقدی آمریکا", "پورتفوی وارن بافت", ...).

They are ordinary Shopify pages (server-rendered by the theme's default page template, so Google reads
every word), rebuilt from the same data as the site after each data build and pushed by sync_guides.py.

Input:  data/stocks/*.json (build.py), branch `superinvestors` (13F data, read with git show)
Output: pages/guides.json  - [{handle, title, seo_title, seo_desc, html}]
"""
import json, os, re, glob, subprocess, datetime as dt, html as H

from build_pages import FA_NAME, FA_SECTOR, MONTHS, fa, pct, big_fa, verdict

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
SRC = os.path.join(ROOT, 'data', 'stocks')
OUT = os.path.join(ROOT, 'pages', 'guides.json')
TODAY = dt.date.today()

SECTOR_PAGES = [  # (data sector, handle, Persian name used in the title)
    ('Technology', 'best-technology-stocks', 'فناوری'),
    ('Health Care', 'best-healthcare-stocks', 'سلامت و دارو'),
    ('Finance', 'best-financial-stocks', 'مالی و بانکی'),
    ('Consumer Discretionary', 'best-consumer-discretionary-stocks', 'کالاهای مصرفی غیرضروری'),
    ('Consumer Staples', 'best-consumer-staples-stocks', 'کالاهای مصرفی ضروری'),
    ('Industrials', 'best-industrial-stocks', 'صنعتی'),
    ('Energy', 'best-energy-stocks', 'انرژی و نفت'),
    ('Real Estate', 'best-real-estate-stocks', 'املاک و مستغلات'),
    ('Utilities', 'best-utility-stocks', 'خدمات عمومی (آب و برق و گاز)'),
    ('Telecommunications', 'best-telecom-stocks', 'مخابرات'),
    ('Basic Materials', 'best-materials-stocks', 'مواد اولیه'),
]
DUP = {'GOOG': 'GOOGL', 'BRK-A': 'BRK-B'}  # second share class: keep one


def date_fa(d):
    return fa(d.day) + ' ' + MONTHS[d.month - 1] + ' ' + fa(d.year)


def e(s):
    return H.escape(str(s if s is not None else ''), quote=True)


# ---------------------------------------------------------------- data
def load():
    rows = []
    for f in glob.glob(os.path.join(SRC, '*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        m = d.get('market') or {}
        if not m.get('mcap') or not d.get('annual') or d['ticker'] in DUP:
            continue
        sc, r, s, bs = d.get('scores') or {}, d.get('ratios') or {}, d.get('summary') or {}, d.get('bs') or {}
        rows.append({
            't': d['ticker'], 'en': (d.get('name') or d['ticker']).strip().rstrip('/,').strip(), 'fa': FA_NAME.get(d['ticker']),
            'sector': m.get('sector'), 'industry': m.get('industry'), 'mcap': m['mcap'], 'price': m.get('price'),
            'tot': sc.get('total'), 'sc': sc, 'r': r, 's': s,
            'cash': bs.get('cash'), 'debt': bs.get('debt'),
            'fcf': (d.get('latest') or {}).get('fcf'),
            'gap': (r['fair_mcap'] / m['mcap'] - 1) if r.get('fair_mcap') else None,
        })
    # one row per company: drop extra share classes / preferreds that share a name with a bigger listing
    best = {}
    for x in rows:
        k = re.sub(r'[^a-z0-9]', '', x['en'].lower())
        if k not in best or x['mcap'] > best[k]['mcap']:
            best[k] = x
    return list(best.values())


def git_json(ref, path):
    try:
        out = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (ref, path)], capture_output=True, timeout=60)
        return json.loads(out.stdout) if out.returncode == 0 else None
    except Exception:
        return None


# ---------------------------------------------------------------- html pieces
CSS = '''<style>
.rzg{line-height:2}
.rzg .upd{color:#8A8F99;font-size:.9em}
.rzg .box{background:#15181F;border:1px solid #262B36;border-radius:12px;padding:14px 18px;margin:18px 0}
.rzg .tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:18px 0;border:1px solid #262B36;border-radius:12px}
.rzg table{width:100%!important;border-collapse:collapse;font-size:.92em;min-width:520px;table-layout:auto!important;margin:0!important}
.rzg th,.rzg td{width:auto!important}
.rzg td:nth-child(2){min-width:150px}
.rzg th{background:#1C2029;color:#C9A961;font-weight:700;text-align:right;padding:9px 10px;white-space:nowrap}
.rzg td{padding:8px 10px;border-top:1px solid #262B36;vertical-align:middle}
.rzg td.n{white-space:nowrap}
.rzg .tk{font-family:Inter,Arial,sans-serif;direction:ltr;unicode-bidi:isolate;color:#8A8F99;font-size:.85em;margin-right:6px}
.rzg .up{color:#4FA37A}.rzg .dn{color:#C8534F}
.rzg .sc{display:inline-block;min-width:2.4em;text-align:center;border-radius:6px;padding:0 6px;background:#1C2029;color:#C9A961;font-weight:700}
.rzg .chips a{display:inline-block;margin:4px 0 4px 8px;padding:4px 12px;border:1px solid #262B36;border-radius:999px;text-decoration:none;font-size:.9em}
.rzg .faq h3{font-size:1.05em;margin:16px 0 4px}
.rzg .dis{color:#8A8F99;font-size:.85em;margin-top:26px}
@media(max-width:700px){.rzg .hm{display:none}}
@media(max-width:600px){.rzg td:nth-child(2){min-width:0}.rzg table{min-width:0;font-size:.82em}.rzg th,.rzg td{padding:7px 6px}.rzg th{white-space:normal}.rzg td .tk{display:block;margin:0}.rzg .hm{display:none}.rzg td.n{white-space:normal}}
</style>'''


def name_cell(x):
    """Company cell: Persian name (or English) + ticker, linked to its stock page."""
    return '<a href="/pages/stocks/%s">%s</a><span class="tk">%s</span>' % (e(x['t'].lower()), nm_html(x.get('fa'), x.get('en') or x['t']), e(x['t']))


def nm_html(fa_name, en):
    """Persian name as is; an English name is isolated left-to-right so its dots and commas stay in place."""
    if fa_name:
        return e(fa_name)
    return '<bdi dir="ltr">%s</bdi>' % e(en)


def label(x):
    return '%s (<span class="tk" style="margin:0">%s</span>)' % (nm_html(x.get('fa'), x.get('en') or x['t']), e(x['t']))


def score(v):
    return '<span class="sc">%s</span>' % (fa('%.1f' % v) if v is not None else '—')


def table(head, rows):
    """Columns whose header is a market value are hidden on phones (class hm) so the table fits the screen."""
    hide = {i for i, c in enumerate(head) if c.startswith('ارزش بازار')} if len(head) > 5 else set()
    cls = lambda i: (' class="hm"' if i in hide else '')
    h = ''.join('<th%s>%s</th>' % (cls(i), c) for i, c in enumerate(head))
    b = ''.join('<tr>' + ''.join('<td class="n%s">%s</td>' % (' hm' if i in hide else '', c) if i != 1 else '<td>%s</td>' % c
                                 for i, c in enumerate(r)) + '</tr>' for r in rows)
    return '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, b)


def signed(v, d=0):
    if v is None:
        return '—'
    cls = 'up' if v >= 0 else 'dn'
    return '<span class="%s">%s%s</span>' % (cls, '+' if v >= 0 else '−', pct(abs(v), d))


def faq_block(qa):
    body = ''.join('<h3>%s</h3><p>%s</p>' % (q, a) for q, a in qa)
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qa]}
    return ('<h2>پرسش‌های رایج</h2><div class="faq">%s</div><script type="application/ld+json">%s</script>'
            % (body, json.dumps(ld, ensure_ascii=False)))


def strip(s):
    import re
    return re.sub(r'<[^>]+>', '', s)


def itemlist(name, items):
    ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': name, 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': (x.get('fa') or x['en']) + ' (' + x['t'] + ')',
         'url': 'https://sahamanaliz.com/pages/stocks/' + x['t'].lower()} for i, x in enumerate(items)]}
    return '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)


def chips(links):
    return '<div class="chips">' + ''.join('<a href="%s">%s</a>' % (u, t) for u, t in links) + '</div>'


DIS = ('<p class="dis">این صفحه هر روز بعد از بسته شدن بازار آمریکا خودکار از روی گزارش‌های رسمی شرکت‌ها (SEC) و قیمت‌های روز به‌روز می‌شود. '
       'فهرست‌ها آموزشی‌اند و توصیه‌ی خرید یا فروش نیستند؛ قبل از هر تصمیم، تحلیل کامل هر سهم را ببین.</p>')

TOOLS = [('/pages/stock', 'تحلیل سهام'), ('/pages/screener', 'غربالگر سهام'), ('/pages/dcf', 'ماشین‌حساب ارزش ذاتی'),
         ('/pages/superinvestors', 'پورتفوی سرمایه‌گذاران بزرگ'), ('/pages/guides', 'همه‌ی فهرست‌ها')]


def wrap(intro, method, tbl, notes, qa, related, extra=''):
    upd = '<p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY)
    return (CSS + '<div class="rzg" dir="rtl">' + upd + intro + ('<div class="box"><strong>روش انتخاب: </strong>%s</div>' % method if method else '')
            + tbl + notes + extra + faq_block(qa) + '<h2>فهرست‌ها و ابزارهای دیگر</h2>' + chips(related + TOOLS) + DIS + '</div>')


# ---------------------------------------------------------------- ranking pages
def top_notes(items, why):
    """A short paragraph about the first three picks, written from their numbers."""
    out = []
    for x in items[:3]:
        out.append('<p><strong>%s:</strong> %s</p>' % (label(x), why(x)))
    return ('<h2>نگاهی به سه سهم اول</h2>' + ''.join(out)) if out else ''


def growth_txt(x):
    s, r = x['s'], x['r']
    bits = []
    if s.get('rev_cagr_3y') is not None:
        bits.append('رشد سالانه‌ی درآمد در ۳ سال اخیر ' + pct(s['rev_cagr_3y']))
    if s.get('net_margin_avg_3y') is not None:
        bits.append('حاشیه سود خالص میانگین ' + pct(s['net_margin_avg_3y']))
    if r.get('pe'):
        bits.append('نسبت قیمت به سود (P/E) حدود ' + fa('%.0f' % r['pe']))
    if x['gap'] is not None:
        bits.append('ارزش ذاتی تقریباً %s %s از قیمت فعلی' % (pct(abs(x['gap'])), 'بالاتر' if x['gap'] >= 0 else 'پایین‌تر'))
    bits.append('امتیاز کلی %s از ۵ (%s)' % (fa('%.1f' % x['tot']), verdict(x['tot'])))
    return '، '.join(bits) + '.'


def related_rank(h):
    allr = [('/pages/best-dividend-stocks', 'سهام سود نقدی'), ('/pages/best-growth-stocks', 'سهام رشدی'),
            ('/pages/undervalued-stocks', 'سهام زیر ارزش ذاتی'), ('/pages/largest-us-companies', 'بزرگ‌ترین شرکت‌ها'),
            ('/pages/high-roic-stocks', 'پربازده‌ترین شرکت‌ها'), ('/pages/debt-free-stocks', 'سهام بدون بدهی'),
            ('/pages/buyback-stocks', 'سهام با بازخرید')]
    return [l for l in allr if not l[0].endswith('/' + h)]


def rank_pages(U):
    pages = []
    big = [x for x in U if x['tot'] is not None and x['mcap'] >= 10e9]  # well-known companies only

    # 1. dividends
    L = [x for x in big if x['r'].get('div_yield') and 0.025 <= x['r']['div_yield'] <= 0.12
         and (x['sc'].get('health') or 0) >= 3 and (x['s'].get('div_years') or 0) >= 5 and (x['fcf'] or 0) > 0]
    L.sort(key=lambda x: (-x['tot'], -x['mcap']))
    L = L[:25]
    rows = [[fa(i + 1), name_cell(x), pct(x['r']['div_yield'], 1), fa(x['s'].get('div_years') or 0) + ' سال',
             short_usd(x['mcap']), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='best-dividend-stocks', title='بهترین سهام سود نقدی آمریکا',
        seo_title='بهترین سهام سود نقدی آمریکا %s | فهرست سهام دیویدندی باکیفیت' % fa(TODAY.year),
        seo_desc='فهرست بهترین سهام سود نقدی (دیویدند) بورس آمریکا با بازده نقدی بالای ۲٫۵٪، سابقه‌ی پرداخت حداقل ۵ ساله و سلامت مالی خوب؛ هر روز به‌روز با داده‌ی رسمی SEC.',
        html=wrap('<p>سهام سود نقدی یعنی شرکت‌هایی که بخشی از سودشان را هر فصل یا هر سال به‌صورت نقد به سهامدار می‌دهند. '
                  'بازده نقدی بالا به‌تنهایی کافی نیست؛ شرکتی که سودش را از جیب بدهی می‌دهد دیر یا زود پرداختش را قطع می‌کند. '
                  'برای همین این فهرست فقط شرکت‌هایی را نشان می‌دهد که هم بازده نقدی خوب دارند و هم از نظر مالی سالم‌اند.</p>',
                  'سهم‌های بورس آمریکا با ارزش بازار بیش از ۱۰ میلیارد دلار، بازده نقدی بین ۲٫۵ تا ۱۲ درصد، حداقل ۵ سال پرداخت سود نقدی، جریان نقد آزاد مثبت و امتیاز سلامت مالی ۳ از ۵ یا بیشتر؛ مرتب‌شده بر اساس امتیاز کلی و بعد اندازه‌ی شرکت.',
                  table(['#', 'شرکت', 'بازده نقدی', 'سابقه‌ی پرداخت', 'ارزش بازار (دلار)', 'امتیاز'], rows),
                  top_notes(L, lambda x: 'بازده نقدی %s، %s سال پیاپی پرداخت سود نقدی و ' % (pct(x['r']['div_yield'], 1), fa(x['s'].get('div_years') or 0)) + growth_txt(x)),
                  [('بازده نقدی (Dividend Yield) یعنی چه؟', 'سود نقدی سالانه‌ی هر سهم تقسیم بر قیمت سهم. مثلاً بازده ۳٪ یعنی با ۱۰۰۰ دلار خرید، سالی حدود ۳۰ دلار سود نقدی می‌گیری.'),
                   ('چرا سهم‌هایی با بازده خیلی بالا در فهرست نیستند؟', 'بازده بالای ۱۲٪ معمولاً یعنی قیمت سهم به خاطر مشکلی جدی ریخته و بازار انتظار دارد سود نقدی کم یا قطع شود. این‌ها را عمداً کنار گذاشتیم.'),
                   ('سود نقدی سهام آمریکا برای ایرانی‌ها چطور پرداخت می‌شود؟', 'سود نقدی به حساب کارگزاری‌ات واریز می‌شود و بسته به کشور محل سکونتت ممکن است بخشی از آن به‌عنوان مالیات آمریکا کسر شود.'),
                   ('این فهرست چند وقت یک بار عوض می‌شود؟', 'هر روز بعد از بسته شدن بازار آمریکا با قیمت‌ها و گزارش‌های جدید دوباره ساخته می‌شود.')],
                  related_rank('best-dividend-stocks')) + itemlist('بهترین سهام سود نقدی آمریکا', L)))

    # 2. growth
    L = [x for x in big if  (x['s'].get('rev_cagr_3y') or 0) >= 0.15 and (x['s'].get('rev_cagr_1y') or 0) >= 0.10
         and (x['sc'].get('future') or 0) >= 4]
    L.sort(key=lambda x: (-x['tot'], -x['mcap']))
    L = L[:25]
    rows = [[fa(i + 1), name_cell(x), pct(x['s'].get('rev_cagr_3y')), pct(x['s'].get('rev_cagr_1y')),
             pct(x['s'].get('net_margin_avg_1y')), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='best-growth-stocks', title='بهترین سهام رشدی آمریکا',
        seo_title='بهترین سهام رشدی آمریکا %s | شرکت‌هایی با سریع‌ترین رشد درآمد' % fa(TODAY.year),
        seo_desc='فهرست سهام رشدی بورس آمریکا: شرکت‌های بزرگ با رشد سالانه‌ی درآمد بیش از ۱۵٪ در ۳ سال اخیر و چشم‌انداز قوی؛ با امتیاز، حاشیه سود و لینک تحلیل کامل هر سهم.',
        html=wrap('<p>سهام رشدی شرکت‌هایی هستند که درآمدشان خیلی سریع‌تر از اقتصاد بزرگ می‌شود. بیشتر بازدهی‌های بزرگ بازار آمریکا از همین شرکت‌ها آمده، '
                  'ولی رشد بدون سودآوری و بدون قیمت منطقی می‌تواند خطرناک باشد. این فهرست رشد واقعی درآمد را کنار امتیاز کلی هر شرکت نشان می‌دهد.</p>',
                  'شرکت‌های بالای ۱۰ میلیارد دلار ارزش بازار با رشد سالانه‌ی درآمد حداقل ۱۵٪ در ۳ سال اخیر، رشد حداقل ۱۰٪ در سال آخر و امتیاز «آینده» ۴ از ۵ یا بیشتر؛ مرتب‌شده بر اساس امتیاز کلی و بعد اندازه‌ی شرکت.',
                  table(['#', 'شرکت', 'رشد درآمد ۳ ساله', 'رشد سال آخر', 'حاشیه سود', 'امتیاز'], rows),
                  top_notes(L, growth_txt),
                  [('سهام رشدی با سهام ارزشی چه فرقی دارد؟', 'سهام رشدی را برای رشد سریع سود در آینده می‌خرند و معمولاً گران‌تر معامله می‌شوند؛ سهام ارزشی را چون ارزان‌تر از ارزش واقعی‌شان هستند.'),
                   ('رشد درآمد ۳ ساله چطور حساب می‌شود؟', 'نرخ رشد مرکب سالانه (CAGR) درآمد از سه سال مالی پیش تا آخرین سال مالی، از روی گزارش‌های رسمی شرکت به SEC.'),
                   ('ریسک سهام رشدی چیست؟', 'اگر رشد کند شود، قیمت این سهم‌ها معمولاً خیلی بیشتر از بقیه افت می‌کند. برای همین P/E و ارزش ذاتی را هم در صفحه‌ی هر سهم چک کن.')],
                  related_rank('best-growth-stocks')) + itemlist('بهترین سهام رشدی آمریکا', L)))

    # 3. undervalued quality
    L = [x for x in big if x['gap'] is not None and 0.2 <= x['gap'] <= 3 and x['tot'] >= 3.5 and (x['sc'].get('health') or 0) >= 3]
    L.sort(key=lambda x: (-x['tot'], -x['mcap']))
    L = L[:25]
    rows = [[fa(i + 1), name_cell(x), signed(x['gap']), fa('%.1f' % x['r']['pe']) if x['r'].get('pe') else '—',
             short_usd(x['mcap']), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='undervalued-stocks', title='سهام باکیفیت آمریکا زیر ارزش ذاتی',
        seo_title='سهام ارزان آمریکا %s | سهام باکیفیت زیر ارزش ذاتی (DCF)' % fa(TODAY.year),
        seo_desc='کدام سهام آمریکایی باکیفیت ارزان‌اند؟ فهرست شرکت‌هایی که قیمتشان حداقل ۲۰٪ زیر ارزش ذاتی محاسبه‌شده با DCF است و امتیاز کیفیت بالایی دارند؛ به‌روز روزانه.',
        html=wrap('<p>سهم ارزان یعنی سهمی که قیمتش پایین‌تر از ارزش واقعی کسب‌وکارش است، نه سهمی که قیمتش افت کرده. '
                  'ارزش ذاتی را با مدل جریان نقد تنزیل‌شده (DCF) و فرض‌های متوسط برای همه‌ی سهم‌ها حساب می‌کنیم. '
                  'سهم ارزانِ بی‌کیفیت معمولاً ارزان می‌ماند، برای همین فقط شرکت‌هایی آمده‌اند که امتیاز کیفیتشان هم بالاست.</p>',
                  'شرکت‌های بالای ۱۰ میلیارد دلار ارزش بازار که ارزش ذاتی‌شان (DCF با فرض متوسط) حداقل ۲۰٪ بالاتر از قیمت فعلی است، امتیاز کلی ۳٫۵ از ۵ یا بیشتر و امتیاز سلامت مالی ۳ یا بیشتر دارند.',
                  table(['#', 'شرکت', 'فاصله تا ارزش ذاتی', 'P/E', 'ارزش بازار (دلار)', 'امتیاز'], rows),
                  top_notes(L, growth_txt),
                  [('ارزش ذاتی سهم چیست؟', 'ارزش امروزِ همه‌ی پولی که کسب‌وکار در آینده تولید می‌کند. اگر قیمت سهم کمتر از آن باشد، سهم ارزان حساب می‌شود.'),
                   ('آیا محاسبه‌ی DCF دقیق است؟', 'نه؛ نتیجه به فرض‌های رشد و نرخ تنزیل حساس است. با ماشین‌حساب ارزش ذاتی سایت می‌توانی فرض‌ها را عوض کنی و نتیجه را ببینی.'),
                   ('چرا یک سهم ممکن است ارزان بماند؟', 'گاهی بازار ریسکی را می‌بیند که در اعداد گذشته نیست، مثل رقیب جدید یا قانون تازه. همیشه بخش ریسک‌ها را در صفحه‌ی هر سهم بخوان.')],
                  related_rank('undervalued-stocks')) + itemlist('سهام باکیفیت زیر ارزش ذاتی', L)))

    # 4. largest companies
    L = sorted(U, key=lambda x: -x['mcap'])[:30]
    rows = [[fa(i + 1), name_cell(x), short_usd(x['mcap']), FA_SECTOR.get(x['sector'] or '', x['sector'] or '—'), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='largest-us-companies', title='بزرگ‌ترین شرکت‌های بورس آمریکا بر اساس ارزش بازار',
        seo_title='بزرگ‌ترین شرکت‌های آمریکا %s | ۳۰ شرکت بزرگ بورس آمریکا از نظر ارزش بازار' % fa(TODAY.year),
        seo_desc='فهرست به‌روز ۳۰ شرکت بزرگ بورس آمریکا بر اساس ارزش بازار، همراه با صنعت و امتیاز تحلیلی هر شرکت؛ اپل، مایکروسافت، انویدیا و بقیه.',
        html=wrap('<p>ارزش بازار یعنی قیمت هر سهم ضرب در تعداد کل سهام شرکت؛ به زبان ساده، قیمتی که بازار برای کل شرکت تعیین کرده. '
                  'این فهرست هر روز با قیمت‌های بسته شدن بازار دوباره مرتب می‌شود.</p>',
                  '', table(['#', 'شرکت', 'ارزش بازار (دلار)', 'صنعت', 'امتیاز'], rows),
                  '<p>اولین شرکت فهرست امروز %s با ارزش بازار %s است.</p>' % (label(L[0]), big_fa(L[0]['mcap'])),
                  [('بزرگ‌ترین شرکت آمریکا کدام است؟', 'امروز %s با ارزش بازار حدود %s.' % (strip(label(L[0])), big_fa(L[0]['mcap']))),
                   ('ارزش بازار با درآمد شرکت چه فرقی دارد؟', 'درآمد پولی است که شرکت در یک سال از فروش به دست می‌آورد؛ ارزش بازار قیمتی است که بازار برای کل شرکت می‌پردازد.'),
                   ('آیا بزرگ‌ترین شرکت‌ها بهترین سرمایه‌گذاری‌اند؟', 'لزوماً نه. بزرگی یعنی ثبات بیشتر، ولی امتیاز و ارزش‌گذاری هر شرکت را جداگانه ببین.')],
                  related_rank('largest-us-companies')) + itemlist('بزرگ‌ترین شرکت‌های آمریکا', L)))

    # 5. high ROIC
    L = [x for x in big if  0.2 <= (x['s'].get('roic_avg_5y') or 0) <= 2 and (x['s'].get('profit_years') or 0) >= 5]
    L.sort(key=lambda x: (-x['tot'], -x['mcap']))
    L = L[:25]
    rows = [[fa(i + 1), name_cell(x), pct(x['s']['roic_avg_5y']), pct(x['s'].get('net_margin_avg_5y')), short_usd(x['mcap']), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='high-roic-stocks', title='پربازده‌ترین شرکت‌های آمریکا (بالاترین ROIC)',
        seo_title='سهام با بالاترین بازده سرمایه (ROIC) در آمریکا %s | شرکت‌های فوق سودآور' % fa(TODAY.year),
        seo_desc='شرکت‌های آمریکایی که با هر دلار سرمایه بیشترین سود را می‌سازند: میانگین ROIC پنج‌ساله بالای ۲۰٪، پنج سال پیاپی سودده؛ نشانه‌ی مزیت رقابتی پایدار.',
        html=wrap('<p>بازده سرمایه‌ی به‌کاررفته (ROIC) نشان می‌دهد شرکت با هر ۱۰۰ دلاری که در کسب‌وکارش گذاشته چقدر سود عملیاتی می‌سازد. '
                  'شرکت‌هایی که سال‌ها ROIC بالای ۲۰٪ دارند معمولاً مزیت رقابتی جدی دارند؛ همان چیزی که وارن بافت به آن «خندق» می‌گوید.</p>',
                  'شرکت‌های بالای ۱۰ میلیارد دلار ارزش بازار با میانگین ROIC پنج‌ساله‌ی بالای ۲۰٪ و حداقل ۵ سال سودده؛ مرتب‌شده بر اساس امتیاز کلی و بعد اندازه‌ی شرکت.',
                  table(['#', 'شرکت', 'ROIC میانگین ۵ ساله', 'حاشیه سود', 'ارزش بازار (دلار)', 'امتیاز'], rows),
                  top_notes(L, lambda x: 'میانگین ROIC پنج‌ساله %s؛ ' % pct(x['s']['roic_avg_5y']) + growth_txt(x)),
                  [('ROIC خوب چقدر است؟', 'بالای ۱۰ تا ۱۲ درصد معمولاً یعنی شرکت بیشتر از هزینه‌ی سرمایه‌اش سود می‌سازد؛ بالای ۲۰٪ عالی است.'),
                   ('فرق ROIC با ROE چیست؟', 'ROE فقط سرمایه‌ی سهامداران را حساب می‌کند و با بدهی زیاد بالا می‌رود؛ ROIC بدهی را هم در نظر می‌گیرد و تصویر واقعی‌تری می‌دهد.'),
                   ('چرا ROIC برای سرمایه‌گذار بلندمدت مهم است؟', 'شرکتی که سودش را با بازده بالا دوباره سرمایه‌گذاری می‌کند، ارزشش در طول زمان مرکب رشد می‌کند.')],
                  related_rank('high-roic-stocks')) + itemlist('پربازده‌ترین شرکت‌های آمریکا', L)))

    # 6. net cash
    L = [x for x in big if x['cash'] is not None and x['debt'] is not None and x['cash'] > x['debt'] and (x['fcf'] or 0) > 0 and x['tot'] >= 3.5]
    L.sort(key=lambda x: (-x['tot'], -x['mcap']))
    L = L[:25]
    rows = [[fa(i + 1), name_cell(x), short_usd(x['cash'] - x['debt']), short_usd(x['fcf']), short_usd(x['mcap']), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='debt-free-stocks', title='سهام آمریکایی بدون بدهی (نقد بیشتر از بدهی)',
        seo_title='سهام بدون بدهی آمریکا %s | شرکت‌هایی با نقدینگی بیشتر از بدهی' % fa(TODAY.year),
        seo_desc='فهرست شرکت‌های باکیفیت آمریکایی که پول نقدشان از کل بدهی‌شان بیشتر است و جریان نقد آزاد مثبت دارند؛ کم‌ریسک‌ترین ترازنامه‌ها در بورس آمریکا.',
        html=wrap('<p>شرکتی که نقدش از بدهی‌اش بیشتر است در رکود و دوره‌ی نرخ بهره‌ی بالا مجبور نیست سهام جدید بفروشد یا وام گران بگیرد. '
                  'این فهرست شرکت‌های باکیفیتی را نشان می‌دهد که «نقد خالص» دارند.</p>',
                  'شرکت‌های بالای ۱۰ میلیارد دلار ارزش بازار که پول نقد و سرمایه‌گذاری کوتاه‌مدتشان از کل بدهی بیشتر است، جریان نقد آزاد مثبت و امتیاز کلی ۳٫۵ یا بیشتر دارند.',
                  table(['#', 'شرکت', 'نقد خالص (دلار)', 'جریان نقد آزاد (دلار)', 'ارزش بازار (دلار)', 'امتیاز'], rows),
                  top_notes(L, lambda x: 'نقد خالص %s؛ ' % big_fa(x['cash'] - x['debt']) + growth_txt(x)),
                  [('نقد خالص یعنی چه؟', 'پول نقد و معادل‌های نقدی شرکت منهای کل بدهی‌های مالی‌اش. مثبت بودنش یعنی شرکت می‌تواند همه‌ی بدهی‌اش را همین امروز بپردازد.'),
                   ('آیا بدهی همیشه بد است؟', 'نه؛ بدهی ارزان می‌تواند رشد را سریع‌تر کند. ولی شرکت بدون بدهی در بحران‌ها انعطاف بیشتری دارد.')],
                  related_rank('debt-free-stocks')) + itemlist('سهام بدون بدهی آمریکا', L)))

    # 7. buybacks
    L = [x for x in big if  (x['s'].get('sh_cagr_3y') or 0) <= -0.02 and (x['r'].get('buyback_yield') or 0) >= 0.02 and x['tot'] >= 3]
    L.sort(key=lambda x: (-x['tot'], -x['mcap']))
    L = L[:25]
    rows = [[fa(i + 1), name_cell(x), signed(x['s']['sh_cagr_3y'], 1), pct(x['r']['buyback_yield'], 1), short_usd(x['mcap']), score(x['tot'])] for i, x in enumerate(L)]
    pages.append(dict(
        handle='buyback-stocks', title='سهام آمریکایی با بیشترین بازخرید سهام',
        seo_title='شرکت‌هایی که سهام خود را بازخرید می‌کنند %s | بازخرید سهام در آمریکا' % fa(TODAY.year),
        seo_desc='فهرست شرکت‌های آمریکایی که با بازخرید سهام تعداد سهامشان را هر سال کم می‌کنند؛ با نرخ کاهش سهام، بازده بازخرید و امتیاز تحلیلی هر شرکت.',
        html=wrap('<p>وقتی شرکت سهام خودش را از بازار می‌خرد، تعداد سهام کم می‌شود و سهم هر سهامدار از سود بیشتر می‌شود؛ مثل سود نقدی، ولی بدون مالیات فوری. '
                  'این فهرست شرکت‌هایی را نشان می‌دهد که واقعاً تعداد سهامشان را کم کرده‌اند، نه فقط اعلام برنامه کرده‌اند.</p>',
                  'شرکت‌های بالای ۱۰ میلیارد دلار ارزش بازار که تعداد سهامشان در ۳ سال اخیر سالانه حداقل ۲٪ کم شده، بازده بازخرید سال اخیرشان حداقل ۲٪ است و امتیاز کلی ۳ یا بیشتر دارند.',
                  table(['#', 'شرکت', 'تغییر سالانه‌ی تعداد سهام', 'بازده بازخرید', 'ارزش بازار (دلار)', 'امتیاز'], rows),
                  top_notes(L, lambda x: 'تعداد سهام سالانه %s کم شده؛ ' % pct(abs(x['s']['sh_cagr_3y']), 1) + growth_txt(x)),
                  [('بازخرید سهام به نفع سهامدار است؟', 'اگر شرکت سهامش را ارزان‌تر از ارزش ذاتی بخرد بله؛ بازخرید با قیمت خیلی بالا ارزش سهامداران را از بین می‌برد.'),
                   ('بازده بازخرید چیست؟', 'مبلغ بازخرید سهام در یک سال تقسیم بر ارزش بازار شرکت.')],
                  related_rank('buyback-stocks')) + itemlist('شرکت‌های با بیشترین بازخرید سهام', L)))
    return pages


def sector_pages(U):
    pages = []
    others = [('/pages/' + h, 'سهام ' + n) for _, h, n in SECTOR_PAGES]
    for sec, h, nfa in SECTOR_PAGES:
        L = [x for x in U if x['sector'] == sec and x['tot'] is not None and x['mcap'] >= 10e9]
        floor = 'ده'
        if len(L) < 12:
            L = [x for x in U if x['sector'] == sec and x['tot'] is not None and x['mcap'] >= 2e9]
            floor = 'دو'
        L.sort(key=lambda x: (-x['tot'], -x['mcap']))
        n_all = len([x for x in U if x['sector'] == sec])
        L = L[:20]
        if len(L) < 5:
            continue
        rows = [[fa(i + 1), name_cell(x), short_usd(x['mcap']), signed(x['gap']) if x['gap'] is not None else '—',
                 pct(x['r']['div_yield'], 1) if x['r'].get('div_yield') else '—', score(x['tot'])] for i, x in enumerate(L)]
        biggest = max((x for x in U if x['sector'] == sec), key=lambda x: x['mcap'])
        pages.append(dict(
            handle=h, title='بهترین سهام %s آمریکا' % nfa,
            seo_title='بهترین سهام %s آمریکا %s | ۲۰ سهم برتر بر اساس امتیاز تحلیلی' % (nfa, fa(TODAY.year)),
            seo_desc='۲۰ سهم برتر بخش %s بورس آمریکا بر اساس امتیاز ۰ تا ۵ در ارزش، رشد، کارنامه، سلامت مالی و بازگشت سرمایه؛ با ارزش ذاتی و سود نقدی، به‌روز روزانه.' % nfa,
            html=wrap('<p>بخش %s در سایت %s سهم بورس آمریکا دارد. بزرگ‌ترین شرکت این بخش %s با ارزش بازار %s است. '
                      'جدول زیر ۲۰ سهم این بخش را که بالاترین امتیاز تحلیلی را دارند نشان می‌دهد.</p>' % (nfa, fa(n_all), label(biggest), big_fa(biggest['mcap'])),
                      'سهم‌های بخش %s با ارزش بازار بیش از ۱۰ میلیارد دلار، مرتب‌شده بر اساس امتیاز کلی ۰ تا ۵ (میانگین پنج بخش ارزش، آینده، گذشته، سلامت مالی و بازگشت سرمایه) و بعد ارزش بازار.' % nfa,
                      table(['#', 'شرکت', 'ارزش بازار (دلار)', 'فاصله تا ارزش ذاتی', 'سود نقدی', 'امتیاز'], rows),
                      top_notes(L, growth_txt),
                      [('بهترین سهم %s آمریکا کدام است؟' % nfa, 'بر اساس امتیاز تحلیلی امروز، %s با امتیاز %s از ۵ در صدر این بخش است. این فقط یک معیار است و جای تحلیل کامل را نمی‌گیرد.' % (strip(label(L[0])), fa('%.1f' % L[0]['tot']))),
                       ('امتیاز ۰ تا ۵ چطور حساب می‌شود؟', 'هر سهم در پنج بخش (ارزش، آینده، گذشته، سلامت مالی، بازگشت سرمایه) پنج آزمون عددی دارد؛ امتیاز کل میانگین این پنج بخش است.'),
                       ('چند سهم %s در بورس آمریکا هست؟' % nfa, 'در داده‌های سایت %s سهم در این بخش وجود دارد که برای هر کدام صفحه‌ی تحلیل جدا داریم.' % fa(n_all))],
                      [l for l in others if not l[0].endswith(h)][:6] + related_rank('')[:3]) + itemlist('بهترین سهام %s آمریکا' % nfa, L)))
    return pages


# ---------------------------------------------------------------- superinvestors
ACT = {'new': ('<span class="up">خرید جدید</span>'), 'add': '<span class="up">افزایش</span>', 'cut': '<span class="dn">کاهش</span>'}


def q_fa(p):
    """'2026-06-30' -> 'فصل دوم ۲۰۲۶'."""
    try:
        y, m = p.split('-')[:2]
        return 'فصل %s %s' % (['اول', 'دوم', 'سوم', 'چهارم'][(int(m) - 1) // 3], fa(int(y)))
    except Exception:
        return p


def short_usd(v):
    """Compact money for table cells (the column header says it is dollars)."""
    if v is None:
        return '—'
    a = abs(v)
    if a >= 1e12:
        return fa('%.1f' % (v / 1e12)) + ' هزار میلیارد'
    if a >= 1e9:
        return fa('%.1f' % (v / 1e9)) + ' میلیارد'
    return fa('%.0f' % (v / 1e6)) + ' میلیون'


def guru_pages(have_page, names):
    idx = git_json(os.environ.get('SI_REF', 'origin/superinvestors'), 'index.json')
    if not idx:
        print('superinvestors data not found - skipping those pages')
        return []
    pages, mans = [], idx.get('managers') or []

    def tk(t, n, fa_n=None):
        t = DUP.get(t, t)
        f2, en2 = names.get(t, (None, None))
        nm = nm_html(fa_n or FA_NAME.get(t) or f2, en2 or n or t)
        if t and t.lower() in have_page:
            return '<a href="/pages/stocks/%s">%s</a><span class="tk">%s</span>' % (e(t.lower()), nm, e(t))
        return '%s<span class="tk">%s</span>' % (nm, e(t or ''))

    links = [('/pages/portfolio-' + m['id'], m['fa']) for m in mans[:12]]
    for m in mans:
        d = git_json(os.environ.get('SI_REF', 'origin/superinvestors'), 'm/%s.json' % m['id']) or m
        hold = d.get('hold') or []
        if not hold:
            continue
        rows = []
        for i, x in enumerate(hold[:40]):
            ch = ACT.get(x.get('a') or '', '—')
            if x.get('a') in ('add', 'cut') and x.get('c'):
                ch += ' ' + signed(x['c'])
            rows.append([fa(i + 1), tk(x.get('t'), x.get('n')), pct(x.get('w'), 1), short_usd(x.get('v')), ch])
        sold = d.get('sold') or []
        sold_html = ''
        if sold:
            sold_html = '<h2>سهم‌هایی که کامل فروخت</h2><p>' + '، '.join(tk(x.get('t'), x.get('n')) for x in sold[:15]) + '</p>'
        top3 = '، '.join(tk(x.get('t'), x.get('n')) for x in hold[:3])
        q = q_fa(d.get('period', ''))
        name = '%s (%s)' % (d['fa'], d['ffa']) if d.get('ffa') and d['ffa'] != d['fa'] else d['fa']
        intro = ('<p><strong>%s</strong> — %s</p><p>طبق آخرین گزارش 13F که %s به کمیسیون بورس آمریکا داده (%s، ثبت‌شده در %s)، ارزش پورتفوی سهام آمریکایی‌اش حدود %s است و در %s سهم سرمایه‌گذاری کرده. '
                 'بزرگ‌ترین سهم‌هایش %s هستند و ۱۰ سهم اول %s کل پورتفو را تشکیل می‌دهند.</p>'
                 % (e(name), e(d.get('bio', '')), e(d['ffa'] or d['fa']), q, date_fa(dt.date.fromisoformat(d['filed'])) if d.get('filed') else '—',
                    big_fa(d.get('value')), fa(d.get('n', len(hold))), top3, pct(d.get('top10'))))
        moves = ('<div class="box">تغییرات این فصل: %s خرید جدید، %s افزایش، %s کاهش و %s فروش کامل.</div>'
                 % (fa(d.get('nnew', 0)), fa(d.get('nadd', 0)), fa(d.get('ncut', 0)), fa(d.get('nsold', 0))))
        pages.append(dict(
            handle='portfolio-' + d['id'], title='پورتفوی %s' % d['fa'],
            seo_title=('پورتفوی %s %s | سهام‌ها و خرید و فروش %s' % (d['fa'], fa(TODAY.year), d['ffa'] or d['fa']))[:70],
            seo_desc=('پورتفوی به‌روز %s (%s) از روی گزارش 13F %s: %s سهم، بزرگ‌ترین‌ها %s؛ خریدها، فروش‌ها و وزن هر سهم به فارسی.'
                      % (d['fa'], d['who'], q, fa(d.get('n', len(hold))), strip(top3)))[:300],
            html=wrap(intro + moves, '', table(['#', 'سهم', 'وزن', 'ارزش (دلار)', 'تغییر این فصل'], rows), sold_html,
                      [('%s الان چه سهامی دارد؟' % d['fa'], 'طبق آخرین گزارش 13F (%s) بزرگ‌ترین سهم‌هایش %s هستند. فهرست کامل در جدول بالاست.' % (q, strip(top3))),
                       ('گزارش 13F چیست؟', 'صندوق‌های آمریکایی با بیش از ۱۰۰ میلیون دلار سهام باید هر فصل حداکثر ۴۵ روز بعد از پایان فصل فهرست سهامشان را به کمیسیون بورس آمریکا (SEC) بدهند.'),
                       ('چرا داده‌ها با تأخیر است؟', 'گزارش 13F تا ۴۵ روز بعد از پایان هر فصل منتشر می‌شود، پس ممکن است مدیر صندوق از آن موقع تا حالا تغییراتی داده باشد.'),
                       ('آیا کپی کردن پورتفوی %s کار درستی است؟' % d['fa'], 'دانستن اینکه سرمایه‌گذاران بزرگ چه می‌خرند ایده‌ی خوبی برای تحقیق است، ولی به خاطر تأخیر گزارش و تفاوت هدف‌ها، کپی کورکورانه توصیه نمی‌شود.')],
                      [l for l in links if l[0] != '/pages/portfolio-' + d['id']][:8] + [('/pages/superinvestors-portfolios', 'محبوب‌ترین سهم‌های سرمایه‌گذاران بزرگ')])))

    # hub: what the legends own and buy
    pop = idx.get('popular') or []
    rows = [[fa(i + 1), tk(x['t'], x.get('n')), fa(x.get('k', 0)) + ' نفر'] for i, x in enumerate(pop[:25])]
    buys = idx.get('buys') or []
    brow = [[fa(i + 1), tk(x['t'], x.get('n')), fa(x.get('k', 0)) + ' نفر', fa(x.get('new', 0))] for i, x in enumerate(buys[:15])]
    q = q_fa(idx.get('latest') or (mans[0].get('period') if mans else ''))
    mlist = '<div class="chips">' + ''.join('<a href="/pages/portfolio-%s">%s</a>' % (m['id'], e(m['fa'])) for m in mans) + '</div>'
    pages.append(dict(
        handle='superinvestors-portfolios', title='سرمایه‌گذاران بزرگ دنیا چه سهامی دارند؟',
        seo_title='پورتفوی سرمایه‌گذاران بزرگ %s | محبوب‌ترین سهام وارن بافت و مدیران صندوق' % fa(TODAY.year),
        seo_desc='محبوب‌ترین سهم‌ها و بیشترین خریدهای %s نفر از سرمایه‌گذاران افسانه‌ای مثل وارن بافت، بیل اکمن و سث کلارمن از روی گزارش‌های 13F؛ به فارسی و به‌روز.' % fa(len(mans)),
        html=wrap('<p>هر فصل صندوق‌های بزرگ آمریکایی فهرست سهامشان را در گزارش 13F منتشر می‌کنند. ما پورتفوی %s نفر از شناخته‌شده‌ترین سرمایه‌گذاران دنیا را دنبال می‌کنیم. '
                  'آخرین داده‌ها مربوط به %s است.</p>' % (fa(len(mans)), q), '',
                  '<h2>سهم‌هایی که بیشترین سرمایه‌گذار بزرگ دارند</h2>' + table(['#', 'سهم', 'تعداد سرمایه‌گذار'], rows)
                  + '<h2>بیشترین خریدهای فصل اخیر</h2>' + table(['#', 'سهم', 'تعداد خریدار', 'خرید جدید'], brow),
                  '<h2>پورتفوی هر سرمایه‌گذار</h2>' + mlist,
                  [('محبوب‌ترین سهم بین سرمایه‌گذاران بزرگ کدام است؟', 'در %s، %s با %s سرمایه‌گذار بزرگ در صدر است.' % (q, strip(tk(pop[0]['t'], pop[0].get('n'))) if pop else '—', fa(pop[0].get('k', 0)) if pop else '—')),
                   ('این داده‌ها از کجا می‌آید؟', 'از گزارش‌های رسمی 13F در سایت کمیسیون بورس آمریکا (SEC) که هر فصل منتشر می‌شوند.')],
                  [('/pages/portfolio-buffett', 'پورتفوی وارن بافت')])))
    return pages


# ---------------------------------------------------------------- hub
def hub(pages):
    groups = [('فهرست‌های انتخاب سهم', [p for p in pages if p['handle'] in (
        'best-dividend-stocks', 'best-growth-stocks', 'undervalued-stocks', 'largest-us-companies', 'high-roic-stocks', 'debt-free-stocks', 'buyback-stocks')]),
              ('بهترین سهام هر صنعت', [p for p in pages if p['handle'] in {h for _, h, _ in SECTOR_PAGES}]),
              ('پورتفوی سرمایه‌گذاران بزرگ', [p for p in pages if p['handle'].startswith('portfolio-') or p['handle'] == 'superinvestors-portfolios'])]
    body = ''
    for g, ps in groups:
        if ps:
            body += '<h2>%s</h2><div class="chips">%s</div>' % (g, ''.join('<a href="/pages/%s">%s</a>' % (p['handle'], e(p['title'])) for p in ps))
    return dict(handle='guides', title='راهنمای انتخاب سهام آمریکا',
                seo_title='راهنمای انتخاب سهام آمریکا | بهترین سهام سود نقدی، رشدی، ارزان و پورتفوی وارن بافت',
                seo_desc='همه‌ی فهرست‌های به‌روز سهام آمریکا به فارسی: بهترین سهام سود نقدی، رشدی، زیر ارزش ذاتی، بدون بدهی، بهترین سهم هر صنعت و پورتفوی سرمایه‌گذاران بزرگ.',
                html=CSS + '<div class="rzg" dir="rtl"><p class="upd">به‌روزرسانی: %s</p><p>این فهرست‌ها هر روز بعد از بسته شدن بازار آمریکا از روی گزارش‌های رسمی شرکت‌ها و قیمت‌های روز دوباره ساخته می‌شوند. '
                     'روی هر سهم بزنی، تحلیل کامل آن را با امتیاز، ارزش ذاتی و صورت‌های مالی ۱۰ ساله می‌بینی.</p>%s<h2>ابزارها</h2>%s%s</div>'
                     % (date_fa(TODAY), body, chips(TOOLS[:4]), DIS))


def main():
    U = load()
    have_page = {x['t'].lower() for x in U}
    names = {x['t']: (x.get('fa'), x['en']) for x in U}
    pages = rank_pages(U) + sector_pages(U) + guru_pages(have_page, names)
    pages.append(hub(pages))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(pages, open(OUT, 'w'), ensure_ascii=False)
    for p in pages:
        print('%-40s %6d chars  %s' % (p['handle'], len(p['html']), p['title']))
    print('guides', len(pages))


if __name__ == '__main__':
    main()
