#!/usr/bin/env python3
"""Push the theme files kept in this repo (theme/**) into the store's live theme.

The liquid under theme/ is the source of truth for the Farsi stock pages. Editing it through the
Shopify admin means a manual publish step every time, so this script writes the files straight into
the live theme with the same app credentials the metaobject sync already uses.

Only files whose content actually differs are sent, so a run with nothing to do costs one query.

Secrets: SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET (scopes must include write_themes).
Env: SHOPIFY_SHOP (default jev8ju-dh.myshopify.com), DRY=1 to report without writing.
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

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


def main():
    files = local_files()
    if not files:
        print('no files under theme/'); return 0
    tok = token()
    j = gql(tok, THEMES)
    nodes = (((j.get('data') or {}).get('themes') or {}).get('nodes') or [])
    if not nodes:
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
