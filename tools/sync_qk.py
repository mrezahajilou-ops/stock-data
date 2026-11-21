"""Copy the quick-keys bar (web_src/qk.js + qk.css) into web/stock.html, which carries its own copy because the
Persian site loads that page as a fragment into Shopify. Run after changing either file.
usage: python3 tools/sync_qk.py"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js = open(os.path.join(R, 'web_src', 'qk.js'), encoding='utf8').read()
css = open(os.path.join(R, 'web_src', 'qk.css'), encoding='utf8').read()
block = '<style>/*QK-CSS*/\n%s</style>\n<script>/*QK-INLINE*/\n%s</script>\n' % (css, js)
p = os.path.join(R, 'web', 'stock.html')
s = open(p, encoding='utf8').read()
s2, n = re.subn(r'<style>/\*QK-CSS\*/.*?</script>\n', lambda m: block, s, flags=re.S)
if not n:
    s2 = s.rstrip('\n') + '\n' + block
open(p, 'w', encoding='utf8').write(s2)
print('stock.html: quick keys', 'updated' if n else 'added')
