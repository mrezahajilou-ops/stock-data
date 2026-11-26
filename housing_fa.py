#!/usr/bin/env python3
"""Farsi housing-market pages for sahamanaliz.com (Shopify): US, Germany, Canada.

The Shopify template page.housing.liquid loads fa-<cc>.html from the data branch "housing" at view time,
so these fragments are rebuilt by .github/workflows/housing.yml right after the data and need no theme deploy.
Shared renderer: housing_page.py (same page as the sister sites), texts: housing_i18n.FA.
Run: HOUSING_DIR=<folder with housing_<cc>.json> python housing_fa.py <outdir>
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import housing_page as HP  # noqa: E402

COUNTRIES = ['us', 'de', 'ca']
URLS = {'us': '/pages/housing', 'de': '/pages/housing-germany', 'ca': '/pages/housing-canada'}
SITE = 'https://sahamanaliz.com'


def chrome():
    try:
        import gen_web
        return gen_web.ACCT
    except Exception:
        return ''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    os.makedirs(out, exist_ok=True)
    n = 0
    for p in HP.build_all(HERE, 'fa', COUNTRIES, chrome(), URLS.get, None, SITE, 'سهام آنالیز'):
        cc = next(c for c, u in URLS.items() if u == p['url'])
        ld = ''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in p['ld'])
        meta = '<script>document.title=%s;</script>' % json.dumps(p['title'] + ' | سهام آنالیز', ensure_ascii=False)
        # SEO text inside the same root so it gets the page styles
        html = p['html']; html = html[:html.rfind('</div>')] + p['seo'] + '</div>' + ld + meta
        open(os.path.join(out, 'fa-%s.html' % cc), 'w', encoding='utf-8').write(html)
        n += 1
        print('fa', cc, len(html) // 1024, 'KB', p['title'])
    if not n:
        sys.exit('no Farsi housing page built')


if __name__ == '__main__':
    main()
