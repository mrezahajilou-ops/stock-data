/**
 * Portfolio contest (مسابقه‌ی پورتفو) — runs inside the rz-events worker, data in the same D1 database.
 *
 * Everyone starts with $10,000 of virtual cash and builds a portfolio of US stocks / ETFs. Orders are placed at the
 * market: a buy or sell is filled at the FIRST quote published after the order (quotes branch, every ~15 min in market
 * hours), so nobody can trade on a price they have already seen. Dividends are credited as cash on the ex-date and
 * splits change share counts (events from the contest-data branch). Returns are measured on daily snapshots.
 *
 * Identity: the shop theme signs the logged-in customer (id | email | pro | time) with HMAC-SHA256 (CONTEST_SECRET,
 * set as an encrypted variable on the worker and in the theme snippet rz-contest-token). Nothing else is trusted.
 *
 *   GET  /c/board?sort=total|cagr|y1|ytd|q|m&off=0      leaderboard (eligible = 3+ stock positions), cached 5 min
 *   GET  /c/me                       (auth) my profiles with positions, orders, trades
 *   POST /c/profile                  (auth) {name, strategy, accept}        one new profile per customer per 182 days
 *   POST /c/order                    (auth) {pid, side:'buy'|'sell', t, amount (buy, $) | qty (sell, shares|'all'), note}
 *   POST /c/cancel                   (auth) {pid, oid}
 *   GET  /c/p/:id                    public profile; holdings/trades only for the owner, the admin, or (from DETAIL_FROM)
 *                                    Stock Pro subscribers
 *   GET  /c/hist/:id                 daily values for the chart (same visibility as details)
 *   GET  /c/tickers                  tickers currently held (for the corporate-actions job)
 *   POST /c/admin                    (admin) {pid, status:'active'|'hidden'}
 */
const C_START = 10000;
const C_MAX_W = 0.70;              // a buy may not make one position more than 70% of the portfolio
const C_MIN_STOCKS = 3;            // needed to appear in the ranking
const C_NEW_EVERY = 182 * 86400;   // one new profile per customer every ~6 months
const C_DETAIL_FROM = Date.UTC(2027, 1, 1) / 1000;   // 1 Feb 2027: details open for Stock Pro
const C_CONTEST_START = '2027-01-01';
let C_RAW = 'https://raw.githubusercontent.com/mrezahajilou-ops/stock-data';   // RAW_BASE var overrides (local tests)
const C_ADMIN = ['mreza.hajilou@gmail.com'];
const C_TOKEN_TTL = 12 * 3600;

const C_SCHEMA = [
  `CREATE TABLE IF NOT EXISTS c_profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, cid TEXT NOT NULL, email TEXT, name TEXT NOT NULL,
     strategy TEXT, created INTEGER NOT NULL, cash REAL NOT NULL, status TEXT NOT NULL DEFAULT 'active', last_trade INTEGER,
     house INTEGER NOT NULL DEFAULT 0)`,
  `CREATE INDEX IF NOT EXISTS c_prof_cid ON c_profiles (cid)`,
  `CREATE TABLE IF NOT EXISTS c_pos (pid INTEGER NOT NULL, t TEXT NOT NULL, qty REAL NOT NULL, cost REAL NOT NULL, PRIMARY KEY (pid, t))`,
  `CREATE TABLE IF NOT EXISTS c_orders (id INTEGER PRIMARY KEY AUTOINCREMENT, pid INTEGER NOT NULL, ts INTEGER NOT NULL, side TEXT NOT NULL,
     t TEXT NOT NULL, amount REAL, qty REAL, note TEXT, status TEXT NOT NULL DEFAULT 'pending', fill_ts INTEGER, price REAL,
     fill_qty REAL, fill_amt REAL, reason TEXT)`,
  `CREATE INDEX IF NOT EXISTS c_ord_pid ON c_orders (pid, ts)`,
  `CREATE INDEX IF NOT EXISTS c_ord_status ON c_orders (status)`,
  `CREATE TABLE IF NOT EXISTS c_cash (id INTEGER PRIMARY KEY AUTOINCREMENT, pid INTEGER NOT NULL, ts INTEGER NOT NULL, kind TEXT NOT NULL,
     t TEXT, amount REAL NOT NULL, note TEXT, ref TEXT, UNIQUE(pid, ref))`,
  `CREATE TABLE IF NOT EXISTS c_snap (pid INTEGER NOT NULL, d TEXT NOT NULL, v REAL NOT NULL, PRIMARY KEY (pid, d))`,
  `CREATE TABLE IF NOT EXISTS c_wins (period TEXT PRIMARY KEY, kind TEXT NOT NULL, pid INTEGER NOT NULL, ret REAL, decided INTEGER NOT NULL)`,
  `CREATE TABLE IF NOT EXISTS c_quotes (t TEXT PRIMARY KEY, p REAL NOT NULL, chg REAL, prev REAL, ts TEXT NOT NULL)`,
`CREATE TABLE IF NOT EXISTS c_hold (t TEXT PRIMARY KEY, ts INTEGER NOT NULL, note TEXT)`,
`CREATE TABLE IF NOT EXISTS c_corp (t TEXT NOT NULL, type TEXT NOT NULL, d TEXT NOT NULL, v REAL NOT NULL, PRIMARY KEY (t, type, d))`,
`CREATE TABLE IF NOT EXISTS c_corpchk (t TEXT PRIMARY KEY, ts INTEGER NOT NULL)`,
`CREATE TABLE IF NOT EXISTS c_kv (k TEXT PRIMARY KEY, v TEXT NOT NULL, ts INTEGER NOT NULL)`,
];
/* migrations for tables created by an earlier version */
const C_MIGRATE = ['ALTER TABLE c_profiles ADD COLUMN house INTEGER NOT NULL DEFAULT 0',
  'ALTER TABLE c_profiles ADD COLUMN spy0 REAL', 'ALTER TABLE c_snap ADD COLUMN n INTEGER'];

/* ---------- helpers ---------- */
const cq = async (env, sql, ...a) => (await env.DB.prepare(sql).bind(...a).all()).results || [];
const c1 = async (env, sql, ...a) => (await env.DB.prepare(sql).bind(...a).first()) || null;
const cnow = () => Math.floor(Date.now() / 1000);
const cday = (ts) => new Date(ts * 1000).toISOString().slice(0, 10);
const cclean = (s, n) => String(s || '').replace(/[\u0000-\u001f<>]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
let C_SCHEMA_OK = false;
let C_ENV = null;
async function cSchema(env) {
  C_ENV = env;
  if (env.RAW_BASE) C_RAW = env.RAW_BASE;
  if (C_SCHEMA_OK) return;
  await env.DB.batch(C_SCHEMA.map(s => env.DB.prepare(s)));
  for (const m of C_MIGRATE) { try { await env.DB.prepare(m).run(); } catch (e) { /* already there */ } }
  C_SCHEMA_OK = true;
}

async function cHmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(msg));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, '0')).join('');
}
/** token = "c|e|p|ts|sig", sig = hex HMAC-SHA256 of "c|e|p|ts"; built by the theme (Liquid hmac_sha256). */
async function cAuth(req, env) {
  const hk = (req.headers.get('X-RZ-House') || '').trim();
  if (hk && env.HOUSE_KEY && hk.length >= 32 && hk === env.HOUSE_KEY) return { cid: 'house', email: C_ADMIN[0], pro: true, admin: true, house: true };
  const tok = (req.headers.get('X-RZ-Token') || '').trim();
  if (!tok || !env.CONTEST_SECRET) return null;
  const [c, e, p, ts, sig] = tok.split('|');
  if (!c || !/^\d+$/.test(c) || !/^\d+$/.test(ts || '') || !/^[0-9a-f]{64}$/.test(sig || '')) return null;
  if (Math.abs(cnow() - parseInt(ts, 10)) > C_TOKEN_TTL) return null;
  const want = await cHmac(env.CONTEST_SECRET, [c, e, p, ts].join('|'));
  if (want !== sig) return null;
  const email = String(e || '').toLowerCase();
  return { cid: c, email, pro: p === '1', admin: C_ADMIN.includes(email) };
}

/* quotes: {t: [price, chg, prev, tradeTime]} cached 60 s; universe + ETF names cached 1 h */
async function cFetchJSON(url, ttl) {
  const cache = caches.default, key = new Request(url.split('?')[0] + '?cache=' + ttl);
  const hit = await cache.match(key);
  if (hit) return hit.json();
  const r = await fetch(url + (url.includes('?') ? '&' : '?') + 'v=' + Math.floor(Date.now() / (ttl * 1000)), { cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error('fetch ' + r.status + ' ' + url);
  const txt = await r.text();
  await cache.put(key, new Response(txt, { headers: { 'Content-Type': 'application/json', 'Cache-Control': 'max-age=' + ttl } }));
  return JSON.parse(txt);
}
// quotes = GitHub file (whole market, can lag) overlaid with the contest's own live quotes (c_quotes, refreshed every 5 min by cron)
const cQuotes = async (fill) => {
  let q = null, kvq = false;
  // whole-market quotes refreshed by the worker itself (GitHub runners are blocked by Nasdaq); the GitHub file is the fallback
  // (not for fills: the screener has no trade times, so a fill could use a price from before the order)
  if (C_ENV && !fill) { try { const kv = await C_ENV.DB.prepare("SELECT v, ts FROM c_kv WHERE k='quotes'").first(); if (kv && cnow() - kv.ts < 6 * 3600) { q = JSON.parse(kv.v).q; kvq = true; } } catch (e) {} }
  if (!q) q = await cFetchJSON(C_RAW + '/quotes/quotes.json', 60).then(j => j.q || {});
  if (!C_ENV) return q;
  try {
    for (const r of (await C_ENV.DB.prepare('SELECT t, p, chg, prev, ts FROM c_quotes').all()).results || []) {
      const f = q[r.t], ft = f && f[3] ? Date.parse(f[3]) : 0;
      if (kvq ? (!f || Date.now() - Date.parse(r.ts) < 30 * 60000) : !(ft >= Date.parse(r.ts))) q[r.t] = [r.p, r.chg, r.prev, r.ts];   // fresh last-trade quotes of held tickers win
    }
    // a ticker on hold (price jump that looks like an unprocessed split) keeps its last contest price
    for (const r of (await C_ENV.DB.prepare('SELECT q.t, q.p, q.chg, q.prev, q.ts FROM c_hold h JOIN c_quotes q ON q.t=h.t').all()).results || []) q[r.t] = [r.p, r.chg, r.prev, r.ts];
  } catch (e) { /* table not ready */ }
  return q;
};
const cUniverse = () => cFetchJSON(C_RAW + '/contest-data/universe.json', 3600);
const cCorp = () => cFetchJSON(C_RAW + '/contest-data/corp.json', 3600).catch(() => ({ events: [] }));
const cQtime = (q) => { const t = q && q[3] ? Date.parse(q[3]) : NaN; return isNaN(t) ? null : Math.floor(t / 1000); };

async function cLive(tickers) {
  // live last-sale price from Nasdaq's watchlist API (same source as quotes.py), 20 symbols per call
  const out = {}, T = [...new Set(tickers)].slice(0, 160);
  const nm = (x) => { const v = parseFloat(String(x == null ? '' : x).replace(/[$,%+]/g, '')); return isNaN(v) ? null : v; };
  let etf = {};
  try { etf = (await cUniverse()).etf || {}; } catch (e) {}
  const H = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/' };
  for (let i = 0; i < T.length; i += 20) {
    const qs = T.slice(i, i + 20).map(t => 'symbol=' + encodeURIComponent(t.replace('-', '.').toLowerCase() + (etf[t] ? '|etf' : '|stocks'))).join('&');
    try {
      const r = await fetch('https://api.nasdaq.com/api/quote/watchlist?' + qs, { headers: H });
      if (!r.ok) continue;
      for (const d of ((await r.json()).data || [])) {
        const t = String(d.symbol || '').toUpperCase().replace('.', '-'), p = parseFloat(String(d.lastSalePrice || '').replace(/[$,]/g, ''));
        const ts = d.lastTradeTimestampDateTime || d.lastTradeTimestamp;
        if (t && p > 0 && ts && !isNaN(Date.parse(ts))) out[t] = [p, nm(d.percentageChange), nm(d.previousClosePrice), ts];
      }
    } catch (e) { /* keep the file quote */ }
  }
  return out;
}
async function cPositions(env, pid) { return cq(env, 'SELECT t, qty, cost FROM c_pos WHERE pid=?1 AND qty>0.0000001 ORDER BY t', pid); }
function cValue(prof, pos, Q) {
  let v = prof.cash;
  for (const p of pos) { const q = Q[p.t]; v += p.qty * (q ? q[0] : p.cost / p.qty); }
  return v;
}

/* ---------- order validation + fills ---------- */
async function cPlace(env, me, b) {
  const pid = parseInt(b.pid, 10);
  const prof = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1 AND (cid=?2 OR (house=1 AND ?3=1))', pid, me.cid, me.admin ? 1 : 0);
  if (!prof) return [403, { error: 'پروفایل پیدا نشد' }];
  if (prof.status !== 'active') return [403, { error: 'این پروفایل غیرفعاله' }];
  const side = b.side === 'sell' ? 'sell' : b.side === 'buy' ? 'buy' : null;
  const t = String(b.t || '').toUpperCase().trim();
  if (!side || !/^[A-Z][A-Z0-9.\-]{0,8}$/.test(t)) return [400, { error: 'سفارش نامعتبر' }];
  const note = cclean(b.note, 500);
  const today = await c1(env, 'SELECT COUNT(*) n FROM c_orders WHERE pid=?1 AND ts>?2', pid, cnow() - 86400);
  if (today && today.n >= 40) return [429, { error: 'حداکثر ۴۰ سفارش در ۲۴ ساعت' }];
  const [Q, U] = await Promise.all([cQuotes(), cUniverse()]);
  const q = Q[t];
  if (!q) return [400, { error: 'قیمت این نماد در دسترس نیست' }];
  if (await c1(env, 'SELECT t FROM c_hold WHERE t=?1', t)) return [400, { error: 'معامله‌ی این نماد موقتاً متوقفه (تغییر غیرعادی قیمت، احتمالاً اسپلیت). کمی بعد دوباره امتحان کن.' }];
  const pos = await cPositions(env, pid);
  const pend = await cq(env, "SELECT side, t, amount, qty FROM c_orders WHERE pid=?1 AND status IN ('pending','filling')", pid);
  if (pend.length >= 20) return [429, { error: 'حداکثر ۲۰ سفارش باز' }];
  if (side === 'buy') {
    if (!(U.t || []).includes(t)) return [400, { error: 'این نماد در مسابقه مجاز نیست (سهام آمریکا با ارزش بازار بالای ۱ میلیارد دلار و قیمت بالای ۵ دلار، یا ETFهای فهرست)' }];
    const amount = Math.round(Number(b.amount) * 100) / 100;
    if (!(amount >= 10)) return [400, { error: 'حداقل مبلغ خرید ۱۰ دلاره' }];
    const reserved = pend.filter(o => o.side === 'buy').reduce((s, o) => s + o.amount, 0);
    if (amount > prof.cash - reserved + 0.005) return [400, { error: 'نقد کافی نداری', cash: prof.cash - reserved }];
    const total = cValue(prof, pos, Q);
    const cur = (pos.find(p => p.t === t) || { qty: 0 }).qty * q[0] + pend.filter(o => o.side === 'buy' && o.t === t).reduce((s, o) => s + o.amount, 0);
    if ((cur + amount) / total > C_MAX_W + 1e-9) return [400, { error: 'بعد از این خرید، این سهم بیش از ۷۰٪ پورتفو می‌شه', max: Math.max(0, C_MAX_W * total - cur) }];
    const r = await env.DB.prepare("INSERT INTO c_orders (pid, ts, side, t, amount, note) VALUES (?1, ?2, 'buy', ?3, ?4, ?5)").bind(pid, cnow(), t, amount, note).run();
    return [200, { ok: true, id: r.meta.last_row_id, est: q[0] }];
  }
  const held = (pos.find(p => p.t === t) || { qty: 0 }).qty - pend.filter(o => o.side === 'sell' && o.t === t).reduce((s, o) => s + (o.qty || 0), 0);
  let qty = b.qty === 'all' ? held : Math.floor(Number(b.qty) * 1e6) / 1e6;
  if (!(qty > 0) || qty > held + 1e-9) return [400, { error: 'تعداد بیشتر از سهم‌هایی که داری', held }];
  const r = await env.DB.prepare("INSERT INTO c_orders (pid, ts, side, t, qty, note) VALUES (?1, ?2, 'sell', ?3, ?4, ?5)").bind(pid, cnow(), t, Math.min(qty, held), note).run();
  return [200, { ok: true, id: r.meta.last_row_id, est: q[0] }];
}

/** Fill every pending order whose ticker has a quote newer than the order. Runs from cron and on /c/me. */
const cReg = (ts) => { const m = new Date(ts * 1000).toLocaleString('en-US', { timeZone: 'America/New_York', hourCycle: 'h23', weekday: 'short', hour: '2-digit', minute: '2-digit' }).match(/(\w+),? (\d\d):(\d\d)/); if (!m || /Sat|Sun/.test(m[1])) return false; const x = +m[2] * 60 + +m[3]; return x >= 570 && x < 960; };
async function cFill(env, onlyPid) {
  // an order claimed by a fill that died before committing goes back to the queue after 10 minutes
  await env.DB.prepare("UPDATE c_orders SET status='pending', fill_ts=NULL WHERE status='filling' AND fill_ts<?1").bind(cnow() - 600).run();
  const pend = onlyPid ? await cq(env, "SELECT * FROM c_orders WHERE status='pending' AND pid=?1 ORDER BY ts", onlyPid)
                       : await cq(env, "SELECT * FROM c_orders WHERE status='pending' ORDER BY ts LIMIT 500");
  if (!pend.length) return 0;
  const Q0 = await cQuotes(true);
  const hold = new Set((await cq(env, 'SELECT t FROM c_hold')).map(r => r.t));
  // the GitHub quotes file can lag by hours: fetch a live price for every ticker whose file quote is older than its order (+ SPY for the benchmark)
  const stale = [...new Set(pend.filter(o => { const t = cQtime(Q0[o.t]); return !hold.has(o.t) && (!t || t <= o.ts); }).map(o => o.t))];
  const Q = stale.length ? Object.assign({}, Q0, await cLive(stale.concat(['SPY']))) : Q0;
  let n = 0;
  for (const o of pend) {
    if (hold.has(o.t)) continue;                                     // wait until the split is processed
    const q = Q[o.t], qt = cQtime(q);
    // no newer trade yet, an absurd tick, or a big jump printed outside regular hours (pre/after-market prints can be bogus:
    // CCEP 164.60 at 4 am ET on 2026-11-11, real price 116): those wait for the regular session
    if (!q || !qt || qt <= o.ts || (q[1] != null && Math.abs(q[1]) >= 90) || (q[1] != null && Math.abs(q[1]) >= 20 && !cReg(qt))) {
      if (cnow() - o.ts > 6 * 86400) await env.DB.prepare("UPDATE c_orders SET status='rejected', reason='no price for 6 days' WHERE id=?1 AND status='pending'").bind(o.id).run();
      continue;
    }
    // claim the order: the 5-minute cron and a visitor's request can reach the same order at the same moment
    // (2026-11-10: a sell was credited twice). Every write below is also guarded inside one transaction.
    const ts = cnow();
    if (!(await env.DB.prepare("UPDATE c_orders SET status='filling', fill_ts=?2 WHERE id=?1 AND status='pending'").bind(o.id, ts).run()).meta.changes) continue;
    const price = q[0];
    const prof = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1', o.pid);
    const pos = await c1(env, 'SELECT qty, cost FROM c_pos WHERE pid=?1 AND t=?2', o.pid, o.t) || { qty: 0, cost: 0 };
    const done = "EXISTS (SELECT 1 FROM c_orders WHERE id=?9 AND status='filled' AND fill_ts=?8)";
    let stmts = null;
    if (!prof) { await env.DB.prepare("UPDATE c_orders SET status='rejected', reason='profile' WHERE id=?1").bind(o.id).run(); continue; }
    if (o.side === 'buy') {
      // re-check cash and the 70% cap at the fill price; shrink the order if the price moved against it
      const all = await cPositions(env, o.pid);
      const total = cValue(prof, all, Q);
      const room = Math.max(0, C_MAX_W * total - pos.qty * price);
      const amt = Math.floor(Math.min(o.amount, prof.cash, room) * 100) / 100;
      if (amt < 1) { await env.DB.prepare("UPDATE c_orders SET status='rejected', reason=?2 WHERE id=?1").bind(o.id, amt <= 0 && room <= 0 ? '70% cap' : 'cash').run(); continue; }
      const qty = amt / price;
      stmts = [
        env.DB.prepare("UPDATE c_orders SET status='filled', price=?3, fill_qty=?4, fill_amt=?5 WHERE id=?9 AND status='filling' AND fill_ts=?8 AND (SELECT cash FROM c_profiles WHERE id=?1) >= ?5 - 0.005")
          .bind(o.pid, null, price, qty, amt, null, null, ts, o.id),
        // S&P 500 benchmark starts at the portfolio's first fill (not at profile creation)
        ...(Q.SPY && Q.SPY[0] > 0 ? [env.DB.prepare('UPDATE c_profiles SET spy0=?2 WHERE id=?1 AND last_trade IS NULL AND ' + done).bind(o.pid, Q.SPY[0], null, null, null, null, null, ts, o.id)] : []),
        env.DB.prepare('UPDATE c_profiles SET cash=cash-?2, last_trade=?8 WHERE id=?1 AND ' + done).bind(o.pid, amt, null, null, null, null, null, ts, o.id),
        env.DB.prepare('INSERT INTO c_pos (pid, t, qty, cost) SELECT ?1, ?2, ?3, ?4 WHERE ' + done + ' ON CONFLICT(pid, t) DO UPDATE SET qty=qty+?3, cost=cost+?4')
          .bind(o.pid, o.t, qty, amt, null, null, null, ts, o.id),
      ];
    } else {
      const qty = Math.min(o.qty, pos.qty);
      if (!(qty > 0)) { await env.DB.prepare("UPDATE c_orders SET status='rejected', reason='no shares' WHERE id=?1").bind(o.id).run(); continue; }
      const amt = qty * price;
      stmts = [
        env.DB.prepare("UPDATE c_orders SET status='filled', price=?3, fill_qty=?4, fill_amt=?5 WHERE id=?9 AND status='filling' AND fill_ts=?8 AND (SELECT qty FROM c_pos WHERE pid=?1 AND t=?2) >= ?4 - 1e-9")
          .bind(o.pid, o.t, price, qty, amt, null, null, ts, o.id),
        env.DB.prepare('UPDATE c_pos SET cost=cost*(qty-?3)/qty, qty=qty-?3 WHERE pid=?1 AND t=?2 AND ' + done).bind(o.pid, o.t, qty, null, null, null, null, ts, o.id),
        env.DB.prepare('DELETE FROM c_pos WHERE pid=?1 AND t=?2 AND qty<=1e-7').bind(o.pid, o.t),
        env.DB.prepare('UPDATE c_profiles SET cash=cash+?5, last_trade=?8 WHERE id=?1 AND ' + done).bind(o.pid, null, null, null, amt, null, null, ts, o.id),
      ];
    }
    await env.DB.batch(stmts);
    const st = await c1(env, 'SELECT status FROM c_orders WHERE id=?1', o.id);
    if (st && st.status === 'filled') n++;
    else await env.DB.prepare("UPDATE c_orders SET status='pending', fill_ts=NULL WHERE id=?1 AND status='filling'").bind(o.id).run();   // cash/shares moved meanwhile: retry
  }
  return n;
}

/* ---------- dividends and splits (contest-data/corp.json: [{t, type:'div'|'split', d:'YYYY-MM-DD', v}]) ---------- */
// dividends + splits straight from Nasdaq (GitHub runners get 403/429 from Nasdaq and Yahoo): 8 held tickers per cron run,
// each ticker re-checked every 20 h; the split calendar once a day
async function cCorpFetch(env) {
  const now = cnow(), since = cday(now - 21 * 86400);
  const mdy = (s) => { const m = String(s || '').match(/^(\d{2})\/(\d{2})\/(\d{4})$/); return m ? `${m[3]}-${m[1]}-${m[2]}` : null; };
  const H = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/' };
  const ins = (t, type, d, v) => env.DB.prepare('INSERT OR IGNORE INTO c_corp (t, type, d, v) VALUES (?1, ?2, ?3, ?4)').bind(t, type, d, v);
  let etf = {};
  try { etf = (await cUniverse()).etf || {}; } catch (e) {}
  const due = await cq(env, `SELECT p.t FROM (SELECT DISTINCT t FROM c_pos WHERE qty>0) p LEFT JOIN c_corpchk c ON c.t=p.t
                             WHERE c.ts IS NULL OR c.ts<?1 ORDER BY COALESCE(c.ts, 0) LIMIT 8`, now - 20 * 3600);
  for (const { t } of due) {
    try {
      const r = await fetch(`https://api.nasdaq.com/api/quote/${encodeURIComponent(t.replace('-', '.'))}/dividends?assetclass=${etf[t] ? 'etf' : 'stocks'}`, { headers: H });
      if (!r.ok) continue;
      const rows = ((((await r.json()) || {}).data || {}).dividends || {}).rows || [];
      const st = [];
      for (const x of rows) {
        const d = mdy(x.exOrEffDate), v = parseFloat(String(x.amount || '').replace(/[$,]/g, ''));
        if (d && d >= since && v > 0 && !/stock/i.test(String(x.type || ''))) st.push(ins(t, 'div', d, v));
      }
      st.push(env.DB.prepare('INSERT INTO c_corpchk (t, ts) VALUES (?1, ?2) ON CONFLICT(t) DO UPDATE SET ts=?2').bind(t, now));
      await env.DB.batch(st);
    } catch (e) { /* try again next run */ }
  }
  const sc = await c1(env, "SELECT ts FROM c_corpchk WHERE t='*SPLITS*'");
  if (!sc || sc.ts < now - 20 * 3600) {
    try {
      const r = await fetch('https://api.nasdaq.com/api/calendar/splits', { headers: H });
      if (r.ok) {
        const held = new Set((await cq(env, 'SELECT DISTINCT t FROM c_pos WHERE qty>0')).map(x => x.t));
        const st = [];
        for (const x of ((((await r.json()) || {}).data || {}).rows || [])) {
          const t = String(x.symbol || '').toUpperCase().replace('.', '-'), d = mdy(x.executionDate);
          const m = String(x.ratio || '').match(/([\d.]+)\s*:\s*([\d.]+)/);
          if (held.has(t) && d && d >= since && m && +m[1] > 0 && +m[2] > 0 && +m[1] !== +m[2]) st.push(ins(t, 'split', d, +m[1] / +m[2]));
        }
        st.push(env.DB.prepare("INSERT INTO c_corpchk (t, ts) VALUES ('*SPLITS*', ?1) ON CONFLICT(t) DO UPDATE SET ts=?1").bind(now));
        await env.DB.batch(st);
      }
    } catch (e) { /* next run */ }
  }
}
async function cCorpApply(env) {
  const seen = new Set(), events = [];
  for (const ev of ((await cCorp()).events || []).concat(await cq(env, 'SELECT t, type, d, v FROM c_corp WHERE d>=?1', cday(cnow() - 30 * 86400)))) {
    const k = ev && ev.t + ':' + ev.type + ':' + ev.d;
    if (ev && !seen.has(k)) { seen.add(k); events.push(ev); }
  }
  let n = 0;
  for (const ev of events || []) {
    if (!ev || !ev.t || !ev.d || !(ev.v > 0)) continue;
    const exTs = Date.parse(ev.d + 'T13:30:00Z') / 1000;           // market open on the ex-date
    if (exTs > cnow()) continue;
    const holders = await cq(env, 'SELECT pid, qty FROM c_pos WHERE t=?1 AND qty>0', ev.t);
    for (const h of holders) {
      // shares held before the ex-date = now minus what was bought since, plus what was sold since
      const since = await c1(env, `SELECT COALESCE(SUM(CASE WHEN side='buy' THEN fill_qty ELSE -fill_qty END),0) net FROM c_orders
                                   WHERE pid=?1 AND t=?2 AND status='filled' AND fill_ts>=?3`, h.pid, ev.t, exTs);
      const before = h.qty - (since ? since.net : 0);
      if (!(before > 1e-7)) continue;
      const ref = ev.type + ':' + ev.t + ':' + ev.d;
      if (ev.type === 'div') {
        const amt = Math.round(before * ev.v * 100) / 100;
        if (amt <= 0) continue;
        // credit + record in one transaction; the credit only happens while the record does not exist yet
        await env.DB.batch([
          env.DB.prepare('UPDATE c_profiles SET cash=cash+?2 WHERE id=?1 AND NOT EXISTS (SELECT 1 FROM c_cash WHERE pid=?1 AND ref=?3)').bind(h.pid, amt, ref),
          env.DB.prepare("INSERT OR IGNORE INTO c_cash (pid, ts, kind, t, amount, note, ref) VALUES (?1, ?2, 'div', ?3, ?4, ?5, ?6)")
            .bind(h.pid, cnow(), ev.t, amt, ev.v + ' per share × ' + before.toFixed(4), ref)]);
        n++;
      } else if (ev.type === 'split') {
        // only shares held before the ex-date are split; shares bought after it were already bought at the new price
        await env.DB.batch([
          env.DB.prepare('UPDATE c_pos SET qty=qty+?3 WHERE pid=?1 AND t=?2 AND NOT EXISTS (SELECT 1 FROM c_cash WHERE pid=?1 AND ref=?4)').bind(h.pid, ev.t, before * (ev.v - 1), ref),
          env.DB.prepare("UPDATE c_orders SET qty=qty*?3 WHERE pid=?1 AND t=?2 AND side='sell' AND status='pending' AND ts<?4 AND NOT EXISTS (SELECT 1 FROM c_cash WHERE pid=?1 AND ref=?5)").bind(h.pid, ev.t, ev.v, exTs, ref),
          env.DB.prepare("INSERT OR IGNORE INTO c_cash (pid, ts, kind, t, amount, note, ref) VALUES (?1, ?2, 'split', ?3, 0, ?4, ?5)")
            .bind(h.pid, cnow(), ev.t, 'split ' + ev.v, ref)]);
        n++;
      }
    }
  }
  // a processed split releases its hold; the next refresh starts a fresh price series
  for (const ev of events || []) if (ev && ev.type === 'split' && Date.parse(ev.d + 'T13:30:00Z') / 1000 <= cnow())
    await env.DB.batch([env.DB.prepare('DELETE FROM c_quotes WHERE t=?1 AND t IN (SELECT t FROM c_hold)').bind(ev.t), env.DB.prepare('DELETE FROM c_hold WHERE t=?1').bind(ev.t)]);
  return n;
}

/* ---------- snapshots + returns ---------- */
async function cSnapshot(env) {
  const Q = await cQuotes();
  const profs = await cq(env, "SELECT * FROM c_profiles WHERE status!='removed'");
  const d = cday(cnow()), stmts = [];
  for (const p of profs) {
    const pos = await cPositions(env, p.id);
    stmts.push(env.DB.prepare('INSERT INTO c_snap (pid, d, v, n) VALUES (?1, ?2, ?3, ?4) ON CONFLICT(pid, d) DO UPDATE SET v=?3, n=?4').bind(p.id, d, Math.round(cValue(p, pos, Q) * 100) / 100, pos.length));
  }
  if (Q.SPY) stmts.push(env.DB.prepare('INSERT INTO c_snap (pid, d, v) VALUES (0, ?1, ?2) ON CONFLICT(pid, d) DO UPDATE SET v=?2').bind(d, Q.SPY[0]));
  for (let i = 0; i < stmts.length; i += 50) await env.DB.batch(stmts.slice(i, i + 50));
  return stmts.length;
}
function cPeriodStart(kind, now) {
  const d = new Date(now * 1000), y = d.getUTCFullYear(), m = d.getUTCMonth();
  if (kind === 'ytd') return `${y}-01-01`;
  if (kind === 'q') return `${y}-${String(Math.floor(m / 3) * 3 + 1).padStart(2, '0')}-01`;
  if (kind === 'm') return `${y}-${String(m + 1).padStart(2, '0')}-01`;
  if (kind === 'y1') return cday(now - 365 * 86400);
  return null;
}

async function cBoard(env) {
  const Q = await cQuotes();
  const profs = await cq(env, "SELECT id, name, strategy, created, cash, last_trade, house, spy0 FROM c_profiles WHERE status='active'");
  const posAll = await cq(env, 'SELECT pid, t, qty, cost FROM c_pos WHERE qty>0.0000001');
  const trades = await cq(env, "SELECT pid, COUNT(*) n FROM c_orders WHERE status='filled' GROUP BY pid");
  const tn = Object.fromEntries(trades.map(r => [r.pid, r.n]));
  const wins = await cq(env, 'SELECT w.period, w.kind, w.pid, w.ret, p.name FROM c_wins w JOIN c_profiles p ON p.id=w.pid ORDER BY w.period DESC');
  const now = cnow(), starts = {};
  for (const k of ['ytd', 'q', 'm', 'y1']) starts[k] = cPeriodStart(k, now);
  // value at the start of each period = last snapshot before that day (or $10,000 if the profile is younger)
  const base = {};
  for (const k of Object.keys(starts)) {
    const rows = await cq(env, `SELECT s.pid, s.v FROM c_snap s JOIN (SELECT pid, MAX(d) d FROM c_snap WHERE d<?1 GROUP BY pid) x ON x.pid=s.pid AND x.d=s.d`, starts[k]);
    base[k] = Object.fromEntries(rows.map(r => [r.pid, r.v]));
  }
  const out = profs.map(p => {
    const pos = posAll.filter(x => x.pid === p.id);
    const v = cValue(p, pos, Q), days = Math.max(1, (now - p.created) / 86400);
    const r = { id: p.id, house: !!p.house, name: p.name, strategy: p.strategy, created: cday(p.created), value: Math.round(v * 100) / 100,
      n_pos: pos.length, n_trades: tn[p.id] || 0, total: v / C_START - 1,
      cagr: days >= 365 ? Math.pow(v / C_START, 365 / days) - 1 : null, last_trade: p.last_trade ? cday(p.last_trade) : null };
    for (const k of Object.keys(starts)) { const b = base[k][p.id] || C_START; r[k] = v / b - 1; }
    r.stars = wins.filter(w => w.pid === p.id && w.kind === 'q').length;
    r.crowns = wins.filter(w => w.pid === p.id && w.kind === 'y').length;
    if (p.spy0 && Q.SPY) r.vs_spy = (v / C_START) / (Q.SPY[0] / p.spy0) - 1;
    r.eligible = pos.length >= C_MIN_STOCKS;
    // prize eligibility: the yearly prize only for profiles created before 1 Jan of that year,
    // a quarterly prize only for profiles created before that quarter started
    r.prize_y = !p.house && r.eligible && r.created < starts.ytd;
    r.prize_q = !p.house && r.eligible && r.created < starts.q;
    return r;
  });
  return { as_of: new Date().toISOString().slice(0, 16) + 'Z', contest_start: C_CONTEST_START, starts, rows: out,
    winners: wins.map(w => ({ period: w.period, kind: w.kind, id: w.pid, name: w.name, ret: w.ret })) };
}

/* ---------- visibility ---------- */
function cCanSee(me, prof) {
  if (me && (me.admin || me.cid === prof.cid)) return true;
    return !!(me && me.pro && cnow() >= C_DETAIL_FROM);
}
async function cDetail(env, prof, Q) {
  const pos = await cPositions(env, prof.id);
  const orders = await cq(env, "SELECT id, ts, side, t, amount, qty, note, CASE status WHEN 'filling' THEN 'pending' ELSE status END status, fill_ts, price, fill_qty, fill_amt, reason FROM c_orders WHERE pid=?1 ORDER BY ts DESC LIMIT 300", prof.id);
  const cash = await cq(env, "SELECT ts, kind, t, amount, note FROM c_cash WHERE pid=?1 ORDER BY ts DESC LIMIT 200", prof.id);
  return { cash: prof.cash, positions: pos.map(p => ({ t: p.t, qty: p.qty, cost: p.cost, px: Q[p.t] ? Q[p.t][0] : null, chg: Q[p.t] ? Q[p.t][1] : null })), orders, income: cash };
}

/* ---------- router ---------- */
async function contest(req, env, url, h) {
  await cSchema(env);
  const path = url.pathname.slice(2);   // after /c
  const J = (o, s = 200, x = {}) => json(o, s, { ...h, 'Cache-Control': 'no-store', ...x });
  const body = async () => { try { return JSON.parse(await req.text()); } catch { return {}; } };

  if (req.method === 'GET' && path === '/board') {
    const cache = caches.default, ck = new Request(url.origin + '/c/board');
    let data, hit = await cache.match(ck);
    if (hit) data = await hit.json();
    else { data = await cBoard(env); await cache.put(ck, new Response(JSON.stringify(data), { headers: { 'Cache-Control': 'max-age=300' } })); }
    return J(data, 200, { 'Cache-Control': 'public, max-age=60' });
  }
  if (req.method === 'GET' && (path === '/quotes.json' || path === '/market.json')) {
    const kv = await c1(env, 'SELECT v FROM c_kv WHERE k=?1', path === '/quotes.json' ? 'quotes' : 'market');
    if (!kv) return J({ error: 'not ready' }, 503);
    return new Response(kv.v, { headers: { ...h, 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=60' } });
  }
  if (req.method === 'GET' && path === '/tickers') {
    return J({ t: (await cq(env, 'SELECT DISTINCT t FROM c_pos WHERE qty>0')).map(r => r.t) });
  }
  if (req.method === 'GET' && path === '/q') {
    const M = globalThis.C_LQ || (globalThis.C_LQ = new Map()), now = Date.now(), out = {}, need = [];
    const T = [...new Set(String(url.searchParams.get('t') || '').toUpperCase().split(',').map(s => s.trim()).filter(s => /^[A-Z][A-Z0-9.\-]{0,8}$/.test(s)))].slice(0, 20);
    for (const t of T) { const c = M.get(t); if (c && now - c[0] < 15000) { if (c[1]) out[t] = c[1]; } else need.push(t); }
    const B = globalThis.C_LQB || (globalThis.C_LQB = { m: 0, n: 0 }), mi = Math.floor(now / 60000);
    if (B.m !== mi) { B.m = mi; B.n = 0; }
    if (need.length && B.n >= 60) need.length = 0;                        // Nasdaq budget per minute: never let the page starve the contest
    if (need.length) { B.n += Math.ceil(need.length / 20); const L = await cLive(need); if (M.size > 5000) M.clear(); for (const t of need) { M.set(t, [now, L[t] || null]); if (L[t]) out[t] = L[t]; } }
    return J({ q: out, at: new Date(now).toISOString() }, 200, { 'Cache-Control': 'public, max-age=10' });
  }
  const me = await cAuth(req, env);
  if (req.method === 'GET' && path === '/me') {
    if (!me) return J({ error: 'login' }, 401);
    const profs = await cq(env, "SELECT * FROM c_profiles WHERE (cid=?1 OR (house=1 AND ?2=1)) AND status!='removed' ORDER BY house, created", me.cid, me.admin ? 1 : 0);
    for (const p of profs) await cFill(env, p.id);
    const Q = await cQuotes();
    const out = [];
    for (const p0 of profs) {
      const p = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1', p0.id);
      const d = await cDetail(env, p, Q);
      out.push({ id: p.id, house: !!p.house, spy0: p.spy0 || null, wins: await cq(env, 'SELECT period, kind, ret FROM c_wins WHERE pid=?1 ORDER BY period', p.id), name: p.name, strategy: p.strategy, created: cday(p.created), status: p.status, value: cValue(p, d.positions.map(x => ({ t: x.t, qty: x.qty, cost: x.cost })), Q), ...d });
    }
    const last = profs.length ? Math.max(...profs.map(p => p.created)) : 0;
    return J({ me: { email: me.email, pro: me.pro, admin: me.admin }, profiles: out, next_new: last ? cday(last + C_NEW_EVERY) : null, can_new: !last || cnow() - last >= C_NEW_EVERY });
  }
  if (req.method === 'POST' && path === '/profile') {
    if (!me) return J({ error: 'login' }, 401);
    const b = await body();
    if (!b.accept) return J({ error: 'قوانین رو باید قبول کنی' }, 400);
    const name = cclean(b.name, 40), strategy = cclean(b.strategy, 200);
    if (name.length < 2) return J({ error: 'اسم پروفایل حداقل ۲ حرف' }, 400);
    const house = me.admin && b.house ? 1 : 0;
    if (house) { const n = await c1(env, "SELECT COUNT(*) n FROM c_profiles WHERE house=1 AND status!='removed'"); if (n && n.n >= 20) return J({ error: 'حداکثر ۲۰ حساب رسمی' }, 400); }
    const last = house ? null : await c1(env, 'SELECT MAX(created) c FROM c_profiles WHERE cid=?1 AND house=0', me.cid);
    if (last && last.c && cnow() - last.c < C_NEW_EVERY && !me.admin) return J({ error: 'هر ۶ ماه فقط یک پروفایل جدید', next: cday(last.c + C_NEW_EVERY) }, 400);
    const dup = await c1(env, "SELECT id FROM c_profiles WHERE lower(name)=lower(?1) AND status!='removed'", name);
    if (dup) return J({ error: 'این اسم قبلاً گرفته شده' }, 400);
    const r = await env.DB.prepare('INSERT INTO c_profiles (cid, email, name, strategy, created, cash, house) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)').bind(house ? 'house' : me.cid, me.email, name, strategy, cnow(), C_START, house).run();
    await env.DB.prepare('INSERT OR IGNORE INTO c_snap (pid, d, v) VALUES (?1, ?2, ?3)').bind(r.meta.last_row_id, cday(cnow() - 86400), C_START).run();
      return J({ ok: true, id: r.meta.last_row_id });
  }
  if (req.method === 'POST' && path === '/order') {
    if (!me) return J({ error: 'login' }, 401);
    const [s, o] = await cPlace(env, me, await body());
    return J(o, s);
  }
  if (req.method === 'POST' && path === '/cancel') {
    if (!me) return J({ error: 'login' }, 401);
    const b = await body();
    const r = await env.DB.prepare(`UPDATE c_orders SET status='cancelled' WHERE id=?1 AND status='pending'
                                    AND pid IN (SELECT id FROM c_profiles WHERE id=?2 AND (cid=?3 OR (house=1 AND ?4=1)))`).bind(parseInt(b.oid, 10), parseInt(b.pid, 10), me.cid, me.admin ? 1 : 0).run();
    return J({ ok: !!r.meta.changes });
  }
  if (req.method === 'POST' && path === '/admin') {
    if (!me || !me.admin) return J({ error: 'forbidden' }, 403);
    const b = await body();
    if (b.reset_spy0) {
      const Q = await cQuotes();
      if (!Q.SPY) return J({ error: 'no SPY' }, 500);
      const r1 = await env.DB.prepare('UPDATE c_profiles SET spy0=?1 WHERE last_trade IS NOT NULL').bind(Q.SPY[0]).run();
      await env.DB.prepare('UPDATE c_profiles SET spy0=NULL WHERE last_trade IS NULL').run();
      await caches.default.delete(new Request(url.origin + '/c/board'));
      return J({ ok: true, spy: Q.SPY[0], n: r1.meta.changes });
    }
    if (b.reprice) {
      // one-off: orders placed before a session's open but filled late (stale price file) -> refill at that session's open price
      const R = b.reprice, px = R.px || {};
      const rows = await cq(env, "SELECT * FROM c_orders WHERE status='filled' AND side='buy' AND fill_ts>=?1 AND ts<?2", R.day_start, R.open_ts);
      let n = 0;
      for (const o of rows) {
        const p = Number(px[o.t]);
        if (!(p > 0)) continue;
        const nq = o.fill_amt / p;
        await env.DB.batch([env.DB.prepare('UPDATE c_pos SET qty=qty+?3 WHERE pid=?1 AND t=?2').bind(o.pid, o.t, nq - o.fill_qty),
          env.DB.prepare('UPDATE c_orders SET price=?2, fill_qty=?3, fill_ts=?4 WHERE id=?1').bind(o.id, p, nq, R.open_ts)]);
        n++;
      }
      if (R.spy > 0) await env.DB.prepare("UPDATE c_profiles SET spy0=?1 WHERE id IN (SELECT DISTINCT pid FROM c_orders WHERE status='filled' AND fill_ts=?2)").bind(R.spy, R.open_ts).run();
      await caches.default.delete(new Request(url.origin + '/c/board'));
      return J({ ok: true, n });
    }
    if (b.unhold) {
      await env.DB.batch([env.DB.prepare('DELETE FROM c_hold WHERE t=?1').bind(String(b.unhold)), env.DB.prepare('DELETE FROM c_quotes WHERE t=?1').bind(String(b.unhold))]);
      return J({ ok: true });
    }
    if (b.holds) return J({ holds: await cq(env, 'SELECT * FROM c_hold') });
    if (b.market) return J({ n: await cMarketRefresh(env, true) });
    if (b.set_spy0) { for (const [pid, v] of b.set_spy0) await env.DB.prepare('UPDATE c_profiles SET spy0=?2 WHERE id=?1').bind(parseInt(pid, 10), Number(v)).run(); await caches.default.delete(new Request(url.origin + '/c/board')); return J({ ok: true }); }
    if (b.set_fill_ts) { for (const [id, v] of b.set_fill_ts) await env.DB.prepare("UPDATE c_orders SET fill_ts=?2 WHERE id=?1 AND status='filled'").bind(parseInt(id, 10), parseInt(v, 10)).run(); return J({ ok: true }); }
    if (b.snap) { const r = await env.DB.prepare('UPDATE c_snap SET v=?3 WHERE pid=?1 AND d=?2').bind(parseInt(b.snap[0], 10), String(b.snap[1]), Number(b.snap[2])).run(); return J({ ok: true, n: r.meta.changes }); }
    if (b.fix) {
      // one-off correction of a portfolio: {pid, cash, pos:[[t, dqty, dcost]], order:[id, fill_qty, fill_amt]}
      const F = b.fix, pid = parseInt(F.pid, 10), st = [];
      if (F.cash) st.push(env.DB.prepare('UPDATE c_profiles SET cash=cash+?2 WHERE id=?1').bind(pid, Number(F.cash)));
      for (const [t, dq, dc] of F.pos || []) st.push(env.DB.prepare('UPDATE c_pos SET qty=qty+?3, cost=cost+?4 WHERE pid=?1 AND t=?2').bind(pid, t, Number(dq), Number(dc)));
      if (F.order) st.push(env.DB.prepare('UPDATE c_orders SET fill_qty=?3, fill_amt=?4 WHERE id=?1 AND pid=?2').bind(F.order[0], pid, Number(F.order[1]), Number(F.order[2])));
      if (st.length) await env.DB.batch(st);
      await caches.default.delete(new Request(url.origin + '/c/board'));
      return J({ ok: true, n: st.length });
    }
    if (b.win_period) {
      if (b.clear) await env.DB.prepare('DELETE FROM c_wins WHERE period=?1').bind(String(b.win_period)).run();
      else await env.DB.prepare('INSERT INTO c_wins (period, kind, pid, ret, decided) VALUES (?1, ?2, ?3, NULL, ?4) ON CONFLICT(period) DO UPDATE SET pid=?3, decided=?4')
        .bind(String(b.win_period), /Q/.test(b.win_period) ? 'q' : 'y', parseInt(b.pid, 10), cnow()).run();
      await caches.default.delete(new Request(url.origin + '/c/board'));
      return J({ ok: true });
    }
    if (!['active', 'hidden', 'removed'].includes(b.status)) return J({ error: 'bad status' }, 400);
    await env.DB.prepare('UPDATE c_profiles SET status=?2 WHERE id=?1').bind(parseInt(b.pid, 10), b.status).run();
    await caches.default.delete(new Request(url.origin + '/c/board'));
    return J({ ok: true });
  }
  const m = path.match(/^\/(p|hist)\/(\d+)$/);
  if (req.method === 'GET' && m) {
    const prof = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1', parseInt(m[2], 10));
    if (!prof || (prof.status !== 'active' && !(me && (me.admin || me.cid === prof.cid)))) return J({ error: 'not found' }, 404);
    const see = cCanSee(me, prof);
    if (m[1] === 'hist') {
      if (!see) return J({ locked: true });
      const v = (await cq(env, 'SELECT d, v FROM c_snap WHERE pid=?1 ORDER BY d', prof.id)).map(r => [r.d, r.v]);
      const spy = v.length ? (await cq(env, 'SELECT d, v FROM c_snap WHERE pid=0 AND d>=?1 ORDER BY d', v[0][0])).map(r => [r.d, r.v]) : [];
      return J({ v, spy, spy0: prof.spy0 || null });
    }
    const Q = await cQuotes();
    const pos = await cPositions(env, prof.id);
    const n = await c1(env, "SELECT COUNT(*) n FROM c_orders WHERE pid=?1 AND status='filled'", prof.id);
    const out = { id: prof.id, house: !!prof.house, name: prof.name, strategy: prof.strategy, created: cday(prof.created), value: cValue(prof, pos, Q),
      n_pos: pos.length, n_trades: n ? n.n : 0, spy0: prof.spy0 || null,
      wins: (await cq(env, 'SELECT period, kind, ret FROM c_wins WHERE pid=?1 ORDER BY period', prof.id)), mine: !!(me && me.cid === prof.cid), locked: !see,
      unlock: cnow() >= C_DETAIL_FROM ? 'pro' : 'feb' };
    if (see) Object.assign(out, await cDetail(env, prof, Q));
    return J(out);
  }
  return J({ error: 'not found' }, 404);
}

/* ---------- winners: each finished quarter / year gets one winner (best eligible participant, never a site portfolio) ---------- */
function cPeriods(now) {
  const out = [], start = new Date(C_CONTEST_START + 'T00:00:00Z'), today = cday(now);
  for (let y = start.getUTCFullYear(); y <= new Date(now * 1000).getUTCFullYear(); y++) {
    for (let q = 0; q < 4; q++) {
      const a = `${y}-${String(q * 3 + 1).padStart(2, '0')}-01`, b = q === 3 ? `${y + 1}-01-01` : `${y}-${String(q * 3 + 4).padStart(2, '0')}-01`;
      if (a >= C_CONTEST_START && b <= today) out.push({ period: `${y}-Q${q + 1}`, kind: 'q', a, b });
    }
    if (`${y + 1}-01-01` <= today && `${y}-01-01` >= C_CONTEST_START) out.push({ period: `${y}`, kind: 'y', a: `${y}-01-01`, b: `${y + 1}-01-01` });
  }
  return out;
}
async function cWinners(env) {
  const done = new Set((await cq(env, 'SELECT period FROM c_wins')).map(r => r.period));
  let n = 0;
  for (const P of cPeriods(cnow())) {
    if (done.has(P.period)) continue;
    const startTs = Date.parse(P.a + 'T00:00:00Z') / 1000, endTs = Date.parse(P.b + 'T00:00:00Z') / 1000;
    const rows = await cq(env, `SELECT p.id, p.cid,
        (SELECT v FROM c_snap s WHERE s.pid=p.id AND s.d<?1 ORDER BY d DESC LIMIT 1) v0,
        (SELECT v FROM c_snap s WHERE s.pid=p.id AND s.d<?2 ORDER BY d DESC LIMIT 1) v1,
        (SELECT n FROM c_snap s WHERE s.pid=p.id AND s.d<?2 ORDER BY d DESC LIMIT 1) n1,
        (SELECT COUNT(*) FROM c_orders o WHERE o.pid=p.id AND o.status='filled' AND o.fill_ts>=?3 AND o.fill_ts<?4) tr
      FROM c_profiles p WHERE p.house=0 AND p.status='active' AND p.created<?3`, P.a, P.b, startTs, endTs);
    const ok = rows.filter(r => r.v0 && r.v1 && (r.n1 == null || r.n1 >= C_MIN_STOCKS) && r.tr > 0)
      .map(r => ({ ...r, ret: r.v1 / r.v0 - 1 })).sort((x, y) => y.ret - x.ret);
    if (!ok.length) continue;
    await env.DB.prepare('INSERT OR IGNORE INTO c_wins (period, kind, pid, ret, decided) VALUES (?1, ?2, ?3, ?4, ?5)').bind(P.period, P.kind, ok[0].id, ok[0].ret, cnow()).run();
    await caches.default.delete(new Request('https://rz-events.mreza-hajilou.workers.dev/c/board'));
    n++;
  }
  return n;
}

// ET clock: session ('Open' | 'Pre Market' | 'After Hours' | 'Closed') and the last regular close as an ISO time with offset
function cET(now) {
  const d = new Date(now * 1000), f = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hourCycle: 'h23', weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', timeZoneName: 'shortOffset' });
  const p = Object.fromEntries(f.formatToParts(d).map(x => [x.type, x.value]));
  const min = +p.hour * 60 + +p.minute, wk = !/Sat|Sun/.test(p.weekday), om = String(p.timeZoneName || 'GMT-5').match(/([+-])(\d+)/);
  const off = om ? `${om[1]}${String(om[2]).padStart(2, '0')}:00` : '-05:00';
  const session = !wk ? 'Closed' : min < 240 ? 'Closed' : min < 570 ? 'Pre Market' : min < 960 ? 'Open' : min < 1200 ? 'After Hours' : 'Closed';
  let back = (wk && min >= 960) ? 0 : 1, day;
  for (; back < 8; back++) { const x = new Date(Date.UTC(+p.year, +p.month - 1, +p.day) - back * 86400000); if (x.getUTCDay() % 6 !== 0) { day = x.toISOString().slice(0, 10); break; } }
  const now_et = `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}:00${off}`;
  return { session, close: `${day}T16:00:00${off}`, now: now_et };
}
// whole US market in one Nasdaq request (screener): price, change, market cap, sector... every 5 minutes while the market is open,
// hourly otherwise. Served as /c/quotes.json (same format as the old GitHub quotes file) and /c/market.json
async function cMarketRefresh(env, force) {
  const now = cnow(), E = cET(now);
  const last = await c1(env, "SELECT ts FROM c_kv WHERE k='quotes'");
  if (!force && last && (E.session === 'Closed' ? now - last.ts < 3600 : E.session !== 'Open' ? now - last.ts < 900 : now - last.ts < 240)) return 0;
  const r = await fetch('https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25000&download=true', { headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/' } });
  if (!r.ok) return 0;
  const rows = ((((await r.json()) || {}).data || {}).rows) || [];
  if (rows.length < 3000) return 0;
  const nm = (x) => { const v = parseFloat(String(x == null ? '' : x).replace(/[$,%+]/g, '')); return isNaN(v) ? null : v; };
  const ts = E.session === 'Open' ? E.now : E.close, q = {}, m = {};
  for (const x of rows) {
    const t = String(x.symbol || '').trim().replace('/', '-').replace('^', '-P'), p = nm(x.lastsale);
    if (!t || !(p > 0)) continue;
    const nc = nm(x.netchange), pc = nm(x.pctchange);
    q[t] = [p, pc, nc != null ? Math.round((p - nc) * 10000) / 10000 : null, ts];
    m[t] = [nm(x.marketCap), (x.sector || '').trim() || null, (x.industry || '').trim() || null, (x.country || '').trim() || null, (x.ipoyear || '').trim() || null];
  }
  const asof = new Date(now * 1000).toISOString().slice(0, 19) + 'Z';
  await env.DB.batch([
    env.DB.prepare("INSERT INTO c_kv (k, v, ts) VALUES ('quotes', ?1, ?2) ON CONFLICT(k) DO UPDATE SET v=?1, ts=?2").bind(JSON.stringify({ as_of: asof, status: E.session, n: Object.keys(q).length, src: 'worker', q }), now),
    env.DB.prepare("INSERT INTO c_kv (k, v, ts) VALUES ('market', ?1, ?2) ON CONFLICT(k) DO UPDATE SET v=?1, ts=?2").bind(JSON.stringify({ as_of: asof, cols: ['mcap', 'sector', 'industry', 'country', 'ipo'], m }), now)]);
  return Object.keys(q).length;
}
// GitHub runs on its own schedule only a few times a day: when a token is configured (worker secret GH_TOKEN), the worker starts
// the hourly earnings fast lane and the quotes-file refresh itself
async function cDispatch(env) {
  if (!env.GH_TOKEN) return;
  const mi = new Date().getUTCMinutes(), go = async (wf) => fetch(`https://api.github.com/repos/mrezahajilou-ops/stock-data/actions/workflows/${wf}/dispatches`,
    { method: 'POST', headers: { 'Authorization': 'Bearer ' + env.GH_TOKEN, 'Accept': 'application/vnd.github+json', 'User-Agent': 'rz-events', 'Content-Type': 'application/json' }, body: '{"ref":"main"}' });
  if (mi < 5) await go('fast.yml');
  if (mi % 15 < 5) await go('quotes.yml');
}
async function cRefreshQuotes(env) {
  const T = (await cq(env, "SELECT DISTINCT t FROM c_pos WHERE qty>0 UNION SELECT DISTINCT t FROM c_orders WHERE status IN ('pending','filling')")).map(r => r.t).concat(['SPY']);
  const L = await cLive(T);
  // price discontinuity without a matching daily change = split / reverse split not yet in corp.json:
  // freeze the ticker (no fills, valued at the last price) until the split is applied or an admin releases it
  const old = {};
  for (const r of await cq(env, 'SELECT t, p FROM c_quotes')) old[r.t] = r.p;
  const held = new Set((await cq(env, 'SELECT t FROM c_hold')).map(r => r.t));
  for (const [t, q] of Object.entries(L)) {
    if (held.has(t)) { delete L[t]; continue; }
    const r = old[t] > 0 ? q[0] / old[t] : 1;
    if ((r > 1.8 || r < 0.55) && !(q[1] != null && Math.abs(q[1]) >= 35)) {
      await env.DB.prepare('INSERT OR IGNORE INTO c_hold (t, ts, note) VALUES (?1, ?2, ?3)').bind(t, cnow(), 'jump ' + old[t] + ' -> ' + q[0]).run();
      delete L[t];
    }
  }
  const st = Object.entries(L).map(([t, q]) => env.DB.prepare('INSERT INTO c_quotes (t, p, chg, prev, ts) VALUES (?1, ?2, ?3, ?4, ?5) ON CONFLICT(t) DO UPDATE SET p=?2, chg=?3, prev=?4, ts=?5').bind(t, q[0], q[1], q[2], q[3]));
  for (let i = 0; i < st.length; i += 50) await env.DB.batch(st.slice(i, i + 50));
  return st.length;
}
async function contestCron(env, cron) {
  await cSchema(env);
  try { await cRefreshQuotes(env); } catch (e) { /* keep file quotes */ }
  try { await cCorpFetch(env); } catch (e) { /* next run */ }
  let n;
  if (String(cron).startsWith('45 23 ')) { await cCorpApply(env); await cFill(env); n = await cSnapshot(env); await cWinners(env); }
  else n = await cFill(env);
  // after the contest work: the whole-market refresh is the heaviest step and must never delay fills
  try { await cMarketRefresh(env); } catch (e) { /* next run */ }
  try { await cDispatch(env); } catch (e) { /* next run */ }
  return n;
}
