# stock-data — nightly SEC fundamentals for rezahajiloubooks.com
- `scripts/build.py` downloads SEC EDGAR bulk XBRL data and writes one JSON per US-listed stock into `data/stocks/`.
- `scripts/verify.py` checks a sample of companies against independently published figures.
- `.github/workflows/nightly.yml` runs it every night and commits the result.
Data: U.S. SEC EDGAR (public domain). Prices are not included.

## Persian site (Shopify): adding a tool page without touching the theme

The theme has one generic template, `templates/page.app.liquid` (added 20 Nov 2026). A new tool needs:

1. `web/<app>.html` committed here (build it in `gen_web.py`);
2. a Shopify page with handle `<app>` and template suffix `app` (Admin API `pageCreate`);
3. the text search engines should read in that page's own body (`pageUpdate`), not in the theme.

Optional page metafields: `rz.app` (app name if it differs from the handle), `rz.ld` (extra JSON-LD),
`rz.noad` (`1` hides the ad). Publishing a theme is only needed for changes to the theme's own chrome.
The connector cannot publish themes on this store, and the store is at its 20-theme limit, so
`themeDuplicate` silently returns nothing; edit an existing draft instead.
