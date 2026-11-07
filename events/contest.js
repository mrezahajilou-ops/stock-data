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
     strategy TEXT, created INTEGER NOT NULL, cash REAL NOT NULL, status TEXT NOT NULL DEFAULT 'active', last_trade INTEGER)`,
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
];

/* ---------- helpers ---------- */
const cq = async (env, sql, ...a) => (await env.DB.prepare(sql).bind(...a).all()).results || [];
const c1 = async (env, sql, ...a) => (await env.DB.prepare(sql).bind(...a).first()) || null;
const cnow = () => Math.floor(Date.now() / 1000);
const cday = (ts) => new Date(ts * 1000).toISOString().slice(0, 10);
const cclean = (s, n) => String(s || '').replace(/[\u0000-\u001f<>]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
let C_SCHEMA_OK = false;
async function cSchema(env) {
  if (env.RAW_BASE) C_RAW = env.RAW_BASE;
  if (C_SCHEMA_OK) return;
  await env.DB.batch(C_SCHEMA.map(s => env.DB.prepare(s)));
  C_SCHEMA_OK = true;
}

async function cHmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(msg));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, '0')).join('');
}
/** token = "c|e|p|ts|sig", sig = hex HMAC-SHA256 of "c|e|p|ts"; built by the theme (Liquid hmac_sha256). */
async function cAuth(req, env) {
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
const cQuotes = () => cFetchJSON(C_RAW + '/quotes/quotes.json', 60).then(j => j.q || {});
const cUniverse = () => cFetchJSON(C_RAW + '/contest-data/universe.json', 3600);
const cCorp = () => cFetchJSON(C_RAW + '/contest-data/corp.json', 3600).catch(() => ({ events: [] }));
const cQtime = (q) => { const t = q && q[3] ? Date.parse(q[3]) : NaN; return isNaN(t) ? null : Math.floor(t / 1000); };

async function cPositions(env, pid) { return cq(env, 'SELECT t, qty, cost FROM c_pos WHERE pid=?1 AND qty>0.0000001 ORDER BY t', pid); }
function cValue(prof, pos, Q) {
  let v = prof.cash;
  for (const p of pos) { const q = Q[p.t]; v += p.qty * (q ? q[0] : p.cost / p.qty); }
  return v;
}

/* ---------- order validation + fills ---------- */
async function cPlace(env, me, b) {
  const pid = parseInt(b.pid, 10);
  const prof = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1 AND cid=?2', pid, me.cid);
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
  const pos = await cPositions(env, pid);
  const pend = await cq(env, "SELECT side, t, amount, qty FROM c_orders WHERE pid=?1 AND status='pending'", pid);
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
async function cFill(env, onlyPid) {
  const pend = onlyPid ? await cq(env, "SELECT * FROM c_orders WHERE status='pending' AND pid=?1 ORDER BY ts", onlyPid)
                       : await cq(env, "SELECT * FROM c_orders WHERE status='pending' ORDER BY ts LIMIT 500");
  if (!pend.length) return 0;
  const Q = await cQuotes();
  let n = 0;
  for (const o of pend) {
    const q = Q[o.t], qt = cQtime(q);
    if (!q || !qt || qt <= o.ts) {
      if (cnow() - o.ts > 6 * 86400) await env.DB.prepare("UPDATE c_orders SET status='rejected', reason='no price for 6 days' WHERE id=?1").bind(o.id).run();
      continue;
    }
    const price = q[0];
    const prof = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1', o.pid);
    if (!prof) continue;
    const pos = await c1(env, 'SELECT qty, cost FROM c_pos WHERE pid=?1 AND t=?2', o.pid, o.t) || { qty: 0, cost: 0 };
    const stmts = [], ts = cnow();
    if (o.side === 'buy') {
      // re-check cash and the 70% cap at the fill price; shrink the order if the price moved against it
      const all = await cPositions(env, o.pid);
      const total = cValue(prof, all, Q);
      const room = Math.max(0, C_MAX_W * total - pos.qty * price);
      const amt = Math.min(o.amount, prof.cash, room);
      if (amt < 1) { await env.DB.prepare("UPDATE c_orders SET status='rejected', reason=?2 WHERE id=?1").bind(o.id, amt <= 0 && room <= 0 ? '70% cap' : 'cash').run(); continue; }
      const qty = amt / price;
      stmts.push(env.DB.prepare('INSERT INTO c_pos (pid, t, qty, cost) VALUES (?1, ?2, ?3, ?4) ON CONFLICT(pid, t) DO UPDATE SET qty=qty+?3, cost=cost+?4').bind(o.pid, o.t, qty, amt));
      stmts.push(env.DB.prepare('UPDATE c_profiles SET cash=cash-?2, last_trade=?3 WHERE id=?1').bind(o.pid, amt, ts));
      stmts.push(env.DB.prepare("UPDATE c_orders SET status='filled', fill_ts=?2, price=?3, fill_qty=?4, fill_amt=?5 WHERE id=?1").bind(o.id, ts, price, qty, amt));
    } else {
      const qty = Math.min(o.qty, pos.qty);
      if (!(qty > 0)) { await env.DB.prepare("UPDATE c_orders SET status='rejected', reason='no shares' WHERE id=?1").bind(o.id).run(); continue; }
      const amt = qty * price, left = pos.qty - qty, costLeft = left > 1e-7 ? pos.cost * left / pos.qty : 0;
      stmts.push(left > 1e-7 ? env.DB.prepare('UPDATE c_pos SET qty=?3, cost=?4 WHERE pid=?1 AND t=?2').bind(o.pid, o.t, left, costLeft)
                              : env.DB.prepare('DELETE FROM c_pos WHERE pid=?1 AND t=?2').bind(o.pid, o.t));
      stmts.push(env.DB.prepare('UPDATE c_profiles SET cash=cash+?2, last_trade=?3 WHERE id=?1').bind(o.pid, amt, ts));
      stmts.push(env.DB.prepare("UPDATE c_orders SET status='filled', fill_ts=?2, price=?3, fill_qty=?4, fill_amt=?5 WHERE id=?1").bind(o.id, ts, price, qty, amt));
    }
    await env.DB.batch(stmts);
    n++;
  }
  return n;
}

/* ---------- dividends and splits (contest-data/corp.json: [{t, type:'div'|'split', d:'YYYY-MM-DD', v}]) ---------- */
async function cCorpApply(env) {
  const { events } = await cCorp();
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
        const r = await env.DB.prepare("INSERT OR IGNORE INTO c_cash (pid, ts, kind, t, amount, note, ref) VALUES (?1, ?2, 'div', ?3, ?4, ?5, ?6)")
          .bind(h.pid, cnow(), ev.t, amt, ev.v + ' per share × ' + before.toFixed(4), ref).run();
        if (r.meta.changes) { await env.DB.prepare('UPDATE c_profiles SET cash=cash+?2 WHERE id=?1').bind(h.pid, amt).run(); n++; }
      } else if (ev.type === 'split') {
        const r = await env.DB.prepare("INSERT OR IGNORE INTO c_cash (pid, ts, kind, t, amount, note, ref) VALUES (?1, ?2, 'split', ?3, 0, ?4, ?5)")
          .bind(h.pid, cnow(), ev.t, 'split ' + ev.v, ref).run();
        // only shares held before the ex-date are split; shares bought after it were already bought at the new price
        if (r.meta.changes) { await env.DB.prepare('UPDATE c_pos SET qty=?3 WHERE pid=?1 AND t=?2').bind(h.pid, ev.t, h.qty + before * (ev.v - 1)).run(); n++; }
      }
    }
  }
  return n;
}

/* ---------- snapshots + returns ---------- */
async function cSnapshot(env) {
  const Q = await cQuotes();
  const profs = await cq(env, "SELECT * FROM c_profiles WHERE status!='removed'");
  const d = cday(cnow()), stmts = [];
  for (const p of profs) {
    const pos = await cPositions(env, p.id);
    stmts.push(env.DB.prepare('INSERT INTO c_snap (pid, d, v) VALUES (?1, ?2, ?3) ON CONFLICT(pid, d) DO UPDATE SET v=?3').bind(p.id, d, Math.round(cValue(p, pos, Q) * 100) / 100));
  }
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
  const profs = await cq(env, "SELECT id, name, strategy, created, cash, last_trade FROM c_profiles WHERE status='active'");
  const posAll = await cq(env, 'SELECT pid, t, qty, cost FROM c_pos WHERE qty>0.0000001');
  const trades = await cq(env, "SELECT pid, COUNT(*) n FROM c_orders WHERE status='filled' GROUP BY pid");
  const tn = Object.fromEntries(trades.map(r => [r.pid, r.n]));
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
    const r = { id: p.id, name: p.name, strategy: p.strategy, created: cday(p.created), value: Math.round(v * 100) / 100,
      n_pos: pos.length, n_trades: tn[p.id] || 0, total: v / C_START - 1,
      cagr: days >= 365 ? Math.pow(v / C_START, 365 / days) - 1 : null, last_trade: p.last_trade ? cday(p.last_trade) : null };
    for (const k of Object.keys(starts)) { const b = base[k][p.id] || C_START; r[k] = v / b - 1; }
    r.eligible = pos.length >= C_MIN_STOCKS;
    // prize eligibility: the yearly prize only for profiles created before 1 Jan of that year,
    // a quarterly prize only for profiles created before that quarter started
    r.prize_y = r.eligible && r.created < starts.ytd;
    r.prize_q = r.eligible && r.created < starts.q;
    return r;
  });
  return { as_of: new Date().toISOString().slice(0, 16) + 'Z', contest_start: C_CONTEST_START, starts, rows: out };
}

/* ---------- visibility ---------- */
function cCanSee(me, prof) {
  if (me && (me.admin || me.cid === prof.cid)) return true;
  return !!(me && me.pro && cnow() >= C_DETAIL_FROM);
}
async function cDetail(env, prof, Q) {
  const pos = await cPositions(env, prof.id);
  const orders = await cq(env, 'SELECT id, ts, side, t, amount, qty, note, status, fill_ts, price, fill_qty, fill_amt, reason FROM c_orders WHERE pid=?1 ORDER BY ts DESC LIMIT 300', prof.id);
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
  if (req.method === 'GET' && path === '/tickers') {
    return J({ t: (await cq(env, 'SELECT DISTINCT t FROM c_pos WHERE qty>0')).map(r => r.t) });
  }
  const me = await cAuth(req, env);
  if (req.method === 'GET' && path === '/me') {
    if (!me) return J({ error: 'login' }, 401);
    const profs = await cq(env, "SELECT * FROM c_profiles WHERE cid=?1 AND status!='removed' ORDER BY created", me.cid);
    for (const p of profs) await cFill(env, p.id);
    const Q = await cQuotes();
    const out = [];
    for (const p0 of profs) {
      const p = await c1(env, 'SELECT * FROM c_profiles WHERE id=?1', p0.id);
      const d = await cDetail(env, p, Q);
      out.push({ id: p.id, name: p.name, strategy: p.strategy, created: cday(p.created), status: p.status, value: cValue(p, d.positions.map(x => ({ t: x.t, qty: x.qty, cost: x.cost })), Q), ...d });
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
    const last = await c1(env, 'SELECT MAX(created) c FROM c_profiles WHERE cid=?1', me.cid);
    if (last && last.c && cnow() - last.c < C_NEW_EVERY && !me.admin) return J({ error: 'هر ۶ ماه فقط یک پروفایل جدید', next: cday(last.c + C_NEW_EVERY) }, 400);
    const dup = await c1(env, "SELECT id FROM c_profiles WHERE lower(name)=lower(?1) AND status!='removed'", name);
    if (dup) return J({ error: 'این اسم قبلاً گرفته شده' }, 400);
    const r = await env.DB.prepare('INSERT INTO c_profiles (cid, email, name, strategy, created, cash) VALUES (?1, ?2, ?3, ?4, ?5, ?6)').bind(me.cid, me.email, name, strategy, cnow(), C_START).run();
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
                                    AND pid IN (SELECT id FROM c_profiles WHERE id=?2 AND cid=?3)`).bind(parseInt(b.oid, 10), parseInt(b.pid, 10), me.cid).run();
    return J({ ok: !!r.meta.changes });
  }
  if (req.method === 'POST' && path === '/admin') {
    if (!me || !me.admin) return J({ error: 'forbidden' }, 403);
    const b = await body();
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
      return J({ v: (await cq(env, 'SELECT d, v FROM c_snap WHERE pid=?1 ORDER BY d', prof.id)).map(r => [r.d, r.v]) });
    }
    const Q = await cQuotes();
    const pos = await cPositions(env, prof.id);
    const n = await c1(env, "SELECT COUNT(*) n FROM c_orders WHERE pid=?1 AND status='filled'", prof.id);
    const out = { id: prof.id, name: prof.name, strategy: prof.strategy, created: cday(prof.created), value: cValue(prof, pos, Q),
      n_pos: pos.length, n_trades: n ? n.n : 0, mine: !!(me && me.cid === prof.cid), locked: !see,
      unlock: cnow() < C_DETAIL_FROM ? 'feb' : 'pro' };
    if (see) Object.assign(out, await cDetail(env, prof, Q));
    return J(out);
  }
  return J({ error: 'not found' }, 404);
}

async function contestCron(env, cron) {
  await cSchema(env);
  if (cron === '45 23 * * 1-5') { await cCorpApply(env); await cFill(env); return cSnapshot(env); }
  return cFill(env);
}
