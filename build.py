#!/usr/bin/env python3
"""
Nightly SEC EDGAR fundamentals engine for rezahajiloubooks.com

1. Downloads SEC's bulk companyfacts.zip (one file, all companies, all XBRL facts).
2. Downloads company_tickers.json (ticker -> CIK map).
3. For every company with a ticker, extracts up to 12 fiscal years of annual figures
   from 10-K / 20-F / 40-F filings, with tag fallbacks (US-GAAP and IFRS).
4. Computes margins, growth, FCF, ROIC, per-share data, etc.
5. Writes data/stocks/<TICKER>.json  (one small file per stock)
          data/index.json             (ticker, name, cik, last FY — for the search box)
          data/meta.json              (build time, counts)

Data source: U.S. Securities and Exchange Commission, EDGAR XBRL APIs (public domain).
"""
import io, json, os, re, sys, time, zipfile, datetime as dt
from collections import defaultdict
import urllib.request

UA = os.environ.get("SEC_USER_AGENT", "Reza Hajilou mreza.hajilou@gmail.com")
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
YEARS = 12
ANNUAL_FORMS = {"10-K", "10-K/A", "10-KT", "20-F", "20-F/A", "40-F", "40-F/A"}
LIMIT = int(os.environ.get("LIMIT", "0"))  # for testing: process only N companies

# ---- concept fallbacks: first tag with data wins (per fiscal year) ----
# (kind: 'dur' = duration/flow over the year, 'inst' = instant/balance at FY end)
CONCEPTS = {
    "revenue": ("dur", [
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax",
        "us-gaap:SalesRevenueNet",
        "us-gaap:SalesRevenueGoodsNet",
        "us-gaap:SalesRevenueServicesNet",
        "us-gaap:RevenuesNetOfInterestExpense",
        "us-gaap:InterestAndDividendIncomeOperating",
        "ifrs-full:Revenue",
        "ifrs-full:RevenueFromContractsWithCustomers",
    ]),
    "cogs": ("dur", ["us-gaap:CostOfRevenue", "us-gaap:CostOfGoodsAndServicesSold", "us-gaap:CostOfGoodsSold",
                      "us-gaap:CostOfServices", "ifrs-full:CostOfSales"]),
    "gross_profit": ("dur", ["us-gaap:GrossProfit", "ifrs-full:GrossProfit"]),
    "op_income": ("dur", ["us-gaap:OperatingIncomeLoss", "ifrs-full:ProfitLossFromOperatingActivities"]),
    "pretax_income": ("dur", [
        "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        "ifrs-full:ProfitLossBeforeTax"]),
    "tax": ("dur", ["us-gaap:IncomeTaxExpenseBenefit", "ifrs-full:IncomeTaxExpenseContinuingOperations"]),
    "net_income": ("dur", ["us-gaap:NetIncomeLoss", "us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic",
                            "us-gaap:ProfitLoss", "ifrs-full:ProfitLossAttributableToOwnersOfParent", "ifrs-full:ProfitLoss"]),
    "eps_diluted": ("dur", ["us-gaap:EarningsPerShareDiluted", "us-gaap:EarningsPerShareBasicAndDiluted",
                             "ifrs-full:DilutedEarningsLossPerShare"]),
    "shares_diluted": ("dur", ["us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding",
                                "us-gaap:WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
                                "ifrs-full:WeightedAverageNumberOfDilutedSharesOutstanding",
                                "ifrs-full:AdjustedWeightedAverageShares"]),
    "shares_basic": ("dur", ["us-gaap:WeightedAverageNumberOfSharesOutstandingBasic",
                              "ifrs-full:WeightedAverageShares"]),
    "cfo": ("dur", ["us-gaap:NetCashProvidedByUsedInOperatingActivities",
                     "us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                     "ifrs-full:CashFlowsFromUsedInOperatingActivities"]),
    "capex": ("dur", ["us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",
                       "us-gaap:PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets",
                       "us-gaap:PaymentsToAcquireProductiveAssets",
                       "us-gaap:PaymentsForCapitalImprovements",
                       "us-gaap:PaymentsToDevelopSoftware",
                       "us-gaap:PaymentsForSoftware",
                       "ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"]),
    "sbc": ("dur", ["us-gaap:ShareBasedCompensation", "us-gaap:AllocatedShareBasedCompensationExpense"]),
    "dividends": ("dur", ["us-gaap:PaymentsOfDividendsCommonStock", "us-gaap:PaymentsOfDividends",
                           "ifrs-full:DividendsPaidClassifiedAsFinancingActivities"]),
    "buybacks": ("dur", ["us-gaap:PaymentsForRepurchaseOfCommonStock",
                          "ifrs-full:PaymentsToAcquireOrRedeemEntitysShares"]),
    "rnd": ("dur", ["us-gaap:ResearchAndDevelopmentExpense",
                     "us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]),
    "da": ("dur", ["us-gaap:DepreciationDepletionAndAmortization", "us-gaap:DepreciationAndAmortization",
                    "us-gaap:DepreciationAmortizationAndAccretionNet",
                    "ifrs-full:DepreciationAndAmortisationExpense"]),
    "interest_exp": ("dur", ["us-gaap:InterestExpense", "us-gaap:InterestExpenseNonoperating",
                              "ifrs-full:InterestExpense"]),
    # balance sheet (instant)
    "assets": ("inst", ["us-gaap:Assets", "ifrs-full:Assets"]),
    "liabilities": ("inst", ["us-gaap:Liabilities", "ifrs-full:Liabilities"]),
    "equity": ("inst", ["us-gaap:StockholdersEquity",
                         "us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                         "ifrs-full:EquityAttributableToOwnersOfParent", "ifrs-full:Equity"]),
    "cash": ("inst", ["us-gaap:CashAndCashEquivalentsAtCarryingValue",
                       "us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                       "us-gaap:CashCashEquivalentsAndShortTermInvestments",
                       "ifrs-full:CashAndCashEquivalents"]),
    "st_investments": ("inst", ["us-gaap:ShortTermInvestments", "us-gaap:MarketableSecuritiesCurrent",
                                 "us-gaap:AvailableForSaleSecuritiesDebtSecuritiesCurrent"]),
    "debt_lt": ("inst", ["us-gaap:LongTermDebtNoncurrent", "us-gaap:LongTermDebtAndCapitalLeaseObligations",
                          "us-gaap:LongTermDebt", "ifrs-full:NoncurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings",
                          "ifrs-full:LongtermBorrowings"]),
    "debt_st": ("inst", ["us-gaap:LongTermDebtCurrent", "us-gaap:DebtCurrent", "us-gaap:ShortTermBorrowings",
                          "us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent", "ifrs-full:ShorttermBorrowings",
                          "ifrs-full:CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings"]),
    "goodwill": ("inst", ["us-gaap:Goodwill", "ifrs-full:Goodwill"]),
    "shares_out": ("inst", ["dei:EntityCommonStockSharesOutstanding", "us-gaap:CommonStockSharesOutstanding",
                             "ifrs-full:NumberOfSharesOutstanding"]),
}

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

def fetch(url, retries=4):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip; data = gzip.decompress(data)
                return data
        except Exception as e:
            log("fetch retry", i, url, e); time.sleep(3 * (i + 1))
    raise RuntimeError("fetch failed " + url)

def days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days

def annual_series(facts, tags, kind):
    """Merge annual values across fallback tags (priority order) per fiscal-period end.
    Returns (values{end: val}, filed{end: filed_date}, history{end: [(filed, val), ...]})."""
    vals, filed, hist = {}, {}, {}
    for tag in tags:
        ns, name = tag.split(":")
        node = facts.get(ns, {}).get(name)
        if not node: continue
        units = node.get("units", {})
        unit_key = next((u for u in ("USD", "shares", "USD/shares") if u in units), None)
        if unit_key is None:
            unit_key = next(iter(units), None)
        if unit_key is None: continue
        series, h = {}, defaultdict(list)
        for f in units[unit_key]:
            if f.get("form") not in ANNUAL_FORMS: continue
            end = f.get("end")
            if not end: continue
            if kind == "dur":
                st = f.get("start")
                if not st or not (340 <= days(st, end) <= 380): continue
            fd = f.get("filed", "")
            h[end].append((fd, f["val"]))
            prev = series.get(end)
            if prev is None or fd >= prev[1]:   # most recently filed (restated) value wins
                series[end] = (f["val"], fd)
        for end, (v, fd) in series.items():
            if any(abs(days(e, end)) <= 20 for e in vals):   # higher-priority tag already covers it
                continue
            vals[end], filed[end], hist[end] = v, fd, h[end]
    return vals, filed, hist

def split_factors(hist):
    """Detect stock splits from restated share counts: same period reported with an integer ratio
    in a later filing. Returns list of (first_restated_filing_date, ratio)."""
    events = []
    for end, obs in hist.items():
        obs = sorted(obs)
        for i in range(1, len(obs)):
            a, b = obs[i - 1][1], obs[i][1]
            if not a or not b: continue
            r = b / a
            ratio = r if r >= 1 else 1 / r
            if ratio >= 1.9 and abs(ratio - round(ratio)) / ratio < 0.03:
                events.append((obs[i][0], r))
    # merge events for the same split (within ~13 months of each other, same ratio)
    events.sort()
    merged = []
    for fd, r in events:
        if merged and abs(merged[-1][1] - r) / r < 0.05 and days(merged[-1][0], fd) < 400:
            continue
        merged.append((fd, r))
    return merged

def pick_fy_ends(all_series):
    """Fiscal-year end dates = union of ends seen on revenue/net income/assets (most reliable tags)."""
    ends = set()
    for key in ("revenue", "net_income", "assets", "cfo"):
        ends |= set(all_series.get(key, {}).keys())
    # collapse ends that are within 20 days of each other (52/53-week years) keeping the latest
    ends = sorted(ends)
    merged = []
    for e in ends:
        if merged and days(merged[-1], e) <= 20:
            merged[-1] = e
        else:
            merged.append(e)
    return merged[-YEARS:]

def nearest(series, end, tol=20):
    if end in series: return series[end]
    for k, v in series.items():
        if abs(days(k, end)) <= tol: return v
    return None

def safe_div(a, b):
    try:
        if a is None or b in (None, 0): return None
        return a / b
    except Exception:
        return None

def r4(x):
    return None if x is None else (round(x, 4) if abs(x) < 1000 else round(x))

def build_company(cik, entry, facts):
    series, filed, hist = {}, {}, {}
    for key, (kind, tags) in CONCEPTS.items():
        series[key], filed[key], hist[key] = annual_series(facts, tags, kind)
    # split-adjust per-share series: values taken from filings made before a split get scaled
    splits = split_factors(hist["shares_diluted"]) or split_factors(hist["shares_basic"]) \
        or [(fd, 1 / r) for fd, r in split_factors(hist["eps_diluted"])]
    if splits:
        for key, mult in (("shares_diluted", 1), ("shares_basic", 1), ("shares_out", 1), ("eps_diluted", -1)):
            for end in list(series[key]):
                f = 1.0
                for fd, r in splits:
                    if filed[key].get(end, "") < fd: f *= r
                if f != 1.0 and series[key][end] is not None:
                    series[key][end] = series[key][end] * f if mult == 1 else series[key][end] / f
    ends = pick_fy_ends(series)
    if len(ends) < 2 or not series["revenue"]:
        return None
    rows = []
    for end in ends:
        g = lambda k: nearest(series[k], end)
        rev, ni, cfo = g("revenue"), g("net_income"), g("cfo")
        capex = g("capex")
        fcf = (cfo - abs(capex)) if (cfo is not None and capex is not None) else None
        op = g("op_income")
        tax, pretax = g("tax"), g("pretax_income")
        tax_rate = safe_div(tax, pretax)
        if tax_rate is None or tax_rate < 0 or tax_rate > 0.5: tax_rate = 0.21
        nopat = op * (1 - tax_rate) if op is not None else None
        debt = (g("debt_lt") or 0) + (g("debt_st") or 0)
        cash = (g("cash") or 0) + (g("st_investments") or 0)
        equity = g("equity")
        invested = (equity + debt) if equity is not None else None
        if invested is not None and invested <= 0: invested = None
        gp = g("gross_profit")
        if gp is None and rev is not None and g("cogs") is not None: gp = rev - g("cogs")
        sh_d = g("shares_diluted") or g("shares_basic")
        if not sh_d and ni and g("eps_diluted"):
            sh_d = abs(ni / g("eps_diluted"))
        rows.append({
            "fy_end": end,
            "fy": int(end[:4]),
            "revenue": rev, "gross_profit": gp, "op_income": op, "net_income": ni,
            "eps_diluted": g("eps_diluted"), "shares_diluted": sh_d, "shares_out": g("shares_out"),
            "cfo": cfo, "capex": None if capex is None else abs(capex), "fcf": fcf,
            "sbc": g("sbc"), "dividends": g("dividends"), "buybacks": g("buybacks"),
            "rnd": g("rnd"), "da": g("da"), "interest_exp": g("interest_exp"),
            "assets": g("assets"), "liabilities": g("liabilities"), "equity": equity,
            "cash": cash or None, "debt": debt or None, "net_debt": (debt - cash) if (debt or cash) else None,
            "goodwill": g("goodwill"),
            # ratios
            "gross_margin": r4(safe_div(gp, rev)),
            "op_margin": r4(safe_div(op, rev)),
            "net_margin": r4(safe_div(ni, rev)),
            "fcf_margin": r4(safe_div(fcf, rev)),
            "roic": r4(safe_div(nopat, invested)),
            "roe": r4(safe_div(ni, equity)),
            "roa": r4(safe_div(ni, g("assets"))),
            "debt_to_equity": r4(safe_div(debt, equity)),
            "fcf_per_share": r4(safe_div(fcf, sh_d)),
            "revenue_per_share": r4(safe_div(rev, sh_d)),
            "book_value_per_share": r4(safe_div(equity, sh_d)),
        })
    rows = [r for r in rows if r["revenue"] is not None or r["net_income"] is not None]
    dedup = {}
    for r in rows: dedup[r["fy"]] = r          # later fiscal-year end wins
    rows = [dedup[k] for k in sorted(dedup)]
    if len(rows) < 2:
        return None
    # growth rates
    for i, r in enumerate(rows):
        for k in ("revenue", "net_income", "fcf", "eps_diluted", "shares_diluted"):
            prev = rows[i - 1][k] if i > 0 else None
            cur = r[k]
            r[k + "_growth"] = r4((cur - prev) / abs(prev)) if (prev not in (None, 0) and cur is not None) else None

    def cagr(key, n):
        if len(rows) <= n: return None
        a, b = rows[-1 - n][key], rows[-1][key]
        if a in (None, 0) or b is None or a < 0 or b < 0: return None
        return r4((b / a) ** (1 / n) - 1)
    def avg(key, n):
        vals = [r[key] for r in rows[-n:] if r[key] is not None]
        return r4(sum(vals) / len(vals)) if vals else None

    summary = {}
    for n in (1, 3, 5, 10):
        summary[f"rev_cagr_{n}y"] = cagr("revenue", n)
        summary[f"ni_cagr_{n}y"] = cagr("net_income", n)
        summary[f"fcf_cagr_{n}y"] = cagr("fcf", n)
        summary[f"eps_cagr_{n}y"] = cagr("eps_diluted", n)
        summary[f"net_margin_avg_{n}y"] = avg("net_margin", n)
        summary[f"fcf_margin_avg_{n}y"] = avg("fcf_margin", n)
        summary[f"roic_avg_{n}y"] = avg("roic", n)
        summary[f"op_margin_avg_{n}y"] = avg("op_margin", n)
    last = rows[-1]
    return {
        "ticker": entry["ticker"], "name": entry["title"], "cik": cik,
        "currency": "USD", "source": "SEC EDGAR XBRL (companyfacts)",
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "latest": {k: last[k] for k in ("fy", "fy_end", "revenue", "net_income", "fcf", "eps_diluted",
                                         "shares_diluted", "shares_out", "cash", "debt", "equity",
                                         "net_margin", "fcf_margin", "roic")},
        "summary": summary,
        "annual": rows,
    }

def main():
    os.makedirs(os.path.join(OUT, "stocks"), exist_ok=True)
    log("downloading ticker map")
    tickers = json.loads(fetch("https://www.sec.gov/files/company_tickers.json"))
    by_cik = defaultdict(list)
    for v in tickers.values():
        by_cik[int(v["cik_str"])].append({"ticker": v["ticker"], "title": v["title"]})
    log("companies with tickers:", len(by_cik))

    log("downloading companyfacts.zip (about 1.2 GB)")
    zpath = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "companyfacts.zip")
    req = urllib.request.Request("https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip",
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=1800) as r, open(zpath, "wb") as f:
        while True:
            chunk = r.read(8 << 20)
            if not chunk: break
            f.write(chunk)
    log("downloaded", os.path.getsize(zpath) // 1_000_000, "MB")
    zf = zipfile.ZipFile(zpath)

    index, done, skipped = [], 0, 0
    for name in zf.namelist():
        m = re.match(r"CIK(\d+)\.json$", name)
        if not m: continue
        cik = int(m.group(1))
        if cik not in by_cik: continue
        if LIMIT and done >= LIMIT: break
        try:
            doc = json.loads(zf.read(name))
        except Exception as e:
            log("bad json", name, e); continue
        facts = doc.get("facts", {})
        for entry in by_cik[cik]:
            # one listing can have several share classes (GOOGL/GOOG): same data, both tickers
            rec = build_company(cik, entry, facts)
            if not rec:
                skipped += 1; continue
            with open(os.path.join(OUT, "stocks", f"{entry['ticker']}.json"), "w") as f:
                json.dump(rec, f, separators=(",", ":"))
            index.append({"t": entry["ticker"], "n": entry["title"], "c": cik,
                          "fy": rec["latest"]["fy"], "rev": rec["latest"]["revenue"]})
            done += 1
        if done % 500 == 0 and done: log("processed", done)

    index.sort(key=lambda x: -(x["rev"] or 0))
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump(index, f, separators=(",", ":"))
    with open(os.path.join(OUT, "meta.json"), "w") as f:
        json.dump({"built": dt.datetime.now(dt.timezone.utc).isoformat(), "stocks": done, "skipped": skipped,
                   "source": "SEC EDGAR"}, f)
    log("done. stocks:", done, "skipped (no usable annual data):", skipped)

if __name__ == "__main__":
    main()
