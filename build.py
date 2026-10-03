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

# ---------------- currency conversion (foreign filers -> USD) ----------------
FX_HIST = {}     # cur -> sorted list of (date, units_per_usd)   (ECB reference rates)
FX_LATEST = {}   # cur -> units_per_usd                          (all currencies, latest)

def load_fx():
    """ECB history via frankfurter.app (no key) + latest rates for all currencies (fallback)."""
    import bisect  # noqa
    try:
        start = (dt.date.today() - dt.timedelta(days=365 * 14)).isoformat()
        j = json.loads(fetch(f"https://api.frankfurter.app/{start}..?from=USD", retries=3))
        for d, rates in j.get("rates", {}).items():
            for c, v in rates.items():
                FX_HIST.setdefault(c.upper(), []).append((d, v))
        for c in FX_HIST: FX_HIST[c].sort()
        log("fx history currencies:", len(FX_HIST))
    except Exception as e:
        log("fx history failed", e)
    for url in ("https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json",
                "https://latest.currency-api.pages.dev/v1/currencies/usd.json"):
        try:
            j = json.loads(fetch(url, retries=2))
            FX_LATEST.update({k.upper(): v for k, v in j["usd"].items() if isinstance(v, (int, float)) and v > 0})
            log("fx latest currencies:", len(FX_LATEST)); break
        except Exception as e:
            log("fx latest failed", url, e)

def fx_rate(cur, date):
    """Units of cur per 1 USD at date (nearest earlier ECB fixing, else latest rate)."""
    import bisect
    h = FX_HIST.get(cur)
    if h:
        i = bisect.bisect_right(h, (date, float("inf"))) - 1
        if i >= 0 and days(h[i][0], date) < 40:
            return h[i][1], True
    v = FX_LATEST.get(cur)
    return (v, False) if v else (None, False)

CUR_RE = re.compile(r"^([A-Z]{3})(/shares)?$")

def annual_series(facts, tags, kind, meta=None):
    """Merge annual values across fallback tags (priority order) per fiscal-period end.
    Foreign-currency values are converted to USD at the fiscal-year-end exchange rate.
    Returns (values{end: val}, filed{end: filed_date}, history{end: [(filed, val), ...]})."""
    vals, filed, hist = {}, {}, {}
    for tag in tags:
        ns, name = tag.split(":")
        node = facts.get(ns, {}).get(name)
        if not node: continue
        units = node.get("units", {})
        unit_key = next((u for u in ("USD", "shares", "USD/shares") if u in units), None)
        cur = "USD"
        if unit_key is None:
            for u in units:
                m = CUR_RE.match(u)
                if m and m.group(1) != "USD":
                    unit_key, cur = u, m.group(1); break
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
            val = f["val"]
            if cur != "USD":
                rate, exact = fx_rate(cur, end)
                if not rate: continue
                val = val / rate
                if meta is not None:
                    meta["currency"] = cur
                    if not exact: meta["fx_approx"] = True
            h[end].append((fd, val))
            prev = series.get(end)
            if prev is None or fd >= prev[1]:   # most recently filed (restated) value wins
                series[end] = (val, fd)
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
    meta = {}
    for key, (kind, tags) in CONCEPTS.items():
        series[key], filed[key], hist[key] = annual_series(facts, tags, kind, meta)
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
        "currency": "USD", "reported_currency": meta.get("currency", "USD"),
        "fx_approx": bool(meta.get("fx_approx")), "source": "SEC EDGAR XBRL (companyfacts)",
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "latest": {k: last[k] for k in ("fy", "fy_end", "revenue", "net_income", "fcf", "eps_diluted",
                                         "shares_diluted", "shares_out", "cash", "debt", "equity",
                                         "net_margin", "fcf_margin", "roic")},
        "summary": summary,
        "annual": rows,
    }

# ---------------- market data (price, market cap, sector) ----------------
def num(x):
    try:
        return float(str(x).replace("$", "").replace(",", "").replace("%", "").strip())
    except Exception:
        return None

def load_market():
    """Last close, market cap, sector & industry for all US-listed stocks (Nasdaq screener, one request).
    Used to compute valuation ratios and scores; refreshed on every build."""
    out = {}
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25000&download=true"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.nasdaq.com", "Referer": "https://www.nasdaq.com/"})
        with urllib.request.urlopen(req, timeout=120) as r:
            j = json.loads(r.read())
        for row in j["data"]["rows"]:
            t = row["symbol"].strip().replace("/", "-").replace("^", "-P")
            out[t] = {"price": num(row.get("lastsale")), "mcap": num(row.get("marketCap")),
                      "sector": (row.get("sector") or "").strip() or None,
                      "industry": (row.get("industry") or "").strip() or None,
                      "country": (row.get("country") or "").strip() or None}
        log("market rows:", len(out))
    except Exception as e:
        log("market data failed", e)
    return out

def clamp(x, a, b):
    return max(a, min(b, x))

def dcf_fair_mcap(rec):
    """Company-level fair value with the same default 'medium' assumptions as the DCF page."""
    s, last = rec["summary"], rec["annual"][-1]
    rev = last["revenue"]
    if not rev or rev <= 0: return None
    g = s.get("rev_cagr_5y") if s.get("rev_cagr_5y") is not None else s.get("rev_cagr_1y")
    g = clamp((g if g is not None else 0.05) * 0.8, -0.05, 0.25)
    pm = s.get("net_margin_avg_5y") if s.get("net_margin_avg_5y") is not None else last.get("net_margin")
    if pm is None or pm < 0.02: pm = last.get("net_margin") if (last.get("net_margin") or 0) > 0.02 else 0.08
    fm = s.get("fcf_margin_avg_5y") if s.get("fcf_margin_avg_5y") is not None else last.get("fcf_margin")
    if fm is None or fm < 0.02: fm = pm
    pm, fm = clamp(pm, 0.02, 0.5), clamp(fm, 0.02, 0.55)
    rev10 = rev * (1 + g) ** 10
    return ((rev10 * pm * 22) + (rev10 * fm * 22)) / 2 / (1.10 ** 10)

def pts(*checks):
    """Each check is True/False/None. Score = passed checks (0-5); None = not enough data (counts as fail)."""
    return sum(1 for c in checks if c is True)

def score(rec, mk, sector_pe):
    a, s = rec["annual"], rec["summary"]
    last = a[-1]
    prev3 = a[-4] if len(a) >= 4 else None
    rev, ni, fcf = last["revenue"], last["net_income"], last["fcf"]
    mcap = (mk or {}).get("mcap")
    pe = mcap / ni if (mcap and ni and ni > 0) else None
    pfcf = mcap / fcf if (mcap and fcf and fcf > 0) else None
    ps = mcap / rev if (mcap and rev and rev > 0) else None
    eg = s.get("eps_cagr_5y") if s.get("eps_cagr_5y") is not None else s.get("ni_cagr_5y")
    peg = pe / (eg * 100) if (pe and eg and eg > 0) else None
    fair = dcf_fair_mcap(rec)
    spe = sector_pe.get((mk or {}).get("sector"))
    value = pts(pe is not None and pe < 25,
                pe is not None and spe is not None and pe < spe,
                pfcf is not None and pfcf < 20,
                fair is not None and mcap is not None and fair > mcap,
                peg is not None and peg < 1.5) if mcap else None

    nm_hist = [r["net_margin"] for r in a[-3:] if r["net_margin"] is not None]
    future = pts((last.get("revenue_growth") or 0) > 0.10,
                 (s.get("rev_cagr_3y") or 0) > 0.10,
                 bool(nm_hist) and last["net_margin"] is not None and last["net_margin"] > sum(nm_hist) / len(nm_hist),
                 (s.get("fcf_cagr_3y") or 0) > 0.10,
                 rev and last.get("rnd") is not None and last["rnd"] / rev > 0.05 or (last.get("revenue_growth") or 0) > 0.20)

    past = pts((s.get("eps_cagr_5y") or 0) > 0.10,
               (s.get("rev_cagr_5y") or 0) > 0.08,
               (s.get("roic_avg_5y") or 0) > 0.12,
               len(a) >= 5 and all((r["net_income"] or -1) > 0 for r in a[-5:]),
               (last.get("roe") or 0) > 0.15)

    debt, cash, eq = last.get("debt") or 0, last.get("cash") or 0, last.get("equity")
    op, ie = last.get("op_income"), last.get("interest_exp")
    health = pts(cash >= debt or (eq and eq > 0 and debt / eq < 0.5),
                 fcf is not None and fcf > 0,
                 debt == 0 or (op is not None and ie and ie > 0 and op / ie > 5) or (op and op > 0 and not ie),
                 debt == 0 or (fcf is not None and fcf > 0 and debt / fcf < 3),
                 bool(last.get("assets")) and last.get("liabilities") is not None and last["liabilities"] / last["assets"] < 0.6)

    divs = [r.get("dividends") for r in a[-3:]]
    sh_now, sh_3 = last.get("shares_diluted"), (prev3 or {}).get("shares_diluted")
    returned = (last.get("dividends") or 0) + (last.get("buybacks") or 0)
    capital = pts((last.get("dividends") or 0) > 0,
                  bool(sh_now and sh_3) and sh_now < sh_3 * 0.99,
                  fcf is not None and fcf > 0 and 0.2 <= returned / fcf <= 1.0,
                  len(divs) == 3 and all((d or 0) > 0 for d in divs),
                  rev and last.get("sbc") is not None and last["sbc"] / rev < 0.05)

    parts = [x for x in (value, future, past, health, capital) if x is not None]
    total = round(sum(parts) / len(parts), 1) if parts else None
    divy = (last.get("dividends") or 0) / mcap if mcap else None
    return {"value": value, "future": future, "past": past, "health": health, "capital": capital, "total": total}, \
           {"pe": pe, "pfcf": pfcf, "ps": ps, "peg": peg, "fair_mcap": fair, "div_yield": divy}

def finish(recs, market):
    # sector median P/E (positive earners with a market cap)
    by_sector = defaultdict(list)
    for r in recs:
        mk = market.get(r["ticker"])
        ni = r["annual"][-1]["net_income"]
        if mk and mk.get("mcap") and mk.get("sector") and ni and ni > 0:
            by_sector[mk["sector"]].append(mk["mcap"] / ni)
    sector_pe = {k: sorted(v)[len(v) // 2] for k, v in by_sector.items() if len(v) >= 10}
    log("sector medians:", {k: round(v, 1) for k, v in sector_pe.items()})

    # one company can have several tickers (share classes, notes, preferred). Keep only the
    # tickers whose market cap is close to the company's main listing; drop odd instruments.
    best = defaultdict(float)
    for r in recs:
        m = (market.get(r["ticker"]) or {}).get("mcap") or 0
        best[r["cik"]] = max(best[r["cik"]], m)
    multi = defaultdict(int)
    for r in recs: multi[r["cik"]] += 1
    def keep(r):
        if multi[r["cik"]] == 1: return True
        m = (market.get(r["ticker"]) or {}).get("mcap") or 0
        return best[r["cik"]] == 0 or m >= 0.5 * best[r["cik"]]
    dropped = [r["ticker"] for r in recs if not keep(r)]
    # alias every dropped ticker to the company's main listing, so a search for e.g. GOOGM
    # opens Alphabet (GOOGL) instead of "not found"
    primary = {}
    for r in recs:
        m = (market.get(r["ticker"]) or {}).get("mcap") or 0
        if keep(r) and (r["cik"] not in primary or m > primary[r["cik"]][1]):
            primary[r["cik"]] = (r["ticker"], m)
    aliases = {r["ticker"]: primary[r["cik"]][0] for r in recs if not keep(r) and r["cik"] in primary}
    alias_names = {r["ticker"]: r["name"] for r in recs if not keep(r)}
    recs = [r for r in recs if keep(r)]
    log("dropped secondary instruments:", len(dropped), dropped[:20])
    with open(os.path.join(OUT, "aliases.json"), "w") as f:
        json.dump(aliases, f, separators=(",", ":"))

    index, screener = [], []
    for r in recs:
        mk = market.get(r["ticker"]) or {}
        sc, ratios = score(r, mk, sector_pe)
        r["market"] = {"price": mk.get("price"), "mcap": mk.get("mcap"), "sector": mk.get("sector"),
                       "industry": mk.get("industry"), "country": mk.get("country"), "as_of": dt.date.today().isoformat()}
        r["ratios"] = {k: r4(v) for k, v in ratios.items()}
        r["scores"] = sc
        with open(os.path.join(OUT, "stocks", f"{r['ticker']}.json"), "w") as f:
            json.dump(r, f, separators=(",", ":"))
        last, s = r["annual"][-1], r["summary"]
        index.append({"t": r["ticker"], "n": r["name"], "rev": last["revenue"]})
        screener.append([r["ticker"], r["name"], mk.get("sector"), mk.get("industry"),
                         mk.get("price"), mk.get("mcap"),
                         r4(ratios["pe"]), r4(ratios["pfcf"]), r4(ratios["ps"]), r4(ratios["div_yield"]),
                         r4(last.get("revenue_growth")), s.get("rev_cagr_5y"), last.get("net_margin"),
                         last.get("fcf_margin"), last.get("roic"), last.get("debt_to_equity"),
                         sc["value"], sc["future"], sc["past"], sc["health"], sc["capital"], sc["total"],
                         last["revenue"], r.get("reported_currency", "USD")])
    index.sort(key=lambda x: -(x["rev"] or 0))
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump([{"t": x["t"], "n": x["n"]} for x in index] +
                  [{"t": a, "n": alias_names.get(a, ""), "a": p} for a, p in sorted(aliases.items())],
                  f, separators=(",", ":"))
    screener.sort(key=lambda x: -(x[5] or 0))
    with open(os.path.join(OUT, "screener.json"), "w") as f:
        json.dump({"cols": ["t", "n", "sector", "industry", "price", "mcap", "pe", "pfcf", "ps", "divy",
                            "revg1", "revg5", "nm", "fm", "roic", "de",
                            "s_value", "s_future", "s_past", "s_health", "s_capital", "s_total", "rev", "cur"],
                   "as_of": dt.date.today().isoformat(), "rows": screener}, f, separators=(",", ":"))
    log("wrote", len(recs), "stocks + screener")

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

    import shutil
    shutil.rmtree(os.path.join(OUT, "stocks"), ignore_errors=True)
    os.makedirs(os.path.join(OUT, "stocks"), exist_ok=True)
    load_fx()
    market = load_market()
    recs, done, skipped = [], 0, 0
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
            recs.append(rec)
            done += 1
        if done % 500 == 0 and done: log("processed", done)

    finish(recs, market)
    with open(os.path.join(OUT, "meta.json"), "w") as f:
        json.dump({"built": dt.datetime.now(dt.timezone.utc).isoformat(), "stocks": done, "skipped": skipped,
                   "source": "SEC EDGAR"}, f)
    log("done. stocks:", done, "skipped (no usable annual data):", skipped)

if __name__ == "__main__":
    main()
