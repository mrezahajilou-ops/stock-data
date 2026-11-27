"""معاملات مدیران (sahamanaliz.com/pages/insider-trading): the Farsi edition of the insider-trading page the other sites build
with tools/insider.py. Same browser code (web_src/insider.js, a copy of the sites' assets/insider.js) and the same live feed
(worker /c/insider.json, from SEC Form 4 every few minutes). Facts only: who traded, what, when, how much; never advice."""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
FEED = 'https://rz-events.mreza-hajilou.workers.dev/c/insider.json'
RAW = 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data'

S = dict(
    tabs=['تازه‌ترین', 'فقط خریدها', 'فقط فروش‌ها', 'بزرگ‌ترین خریدهای ۷ روز', 'بزرگ‌ترین فروش‌های ۷ روز'],
    th=['زمان گزارش', 'سهم', 'نام فرد', 'سمت', 'نوع معامله', 'تعداد سهم', 'قیمت', 'ارزش'],
    buy='خرید', sell='فروش', plan='فروش برنامه‌ریزی‌شده', plan_b='خرید برنامه‌ریزی‌شده', plan_tip='طبق برنامه‌ای که ماه‌ها قبل از معامله ثبت شده',
    wk='۷ روز گذشته', nb='خرید', ns='فروش', ratio='سهم خریدها از ارزش معاملات',
    upd='به‌روزرسانی', ago='%s پیش', now='همین الان', min='دقیقه', hr='ساعت', day='روز', loading='در حال بارگذاری تازه‌ترین گزارش‌ها…', none='هنوز معامله‌ای در این بخش نیست.',
    more='۳۰ معامله‌ی دیگر', open='تحلیل کامل %s ›', close='بستن',
    p_h='%s: معاملات مدیران در ۱۲ ماه گذشته', p_leg=['قیمت (پایانی هفتگی)', 'خرید مدیر', 'فروش مدیر'],
    p_sum='۱۲ ماه گذشته: %d خرید (%s) و %d فروش (%s).', p_none='در ۱۲ ماه گذشته هیچ خرید یا فروشی از بازار توسط مدیران این شرکت ثبت نشده.',
    who_h='%s: معاملات ثبت‌شده', who_at='در', who_note='معاملات ۱۲ ماه گذشته‌ی این فرد در این شرکت، به‌علاوه‌ی معاملاتی که در گزارش‌های زنده آمده.',
    held='سهام بعد از معامله', of_hold='سهم او %s',
    roles=dict(ceo='مدیرعامل', cfo='مدیر مالی', coo='مدیر عملیات', pres='رئیس شرکت', chair='رئیس هیئت‌مدیره', dir='عضو هیئت‌مدیره', own='سهامدار عمده (۱۰٪)',
               vp='معاون', law='مشاور حقوقی ارشد', off='مدیر ارشد', oth='سایر'))

TITLE = '🕵️ معاملات مدیران: خرید و فروش مدیران شرکت‌های آمریکایی به‌صورت زنده'
SUB = ('وقتی مدیرعامل، عضو هیئت‌مدیره یا سهامدار عمده‌ی یک شرکت سهام همان شرکت را می‌خرد یا می‌فروشد، باید ظرف دو روز کاری به کمیسیون بورس آمریکا گزارش بدهد. '
       'این صفحه همان گزارش‌ها را به محض ثبت نشان می‌دهد. روی هر معامله بزن تا نمودار یک‌ساله‌ی سهم با همه‌ی خریدها و فروش‌های مدیران باز شود؛ روی نام هر فرد بزن تا معاملاتش را ببینی.')
FAQ = [('آیا معامله‌ی مدیران قانونی است؟', 'بله، به شرط گزارش. مدیران، اعضای هیئت‌مدیره و سهامداران بالای ۱۰٪ می‌توانند سهام شرکت خودشان را بخرند و بفروشند، اما باید ظرف دو روز کاری فرم ۴ را به کمیسیون بورس آمریکا بدهند. غیرقانونی، معامله با اطلاعات محرمانه‌ای است که مردم از آن خبر ندارند.'),
       ('چرا خرید مدیران مهم‌تر از فروش آن‌هاست؟', 'فروش دلیل‌های زیادی دارد: مالیات، خرید خانه، پخش کردن دارایی. اما خرید با پول شخصی معمولاً یک دلیل دارد: مدیر فکر می‌کند سهم بیشتر از قیمت فعلی می‌ارزد. برای همین خریدها، مخصوصاً وقتی چند مدیر هم‌زمان می‌خرند، بیشتر زیر نظرند.'),
       ('فروش برنامه‌ریزی‌شده یعنی چه؟', 'فروشی که طبق برنامه‌ای انجام می‌شود که مدیر ماه‌ها قبل با تاریخ یا قیمت مشخص ثبت کرده. چون زمانش از قبل تعیین شده، کمتر درباره‌ی نظر فعلی مدیر چیزی می‌گوید.'),
       ('این صفحه هر چند وقت به‌روز می‌شود؟', 'گزارش‌های تازه‌ی فرم ۴ هر چند دقیقه یک بار جمع می‌شوند. خود معامله ممکن است تا دو روز کاری قبل از گزارش انجام شده باشد.')]
DIS = 'منبع: گزارش‌های فرم ۴ در سامانه‌ی کمیسیون بورس آمریکا؛ فقط خرید (کد P) و فروش (کد S) از بازار. فقط اطلاع‌رسانی است و پیشنهاد خرید یا فروش نیست.'


def _tickers():
    try:
        return sorted(r[0] for r in json.load(open(os.path.join(ROOT, 'data', 'screener.json')))['rows'])
    except Exception:
        return []


def body():
    esc = lambda s: str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    cfg = dict(feed=FEED, raw=RAW, su='/pages/stocks/%s', lc=True, loc='fa-IR-u-ca-gregory-nu-latn', rtl=True, tk=','.join(_tickers()), S=S, keep=False, noco=False)
    tabs = ''.join('<button role="tab" data-k="%d"%s>%s</button>' % (i, ' aria-selected="true" class="on"' if i == 0 else '', esc(t)) for i, t in enumerate(S['tabs']))
    faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in FAQ)
    css = open(os.path.join(ROOT, 'web_src', 'insider.css'), encoding='utf-8').read()
    return ('<style>%s\n#rzin .ins{--ib:#4FA37A}#rzin .ins-t th,#rzin .ins-t td{text-align:right}#rzin .ins-t .n{text-align:left}#rzin details{margin:6px 0}#rzin summary{cursor:pointer;font-weight:800}</style>'
            '<article class="ins ins-rtl"><p class="meta"><span class="ins-dot"></span><span id="ins-upd">%s</span></p><div class="ins-sum" id="ins-sum"></div>'
            '<div class="ins-tabs" role="tablist">%s</div><div class="ins-wrap"><table class="ins-t" id="ins-t"><thead><tr>%s</tr></thead><tbody><tr><td colspan="8" class="none">%s</td></tr></tbody></table></div>'
            '<p class="ins-more"><button id="ins-more" hidden>%s</button></p><h2>پرسش‌های رایج</h2>%s<p class="note">%s</p>'
            '<script>window.INS_CFG=%s;</script></article>'
            % (css, esc('گزارش‌های فرم ۴ کمیسیون بورس آمریکا · گزارش‌های تازه در چند دقیقه'), tabs, ''.join('<th>%s</th>' % esc(h) for h in S['th']),
               esc(S['loading']), esc(S['more']), faq, esc(DIS), json.dumps(cfg, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))


def js():
    return open(os.path.join(ROOT, 'web_src', 'insider.js'), encoding='utf-8').read()
