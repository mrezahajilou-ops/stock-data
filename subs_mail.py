"""Subscription emails for sahamanaliz.com (runs in GitHub Actions; never prints names or addresses).

  python subs_mail.py cancel    every 15 min: reads new cancellation requests from /pages/cancel (Shopify contact
                                messages containing RZ-KUENDIGUNG) in the shop Gmail inbox, emails the customer a
                                confirmation (contract, type, end date, time received - §312k BGB) and Reza a to-do.
                                Processed messages get the Gmail label "rz-kuendigung-done", so nothing is sent twice.
  python subs_mail.py remind    daily: 30 days before a yearly auto-renewal (Stock Pro yearly, portfolio yearly), emails
                                the customer a reminder with the date, price and how to cancel. Only orders bought as a
                                subscription (line item with a selling plan) renew; one-time yearly purchases are skipped.
                                Skips anyone who already got a reminder in the last 25 days or whose cancellation was confirmed.

Secrets: GMAIL_USER, GMAIL_APP_PASSWORD (IMAP + SMTP), SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET (read_orders, read_all_orders).
"""
import datetime as dt
import email
import email.header
import email.utils
import html as H
import imaplib
import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SITE = 'https://sahamanaliz.com'
CANCEL_URL = SITE + '/pages/cancel'
DONE_LABEL = 'rz-kuendigung-done'
SUBJ_CONFIRM = 'Kündigungsbestätigung | تأیید لغو اشتراک – سهام آنالیز'
SUBJ_REMIND = 'Erinnerung: Verlängerung deines Jahresabos | یادآوری تمدید اشتراک سالانه – سهام آنالیز'
TEST = os.environ.get('TEST', '') not in ('', '0', 'false')
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
BERLIN = dt.timezone(dt.timedelta(hours=1))


def creds():
    user = re.sub(r'\s+', '', os.environ.get('GMAIL_USER', ''))
    pw = re.sub(r'\s+', '', os.environ.get('GMAIL_APP_PASSWORD', ''))
    if not user or not pw:
        sys.exit('GMAIL_USER / GMAIL_APP_PASSWORD missing')
    return user, pw


def imap():
    user, pw = creds()
    m = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    m.login(user, pw)
    return m


def page(title, inner, name=''):
    hi = ('سلام %s،' % H.escape(name)) if name else 'سلام،'
    return ('<!doctype html><html dir="rtl" lang="fa"><body style="margin:0;background:#efede6;padding:24px 12px;font-family:Vazirmatn,Tahoma,Arial,sans-serif;color:#1d1d1f">'
            '<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:18px;padding:26px 24px;direction:rtl;text-align:right;line-height:1.9">'
            '<div style="font-size:12.5px;color:#8a8f99;margin-bottom:10px">سهام آنالیز | sahamanaliz.com</div>'
            '<h1 style="font-size:20px;margin:0 0 14px;line-height:1.6">%s</h1><p style="margin:0 0 14px">%s</p>%s</div></body></html>'
            % (H.escape(title), hi, inner))


def table(rows):
    tr = ''.join('<tr><td style="padding:4px 0 4px 14px;color:#8a8f99;white-space:nowrap;vertical-align:top">%s</td>'
                 '<td style="padding:4px 0;font-weight:700" dir="auto">%s</td></tr>' % (H.escape(k), H.escape(v)) for k, v in rows)
    return '<table style="border-collapse:collapse;margin:0 0 14px;font-size:14px">%s</table>' % tr


def send(to, subject, html_body, bcc_self=False):
    user, pw = creds()
    if TEST:
        to = user
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr(('سهام آنالیز – Reza Hajilou', user))
    msg['To'] = to
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Message-ID'] = email.utils.make_msgid(domain='sahamanaliz.com')
    plain = re.sub(r'<[^>]+>', ' ', html_body.replace('<br>', '\n').replace('</tr>', '\n').replace('</p>', '\n'))
    msg.attach(MIMEText(re.sub(r'[ \t]+', ' ', plain), 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    rcpt = [to] + ([user] if bcc_self and to != user else [])
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60) as s:
        s.login(user, pw)
        s.sendmail(user, rcpt, msg.as_string())


def body_text(msg):
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', 'replace')
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            t = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', 'replace')
            return re.sub(r'<[^>]+>', '\n', t)
    return ''


def fields(text):
    """Shopify contact mail: 'Label:\\nvalue\\n\\n' blocks."""
    out = {}
    for m in re.finditer(r'(?m)^([^\n:]{1,40}):\s*\n(.*?)(?=\n\s*\n|\Z)', text, re.S):
        out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def run_cancel():
    m = imap()
    m.select('INBOX')
    typ, data = m.uid('SEARCH', None, 'X-GM-RAW', '"from:mailer@shopify.com RZ-KUENDIGUNG -label:%s newer_than:14d"' % DONE_LABEL)
    uids = (data[0] or b'').split() if typ == 'OK' else []
    print('new cancellation requests: %d' % len(uids))
    done = 0
    for uid in uids:
        typ, raw = m.uid('FETCH', uid, '(RFC822)')
        if typ != 'OK' or not raw or not raw[0]:
            continue
        msg = email.message_from_bytes(raw[0][1])
        f = fields(body_text(msg))
        to = (f.get('email') or f.get('e-mail') or '').strip()
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', to):
            print('::warning::one request without a valid email, left for manual handling')
            m.uid('STORE', uid, '+X-GM-LABELS', DONE_LABEL)
            continue
        when = email.utils.parsedate_to_datetime(msg['Date']).astimezone(BERLIN)
        rec = when.strftime('%d.%m.%Y, %H:%M Uhr (MEZ)')
        rows = [('Name / نام', f.get('name', '')), ('E-Mail / ایمیل', to),
                ('Vertrag / قرارداد', f.get('vertrag', '')),
                ('Art / نوع لغو', f.get('kuendigungsart', 'ordentliche Kündigung')),
                ('Zum / از کی', f.get('zeitpunkt', 'zum nächstmöglichen Zeitpunkt')),
                ('Eingang / زمان دریافت', rec)]
        if f.get('bestellnummer'):
            rows.insert(3, ('Bestellnummer / سفارش', f['bestellnummer']))
        if f.get('grund'):
            rows.append(('Grund / دلیل', f['grund']))
        inner = ('<p style="margin:0 0 12px">درخواست لغو اشتراکت رو دریافت کردیم. جزئیات:</p>' + table(rows) +
                 '<p style="margin:0 0 12px">لغو در اولین زمان ممکن انجام می‌شه و دیگه پولی از کارتت کم نمی‌شه. '
                 'اگه اشتراک سالانه‌ت بعد از سال اول تمدید شده، پول ماه‌های کامل باقی‌مونده به همون روش پرداخت برمی‌گرده.</p>'
                 '<p style="margin:0 0 12px;font-size:13px;color:#555" dir="ltr" lang="de">Hiermit bestätigen wir den Eingang deiner Kündigung '
                 '(Inhalt, Eingangszeitpunkt und gewünschter Beendigungszeitpunkt siehe oben). Wurde dein Jahresabo nach dem ersten Jahr '
                 'verlängert, erstatten wir die verbleibenden vollen Monate anteilig.</p>'
                 '<p style="margin:0;font-size:12px;color:#8a8f99">این ایمیل رو برای سوابقت نگه دار. سؤالی داشتی به همین ایمیل جواب بده.</p>')
        send(to, SUBJ_CONFIRM, page('درخواست لغو دریافت شد ✅', inner, f.get('name', '').split(' ')[0]), bcc_self=True)
        # to-do for Reza (to the shop inbox only)
        user, _ = creds()
        todo = ('<p>یک درخواست لغو اومد و تأییدش برای مشتری فرستاده شد. کارهای تو:</p><ol>'
                '<li>Shopify ← Apps ← Subscriptions ← Verträge: قرارداد این ایمیل رو پیدا کن و <b>Abbrechen / Cancel</b> بزن.</li>'
                '<li>اگه اشتراک سالانه بعد از سال اول تمدید شده: ماه‌های کامل باقی‌مونده رو از سفارش آخرش Refund کن.</li></ol>' + table(rows))
        if not TEST:
            send(user, 'TODO: Kündigung bearbeiten – ' + f.get('vertrag', '')[:40], page('درخواست لغو جدید', todo))
        m.uid('STORE', uid, '+X-GM-LABELS', DONE_LABEL)
        done += 1
    print('confirmations sent: %d' % done)
    m.logout()


ORDERS = '''query($c: String, $q: String) { orders(first: 100, after: $c, query: $q, sortKey: CREATED_AT) {
  nodes { createdAt email displayFinancialStatus customer { firstName email }
          lineItems(first: 10) { nodes { sku title sellingPlan { name } originalTotalSet { presentmentMoney { amount currencyCode } } } } }
  pageInfo { hasNextPage endCursor } } }'''


def is_yearly(li):
    sku = (li.get('sku') or '').upper()
    t = li.get('title') or ''
    return sku.startswith('PORTFOLIO') or 'سالانه' in t


def all_mail(m):
    """Name of Gmail's 'All Mail' folder (localized, e.g. '[Gmail]/Alle Nachrichten'), found by its \\All flag."""
    typ, data = m.list()
    for line in data or []:
        s = line.decode('utf-8', 'replace')
        if '\\All' in s:
            return s.rsplit(' "/" ', 1)[-1]
    return '"[Gmail]/All Mail"'


def gmail_sent_to(m, to, subject_word, days):
    m.select(m._rz_all, readonly=True)
    q = '"to:%s subject:(%s) newer_than:%dd"' % (to, subject_word, days)
    typ, data = m.uid('SEARCH', None, 'X-GM-RAW', q)
    return typ == 'OK' and bool((data[0] or b'').split())


def run_remind():
    from sync_shopify import token, gql
    tok = token()
    now = dt.datetime.now(dt.timezone.utc)
    lo, hi = (now - dt.timedelta(days=338)).date(), (now - dt.timedelta(days=330)).date()
    q = 'created_at:>=%s created_at:<=%s' % (lo, hi)
    cand, cur = {}, None
    while True:
        j = gql(tok, ORDERS, {'c': cur, 'q': q})
        if j.get('errors'):
            sys.exit('orders query failed: %s' % str(j['errors'])[:300])
        o = j['data']['orders']
        for n in o['nodes']:
            if n.get('displayFinancialStatus') not in ('PAID', 'PARTIALLY_REFUNDED'):
                continue
            for li in n['lineItems']['nodes']:
                if is_yearly(li) and li.get('sellingPlan'):
                    to = ((n.get('customer') or {}).get('email') or n.get('email') or '').strip().lower()
                    if to:
                        cand[to] = (n, li)
        if not o['pageInfo']['hasNextPage']:
            break
        cur = o['pageInfo']['endCursor']
    print('renewals in ~30 days: %d' % len(cand))
    if not cand:
        return
    m = imap()
    m._rz_all = all_mail(m)
    sent = 0
    for to, (n, li) in cand.items():
        if gmail_sent_to(m, to, 'Kündigungsbestätigung', 400) or gmail_sent_to(m, to, 'Erinnerung', 25):
            continue
        created = dt.datetime.fromisoformat(n['createdAt'].replace('Z', '+00:00'))
        renew = (created + dt.timedelta(days=365)).astimezone(BERLIN)
        money = ((li.get('originalTotalSet') or {}).get('presentmentMoney')) or {}
        price = ('%s %s' % (money.get('amount', ''), money.get('currencyCode', ''))).strip()
        name = ((n.get('customer') or {}).get('firstName') or '').strip()
        rows = [('اشتراک / Abo', li.get('title', '')), ('تاریخ تمدید / Verlängerung am', renew.strftime('%d.%m.%Y')),
                ('مبلغ / Betrag', price)]
        inner = ('<p style="margin:0 0 12px">اشتراک سالانه‌ت حدود ۳۰ روز دیگه خودکار تمدید می‌شه:</p>'.translate(FA) + table(rows) +
                 '<p style="margin:0 0 12px">اگه می‌خوای ادامه بدی، لازم نیست کاری کنی. اگه نمی‌خوای، قبل از تاریخ تمدید از '
                 '<b>حساب من ← اشتراک‌ها</b> یا این صفحه لغو کن:</p>'
                 '<p style="margin:0 0 14px"><a href="%s" style="display:inline-block;background:#C9A961;color:#15120A;text-decoration:none;font-weight:700;padding:11px 20px;border-radius:999px">لغو اشتراک</a></p>'
                 '<p style="margin:0 0 12px;font-size:13px;color:#555" dir="ltr" lang="de">Dein Jahresabo verlängert sich automatisch am oben genannten Datum. '
                 'Du kannst jederzeit kündigen; nach dem ersten Jahr mit einer Frist von höchstens einem Monat, zu viel gezahlte Monate werden erstattet.</p>'
                 % CANCEL_URL)
        send(to, SUBJ_REMIND, page('یادآوری تمدید اشتراک سالانه', inner, name))
        sent += 1
    print('reminders sent: %d' % sent)
    m.logout()


if __name__ == '__main__':
    mode = (sys.argv[1:] or ['cancel'])[0]
    {'cancel': run_cancel, 'remind': run_remind}[mode]()
