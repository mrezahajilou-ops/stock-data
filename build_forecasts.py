#!/usr/bin/env python3
"""«پیش‌بینی سهام X» pages: analysts' price targets and earnings forecasts for the ~500 largest US companies.

One ordinary Shopify page per stock (/pages/<ticker>-forecast) plus a hub (/pages/stock-forecasts), written in
Persian from the numbers, so Google can read them (the stock tool itself is drawn by JavaScript).
Only companies that report in dollars and have at least 3 analysts with a price target.

Input:  data/stocks/*.json (price, market value), branch `estimates` est.json (consensus, read with git show)
Output: pages/forecasts.json  [{handle, title, seo_title, seo_desc, html}]  -> synced by sync_guides.py
"""
import json, os, datetime as dt

from build_guides import (load, git_json, nm_html, alt_html, e, chips, faq_block, table, date_fa, CSS, DIS, TODAY, ROOT,
                          MONTHS, label)
from build_pages import fa, pct, big_fa, FA_NAME

OUT = os.path.join(ROOT, 'pages', 'forecasts.json')
TOP = 500
REC = {'strong_buy': 'خرید قوی', 'buy': 'خرید', 'hold': 'نگه‌داری', 'underperform': 'عملکرد ضعیف‌تر از بازار', 'sell': 'فروش'}


def usd(v, d=2):
    return '—' if v is None else '<span class="n" dir="ltr">$%s</span>' % ('{:,.%df}' % d).format(v)


def month_year(s):
    try:
        x = dt.date.fromisoformat(s[:10])
        return MONTHS[x.month - 1] + ' ' + fa(x.year)
    except Exception:
        return '—'


def chg(a, b):
    """a vs b as a signed Persian percent ('+۷۴٪')."""
    if not a or not b:
        return '—'
    g = a / b - 1
    return '<span class="%s" dir="ltr">%s%s</span>' % ('up' if g >= 0 else 'dn', '+' if g >= 0 else '−', pct(abs(g), 0))


def sg(g):
    if g is None:
        return '—'
    return '<span class="%s" dir="ltr">%s%s</span>' % ('up' if g >= 0 else 'dn', '+' if g >= 0 else '−', pct(abs(g), 0))


def name(x):
    return x.get('fa') or x['en']


def page(x, s, peers):
    t, nm, p = x['t'], name(x), x['price']
    lab = label(x)
    tgt, lo, hi, nt = s['tgt'], s.get('tlo'), s.get('thi'), s.get('nt')
    up = tgt / p - 1
    rec = REC.get(s.get('rec'))
    rt = s.get('rt') or []
    intro = ('<p>%s تحلیلگر برای سهم %s قیمت هدف ۱۲ ماهه اعلام کرده‌اند. میانگین قیمت هدف آن‌ها %s است که نسبت به قیمت پایانی %s، '
             '%s %s را نشان می‌دهد. خوش‌بین‌ترین تحلیلگر %s و بدبین‌ترین %s را هدف گذاشته است.%s</p>'
             % (fa(nt), lab, usd(tgt), usd(p), pct(abs(up), 0), 'رشد' if up >= 0 else 'افت', usd(hi), usd(lo),
                (' جمع‌بندی نظر تحلیلگرها «%s» است.' % rec) if rec else ''))
    rows = [['کمترین قیمت هدف', usd(lo), chg(lo, p)], ['میانگین قیمت هدف', usd(tgt), chg(tgt, p)], ['بیشترین قیمت هدف', usd(hi), chg(hi, p)]]
    tg = '<h2>قیمت هدف تحلیلگرها برای %s</h2>' % nm_html(x.get('fa'), x['en']) + table(['', 'قیمت هدف', 'فاصله با قیمت فعلی'], [[r[0], r[1], r[2]] for r in rows])
    if len(rt) == 5 and sum(rt):
        tot = sum(rt)
        bars = ''.join('<div class="rb"><span>%s</span><b style="width:%d%%" class="%s"></b><em>%s</em></div>'
                       % (l, round(v / tot * 100), c, fa(v)) for l, v, c in
                       (('خرید قوی', rt[0], 'g2'), ('خرید', rt[1], 'g1'), ('نگه‌داری', rt[2], 'g0'), ('فروش', rt[3], 'r1'), ('فروش قوی', rt[4], 'r2')))
        tg += '<h2>نظر تحلیلگرها: خرید، نگه‌داری یا فروش؟</h2><div class="rbs">%s</div>' % bars

    ep = ''
    if s.get('e0') is not None and s.get('fy0'):
        r = [['سال مالی منتهی به ' + month_year(s['fy0']), usd(s.get('e0')), sg(s.get('ge0')),
              big_fa(s.get('r0')) if s.get('r0') else '—']]
        if s.get('e1') is not None and s.get('fy1'):
            r.append(['سال مالی منتهی به ' + month_year(s['fy1']), usd(s.get('e1')), sg(s.get('ge1')),
                      big_fa(s.get('r1')) if s.get('r1') else '—'])
        ep = ('<h2>پیش‌بینی سود و درآمد %s</h2>' % nm_html(x.get('fa'), x['en'])
              + table(['دوره', 'سود هر سهم', 'رشد سود', 'درآمد'], r))
        if s.get('fpe'):
            ep += '<p>با این پیش‌بینی، نسبت قیمت به سود آینده‌ی %s حدود %s است.</p>' % (lab, fa('%.1f' % s['fpe']))
        if s.get('qe0') is not None and s.get('q0'):
            ep += ('<p>برای فصل منتهی به %s، تحلیلگرها سود هر سهم %s%s را پیش‌بینی کرده‌اند.</p>'
                   % (month_year(s['q0']), usd(s['qe0']), (' و درآمد ' + big_fa(s['qr0'])) if s.get('qr0') else ''))
    hist = ''
    eh = [r for r in (s.get('eh') or []) if r[1] is not None and r[2] is not None][-4:]
    if eh:
        beats = sum(1 for r in eh if r[1] >= r[2])
        hist = ('<h2>تحلیلگرها در گذشته چقدر درست گفته‌اند؟</h2><p>%s در %s فصل از %s فصل اخیر سودی بیشتر یا برابر پیش‌بینی تحلیلگرها گزارش کرده است.</p>'
                % (lab, fa(beats), fa(len(eh)))
                + table(['فصل منتهی به', 'سود واقعی هر سهم', 'پیش‌بینی', 'نتیجه'],
                        [[month_year(r[0]), usd(r[1]), usd(r[2]), '<span class="%s">%s</span>' % (('up', 'بهتر از پیش‌بینی') if r[1] > r[2] else ('', 'برابر') if r[1] == r[2] else ('dn', 'ضعیف‌تر'))]
                         for r in reversed(eh)]))
    rv = s.get('rev30') or {}
    if rv.get('upLast30days') or rv.get('downLast30days'):
        hist += ('<p>در ۳۰ روز گذشته %s تحلیلگر پیش‌بینی سودشان را بالا و %s تحلیلگر پایین برده‌اند.</p>'
                 % (fa(rv.get('upLast30days') or 0), fa(rv.get('downLast30days') or 0)))

    qa = [('قیمت هدف سهام %s چقدر است؟' % nm, 'میانگین قیمت هدف %s تحلیلگر %s است؛ کمترین %s و بیشترین %s.' % (fa(nt), usd(tgt), usd(lo), usd(hi))),
          ('تحلیلگرها درباره‌ی سهم %s چه نظری دارند؟' % nm, ('جمع‌بندی نظرشان «%s» است. ' % rec if rec else '') +
           'این نظرها پیش‌بینی‌اند و بارها اشتباه از آب درآمده‌اند؛ قیمت هدف معمولاً با خود قیمت بالا و پایین می‌رود.')]
    if s.get('e1') is not None and s.get('fy1'):
        qa.append(('سود هر سهم %s در سال آینده چقدر پیش‌بینی می‌شود؟' % nm,
                   'برای سال مالی منتهی به %s، میانگین پیش‌بینی %s است.' % (month_year(s['fy1']), usd(s['e1']))))
    more = chips([('/pages/stocks/' + t.lower(), 'تحلیل کامل سهام ' + nm_html(x.get('fa'), x['en'])), ('/pages/dcf', 'ارزش ذاتی با فرض‌های خودت'),
                  ('/pages/earnings', 'تقویم گزارش‌های مالی'), ('/pages/stock-forecasts', 'پیش‌بینی سهام شرکت‌های دیگر')]
                 + [('/pages/%s-forecast' % y['t'].lower().replace('.', '-'), 'پیش‌بینی سهام ' + nm_html(y.get('fa'), y['en'])) for y in peers])
    html = (CSS + FX + '<div class="rzg" dir="rtl"><p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY) + intro + tg + ep + hist
            + faq_block(qa) + '<h2>بیشتر</h2>' + more
            + '<p class="dis">اعداد از میانگین پیش‌بینی تحلیلگرهای وال‌استریت است و هر روز خودکار به‌روز می‌شود. سهام آنالیز پیش‌بینی خودش را '
              'نمی‌دهد و این صفحه توصیه‌ی خرید یا فروش نیست.</p></div>')
    title = 'پیش‌بینی سهام %s (%s)' % (nm, t)
    return dict(handle=t.lower().replace('.', '-') + '-forecast', title=title, html=html,
                seo_title=('پیش‌بینی سهام %s | قیمت هدف %s تحلیلگر' % (nm, fa(nt)))[:70],
                seo_desc=('پیش‌بینی قیمت سهام %s (%s) به فارسی: میانگین قیمت هدف %s تحلیلگر $%s (%s%s نسبت به قیمت فعلی)، نظر خرید یا فروش، '
                          'پیش‌بینی سود هر سهم و درآمد سال آینده.' % (nm, t, fa(nt), '{:,.2f}'.format(tgt), '+' if up >= 0 else '−', pct(abs(up), 0)))[:300])


FX = '''<style>
.rzg .n{font-family:Inter,Arial,sans-serif;unicode-bidi:isolate}
.rzg .rbs{max-width:560px;margin:10px 0 18px}
.rzg .rb{display:grid;grid-template-columns:120px 1fr 34px;align-items:center;gap:8px;margin:5px 0;font-size:.92em}
.rzg .rb b{display:block;height:12px;border-radius:6px;min-width:3px}
.rzg .rb em{font-style:normal;color:#8A8F99;text-align:left}
.rzg .g2{background:#2f8f63}.rzg .g1{background:#4FA37A}.rzg .g0{background:#8A8F99}.rzg .r1{background:#C8534F}.rzg .r2{background:#9b2f2b}
</style>'''


def main():
    est = (git_json(os.environ.get('EST_REF', 'origin/estimates'), 'est.json') or {}).get('est') or {}
    if not est:
        print('estimates not found - skipping forecasts'); return
    rows = [x for x in sorted(load(), key=lambda x: -x['mcap'])
            if x.get('price') and (est.get(x['t']) or {}).get('cur') == 'USD' and (est[x['t']].get('nt') or 0) >= 3 and est[x['t']].get('tgt')][:TOP]
    by_ind = {}
    for x in rows:
        by_ind.setdefault(x.get('industry') or x.get('sector'), []).append(x)
    pages = []
    for x in rows:
        peers = [y for y in by_ind[x.get('industry') or x.get('sector')] if y['t'] != x['t']][:5]
        pages.append(page(x, est[x['t']], peers))
    # hub
    tb = table(['#', 'شرکت', 'قیمت', 'میانگین قیمت هدف', 'فاصله', 'تعداد تحلیلگر'],
               [[fa(i + 1), '<a href="/pages/%s-forecast">%s</a>%s<span class="tk">%s</span>' % (e(x['t'].lower().replace('.', '-')), nm_html(x.get('fa'), x['en']), alt_html(x['t']), e(x['t'])),
                 usd(x['price']), usd(est[x['t']]['tgt']), chg(est[x['t']]['tgt'], x['price']), fa(est[x['t']]['nt'])] for i, x in enumerate(rows)])
    hub = dict(handle='stock-forecasts', title='پیش‌بینی سهام آمریکا: قیمت هدف تحلیلگرها برای %s شرکت بزرگ' % fa(len(rows)),
               seo_title='پیش‌بینی سهام آمریکا | قیمت هدف تحلیلگرها'[:70],
               seo_desc=('قیمت هدف و پیش‌بینی سود تحلیلگرهای وال‌استریت برای %s شرکت بزرگ بورس آمریکا به فارسی، هر روز به‌روز.' % fa(len(rows))),
               html=CSS + FX + '<div class="rzg" dir="rtl"><p class="upd">به‌روزرسانی: %s</p>' % date_fa(TODAY)
               + '<p>برای هر شرکت، میانگین قیمت هدف ۱۲ ماهه‌ی تحلیلگرها، نظر خرید یا فروش و پیش‌بینی سود سال آینده را در صفحه‌ی جداگانه‌اش ببین. '
                 'فهرست به ترتیب ارزش بازار است. روی اسم هر شرکت بزن.</p>' + tb
               + '<h2>بیشتر</h2>' + chips([('/pages/top-30', '۳۰ سهم برتر به انتخاب تحلیلگرها'), ('/pages/guides', 'فهرست‌های آماده‌ی سهام'), ('/pages/stock', 'تحلیل سهام')])
               + '<p class="dis">اعداد از میانگین پیش‌بینی تحلیلگرهاست و توصیه‌ی خرید یا فروش نیست.</p></div>')
    pages.append(hub)
    json.dump(pages, open(OUT, 'w'), ensure_ascii=False)
    print('forecast pages', len(pages))


if __name__ == '__main__':
    main()
