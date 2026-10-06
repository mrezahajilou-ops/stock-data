#!/usr/bin/env python3
"""Push pages/pages.jsonl (from build_pages.py) into Shopify as `rz_stock` metaobjects.
Each one is a public page at https://rezahajiloubooks.com/pages/stocks/<ticker>.

Auth: Dev Dashboard app installed on the store, client credentials grant (token valid 24h).
Secrets (GitHub repo -> Settings -> Secrets and variables -> Actions):
  SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET   (scopes: read/write_metaobjects)
Optional env SHOPIFY_SHOP (default jev8ju-dh.myshopify.com), LIMIT=N for a test run.
Only pages whose content changed since the last successful sync are sent (hashes in pages/hashes.json,
cached between runs by the workflow).
"""
import json, os, sys, time, hashlib, urllib.request, urllib.parse, urllib.error

SHOP = os.environ.get('SHOPIFY_SHOP', 'jev8ju-dh.myshopify.com')
API = 'https://%s/admin/api/2026-01/graphql.json' % SHOP
ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
PAGES = os.path.join(ROOT, 'pages', 'pages.jsonl')
HASHES = os.path.join(ROOT, 'pages', 'hashes.json')
LIMIT = int(os.environ.get('LIMIT') or 0)

UPSERT = '''mutation Up($h: MetaobjectHandleInput!, $m: MetaobjectUpsertInput!) {
  metaobjectUpsert(handle: $h, metaobject: $m) { metaobject { id handle } userErrors { field message code } } }'''


def token():
    cid, sec = os.environ['SHOPIFY_CLIENT_ID'].strip(), os.environ['SHOPIFY_CLIENT_SECRET'].strip()
    # safe diagnostics (never prints the values): lengths and whether the two are identical
    print('client id length %d, secret length %d, same=%s' % (len(cid), len(sec), cid == sec), flush=True)
    body = urllib.parse.urlencode({'client_id': os.environ['SHOPIFY_CLIENT_ID'].strip(),
                                   'client_secret': os.environ['SHOPIFY_CLIENT_SECRET'].strip(),
                                   'grant_type': 'client_credentials'}).encode()
    req = urllib.request.Request('https://%s/admin/oauth/access_token' % SHOP, data=body,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['access_token']


def gql(tok, query, variables):
    data = json.dumps({'query': query, 'variables': variables}).encode()
    for attempt in range(6):
        req = urllib.request.Request(API, data=data, headers={'Content-Type': 'application/json', 'X-Shopify-Access-Token': tok})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                j = json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1)); continue
            raise
        errs = j.get('errors') or []
        if any((e.get('extensions') or {}).get('code') == 'THROTTLED' for e in errs):
            time.sleep(2 * (attempt + 1)); continue
        # stay inside the cost bucket: pause when it runs low
        ts = ((j.get('extensions') or {}).get('cost') or {}).get('throttleStatus') or {}
        if ts and ts.get('currentlyAvailable', 1000) < 100:
            time.sleep((100 - ts['currentlyAvailable']) / max(ts.get('restoreRate', 50), 1) + 0.5)
        return j
    raise RuntimeError('throttled too long')


def main():
    old = {}
    if os.path.exists(HASHES):
        try:
            old = json.load(open(HASHES))
        except Exception:
            old = {}
    rows = [json.loads(l) for l in open(PAGES)]
    if LIMIT:
        rows = rows[:LIMIT]
    tok = token()
    new, sent, failed, skipped = dict(old), 0, 0, 0
    t0 = time.time()
    for p in rows:
        h = hashlib.sha1(json.dumps(p['fields'], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if old.get(p['handle']) == h:
            skipped += 1
            continue
        m = {'fields': [{'key': k, 'value': v} for k, v in p['fields'].items()],
             'capabilities': {'publishable': {'status': 'ACTIVE'}}}
        j = gql(tok, UPSERT, {'h': {'type': 'rz_stock', 'handle': p['handle']}, 'm': m})
        ue = (((j.get('data') or {}).get('metaobjectUpsert')) or {}).get('userErrors') or j.get('errors')
        if ue:
            failed += 1
            if failed <= 5:
                print('::error::%s %s' % (p['handle'], json.dumps(ue)[:300]), flush=True)
            continue
        new[p['handle']] = h
        sent += 1
        if sent % 250 == 0:
            print('sent %d (%.0fs)' % (sent, time.time() - t0), flush=True)
            json.dump(new, open(HASHES, 'w'))
    json.dump(new, open(HASHES, 'w'))
    print('done: sent %d, unchanged %d, failed %d, %.0fs' % (sent, skipped, failed, time.time() - t0))
    if failed > max(20, len(rows) // 20):
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as e:
        import re as _re
        raw = e.read().decode('utf-8', 'ignore')
        txt = _re.sub(r'\s+', ' ', _re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', raw, flags=_re.S))
        i = max(txt.lower().find('error'), txt.lower().find('oauth'), 0)
        body = txt[max(0, i - 80): i + 300]
        print('::error::HTTP %s from %s: %s' % (e.code, e.url.split('?')[0], body), flush=True)
        sys.exit(1)
    except Exception as e:
        print('::error::%s: %s' % (type(e).__name__, str(e)[:300]), flush=True)
        sys.exit(1)
