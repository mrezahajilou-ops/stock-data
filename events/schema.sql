CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,          -- unix seconds
  k  TEXT NOT NULL,             -- view | search | watch_add | watch_remove | vote | compare
  t  TEXT NOT NULL,             -- ticker
  u  TEXT NOT NULL,             -- anonymous browser id
  v  TEXT                       -- small value: 'pw' (paywalled view), 'bull'/'bear', compare pair
);
CREATE INDEX IF NOT EXISTS ev_ts ON events (ts);
CREATE INDEX IF NOT EXISTS ev_k_ts ON events (k, ts);
CREATE INDEX IF NOT EXISTS ev_t_ts ON events (t, ts);
CREATE INDEX IF NOT EXISTS ev_vote ON events (k, t, u, ts);
