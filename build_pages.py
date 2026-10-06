#!/usr/bin/env python3
"""Build the content of one SEO page per stock (Shopify metaobject type `rz_stock`, URL /pages/stocks/<ticker>).

Input:  data/stocks/*.json (from build.py)
Output: pages/pages.jsonl  - one JSON object per line: {"handle", "fields": {...}} ready for metaobjectUpsert
The text is written in Persian from the same numbers and checks the interactive tool uses,
so every page is unique, factual and indexable (it is rendered server-side by the theme).
"""
import json, os, glob, datetime as dt
from collections import defaultdict

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
SRC = os.path.join(ROOT, 'data', 'stocks')
OUT = os.path.join(ROOT, 'pages')

FA_NAME = {
    'AAPL': 'اپل', 'MSFT': 'مایکروسافت', 'NVDA': 'انویدیا', 'AMZN': 'آمازون', 'GOOGL': 'آلفابت گوگل',
    'GOOG': 'آلفابت گوگل', 'META': 'متا', 'TSLA': 'تسلا', 'NFLX': 'نتفلیکس', 'AMD': 'ای‌ام‌دی',
    'INTC': 'اینتل', 'AVGO': 'برادکام', 'ORCL': 'اوراکل', 'CRM': 'سیلزفورس', 'ADBE': 'ادوبی', 'PLTR': 'پالانتیر',
    'MELI': 'مرکادولیبره', 'SE': 'سی لیمیتد', 'NKE': 'نایکی', 'MCD': 'مک‌دونالد', 'KO': 'کوکاکولا', 'PEP': 'پپسی‌کو',
    'JPM': 'جی‌پی مورگان', 'V': 'ویزا', 'MA': 'مسترکارت', 'BRK-B': 'برکشایر هاتاوی', 'BRK-A': 'برکشایر هاتاوی',
    'WMT': 'والمارت', 'COST': 'کاستکو', 'DIS': 'دیزنی', 'PYPL': 'پی‌پال', 'UBER': 'اوبر', 'ABNB': 'ایربی‌ان‌بی',
    'SBUX': 'استارباکس', 'BA': 'بوئینگ', 'XOM': 'اکسون موبیل', 'CVX': 'شورون', 'PFE': 'فایزر', 'JNJ': 'جانسون اند جانسون',
    'LLY': 'الی لیلی', 'NVO': 'نوو نوردیسک', 'UNH': 'یونایتدهلث', 'TSM': 'تی‌اس‌ام‌سی', 'ASML': 'ای‌اس‌ام‌ال',
    'QCOM': 'کوالکام', 'IBM': 'آی‌بی‌ام', 'CSCO': 'سیسکو', 'SHOP': 'شاپیفای', 'SPOT': 'اسپاتیفای', 'COIN': 'کوین‌بیس',
    'HOOD': 'رابین‌هود', 'SNOW': 'اسنوفلیک', 'MU': 'مایکرون', 'GS': 'گلدمن ساکس', 'BAC': 'بانک آو امریکا',
    'PG': 'پراکتر اند گمبل', 'HD': 'هوم دیپو', 'GE': 'جنرال الکتریک', 'F': 'فورد', 'GM': 'جنرال موتورز',
    'PODD': 'اینسولت', 'CNC': 'سنتین', 'AXP': 'امریکن اکسپرس', 'MRK': 'مرک', 'ABBV': 'اب‌وی', 'T': 'ای‌تی‌اند‌تی',
    'VZ': 'وریزون', 'TMUS': 'تی‌موبایل', 'CAT': 'کاترپیلار', 'LMT': 'لاکهید مارتین', 'RTX': 'آر‌تی‌ایکس',
}
FA_SECTOR = {
    'Technology': 'فناوری', 'Consumer Discretionary': 'کالاهای مصرفی غیرضروری', 'Industrials': 'صنعتی',
    'Health Care': 'سلامت و دارو', 'Finance': 'مالی', 'Telecommunications': 'مخابرات', 'Energy': 'انرژی',
    'Consumer Staples': 'کالاهای مصرفی ضروری', 'Basic Materials': 'مواد اولیه', 'Real Estate': 'املاک و مستغلات',
    'Utilities': 'خدمات عمومی', 'Miscellaneous': 'متفرقه',
}
AX = [('value', 'ارزش'), ('future', 'آینده'), ('past', 'گذشته'), ('health', 'سلامت مالی'), ('capital', 'بازگشت سرمایه')]
WHY = {
    'value': ['P/E کمتر از ۲۵', 'P/E کمتر از میانه‌ی صنعت', 'P/FCF کمتر از ۲۰', 'قیمت پایین‌تر از ارزش ذاتی (DCF با فرض متوسط)', 'PEG کمتر از ۱٫۵'],
    'future': ['رشد درآمد سال آخر بالای ۱۰٪', 'رشد سالانه‌ی درآمد ۳ ساله بالای ۱۰٪', 'حاشیه سود در حال بهبود', 'رشد سالانه‌ی جریان نقد آزاد ۳ ساله بالای ۱۰٪', 'سرمایه‌گذاری قوی در R&D یا رشد بالای ۲۰٪'],
    'past': ['رشد سالانه‌ی EPS ۵ ساله بالای ۱۰٪', 'رشد سالانه‌ی درآمد ۵ ساله بالای ۸٪', 'میانگین ROIC ۵ ساله بالای ۱۲٪', '۵ سال پیاپی سودده', 'ROE بالای ۱۵٪'],
    'health': ['نقد بیشتر از بدهی یا بدهی کم نسبت به حقوق صاحبان سهام', 'جریان نقد آزاد مثبت', 'پوشش بهره بالای ۵ برابر', 'بدهی کمتر از ۳ سال جریان نقد آزاد', 'بدهی‌ها کمتر از ۶۰٪ دارایی‌ها'],
    'capital': ['سود نقدی پرداخت می‌کنه', 'تعداد سهام در ۳ سال کم شده (بازخرید)', '۲۰ تا ۱۰۰٪ جریان نقد آزاد به سهامدار برگشته', '۳ سال پیاپی سود نقدی', 'پاداش سهامی کارکنان کمتر از ۵٪ درآمد'],
}
FD = str.maketrans('0123456789.-', '۰۱۲۳۴۵۶۷۸۹٫−')


def fa(x):
    return str(x).translate(FD)


def num(v, d=1):
    return None if v is None else round(float(v), d)


def pct(v, d=0):
    return None if v is None else fa(('%.' + str(d) + 'f') % (v * 100)) + '٪'


def big_fa(v):
    if v is None:
        return '—'
    a = abs(v)
    if a >= 1e12:
        return fa('%.2f' % (v / 1e12)) + ' هزار میلیارد دلار'
    if a >= 1e9:
        return fa('%.1f' % (v / 1e9)) + ' میلیارد دلار'
    return fa('%.0f' % (v / 1e6)) + ' میلیون دلار'


def verdict(t):
    if t is None:
        return 'نامشخص'
    return 'عالی' if t >= 4 else 'خوب' if t >= 3.25 else 'متوسط' if t >= 2.5 else 'ضعیف'


def page(d, related):
    t = d['ticker']
    a, s, sc, ck = d['annual'], d.get('summary') or {}, d.get('scores') or {}, d.get('checks') or {}
    m, r, L = d.get('market') or {}, d.get('ratios') or {}, d['annual'][-1]
    nm_en = (d.get('name') or t).strip()
    nm = FA_NAME.get(t)
    label = (nm + ' (' + t + ')') if nm else (nm_en + ' (' + t + ')')
    sector_fa = FA_SECTOR.get(m.get('sector') or '', m.get('sector') or '')
    tot = sc.get('total')
    strengths, weaknesses = [], []
    for k, _ in AX:
        for i, ok in enumerate(ck.get(k) or []):
            (strengths if ok else weaknesses).append(WHY[k][i])

    # ---- text ----
    p1 = ('%s از شرکت‌های %sبورس آمریکاست%s. ' % (label, ('بخش ' + sector_fa + ' در ') if sector_fa else '',
          (' و ارزش بازارش حدود ' + big_fa(m.get('mcap')) + ' است') if m.get('mcap') else ''))
    p1 += ('در آخرین سال مالی (%s) درآمدش %s و سود خالصش %s بوده' % (fa(L['fy']), big_fa(L.get('revenue')), big_fa(L.get('net_income'))))
    if L.get('net_margin') is not None:
        p1 += ' که یعنی حاشیه سود خالص ' + pct(L['net_margin'])
    p1 += '.'
    if tot is not None:
        p2 = ('امتیاز کلی %s در تحلیل ما %s از ۵ است (%s). ' % (label, fa('%.1f' % tot), verdict(tot)))
        best = max(AX, key=lambda x: sc.get(x[0]) or -1)
        worst = min(AX, key=lambda x: 9 if sc.get(x[0]) is None else sc[x[0]])
        p2 += ('قوی‌ترین بخشش «%s» با %s از ۵ و ضعیف‌ترین بخشش «%s» با %s از ۵ است.' %
               (best[1], fa(sc.get(best[0])), worst[1], fa(sc.get(worst[0]))))
    else:
        p2 = 'برای این سهم داده‌ی کافی برای امتیازدهی کامل وجود ندارد.'
    bits = []
    if r.get('pe'):
        bits.append('P/E حدود ' + fa('%.1f' % r['pe']))
    if r.get('pfcf'):
        bits.append('P/FCF حدود ' + fa('%.1f' % r['pfcf']))
    if s.get('rev_cagr_5y') is not None:
        bits.append('رشد سالانه‌ی درآمد ۵ ساله ' + pct(s['rev_cagr_5y']))
    if s.get('roic_avg_5y') is not None:
        bits.append('میانگین ROIC ۵ ساله ' + pct(s['roic_avg_5y']))
    p3 = ('مهم‌ترین اعداد: ' + '، '.join(bits) + '.') if bits else ''
    if r.get('fair_mcap') and m.get('mcap'):
        g = r['fair_mcap'] / m['mcap'] - 1
        p3 += (' بر اساس DCF با فرض‌های متوسط، ارزش ذاتی تقریباً %s %s از قیمت فعلی است.' %
               (pct(abs(g)), 'بالاتر' if g >= 0 else 'پایین‌تر'))
    summary = '\n\n'.join(x for x in (p1, p2, p3) if x)

    title = 'تحلیل سهام %s به فارسی | امتیاز %s از ۵، ارزش ذاتی و صورت‌های مالی' % (label, fa('%.1f' % tot) if tot is not None else '—')
    desc = ('تحلیل فارسی سهم %s: امتیاز %s از ۵ در ارزش، رشد، کارنامه، سلامت مالی و بازگشت سرمایه؛ P/E، جریان نقد آزاد، ارزش ذاتی DCF و صورت‌های مالی ۱۰ ساله از گزارش‌های رسمی SEC.'
            % (label, fa('%.1f' % tot) if tot is not None else '—'))

    hist = [{'fy': x['fy'], 'rev': x.get('revenue'), 'ni': x.get('net_income'), 'fcf': x.get('fcf'),
             'nm': num(x.get('net_margin'), 4), 'roic': num(x.get('roic'), 4)} for x in a[-6:]]
    data = {
        't': t, 'name': nm_en, 'fa': nm, 'sector': m.get('sector'), 'sector_fa': sector_fa, 'industry': m.get('industry'),
        'price': m.get('price'), 'mcap': m.get('mcap'), 'as_of': m.get('as_of'),
        'scores': {k: sc.get(k) for k, _ in AX}, 'total': tot, 'verdict': verdict(tot),
        'axes': [{'k': k, 'fa': f, 'v': sc.get(k)} for k, f in AX],
        'strengths': strengths[:8], 'weaknesses': weaknesses[:8],
        'ratios': {k: num(r.get(k), 2) for k in ('pe', 'pfcf', 'ps', 'pb', 'peg', 'ev_ebitda')},
        'yields': {k: num(r.get(k), 4) for k in ('div_yield', 'fcf_yield', 'shareholder_yield')},
        'fair_gap': num(r['fair_mcap'] / m['mcap'] - 1, 4) if (r.get('fair_mcap') and m.get('mcap')) else None,
        'growth': {k: num(s.get(k), 4) for k in ('rev_cagr_1y', 'rev_cagr_5y', 'eps_cagr_5y', 'fcf_cagr_3y', 'roic_avg_5y', 'net_margin_avg_5y')},
        'hist': hist, 'related': related,
    }
    fields = {'ticker': t, 'name': nm_en, 'sector': sector_fa or '', 'seo_title': title[:255], 'seo_description': desc,
              'summary': summary, 'data': json.dumps(data, ensure_ascii=False, separators=(',', ':')),
              'updated': dt.date.today().isoformat()}
    if tot is not None:
        fields['score_total'] = str(tot)
    return {'handle': t.lower(), 'fields': fields}


def main():
    docs = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.json'))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not d.get('annual') or not (d.get('market') or {}).get('mcap'):
            continue  # pages only for listed stocks with a market value
        docs.append(d)
    by_ind = defaultdict(list)
    for d in docs:
        by_ind[(d['market'].get('industry') or d['market'].get('sector') or '')].append(d)
    os.makedirs(OUT, exist_ok=True)
    n = 0
    with open(os.path.join(OUT, 'pages.jsonl'), 'w') as out:
        for d in docs:
            peers = sorted((x for x in by_ind[(d['market'].get('industry') or d['market'].get('sector') or '')] if x['ticker'] != d['ticker']),
                           key=lambda x: -(x['market'].get('mcap') or 0))[:6]
            related = [{'t': x['ticker'], 'n': FA_NAME.get(x['ticker']) or x.get('name'), 's': (x.get('scores') or {}).get('total')} for x in peers]
            out.write(json.dumps(page(d, related), ensure_ascii=False) + '\n')
            n += 1
    print('pages', n)


if __name__ == '__main__':
    main()
