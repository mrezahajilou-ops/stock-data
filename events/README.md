# rz-events — anonymous usage events

Receives tiny anonymous events from the site (which stock was viewed / searched / added to a watchlist / voted on)
and serves the aggregates for the "نبض جامعه" page and the community tile on each stock page.

Deploy once (needs a free Cloudflare account):
1. Create an API token at dash.cloudflare.com → My Profile → API Tokens → "Edit Cloudflare Workers" template (add D1:Edit).
2. `export CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=...` then `./deploy.sh` (creates the D1 database, applies schema.sql, deploys).
3. Put the printed `https://rz-events.<account>.workers.dev` into `EVENTS_URL` in gen_web.py and run `python3 gen_web.py`.

Until EVENTS_URL is set, the beacon in the pages is a no-op and the pulse page says data collection is not active.
Privacy: no IP, user agent, name or email is stored — only a random browser id, the ticker and the event kind; rows older than 400 days are deleted nightly.
