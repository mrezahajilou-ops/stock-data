"""SEO guard: stops a deploy that would hide many pages Google can index today.

Why (28 Nov 2026): a size-based noindex rule on stockanaliz.com hid thousands of indexable pages, some of them
earning impressions, and Google impressions fell ~90% in three days; a file-count trim once dropped 829 news articles
in one build. Both went live silently. This runs after the build, before deploy, on every edition:

  python3 $SD/tools/seo_guard.py public <domain> [content/seo/protect.txt]

It compares the new build with the live site (https://<domain>/seo-index.txt, the list of indexable pages written by
the previous build) and fails the build, so the previous version stays live, when
  1. more than 3% (and more than 300) of the pages that are indexable on the live site become noindex or disappear
     without a redirect, or
  2. a URL in the optional protect list (pages Search Console showed impressions for) carries noindex, or more than
     8% (and at least 20) of them are gone.
It then writes public/seo-index.txt and public/seo-guard.json for the next build. A deliberate change: run the
build once with SEO_GUARD_ALLOW=1.
"""
import gzip
import json
import os
import re
import sys
import urllib.request

ROBOTS = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*>', re.I)
LEGAL = ('impressum', 'kunye', 'aviso-legal', 'mentions-legales', 'note-legali', 'gioi-thieu-phap-ly')


def is_noindex(fn):
    try:
        with open(fn, encoding='utf-8', errors='ignore') as fh:
            head = fh.read(20000)
    except OSError:
        return False
    m = ROBOTS.search(head)
    return bool(m and 'noindex' in m.group(0).lower())


def url_of(pub, fn):
    rel = os.path.relpath(fn, pub).replace(os.sep, '/')
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel


def redirect_sources(pub):
    out = []
    f = os.path.join(pub, '_redirects')
    if os.path.exists(f):
        for line in open(f, encoding='utf-8', errors='ignore'):
            p = line.split()
            if len(p) >= 2 and not p[0].startswith('#'):
                out.append(p[0].rstrip('*'))
    return out


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'seo-guard', 'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            b = gzip.decompress(b)
        return b.decode('utf-8', 'ignore')


def main():
    pub, domain = sys.argv[1], sys.argv[2]
    prot_file = sys.argv[3] if len(sys.argv) > 3 else 'content/seo/protect.txt'
    allow = os.environ.get('SEO_GUARD_ALLOW') == '1'

    indexable, noindex = set(), set()
    for root, _, files in os.walk(pub):
        for f in files:
            if f.endswith('.html') and f != '404.html':
                fn = os.path.join(root, f)
                (noindex if is_noindex(fn) else indexable).add(url_of(pub, fn))
    red = [r for r in redirect_sources(pub) if r]
    covered = lambda u: any(u.startswith(r) for r in red)
    problems = []

    # 1. against the live site
    old = None
    try:
        old = set(x for x in fetch('https://%s/seo-index.txt' % domain).split() if x.startswith('/'))
    except Exception as ex:
        print('seo guard: no live baseline yet (%s)' % ex.__class__.__name__)
    lost_noidx, lost_gone = [], []
    if old:
        for u in old - indexable:
            if u in noindex:
                lost_noidx.append(u)
            elif not covered(u):
                lost_gone.append(u)
        lost = len(lost_noidx) + len(lost_gone)
        if lost > 300 and lost > 0.03 * len(old):
            problems.append('%d of %d pages indexable on the live site would be lost: %d become noindex (e.g. %s), %d disappear (e.g. %s)' % (
                lost, len(old), len(lost_noidx), ', '.join(sorted(lost_noidx)[:6]), len(lost_gone), ', '.join(sorted(lost_gone)[:6])))

    # 2. protect list
    prot = []
    if os.path.exists(prot_file):
        for tok in open(prot_file, encoding='utf-8').read().split():
            if tok.startswith('#'):
                continue
            k, sep, v = tok.partition(':')
            if sep and k in ('s', 'c', 'n') and not tok.startswith('http'):   # stockanaliz protect_seed.txt tokens
                prot.append({'s': '/stocks/', 'c': '/compare/', 'n': '/news/'}[k] + v.strip('/') + '/')
            else:
                prot.append(re.sub(r'^https?://(www\.)?[^/]+', '', tok) or '/')
    hidden = [u for u in prot if u in noindex and not u.rstrip('/').endswith(LEGAL)]
    gone = [u for u in prot if u not in indexable and u not in noindex and not covered(u)]
    if hidden:
        problems.append('%d protected URLs carry noindex, e.g. %s' % (len(hidden), ', '.join(hidden[:8])))
    if len(gone) >= 20 and len(gone) > 0.08 * len(prot):
        problems.append('%d of %d protected URLs are gone, e.g. %s' % (len(gone), len(prot), ', '.join(gone[:8])))

    with open(os.path.join(pub, 'seo-index.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(sorted(indexable)) + '\n')
    json.dump({'indexable': len(indexable), 'noindex': len(noindex), 'live_indexable': len(old) if old else None,
               'lost_noindex': len(lost_noidx), 'lost_gone': len(lost_gone), 'protected': len(prot)},
              open(os.path.join(pub, 'seo-guard.json'), 'w'))
    print('seo guard: %d indexable, %d noindex; vs live %s: %d -> noindex, %d gone; protect list %d' % (
        len(indexable), len(noindex), len(old) if old else '-', len(lost_noidx), len(lost_gone), len(prot)))
    if problems:
        for p in problems:
            print('SEO GUARD: ' + p)
        if allow:
            print('SEO GUARD: SEO_GUARD_ALLOW=1, deploying anyway')
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
