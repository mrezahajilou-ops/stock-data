"""Watchdog: checks that every automatic job, the site, the worker and the contest are healthy, and emails Reza when not.

Checks
  1. GitHub workflows  - the newest successful run is not older than the job's allowed age, and the two newest finished
                         runs are not both failures (one failure that fixed itself next run is not reported).
  2. Site              - the home page and one stock page answer 200.
  3. Worker            - /c/quotes.json answers and, during the US regular session, is at most 45 minutes old.
  4. Contest (public)  - /c/board answers; every value is a sane number; no profile jumped more than 30% since the
                         previous watchdog run (catches double fills like 2026-11-10).
  5. Contest (deep)    - /c/audit, written nightly by the worker (cash ledger, negative cash, duplicate fills, stuck
                         orders, frozen tickers). Skipped quietly until the worker version with /c/audit is deployed.

Email (Gmail SMTP, GMAIL_USER -> GMAIL_USER, i.e. only to Reza)
  - when a new problem appears
  - once a day while problems persist
  - once when everything is fine again
State lives in branch "watchdog" (state.json), so nothing is mailed twice.

Env: GITHUB_TOKEN, GITHUB_REPOSITORY, GMAIL_USER, GMAIL_APP_PASSWORD, STATE_IN, STATE_OUT, TEST=1 (send a test mail), DRY=1 (no mail).
Nothing private is printed: the contest output is ids and numbers only, never holdings.
"""
import json, os, re, sys, math, smtplib, time, urllib.request, urllib.error, datetime as dt
from email.mime.text import MIMEText
from email.header import Header

REPO = os.environ.get('GITHUB_REPOSITORY', 'mrezahajilou-ops/stock-data')
TOKEN = os.environ.get('GITHUB_TOKEN', '')
WORKER = 'https://rz-events.mreza-hajilou.workers.dev'
SITE = 'https://sahamanaliz.com'
TEST = os.environ.get('TEST', '') not in ('', '0', 'false')
DRY = os.environ.get('DRY', '') not in ('', '0', 'false')
NOW = dt.datetime.now(dt.timezone.utc)

# workflow file -> (Farsi label, max hours since the last success). GitHub delays scheduled runs by hours,
# so the limits are generous: they catch a job that is really dead, not one that is merely late.
JOBS = {
    'quotes.yml':         ('قیمت‌های لحظه‌ای', 6),
    'fast.yml':           ('مسیر سریع گزارش‌های مالی جدید', 6),
    'portfolio.yml':      ('بازده پورتفوی رضا', 8),
    'gold.yml':           ('صفحه‌ی طلا و نقره', 8),
    'subs-mail.yml':      ('ایمیل‌های اشتراک (لغو، یادآوری تمدید)', 12),
    'alerts.yml':         ('ایمیل معاملات به مشترک‌های پورتفو', 12),
    'extras.yml':         ('اخبار و معاملات داخلی‌ها', 24),
    'superinvestors.yml': ('سوپر سرمایه‌گذارها', 48),
    'calendar.yml':       ('تقویم گزارش‌ها', 60),
    'earnings.yml':       ('تاریخچه‌ی گزارش‌ها', 60),
    'estimates.yml':      ('پیش‌بینی تحلیلگرها', 60),
    'contest-data.yml':   ('داده‌های مسابقه (نمادها، سود نقدی، اسپلیت)', 60),
    'top30.yml':          ('۳۰ سهم برتر', 80),
    'sec-build.yml':      ('ساخت داده‌های گزارش‌های رسمی', 80),
    'pages.yml':          ('صفحه‌های سئوی سهام', 80),
    'prices.yml':         ('تاریخچه‌ی قیمت', 80),
    'bench.yml':          ('شاخص‌های مقایسه (SPY، QQQ)', 80),
}


def get(url, gh=False, timeout=30):
    h = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 rz-watchdog',
         'Accept': 'application/json' if (gh or '/c/' in url) else 'text/html,*/*'}
    if gh and TOKEN:
        h['Authorization'] = 'Bearer ' + TOKEN
        h['Accept'] = 'application/vnd.github+json'
    r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout)
    return r.status, r.read()


def getj(url, gh=False):
    for a in range(3):
        try:
            return json.loads(get(url, gh)[1])
        except Exception:
            if a == 2:
                raise
            time.sleep(5)


def age_h(iso):
    return (NOW - dt.datetime.fromisoformat(iso.replace('Z', '+00:00'))).total_seconds() / 3600


def check_jobs(issues):
    for wf, (label, max_h) in JOBS.items():
        try:
            runs = getj(f'https://api.github.com/repos/{REPO}/actions/workflows/{wf}/runs?per_page=20', gh=True)['workflow_runs']
        except Exception as e:
            issues['gh-api'] = 'خواندن وضعیت کارهای گیت‌هاب ممکن نشد: ' + type(e).__name__
            return
        done = [r for r in runs if r['status'] == 'completed' and r['conclusion'] in ('success', 'failure', 'timed_out')]
        ok = [r for r in done if r['conclusion'] == 'success']
        if len(done) >= 2 and done[0]['conclusion'] != 'success' and done[1]['conclusion'] != 'success':
            issues['fail:' + wf] = f'«{label}» دو بار پشت سر هم شکست خورده ({wf}).'
        elif not ok:
            issues['stale:' + wf] = f'«{label}» در ۲۰ اجرای آخر هیچ اجرای موفقی نداشته ({wf}).'
        elif age_h(ok[0]['updated_at']) > max_h:
            issues['stale:' + wf] = f'«{label}» {age_h(ok[0]["updated_at"]):.0f} ساعته موفق اجرا نشده (حد مجاز {max_h} ساعت، {wf}).'


def us_session():
    """True during the US regular session (Mon-Fri 9:30-16:00 New York), DST-aware without extra packages."""
    y = NOW.year
    # DST: second Sunday of March 07:00 UTC .. first Sunday of November 06:00 UTC
    def nth_sunday(month, n):
        d = dt.datetime(y, month, 1, tzinfo=dt.timezone.utc)
        d += dt.timedelta(days=(6 - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    dst = nth_sunday(3, 2) + dt.timedelta(hours=7) <= NOW < nth_sunday(11, 1) + dt.timedelta(hours=6)
    ny = NOW - dt.timedelta(hours=4 if dst else 5)
    m = ny.hour * 60 + ny.minute
    return ny.weekday() < 5 and 570 <= m < 960


def check_site(issues):
    for name, url in (('صفحه‌ی اصلی', SITE + '/'), ('صفحه‌ی سهم اپل', SITE + '/pages/stocks/aapl')):
        try:
            st, body = get(url, timeout=40)
            if st != 200 or len(body) < 2000:
                issues['site:' + url] = f'{name} درست باز نمی‌شود (کد {st}).'
        except urllib.error.HTTPError as e:
            issues['site:' + url] = f'{name} باز نمی‌شود (کد {e.code}).'
        except Exception as e:
            issues['site:' + url] = f'{name} باز نمی‌شود ({type(e).__name__}).'


def check_worker(issues):
    try:
        q = getj(WORKER + '/c/quotes.json')
        h = age_h(q['as_of'])
        if us_session() and h > 0.75:
            issues['quotes-age'] = f'قیمت‌های ورکر {h * 60:.0f} دقیقه است به‌روز نشده (بازار آمریکا باز است).'
        if (q.get('n') or 0) < 3000:
            issues['quotes-n'] = f'ورکر فقط {q.get("n")} قیمت دارد (عادی بیش از ۳۰۰۰).'
    except Exception as e:
        issues['worker'] = f'ورکر کلادفلر (قیمت‌ها و مسابقه) جواب نمی‌دهد ({type(e).__name__}).'


def check_contest(issues, state):
    try:
        b = getj(WORKER + '/c/board')
    except Exception as e:
        issues['board'] = f'جدول مسابقه باز نمی‌شود ({type(e).__name__}).'
        return
    prev = state.get('board') or {}
    cur = {}
    for r in b.get('rows') or []:
        pid, v = str(r.get('id')), r.get('value')
        if not isinstance(v, (int, float)) or math.isnan(v) or v <= 0 or v > 1_000_000:
            issues['value:' + pid] = f'ارزش پورتفوی شماره‌ی {pid} در مسابقه غیرعادی است: {v}'
            continue
        cur[pid] = v
        if pid in prev and prev[pid] > 0 and abs(v / prev[pid] - 1) > 0.30:
            issues['jump:' + pid] = (f'ارزش پورتفوی شماره‌ی {pid} از آخرین بررسی {(v / prev[pid] - 1) * 100:+.0f}% تغییر کرده '
                                     f'({prev[pid]:,.0f} → {v:,.0f} دلار). احتمال خطای قیمت یا معامله‌ی تکراری.')
    state['board'] = cur
    # deep audit written by the worker each night (ids, codes and numbers only)
    try:
        a = getj(WORKER + '/c/audit')
    except Exception:
        return  # not deployed yet
    if a.get('as_of') and age_h(a['as_of']) > 80:
        issues['audit-age'] = 'بررسی شبانه‌ی مسابقه در ورکر بیش از ۳ روز است اجرا نشده.'
    for x in a.get('issues') or []:
        issues['audit:%s:%s' % (x.get('code'), x.get('pid'))] = 'مسابقه: ' + str(x.get('fa') or x.get('code'))


def send(subject, lines):
    user = re.sub(r'\s+', '', os.environ.get('GMAIL_USER', ''))
    pw = re.sub(r'\s+', '', os.environ.get('GMAIL_APP_PASSWORD', ''))
    if not user or not pw:
        print('no Gmail secrets: mail skipped')
        return False
    li = ''.join(f'<li style="margin:6px 0">{x}</li>' for x in lines)
    html = (f'<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;font-size:15px;line-height:1.8">'
            f'<ul>{li}</ul><p style="color:#888;font-size:12px">نگهبان خودکار سهام آنالیز · '
            f'<bdi>{NOW:%Y-%m-%d %H:%M} UTC</bdi> · <a href="https://github.com/{REPO}/actions">وضعیت کارها</a></p></div>')
    msg = MIMEText(html, 'html', 'utf-8')
    msg['Subject'], msg['From'], msg['To'] = str(Header(subject, 'utf-8')), user, user
    if DRY:
        print('DRY mail:', subject, *lines, sep='\n  ')
        return True
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60) as s:
        s.login(user, pw)
        s.sendmail(user, [user], msg.as_string())
    return True


def main():
    sin, sout = os.environ.get('STATE_IN', 'state_in.json'), os.environ.get('STATE_OUT', 'state.json')
    try:
        state = json.load(open(sin))
    except Exception:
        state = {}
    if TEST:
        send('آزمایش نگهبان سهام آنالیز', ['این یک ایمیل آزمایشی است. اگر این را می‌بینی، هشدارها به دستت می‌رسند.'])
        return
    issues = {}
    check_jobs(issues)
    check_site(issues)
    check_worker(issues)
    check_contest(issues, state)

    old = state.get('issues') or {}
    new = [k for k in issues if k not in old]
    last = state.get('last_mail')
    stale_mail = not last or age_h(last) >= 24
    print('issues:', len(issues), '| new:', len(new))
    for k in sorted(issues):
        print(' -', k, '|', issues[k])   # texts hold job names and numbers only, nothing private
    mailed = False
    if issues and (new or stale_mail):
        order = sorted(issues, key=lambda k: (k not in new, k))
        lines = [('🆕 ' if k in new else '') + issues[k] for k in order]
        mailed = send(f'⚠️ سهام آنالیز: {len(issues)} مشکل' + (f' ({len(new)} مورد جدید)' if new else ''), lines)
    elif not issues and old:
        mailed = send('✅ سهام آنالیز: همه‌چیز دوباره درست است', [f'{len(old)} مشکل قبلی برطرف شد.'])
    state['issues'] = {k: old.get(k, NOW.isoformat()) for k in issues}
    if mailed:
        state['last_mail'] = NOW.isoformat()
    state['checked'] = NOW.isoformat()
    json.dump(state, open(sout, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
