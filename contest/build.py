#!/usr/bin/env python3
"""Build web/contest.js (the whole contest page: style + markup + logic) from
contest/page.html (snapshot of the live page), contest/rank.js and contest/extra.css.
The Shopify page body then only needs: <div id="rzk" dir="rtl"></div><script src=".../web/contest.js"></script>"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(D, 'page.html'), encoding='utf-8').read()
i = s.find('<div id="rzk" dir="rtl">'); j = s.find('</script>\n</div>', i) + len('</script>\n</div>')
blk = s[i + len('<div id="rzk" dir="rtl">'):j - len('</div>')]
sc = blk.rfind('<script>')
markup = blk[:sc].strip()
js = blk[sc + len('<script>'):blk.rfind('</script>')]
extra = open(os.path.join(D, 'extra.css'), encoding='utf-8').read()
markup = markup.replace('</style>', extra + '</style>', 1)
rank = open(os.path.join(D, 'rank.js'), encoding='utf-8').read()
a = js.find('function px(t){'); b = js.find('function setupForm(){')
assert a > 0 and b > a
js = js[:a] + rank + js[b:]
rep = [("var PRICES='https://cdn.jsdelivr.net/gh/mrezahajilou-ops/stock-data@prices';", ''),
       ("var X=R[1]||{}, ex={};", "var X=R[1]||{}, ex={}; XF=X.final||null;"),
       ("box.innerHTML='<div class=\"empty\">در حال محاسبه‌ی بازده‌ها…</div>';", "if(!ROWS.length)box.innerHTML='<div class=\"empty\">در حال محاسبه‌ی بازده‌ها…</div>';"),
       ("loadEntries().then(function(E){renderPop(E);renderRank(E);setupForm()})",
        "loadEntries().then(function(E){if(Date.now()>=STARTMS){[].forEach.call(document.querySelectorAll('#rzk .tabs button'),function(x){if(x.dataset.b==='rank')x.click()})}renderPop(E);renderRank(E);setupForm()})")]
for o, n in rep:
    assert o in js, o[:60]
    js = js.replace(o, n, 1)
out = ('/* rezahajiloubooks.com stock contest - built by contest/build.py, do not edit by hand */\n'
       '(function(){var R=document.getElementById("rzk");if(!R)return;R.innerHTML=' + json.dumps(markup, ensure_ascii=False) + ';\n' + js + '\n})();\n')
os.makedirs(os.path.join(D, '..', 'web'), exist_ok=True)
open(os.path.join(D, '..', 'web', 'contest.js'), 'w', encoding='utf-8').write(out)
print('web/contest.js', len(out), 'bytes')
