#!/usr/bin/env python3
"""Daily Persian post drafts for Reza's X / Instagram, emailed to him (GMAIL_USER -> GMAIL_USER).

Nothing is posted anywhere: these are ready-to-paste texts built from the site's own data, each with a
link to the matching page so posts bring visitors to sahamanaliz.com.
  1-2. the most notable earnings reports of the last day (pages/articles.json from build_earnings.py)
  3.   "list of the day" (rotates through the guide pages, top 5 names)
  4.   one super investor's portfolio (rotates daily)
Env: GMAIL_USER, GMAIL_APP_PASSWORD, DRY=1 (print only).
"""
import json, os, re, smtplib, datetime as dt
from email.mime.text import MIMEText
from email.header import Header

from build_pages import FA_NAME, fa, pct
from build_guides import load, rank_pages, sector_pages, git_json, date_fa

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
SITE = 'https://sahamanaliz.com'
TODAY = dt.date.today()


def nm(t, en=None):
    """Persian name when we have one, else the cashtag (keeps Latin words out of Persian sentences)."""
    return FA_NAME.get(t) or ('$' + t)


def earnings_drafts():
    try:
        arts = json.load(open(os.path.join(ROOT, 'pages', 'articles.json')))['articles']
    except Exception:
        return []
    since = (TODAY - dt.timedelta(days=2)).isoformat()
    recent = [a for a in arts if a['date'][:10] >= since]
    out = []
    for a in recent[:40]:
        t = a['tags'][0]
        m = re.search(r'سود هر سهم ([^ ]+) دلار در برابر پیش‌بینی ([^ ]+) دلار', a['seo_desc'])
        if not m:
            continue
        word = a['title'].rsplit(':', 1)[-1].strip()
        q = re.search(r'در (سه‌ماهه‌ی منتهی به [^:]+):', a['title'])
        out.append((t, '📊 گزارش سود %s %s\n\n%s\nسود هر سهم: %s دلار\nپیش‌بینی تحلیلگرها: %s دلار\n\nجزئیات، چهار فصل اخیر و ارزش‌گذاری 👇\n%s/blogs/earnings-reports/%s\n\n#سهام_آمریکا #گزارش_مالی $%s'
                    % (nm(t), ('(' + q.group(1) + ')') if q else '', word, m.group(1), m.group(2), SITE, a['handle'], t)))
    # the articles are newest first; prefer names people know (Persian name available)
    out.sort(key=lambda x: 0 if x[0] in FA_NAME else 1)
    return [d for _, d in out[:2]]


def list_draft(U):
    pages = rank_pages(U) + sector_pages(U)
    p = pages[TODAY.toordinal() % len(pages)]
    names = re.findall(r'href="/pages/stocks/([a-z0-9\-\.]+)"', p['html'])
    seen, top = set(), []
    for t in names:
        if t not in seen:
            seen.add(t)
            top.append(t.upper())
        if len(top) == 5:
            break
    lines = '\n'.join('%s. %s' % (fa(i + 1), nm(t)) for i, t in enumerate(top))
    return '📋 %s (به‌روز %s)\n\n%s\n\nفهرست کامل با امتیاز و ارزش ذاتی 👇\n%s/pages/%s\n\n#سهام_آمریکا #سرمایه_گذاری' % (
        p['title'], date_fa(TODAY), lines, SITE, p['handle'])


def guru_draft():
    idx = git_json(os.environ.get('SI_REF', 'origin/superinvestors'), 'index.json') or {}
    mans = idx.get('managers') or []
    if not mans:
        return None
    m = mans[TODAY.toordinal() % min(len(mans), 25)]
    top = m.get('top') or []
    lines = '\n'.join('%s. %s، %s از پورتفو' % (fa(i + 1), nm(x[0]), pct(x[2], 1)) for i, x in enumerate(top[:5]))
    return '🧠 %s چه سهامی دارد؟\n\n%s\n\nاین فصل: %s خرید جدید، %s فروش کامل\nپورتفوی کامل و همه‌ی خرید و فروش‌ها 👇\n%s/pages/portfolio-%s\n\n#سهام_آمریکا #سرمایه_گذاری' % (
        m['fa'], lines, fa(m.get('nnew', 0)), fa(m.get('nsold', 0)), SITE, m['id'])


def send(subject, html):
    user = re.sub(r'\s+', '', os.environ.get('GMAIL_USER', ''))
    pw = re.sub(r'\s+', '', os.environ.get('GMAIL_APP_PASSWORD', ''))
    if not user or not pw:
        print('no mail credentials')
        return
    msg = MIMEText(html, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = user
    msg['To'] = user
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60) as s:
        s.login(user, pw)
        s.sendmail(user, [user], msg.as_string())


def main():
    U = load()
    drafts = earnings_drafts() + [list_draft(U)]
    g = guru_draft()
    if g:
        drafts.append(g)
    blocks = ''.join('<div style="background:#f6f6f6;border-radius:10px;padding:14px 16px;margin:14px 0;white-space:pre-wrap;font-size:15px;line-height:1.9">%s</div>'
                     % d.replace('&', '&amp;').replace('<', '&lt;') for d in drafts)
    html = ('<div dir="rtl" style="font-family:Tahoma,Vazirmatn,sans-serif">'
            '<p>پیش‌نویس‌های امروز برای ایکس و اینستاگرام. هیچ‌کدام منتشر نشده؛ هر کدام را خواستی کپی کن.</p>%s'
            '<p style="color:#888;font-size:12px">ساخته‌شده خودکار از داده‌های سهام آنالیز · %s</p></div>' % (blocks, date_fa(TODAY)))
    print('\n\n----\n\n'.join(drafts))
    if not os.environ.get('DRY'):
        send('✍️ پیش‌نویس پست‌های امروز – ' + date_fa(TODAY), html)


if __name__ == '__main__':
    main()
