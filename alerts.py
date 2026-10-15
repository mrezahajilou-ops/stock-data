#!/usr/bin/env python3
"""Trade alerts for Reza's paid portfolio (https://rezahajiloubooks.com/pages/portfolio).

Every run:
  1. reads all `rz_trade` metaobjects from Shopify and compares them with the ids already announced
     (metaobject rz_alerts/main -> state.sent); only trades entered in the last 7 days and not history_only count
  2. builds the subscriber list from Shopify customers tagged `portfolio-alerts`
       - verified = has the tag `pro` or `portfolio`, or a paid order of product `portfolio-pro` in the last 380 days
         (same rule as the page's access check, snippets/rz-portfolio-access.liquid)
       - on/off and address from tags: newest `alert-to:<unix>:<email>` vs newest `alert-off:<unix>` (newest wins)
  3. sends one Farsi email per subscriber over Gmail SMTP (GMAIL_USER / GMAIL_APP_PASSWORD) and records the ids

Manual mode (workflow_dispatch): ALERT_SUBJECT + ALERT_BODY env -> the same list gets that message instead.
TEST=1 sends everything to GMAIL_USER only (nothing to subscribers) and records nothing.

Holdings are PRIVATE: this script never prints trades, emails or names to the log (only counts).
Auth: SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET (scopes: read_metaobjects, write_metaobjects, read_customers, read_orders).
"""
import json, os, re, sys, smtplib, datetime as dt, html as H
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_shopify import token, gql  # noqa: E402

SITE = 'https://rezahajiloubooks.com'
PAGE = SITE + '/pages/portfolio'
TEST = os.environ.get('TEST', '') not in ('', '0', 'false')
RECENT_DAYS = 7

TRADES = '''query($c: String) { metaobjects(type: "rz_trade", first: 250, after: $c) {
  nodes { id updatedAt fields { key value } } pageInfo { hasNextPage endCursor } } }'''
STATE = '''{ metaobjectByHandle(handle: {type: "rz_alerts", handle: "main"}) { id fields { key value } } }'''
UPDATE = '''mutation($id: ID!, $f: [MetaobjectFieldInput!]!) { metaobjectUpdate(id: $id, metaobject: {fields: $f}) {
  metaobject { id } userErrors { field message } } }'''
SUBS = '''query($c: String) { customers(first: 100, after: $c, query: "tag:portfolio-alerts") {
  nodes { id email firstName tags
          orders(first: 25, reverse: true, query: "financial_status:paid OR financial_status:partially_refunded") {
            nodes { createdAt lineItems(first: 10) { nodes { product { handle } } } } } }
  pageInfo { hasNextPage endCursor } } }'''

FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ACT = {'BUY': 'خرید', 'SELL': 'فروش', 'OPEN': 'افتتاح پوزیشن', 'DIVIDEND': 'سود نقدی', 'DEPOSIT': 'واریز', 'WITHDRAW': 'برداشت'}


def fa(n, d=2):
    if n is None:
        return ''
    s = ('{:,.%df}' % d).format(n).rstrip('0').rstrip('.') if d else '{:,.0f}'.format(n)
    return s.translate(FA)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_trades(tok):
    out, cur = [], None
    while True:
        j = gql(tok, TRADES, {'c': cur})
        mo = ((j.get('data') or {}).get('metaobjects')) or {}
        for n in mo.get('nodes') or []:
            f = {x['key']: x['value'] for x in n['fields']}
            out.append({'id': n['id'], 'up': n.get('updatedAt') or '', 'd': f.get('date') or '', 'a': (f.get('action') or '').upper(),
                        't': (f.get('ticker') or '').strip().upper(), 'n': num(f.get('shares')), 'p': num(f.get('price')),
                        'm': num(f.get('amount')), 'x': (f.get('note') or '').strip(), 'h': f.get('history_only') == 'true'})
        if not (mo.get('pageInfo') or {}).get('hasNextPage'):
            break
        cur = mo['pageInfo']['endCursor']
    out.sort(key=lambda t: t['d'])
    return out


def load_subs(tok):
    """[(email, first_name)] of verified, opted-in subscribers. Never printed."""
    out, cur, now = {}, None, dt.datetime.now(dt.timezone.utc)
    while True:
        j = gql(tok, SUBS, {'c': cur})
        if j.get('errors'):
            sys.exit('customers query failed (missing read_customers / read_orders scope?): %s' % json.dumps(j['errors'])[:300])
        cs = ((j.get('data') or {}).get('customers')) or {}
        for c in cs.get('nodes') or []:
            tags = [t.strip() for t in (c.get('tags') or [])]
            if 'portfolio-alerts' not in tags:
                continue
            on_ts, off_ts, to = 0, 0, (c.get('email') or '').strip().lower()
            for t in tags:
                m = re.match(r'^alert-to:(\d+):(.+@.+\..+)$', t)
                if m and int(m.group(1)) > on_ts:
                    on_ts, to = int(m.group(1)), m.group(2).strip().lower()
                m = re.match(r'^alert-off:(\d+)$', t)
                if m:
                    off_ts = max(off_ts, int(m.group(1)))
            if not on_ts or off_ts >= on_ts:
                continue  # switched off (or never properly activated)
            ok = 'pro' in tags or 'portfolio' in tags
            if not ok:
                for o in ((c.get('orders') or {}).get('nodes') or []):
                    age = now - dt.datetime.fromisoformat(o['createdAt'].replace('Z', '+00:00'))
                    if age.days <= 380 and any(((li.get('product') or {}).get('handle')) == 'portfolio-pro'
                                               for li in ((o.get('lineItems') or {}).get('nodes') or [])):
                        ok = True; break
            if not ok:
                continue
            if to:
                out[to] = (c.get('firstName') or '').strip()
        if not (cs.get('pageInfo') or {}).get('hasNextPage'):
            break
        cur = cs['pageInfo']['endCursor']
    return sorted(out.items())


def trade_lines(trades):
    rows = []
    for t in trades:
        a = ACT.get(t['a'], t['a'])
        when = t['d'][:10].translate(FA)
        if t['a'] in ('BUY', 'SELL', 'OPEN') and t['t']:
            body = '%s <b dir="ltr">%s</b>' % (a, H.escape(t['t']))
            det = []
            if t['n']:
                det.append('%s سهم' % fa(t['n'], 2))
            if t['p']:
                det.append('قیمت <span dir="ltr">$%s</span>' % fa(t['p'], 2))
            if t['n'] and t['p']:
                det.append('جمعاً <span dir="ltr">$%s</span>' % fa(t['n'] * t['p'], 0))
            if det:
                body += ' — ' + ' · '.join(det)
        elif t['a'] == 'DIVIDEND' and t['t']:
            body = 'سود نقدی <b dir="ltr">%s</b>' % H.escape(t['t'])
            if t['m']:
                body += ' — <span dir="ltr">$%s</span>' % fa(t['m'], 2)
        else:
            body = a + ((' — <span dir="ltr">$%s</span>' % fa(t['m'], 0)) if t['m'] else '')
        note = ('<div style="margin:6px 0 0;color:#444;line-height:1.9">%s</div>' % H.escape(t['x']).replace('\n', '<br>')) if t['x'] else ''
        rows.append('<li style="margin:0 0 14px;padding:12px 14px;background:#f7f5ef;border-radius:12px;list-style:none">'
                    '<div style="font-size:12.5px;color:#8a8f99;margin-bottom:4px">%s</div><div style="font-size:16px">%s</div>%s</li>' % (when, body, note))
    return ''.join(rows)


def subject_for(trades):
    live = [t for t in trades if t['a'] in ('BUY', 'SELL') and t['t']]
    if len(live) == 1:
        return 'پورتفوی رضا: %s %s' % (ACT[live[0]['a']], live[0]['t'])
    if live:
        return 'پورتفوی رضا: %s معامله‌ی جدید (%s)' % (fa(len(live), 0), '، '.join(sorted({t['t'] for t in live})))
    return 'پورتفوی رضا: به‌روزرسانی جدید'


def render(title, inner, name=''):
    hi = ('سلام %s،' % H.escape(name)) if name else 'سلام،'
    return ('<!doctype html><html dir="rtl" lang="fa"><body style="margin:0;background:#efede6;padding:24px 12px;font-family:Vazirmatn,Tahoma,Arial,sans-serif;color:#1d1d1f">'
            '<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:18px;padding:26px 24px;direction:rtl;text-align:right">'
            '<div style="font-size:12.5px;color:#8a8f99;margin-bottom:10px">هشدار فوری · پورتفوی رضا</div>'
            '<h1 style="font-size:20px;margin:0 0 14px;line-height:1.6">%s</h1><p style="margin:0 0 14px;line-height:1.9">%s</p>%s'
            '<p style="margin:18px 0 0"><a href="%s" style="display:inline-block;background:#C9A961;color:#15120A;text-decoration:none;font-weight:700;padding:11px 20px;border-radius:999px">دیدن پورتفوی و توضیحات</a></p>'
            '<p style="margin:22px 0 0;font-size:12px;color:#8a8f99;line-height:1.9">این ایمیل رو می‌گیری چون هشدار معاملات رو در صفحه‌ی پورتفوی فعال کردی. آموزشیه و توصیه‌ی خرید یا فروش نیست. '
            'برای تغییر ایمیل یا خاموش کردن هشدار به <a href="%s#alerts" style="color:#8a8f99">صفحه‌ی پورتفوی</a> برو.</p></div></body></html>'
            % (H.escape(title), hi, inner, PAGE, PAGE))


def send_all(subs, subject, html_for):
    user, pw = os.environ.get('GMAIL_USER', '').strip(), os.environ.get('GMAIL_APP_PASSWORD', '').strip()
    if not user or not pw:
        sys.exit('GMAIL_USER / GMAIL_APP_PASSWORD missing')
    if TEST:
        subs = [(user, 'تست')]
    sent = 0
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60) as s:
        s.login(user, pw)
        for to, name in subs:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr(('رضا حاجیلو – پورتفوی', user))
            msg['To'] = to
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid(domain='rezahajiloubooks.com')
            msg['List-Unsubscribe'] = '<%s#alerts>' % PAGE
            body = html_for(name)
            msg.attach(MIMEText(re.sub(r'<[^>]+>', '', body.replace('<br>', '\n').replace('</li>', '\n')), 'plain', 'utf-8'))
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            try:
                s.sendmail(user, [to], msg.as_string()); sent += 1
            except smtplib.SMTPException as e:
                print('::warning::one email failed: %s' % type(e).__name__)
    return sent


def main():
    tok = token()
    j = gql(tok, STATE, {})
    mo = (j.get('data') or {}).get('metaobjectByHandle')
    if not mo:
        sys.exit('rz_alerts/main missing')
    st = json.loads(({x['key']: x['value'] for x in mo['fields']}).get('state') or '{}')
    sent_ids, log = list(st.get('sent') or []), list(st.get('log') or [])

    subject, body = os.environ.get('ALERT_SUBJECT', '').strip(), os.environ.get('ALERT_BODY', '').strip()
    if subject and body:                                   # manual message to all subscribers
        subs = load_subs(tok)
        inner = '<div style="line-height:1.95;font-size:15.5px">%s</div>' % H.escape(body).replace('\n', '<br>')
        n = send_all(subs, subject, lambda name: render(subject, inner, name))
        print('manual message: %d sent (subscribers: %d, test=%s)' % (n, len(subs), TEST))
        if not TEST:
            log.append({'t': dt.datetime.now(dt.timezone.utc).isoformat()[:16], 'kind': 'manual', 'n': n})
    else:
        trades = load_trades(tok)
        known = set(sent_ids)
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=RECENT_DAYS)).isoformat()
        if not sent_ids and not st.get('armed'):
            # first ever run: everything already on the page is old news - record it, announce nothing
            sent_ids = [t['id'] for t in trades]; st['armed'] = True
            print('armed: %d existing trades recorded, no email' % len(sent_ids))
        else:
            new = [t for t in trades if t['id'] not in known and not t['h'] and t['up'] >= cutoff]
            if not new:
                print('no new trades'); return
            subs = load_subs(tok)
            subject = subject_for(new)
            inner = '<ul style="padding:0;margin:0">%s</ul>' % trade_lines(new)
            n = send_all(subs, subject, lambda name: render(subject, inner, name))
            print('trade alert: %d new trade(s), %d emails sent (subscribers: %d, test=%s)' % (len(new), n, len(subs), TEST))
            if TEST:
                return
            sent_ids += [t['id'] for t in new]
            log.append({'t': dt.datetime.now(dt.timezone.utc).isoformat()[:16], 'kind': 'trade', 'trades': len(new), 'n': n})
    st['sent'], st['log'] = sent_ids[-500:], log[-100:]
    j = gql(tok, UPDATE, {'id': mo['id'], 'f': [{'key': 'state', 'value': json.dumps(st, separators=(',', ':'))}]})
    ue = ((j.get('data') or {}).get('metaobjectUpdate') or {}).get('userErrors') or j.get('errors')
    if ue:
        sys.exit('state update failed: %s' % json.dumps(ue)[:300])


if __name__ == '__main__':
    main()
