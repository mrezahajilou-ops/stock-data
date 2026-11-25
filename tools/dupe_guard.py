#!/usr/bin/env python3
"""Duplicate-content guard for any of the stock sites (works on the built output folder).

Google does not penalise a page for being a translation of a page on another site; what hurts is a site whose
own pages read alike (thousands of stock pages that differ only in their numbers) and repeated titles or
descriptions. For every indexable page this guard measures:

  * unique share  - the part of the page's text (numbers ignored) that few other pages of the same kind share.
                    Template sentences that appear on most pages of a group count as boilerplate.
  * twin          - the most similar other page of the same kind (Jaccard of word 5-grams, numbers ignored).
  * titles / meta descriptions used by more than one page.

    python3 tools/dupe_guard.py <built site> [--json report.json] [--strict]

Prints a report per page group (e.g. stocks/*/dividend). --strict exits 1 when a limit is broken, so a
build can refuse to publish. Limits: no repeated <title>, no repeated description, and in every group of 20+
pages the median unique share must stay above MIN_UNIQUE and at most MAX_TWINS of the pages may have a twin
above TWIN.
"""
import collections, html, json, os, random, re, statistics, sys

MIN_UNIQUE = 0.20      # median share of a page's text that is its own
TWIN = 0.85            # pages this alike (numbers ignored) count as twins
MAX_TWINS = 0.10       # share of a group allowed to have a twin
K = 5                  # words per shingle

ROOT = sys.argv[1]
ARGS = sys.argv[2:]
STRICT = '--strict' in ARGS
JSON_OUT = ARGS[ARGS.index('--json') + 1] if '--json' in ARGS else None

CUT = re.compile(r'(?is)<script\b.*?</script>|<style\b.*?</style>|<header\b.*?</header>|<footer\b.*?</footer>|<nav\b.*?</nav>|<svg\b.*?</svg>|<form\b.*?</form>')
TAG = re.compile(r'<[^>]+>')
NUM = re.compile(r'[−+-]?\$?\d[\d,. ]*%?')
WORD = re.compile(r'\w+', re.U)


def page_text(s):
    m = re.search(r'(?is)<main\b.*?</main>', s)
    body = m.group(0) if m else s
    body = CUT.sub(' ', body)
    t = html.unescape(TAG.sub(' ', body))
    return NUM.sub(' # ', t).lower()


def shingles(words):
    if len(words) < K:
        return {hash(' '.join(words))} if words else set()
    return {hash(' '.join(words[i:i + K])) for i in range(len(words) - K + 1)}


def group_of(rel):
    seg = [x for x in rel.split('/') if x and x != 'index.html']
    if not seg:
        return 'home'
    if len(seg) == 1:
        return seg[0]
    if len(seg) == 2:
        return seg[0] + '/*'
    return seg[0] + '/*/' + '/'.join(seg[2:]) if len(seg) == 3 else seg[0] + '/*/' + seg[2] + '/*'


pages = {}
titles, descs = collections.defaultdict(list), collections.defaultdict(list)
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        if f != 'index.html':
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        s = open(p, encoding='utf-8', errors='ignore').read()
        if re.search(r'<meta name="robots" content="[^"]*noindex', s) or 'http-equiv="refresh"' in s:
            continue
        t = re.search(r'(?is)<title>(.*?)</title>', s)
        d = re.search(r'<meta name="description" content="([^"]*)"', s)
        url = '/' + rel[:-len('index.html')]
        if t:
            titles[html.unescape(t.group(1)).strip()].append(url)
        if d:
            descs[html.unescape(d.group(1)).strip()].append(url)
        w = WORD.findall(page_text(s))
        pages[url] = (group_of(rel), shingles(w), len(w))

groups = collections.defaultdict(list)
for u, (g, sh, n) in pages.items():
    groups[g].append(u)

report, broken = {}, []
for g, us in sorted(groups.items(), key=lambda x: -len(x[1])):
    df = collections.Counter()
    for u in us:
        df.update(pages[u][1])
    lim = max(2, int(len(us) * 0.02))
    uniq = []
    for u in us:
        sh = pages[u][1]
        uniq.append((sum(1 for x in sh if df[x] <= lim) / len(sh)) if sh else 0.0)
    # twins: compare each page with a sample of pages that share its rarest shingles
    random.seed(7)
    sample = us if len(us) <= 400 else random.sample(us, 400)
    inv = collections.defaultdict(list)
    for u in us:
        sh = pages[u][1]
        for x in sorted(sh, key=lambda x: df[x])[:12]:
            inv[x].append(u)
    twins = []
    for u in sample:
        a = pages[u][1]
        if not a:
            continue
        cand = collections.Counter()
        for x in sorted(a, key=lambda x: df[x])[:12]:
            for v in inv[x]:
                if v != u:
                    cand[v] += 1
        best, bu = 0.0, None
        for v, _ in cand.most_common(15):
            b = pages[v][1]
            j = len(a & b) / len(a | b) if b else 0
            if j > best:
                best, bu = j, v
        twins.append((best, u, bu))
    med = statistics.median(uniq) if uniq else 0
    tw = sum(1 for x in twins if x[0] >= TWIN) / len(twins) if twins else 0
    words = statistics.median(pages[u][2] for u in us)
    worst = sorted(zip(uniq, us))[:3]
    report[g] = dict(pages=len(us), median_unique=round(med, 3), twin_share=round(tw, 3), median_words=words,
                     least_unique=[(round(a, 2), b) for a, b in worst],
                     closest_twins=[(round(a, 2), b, c) for a, b, c in sorted(twins, reverse=True)[:3]])
    if len(us) >= 20 and (med < MIN_UNIQUE or tw > MAX_TWINS):
        broken.append(g)

dt = {k: v for k, v in titles.items() if len(v) > 1}
dd = {k: v for k, v in descs.items() if len(v) > 1}
print('dupe guard: %d indexable pages in %d groups' % (len(pages), len(groups)))
print('%-38s %7s %8s %7s %7s' % ('group', 'pages', 'unique', 'twins', 'words'))
for g, r in report.items():
    if r['pages'] < 5:
        continue
    flag = '  <-- below limit' if g in broken else ''
    print('%-38s %7d %7.0f%% %6.0f%% %7d%s' % (g[:38], r['pages'], r['median_unique'] * 100, r['twin_share'] * 100, r['median_words'], flag))
print('repeated titles: %d   repeated descriptions: %d' % (len(dt), len(dd)))
for k, v in list(dt.items())[:8]:
    print('  title x%d: %s  %s' % (len(v), k[:70], v[:3]))
for k, v in list(dd.items())[:8]:
    print('  desc  x%d: %s  %s' % (len(v), k[:70], v[:3]))
if JSON_OUT:
    json.dump(dict(groups=report, titles=dt, descriptions=dd), open(JSON_OUT, 'w'), ensure_ascii=False, indent=1)
if STRICT and (broken or dt or dd):
    print('dupe guard: FAILED (%s)' % ', '.join(broken + (['titles'] if dt else []) + (['descriptions'] if dd else [])))
    sys.exit(1)
