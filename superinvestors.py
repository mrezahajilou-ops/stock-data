#!/usr/bin/env python3
"""Super investors / fund manager portfolios from SEC 13F filings (public data).

For every manager in MANAGERS:
  - reads the filing list (data.sec.gov/submissions), takes the last 8 quarters of 13F-HR filings
    (amendments: RESTATEMENT replaces the quarter, NEW HOLDINGS is added to it)
  - parses the information table (all rows of one CUSIP are summed; options and bonds kept apart)
  - CUSIP -> ticker via OpenFIGI (cached in the output branch, so each CUSIP is looked up once)
  - quarter-over-quarter activity per position (new / add / reduce / sold out), split-adjusted
Writes to ./superinvestors (published to the branch "superinvestors"):
  index.json   managers + "most owned", "most bought", "most sold", latest filings
  m/<id>.json  one manager: holdings, activity, 8 quarters of value
  owners.json  ticker -> [[manager id, % of portfolio, activity]] (for the stock page)
  cusip.json   CUSIP -> [ticker, name, security type] cache
"""
import gzip, json, os, re, sys, time, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'superinvestors')
UA = os.environ.get('SEC_USER_AGENT', 'Reza Hajilou mreza.hajilou@gmail.com')
NQ = 8          # quarters kept per manager
TOP = 200       # holdings stored per manager (rest only counted)

# id, CIK, words that must appear in the SEC filer name, person (en), firm (en), person (fa), firm (fa), style, bio (fa)
MANAGERS = [
    ('buffett', 1067983, 'BERKSHIRE', 'Warren Buffett', 'Berkshire Hathaway', 'وارن بافت', 'برکشایر هاتاوی', 'ارزشی',
     'مشهورترین سرمایه‌گذار دنیا؛ برکشایر سهم شرکت‌های باکیفیت رو برای سال‌های طولانی نگه می‌داره. از ۲۰۲۶ گرگ ایبل مدیرعامله و بافت رئیس هیئت‌مدیره است.'),
    ('ackman', 1336528, 'PERSHING', 'Bill Ackman', 'Pershing Square', 'بیل اکمن', 'پرشینگ اسکوئر', 'متمرکز / فعال',
     'پورتفوی خیلی متمرکز (معمولاً کمتر از ۱۲ سهم) از شرکت‌های بزرگ و ساده؛ گاهی برای تغییر مدیریت فشار میاره.'),
    ('burry', 1649339, 'SCION', 'Michael Burry', 'Scion Asset Management', 'مایکل بِری', 'سایون', 'ارزشی / مخالف‌جریان',
     'همون کسی که بحران ۲۰۰۸ رو پیش‌بینی کرد (فیلم Big Short). معاملاتش سریع و مخالف جریان بازاره. صندوقش در اواخر ۲۰۲۵ ثبتش رو پس گرفت، پس آخرین گزارش قدیمیه.'),
    ('lilu', 1709323, 'HIMALAYA', 'Li Lu', 'Himalaya Capital', 'لی لو', 'هیمالیا کپیتال', 'ارزشی',
     'مدیری که چارلی مانگر پولش رو بهش سپرده بود؛ فقط چند سهم رو با اطمینان بالا و برای مدت خیلی طولانی نگه می‌داره.'),
    ('smith', 1569205, 'FUNDSMITH', 'Terry Smith', 'Fundsmith', 'تری اسمیت', 'فاندزمیت', 'کیفیت',
     'شعارش «سهام خوب بخر، گرون نخر، هیچ کاری نکن». روی شرکت‌های با بازده سرمایه‌ی بالا و رشد پایدار تمرکز داره.'),
    ('pabrai', 1549575, 'DALAL', 'Mohnish Pabrai', 'Pabrai (Dalal Street)', 'مونیش پابرای', 'پابرای', 'ارزشی / متمرکز',
     'شاگرد سبک بافت و مانگر؛ شرط‌های کم و بزرگ روی سهم‌های خیلی ارزون. بخش بزرگی از پورتفوش خارج از آمریکاست که اینجا دیده نمیشه.'),
    ('klarman', 1061768, 'BAUPOST', 'Seth Klarman', 'Baupost Group', 'ست کلارمن', 'باپوست', 'ارزشی',
     'نویسنده‌ی کتاب افسانه‌ای Margin of Safety؛ خیلی محتاطه و فقط وقتی قیمت با حاشیه‌ی امن زیاد پایینه می‌خره.'),
    ('tepper', 1656456, 'APPALOOSA', 'David Tepper', 'Appaloosa', 'دیوید تپر', 'آپالوسا', 'رشد / فرصت‌طلب',
     'یکی از موفق‌ترین مدیران صندوق پوشش ریسک؛ وقتی بازار ترسیده با جسارت می‌خره. این روزها بیشتر روی تکنولوژی و چین.'),
    ('druck', 1536411, 'DUQUESNE', 'Stanley Druckenmiller', 'Duquesne Family Office', 'استنلی دراکنمیلر', 'دوکین', 'کلان / رشد',
     'شریک قدیمی سوروس و یکی از بهترین سابقه‌های بازدهی تاریخ؛ بر اساس روندهای کلان اقتصاد سریع جابه‌جا میشه.'),
    ('icahn', 921669, 'ICAHN', 'Carl Icahn', 'Icahn Capital', 'کارل آیکان', 'آیکان', 'فعال',
     'معروف‌ترین سرمایه‌گذار فعال (اکتیویست)؛ سهم بزرگ می‌خره و هیئت‌مدیره رو برای تغییر تحت فشار می‌ذاره.'),
    ('loeb', 1040273, 'THIRD POINT', 'Dan Loeb', 'Third Point', 'دن لوب', 'تِرد پوینت', 'فعال / رویدادمحور',
     'اکتیویست معروف با نامه‌های تند به مدیران شرکت‌ها؛ روی رویدادهایی مثل جداسازی و تغییر مدیریت سرمایه‌گذاری می‌کنه.'),
    ('coleman', 1167483, 'TIGER GLOBAL', 'Chase Coleman', 'Tiger Global', 'چیس کلمن', 'تایگر گلوبال', 'رشد / تکنولوژی',
     'از «توله‌ببرهای» جولین رابرتسون؛ روی شرکت‌های اینترنتی و نرم‌افزاری پررشد تمرکز داره.'),
    ('mandel', 1061165, 'LONE PINE', 'Stephen Mandel', 'Lone Pine Capital', 'استیون مندل', 'لون پاین', 'رشد',
     'یکی دیگه از شاگردهای تایگر؛ سهم‌های رشدی باکیفیت با مدیریت قوی.'),
    ('halvorsen', 1103804, 'VIKING', 'Andreas Halvorsen', 'Viking Global', 'آندریاس هالوورسن', 'وایکینگ گلوبال', 'رشد / بنیادی',
     'صندوق بزرگ با تحلیل بنیادی دقیق؛ پورتفوی متنوع از شرکت‌های بزرگ در همه‌ی بخش‌ها.'),
    ('laffont', 1135730, 'COATUE', 'Philippe Laffont', 'Coatue Management', 'فیلیپ لافون', 'کواتو', 'تکنولوژی',
     'متخصص سهام تکنولوژی؛ از اولین‌ها در هوش مصنوعی و نیمه‌هادی‌ها.'),
    ('dalio', 1350694, 'BRIDGEWATER', 'Ray Dalio', 'Bridgewater Associates', 'ری دالیو', 'بریج‌واتر', 'کلان',
     'بزرگ‌ترین صندوق پوشش ریسک دنیا؛ پورتفوی خیلی متنوع و بر پایه‌ی مدل‌های اقتصاد کلان. دالیو دیگه در مدیریت نیست.'),
    ('soros', 1029160, 'SOROS FUND', 'George Soros', 'Soros Fund Management', 'جورج سوروس', 'سوروس', 'کلان',
     'کسی که با شرط علیه پوند انگلیس معروف شد؛ دفتر خانوادگیش امروز پورتفوی متنوعی داره.'),
    ('gates', 1166559, 'GATES FOUNDATION', 'Bill Gates', 'Gates Foundation Trust', 'بیل گیتس', 'بنیاد گیتس', 'ارزشی / بلندمدت',
     'صندوق بنیاد بیل و ملیندا گیتس؛ سهم بزرگی از مایکروسافت و برکشایر و چند شرکت باثبات دیگه.'),
    ('gayner', 1096343, 'MARKEL', 'Tom Gayner', 'Markel Group', 'تام گینر', 'مارکل', 'کیفیت',
     'به «برکشایر کوچک» معروفه؛ شرکت‌های باکیفیت با مدیران صادق رو برای سال‌ها نگه می‌داره.'),
    ('watsa', 915191, 'FAIRFAX', 'Prem Watsa', 'Fairfax Financial', 'پرم واتسا', 'فیرفکس', 'ارزشی',
     'به «وارن بافت کانادا» معروفه؛ سرمایه‌گذاری ارزشی و مخالف جریان.'),
    ('munger', 783412, 'DAILY JOURNAL', 'Charlie Munger', 'Daily Journal', 'چارلی مانگر', 'دیلی ژورنال', 'ارزشی',
     'پورتفوی شرکت دیلی ژورنال که چارلی مانگر تا ۲۰۲۳ مدیریتش می‌کرد؛ چند سهم معدود و بسیار متمرکز.'),
    ('akre', 1112520, 'AKRE', 'Chuck Akre', 'Akre Capital', 'چاک ایکر', 'ایکر کپیتال', 'کیفیت',
     'فلسفه‌ی «چارپایه‌ی سه‌پایه»: کسب‌وکار عالی، مدیران عالی، و فرصت‌های سرمایه‌گذاری مجدد. سهم‌ها رو ده‌ها سال نگه می‌داره.'),
    ('rochon', 1641864, 'GIVERNY', 'François Rochon', 'Giverny Capital', 'فرانسوا روشون', 'جیورنی', 'کیفیت',
     'مدیر کانادایی با سابقه‌ی بلند شکست دادن بازار؛ شرکت‌های باکیفیت با قیمت منطقی.'),
    ('marks', 949509, 'OAKTREE', 'Howard Marks', 'Oaktree Capital', 'هوارد مارکس', 'اوک‌تری', 'ارزشی / اعتباری',
     'نویسنده‌ی یادداشت‌های معروف و کتاب The Most Important Thing؛ اوک‌تری بیشتر در اوراق قرضه و دارایی‌های تحت فشار فعاله.'),
    ('elliott', 1791786, 'ELLIOTT', 'Paul Singer', 'Elliott Investment Management', 'پل سینگر', 'الیوت', 'فعال',
     'قدرتمندترین صندوق اکتیویست دنیا؛ در شرکت‌های بزرگ سهم می‌خره و برای تغییر استراتژی فشار میاره.'),
    ('valueact', 1418814, 'VALUEACT', 'Mason Morfit', 'ValueAct Capital', 'میسون مورفیت', 'ولیو اکت', 'فعال / ارزشی',
     'اکتیویست آرام؛ به جای جنگ با مدیریت، معمولاً با یه کرسی در هیئت‌مدیره همکاری می‌کنه.'),
    ('peltz', 1345471, 'TRIAN', 'Nelson Peltz', 'Trian Fund Management', 'نلسون پلتز', 'ترایان', 'فعال',
     'اکتیویست معروف در شرکت‌های بزرگ مصرفی و صنعتی؛ معمولاً پورتفوی خیلی متمرکز.'),
    ('starboard', 1517137, 'STARBOARD', 'Jeff Smith', 'Starboard Value', 'جف اسمیت', 'استاربورد', 'فعال',
     'اکتیویستی که روی بهبود حاشیه‌ی سود و کارایی شرکت‌ها تمرکز داره.'),
    ('gerstner', 1541617, 'ALTIMETER', 'Brad Gerstner', 'Altimeter Capital', 'برد گرستنر', 'آلتیمیتر', 'تکنولوژی',
     'سرمایه‌گذار تکنولوژی؛ از حامیان بزرگ انویدیا و سهام هوش مصنوعی.'),
    ('wood', 1697748, 'ARK INVEST', 'Cathie Wood', 'ARK Investment', 'کتی وود', 'آرک اینوست', 'نوآوری',
     'روی نوآوری‌های بزرگ مثل هوش مصنوعی، رباتیک، ژنتیک و رمزارز سرمایه‌گذاری می‌کنه؛ پرنوسان و پرمعامله.'),
    ('polen', 1034524, 'POLEN', 'Dan Davidowitz', 'Polen Capital', 'دن دیویدوویتز', 'پولن کپیتال', 'رشد باکیفیت',
     'فقط شرکت‌هایی که سال‌ها رشد پایدار سود با ترازنامه‌ی قوی داشتن.'),
    ('nygren', 813917, 'HARRIS ASSOCIATES', 'Bill Nygren', 'Harris Associates (Oakmark)', 'بیل نایگرن', 'هریس / اوک‌مارک', 'ارزشی',
     'مدیر صندوق‌های معروف اوک‌مارک؛ سهام ارزون نسبت به ارزش ذاتی.'),
    ('sequoia', 1720792, 'RUANE', 'Ruane Cunniff', 'Sequoia Fund (Ruane Cunniff)', 'روان کانیف', 'صندوق سکویا', 'کیفیت',
     'صندوقی که بافت در دهه‌ی ۷۰ به سرمایه‌گذارهاش پیشنهاد داد؛ پورتفوی متمرکز از شرکت‌های عالی.'),
    ('russo', 860643, 'GARDNER RUSSO', 'Thomas Russo', 'Gardner Russo & Quinn', 'تامس روسو', 'گاردنر روسو', 'کیفیت / جهانی',
     'برندهای جهانی مصرفی که ده‌ها سال رشد می‌کنن؛ سهم‌ها رو خیلی طولانی نگه می‌داره.'),
    ('bloomstran', 1115373, 'SEMPER AUGUSTUS', 'Chris Bloomstran', 'Semper Augustus', 'کریس بلومستران', 'سمپر آگوستوس', 'ارزشی',
     'از بهترین تحلیلگرهای برکشایر؛ پورتفوی متمرکز و نامه‌های سالانه‌ی خیلی مفصل.'),
    ('firsteagle', 1325447, 'FIRST EAGLE', 'First Eagle', 'First Eagle Investment', 'فرست ایگل', 'فرست ایگل', 'ارزشی / محافظه‌کار',
     'سرمایه‌گذاری محتاطانه با حاشیه‌ی امن؛ همیشه بخشی رو در طلا نگه می‌داره.'),
    ('tweedy', 732905, 'TWEEDY', 'Tweedy, Browne', 'Tweedy, Browne', 'تویدی براون', 'تویدی براون', 'ارزشی',
     'یکی از قدیمی‌ترین شرکت‌های سرمایه‌گذاری ارزشی به سبک بنجامین گراهام.'),
    ('hawkins', 807985, 'SOUTHEASTERN', 'Mason Hawkins', 'Southeastern Asset Management', 'میسون هاوکینز', 'ساوث‌ایسترن (لانگ‌لیف)', 'ارزشی',
     'مدیر صندوق‌های لانگ‌لیف؛ شرکت‌های خوب با قیمت حدود ۶۰٪ ارزش ذاتی.'),
    ('weitz', 883965, 'WEITZ', 'Wally Weitz', 'Weitz Investment', 'والی وایتز', 'وایتز', 'ارزشی',
     'سرمایه‌گذار ارزشی اهل اوماها، همشهری بافت.'),
    ('train', 1484148, 'LINDSELL', 'Nick Train', 'Lindsell Train', 'نیک ترین', 'لیندسل ترین', 'کیفیت',
     'مدیر انگلیسی با چرخش خیلی کم؛ برندهای قدرتمند و کسب‌وکارهای دیجیتال.'),
    ('altarock', 1631014, 'ALTAROCK', 'Mark Massey', 'AltaRock Partners', 'مارک مسی', 'آلتاراک', 'کیفیت / متمرکز',
     'پورتفوی خیلی متمرکز از چند شرکت عالی که سال‌ها نگه داشته میشن.'),
    ('durable', 1798849, 'DURABLE', 'Henry Ellenbogen', 'Durable Capital', 'هنری النبوگن', 'دیوربل کپیتال', 'رشد',
     'مدیر سابق تی‌رو پرایس؛ شرکت‌های پررشد که می‌تونن سال‌ها مرکب رشد کنن.'),
    ('sundheim', 1747057, 'D1 CAPITAL', 'Dan Sundheim', 'D1 Capital Partners', 'دن ساندهایم', 'دی‌وان کپیتال', 'رشد',
     'مدیر سابق وایکینگ؛ ترکیب سهام بورسی و شرکت‌های خصوصی.'),
    ('abrams', 1358706, 'ABRAMS CAPITAL', 'David Abrams', 'Abrams Capital', 'دیوید آبرامز', 'آبرامز کپیتال', 'ارزشی',
     'شاگرد ست کلارمن؛ کم حرف و صبور، با تمرکز روی حاشیه‌ی امن.'),
    ('hohn', 1647251, 'TCI FUND', 'Chris Hohn', 'TCI Fund Management', 'کریس هون', 'تی‌سی‌آی', 'کیفیت / فعال',
     'مدیر انگلیسی با یکی از بهترین بازدهی‌های دهه‌ی اخیر؛ چند شرکت انحصاری مثل فرودگاه‌ها و ویزا/مسترکارت.'),
    ('davis', 1036325, 'DAVIS SELECTED', 'Chris Davis', 'Davis Advisors', 'کریس دیویس', 'دیویس', 'ارزشی / رشد',
     'خانواده‌ای که سه نسل سرمایه‌گذاری بلندمدت کردن؛ تمرکز روی بانک‌ها و شرکت‌های باکیفیت.'),
    ('yacktman', 905567, 'YACKTMAN', 'Yacktman', 'Yacktman Asset Management', 'یکتمن', 'یکتمن', 'ارزشی / کیفیت',
     'شرکت‌های باکیفیت و کم‌ریسک با قیمت مناسب؛ خیلی محافظه‌کار.'),
    ('pzena', 1027796, 'PZENA', 'Richard Pzena', 'Pzena Investment', 'ریچارد پزنا', 'پزنا', 'ارزشی عمیق',
     'سهام خیلی ارزون که بازار ازشون ناامید شده؛ سبک ارزشی عمیق.'),
    ('dodge', 200217, 'DODGE', 'Dodge & Cox', 'Dodge & Cox', 'داج اند کاکس', 'داج اند کاکس', 'ارزشی',
     'یکی از قدیمی‌ترین مدیران صندوق آمریکا (از ۱۹۳۰)؛ ارزشی و بلندمدت.'),
    ('greenberg', 1553733, 'BRAVE WARRIOR', 'Glenn Greenberg', 'Brave Warrior Advisors', 'گلن گرینبرگ', 'بریو واریر', 'متمرکز',
     'پورتفوی خیلی متمرکز از حدود ده شرکت که عمیق می‌شناسه.'),
    ('gabelli', 807249, 'GAMCO', 'Mario Gabelli', 'GAMCO Investors', 'ماریو گابلی', 'گمکو', 'ارزشی',
     'سرمایه‌گذار ارزشی قدیمی با تمرکز روی شرکت‌های رسانه‌ای و صنعتی و موقعیت‌های ادغام.'),
]


def get(url, tries=4, data=None, headers=None):
    h = {'User-Agent': UA, 'Accept-Encoding': 'gzip'}
    h.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    b = gzip.decompress(b)
                return b
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                time.sleep(15 * (i + 1))
                continue
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return None


_last = [0.0]
DEBUG = {}


def sec(url):
    dt = time.time() - _last[0]
    if dt < 0.13:  # SEC asks for at most 10 requests per second
        time.sleep(0.13 - dt)
    _last[0] = time.time()
    return get(url)


def local(tag):
    return tag.rsplit('}', 1)[-1]


def parse_table(xml):
    rows = []
    root = ET.fromstring(xml)
    for it in root.iter():
        if local(it.tag) != 'infoTable':
            continue
        d = {}
        for c in it.iter():
            k = local(c.tag)
            if k in ('nameOfIssuer', 'titleOfClass', 'cusip', 'value', 'sshPrnamt', 'sshPrnamtType', 'putCall'):
                d[k] = (c.text or '').strip()
        rows.append(d)
    return rows


def amendment_type(cik, acc):
    b = sec('https://www.sec.gov/Archives/edgar/data/%d/%s/primary_doc.xml' % (cik, acc.replace('-', '')))
    if not b:
        return 'RESTATEMENT'
    m = re.search(rb'<(?:\w+:)?amendmentType>\s*([^<]+)<', b)
    return m.group(1).decode().strip().upper() if m else 'RESTATEMENT'


def info_table(cik, acc):
    base = 'https://www.sec.gov/Archives/edgar/data/%d/%s/' % (cik, acc.replace('-', ''))
    b = sec(base + 'index.json')
    if not b:
        return None
    items = json.loads(b).get('directory', {}).get('item', [])
    xs = [i for i in items if i['name'].lower().endswith('.xml') and i['name'].lower() != 'primary_doc.xml']
    if not xs:
        return None
    xs.sort(key=lambda i: (('info' in i['name'].lower() or 'table' in i['name'].lower()), int(i.get('size') or 0)), reverse=True)
    x = sec(base + xs[0]['name'])
    return parse_table(x) if x else None


def num(s):
    try:
        return float(str(s).replace(',', ''))
    except ValueError:
        return 0.0


def quarter_rows(rows, filed):
    """Sum rows per CUSIP. Returns {cusip: {...}} for shares (common/ADR/ETF) and options separately."""
    eq, opt = {}, {}
    for r in rows:
        cu = (r.get('cusip') or '').upper().strip()
        if not cu:
            continue
        v, n = num(r.get('value')), num(r.get('sshPrnamt'))
        pc = (r.get('putCall') or '').strip().upper()
        if pc:
            o = opt.setdefault((cu, pc), {'cusip': cu, 'pc': pc, 'name': r.get('nameOfIssuer'), 'v': 0.0, 'n': 0.0})
            o['v'] += v; o['n'] += n
            continue
        if (r.get('sshPrnamtType') or 'SH').upper() != 'SH':
            continue  # bonds / notes
        o = eq.setdefault(cu, {'cusip': cu, 'name': r.get('nameOfIssuer'), 'cls': r.get('titleOfClass'), 'v': 0.0, 'n': 0.0})
        o['v'] += v; o['n'] += n
    # values were reported in thousands of dollars before 2023
    mult = 1000.0 if filed < '2023-01-03' else 1.0
    px = sorted(o['v'] / o['n'] for o in eq.values() if o['n'] > 0 and o['v'] > 0)
    if mult == 1.0 and px and px[len(px) // 2] < 0.5:
        mult = 1000.0  # filer still reports in thousands
    for o in list(eq.values()) + list(opt.values()):
        o['v'] *= mult
    return eq, opt


def load_manager(m):
    mid, cik, word = m[0], m[1], m[2]
    b = sec('https://data.sec.gov/submissions/CIK%010d.json' % cik)
    if not b:
        print('::warning::%s: no SEC submissions (CIK %d)' % (mid, cik)); return None
    j = json.loads(b)
    name = j.get('name') or ''
    if word.upper() not in name.upper():
        print('::warning::%s: CIK %d is "%s" - expected %s, skipped' % (mid, cik, name, word)); return None
    rc = j['filings']['recent']
    fs = [dict(form=rc['form'][i], acc=rc['accessionNumber'][i], filed=rc['filingDate'][i], period=rc['reportDate'][i])
          for i in range(len(rc['form'])) if rc['form'][i] in ('13F-HR', '13F-HR/A')]
    if not fs:
        print('::warning::%s: no 13F filings' % mid); return None
    periods = sorted({f['period'] for f in fs if f['form'] == '13F-HR'}, reverse=True)[:NQ]
    Q = []
    for p in periods:
        group = sorted([f for f in fs if f['period'] == p], key=lambda f: f['filed'])
        orig = [f for f in group if f['form'] == '13F-HR']
        base = orig[-1]
        rows = info_table(cik, base['acc']) or []
        filed = base['filed']
        for a in [f for f in group if f['form'] == '13F-HR/A' and f['filed'] >= base['filed']]:
            t = amendment_type(cik, a['acc'])
            ar = info_table(cik, a['acc']) or []
            if not ar:
                continue
            rows = ar if t.startswith('RESTATEMENT') else rows + ar
            filed = a['filed']
        eq, opt = quarter_rows(rows, base['filed'])
        Q.append({'period': p, 'filed': filed, 'first_filed': base['filed'], 'eq': eq, 'opt': opt})
    DEBUG[mid] = {'sec': name, 'forms': [[f['form'], f['period'], f['filed']] for f in fs[:6]]}
    print('%s: %s, %d quarters, latest %s (%d positions)' % (mid, name, len(Q), Q[0]['period'] if Q else '-', len(Q[0]['eq']) if Q else 0))
    return {'m': m, 'sec_name': name, 'Q': Q}


# ------------------------------------------------------------------ CUSIP -> ticker
def figi(cusips, cache):
    todo = [c for c in cusips if c not in cache]
    print('OpenFIGI: %d new CUSIPs (%d cached)' % (len(todo), len(cache)))
    key = os.environ.get('OPENFIGI_KEY')
    step, pause = (100, 0.3) if key else (10, 2.6)
    hdr = {'Content-Type': 'application/json'}
    if key:
        hdr['X-OPENFIGI-APIKEY'] = key
    for i in range(0, len(todo), step):
        chunk = todo[i:i + step]
        body = json.dumps([{'idType': 'ID_CUSIP', 'idValue': c, 'exchCode': 'US'} for c in chunk]).encode()
        b = get('https://api.openfigi.com/v3/mapping', data=body, headers=hdr, tries=6)
        time.sleep(pause)
        if not b:
            continue
        for c, res in zip(chunk, json.loads(b)):
            d = (res.get('data') or [None])[0] if isinstance(res, dict) else None
            if d and d.get('ticker'):
                cache[c] = [d['ticker'].replace('/', '-').upper(), d.get('name') or '', d.get('securityType') or '']
            elif isinstance(res, dict) and 'error' in res and 'No identifier' in str(res.get('error')):
                cache[c] = [None, '', '']
    # second pass for misses (foreign-domiciled CUSIPs etc.): any exchange, keep a US listing if there is one
    US = ('US', 'UN', 'UW', 'UQ', 'UA', 'UR', 'UP', 'UV', 'UF')
    miss = [c for c in cusips if c in cache and not cache[c][0] and len(cache[c]) < 4]
    print('OpenFIGI retry: %d' % len(miss))
    for i in range(0, len(miss), step):
        chunk = miss[i:i + step]
        body = json.dumps([{'idType': 'ID_CUSIP', 'idValue': c} for c in chunk]).encode()
        b = get('https://api.openfigi.com/v3/mapping', data=body, headers=hdr, tries=6)
        time.sleep(pause)
        if not b:
            continue
        for c, res in zip(chunk, json.loads(b)):
            ds = (res.get('data') or []) if isinstance(res, dict) else []
            us = [d for d in ds if d.get('exchCode') in US and d.get('ticker')]
            if us:
                d = us[0]
                cache[c] = [d['ticker'].replace('/', '-').upper(), d.get('name') or '', d.get('securityType') or '']
            elif isinstance(res, dict) and ('data' in res or 'No identifier' in str(res.get('error'))):
                cache[c] = [None, (ds[0].get('name') if ds else '') or '', '', 1]
    return cache


def norm(s):
    s = re.sub(r'[^A-Z0-9 ]', ' ', (s or '').upper())
    s = re.sub(r'\b(INC|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|PLC|PUB|HOLDINGS?|HLDGS?|HLDNGS|GROUP|GRP|THE|CL|CLASS|A|B|C|NEW|DEL|COM|SA|NV|N V|AG|SE|SPONSORED|ADR|ADS|IRELAND|INTL|INTERNATIONAL|INTERNATION)\b', ' ', s)
    return ' '.join(s.split())


# ------------------------------------------------------------------ main
def main():
    os.makedirs(os.path.join(OUT, 'm'), exist_ok=True)
    idx = json.load(open(os.path.join(ROOT, 'data', 'index.json')))
    aliases = json.load(open(os.path.join(ROOT, 'data', 'aliases.json')))
    universe = {r['t'] for r in idx}
    names_by_t = {r['t']: r['n'] for r in idx}
    byname = {}
    byname2 = {}
    for r in idx:
        byname.setdefault(norm(r['n']), r['t'])
        k2 = ' '.join(norm(r['n']).split()[:2])
        byname2[k2] = r['t'] if k2 not in byname2 else None  # only unique prefixes
    try:
        cache = json.load(open(os.path.join(OUT, 'cusip.json')))
    except Exception:
        cache = {}

    data = []
    for m in MANAGERS:
        try:
            d = load_manager(m)
        except Exception as e:  # one bad filing must not stop the rest
            print('::warning::%s failed: %s' % (m[0], str(e)[:200])); d = None
        if d and d['Q']:
            data.append(d)
    if len(data) < len(MANAGERS) // 2:
        sys.exit('too few managers loaded (%d) - not publishing' % len(data))

    cus = set()
    for d in data:
        for q in d['Q'][:2]:
            cus.update(q['eq'].keys())
            cus.update(k[0] for k in q['opt'].keys())
        for q in d['Q'][2:]:
            cus.update(sorted(q['eq'], key=lambda c: -q['eq'][c]['v'])[:40])
    figi(sorted(cus), cache)
    json.dump(cache, open(os.path.join(OUT, 'cusip.json'), 'w'), separators=(',', ':'))

    def ticker(cu, name):
        c = cache.get(cu)
        t = c[0] if c else None
        if t:
            if t not in universe:
                t = aliases.get(t, t)
            if t not in universe and t.replace('-', '') in universe:
                t = t.replace('-', '')
            return t
        k = norm(name)
        if k in byname:
            return byname[k]
        k2 = ' '.join(k.split()[:2])
        return byname2.get(k2) if len(k2) >= 6 else None

    def title(s):
        return ' '.join(w if len(w) <= 3 and w.isupper() and w not in ('INC', 'COM', 'NEW', 'THE', 'CO') else w.capitalize() for w in (s or '').split())

    SAME = {'GOOG': 'GOOGL', 'BRK-A': 'BRK-B', 'FOX': 'FOXA', 'NWS': 'NWSA', 'FWONK': 'FWONA', 'LBRDA': 'LBRDK', 'LSXMK': 'LSXMA', 'UHAL': 'UHAL-B', 'HEI-A': 'HEI'}
    latest_all = max(d['Q'][0]['period'] for d in data)
    summary, owners, act_all = [], defaultdict(list), []
    for d in data:
        m, Q = d['m'], d['Q']
        mid = m[0]
        tot = [sum(o['v'] for o in q['eq'].values()) for q in Q]
        cur, prev = Q[0], (Q[1] if len(Q) > 1 else None)
        T0 = tot[0] or 1
        # shares history per CUSIP (split-adjusted backwards)
        hold = []
        for cu, o in sorted(cur['eq'].items(), key=lambda kv: -kv[1]['v']):
            p = prev['eq'].get(cu) if prev else None
            n, pn = o['n'], (p['n'] if p else 0.0)
            px = o['v'] / n if n else None
            ppx = p['v'] / p['n'] if p and p['n'] else None
            split = 1
            if pn and px and ppx:
                r, pr = n / pn, px / ppx
                for k in (2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 40, 50):
                    if abs(r / k - 1) < 0.08 and abs(r * pr - 1) < 0.4 and pr < 0.75:
                        split = k; break
                    if abs(r * k - 1) < 0.08 and abs(r * pr - 1) < 0.4 and pr > 1.4:
                        split = 1.0 / k; break
            pa = pn * split
            if not prev:
                act, ch = '', None
            elif pa <= 0:
                act, ch = 'new', None
            elif n > pa * 1.005:
                act, ch = 'add', n / pa - 1
            elif n < pa * 0.995:
                act, ch = 'cut', 1 - n / pa
            else:
                act, ch = '', 0.0
            eff = ((n - pa) * px / T0) if (px and prev) else None
            hs = []
            for q in Q[:NQ]:
                x = q['eq'].get(cu)
                hs.append(round(x['n']) if x else 0)
            t = ticker(cu, o['name'])
            hold.append({'t': t, 'n': title(cache.get(cu, [None, ''])[1] or o['name']) if cache.get(cu, [None, ''])[1] else title(o['name']),
                         'cu': cu, 'sh': round(n), 'v': round(o['v']), 'w': round(o['v'] / T0, 5), 'px': round(px, 2) if px else None,
                         'a': act, 'c': round(ch, 4) if ch is not None else None, 'e': round(eff, 5) if eff is not None else None,
                         'u': 1 if t in universe else 0, 'h': hs})
        sold = []
        if prev:
            Tp = tot[1] or 1
            for cu, p in sorted(prev['eq'].items(), key=lambda kv: -kv[1]['v']):
                if cu in cur['eq']:
                    continue
                t = ticker(cu, p['name'])
                sold.append({'t': t, 'n': title(cache.get(cu, [None, ''])[1] or p['name']), 'sh': round(p['n']), 'v': round(p['v']),
                             'w': round(p['v'] / Tp, 5), 'px': round(p['v'] / p['n'], 2) if p['n'] else None, 'u': 1 if t in universe else 0})
        opts = [{'t': ticker(k[0], o['name']), 'n': title(o['name']), 'pc': o['pc'], 'v': round(o['v']), 'sh': round(o['n'])}
                for k, o in sorted(cur['opt'].items(), key=lambda kv: -kv[1]['v'])][:30]
        stale = cur['period'] < quarter_back(latest_all, 1)
        q_hist = [{'p': q['period'], 'f': q['filed'], 'v': round(tot[i]), 'n': len(q['eq'])} for i, q in enumerate(Q)]
        top10 = sum(h['w'] for h in hold[:10])
        turnover = None
        if prev:
            turnover = round(sum(abs(h['e'] or 0) for h in hold) / 2 + sum(s['w'] for s in sold) / 2, 4)
        rec = {'id': mid, 'who': m[3], 'firm': m[4], 'fa': m[5], 'ffa': m[6], 'style': m[7], 'bio': m[8], 'sec': d['sec_name'],
               'cik': m[1], 'period': cur['period'], 'filed': cur['filed'], 'value': round(tot[0]), 'n': len(cur['eq']),
               'chg': round(tot[0] / tot[1] - 1, 4) if len(tot) > 1 and tot[1] else None, 'top10': round(top10, 4), 'turn': turnover,
               'stale': stale, 'nnew': sum(1 for h in hold if h['a'] == 'new'), 'nadd': sum(1 for h in hold if h['a'] == 'add'),
               'ncut': sum(1 for h in hold if h['a'] == 'cut'), 'nsold': len(sold),
               'top': [[h['t'] or '', h['n'], h['w']] for h in hold[:5]]}
        summary.append(rec)
        full = dict(rec, q=q_hist, hold=hold[:TOP], more=max(0, len(hold) - TOP), sold=sold[:60], opt=opts)
        json.dump(full, open(os.path.join(OUT, 'm', mid + '.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
        if not stale:
            agg = {}
            for h in hold:
                if h['t'] and h['w'] >= 0.001:
                    k = SAME.get(h['t'], h['t'])
                    if k in agg:
                        agg[k][1] += h['w']
                        if not agg[k][2]:
                            agg[k][2] = h['a']
                    else:
                        agg[k] = [mid, h['w'], h['a'], h['c'], h['n'] if k == h['t'] else (names_by_t.get(k) or h['n'])]
            for k, v in agg.items():
                v[1] = round(v[1], 5)
                owners[k].append(v)
            seen = set()
            for s in sold:
                if s['t'] and SAME.get(s['t'], s['t']) not in agg:
                    k = SAME.get(s['t'], s['t'])
                    if k not in seen:
                        seen.add(k); act_all.append((k, s['n'], mid, 'sold', s['w']))
            for h in hold:
                if h['t'] and h['a'] in ('new', 'add', 'cut'):
                    k = SAME.get(h['t'], h['t'])
                    if k not in seen:
                        seen.add(k); act_all.append((k, h['n'], mid, h['a'], h['e'] or 0))

    # most owned
    pop = []
    for t, L in owners.items():
        pop.append({'t': t, 'n': L[0][4], 'k': len(L), 'sw': round(sum(x[1] for x in L), 4),
                    'o': sorted([[x[0], x[1], x[2]] for x in L], key=lambda x: -x[1]), 'u': 1 if t in universe else 0})
    pop.sort(key=lambda r: (-r['k'], -r['sw']))
    # most bought / sold this quarter (by number of managers, then by portfolio effect)
    B, S = defaultdict(lambda: {'k': 0, 'new': 0, 'e': 0.0, 'o': []}), defaultdict(lambda: {'k': 0, 'sold': 0, 'e': 0.0, 'o': []})
    names = {}
    for t, n, mid, a, e in act_all:
        names[t] = n
        if a in ('new', 'add'):
            r = B[t]; r['k'] += 1; r['new'] += a == 'new'; r['e'] += e; r['o'].append([mid, a, round(e, 5)])
        else:
            r = S[t]; r['k'] += 1; r['sold'] += a == 'sold'; r['e'] += abs(e); r['o'].append([mid, a, round(abs(e), 5)])
    def lst(D):
        out = [dict(t=t, n=names[t], u=1 if t in universe else 0, **{k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()}) for t, r in D.items()]
        out.sort(key=lambda r: (-r['k'], -r['e']))
        return out[:80]
    summary.sort(key=lambda r: -r['value'])
    recent = sorted(summary, key=lambda r: r['filed'], reverse=True)
    index = {'as_of': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'latest': latest_all, 'managers': summary,
             'popular': pop[:100], 'buys': lst(B), 'sells': lst(S),
             'recent': [[r['id'], r['filed'], r['period']] for r in recent[:20]]}
    json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    json.dump({t: [[x[0], x[1], x[2]] for x in sorted(L, key=lambda x: -x[1])] for t, L in owners.items()},
              open(os.path.join(OUT, 'owners.json'), 'w'), separators=(',', ':'))
    json.dump(DEBUG, open(os.path.join(OUT, 'debug.json'), 'w'), indent=0)
    print('done: %d managers, %d stocks owned, latest quarter %s' % (len(summary), len(owners), latest_all))


def quarter_back(p, n):
    y, mth = int(p[:4]), int(p[5:7])
    q = (mth - 1) // 3 - n
    y += q // 4; q %= 4
    return '%04d-%02d-%02d' % (y, q * 3 + 3, 30 if q in (1, 2) else 31)


if __name__ == '__main__':
    main()
