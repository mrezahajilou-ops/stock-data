#!/usr/bin/env python3
"""Push pages/guides.json (build_guides.py) to Shopify as ordinary online-store pages, plus the
blog articles in pages/articles.json (build_earnings.py) when that file exists.

Same app credentials as sync_shopify.py; needs the content scope (read/write_content).
A page is created the first time and updated afterwards (looked up by handle); the SEO title and
description go into the global.title_tag / global.description_tag metafields Shopify uses for <title>.
Only pages whose content changed are sent (hashes in pages/guide_hashes.json, cached by the workflow).
"""
import json, os, sys, hashlib

from sync_shopify import token, gql, ROOT

GUIDES = os.path.join(ROOT, 'pages', 'guides.json')
ARTICLES = os.path.join(ROOT, 'pages', 'articles.json')
HASHES = os.path.join(ROOT, 'pages', 'guide_hashes.json')

FIND = '''query($q: String!) { pages(first: 1, query: $q) { nodes { id handle } } }'''
CREATE = '''mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id handle } userErrors { field message } } }'''
UPDATE = '''mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id handle } userErrors { field message } } }'''
SCOPES = '''{ currentAppInstallation { accessScopes { handle } } }'''

BLOG_FIND = '''query($q: String!) { blogs(first: 1, query: $q) { nodes { id handle } } }'''
BLOG_CREATE = '''mutation($b: BlogCreateInput!) { blogCreate(blog: $b) { blog { id handle } userErrors { field message } } }'''
ART_FIND = '''query($q: String!) { articles(first: 1, query: $q) { nodes { id handle blog { handle } } } }'''
ART_CREATE = '''mutation($a: ArticleCreateInput!) { articleCreate(article: $a) { article { id handle } userErrors { field message } } }'''
ART_UPDATE = '''mutation($id: ID!, $a: ArticleUpdateInput!) { articleUpdate(id: $id, article: $a) { article { id handle } userErrors { field message } } }'''


def seo(p):
    return [{'namespace': 'global', 'key': 'title_tag', 'type': 'single_line_text_field', 'value': p['seo_title'][:255]},
            {'namespace': 'global', 'key': 'description_tag', 'type': 'single_line_text_field', 'value': p['seo_desc'][:320]}]


def errs(j, key):
    return (((j.get('data') or {}).get(key)) or {}).get('userErrors') or j.get('errors')


def hsh(p):
    return hashlib.sha1(json.dumps(p, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sync_pages(tok, rows, old, new):
    sent = failed = 0
    for p in rows:
        h = hsh(p)
        if old.get('page:' + p['handle']) == h:
            continue
        j = gql(tok, FIND, {'q': 'handle:%s' % p['handle']})
        nodes = (((j.get('data') or {}).get('pages')) or {}).get('nodes') or []
        node = next((n for n in nodes if n['handle'] == p['handle']), None)
        body = {'title': p['title'], 'body': p['html'], 'metafields': seo(p)}
        if node:
            j = gql(tok, UPDATE, {'id': node['id'], 'p': body})
            ue = errs(j, 'pageUpdate')
        else:
            body.update({'handle': p['handle'], 'isPublished': True})
            j = gql(tok, CREATE, {'p': body})
            ue = errs(j, 'pageCreate')
        if ue:
            failed += 1
            print('::error::page %s %s' % (p['handle'], json.dumps(ue, ensure_ascii=False)[:300]), flush=True)
            continue
        new['page:' + p['handle']] = h
        sent += 1
    print('pages: sent %d, unchanged %d, failed %d' % (sent, len(rows) - sent - failed, failed), flush=True)
    return failed


def blog_id(tok, handle, title):
    j = gql(tok, BLOG_FIND, {'q': 'handle:%s' % handle})
    for n in (((j.get('data') or {}).get('blogs')) or {}).get('nodes') or []:
        if n['handle'] == handle:
            return n['id']
    j = gql(tok, BLOG_CREATE, {'b': {'title': title, 'handle': handle}})
    ue = errs(j, 'blogCreate')
    if ue:
        raise RuntimeError('blogCreate %s' % json.dumps(ue, ensure_ascii=False)[:300])
    return j['data']['blogCreate']['blog']['id']


def sync_articles(tok, doc, old, new):
    bid = blog_id(tok, doc['blog'], doc['blog_title'])
    sent = failed = 0
    for a in doc['articles']:
        h = hsh(a)
        if old.get('art:' + a['handle']) == h:
            continue
        j = gql(tok, ART_FIND, {'q': 'handle:%s' % a['handle']})
        nodes = (((j.get('data') or {}).get('articles')) or {}).get('nodes') or []
        node = next((n for n in nodes if n['handle'] == a['handle'] and (n.get('blog') or {}).get('handle') == doc['blog']), None)
        body = {'title': a['title'], 'body': a['html'], 'summary': a.get('summary'), 'tags': a.get('tags') or [],
                'metafields': seo(a)}
        if node:
            j = gql(tok, ART_UPDATE, {'id': node['id'], 'a': body})
            ue = errs(j, 'articleUpdate')
        else:
            body.update({'handle': a['handle'], 'blogId': bid, 'isPublished': True,
                         'author': {'name': 'سهام آنالیز'}, 'publishDate': a.get('date')})
            j = gql(tok, ART_CREATE, {'a': body})
            ue = errs(j, 'articleCreate')
        if ue:
            failed += 1
            print('::error::article %s %s' % (a['handle'], json.dumps(ue, ensure_ascii=False)[:300]), flush=True)
            continue
        new['art:' + a['handle']] = h
        sent += 1
    print('articles: sent %d, unchanged %d, failed %d' % (sent, len(doc['articles']) - sent - failed, failed), flush=True)
    return failed


def main():
    tok = token()
    sc = {s['handle'] for s in ((gql(tok, SCOPES, {}).get('data') or {}).get('currentAppInstallation') or {}).get('accessScopes') or []}
    print('app scopes:', ' '.join(sorted(sc)), flush=True)
    if 'write_content' not in sc and 'write_online_store_pages' not in sc:
        print('::error::the Shopify app needs the write_content scope to publish guide pages', flush=True)
        sys.exit(1)
    old = {}
    if os.path.exists(HASHES):
        try:
            old = json.load(open(HASHES))
        except Exception:
            old = {}
    new = dict(old)
    failed = sync_pages(tok, json.load(open(GUIDES)), old, new) if os.path.exists(GUIDES) else 0
    for path in (ARTICLES, os.path.join(ROOT, 'pages', 'explainers.json')):
        if os.path.exists(path):
            failed += sync_articles(tok, json.load(open(path)), old, new)
    json.dump(new, open(HASHES, 'w'))
    if failed > 5:
        sys.exit(1)


if __name__ == '__main__':
    main()
