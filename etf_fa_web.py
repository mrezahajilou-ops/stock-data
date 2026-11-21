#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persian ETF pages for sahamanaliz.com, built by the same code as every other edition.

The Persian site is a Shopify store, so it cannot serve fifty static pages the way the other four
sites do. Instead this writes each page's HTML as a fragment under web/etf/ and the thin loader in
web/etf.html (gen_web.py) shows the right one for the address. The structure of every page is
therefore exactly the English one: etf_pages.py builds both.

Run after etf_data.py:  python3 etf_fa_web.py
"""
import os, sys, io, datetime as dt, importlib.util as _iu

SD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SD, 'web', 'etf')
SECTORS = {
    'Technology': 'فناوری', 'Finance': 'مالی', 'Health Care': 'سلامت',
    'Consumer Discretionary': 'مصرفی غیرضروری', 'Consumer Staples': 'مصرفی ضروری',
    'Industrials': 'صنعتی', 'Energy': 'انرژی', 'Utilities': 'آب و برق و گاز',
    'Real Estate': 'املاک', 'Basic Materials': 'مواد پایه',
    'Telecommunications': 'مخابرات', 'Miscellaneous': 'سایر', 'Other': 'سایر',
}
MONTH = ['ژانویه', 'فوریه', 'مارس', 'آوریل', 'مه', 'ژوئن', 'ژوئیه', 'اوت', 'سپتامبر', 'اکتبر', 'نوامبر', 'دسامبر']


def _mod(path, name):
    sp = _iu.spec_from_file_location(name, os.path.join(SD, path))
    m = _iu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def fdate(s):
    try:
        d = dt.date.fromisoformat(str(s)[:10])
        return '⁨%d⁩ %s ⁨%d⁩' % (d.day, MONTH[d.month - 1], d.year)
    except Exception:
        return str(s or '')


def main():
    if SD not in sys.path:
        sys.path.insert(0, SD)
    pages = _mod('etf_pages.py', 'etf_pages')
    lang = _mod('content/etf/fa.py', 'etf_lang_fa')
    p = pages.Pack(lang='fa', ui=lang.UI, text=lang.T, ucits=lang.UCITS, base='#etf/',
                   stock_url=lambda t: '/pages/stock#%s' % t.upper(),
                   site='https://sahamanaliz.com', rtl=True, iso=pages.make_iso(), fdate=fdate)
    p.inline_assets = False      # the shell (gen_web.etf_page) already carries the styles and scripts these pages use
    p.qk_idx = 'https://cdn.jsdelivr.net/gh/mrezahajilou-ops/stock-data@main/data/index.json'   # stock list for the bar's search
    os.makedirs(OUT, exist_ok=True)
    keep = set()
    for pg in pages.build(SD, p, SECTORS):
        name = pg['url'].replace('#etf/', '').strip('/') or 'index'
        io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(pg['html'])
        keep.add(name + '.html')
    for f in os.listdir(OUT):
        if f.endswith('.html') and f not in keep:
            os.remove(os.path.join(OUT, f))
    print('persian etf fragments:', len(keep))


if __name__ == '__main__':
    main()
