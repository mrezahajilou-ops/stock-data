/**
 * rz-events — anonymous usage events for rezahajiloubooks.com (Cloudflare Worker + D1).
 *
 * The site stores watchlists only in the visitor's browser, and the stock tool uses #TICKER links that no server ever
 * sees, so until now nobody could tell which stocks people actually look at. This worker receives five tiny events and
 * serves the aggregates the "نبض جامعه" page and the stock pages show.
 *
 *   POST /e           {k, t, v, u}   k: view | search | watch_add | watch_remove | vote | compare
 *                                     t: ticker (A-Z . -), v: free short value (e.g. "pw" for paywalled view, "bull"/"bear"),
 *                                     u: random anonymous id the browser made (no cookie, no IP, no name)
 *   GET  /stats?days=7                aggregates for the pulse page (cached 10 min)
 *   GET  /t/TSM?u=...                 one stock: weekly views, rank, votes, and this visitor's own vote
 *
 * Privacy: no IP address or user agent is stored; events older than RETAIN_DAYS are deleted by the daily cron;
 * the pulse page only shows stocks seen by at least MIN_UNIQ different visitors.
 */
const KINDS = new Set(['view', 'search', 'watch_add', 'watch_remove', 'vote', 'compare']);
const T_RE = /^[A-Z][A-Z0-9.\-]{0,8}$/;
const U_RE = /^[a-z0-9]{8,32}$/;
const RETAIN_DAYS = 400;
const MIN_UNIQ = 3;

function cors(req, env) {
  const o = req.headers.get('Origin') || '';
  const allowed = (env.ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  const ok = allowed.length === 0 || allowed.includes(o) || /^http:\/\/localhost(:\d+)?$/.test(o);
  return {
    'Access-Control-Allow-Origin': ok ? (o || '*') : 'null',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}
const json = (obj, status = 200, extra = {}) =>
  new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...extra } });

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const h = cors(req, env);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });

    if (req.method === 'POST' && url.pathname === '/e') {
      let b;
      try { b = JSON.parse(await req.text()); } catch { return json({ error: 'bad json' }, 400, h); }
      const k = String(b.k || ''), t = String(b.t || '').toUpperCase(), u = String(b.u || ''), v = String(b.v || '').slice(0, 24);
      if (!KINDS.has(k) || !T_RE.test(t) || !U_RE.test(u)) return json({ error: 'bad event' }, 400, h);
      const ts = Math.floor(Date.now() / 1000);
      ctx.waitUntil(env.DB.prepare('INSERT INTO events (ts, k, t, u, v) VALUES (?1, ?2, ?3, ?4, ?5)').bind(ts, k, t, u, v).run());
      return new Response(null, { status: 204, headers: h });
    }

    if (req.method === 'GET' && url.pathname === '/stats') {
      const days = Math.min(90, Math.max(1, parseInt(url.searchParams.get('days') || '7', 10) || 7));
      const cache = caches.default;
      const ck = new Request(url.origin + '/stats?days=' + days);
      const hit = await cache.match(ck);
      if (hit) { const r = new Response(hit.body, hit); Object.entries(h).forEach(([a, b]) => r.headers.set(a, b)); return r; }
      const out = await stats(env, days);
      const r = json(out, 200, { ...h, 'Cache-Control': 'public, max-age=600' });
      ctx.waitUntil(cache.put(ck, r.clone()));
      return r;
    }

    const m = url.pathname.match(/^\/t\/([A-Za-z0-9.\-]{1,9})$/);
    if (req.method === 'GET' && m) {
      const t = m[1].toUpperCase(), u = url.searchParams.get('u') || '';
      return json(await one(env, t, U_RE.test(u) ? u : null), 200, { ...h, 'Cache-Control': 'no-store' });
    }
    return json({ ok: true, service: 'rz-events' }, 200, h);
  },

  async scheduled(ev, env) {
    const cut = Math.floor(Date.now() / 1000) - RETAIN_DAYS * 86400;
    await env.DB.prepare('DELETE FROM events WHERE ts < ?1').bind(cut).run();
  },
};

async function stats(env, days) {
  const now = Math.floor(Date.now() / 1000), a = now - days * 86400, p = a - days * 86400;
  const q = async (sql, ...args) => (await env.DB.prepare(sql).bind(...args).all()).results || [];
  // views: unique visitors per ticker, this period and the one before (for the "change" arrow)
  const cur = await q(`SELECT t, COUNT(*) views, COUNT(DISTINCT u) uniq, SUM(CASE WHEN v='pw' THEN 1 ELSE 0 END) pw
                       FROM events WHERE k='view' AND ts>=?1 GROUP BY t HAVING uniq>=?2 ORDER BY uniq DESC, views DESC LIMIT 60`, a, MIN_UNIQ);
  const prev = await q(`SELECT t, COUNT(DISTINCT u) uniq FROM events WHERE k='view' AND ts>=?1 AND ts<?2 GROUP BY t`, p, a);
  const pm = Object.fromEntries(prev.map(r => [r.t, r.uniq]));
  const watch = await q(`SELECT t, SUM(CASE WHEN k='watch_add' THEN 1 ELSE 0 END) adds, SUM(CASE WHEN k='watch_remove' THEN 1 ELSE 0 END) removes
                         FROM events WHERE k IN ('watch_add','watch_remove') AND ts>=?1 GROUP BY t`, a);
  const wm = Object.fromEntries(watch.map(r => [r.t, r]));
  // votes: the latest vote of each visitor per stock within 90 days
  const votes = await q(`SELECT t, SUM(CASE WHEN v='bull' THEN 1 ELSE 0 END) bull, SUM(CASE WHEN v='bear' THEN 1 ELSE 0 END) bear FROM (
                           SELECT t, u, v FROM events e WHERE k='vote' AND ts>=?1 AND ts=(SELECT MAX(ts) FROM events x WHERE x.k='vote' AND x.t=e.t AND x.u=e.u)
                         ) GROUP BY t`, now - 90 * 86400);
  const vm = Object.fromEntries(votes.map(r => [r.t, r]));
  const searches = await q(`SELECT t, COUNT(DISTINCT u) n FROM events WHERE k='search' AND ts>=?1 GROUP BY t HAVING n>=?2 ORDER BY n DESC LIMIT 25`, a, MIN_UNIQ);
  const compares = await q(`SELECT v pair, COUNT(DISTINCT u) n FROM events WHERE k='compare' AND ts>=?1 GROUP BY v HAVING n>=?2 ORDER BY n DESC LIMIT 15`, a, MIN_UNIQ);
  const flows = await q(`SELECT t, SUM(CASE WHEN k='watch_add' THEN 1 ELSE -1 END) net, COUNT(DISTINCT u) n FROM events
                         WHERE k IN ('watch_add','watch_remove') AND ts>=?1 GROUP BY t HAVING n>=?2 ORDER BY net DESC LIMIT 40`, a, MIN_UNIQ);
  const tot = (await q(`SELECT COUNT(*) events, COUNT(DISTINCT u) uniq, COUNT(DISTINCT t) tickers FROM events WHERE ts>=?1`, a))[0] || {};
  return {
    as_of: new Date().toISOString().slice(0, 16) + 'Z', days, min_uniq: MIN_UNIQ, totals: tot,
    top: cur.map((r, i) => ({ rank: i + 1, t: r.t, views: r.views, uniq: r.uniq, prev_uniq: pm[r.t] || 0, pw: r.pw,
      watch_add: (wm[r.t] || {}).adds || 0, watch_remove: (wm[r.t] || {}).removes || 0,
      bull: (vm[r.t] || {}).bull || 0, bear: (vm[r.t] || {}).bear || 0 })),
    searches: searches.map(r => ({ t: r.t, n: r.n })),
    compares: compares.map(r => ({ pair: r.pair, n: r.n })),
    watch_in: flows.filter(r => r.net > 0).slice(0, 15), watch_out: flows.filter(r => r.net < 0).slice(-15).reverse(),
  };
}

async function one(env, t, u) {
  const now = Math.floor(Date.now() / 1000), a = now - 7 * 86400;
  const q = async (sql, ...args) => (await env.DB.prepare(sql).bind(...args).all()).results || [];
  const v = (await q(`SELECT COUNT(*) views, COUNT(DISTINCT u) uniq FROM events WHERE k='view' AND t=?1 AND ts>=?2`, t, a))[0] || {};
  const rank = (await q(`SELECT COUNT(*)+1 r FROM (SELECT t, COUNT(DISTINCT u) n FROM events WHERE k='view' AND ts>=?1 GROUP BY t HAVING n>?2)`, a, v.uniq || 0))[0] || {};
  const votes = (await q(`SELECT SUM(CASE WHEN v='bull' THEN 1 ELSE 0 END) bull, SUM(CASE WHEN v='bear' THEN 1 ELSE 0 END) bear FROM (
                            SELECT u, v FROM events e WHERE k='vote' AND t=?1 AND ts>=?2 AND ts=(SELECT MAX(ts) FROM events x WHERE x.k='vote' AND x.t=e.t AND x.u=e.u))`, t, now - 90 * 86400))[0] || {};
  let mine = null;
  if (u) { const r = await q(`SELECT v FROM events WHERE k='vote' AND t=?1 AND u=?2 ORDER BY ts DESC LIMIT 1`, t, u); mine = r.length ? r[0].v : null; }
  const watchers = (await q(`SELECT COUNT(*) n FROM (SELECT u, SUM(CASE WHEN k='watch_add' THEN 1 ELSE -1 END) s FROM events WHERE k IN ('watch_add','watch_remove') AND t=?1 GROUP BY u HAVING s>0)`, t))[0] || {};
  return { t, views7: v.views || 0, uniq7: v.uniq || 0, rank7: (v.uniq || 0) >= MIN_UNIQ ? rank.r : null, bull: votes.bull || 0, bear: votes.bear || 0, mine, watchers: watchers.n || 0 };
}
