#!/usr/bin/env python3
"""Screenshots of live pages for checking layout after a deploy (workflow shot.yml -> branch "shots").
Usage: python tools/shot.py <outdir> <url> [<url> ...]   desktop 1400 px and phone 390 px, full page, plus a JSON report
(page width overflow, script errors, visible text with Latin letters inside right-to-left pages)."""
import asyncio, json, os, re, sys
from playwright.async_api import async_playwright


async def main(out, urls):
    os.makedirs(out, exist_ok=True)
    rep = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for i, u in enumerate(urls):
            for tag, w in (('d', 1400), ('m', 390)):
                pg = await b.new_page(viewport={'width': w, 'height': 900}, device_scale_factor=1)
                errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
                try:
                    await pg.goto(u, wait_until='networkidle', timeout=60000)
                except Exception as e:
                    errs.append('goto: %s' % str(e)[:150])
                await pg.wait_for_timeout(4000)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                latin = await pg.evaluate(r'''(()=>{var r=document.querySelector('[dir=rtl] #hs,#hs[dir=rtl]');if(!r)return [];
                  var o=[],w=document.createTreeWalker(r,NodeFilter.SHOW_TEXT);while(w.nextNode()){var t=w.currentNode,p=t.parentNode;
                  if(p.closest('script,style,svg'))continue;var m=t.nodeValue.match(/[A-Za-z]{2,}[A-Za-z .&-]*/g);if(m)o.push(m.join(' | '))}
                  return o.slice(0,40)})()''')
                fn = '%02d-%s.png' % (i, tag)
                await pg.screenshot(path=os.path.join(out, fn), full_page=True)
                rep['%s %s' % (u, tag)] = {'file': fn, 'scrollWidth': sw, 'errors': errs[:8], 'latin_in_rtl': latin}
                await pg.close()
        await b.close()
    json.dump(rep, open(os.path.join(out, 'report.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:6000])

asyncio.run(main(sys.argv[1], sys.argv[2:]))
