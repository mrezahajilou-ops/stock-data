#!/usr/bin/env python3
"""Google AdSense on Reza's sites (28 Nov 2026).

Run at the end of a site's build:  python3 adsense_inject.py <public dir>
- puts the AdSense loader in the <head> of every HTML page (once; pages that already have it are left alone)
- writes /ads.txt for the AdSense account

Account: pub-7057593320510341 (Reza's YouTube AdSense account, upgraded to full AdSense on 28 Nov 2026).
Which ads show and where is set in the AdSense dashboard (Auto ads, per site), and the EU consent banner is
Google's own CMP from AdSense "Privacy & messaging" - nothing else is needed in the pages.
A page can opt out by containing the comment <!-- no-adsense -->.
"""
import os
import sys

PUB = 'pub-7057593320510341'
TAG = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-' + PUB +
       '" crossorigin="anonymous"></script>')
ADS_TXT = 'google.com, ' + PUB + ', DIRECT, f08c47fec0942fa0\n'


def main(root):
    done = skipped = 0
    for d, _, files in os.walk(root):
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(d, f)
            with open(p, encoding='utf-8', errors='surrogateescape') as fh:
                s = fh.read()
            if 'adsbygoogle.js' in s or '<!-- no-adsense -->' in s:
                skipped += 1
                continue
            i = s.find('</head>')
            if i < 0:
                skipped += 1
                continue
            with open(p, 'w', encoding='utf-8', errors='surrogateescape') as fh:
                fh.write(s[:i] + TAG + s[i:])
            done += 1
    txt = os.path.join(root, 'ads.txt')
    old = open(txt, encoding='utf-8').read() if os.path.exists(txt) else ''
    if PUB not in old:
        with open(txt, 'w', encoding='utf-8') as fh:
            fh.write(old + ('' if not old or old.endswith('\n') else '\n') + ADS_TXT)
    print(f'adsense: tag added to {done} pages, {skipped} skipped; ads.txt ready')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'public')
