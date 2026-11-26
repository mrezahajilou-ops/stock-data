#!/usr/bin/env python3
"""Push the theme files kept in this repo (theme/**) into the store's live theme.

The liquid under theme/ is the source of truth for the Farsi stock pages. Editing it through the
Shopify admin means a manual publish step every time, so this script writes the files straight into
the live theme with the same app credentials the metaobject sync already uses.

Only files whose content actually differs are sent, so a run with nothing to do costs one query.

Secrets: SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET (scopes must include write_themes).
Env: SHOPIFY_SHOP (default jev8ju-dh.myshopify.com), DRY=1 to report without writing.
"""
import json, os, re, sys, time, urllib.request, urllib.parse, urllib.error

SHOP = os.environ.get('SHOPIFY_SHOP', 'jev8ju-dh.myshopify.com')
API = 'https://%s/admin/api/2026-01/graphql.json' % SHOP
ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
SRC = os.path.join(ROOT, 'theme')
DRY = os.environ.get('DRY') == '1'


def token():
    body = urllib.parse.urlencode({'client_id': os.environ['SHOPIFY_CLIENT_ID'].strip(),
                                   'client_secret': os.environ['SHOPIFY_CLIENT_SECRET'].strip(),
                                   'grant_type': 'client_credentials'}).encode()
    req = urllib.request.Request('https://%s/admin/oauth/access_token' % SHOP, data=body,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.loads(r.read())
    print('granted scopes: %s' % j.get('scope'), flush=True)
    return j['access_token']


def gql(tok, query, variables=None):
    data = json.dumps({'query': query, 'variables': variables or {}}).encode()
    for attempt in range(6):
        req = urllib.request.Request(API, data=data, headers={'Content-Type': 'application/json',
                                                              'X-Shopify-Access-Token': tok})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                j = json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1)); continue
            raise
        if any((e.get('extensions') or {}).get('code') == 'THROTTLED' for e in (j.get('errors') or [])):
            time.sleep(2 * (attempt + 1)); continue
        return j
    raise RuntimeError('throttled too long')


THEMES = '{ themes(first: 10, roles: [MAIN]) { nodes { id name } } }'

READ = '''query($id: ID!, $names: [String!]) {
  theme(id: $id) { files(first: 50, filenames: $names) {
    nodes { filename body { ... on OnlineStoreThemeFileBodyText { content } } } } } }'''

UPSERT = '''mutation Up($id: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
  themeFilesUpsert(themeId: $id, files: $files) {
    upsertedThemeFiles { filename }
    userErrors { filename code message } } }'''


TEXT_EXT = ('.liquid', '.css', '.js', '.json')
# config/settings_data.json holds the settings Reza changes in the theme editor, and the images are
# binary, so neither belongs in a text sync: only the code written in this repo is pushed.
SKIP_DIRS = ('config',)


def local_files():
    out = {}
    for base, _, names in os.walk(SRC):
        for n in names:
            if n.startswith('.') or not n.endswith(TEXT_EXT):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, SRC).replace(os.sep, '/')
            if rel.split('/')[0] in SKIP_DIRS:
                continue
            with open(p, encoding='utf-8') as f:
                out[rel] = f.read()
    return out


# --- edits to files the repo does not own (Nov 2026) ------------------------------------------------
# The store's primary language is English, so the theme printed <html lang="en"> on every Farsi page and
# the cart drawer greeted Farsi readers with "Your cart is empty" / "Estimated total". These patch the live
# layout and default locale in place (only the listed strings), so theme updates keep everything else.
CART_FA = {
    ('sections', 'cart', 'title'): 'سبد خرید شما',
    ('sections', 'cart', 'empty'): 'سبد خرید شما خالی است',
    ('sections', 'cart', 'estimated_total'): 'جمع کل',
    ('sections', 'cart', 'new_estimated_total'): 'جمع کل جدید',
    ('sections', 'cart', 'subtotal'): 'جمع',
    ('sections', 'cart', 'new_subtotal'): 'جمع جدید',
    ('sections', 'cart', 'checkout'): 'پرداخت',
    ('sections', 'cart', 'update'): 'به‌روزرسانی',
    ('sections', 'cart', 'remove_all'): 'حذف همه',
    ('sections', 'cart', 'note'): 'توضیح سفارش',
    ('sections', 'cart', 'headings', 'product'): 'محصول',
    ('sections', 'cart', 'headings', 'price'): 'قیمت',
    ('sections', 'cart', 'headings', 'total'): 'جمع',
    ('sections', 'cart', 'headings', 'quantity'): 'تعداد',
    ('sections', 'cart', 'login', 'title'): 'حساب کاربری دارید؟',
    ('general', 'continue_shopping'): 'ادامه‌ی خرید',
    ('general', 'cart', 'view'): 'مشاهده‌ی سبد خرید',
    ('templates', 'cart', 'cart'): 'سبد خرید',
    ('accessibility', 'close'): 'بستن',
}


def _set_existing(d, path, val):
    for k in path[:-1]:
        if not isinstance(d, dict) or k not in d:
            return False
        d = d[k]
    if isinstance(d, dict) and path[-1] in d and isinstance(d[path[-1]], str) and d[path[-1]] != val:
        d[path[-1]] = val
        return True
    return False


def patch_live(tok, tid):
    names = ['layout/theme.liquid', 'locales/en.default.json']
    r = gql(tok, READ, {'id': tid, 'names': names})
    cur = {n['filename']: (n.get('body') or {}).get('content')
           for n in ((((r.get('data') or {}).get('theme') or {}).get('files') or {}).get('nodes') or [])}
    out = []
    lay = cur.get('layout/theme.liquid')
    if lay:
        new = re.sub(r'lang="\{\{\s*request\.locale\.iso_code\s*\}\}"', 'lang="fa"', lay, count=1)
        if new != lay:
            out.append(('layout/theme.liquid', new))
    loc = cur.get('locales/en.default.json')
    if loc:
        m = re.match(r'\s*(/\*.*?\*/)?\s*', loc, re.S)
        head = (m.group(1) + '\n') if m and m.group(1) else ''
        try:
            d = json.loads(loc[m.end():] if m else loc)
            if sum(_set_existing(d, k, v) for k, v in CART_FA.items()):
                out.append(('locales/en.default.json', head + json.dumps(d, ensure_ascii=False, indent=2)))
        except Exception as ex:
            print('locale patch skipped:', ex)
    if not out:
        print('live layout/locale already patched'); return 0
    print('patching: %s' % ', '.join(n for n, _ in out))
    if DRY:
        return 0
    r = gql(tok, UPSERT, {'id': tid, 'files': [{'filename': n, 'body': {'type': 'TEXT', 'value': v}} for n, v in out]})
    res = ((r.get('data') or {}).get('themeFilesUpsert') or {})
    errs = (r.get('errors') or []) + (res.get('userErrors') or [])
    if errs:
        print('::error::%s' % json.dumps(errs, ensure_ascii=False)); return 1
    return 0


def main():
    files = local_files()
    if not files:
        print('no files under theme/'); return 0
    tok = token()
    j = gql(tok, THEMES)
    nodes = (((j.get('data') or {}).get('themes') or {}).get('nodes') or [])
    if not nodes:
        if 'ACCESS_DENIED' in json.dumps(j) or 'read_themes' in json.dumps(j):
            # The store app was never granted read_themes/write_themes, so this job cannot write the theme.
            # Theme changes are made through Claude's Shopify connection instead (and the live theme is newer than
            # theme/ for some files, e.g. the home page), so a failure here is expected, not an outage: say so and stop.
            print('::notice::store app lacks the read_themes/write_themes scopes - theme not pushed from this job '
                  '(changes go through the Shopify connection; grant the scopes to re-enable this job)')
            return 0
        print('::error::no live theme found: %s' % json.dumps(j, ensure_ascii=False)[:600]); return 1
    tid, tname = nodes[0]['id'], nodes[0]['name']
    print('live theme: %s (%s)' % (tname, tid))

    names = sorted(files)
    live = {}
    for i in range(0, len(names), 50):
        chunk = names[i:i + 50]
        r = gql(tok, READ, {'id': tid, 'names': chunk})
        for n in ((((r.get('data') or {}).get('theme') or {}).get('files') or {}).get('nodes') or []):
            live[n['filename']] = ((n.get('body') or {}).get('content'))

    changed = [n for n in names if files[n] != live.get(n)]
    if patch_live(tok, tid):
        return 1
    if not changed:
        print('theme is already up to date (%d files checked)' % len(names)); return 0
    print('changed: %s' % ', '.join(changed))
    if DRY:
        return 0

    for i in range(0, len(changed), 20):
        chunk = changed[i:i + 20]
        r = gql(tok, UPSERT, {'id': tid, 'files': [{'filename': n, 'body': {'type': 'TEXT', 'value': files[n]}}
                                                   for n in chunk]})
        res = ((r.get('data') or {}).get('themeFilesUpsert') or {})
        errs = (r.get('errors') or []) + (res.get('userErrors') or [])
        if errs:
            print('::error::%s' % json.dumps(errs, ensure_ascii=False)); return 1
        for f in (res.get('upsertedThemeFiles') or []):
            print('wrote %s' % f['filename'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
