#!/usr/bin/env python3
"""One Persian blog article per quarterly earnings report ("گزارش سود انویدیا ...").

Written from the numbers alone (reported EPS vs the analysts' forecast, revenue vs a year ago, the
price reaction, the last four quarters, the next expected report), so it can be published within hours
of the report by the fast lane / daily build. Pushed by sync_guides.py into the blog `earnings-reports`.

Input:  branch `earnings` (e/<T>.json, read with git archive), branch `calendar`, data/stocks/<T>.json
Output: pages/articles.json  {blog, blog_title, articles: [{handle, title, seo_title, seo_desc, summary, html, date, tags}]}
"""
import json, os, io, tarfile, subprocess, datetime as dt

from build_pages import FA_NAME, FA_SECTOR, MONTHS, fa, pct, big_fa, verdict
from build_guides import CSS, DIS, e, label, nm_html, date_fa, score, table, signed, faq_block, chips, TOOLS

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
OUT = os.path.join(ROOT, 'pages', 'articles.json')
WINDOW = int(os.environ.get('EARN_DAYS') or 10)     # reports this recent get an article
MIN_MCAP = 10e9                                      # well-known companies only
TODAY = dt.date.today()
MON = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}


def branch_files(ref, prefix=''):
    """All JSON files of a branch in one go (thousands of `git show` calls would take minutes)."""
    try:
        raw = subprocess.run(['git', '-C', ROOT, 'archive', ref], capture_output=True, timeout=120).stdout
        out = {}
        with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
            for m in tf.getmembers():
                if m.isfile() and m.name.startswith(prefix) and m.name.endswith('.json'):
                    try:
                        out[m.name] = json.load(tf.extractfile(m))
                    except Exception:
                        pass
        return out
    except Exception as ex:
        print('cannot read %s: %s' % (ref, ex))
        return {}


def q_label(q):
    """'Sep/2026' -> 'سه‌ماهه‌ی منتهی به سپتامبر ۲۰۲۶' and a short 'q3-2026'-style slug part."""
    try:
        m, y = q.split('/')
        mi = MON[m[:3]]
        return 'سه‌ماهه‌ی منتهی به %s %s' % (MONTHS[mi - 1], fa(int(y))), '%s-%02d' % (y, mi)
    except Exception:
        return q, q.replace('/', '-').lower()


def money_q(v):
    return big_fa(v) if v is not None else '—'


def article(t, rep, hist, st, nxt):
    m, r, sc = st.get('market') or {}, st.get('ratios') or {}, st.get('scores') or {}
    an = st.get('analyst') or {}
    import re
    en = re.sub(r'\s*/[a-z]+/?$', '', (st.get('name') or t).strip(), flags=re.I).rstrip('/,').strip()
    x = {'t': t, 'fa': FA_NAME.get(t), 'en': en}
    nm = x['fa'] or ('<bdi dir="ltr">%s</bdi>' % t)   # short name for repeat mentions; HTML-safe
    ql, slug_q = q_label(rep['q'])
    d = dt.date.fromisoformat(rep['d'])
    act, f, sur = rep.get('act'), rep.get('f'), rep.get('sur')
    beat = None if (act is None or f is None) else (round(act, 2) > round(f, 2)) - (round(act, 2) < round(f, 2))
    word = {1: 'بهتر از انتظار', 0: 'مطابق انتظار', -1: 'ضعیف‌تر از انتظار', None: 'منتشر شد'}[beat]
    rev, revly = rep.get('rev'), rep.get('revly')
    rg = (rev / revly - 1) if (rev and revly) else None

    # titles stay Persian: a Latin company name inside a Persian title breaks right-to-left order
    who = ('%s (%s)' % (x['fa'], t)) if x['fa'] else ('سهام ' + t)
    title = 'گزارش سود %s در %s: %s' % (who, ql, word)
    p = []
    p.append('<p><strong>%s</strong> روز %s نتایج %s را منتشر کرد. سود هر سهم (EPS)%s %s دلار بود؛ تحلیلگرها به‌طور میانگین %s دلار پیش‌بینی کرده بودند%s.</p>'
             % (label(x), date_fa(d), ql, ' تعدیل‌شده' if rep.get('eb') == 'adj' else '',
                fa('%.2f' % act) if act is not None else '—', fa('%.2f' % f) if f is not None else '—',
                ('، یعنی %s %s از انتظار' % (pct(abs(sur) / 100, 1), 'بهتر' if sur >= 0 else 'ضعیف‌تر')) if sur is not None else ''))
    if rev:
        p.append('<p>درآمد این فصل %s بود%s.</p>' % (money_q(rev), ('؛ نسبت به همین فصل سال قبل (%s) %s %s' % (
            money_q(revly), pct(abs(rg), 1), 'رشد' if rg >= 0 else 'کاهش')) if rg is not None else ''))
    if rep.get('rx') is not None:
        rx = rep['rx']
        p.append('<p>واکنش بازار: قیمت سهم در اولین روز معاملاتی بعد از گزارش %s %s کرد.</p>' % (pct(abs(rx), 1), 'رشد' if rx >= 0 else 'افت'))

    # last four quarters
    rows, beats = [], 0
    for h in hist[:4]:
        hl, _ = q_label(h['q'])
        if h.get('act') is not None and h.get('f') is not None and h['act'] > h['f']:
            beats += 1
        g = (h['rev'] / h['revly'] - 1) if (h.get('rev') and h.get('revly')) else None
        rows.append([e(hl.replace('سه‌ماهه‌ی منتهی به ', '')), fa('%.2f' % h['act']) if h.get('act') is not None else '—',
                     fa('%.2f' % h['f']) if h.get('f') is not None else '—', signed(h['sur'] / 100, 1) if h.get('sur') is not None else '—',
                     signed(g, 0) if g is not None else '—', signed(h['rx'], 1) if h.get('rx') is not None else '—'])
    hist_html = ''
    if rows:
        hist_html = ('<h2>چهار فصل اخیر</h2><p>%s در %s فصل از %s فصل اخیر سود بهتر از پیش‌بینی تحلیلگرها گزارش کرده است.</p>'
                     % (nm, fa(beats), fa(len(rows)))
                     + table(['فصل', 'EPS واقعی', 'پیش‌بینی', 'غافلگیری', 'رشد درآمد', 'واکنش قیمت'], rows))

    # what next
    nx = []
    if an.get('qe0') is not None:
        nx.append('میانگین پیش‌بینی تحلیلگرها برای سود هر سهم فصل بعد %s دلار است' % fa('%.2f' % an['qe0']))
    if nxt:
        nx.append('گزارش بعدی حدود %s منتشر می‌شود' % date_fa(dt.date.fromisoformat(nxt)))
    next_html = ('<h2>بعد از این گزارش</h2><p>' + '. '.join(nx) + '.</p>') if nx else ''

    val = []
    if sc.get('total') is not None:
        val.append('امتیاز کلی %s در تحلیل سهام آنالیز %s از ۵ است (%s)' % (nm, fa('%.1f' % sc['total']), verdict(sc['total'])))
    if r.get('pe'):
        val.append('نسبت قیمت به سود (P/E) حدود %s' % fa('%.1f' % r['pe']))
    if r.get('fair_mcap') and m.get('mcap'):
        g = r['fair_mcap'] / m['mcap'] - 1
        val.append('ارزش ذاتی با فرض‌های متوسط تقریباً %s %s از قیمت فعلی' % (pct(abs(g)), 'بالاتر' if g >= 0 else 'پایین‌تر'))
    val_html = ('<h2>ارزش‌گذاری و امتیاز</h2><p>%s. <a href="/pages/stocks/%s">تحلیل کامل %s با صورت‌های مالی ۱۰ ساله</a></p>'
                % ('؛ '.join(val), t.lower(), nm)) if val else ''

    qa = [('سود هر سهم %s در %s چقدر بود؟' % (nm, ql), '%s دلار، در برابر پیش‌بینی %s دلار.' % (
              fa('%.2f' % act) if act is not None else '—', fa('%.2f' % f) if f is not None else '—'))]
    if rev:
        qa.append(('درآمد %s در این فصل چقدر بود؟' % nm, money_q(rev) + ((' که نسبت به سال قبل %s %s داشت.' % (pct(abs(rg), 1), 'رشد' if rg >= 0 else 'کاهش')) if rg is not None else '.')))
    if nxt:
        qa.append(('گزارش بعدی %s کی است؟' % nm, 'حدود %s (تاریخ دقیق را شرکت اعلام می‌کند).' % date_fa(dt.date.fromisoformat(nxt))))

    sector = FA_SECTOR.get(m.get('sector') or '', '')
    html = (CSS + '<div class="rzg" dir="rtl">' + ''.join(p) + hist_html + next_html + val_html + faq_block(qa)
            + '<h2>بیشتر</h2>' + chips([('/pages/stocks/' + t.lower(), 'تحلیل سهام ' + nm), ('/pages/earnings', 'تقویم گزارش‌های مالی'),
                                         ('/blogs/earnings-reports', 'همه‌ی گزارش‌های فصلی')] + TOOLS[:2])
            + DIS.replace('این صفحه هر روز بعد از بسته شدن بازار آمریکا خودکار', 'این گزارش خودکار') + '</div>')
    summary = '<p>%s: سود هر سهم %s دلار در برابر پیش‌بینی %s دلار%s.</p>' % (
        e(title.split(':')[0]), fa('%.2f' % act) if act is not None else '—', fa('%.2f' % f) if f is not None else '—',
        ('، درآمد %s' % money_q(rev)) if rev else '')
    seo_desc = ('گزارش سود %s در %s به فارسی: سود هر سهم %s دلار در برابر پیش‌بینی %s دلار%s%s، واکنش بازار و چشم‌انداز فصل بعد.'
                % (who, ql, fa('%.2f' % act) if act is not None else '—', fa('%.2f' % f) if f is not None else '—',
                   ('، درآمد %s' % money_q(rev)) if rev else '', ('، رشد %s نسبت به سال قبل' % pct(rg, 0)) if rg is not None and rg >= 0 else ''))
    return dict(handle='%s-earnings-%s' % (t.lower().replace('.', '-'), slug_q), title=title,
                seo_title=('گزارش سود %s %s | %s' % (who, ql.replace('سه‌ماهه‌ی منتهی به ', ''), word))[:70],
                seo_desc=seo_desc[:300], summary=summary, html=html,
                date=rep['d'] + 'T21:00:00Z', tags=[t, nm] + ([sector] if sector else []))


def main():
    files = branch_files(os.environ.get('EARN_REF', 'origin/earnings'), 'e/')
    cal = (branch_files(os.environ.get('CAL_REF', 'origin/calendar')).get('earnings.json') or {}).get('days') or {}
    upcoming = {}
    for day in sorted(cal):
        if day > TODAY.isoformat():
            for row in cal[day]:
                upcoming.setdefault(row['t'], day)
    arts = []
    cutoff = (TODAY - dt.timedelta(days=WINDOW)).isoformat()
    for name, doc in files.items():
        t = doc.get('t')
        qs = [q for q in doc.get('q') or [] if q.get('act') is not None]
        if qs and qs[0].get('f') is None:
            continue  # no analyst forecast to compare with - nothing to say about beat or miss
        if not t or not qs or qs[0]['d'] < cutoff:
            continue
        try:
            st = json.load(open(os.path.join(ROOT, 'data', 'stocks', t + '.json')))
        except Exception:
            continue
        if ((st.get('market') or {}).get('mcap') or 0) < MIN_MCAP:
            continue
        # earnings per share must be in dollars: foreign filers report EPS in won, euro, yuan...
        if (st.get('reported_currency') or 'USD') != 'USD' or ((st.get('analyst') or {}).get('cur') or 'USD') != 'USD':
            continue
        arts.append(article(t, qs[0], qs, st, upcoming.get(t)))
    arts.sort(key=lambda a: a['date'], reverse=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'blog': 'earnings-reports', 'blog_title': 'گزارش‌های فصلی شرکت‌های آمریکایی', 'articles': arts}, open(OUT, 'w'), ensure_ascii=False)
    print('earnings articles', len(arts), [a['handle'] for a in arts[:8]])


if __name__ == '__main__':
    main()
