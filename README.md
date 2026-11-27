# breaking — live feed for /breaking-news/ on the stock sites

`en.json` = {"updated": iso, "items": [{id, t (UTC iso), text, src, url}]} newest first.
- `text`: one or two lines, companies as cashtags ($NVDA) — each becomes a link to the stock analysis tool.
- What happened and why, with the source. No forecasts, no advice. Never repeat a story.
- Read live by assets/breaking.js (raw.githubusercontent) and baked into the pages on each site build.
Add items with `python3 add.py items.json` (dedupes by id and by near-identical text, keeps 3,000 newest).
