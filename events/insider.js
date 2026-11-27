
/* ---------- insider trading feed: SEC EDGAR Form 4, served at GET /c/insider.json ----------
   Every Form 4 that lands on EDGAR is listed in the SEC's "latest filings" Atom feed within minutes. Each run reads that feed,
   opens the filings it has not seen yet (one request each: the full submission text holds the XML) and keeps the open-market
   buys (code P) and sales (code S): one row per filing and code, shares summed, price weighted.
   Refreshed by the 5-minute cron and, while someone has the page open, at most once a minute from the request itself.
   The SEC asks for a contact in the User-Agent: set the worker variable SEC_UA ("Name contact-address") in Cloudflare.
   Public data from the SEC; the sites show it as facts (who, what, when, how much), never as advice. */
const INS_FEED = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=include&start=0&count=100&output=atom';
const INS_KEEP = 800, INS_SEEN = 900, INS_GAP = 50;

function insVal(s, tag) {
  const m = s.match(new RegExp('<' + tag + '>\\s*(?:<value>)?\\s*([^<]*)'));
  return m ? m[1].trim() : '';
}
const insNum = (x) => { const v = parseFloat(String(x || '').replace(/,/g, '')); return isFinite(v) ? v : 0; };
const insBool = (s, tag) => /^(1|true)$/i.test(insVal(s, tag));
const insName = (n) => String(n || '').replace(/\s+/g, ' ').trim().split(' ')
  .map(w => (w === w.toUpperCase() || w === w.toLowerCase()) && w.length > 1 && !/^(II|III|IV|LLC|LP|L\.P\.|INC\.?|JR\.?|SR\.?)$/i.test(w) ? w[0].toUpperCase() + w.slice(1).toLowerCase() : w).join(' ');

// one Form 4 XML -> rows (open-market buys and sales only)
function insParse(xml, acc, filed) {
  const t = insVal(xml, 'issuerTradingSymbol').toUpperCase().replace(/[^A-Z0-9.\-]/g, '').replace('.', '-');
  if (!t || t === 'NONE' || t === 'NA' || t.length > 8) return [];
  const co = insVal(xml, 'issuerName').replace(/&amp;/g, '&');
  const own = (xml.match(/<reportingOwner>[\s\S]*?<\/reportingOwner>/) || [''])[0];
  const nOwners = (xml.match(/<reportingOwner>/g) || []).length;
  const n = insName(insVal(own, 'rptOwnerName').replace(/&amp;/g, '&'));
  let r;
  if (insBool(own, 'isOfficer')) r = (insVal(own, 'officerTitle') || 'Officer').replace(/&amp;/g, '&').replace(/\s+/g, ' ').slice(0, 60);
  else if (insBool(own, 'isDirector')) r = 'Director';
  else if (insBool(own, 'isTenPercentOwner')) r = '10% owner';
  else r = 'Other';
  const plan = insBool(xml, 'aff10b5One') || /10b5-1/i.test(xml);
  const by = {};
  for (const b of xml.match(/<nonDerivativeTransaction>[\s\S]*?<\/nonDerivativeTransaction>/g) || []) {
    const c = insVal(b, 'transactionCode');
    if (c !== 'P' && c !== 'S') continue;
    const q = insNum(insVal(b, 'transactionShares')), p = insNum(insVal(b, 'transactionPricePerShare'));
    if (!(q > 0)) continue;
    const d = insVal(b, 'transactionDate').slice(0, 10), h = insNum(insVal(b, 'sharesOwnedFollowingTransaction'));
    const o = by[c] || (by[c] = { a: acc, t, co, n, r, c, d, q: 0, v: 0, h: 0, f: filed, x: plan ? 1 : 0, m: nOwners > 1 ? 1 : 0 });
    o.q += q; o.v += q * p;
    if (d > o.d) o.d = d;
    if (h) o.h = h;   // holdings after the last line of the filing
  }
  return Object.values(by).map(o => ({ ...o, q: Math.round(o.q), v: Math.round(o.v), p: o.q ? Math.round(o.v / o.q * 100) / 100 : 0, h: Math.round(o.h) }));
}

async function insiderRefresh(env, maxDocs) {
  const now = Math.floor(Date.now() / 1000);
  const lock = await env.DB.prepare("SELECT ts FROM c_kv WHERE k='insider_lock'").first();
  if (lock && now - lock.ts < INS_GAP) return 0;
  await env.DB.prepare("INSERT INTO c_kv (k, v, ts) VALUES ('insider_lock', '1', ?1) ON CONFLICT(k) DO UPDATE SET ts=?1").bind(now).run();
  const H = { 'User-Agent': env.SEC_UA || 'StockAnaliz insider feed stockanaliz.com', 'Accept': 'application/atom+xml, text/xml, text/plain, */*' };
  const fr = await fetch(INS_FEED, { headers: H });
  if (!fr.ok) {
    await env.DB.prepare("INSERT INTO c_kv (k, v, ts) VALUES ('insider_err', ?1, ?2) ON CONFLICT(k) DO UPDATE SET v=?1, ts=?2").bind('feed ' + fr.status, now).run();
    return 0;
  }
  const feed = await fr.text();
  const row0 = await env.DB.prepare("SELECT v FROM c_kv WHERE k='insider'").first();
  const st = row0 ? JSON.parse(row0.v) : { rows: [], seen: [] };
  const seen = new Set(st.seen || []);
  const todo = [], inFeed = new Set();
  for (const e of feed.split('<entry>').slice(1)) {
    const href = (e.match(/<link[^>]*href="([^"]+)"/) || [])[1] || '';
    const m = href.match(/\/edgar\/data\/(\d+)\/(\d{18})\//);
    if (!m) continue;
    const acc = m[2].slice(0, 10) + '-' + m[2].slice(10, 12) + '-' + m[2].slice(12);
    if (inFeed.has(acc)) continue;   // each filing is listed twice (issuer and reporting owner)
    inFeed.add(acc);
    if (seen.has(acc)) continue;
    const upd = (e.match(/<updated>([^<]+)<\/updated>/) || [])[1] || '';
    const fd = upd && !isNaN(Date.parse(upd)) ? new Date(upd) : new Date();
    todo.push({ cik: m[1], dir: m[2], acc, filed: fd.toISOString().slice(0, 19) + 'Z' });
  }
  const add = [], lim = maxDocs || 20;
  let fails = 0;
  for (const x of todo.slice(0, lim)) {
    let txt = '';
    try {
      const r = await fetch(`https://www.sec.gov/Archives/edgar/data/${x.cik}/${x.dir}/${x.acc}.txt`, { headers: H });
      if (r.ok) txt = await r.text(); else fails++;
    } catch (e) { fails++; continue; }
    if (!txt) continue;   // not marked seen: tried again next run
    seen.add(x.acc);
    const doc = (txt.match(/<ownershipDocument>[\s\S]*?<\/ownershipDocument>/) || [''])[0];
    if (doc) add.push(...insParse(doc, x.acc, x.filed));
  }
  const rows = add.concat(st.rows || []);
  rows.sort((a, b) => (b.f || '').localeCompare(a.f || ''));
  const out = { as_of: new Date().toISOString().slice(0, 19) + 'Z', src: 'SEC EDGAR Form 4', rows: rows.slice(0, INS_KEEP),
                seen: [...seen].slice(-INS_SEEN), backlog: Math.max(0, todo.length - lim), fails };
  await env.DB.prepare("INSERT INTO c_kv (k, v, ts) VALUES ('insider', ?1, ?2) ON CONFLICT(k) DO UPDATE SET v=?1, ts=?2").bind(JSON.stringify(out), now).run();
  return add.length;
}

async function insiderServe(env, ctx, h) {
  let kv = await env.DB.prepare("SELECT v, ts FROM c_kv WHERE k='insider'").first();
  const now = Math.floor(Date.now() / 1000);
  if (!kv) { try { await insiderRefresh(env, 20); } catch (e) {} kv = await env.DB.prepare("SELECT v, ts FROM c_kv WHERE k='insider'").first(); }
  else if (now - kv.ts >= 60) ctx.waitUntil(insiderRefresh(env, 20).catch(() => 0));
  if (!kv) {
    const err = await env.DB.prepare("SELECT v FROM c_kv WHERE k='insider_err'").first();
    return new Response(JSON.stringify({ error: 'not ready', detail: err ? err.v : '' }), { status: 503, headers: { 'Content-Type': 'application/json', ...h } });
  }
  const o = JSON.parse(kv.v);
  delete o.seen;
  o.checked = new Date(kv.ts * 1000).toISOString().slice(0, 19) + 'Z';
  return new Response(JSON.stringify(o), { headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=20', ...h } });
}
