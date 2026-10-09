#!/usr/bin/env python3
"""
SEC EDGAR fundamentals engine for rezahajiloubooks.com  (v2)

1. Downloads SEC's bulk companyfacts.zip (one file, all companies, all XBRL facts).
2. Downloads company_tickers.json (ticker -> CIK map).
3. For every company with a ticker, extracts up to 12 fiscal years of annual figures
   from 10-K / 20-F / 40-F filings, with tag fallbacks (US-GAAP and IFRS).
4. Computes margins, growth, FCF, ROIC, per-share data, EV multiples, quality checks, etc.
5. Writes data/stocks/<TICKER>.json (one small file per stock)
          data/index.json   (ticker, name, cik — for the search box)
          data/screener.json (one row per stock for the screener)
          data/meta.json    (build time, counts)

Data source: U.S. Securities and Exchange Commission, EDGAR XBRL APIs (public domain).
"""
import io, json, os, re, sys, time, zipfile, datetime as dt
from collections import defaultdict
import urllib.request

UA = os.environ.get("SEC_USER_AGENT", "Reza Hajilou mreza.hajilou@gmail.com")
OUT = os.path.join(os.getcwd(), "data")
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
        # utilities, REITs, miners, energy, healthcare (fill-only: used when the tags above are missing)
        "us-gaap:RegulatedAndUnregulatedOperatingRevenue",
        "us-gaap:RegulatedOperatingRevenue",
        "us-gaap:ElectricUtilityRevenue",
        "us-gaap:OperatingLeaseLeaseIncome",
        "us-gaap:OperatingLeasesIncomeStatementLeaseRevenue",
        "us-gaap:RealEstateRevenueNet",
        "us-gaap:RevenueMineralSales",
        "us-gaap:OilAndGasRevenue",
        "us-gaap:HealthCareOrganizationRevenue",
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
                            "ifrs-full:DilutedEarningsLossPerShare", "us-gaap:EarningsPerShareBasic",
                            "us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare",
                            "ifrs-full:BasicAndDilutedEarningsLossPerShare", "ifrs-full:BasicEarningsLossPerShare"]),
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
                      "ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
                      "us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment",
                      "us-gaap:PaymentsForProceedsFromProductiveAssets",
                      "us-gaap:PaymentsToAcquireRealEstate",
                      "us-gaap:PaymentsToDevelopRealEstateAssets",
                      "us-gaap:PaymentsToAcquireOilAndGasPropertyAndEquipment",
                      "ifrs-full:PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets"]),
    "sbc": ("dur", ["us-gaap:ShareBasedCompensation", "us-gaap:AllocatedShareBasedCompensationExpense",
                    "ifrs-full:AdjustmentsForSharebasedPayments"]),
    "dividends": ("dur", ["us-gaap:PaymentsOfDividendsCommonStock", "us-gaap:PaymentsOfDividends",
                          "ifrs-full:DividendsPaidClassifiedAsFinancingActivities", "us-gaap:PaymentsOfOrdinaryDividends",
                          "us-gaap:DividendsCommonStockCash", "us-gaap:DividendsCommonStock",
                          "ifrs-full:DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities", "ifrs-full:DividendsPaid"]),
    "buybacks": ("dur", ["us-gaap:PaymentsForRepurchaseOfCommonStock",
                         "ifrs-full:PaymentsToAcquireOrRedeemEntitysShares", "us-gaap:PaymentsForRepurchaseOfEquity"]),
    "rnd": ("dur", ["us-gaap:ResearchAndDevelopmentExpense",
                    "us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]),
    "da": ("dur", ["us-gaap:DepreciationDepletionAndAmortization", "us-gaap:DepreciationAndAmortization",
                   "us-gaap:DepreciationAmortizationAndAccretionNet",
                   "ifrs-full:DepreciationAndAmortisationExpense", "us-gaap:Depreciation",
                   "us-gaap:DepreciationAmortizationAndOther",
                   "ifrs-full:DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss",
                   "ifrs-full:DepreciationExpense"]),
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
                         "ifrs-full:LongtermBorrowings", "us-gaap:LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
                         "us-gaap:DebtLongtermAndShorttermCombinedAmount", "us-gaap:SeniorLongTermNotes", "us-gaap:SeniorNotes",
                         "us-gaap:LongTermNotesPayable", "us-gaap:NotesPayable", "us-gaap:ConvertibleNotesPayable",
                         "us-gaap:ConvertibleDebtNoncurrent", "us-gaap:UnsecuredLongTermDebt", "us-gaap:SecuredLongTermDebt",
                         "us-gaap:OtherLongTermDebtNoncurrent", "us-gaap:LongTermLineOfCredit", "us-gaap:DebtInstrumentCarryingAmount",
                         "ifrs-full:Borrowings", "ifrs-full:NoncurrentPortionOfNoncurrentBorrowings"]),
    "debt_st": ("inst", ["us-gaap:LongTermDebtCurrent", "us-gaap:DebtCurrent", "us-gaap:ShortTermBorrowings",
                         "us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent", "ifrs-full:ShorttermBorrowings",
                         "ifrs-full:CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings", "us-gaap:CommercialPaper",
                         "us-gaap:NotesPayableCurrent", "us-gaap:ConvertibleNotesPayableCurrent", "us-gaap:LinesOfCreditCurrent"]),
    "goodwill": ("inst", ["us-gaap:Goodwill", "ifrs-full:Goodwill"]),
    "intangibles": ("inst", ["us-gaap:IntangibleAssetsNetExcludingGoodwill",
                             "ifrs-full:IntangibleAssetsOtherThanGoodwill"]),
    "current_assets": ("inst", ["us-gaap:AssetsCurrent", "ifrs-full:CurrentAssets"]),
    "current_liabilities": ("inst", ["us-gaap:LiabilitiesCurrent", "ifrs-full:CurrentLiabilities"]),
    "liab_eq": ("inst", ["us-gaap:LiabilitiesAndStockholdersEquity", "ifrs-full:EquityAndLiabilities"]),
    "equity_total": ("inst", ["us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "ifrs-full:Equity"]),
    "costs_expenses": ("dur", ["us-gaap:CostsAndExpenses"]),
    "opex": ("dur", ["us-gaap:OperatingExpenses"]),
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
                    import gzip
                    data = gzip.decompress(data)
                return data
        except Exception as e:
            log("fetch retry", i, url, e)
            time.sleep(3 * (i + 1))
    raise RuntimeError("fetch failed " + url)


def days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


# ---------------- currency conversion (foreign filers -> USD) ----------------
FX_HIST = {}    # cur -> sorted list of (date, units_per_usd) (ECB reference rates)
FX_LATEST = {}  # cur -> units_per_usd (all currencies, latest)


def load_fx():
    """ECB history via frankfurter.app (no key) + latest rates for all currencies (fallback)."""
    try:
        start = (dt.date.today() - dt.timedelta(days=365 * 14)).isoformat()
        j = json.loads(fetch(f"https://api.frankfurter.app/{start}..?from=USD", retries=3))
        for d, rates in j.get("rates", {}).items():
            for c, v in rates.items():
                FX_HIST.setdefault(c.upper(), []).append((d, v))
        for c in FX_HIST:
            FX_HIST[c].sort()
        log("fx history currencies:", len(FX_HIST))
    except Exception as e:
        log("fx history failed", e)
    for url in ("https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json",
                "https://latest.currency-api.pages.dev/v1/currencies/usd.json"):
        try:
            j = json.loads(fetch(url, retries=2))
            FX_LATEST.update({k.upper(): v for k, v in j["usd"].items() if isinstance(v, (int, float)) and v > 0})
            log("fx latest currencies:", len(FX_LATEST))
            break
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
        if not node:
            continue
        units = node.get("units", {})
        unit_key = next((u for u in ("USD", "shares", "USD/shares") if u in units), None)
        cur = "USD"
        if unit_key is None:
            for u in units:
                m = CUR_RE.match(u)
                if m and m.group(1) != "USD":
                    unit_key, cur = u, m.group(1)
                    break
        if unit_key is None:
            continue
        series, h = {}, defaultdict(list)
        if kind == "dur":
            q4s, ytd9 = [], {}
            for f in units[unit_key]:
                st, en = f.get("start"), f.get("end")
                if not st or not en:
                    continue
                n = days(st, en)
                if f.get("form") in ANNUAL_FORMS and 80 <= n <= 100:
                    q4s.append(f)
                elif 255 <= n <= 290:
                    ytd9.setdefault((st, en), f)
            cands = {}
            for f in q4s:
                for (s9, e9), g in ytd9.items():
                    if abs(days(e9, f["start"])) <= 6 and 350 <= days(s9, f["end"]) <= 380:
                        rate = 1.0
                        if cur != "USD":
                            rate, _ = fx_rate(cur, f["end"])
                            if not rate:
                                break
                        cands[f["end"]] = ((f["val"] + g["val"]) / rate, f["val"] / rate, g["val"] / rate, f.get("filed", ""))
                        break
        derived = set()
        for f in units[unit_key]:
            if f.get("form") not in ANNUAL_FORMS:
                continue
            end = f.get("end")
            if not end:
                continue
            if kind == "dur":
                st = f.get("start")
                if not st or not (340 <= days(st, end) <= 380):
                    continue
            fd = f.get("filed", "")
            val = f["val"]
            if cur != "USD":
                rate, exact = fx_rate(cur, end)
                if not rate:
                    continue
                val = val / rate
                if meta is not None:
                    meta["currency"] = cur
                    if not exact:
                        meta["fx_approx"] = True
            h[end].append((fd, val))
            prev = series.get(end)
            if prev is None or fd >= prev[1]:  # most recently filed (restated) value wins
                series[end] = (val, fd)
        if kind == "dur":
            # fiscal years whose 10-K only tags the 4th quarter: Q4 + 9-month YTD. Some filers tag the full
            # year with a 3-month start date by mistake, so check against the prior year before adding.
            for end, (summed, q4, y9, fd) in cands.items():
                if end in series:
                    continue
                prior = [v for e, (v, _) in series.items() if 330 <= days(e, end) <= 400]
                val = summed
                if prior and prior[0]:
                    if abs(q4 / prior[0] - 1) < abs(summed / prior[0] - 1):
                        val = q4
                elif q4 > 0.6 * y9:
                    val = q4
                series[end] = (val, fd)
                h[end].append((fd, val))
        for end, (v, fd) in series.items():
            if any(abs(days(e, end)) <= 20 for e in vals):  # higher-priority tag already covers it
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
            if not a or not b:
                continue
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


def fy_of(end):
    """52/53-week fiscal years that end in the first days of January belong to the previous year."""
    d = dt.date.fromisoformat(end)
    return d.year - 1 if (d.month == 1 and d.day <= 10) else d.year


def quarterly(facts, tags, n=12):
    """{quarter_end: value} for the last n quarters (3-month values; Q4 = fiscal year minus the 9-month YTD)."""
    for tag in tags:
        ns, name = tag.split(":")
        units = (facts.get(ns, {}).get(name) or {}).get("units", {})
        if "USD" not in units:
            continue
        q, ytd9, ann = {}, {}, {}
        for f in units["USD"]:
            st, en = f.get("start"), f.get("end")
            if not st or not en:
                continue
            k = days(st, en)
            fd = f.get("filed", "")
            if 80 <= k <= 100:
                if en not in q or fd >= q[en][1]:
                    q[en] = (f["val"], fd)
            elif 255 <= k <= 290:
                ytd9[(st, en)] = f["val"]
            elif 350 <= k <= 380 and f.get("form") in ANNUAL_FORMS:
                ann[(st, en)] = f["val"]
        for (st, en), v in ann.items():
            if en in q:
                continue
            for (s9, e9), v9 in ytd9.items():
                if s9 == st and 80 <= days(e9, en) <= 100:
                    q[en] = (v - v9, "")
                    break
        if q and max(q) >= (dt.date.today() - dt.timedelta(days=400)).isoformat():
            ks = sorted(q)[-n:]
            out = {k: q[k][0] for k in ks}
            vs = sorted(abs(v) for v in out.values() if v is not None)
            med = vs[len(vs) // 2] if vs else 0
            for k in ks:
                v = out[k]
                if med and v is not None and abs(v) > 2.6 * med and len(vs) >= 6 and v > 0:
                    out[k] = None  # a full year tagged as one quarter
            return out
    return {}


def nearest(series, end, tol=20):
    if end in series:
        return series[end]
    for k, v in series.items():
        if abs(days(k, end)) <= tol:
            return v
    return None


def safe_div(a, b):
    try:
        if a is None or b in (None, 0):
            return None
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
                    if filed[key].get(end, "") < fd:
                        f *= r
                if f != 1.0 and series[key][end] is not None:
                    series[key][end] = series[key][end] * f if mult == 1 else series[key][end] / f
    ends = pick_fy_ends(series)
    if len(ends) < 2 or not series["revenue"]:
        return None
    has_debt = bool(series["debt_lt"] or series["debt_st"])
    has_capex = bool(series["capex"])
    rows = []
    for end in ends:
        g = lambda k: nearest(series[k], end)
        rev, ni, cfo = g("revenue"), g("net_income"), g("cfo")
        capex = g("capex")
        fcf = (cfo - abs(capex)) if (cfo is not None and capex is not None) else None
        op = g("op_income")
        if op is None and rev is not None and g("costs_expenses") is not None:
            op = rev - g("costs_expenses")
        tax, pretax = g("tax"), g("pretax_income")
        tax_rate = safe_div(tax, pretax)
        if tax_rate is None or tax_rate < 0 or tax_rate > 0.5:
            tax_rate = 0.21
        nopat = op * (1 - tax_rate) if op is not None else None
        debt_known = g("debt_lt") is not None or g("debt_st") is not None
        debt = (g("debt_lt") or 0) + (g("debt_st") or 0)
        ie0 = g("interest_exp")
        if not debt and not has_debt and g("assets") and (not ie0 or (rev and ie0 <= 0.002 * rev)):
            debt, debt_known = 0.0, True  # the company never reports any borrowings: debt-free
        cash = (g("cash") or 0) + (g("st_investments") or 0)
        equity = g("equity")
        invested = (equity + debt) if equity is not None else None
        if invested is not None and invested <= 0:
            invested = None
        gp = g("gross_profit")
        if gp is None and rev is not None and g("cogs") is not None:
            gp = rev - g("cogs")
        if op is None and gp is not None and g("opex") is not None:
            op = gp - g("opex")
            nopat = op * (1 - tax_rate)
        sh_d = g("shares_diluted") or g("shares_basic")
        eps = g("eps_diluted")
        if not sh_d and ni and eps:
            sh_d = abs(ni / eps)
        if eps is None and ni is not None and sh_d:
            eps = ni / sh_d
        liab = g("liabilities")
        if liab is None and g("liab_eq") is not None:
            eqt = g("equity_total") if g("equity_total") is not None else equity
            if eqt is not None:
                liab = g("liab_eq") - eqt
        if capex is None and not has_capex and cfo is not None:
            capex, fcf = 0.0, cfo  # no capital spending line at all (banks, insurers, asset managers)
        da = g("da")
        ebitda = (op + da) if (op is not None and da is not None) else None
        ie = g("interest_exp")
        ca, cl = g("current_assets"), g("current_liabilities")
        rows.append({
            "fy_end": end,
            "fy": fy_of(end),
            "revenue": rev, "gross_profit": gp, "op_income": op, "net_income": ni,
            "eps_diluted": eps, "shares_diluted": sh_d, "shares_out": g("shares_out"),
            "cfo": cfo, "capex": None if capex is None else abs(capex), "fcf": fcf,
            "sbc": g("sbc"), "dividends": g("dividends"), "buybacks": g("buybacks"),
            "rnd": g("rnd"), "da": da, "ebitda": ebitda, "interest_exp": ie,
            "assets": g("assets"), "liabilities": liab, "equity": equity,
            "cash": cash or None, "debt": debt if debt_known else None, "net_debt": (debt - cash) if (debt or cash) else None,
            "goodwill": g("goodwill"), "intangibles": g("intangibles"),
            "current_assets": ca, "current_liabilities": cl,
            # ratios
            "gross_margin": r4(safe_div(gp, rev)),
            "op_margin": r4(safe_div(op, rev)),
            "net_margin": r4(safe_div(ni, rev)),
            "fcf_margin": r4(safe_div(fcf, rev)),
            "ebitda_margin": r4(safe_div(ebitda, rev)),
            "roic": r4(safe_div(nopat, invested)),
            "roe": r4(safe_div(ni, equity)),
            "roa": r4(safe_div(ni, g("assets"))),
            "debt_to_equity": r4(safe_div(debt, equity)),
            "current_ratio": r4(safe_div(ca, cl)),
            "interest_cov": r4(safe_div(op, ie)) if (ie and ie > 0) else None,
            "nd_ebitda": r4(safe_div(debt - cash, ebitda)) if (ebitda and ebitda > 0) else None,
            "fcf_conv": r4(safe_div(fcf, ni)) if (ni and ni > 0) else None,
            "sbc_pct": r4(safe_div(g("sbc"), rev)),
            "payout": r4(safe_div((g("dividends") or 0) + (g("buybacks") or 0), fcf)) if (fcf and fcf > 0) else None,
            "fcf_per_share": r4(safe_div(fcf, sh_d)),
            "revenue_per_share": r4(safe_div(rev, sh_d)),
            "book_value_per_share": r4(safe_div(equity, sh_d)),
            "div_per_share": r4(safe_div(g("dividends"), sh_d)),
        })
    rows = [r for r in rows if r["revenue"] is not None or r["net_income"] is not None]
    dedup = {}
    for r in rows:
        dedup[r["fy"]] = r  # later fiscal-year end wins
    rows = [dedup[k] for k in sorted(dedup)]
    if len(rows) < 2:
        return None
    # growth rates
    for i, r in enumerate(rows):
        for k in ("revenue", "net_income", "fcf", "eps_diluted", "shares_diluted", "dividends"):
            prev = rows[i - 1][k] if i > 0 else None
            cur = r[k]
            r[k + "_growth"] = r4((cur - prev) / abs(prev)) if (prev not in (None, 0) and cur is not None) else None

    def cagr(key, n):
        if len(rows) <= n:
            return None
        a, b = rows[-1 - n][key], rows[-1][key]
        if a in (None, 0) or b is None or a < 0 or b < 0:
            return None
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
        summary[f"gross_margin_avg_{n}y"] = avg("gross_margin", n)
    for n in (3, 5):
        # share count change per year (negative = buybacks shrink the count)
        a = rows[-1 - n]["shares_diluted"] if len(rows) > n else None
        b = rows[-1]["shares_diluted"]
        summary[f"sh_cagr_{n}y"] = r4((b / a) ** (1 / n) - 1) if (a and b and a > 0 and b > 0) else None
    # margin trend: latest net margin minus the average of the 3 years before it
    prev_nm = [r["net_margin"] for r in rows[-4:-1] if r["net_margin"] is not None]
    summary["nm_trend"] = r4(rows[-1]["net_margin"] - sum(prev_nm) / len(prev_nm)) \
        if (prev_nm and rows[-1]["net_margin"] is not None) else None
    prev_om = [r["op_margin"] for r in rows[-4:-1] if r["op_margin"] is not None]
    summary["om_trend"] = r4(rows[-1]["op_margin"] - sum(prev_om) / len(prev_om)) \
        if (prev_om and rows[-1]["op_margin"] is not None) else None
    summary["profit_years"] = sum(1 for r in rows[-10:] if (r["net_income"] or 0) > 0)
    summary["fcf_pos_years"] = sum(1 for r in rows[-10:] if (r["fcf"] or 0) > 0)
    summary["div_years"] = sum(1 for r in rows[-10:] if (r["dividends"] or 0) > 0)
    summary["years"] = len(rows)
    last = rows[-1]
    # last 12 quarters of revenue and net income (charts on the stock page); USD filers only
    qrows = []
    if meta.get("currency", "USD") == "USD":
        qr = quarterly(facts, CONCEPTS["revenue"][1])
        qn = quarterly(facts, CONCEPTS["net_income"][1])
        for k in sorted(set(qr) | set(qn))[-12:]:
            qrows.append([k, qr.get(k), nearest(qn, k, 10) if qn else None])
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
        "quarterly": qrows,
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
                      "country": (row.get("country") or "").strip() or None,
                      "ipo": (row.get("ipoyear") or "").strip() or None}
        log("market rows:", len(out))
    except Exception as e:
        log("market data failed", e)
    # The screener's "lastsale" can lag several days. Overlay the near-live prices from the
    # quotes branch (quotes.py, every 15 min in market hours); market cap scales with price.
    try:
        url = "https://raw.githubusercontent.com/" + os.environ.get("GITHUB_REPOSITORY", "mrezahajilou-ops/stock-data") + "/quotes/quotes.json"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "stock-data-build"}), timeout=60) as r:
            q = json.loads(r.read()).get("q") or {}
        n = 0
        for t, v in q.items():
            m, p = out.get(t), (v[0] if v else None)
            if not m or not p or p <= 0:
                continue
            if m.get("price") and m.get("mcap"):
                m["mcap"] = m["mcap"] * p / m["price"]
            m["price"] = p
            n += 1
        log("live quotes applied:", n)
    except Exception as e:
        log("live quotes unavailable", e)
    return out


def clamp(x, a, b):
    return max(a, min(b, x))


def dcf_fair_mcap(rec):
    """Company-level fair value with the same default 'medium' assumptions as the DCF page."""
    s, last = rec["summary"], rec["annual"][-1]
    rev = last["revenue"]
    if not rev or rev <= 0:
        return None
    g = s.get("rev_cagr_5y") if s.get("rev_cagr_5y") is not None else s.get("rev_cagr_1y")
    g = clamp((g if g is not None else 0.05) * 0.8, -0.05, 0.25)
    pm = s.get("net_margin_avg_5y") if s.get("net_margin_avg_5y") is not None else last.get("net_margin")
    if pm is None or pm < 0.02:
        pm = last.get("net_margin") if (last.get("net_margin") or 0) > 0.02 else 0.08
    fm = s.get("fcf_margin_avg_5y") if s.get("fcf_margin_avg_5y") is not None else last.get("fcf_margin")
    if fm is None or fm < 0.02:
        fm = pm
    pm, fm = clamp(pm, 0.02, 0.5), clamp(fm, 0.02, 0.55)
    rev10 = rev * (1 + g) ** 10
    return ((rev10 * pm * 22) + (rev10 * fm * 22)) / 2 / (1.10 ** 10)


def pts(*checks):
    """Each check is True/False/None. Score = passed checks (0-5); None = not enough data (counts as fail)."""
    return sum(1 for c in checks if c is True)


def score(rec, mk, sector_pe):
    """Five 0-5 scores. Also returns the individual checks (as 1/0) so the site can explain WHY."""
    a, s = rec["annual"], rec["summary"]
    last = a[-1]
    prev3 = a[-4] if len(a) >= 4 else None
    rev, ni, fcf = last["revenue"], last["net_income"], last["fcf"]
    mcap = (mk or {}).get("mcap")
    pe = mcap / ni if (mcap and ni and ni > 0) else None
    pfcf = mcap / fcf if (mcap and fcf and fcf > 0) else None
    ps = mcap / rev if (mcap and rev and rev > 0) else None
    pb = mcap / last["equity"] if (mcap and last.get("equity") and last["equity"] > 0) else None
    eg = s.get("eps_cagr_5y") if s.get("eps_cagr_5y") is not None else s.get("ni_cagr_5y")
    peg = pe / (eg * 100) if (pe and eg and eg > 0) else None
    fair = dcf_fair_mcap(rec)
    spe = sector_pe.get((mk or {}).get("sector"))
    debt, cash = last.get("debt") or 0, last.get("cash") or 0
    ev = (mcap + debt - cash) if mcap else None
    ebitda = last.get("ebitda")
    ev_ebitda = ev / ebitda if (ev and ebitda and ebitda > 0) else None
    fcf_yield = fcf / mcap if (mcap and fcf is not None) else None
    earn_yield = ni / mcap if (mcap and ni is not None) else None

    v_checks = [pe is not None and pe < 25,
                pe is not None and spe is not None and pe < spe,
                pfcf is not None and pfcf < 20,
                fair is not None and mcap is not None and fair > mcap,
                peg is not None and peg < 1.5] if mcap else None
    value = pts(*v_checks) if v_checks else None

    nm_hist = [r["net_margin"] for r in a[-3:] if r["net_margin"] is not None]
    f_checks = [(last.get("revenue_growth") or 0) > 0.10,
                (s.get("rev_cagr_3y") or 0) > 0.10,
                bool(nm_hist) and last["net_margin"] is not None and last["net_margin"] > sum(nm_hist) / len(nm_hist),
                (s.get("fcf_cagr_3y") or 0) > 0.10,
                bool(rev and last.get("rnd") is not None and last["rnd"] / rev > 0.05) or (last.get("revenue_growth") or 0) > 0.20]
    future = pts(*f_checks)

    p_checks = [(s.get("eps_cagr_5y") or 0) > 0.10,
                (s.get("rev_cagr_5y") or 0) > 0.08,
                (s.get("roic_avg_5y") or 0) > 0.12,
                len(a) >= 5 and all((r["net_income"] or -1) > 0 for r in a[-5:]),
                (last.get("roe") or 0) > 0.15]
    past = pts(*p_checks)

    eq = last.get("equity")
    op, ie = last.get("op_income"), last.get("interest_exp")
    h_checks = [cash >= debt or bool(eq and eq > 0 and debt / eq < 0.5),
                fcf is not None and fcf > 0,
                debt == 0 or bool(op is not None and ie and ie > 0 and op / ie > 5) or bool(op and op > 0 and not ie),
                debt == 0 or bool(fcf is not None and fcf > 0 and debt / fcf < 3),
                bool(last.get("assets")) and last.get("liabilities") is not None and last["liabilities"] / last["assets"] < 0.6]
    health = pts(*h_checks)

    divs = [r.get("dividends") for r in a[-3:]]
    sh_now, sh_3 = last.get("shares_diluted"), (prev3 or {}).get("shares_diluted")
    returned = (last.get("dividends") or 0) + (last.get("buybacks") or 0)
    c_checks = [(last.get("dividends") or 0) > 0,
                bool(sh_now and sh_3) and sh_now < sh_3 * 0.99,
                fcf is not None and fcf > 0 and 0.2 <= returned / fcf <= 1.0,
                len(divs) == 3 and all((d or 0) > 0 for d in divs),
                bool(rev and last.get("sbc") is not None and last["sbc"] / rev < 0.05)]
    capital = pts(*c_checks)

    parts = [x for x in (value, future, past, health, capital) if x is not None]
    total = round(sum(parts) / len(parts), 1) if parts else None
    divy = (last.get("dividends") or 0) / mcap if mcap else None
    buyback_y = (last.get("buybacks") or 0) / mcap if mcap else None
    checks = {"value": [int(bool(c)) for c in v_checks] if v_checks else None,
              "future": [int(bool(c)) for c in f_checks], "past": [int(bool(c)) for c in p_checks],
              "health": [int(bool(c)) for c in h_checks], "capital": [int(bool(c)) for c in c_checks]}
    scores = {"value": value, "future": future, "past": past, "health": health, "capital": capital, "total": total}
    ratios = {"pe": pe, "pfcf": pfcf, "ps": ps, "pb": pb, "peg": peg, "fair_mcap": fair, "div_yield": divy,
              "buyback_yield": buyback_y, "shareholder_yield": (divy or 0) + (buyback_y or 0) if mcap else None,
              "ev": ev, "ev_ebitda": ev_ebitda, "fcf_yield": fcf_yield, "earnings_yield": earn_yield,
              "sector_pe": spe}
    return scores, ratios, checks


SCREENER_COLS = ["t", "n", "sector", "industry", "price", "mcap", "pe", "pfcf", "ps", "divy",
                 "revg1", "revg5", "nm", "fm", "roic", "de",
                 "s_value", "s_future", "s_past", "s_health", "s_capital", "s_total", "rev", "cur",
                 # v2 columns
                 "revg3", "epsg5", "fcfg3", "gm", "om", "roe", "ev_ebitda", "fcf_yield", "peg", "pb",
                 "nd_ebitda", "int_cov", "sh_chg3", "sbc_pct", "nm_trend", "shy", "profit_yrs", "div_yrs",
                 "fcf_conv", "fair_up", "years"]


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
    first = {}
    for r in recs:
        multi[r["cik"]] += 1
        first.setdefault(r["cik"], r["ticker"])   # SEC usually lists a company's main common stock first
    # ...but not always (BIPH note before BIP, LUCYW warrant before LUCY): if another ticker of the
    # same company is a prefix of the chosen one and has market data, it is the real common stock.
    for r in recs:
        f = first[r["cik"]]
        t = r["ticker"]
        if t != f and f.startswith(t) and len(t) < len(f) and (market.get(t) or {}).get("mcap"):
            first[r["cik"]] = t

    def mc(t):
        return (market.get(t) or {}).get("mcap") or 0

    def keep(r):
        if multi[r["cik"]] == 1:
            return True
        ref = mc(first[r["cik"]])
        if ref:
            # main listing always stays; other classes only when their market cap matches it
            # (GOOG next to GOOGL). Notes / preferreds / warrants often carry a bogus screener
            # market cap (CCZ next to Comcast's CMCSA) and must not replace the common stock.
            return r["ticker"] == first[r["cik"]] or 0.5 * ref <= mc(r["ticker"]) <= 1.5 * ref
        m = mc(r["ticker"])
        return best[r["cik"]] == 0 or m >= 0.5 * best[r["cik"]]

    dropped = [r["ticker"] for r in recs if not keep(r)]
    # alias every dropped ticker to the company's main listing, so a search for e.g. GOOGM
    # opens Alphabet (GOOGL) instead of "not found"
    primary = {}
    for r in recs:
        if not keep(r):
            continue
        m = mc(r["ticker"])
        if mc(first[r["cik"]]):
            primary[r["cik"]] = (first[r["cik"]], m)
        elif r["cik"] not in primary or m > primary[r["cik"]][1]:
            primary[r["cik"]] = (r["ticker"], m)
    aliases = {r["ticker"]: primary[r["cik"]][0] for r in recs if not keep(r) and r["cik"] in primary}
    alias_names = {r["ticker"]: r["name"] for r in recs if not keep(r)}
    recs = [r for r in recs if keep(r)]
    log("dropped secondary instruments:", len(dropped), dropped[:20])
    with open(os.path.join(OUT, "aliases.json"), "w") as f:
        json.dump(aliases, f, separators=(",", ":"))

    SECTOR_FIX = {"BRK-A": ("Finance", "Property-Casualty Insurers"), "BRK-B": ("Finance", "Property-Casualty Insurers"),
                  "KSPI": ("Finance", "Major Banks")}
    for t, (sec, ind) in SECTOR_FIX.items():
        if t in market and not market[t].get("sector"):
            market[t]["sector"], market[t]["industry"] = sec, ind
    PS_FIELDS = ("eps_diluted", "fcf_per_share", "revenue_per_share", "book_value_per_share", "div_per_share")
    CAND = [1e6, 1000, 100, 50, 40, 30, 25, 20, 15, 10, 8, 6, 5, 4, 3, 2, 1 / 2, 1 / 3, 1 / 4, 1 / 5, 1 / 6, 1 / 8, 1 / 10,
            1 / 15, 1 / 20, 1 / 25, 1 / 30, 1 / 40, 1 / 50, 1 / 100, 1 / 1000]
    fixed = []
    for r in recs:
        mk = market.get(r["ticker"]) or {}
        last = r["annual"][-1]
        if not (mk.get("mcap") and mk.get("price")):
            continue
        implied = mk["mcap"] / mk["price"]   # shares (or ADS) the market price refers to
        sh = last.get("shares_diluted")
        if not sh:
            # no share count in the filings (Berkshire's class-A equivalents): use the market's for the latest year
            if last.get("net_income") is not None:
                last["shares_diluted"] = implied
                last["eps_diluted"] = r4(last["net_income"] / implied)
                for k, src in (("fcf_per_share", "fcf"), ("revenue_per_share", "revenue"), ("book_value_per_share", "equity"),
                               ("div_per_share", "dividends")):
                    last[k] = r4(safe_div(last.get(src), implied))
                fixed.append(r["ticker"])
            continue
        k = implied / sh
        if 0.87 <= k <= 1.15:
            continue
        n = next((c for c in CAND if abs(k / c - 1) < (0.12 if c in (1000, 1e6) else 0.06)), None)
        if not n:
            continue
        prev = r["annual"][-2].get("shares_diluted") if len(r["annual"]) > 1 else None
        if n > 1 and prev and sh / prev > 1.3 and n not in (1000, 1e6):
            continue  # share count is exploding through issuance (crypto treasuries etc.), not a split
        # ADRs (one ADS = several ordinary shares) and filers that report shares in thousands:
        # restate share counts and per-share values in the units the market price is quoted in
        for row in r["annual"]:
            for f in ("shares_diluted", "shares_out"):
                if row.get(f):
                    row[f] = row[f] * n
            for f in PS_FIELDS:
                if f == "eps_diluted" and n in (1e6, 1000):
                    continue  # EPS was reported correctly, only the share count had the wrong unit
                if row.get(f) is not None:
                    row[f] = r4(row[f] / n)
        r["share_factor"] = n
        fixed.append(r["ticker"])
    for r in recs:
        last = r["annual"][-1]
        r["latest"].update({k: last.get(k) for k in ("eps_diluted", "shares_diluted", "shares_out")})
    log("per-share fixes (ADR ratio / missing shares):", len(fixed), fixed[:25])

    index, screener = [], []
    for r in recs:
        mk = market.get(r["ticker"]) or {}
        sc, ratios, checks = score(r, mk, sector_pe)
        r["market"] = {"price": mk.get("price"), "mcap": mk.get("mcap"), "sector": mk.get("sector"),
                       "industry": mk.get("industry"), "country": mk.get("country"), "ipo": mk.get("ipo"),
                       "as_of": dt.date.today().isoformat()}
        r["ratios"] = {k: r4(v) for k, v in ratios.items()}
        r["scores"] = sc
        r["checks"] = checks
        with open(os.path.join(OUT, "stocks", f"{r['ticker']}.json"), "w") as f:
            json.dump(r, f, separators=(",", ":"))
        last, s = r["annual"][-1], r["summary"]
        index.append({"t": r["ticker"], "n": r["name"], "rev": last["revenue"]})
        fair_up = (ratios["fair_mcap"] / mk["mcap"] - 1) if (ratios.get("fair_mcap") and mk.get("mcap")) else None
        screener.append([r["ticker"], r["name"], mk.get("sector"), mk.get("industry"),
                         mk.get("price"), mk.get("mcap"),
                         r4(ratios["pe"]), r4(ratios["pfcf"]), r4(ratios["ps"]), r4(ratios["div_yield"]),
                         r4(last.get("revenue_growth")), s.get("rev_cagr_5y"), last.get("net_margin"),
                         last.get("fcf_margin"), last.get("roic"), last.get("debt_to_equity"),
                         sc["value"], sc["future"], sc["past"], sc["health"], sc["capital"], sc["total"],
                         last["revenue"], r.get("reported_currency", "USD"),
                         s.get("rev_cagr_3y"), s.get("eps_cagr_5y"), s.get("fcf_cagr_3y"),
                         last.get("gross_margin"), last.get("op_margin"), last.get("roe"),
                         r4(ratios["ev_ebitda"]), r4(ratios["fcf_yield"]), r4(ratios["peg"]), r4(ratios["pb"]),
                         last.get("nd_ebitda"), last.get("interest_cov"), s.get("sh_cagr_3y"), last.get("sbc_pct"),
                         s.get("nm_trend"), r4(ratios["shareholder_yield"]), s.get("profit_years"), s.get("div_years"),
                         last.get("fcf_conv"), r4(fair_up), s.get("years")])
    index.sort(key=lambda x: -(x["rev"] or 0))
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump([{"t": x["t"], "n": x["n"]} for x in index] +
                  [{"t": a, "n": alias_names.get(a, ""), "a": p} for a, p in sorted(aliases.items())],
                  f, separators=(",", ":"))
    screener.sort(key=lambda x: -(x[5] or 0))
    with open(os.path.join(OUT, "screener.json"), "w") as f:
        json.dump({"cols": SCREENER_COLS, "as_of": dt.date.today().isoformat(), "rows": screener},
                  f, separators=(",", ":"))
    # sector / industry medians for the "compared to sector" view
    med = defaultdict(lambda: defaultdict(list))
    ci = {c: i for i, c in enumerate(SCREENER_COLS)}
    for row in screener:
        sec = row[ci["sector"]]
        if not sec:
            continue
        for k in ("pe", "pfcf", "ps", "ev_ebitda", "nm", "gm", "roic", "revg1", "divy", "fcf_yield", "de"):
            v = row[ci[k]]
            if v is not None and isinstance(v, (int, float)):
                med[sec][k].append(v)
    with open(os.path.join(OUT, "sectors.json"), "w") as f:
        json.dump({sec: {k: r4(sorted(v)[len(v) // 2]) for k, v in d.items() if len(v) >= 10}
                   for sec, d in med.items()}, f, separators=(",", ":"))
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
            if not chunk:
                break
            f.write(chunk)
    log("downloaded", os.path.getsize(zpath) // 1_000_000, "MB")
    zf = zipfile.ZipFile(zpath)

    import shutil
    shutil.rmtree(os.path.join(OUT, "stocks"), ignore_errors=True)
    os.makedirs(os.path.join(OUT, "stocks"), exist_ok=True)
    load_fx()
    market = load_market()
    recs, done, skipped = [], 0, 0
    seen_cik, why = set(), {}
    for name in zf.namelist():
        m = re.match(r"CIK(\d+)\.json$", name)
        if not m:
            continue
        cik = int(m.group(1))
        if cik not in by_cik:
            continue
        if LIMIT and done >= LIMIT:
            break
        try:
            doc = json.loads(zf.read(name))
        except Exception as e:
            log("bad json", name, e)
            continue
        facts = doc.get("facts", {})
        seen_cik.add(cik)
        for entry in by_cik[cik]:
            # one listing can have several share classes (GOOGL/GOOG): same data, both tickers
            try:
                rec = build_company(cik, entry, facts)
            except Exception as e:
                log("build error", entry["ticker"], repr(e)[:200])
                why[entry["ticker"]] = "error: " + repr(e)[:120]
                rec = None
            if not rec:
                skipped += 1
                why.setdefault(entry["ticker"], "no usable annual data")
                continue
            recs.append(rec)
            done += 1
            if done % 500 == 0 and done:
                log("processed", done)

    # large listed companies that did not make it into the data set, with the reason (data/missing.json)
    built = {r["ticker"] for r in recs}
    t2cik = {e["ticker"]: c for c, es in by_cik.items() for e in es}
    miss = []
    for t, mk in market.items():
        if (mk.get("mcap") or 0) < 2e9 or t in built:
            continue
        reason = why.get(t) or ("not in SEC ticker map" if t not in t2cik else
                               ("no companyfacts file" if t2cik[t] not in seen_cik else "unknown"))
        miss.append({"t": t, "mcap": round(mk["mcap"]), "why": reason, "cik": t2cik.get(t)})
    miss.sort(key=lambda x: -x["mcap"])
    with open(os.path.join(OUT, "missing.json"), "w") as f:
        json.dump(miss, f, indent=0)
    log("large companies missing:", len(miss), [(m["t"], m["why"]) for m in miss[:30]])
    finish(recs, market)
    with open(os.path.join(OUT, "meta.json"), "w") as f:
        json.dump({"built": dt.datetime.now(dt.timezone.utc).isoformat(), "stocks": done, "skipped": skipped,
                   "source": "SEC EDGAR", "version": 2}, f)
    log("done. stocks:", done, "skipped (no usable annual data):", skipped)


if __name__ == "__main__":
    main()
