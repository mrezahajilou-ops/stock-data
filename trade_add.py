#!/usr/bin/env python3
"""Add one trade to Reza's portfolio (metaobject rz_trade) from the command line / GitHub Actions.
Env: TR_ACTION (BUY|SELL|DIVIDEND|DEPOSIT|WITHDRAW), TR_TICKER, TR_SHARES, TR_PRICE, TR_AMOUNT, TR_DATE (ISO UTC), TR_NOTE, TR_LABEL.
Auth: SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET (write_metaobjects). Prints only the handle - never the private numbers.
"""
import os, re, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_shopify import token, gql  # noqa: E402

FA = {'BUY': 'خرید', 'SELL': 'فروش', 'DIVIDEND': 'سود نقدی', 'DEPOSIT': 'واریز', 'WITHDRAW': 'برداشت'}
M = '''mutation($m: MetaobjectCreateInput!) { metaobjectCreate(metaobject: $m) { metaobject { handle } userErrors { field message } } }'''

def main():
    a = os.environ.get('TR_ACTION', '').strip().upper()
    t = os.environ.get('TR_TICKER', '').strip().upper()
    if a not in FA:
        sys.exit('bad action')
    if a in ('BUY', 'SELL', 'DIVIDEND') and not re.match(r'^[A-Z][A-Z0-9.\-]{0,8}$', t):
        sys.exit('bad ticker')
    date = os.environ.get('TR_DATE', '').strip() or dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z')
    fields = [{'key': 'label', 'value': os.environ.get('TR_LABEL', '').strip() or (FA[a] + (' ' + t if t else ''))},
              {'key': 'date', 'value': date}, {'key': 'action', 'value': a}]
    if t: fields.append({'key': 'ticker', 'value': t})
    for k, env in (('shares', 'TR_SHARES'), ('price', 'TR_PRICE'), ('amount', 'TR_AMOUNT')):
        v = os.environ.get(env, '').strip()
        if v: fields.append({'key': k, 'value': str(float(v))})
    note = os.environ.get('TR_NOTE', '').strip()
    if note: fields.append({'key': 'note', 'value': note})
    handle = '%s-%s-%s' % (a.lower(), (t or 'cash').lower().replace('.', '-'), date[:16].lower().replace(':', '').replace('t', '-'))
    j = gql(token(), M, {'m': {'type': 'rz_trade', 'handle': handle, 'fields': fields}})
    r = (j.get('data') or {}).get('metaobjectCreate') or {}
    if r.get('userErrors') or j.get('errors'):
        sys.exit('failed: %s' % json.dumps(r.get('userErrors') or j.get('errors'))[:300])
    print('added', r['metaobject']['handle'])

if __name__ == '__main__':
    main()
