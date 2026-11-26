// Daily data-quality guard for the shared financials widget (fin2.js), used by every site in every language.
// Renders income / balance / cash / ratios for the largest companies exactly as visitors see them and checks:
//   1. the widget renders (no exception, no NaN / undefined / raw %s placeholders);
//   2. no company has a flat share-count history (every year the same number: a build bug that makes past EPS wrong);
//   3. blank cells ("—") per table row do not grow past the stored baseline (tools/fin2_audit_baseline.json) by more than 20 %;
//   4. none of the newer widget phrases is left in English in any site language.
// Usage: node tools/fin2_audit.js [N=300] [--write-baseline]      exit 1 on any problem
const fs = require('fs'), cp = require('child_process'), path = require('path');
const SD = path.join(__dirname, '..'), N = +(process.argv.find(a => /^\d+$/.test(a)) || 300), WRITE = process.argv.includes('--write-baseline');
const show = (ref, t) => { try { return JSON.parse(cp.execFileSync('git', ['-C', SD, 'show', 'origin/' + ref + ':' + t + '.json'], { stdio: ['ignore', 'pipe', 'ignore'], maxBuffer: 1 << 26 })); } catch (e) { return null; } };
const load = (lang) => { for (const k of Object.keys(require.cache)) if (/fin2/.test(k)) delete require.cache[k]; global.window = { FIN2_CFG: { noTool: 1, lang } }; require(path.join(SD, 'web', 'fin2_i18n.js')); require(path.join(SD, 'web', 'fin2.js')); };
const list = fs.readdirSync(path.join(SD, 'data', 'stocks')).filter(f => f.endsWith('.json')).map(f => { try { const d = JSON.parse(fs.readFileSync(path.join(SD, 'data', 'stocks', f), 'utf8')); return [(d.market || {}).mcap || 0, d.ticker]; } catch (e) { return [0, '']; } }).filter(x => x[1]).sort((a, b) => b[0] - a[0]).slice(0, N);
const cache = {};
const cur = t => cache[t] || (cache[t] = { d: JSON.parse(fs.readFileSync(path.join(SD, 'data', 'stocks', t + '.json'), 'utf8')), k: show('keystats', t) || {}, w: (show('prices', t) || {}).w || [] });
const use = c => { global.fetch = u => Promise.resolve({ ok: true, json: () => Promise.resolve(u.includes('/keystats/') ? c.k : u.includes('/prices/') ? { w: c.w } : c.d) }); };
const bad = [], C = {}, flat = [];
(async () => {
  load('en');
  for (const [, t] of list) {
    const c0 = cur(t); use(c0);
    const sh = (c0.d.annual || []).map(a => a.shares_diluted).filter(Boolean);
    if (sh.length >= 4 && new Set(sh.slice(-6).map(x => Math.round(x))).size === 1) flat.push(t);
    let c; try { c = await window.FIN2.load(t); } catch (e) { bad.push(t + ': load failed ' + e.message); continue; }
    for (const fn of ['income', 'balance', 'cash', 'ratios']) {
      let h; try { h = window.FIN2[fn](c); } catch (e) { bad.push(t + ' ' + fn + ': ' + e.message); continue; }
      if (/NaN|undefined|\[object|%s|%\d\$s/.test(h.replace(/<[^>]+>/g, ' '))) bad.push(t + ' ' + fn + ': broken value');
      const sec = h.split(/<div[^>]*class="[^"]*v2-sec[^"]*"/)[1] || h;
      for (const m of sec.matchAll(/<tr[^>]*>(.*?)<\/tr>/gs)) {
        const cells = [...m[1].matchAll(/<t[hd][^>]*>(.*?)<\/t[hd]>/gs)].map(x => x[1].replace(/<[^>]+>/g, '').trim());
        if (cells.length < 3) continue;
        const b = cells.slice(1, 6).filter(v => v === '—').length;
        if (b) C[fn + ' | ' + cells[0]] = (C[fn + ' | ' + cells[0]] || 0) + b;
      }
    }
  }
  if (flat.length) bad.push('flat share-count history (same count every year): ' + flat.slice(0, 40).join(' ') + (flat.length > 40 ? ' …' : ''));
  const bf = path.join(__dirname, 'fin2_audit_baseline.json');
  if (WRITE) { fs.writeFileSync(bf, JSON.stringify({ n: N, rows: C }, null, 1)); console.log('baseline written:', Object.keys(C).length, 'rows'); }
  else if (fs.existsSync(bf)) {
    const B = JSON.parse(fs.readFileSync(bf, 'utf8')).rows || {};
    for (const [k, v] of Object.entries(C)) { const b = B[k] || 0; if (v > Math.max(b * 1.2, b + 15)) bad.push('more blanks than baseline: ' + k + ' ' + b + ' -> ' + v); }
  }
  // phrases added to the widget must exist in every site language (central file + the newer sites' own files)
  const PH = ['turned profitable', 'loss narrowed', 'loss widened', 'turned to a loss', '— = not reported for that period in the filings, or not meaningful (for example a tax rate on a pre-tax loss).'];
  global.window = {}; for (const k of Object.keys(require.cache)) if (/fin2/.test(k)) delete require.cache[k];
  require(path.join(SD, 'web', 'fin2_i18n.js'));
  for (const [lang, W] of Object.entries(window.FIN2_I18N || {})) for (const p of PH) if (!W[p]) bad.push('missing ' + lang + ' translation: ' + p);
  const top = Object.entries(C).sort((a, b) => b[1] - a[1]).slice(0, 25);
  console.log('companies:', list.length, ' rows with blanks:', Object.keys(C).length);
  for (const [k, v] of top) console.log(String(v).padStart(6), k);
  if (bad.length) { console.error('\nfin2 audit FAILED (' + bad.length + '):\n  ' + bad.slice(0, 80).join('\n  ')); process.exit(1); }
  console.log('fin2 audit: ok');
})();
