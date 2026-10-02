# stock-data — nightly SEC fundamentals for rezahajiloubooks.com
- `scripts/build.py` downloads SEC EDGAR bulk XBRL data and writes one JSON per US-listed stock into `data/stocks/`.
- `scripts/verify.py` checks a sample of companies against independently published figures.
- `.github/workflows/nightly.yml` runs it every night and commits the result.
Data: U.S. SEC EDGAR (public domain). Prices are not included.
