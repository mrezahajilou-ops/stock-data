#!/usr/bin/env python3
"""Text Google can read for the tool pages, shown at the very BOTTOM of each page (Reza: Nov 2026 — the
designed page on top stays exactly as it is; the explanation is only added under it).

The tools (home, stock analysis, screener, ...) are drawn by JavaScript, so without this block their HTML
holds only «در حال بارگذاری…». Each block is a Shopify metaobject `rz_block` (handle = page handle, `home` for
the front page) rendered server-side by snippets/rz-seo-block.liquid from layout/theme.liquid.

Input:  data/stocks/*.json, pages/guides.json, pages/explainers.json, pages/articles.json (built just before)
Output: pages/blocks.json  [{handle, html}]  -> synced by sync_guides.py
"""
import json, os

from build_guides import load, nm_html, alt_html, e, chips, faq_block, date_fa, TODAY, ROOT
from build_pages import fa

OUT = os.path.join(ROOT, 'pages', 'blocks.json')


def jl(name):
    try:
        return json.load(open(os.path.join(ROOT, 'pages', name)))
    except Exception:
        return None


ROWS = sorted(load(), key=lambda x: -x['mcap'])
N_STOCKS = len(ROWS)
GUIDES = jl('guides.json') or []
EXPL = (jl('explainers.json') or {}).get('articles') or []
EARN = sorted((jl('articles.json') or {}).get('articles') or [], key=lambda a: a.get('date', ''), reverse=True)


def n_fa(n):
    return fa('{:,}'.format(n).replace(',', '٬'))


def stock_chips(rows):
    return '<div class="chips">' + ''.join(
        '<a href="/pages/stocks/%s">%s%s <span class="tk">%s</span></a>' % (e(x['t'].lower()), nm_html(x.get('fa'), x['en']), alt_html(x['t']), e(x['t']))
        for x in rows) + '</div>'


FC = {p['handle'] for p in (jl('forecasts.json') or [])}
FC_HUB = ('/pages/stock-forecasts', 'پیش‌بینی سهام آمریکا (قیمت هدف تحلیلگرها)')


def stock_chips_more(rows, n):
    if len(rows) <= n + 2:
        return stock_chips(rows)
    return stock_chips(rows[:n]) + '<details class="more"><summary>شرکت‌های بیشتر (%s مورد دیگر)</summary>%s</details>' % (fa(len(rows) - n), stock_chips(rows[n:]))


def forecast_chips(rows):
    rows = [x for x in rows if x['t'].lower().replace('.', '-') + '-forecast' in FC]
    return '<div class="chips">' + ''.join('<a href="/pages/%s-forecast">پیش‌بینی سهام %s</a>' % (e(x['t'].lower().replace('.', '-')), nm_html(x.get('fa'), x['en']))
                                           for x in rows) + '</div>'


def guide_links(pred):
    return [('/pages/' + g['handle'], e(g['title'])) for g in GUIDES if pred(g['handle'])]


def learn(*handles):
    by = {a['handle']: a for a in EXPL}
    return [('/blogs/learn/' + h, e(by[h]['title'])) for h in handles if h in by]


def _auto(h):
    """Programmatic pages from build_seo_more (daily market pages, 10-year histories, comparisons, A-Z index):
    hundreds of them, so they get their own compact sections instead of flooding the ranking lists."""
    return (h.startswith('stock-market-') or h.endswith('-financial-history') or '-vs-' in h or h == 'all-stocks'
            or (h.startswith('stocks-') and len(h) <= 9) or h == 'market-movers')


RANKINGS = guide_links(lambda h: not h.startswith('best-') and not h.startswith('portfolio-') and h not in ('guides', 'superinvestors-portfolios') and not _auto(h))
DAYS = sorted(guide_links(lambda h: h.startswith('stock-market-')), reverse=True)
HIST = guide_links(lambda h: h.endswith('-financial-history'))
CMP = guide_links(lambda h: '-vs-' in h)


def chips_more(links, n, more='بیشتر'):
    """First n links as chips, the rest folded under a "more" toggle. All links stay in the HTML for search engines."""
    links = list(links)
    if len(links) <= n + 2:
        return chips(links)
    return chips(links[:n]) + ('<details class="more"><summary>%s (%s مورد دیگر)</summary>%s</details>'
                               % (more, fa(len(links) - n), chips(links[n:])))
SECTORS = guide_links(lambda h: h.startswith('best-'))
PORTFOLIOS = guide_links(lambda h: h.startswith('portfolio-') or h == 'superinvestors-portfolios')

TOOLS = [
    ('/pages/stock', 'تحلیل سهام', 'امتیاز ۵ بخشی، ارزش ذاتی، صورت‌های مالی ۱۰ ساله و نمودارهای هر شرکت'),
    ('/pages/top-30', '۳۰ سهم برتر', 'سهم‌هایی که تحلیلگرها بیشترین رشد را برایشان پیش‌بینی کرده‌اند'),
    ('/pages/screener', 'غربالگر سهام', 'فیلتر کردن هزاران سهم با نسبت قیمت به سود، رشد، بدهی و سود نقدی'),
    ('/pages/dcf', 'ماشین‌حساب ارزش ذاتی', 'محاسبه‌ی ارزش ذاتی هر سهم با فرض‌های خودت'),
    ('/pages/superinvestors', 'سوپر سرمایه‌گذارها', 'پورتفوی وارن بافت و مدیران بزرگ صندوق‌ها از گزارش‌های رسمی'),
    ('/pages/compare', 'مقایسه‌ی سهام', 'دو یا چند شرکت کنار هم، عدد به عدد'),
    ('/pages/earnings', 'تقویم گزارش‌های مالی', 'کدام شرکت کی گزارش می‌دهد و نتیجه در برابر پیش‌بینی چه بود'),
    ('/pages/watchlist', 'واچ‌لیست و هشدار قیمت', 'دنبال کردن سهم‌های دلخواه و ایمیل وقتی قیمت به عدد مورد نظر رسید'),
    ('/pages/gold', 'قیمت طلا و نقره', 'قیمت لحظه‌ای به دلار، تورم آمریکا و عوامل اصلی قیمت'),
    ('/pages/pulse', 'نبض جامعه', 'سهم‌هایی که این روزها بیشتر از همه بین فارسی‌زبان‌ها دیده می‌شوند'),
    ('/pages/contest', 'مسابقه‌ی پورتفو', 'ساختن پورتفوی فرضی ۱۰ هزار دلاری و رقابت با بقیه'),
    ('/blogs/learn', 'آموزش', 'مفاهیم پایه‌ی سرمایه‌گذاری به زبان ساده'),
]


def tool_list(skip=None):
    return '<ul class="tl">' + ''.join('<li><a href="%s">%s</a>: %s</li>' % (u, t, d) for u, t, d in TOOLS if u != skip) + '</ul>'


def other_tools(skip):
    return '<h2>ابزارهای دیگر سهام آنالیز</h2>' + chips([(u, t) for u, t, _ in TOOLS if u != skip] + [('/pages/guides', 'فهرست‌های آماده‌ی سهام')])


def block(h1, intro, *parts):
    return ('<h2 class="h1">%s</h2>' % h1 if not h1.startswith('<h1') else h1) + ''.join('<p>%s</p>' % p for p in intro) + ''.join(parts) \
        + '<p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY)


def build():
    top30, top50 = ROWS[:30], ROWS[:50]
    nf = n_fa(N_STOCKS)
    B = {}

    B['home'] = block(
        '<h1>سهام آنالیز: تحلیل سهام آمریکا به فارسی</h1>',
        ['سهام آنالیز ابزار تحلیل سهام بورس آمریکا به زبان فارسی است و بیش از %s شرکت را پوشش می‌دهد. برای هر شرکت امتیاز کلی از ۵ در پنج بخش '
         '(ارزش، آینده، گذشته، سلامت مالی و بازگشت سرمایه)، ارزش ذاتی با روش جریان نقد تنزیل‌شده، صورت‌های مالی ۱۰ ساله از گزارش‌های رسمی '
         'کمیسیون بورس آمریکا و قیمت هدف تحلیلگرها را می‌بینی.' % nf,
         'همه‌ی اعداد هر روز بعد از بسته شدن بازار آمریکا خودکار به‌روز می‌شوند و همه‌چیز به دلار است. این سایت آموزشی است و توصیه‌ی خرید یا فروش نمی‌دهد.'],
        '<h2>ابزارهای سهام آنالیز</h2>', tool_list(),
        '<h2>بزرگ‌ترین شرکت‌های بورس آمریکا</h2>', stock_chips_more(top30, 15),
        '<h2>فهرست‌های آماده‌ی سهام</h2>', chips_more([FC_HUB] + RANKINGS + SECTORS + [('/pages/guides', 'همه‌ی فهرست‌ها')], 9, 'فهرست‌های بیشتر'),
        '<h2>بورس آمریکا روزبه‌روز</h2>', chips_more([('/pages/market-movers', 'بیشترین رشد و افت امروز')]
                                                     + [(u, 'بازار ' + t.split(' در ', 1)[-1].split(':')[0]) for u, t in DAYS], 6, 'روزهای قبل'),
        '<h2>درآمد و سود ۱۰ ساله‌ی بزرگ‌ترین شرکت‌ها</h2>', chips_more([(u, t.replace('درآمد و سود ', '').split(' از ')[0]) for u, t in HIST[:60]] + [('/pages/all-stocks', 'فهرست همه‌ی سهام')], 8, 'شرکت‌های بیشتر'),
        '<h2>مقایسه‌ی سهام هم‌صنعت</h2>', chips_more(CMP[:40], 6, 'مقایسه‌های بیشتر'),
        '<h2>آموزش و اخبار</h2>', chips([('/blogs/learn', 'آموزش سرمایه‌گذاری'), ('/blogs/news', 'اخبار و مقالات'),
                                          ('/blogs/earnings-reports', 'گزارش‌های فصلی شرکت‌ها')] + learn('pe-ratio', 'intrinsic-value', 'etf', 'dividend')),
        faq_block([
            ('سهام آنالیز چیست؟', 'ابزار فارسی تحلیل سهام آمریکا که اعداد هر شرکت را از گزارش‌های رسمی خود شرکت می‌خواند و به زبان ساده توضیح می‌دهد.'),
            ('اعداد از کجا می‌آیند؟', 'صورت‌های مالی از گزارش‌های رسمی شرکت‌ها به کمیسیون بورس آمریکا، قیمت‌ها از بازار آمریکا و پیش‌بینی‌ها از میانگین تحلیلگرها.'),
            ('هر چند وقت به‌روز می‌شود؟', 'قیمت‌ها در ساعت‌های باز بودن بازار چند بار در ساعت و بقیه‌ی اعداد هر روز بعد از بسته شدن بازار.'),
            ('آیا سهام آنالیز پیشنهاد خرید یا فروش می‌دهد؟', 'نه. همه‌ی امتیازها و محاسبه‌ها آموزشی‌اند و تصمیم نهایی با خودت است.')]))

    B['stock'] = block(
        'تحلیل سهام آمریکا به فارسی',
        ['نماد یا اسم هر شرکت بورس آمریکا را بنویس تا تحلیل کاملش را ببینی: امتیاز از ۵ در ارزش، آینده، گذشته، سلامت مالی و بازگشت سرمایه، '
         'نسبت قیمت به سود و جریان نقد آزاد، رشد درآمد و سود در ۱۰ سال، ارزش ذاتی با سه سناریو، قیمت هدف تحلیلگرها و مقایسه با شرکت‌های هم‌صنعت.',
         'اعداد از گزارش‌های رسمی سالانه و فصلی شرکت‌ها می‌آیند و هر روز به‌روز می‌شوند. %s شرکت پوشش داده می‌شود.' % nf],
        '<h2>تحلیل پربازدیدترین سهم‌ها</h2>', stock_chips(top50),
        '<h2>پیش‌بینی تحلیلگرها برای بزرگ‌ترین شرکت‌ها</h2>', forecast_chips(top30[:20]),
        '<h2>یاد بگیر چطور یک سهم را تحلیل کنی</h2>', chips(learn('pe-ratio', 'eps', 'free-cash-flow', 'roic', 'profit-margin', 'intrinsic-value', 'market-cap')),
        other_tools('/pages/stock'))

    B['screener'] = block(
        'غربالگر سهام آمریکا',
        ['با غربالگر، از میان %s سهم بورس آمریکا فقط آن‌هایی را پیدا کن که شرط‌های تو را دارند: نسبت قیمت به سود پایین، رشد درآمد بالا، '
         'بدهی کم، سود نقدی، بازده سرمایه‌ی بالا یا فاصله تا ارزش ذاتی. نتیجه را می‌شود بر اساس هر ستون مرتب کرد.' % nf,
         'اگر وقت ساختن فیلتر نداری، فهرست‌های آماده‌ی پایین همین کار را از قبل انجام داده‌اند.'],
        '<h2>فهرست‌های آماده</h2>', chips_more(RANKINGS, 10, 'فهرست‌های بیشتر'),
        '<h2>بهترین سهام هر صنعت</h2>', chips_more(SECTORS, 10, 'صنعت‌های بیشتر'),
        other_tools('/pages/screener'))

    B['dcf'] = block(
        'ماشین‌حساب ارزش ذاتی سهام (روش جریان نقد تنزیل‌شده)',
        ['ارزش ذاتی یعنی ارزش واقعی یک شرکت بر اساس پولی که در آینده تولید می‌کند. این ماشین‌حساب جریان نقد آزاد شرکت را با رشدی که تو تعیین می‌کنی '
         'برای سال‌های آینده پیش‌بینی می‌کند، آن را با نرخ تنزیل به امروز برمی‌گرداند و نتیجه را با قیمت فعلی مقایسه می‌کند.',
         'برای هر سهم سه سناریوی بدبینانه، متوسط و خوش‌بینانه آماده است و می‌توانی همه‌ی فرض‌ها را خودت عوض کنی.'],
        '<h2>بیشتر بدان</h2>', chips(learn('intrinsic-value', 'free-cash-flow', 'pe-ratio') + [('/pages/undervalued-stocks', 'سهام باکیفیت زیر ارزش ذاتی')]),
        '<h2>ارزش ذاتی بزرگ‌ترین شرکت‌ها</h2>', stock_chips(top30[:20]),
        other_tools('/pages/dcf'))

    B['superinvestors'] = block(
        'پورتفوی سوپر سرمایه‌گذارها: وارن بافت و مدیران بزرگ صندوق‌ها',
        ['صندوق‌های بزرگ آمریکا موظف‌اند هر سه ماه یک بار سهم‌هایشان را در گزارش رسمی ۱۳اف به کمیسیون بورس آمریکا اعلام کنند. '
         'این صفحه پورتفوی وارن بافت و ده‌ها سرمایه‌گذار مشهور دیگر را از همین گزارش‌ها نشان می‌دهد: چه دارند، چه خریده‌اند و چه فروخته‌اند.',
         'این گزارش‌ها حدود ۴۵ روز بعد از پایان هر فصل منتشر می‌شوند؛ پس نشان می‌دهند مدیرها چند هفته پیش چه داشتند، نه امروز.'],
        '<h2>پورتفوی هر سرمایه‌گذار</h2>', chips_more(PORTFOLIOS, 10, 'سرمایه‌گذارهای بیشتر'),
        '<h2>بیشتر بدان</h2>', chips(learn('13f', 'buyback', 'roic')),
        other_tools('/pages/superinvestors'))

    B['top-30'] = block(
        '۳۰ سهم برتر آمریکا به انتخاب تحلیلگرها',
        ['این فهرست ۳۰ سهم بورس آمریکا را نشان می‌دهد که میانگین قیمت هدف تحلیلگرها بیشترین فاصله را با قیمت فعلی‌شان دارد؛ یعنی تحلیلگرها '
         'بیشترین رشد را برایشان انتظار دارند. رتبه و درصد رشد تا قیمت هدف برای همه باز است و فهرست هر روز به‌روز می‌شود.',
         'قیمت هدف تحلیلگرها پیش‌بینی است و ممکن است اشتباه باشد؛ قبل از هر تصمیم تحلیل کامل هر سهم را ببین.'],
        '<h2>قیمت هدف تحلیلگرها برای هر شرکت</h2>', forecast_chips(top30[:20]),
        '<h2>فهرست‌های رایگان</h2>', chips([FC_HUB] + RANKINGS + SECTORS[:4]),
        other_tools('/pages/top-30'))

    B['compare'] = block(
        'مقایسه‌ی سهام آمریکا کنار هم',
        ['دو یا چند سهم را انتخاب کن تا عددهایشان ردیف به ردیف کنار هم بیاید: امتیازها، نسبت قیمت به سود، رشد درآمد و سود، حاشیه‌ی سود، بدهی، '
         'بازده سرمایه، سود نقدی و ارزش ذاتی. برای تصمیم بین دو شرکت هم‌صنعت، این سریع‌ترین راه است.'],
        '<h2>شرکت‌هایی که بیشتر مقایسه می‌شوند</h2>', stock_chips(top30[:16]),
        other_tools('/pages/compare'))

    recent = [('/blogs/earnings-reports/' + a['handle'], e(a['title'])) for a in EARN[:12]]
    B['earnings'] = block(
        'تقویم گزارش‌های مالی سهام آمریکا',
        ['شرکت‌های بورس آمریکا هر سه ماه یک بار نتیجه‌ی کارشان را اعلام می‌کنند. این تقویم نشان می‌دهد کدام شرکت کی گزارش می‌دهد، '
         'تحلیلگرها چه سودی برای هر سهم پیش‌بینی کرده‌اند و بعد از گزارش، نتیجه بهتر یا بدتر از پیش‌بینی بوده است.'],
        ('<h2>آخرین گزارش‌های فصلی</h2>' + chips(recent)) if recent else '',
        '<h2>بیشتر بدان</h2>', chips(learn('earnings-season', 'eps', 'profit-margin') + [('/blogs/earnings-reports', 'همه‌ی گزارش‌های فصلی')]),
        other_tools('/pages/earnings'))

    B['watchlist'] = block(
        'واچ‌لیست و هشدار قیمت سهام آمریکا',
        ['سهم‌هایی را که دنبال می‌کنی در واچ‌لیست بگذار تا قیمت، تغییر روزانه و امتیازشان را یک‌جا ببینی. برای هر سهم می‌توانی قیمت هدف بگذاری؛ '
         'وقتی قیمت به آن عدد رسید، ایمیل هشدار برایت می‌آید.'],
        '<h2>پیشنهاد برای شروع</h2>', stock_chips(top30[:12]),
        other_tools('/pages/watchlist'))

    B['pulse'] = block(
        'نبض جامعه: سهم‌هایی که فارسی‌زبان‌ها دنبال می‌کنند',
        ['این صفحه نشان می‌دهد کاربران سهام آنالیز این روزها بیشتر سراغ کدام سهم‌ها رفته‌اند: پربازدیدترین‌ها، جستجوها و ورود و خروج از واچ‌لیست‌ها. '
         'آمار بدون نام، ایمیل یا نشانی اینترنتی کاربران ساخته می‌شود. محبوب بودن یک سهم به معنی خوب بودنش نیست؛ تحلیل کامل هر سهم را ببین.'],
        '<h2>بزرگ‌ترین شرکت‌های بورس آمریکا</h2>', stock_chips(top30[:16]),
        other_tools('/pages/pulse'))

    B['contest'] = block(
        'مسابقه‌ی پورتفوی سهام آمریکا',
        ['در این مسابقه هر نفر با ۱۰ هزار دلار فرضی یک پورتفوی سهام آمریکا می‌سازد. قیمت خرید و فروش را بازار تعیین می‌کند و سود نقدی هم حساب می‌شود. '
         'رتبه‌بندی بر اساس بازده است و شرکت در مسابقه رایگان است.'],
        '<h2>قبل از انتخاب سهم</h2>', chips(RANKINGS[:5] + [('/pages/stock', 'تحلیل سهام')]),
        other_tools('/pages/contest'))
    return B


def main():
    B = build()
    json.dump([{'handle': k, 'html': v} for k, v in B.items()], open(OUT, 'w'), ensure_ascii=False)
    print('blocks', len(B), {k: len(v) for k, v in B.items()})


if __name__ == '__main__':
    main()
