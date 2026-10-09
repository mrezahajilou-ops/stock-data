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
LIMIT = int(os.environ.get("LIMIT", "0"))
# new holding companies that took over a listed company's ticker: CIK -> predecessor CIK with the history
PREDECESSOR = {2115436: 34088}  # ExxonMobil Holdings Corp (2026) <- Exxon Mobil Corp  # for testing: process only N companies

# ---- concept fallbacks: first tag with data wins (per fiscal year) ----
# (kind: 'dur' = duration/flow over the year, 'inst' = instant/balance at FY end)
CONCEPTS = {
    "revenue": ("dur", [
        "us-gaap:RevenuesNetOfInterestExpense",  # banks / card issuers: total net revenue (American Express, JPMorgan)
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax",
        "us-gaap:SalesRevenueNet",
        "us-gaap:SalesRevenueGoodsNet",
        "us-gaap:SalesRevenueServicesNet",
        "us-gaap:InterestAndDividendIncomeOperating",
        "ifrs-full:Revenue",
        "ifrs-full:RevenueFromContractsWithCustomers",
        "ifrs-full:RevenueAndOperatingIncome",
        "ifrs-full:RevenueFromSaleOfGoods",
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
                      "us-gaap:PaymentsToExploreAndDevelopOilAndGasProperties",
                      "us-gaap:PaymentsToAcquireOilAndGasProperty",
                      "ifrs-full:PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets"]),
    "sbc": ("dur", ["us-gaap:ShareBasedCompensation", "us-gaap:AllocatedShareBasedCompensationExpense",
                    "ifrs-full:AdjustmentsForSharebasedPayments"]),
    "dividends": ("dur", ["us-gaap:PaymentsOfDividendsCommonStock", "us-gaap:PaymentsOfDividends",
                          "ifrs-full:DividendsPaidClassifiedAsFinancingActivities", "us-gaap:PaymentsOfOrdinaryDividends",
                          "us-gaap:DividendsCommonStockCash", "us-gaap:DividendsCommonStock",
                          "ifrs-full:DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities", "ifrs-full:DividendsPaid",
                          "us-gaap:DividendsCash"]),
    "buybacks": ("dur", ["us-gaap:PaymentsForRepurchaseOfCommonStock",
                         "ifrs-full:PaymentsToAcquireOrRedeemEntitysShares", "us-gaap:PaymentsForRepurchaseOfEquity"]),
    "rnd": ("dur", ["us-gaap:ResearchAndDevelopmentExpense",
                    "us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]),
    "da": ("dur", ["us-gaap:DepreciationDepletionAndAmortization", "us-gaap:DepreciationAndAmortization",
                   "us-gaap:DepreciationAmortizationAndAccretionNet",
                   "ifrs-full:DepreciationAndAmortisationExpense",
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
                                "us-gaap:AvailableForSaleSecuritiesDebtSecuritiesCurrent", "us-gaap:DebtSecuritiesCurrent",
                                "us-gaap:HeldToMaturitySecuritiesCurrent", "ifrs-full:CurrentInvestments"]),
    # long-term debt WITHOUT the current portion
    "debt_lt": ("inst", ["us-gaap:LongTermDebtNoncurrent", "us-gaap:LongTermDebtAndCapitalLeaseObligations",
                         "us-gaap:LongTermNotesPayable", "us-gaap:SeniorLongTermNotes", "us-gaap:ConvertibleDebtNoncurrent",
                         "us-gaap:UnsecuredLongTermDebt", "us-gaap:SecuredLongTermDebt", "us-gaap:OtherLongTermDebtNoncurrent",
                         "us-gaap:LongTermLineOfCredit", "ifrs-full:LongtermBorrowings",
                         "ifrs-full:NoncurrentPortionOfNoncurrentBorrowings"]),
    # total debt tags (already include the current portion)
    "debt_total": ("inst", ["us-gaap:DebtLongtermAndShorttermCombinedAmount",
                            "us-gaap:LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", "us-gaap:LongTermDebt",
                            "ifrs-full:Borrowings", "ifrs-full:NoncurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings",
                            "us-gaap:SeniorNotes", "us-gaap:NotesPayable", "us-gaap:ConvertibleNotesPayable",
                            "us-gaap:DebtInstrumentCarryingAmount"]),
    "debt_st": ("inst", ["us-gaap:LongTermDebtCurrent", "us-gaap:DebtCurrent", "us-gaap:ShortTermBorrowings",
                         "us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent", "ifrs-full:ShorttermBorrowings",
                         "ifrs-full:CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings", "us-gaap:CommercialPaper",
                         "us-gaap:NotesPayableCurrent", "us-gaap:ConvertibleNotesPayableCurrent", "us-gaap:LinesOfCreditCurrent"]),
    "goodwill": ("inst", ["us-gaap:Goodwill", "ifrs-full:Goodwill"]),
    "intangibles": ("inst", ["us-gaap:IntangibleAssetsNetExcludingGoodwill",
                             "ifrs-full:IntangibleAssetsOtherThanGoodwill"]),
    "current_assets": ("inst", ["us-gaap:AssetsCurrent", "ifrs-full:CurrentAssets"]),
    "current_liabilities": ("inst", ["us-gaap:LiabilitiesCurrent", "ifrs-full:CurrentLiabilities"]),
    "ppe": ("inst", ["us-gaap:PropertyPlantAndEquipmentNet",
                     "us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
                     "ifrs-full:PropertyPlantAndEquipment"]),
    "dep": ("dur", ["us-gaap:Depreciation"]),
    "amort": ("dur", ["us-gaap:AmortizationOfIntangibleAssets"]),
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
        # pick the unit with the most recent annual data: foreign filers sometimes add a USD
        # convenience translation for one old year next to their full home-currency history (SAP)
        def latest_end(u):
            return max((f.get("end", "") for f in units[u] if f.get("form") in ANNUAL_FORMS), default="")
        cands = [u for u in ("USD", "shares", "USD/shares") if u in units]
        cands += [u for u in units if CUR_RE.match(u) and CUR_RE.match(u).group(1) != "USD"]
        if not cands:
            continue
        usd = [u for u in ("USD", "shares", "USD/shares") if u in units]
        unit_key = usd[0] if usd else None
        other = [u for u in cands if u not in usd]
        if other:
            best_other = max(other, key=latest_end)
            # a foreign currency only wins when USD is missing or clearly stale (SAP: USD for one old year only);
            # never because of a single foreign-currency debt line (Oracle's yen bonds)
            if unit_key is None or (latest_end(best_other)[:4] and int(latest_end(best_other)[:4] or 0) - int(latest_end(unit_key)[:4] or 0) >= 2):
                unit_key = best_other
        cur = "USD"
        m = CUR_RE.match(unit_key)
        if m and m.group(1) != "USD":
            cur = m.group(1)
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
            if meta is not None:
                meta.setdefault("forms", set()).add(f.get("form"))
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


QFORMS = {"10-Q", "10-Q/A", "10-K", "10-K/A", "10-KT"}


def quarterly(facts, tags, n=12, unit="USD"):
    """{quarter_end: value} for the last n fiscal quarters (USD filers).
    3-month values are taken directly when tagged, otherwise derived from the year-to-date figures
    (cash-flow items are only reported YTD): Q2 = 6M - 3M, Q3 = 9M - 6M, Q4 = 12M - 9M."""
    for tag in tags:
        ns, name = tag.split(":")
        units = (facts.get(ns, {}).get(name) or {}).get("units", {})
        if unit not in units:
            continue
        direct, cum = {}, {}
        for f in units[unit]:
            st, en = f.get("start"), f.get("end")
            if not st or not en or f.get("form") not in QFORMS:
                continue  # proxy statements (DEF 14A) and 8-Ks sometimes repeat figures in the wrong unit
            k = days(st, en)
            fd = f.get("filed", "")
            if 80 <= k <= 115:  # 12- and 16-week quarters too (PepsiCo)
                if en not in direct or fd >= direct[en][1]:
                    direct[en] = (f["val"], fd)
            if k >= 350 and not f.get("form", "").startswith("10-K"):
                continue  # a full year inside a 10-Q is a tagging error (Comfort Systems), not a YTD figure
            if 80 <= k <= 115 or 165 <= k <= 200 or 245 <= k <= 290 or 350 <= k <= 380:
                key = (st, en)
                if key not in cum or fd >= cum[key][1]:
                    cum[key] = (f["val"], fd)
        q = {en: v for en, (v, _) in direct.items()}
        annual_ends = {}
        by_start = defaultdict(list)
        for (st, en), (v, _) in cum.items():
            by_start[st].append((en, v))
            if 350 <= days(st, en) <= 380:
                annual_ends[en] = v
        derived = {}
        for st, rows in by_start.items():
            rows.sort()
            for (e0, v0), (e1, v1) in zip(rows, rows[1:]):
                if 80 <= days(e0, e1) <= 115:
                    derived[e1] = v1 - v0
        for en, v in derived.items():
            if en not in q:
                q[en] = v
            elif en in annual_ends and annual_ends[en] and abs(q[en] / annual_ends[en] - 1) < 0.03:
                q[en] = v  # a full year tagged as the 4th quarter (L3Harris 2025)
        if q and max(q) >= (dt.date.today() - dt.timedelta(days=400)).isoformat():
            ks = sorted(q)[-n:]
            out = {k: q[k] for k in ks}
            # a full year tagged as one quarter with no way to derive it: several times both neighbours
            for i in range(1, len(ks) - 1):
                a, v, b = out[ks[i - 1]], out[ks[i]], out[ks[i + 1]]
                if ks[i] in direct and ks[i] not in derived and a and b and v and a > 0 and b > 0 and v > 2.5 * max(a, b):
                    out[ks[i]] = None
            return out
    return {}


def latest_inst(facts, tags, after=""):
    """Most recent balance-sheet value (10-Q or 10-K), USD only: (value, end). Tags are tried in priority order;
    a lower-priority tag is only used when it is more recent than everything found so far."""
    best = (None, "")
    for tag in tags:
        ns, name = tag.split(":")
        arr = ((facts.get(ns, {}).get(name) or {}).get("units", {}) or {}).get("USD") or []
        cand = (None, "")
        for f in arr:
            if f.get("start") or f.get("form") not in QFORMS:
                continue
            en = f.get("end", "")
            if en >= after and (en > cand[1] or (en == cand[1] and f.get("filed", "") >= cand_f)):
                cand, cand_f = (f["val"], en), f.get("filed", "")
            if cand[0] is None:
                cand_f = ""
        if cand[0] is not None and (best[0] is None or days(best[1], cand[1]) > 10):
            best = cand
    return best


# revenue tags that can each be the company's TOTAL revenue (not a component): the largest one per period wins
REV_TOTAL = ["us-gaap:RevenuesNetOfInterestExpense", "us-gaap:Revenues", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
             "us-gaap:SalesRevenueNet", "us-gaap:SalesRevenueGoodsNet", "us-gaap:RegulatedAndUnregulatedOperatingRevenue",
             "us-gaap:ElectricUtilityRevenue", "us-gaap:OperatingLeaseLeaseIncome", "us-gaap:OperatingLeasesIncomeStatementLeaseRevenue",
             "us-gaap:RealEstateRevenueNet", "us-gaap:HealthCareOrganizationRevenue", "ifrs-full:Revenue",
             "ifrs-full:RevenueAndOperatingIncome"]
BANK_NII, BANK_NONII = "us-gaap:InterestIncomeExpenseNet", "us-gaap:NoninterestIncome"


def revenue_max(per_tag):
    """per_tag: list of {end: value}. Max per period end (ends within 10 days are the same period)."""
    out = {}
    for d in per_tag:
        for e, v in d.items():
            if v is None:
                continue
            k = next((x for x in out if abs(days(x, e)) <= 10), e)
            if out.get(k) is None or v > out[k]:
                out[k] = v
    return out


def ttm_tags(facts, tags):
    """TTM from the first tag that has four consecutive recent quarters (companies switch tags over time)."""
    best = (None, None)
    for tag in tags:
        v, e = ttm(quarterly(facts, [tag]))
        if v is not None and (best[1] is None or e > best[1]):
            best = (v, e)
    return best


def ttm(qs):
    """Sum of the last four quarters if they are consecutive."""
    ks = sorted(k for k, v in qs.items() if v is not None)
    if len(ks) < 4:
        return None, None
    last4 = ks[-4:]
    if not (250 <= days(last4[0], last4[-1]) <= 290):
        return None, None
    return sum(qs[k] for k in last4), last4[-1]


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
        series[key], filed[key], hist[key] = annual_series(facts, tags, kind, meta if key in ("revenue", "net_income", "assets", "cfo", "equity") else {})
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
    if len(ends) < 2 or not (series["revenue"] or series["net_income"]):
        return None
    has_debt = bool(series["debt_lt"] or series["debt_st"] or series["debt_total"])
    # total revenue: a high-priority tag can hold only a component (fee income of a bank or REIT, Owl Rock's
    # "Revenues"), so take the largest total-revenue tag per year; banks: net interest income + non-interest income
    alts = [annual_series(facts, [tg], "dur", {})[0] for tg in REV_TOTAL]
    nii, nonii = annual_series(facts, [BANK_NII], "dur", {})[0], annual_series(facts, [BANK_NONII], "dur", {})[0]
    bank = {e: v + nearest(nonii, e) for e, v in nii.items() if nearest(nonii, e) is not None}
    best = revenue_max(alts)
    for e, v in best.items():
        cur = nearest(series["revenue"], e)
        if cur is None or v > cur * 1.02:
            k = next((x for x in series["revenue"] if abs(days(x, e)) <= 20), e)
            series["revenue"][k] = v
    # banks: revenue = net interest income + non-interest income (gross interest income is not revenue)
    netrev = alts[0]
    for e, v in bank.items():
        k = next((x for x in series["revenue"] if abs(days(x, e)) <= 20), e)
        series["revenue"][k] = max(v, nearest(netrev, e) or 0)
    has_capex = bool(series["capex"])
    pays_div = bool(series["dividends"])
    rows = []
    for end in ends:
        g = lambda k: nearest(series[k], end)
        rev, ni, cfo = g("revenue"), g("net_income"), g("cfo")
        if rev is not None and ni is not None and ni > 0 and rev < 0.5 * ni:
            rev = None  # a partial revenue line (e.g. a bank's "sale of goods"), not total revenue
        capex = g("capex")
        fcf = (cfo - abs(capex)) if (cfo is not None and capex is not None) else None
        op = g("op_income")
        if op is None and rev is not None and g("costs_expenses") is not None:
            op = rev - g("costs_expenses")
        if op is None and rev is not None and g("pretax_income") is not None and g("cogs") is not None:
            op = g("pretax_income") + (g("interest_exp") or 0)  # EBIT for companies without an operating income line
        tax, pretax = g("tax"), g("pretax_income")
        tax_rate = safe_div(tax, pretax)
        if tax_rate is None or tax_rate < 0 or tax_rate > 0.5:
            tax_rate = 0.21
        nopat = op * (1 - tax_rate) if op is not None else None
        debt_known = g("debt_lt") is not None or g("debt_st") is not None or g("debt_total") is not None
        debt = max((g("debt_lt") or 0) + (g("debt_st") or 0), g("debt_total") or 0)
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
        ppe = g("ppe")
        A0, L0 = g("assets"), (g("liabilities") or (g("liab_eq") - (g("equity_total") or equity or 0) if g("liab_eq") else None))
        financial = bool(A0 and L0 and L0 / A0 > 0.8)  # banks, insurers, mortgage REITs: balance sheet is mostly liabilities
        asset_light = (ppe is not None and A0 and ppe < 0.05 * A0) or (ppe is None and financial)
        if capex is None and not has_capex and cfo is not None and asset_light:
            capex, fcf = 0.0, cfo  # no capital spending line at all (banks, insurers, asset managers)
        da = g("da")
        if da is None and g("dep") is not None:
            da = g("dep") + (g("amort") or 0)  # depreciation and intangible amortization reported separately (AMD)
        ebitda = (op + da) if (op is not None and da is not None) else None
        ie = g("interest_exp")
        ca, cl = g("current_assets"), g("current_liabilities")
        rows.append({
            "fy_end": end,
            "fy": fy_of(end),
            "revenue": rev, "gross_profit": gp, "op_income": op, "net_income": ni,
            "eps_diluted": eps, "shares_diluted": sh_d, "shares_out": g("shares_out"),
            "cfo": cfo, "capex": None if capex is None else abs(capex), "fcf": fcf,
            "sbc": g("sbc"), "dividends": g("dividends") if pays_div else (0.0 if ni is not None else None), "buybacks": g("buybacks"),
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
            "div_per_share": r4(safe_div(g("dividends"), sh_d)) if pays_div else (0.0 if sh_d else None),
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
    qrows, ttm_rec, bs = [], None, None
    if meta.get("currency", "USD") == "USD":
        # latest balance sheet (most recent 10-Q), used for P/B and enterprise value
        eq, e_eq = latest_inst(facts, CONCEPTS["equity"][1], last["fy_end"])
        if e_eq and e_eq > last["fy_end"]:
            near = lambda e: bool(e) and abs(days(e, e_eq)) <= 10
            c, e_c = latest_inst(facts, CONCEPTS["cash"][1], last["fy_end"])
            si, e_si = latest_inst(facts, CONCEPTS["st_investments"][1], last["fy_end"])
            dl, e_dl = latest_inst(facts, CONCEPTS["debt_lt"][1], last["fy_end"])
            ds, e_ds = latest_inst(facts, CONCEPTS["debt_st"][1], last["fy_end"])
            dt_, e_dt = latest_inst(facts, CONCEPTS["debt_total"][1], last["fy_end"])
            bs = {"end": e_eq, "equity": eq,
                  "cash": ((c or 0) if near(e_c) else 0) + ((si or 0) if near(e_si) else 0) or None,
                  "debt": max(((dl or 0) + ((ds or 0) if near(e_ds) else 0)) if near(e_dl) else 0,
                              ((dt_ or 0) if near(e_dt) else 0)) if (near(e_dl) or near(e_dt)) else None}
            if not near(e_c):
                bs["cash"] = None
        qr = quarterly(facts, CONCEPTS["revenue"][1])
        q_alts = [quarterly(facts, [tg]) for tg in REV_TOTAL]
        q_nii, q_non = quarterly(facts, [BANK_NII]), quarterly(facts, [BANK_NONII])
        q_bank = {e: v + q_non[e] for e, v in q_nii.items() if v is not None and q_non.get(e) is not None}
        qbest = revenue_max(q_alts)
        for e, v in qbest.items():
            k = next((x for x in qr if abs(days(x, e)) <= 10), None)
            if k is None:
                if qr and e >= min(qr):
                    qr[e] = v
            elif qr[k] is None or v > qr[k] * 1.02:
                qr[k] = v
        for e, v in q_bank.items():
            k = next((x for x in qr if abs(days(x, e)) <= 10), e)
            qr[k] = max(v, (q_alts[0] or {}).get(e) or 0)
        qr = dict(sorted(qr.items())[-12:])
        qn = quarterly(facts, CONCEPTS["net_income"][1])
        for k in sorted(set(qr) | set(qn))[-12:]:
            qrows.append([k, qr.get(k), nearest(qn, k, 10) if qn else None])
        # trailing twelve months (what most sites use for P/E, P/S, P/FCF, EV/EBITDA)
        t_rev, e_rev = ttm(qr)
        if t_rev is None:
            t_rev, e_rev = ttm_tags(facts, CONCEPTS["revenue"][1])
        t_ni, e_ni = ttm(qn)
        if t_ni is None:
            t_ni, e_ni = ttm_tags(facts, CONCEPTS["net_income"][1])
        t_cfo, e_cfo = ttm_tags(facts, CONCEPTS["cfo"][1])
        t_cap, e_cap = ttm_tags(facts, CONCEPTS["capex"][1])
        t_op, e_op = ttm_tags(facts, CONCEPTS["op_income"][1])
        if t_op is None:
            # no operating income line (Eli Lilly): EBIT = pre-tax income + interest expense
            t_pt, e_pt = ttm_tags(facts, CONCEPTS["pretax_income"][1])
            t_ie, e_ie = ttm_tags(facts, CONCEPTS["interest_exp"][1])
            if t_pt is not None:
                t_op, e_op = t_pt + (t_ie or 0), e_pt
        t_da, e_da = ttm_tags(facts, CONCEPTS["da"][1])
        t_div, e_div = ttm_tags(facts, CONCEPTS["dividends"][1])
        t_eps, e_eps = None, None
        for tag in CONCEPTS["eps_diluted"][1]:
            v, e = ttm(quarterly(facts, [tag], unit="USD/shares"))
            if v is not None:
                t_eps, e_eps = v, e
                break
        end = e_ni or e_rev
        if end and end > last["fy_end"]:
            same = lambda e: e is not None and abs(days(e, end)) <= 10
            ttm_rec = {"end": end,
                       "revenue": t_rev if same(e_rev) else None,
                       "net_income": t_ni if same(e_ni) else None,
                       "cfo": t_cfo if same(e_cfo) else None,
                       "capex": abs(t_cap) if same(e_cap) else (0.0 if (same(e_cfo) and not series["capex"] and last["capex"] == 0) else None),
                       "op_income": t_op if same(e_op) else None,
                       "da": t_da if same(e_da) else None,
                       "dividends": abs(t_div) if same(e_div) else None,
                       "eps": t_eps if same(e_eps) else None}
            ttm_rec["fcf"] = (ttm_rec["cfo"] - ttm_rec["capex"]) if (ttm_rec["cfo"] is not None and ttm_rec["capex"] is not None) else None
            da_t = ttm_rec["da"] if ttm_rec["da"] is not None else last.get("da")  # D&A often only reported yearly
            ttm_rec["ebitda"] = (ttm_rec["op_income"] + da_t) if (ttm_rec["op_income"] is not None and da_t is not None) else None
    return {
        "ticker": entry["ticker"], "name": entry["title"], "cik": cik,
        "currency": "USD", "reported_currency": meta.get("currency", "USD"),
        "foreign": bool((meta.get("forms") or set()) & {"20-F", "20-F/A", "40-F", "40-F/A"}),
        "fx_approx": bool(meta.get("fx_approx")), "source": "SEC EDGAR XBRL (companyfacts)",
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "latest": {k: last[k] for k in ("fy", "fy_end", "revenue", "net_income", "fcf", "eps_diluted",
                                         "shares_diluted", "shares_out", "cash", "debt", "equity",
                                         "net_margin", "fcf_margin", "roic")},
        "summary": summary,
        "annual": rows,
        "quarterly": qrows,
        "ttm": ttm_rec,
        "bs": bs,
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


EST = {}


def load_estimates():
    """Analyst consensus (estimates.py -> branch "estimates")."""
    try:
        url = "https://raw.githubusercontent.com/" + os.environ.get("GITHUB_REPOSITORY", "mrezahajilou-ops/stock-data") + "/estimates/est.json"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "stock-data-build"}), timeout=60) as r:
            EST.update(json.loads(r.read()).get("est") or {})
        log("analyst estimates:", len(EST))
    except Exception as e:
        log("estimates unavailable", e)


def forward(rec, mk):
    """Forward multiples on the next twelve months (NTM) of analyst consensus: the current and next fiscal
    year estimates weighted by how much of the current fiscal year is still ahead (FactSet/stockanalysis style)."""
    e = EST.get(rec["ticker"]) or {}
    out = {}
    mcap, price = (mk or {}).get("mcap"), (mk or {}).get("price")
    if not e or not mcap or not price:
        return out
    today = dt.date.today()
    try:
        w = (dt.date.fromisoformat(e["fy0"]) - today).days / 365.0 if e.get("fy0") else 0.5
    except Exception:
        w = 0.5
    w = max(0.0, min(1.0, w))

    def ntm(a, b):
        if a is not None and b is not None:
            return w * a + (1 - w) * b
        return b if b is not None else a
    cur = e.get("cur") or "USD"
    fx = 1.0 if cur == "USD" else (FX_LATEST.get(cur) or None)
    eps, revn = ntm(e.get("e0"), e.get("e1")), ntm(e.get("r0"), e.get("r1"))
    # preferred: next four quarters = the two quarters analysts estimate explicitly + two average quarters of
    # the next fiscal year (avoids one-off gains already booked in the current year's GAAP figure)
    if e.get("qe0") is not None and e.get("qe1") is not None and e.get("e1") is not None:
        eps = e["qe0"] + e["qe1"] + e["e1"] / 2
    if e.get("qr0") and e.get("qr1") and e.get("r1"):
        revn = e["qr0"] + e["qr1"] + e["r1"] / 2
    if cur == "USD":
        if eps and eps > 0:
            out["fwd_pe"] = price / eps
            out["fwd_eps"] = eps
    elif e.get("fpe") and e["fpe"] > 0:
        out["fwd_pe"] = e["fpe"]  # foreign filers: per-ADS conversion done by the data provider
    if revn and revn > 0 and fx:
        out["fwd_ps"] = mcap / (revn / fx)
        out["fwd_rev"] = revn / fx
        # forward P/FCF: no consensus FCF is published, so analysts' revenue x the company's own FCF margin
        # (latest 12 months, else last fiscal year)
        t, last = rec.get("ttm") or {}, rec["annual"][-1]
        fm = (t["fcf"] / t["revenue"]) if (t.get("fcf") is not None and t.get("revenue")) else last.get("fcf_margin")
        if fm and fm > 0:
            out["fwd_pfcf"] = mcap / (revn / fx * fm)
    if e.get("tgt"):
        rec["analyst"] = {k: e.get(k) for k in ("tgt", "tlo", "thi", "nt", "rec", "rm", "n", "fy0", "fy1", "e0", "e1", "r0", "r1", "cur")}
        rec["analyst"]["up"] = e["tgt"] / price - 1
        rec["analyst"]["fwd_eps"] = out.get("fwd_eps")
        rec["analyst"]["fwd_rev"] = out.get("fwd_rev")
    return out


def score(rec, mk, sector_pe):
    """Five 0-5 scores. Also returns the individual checks (as 1/0) so the site can explain WHY."""
    a, s = rec["annual"], rec["summary"]
    last = a[-1]
    prev3 = a[-4] if len(a) >= 4 else None
    rev, ni, fcf = last["revenue"], last["net_income"], last["fcf"]
    ebitda = last.get("ebitda")
    t = rec.get("ttm") or {}
    # valuation multiples on the trailing twelve months when the quarters are available
    if t.get("net_income") is not None:
        ni = t["net_income"]
    if t.get("revenue") is not None:
        rev = t["revenue"]
    if t.get("fcf") is not None:
        fcf = t["fcf"]
    if t.get("ebitda") is not None:
        ebitda = t["ebitda"]
    mcap = (mk or {}).get("mcap")
    price = (mk or {}).get("price")
    # SEC data can lag: a 10-Q missing from SEC's XBRL feed (Abbott, NextEra) or foreign filers without quarterly
    # XBRL (Shell, Toyota). Then use the independent trailing figures (Yahoo) instead of stale ones.
    ref = (EST.get(rec["ticker"]) or {}).get("ref") or {}
    e = EST.get(rec["ticker"]) or {}
    stale = (not t.get("end")) or (dt.date.today() - dt.date.fromisoformat(t["end"])).days > 135
    rec["ttm_src"] = "sec"
    if stale and ref:
        fxr = 1.0 if (e.get("cur") or "USD") == "USD" else FX_LATEST.get(e.get("cur"))
        if isinstance(ref.get("rev"), (int, float)) and ref["rev"] > 0 and fxr:
            rev = ref["rev"] / fxr
        if isinstance(ref.get("ni"), (int, float)) and fxr:
            ni = ref["ni"] / fxr
        if isinstance(ref.get("ebitda"), (int, float)) and fxr:
            ebitda = ref["ebitda"] / fxr
        rec["ttm_src"] = "yahoo"
    pe = mcap / ni if (mcap and ni and ni > 0) else None
    if not stale and t.get("eps") and t["eps"] > 0 and price:
        pe = price / t["eps"]  # price / diluted EPS of the last four quarters (as Yahoo / stockanalysis)
    elif not stale and t.get("eps") is not None and t["eps"] <= 0:
        pe = None
    elif isinstance(ref.get("teps"), (int, float)) and price and (stale or t.get("eps") is None):
        pe = price / ref["teps"] if ref["teps"] > 0 else None
    pfcf = mcap / fcf if (mcap and fcf and fcf > 0) else None
    ps = mcap / rev if (mcap and rev and rev > 0) else None
    b = rec.get("bs") or {}
    equity_now = b.get("equity") if b.get("equity") is not None else last.get("equity")
    pb = mcap / equity_now if (mcap and equity_now and equity_now > 0) else None
    eg = s.get("eps_cagr_5y") if s.get("eps_cagr_5y") is not None else s.get("ni_cagr_5y")
    peg = pe / (eg * 100) if (pe and eg and eg > 0) else None
    fair = dcf_fair_mcap(rec)
    spe = sector_pe.get((mk or {}).get("sector"))
    debt = (b["debt"] if b.get("debt") is not None else last.get("debt")) or 0
    cash = (b["cash"] if b.get("cash") is not None else last.get("cash")) or 0
    ev = (mcap + debt - cash) if mcap else None
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
    div_t = t.get("dividends") if t.get("dividends") is not None else last.get("dividends")
    divy = (div_t or 0) / mcap if mcap else None
    buyback_y = (last.get("buybacks") or 0) / mcap if mcap else None
    checks = {"value": [int(bool(c)) for c in v_checks] if v_checks else None,
              "future": [int(bool(c)) for c in f_checks], "past": [int(bool(c)) for c in p_checks],
              "health": [int(bool(c)) for c in h_checks], "capital": [int(bool(c)) for c in c_checks]}
    scores = {"value": value, "future": future, "past": past, "health": health, "capital": capital, "total": total}
    fwd = forward(rec, mk)
    ratios = {"pe": pe, "pfcf": pfcf, "ps": ps, "pb": pb, "peg": peg, "fair_mcap": fair, "div_yield": divy,
              "fwd_pe": fwd.get("fwd_pe"), "fwd_ps": fwd.get("fwd_ps"), "fwd_pfcf": fwd.get("fwd_pfcf"),
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
                 "fcf_conv", "fair_up", "years",
                 # v3: analyst consensus
                 "fwd_pe", "fwd_ps", "fwd_pfcf", "tgt_up", "rm"]


def fix_mcap(recs, market):
    """Cross-check market caps with an independent source (Yahoo, via the estimates branch). The Nasdaq screener
    sometimes counts only one share class (Interactive Brokers, Blackstone) or a stale share count (after splits).
    When the share counts differ by more than 8%, use the independent share count with our price."""
    fixed = []
    for r in recs:
        t = r["ticker"]
        mk, ref = market.get(t), ((EST.get(t) or {}).get("ref") or {})
        if not mk or not mk.get("mcap") or not mk.get("price") or not ref.get("mcap") or not ref.get("price"):
            continue
        sh_ours, sh_ref = mk["mcap"] / mk["price"], ref["mcap"] / ref["price"]
        if abs(sh_ours / sh_ref - 1) > 0.08:
            mk["mcap"] = mk["price"] * sh_ref
            fixed.append((t, round(sh_ours / sh_ref, 2)))
    log("market caps corrected:", len(fixed), fixed[:30])


def finish(recs, market):
    fix_mcap(recs, market)
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
        n = next((c for c in CAND if abs(k / c - 1) < (0.12 if c in (1000, 1e6) else 0.06)), None) if not (0.87 <= k <= 1.15) else None
        if not r.get("foreign") and n not in (1000, 1e6):
            # US filers: share counts vs market cap are unreliable for multi-class companies (Interactive Brokers)
            # and spin-offs, so detect a stock split from EPS instead: our EPS of the last four quarters vs the
            # independent trailing EPS (Yahoo), which is restated for splits
            n = None
            te, ye = (r.get("ttm") or {}).get("eps"), ((EST.get(r["ticker"]) or {}).get("ref") or {}).get("teps")
            if te and ye and isinstance(ye, (int, float)) and ye > 0 and te > 0:
                q = te / ye
                n = next((c for c in CAND if c not in (1000, 1e6) and abs(q / c - 1) < 0.06), None)
                n = 1 / n if n else None  # EPS too high by q -> shares too low by q
        if not n:
            continue
        prev = r["annual"][-2].get("shares_diluted") if len(r["annual"]) > 1 else None
        if r.get("foreign") and n > 1 and prev and sh / prev > 1.3 and n not in (1000, 1e6):
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
        if (r.get("ttm") or {}).get("eps") is not None and n not in (1e6, 1000):
            r["ttm"]["eps"] = r["ttm"]["eps"] / n
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
                         last.get("fcf_conv"), r4(fair_up), s.get("years"),
                         r4(ratios.get("fwd_pe")), r4(ratios.get("fwd_ps")), r4(ratios.get("fwd_pfcf")),
                         r4((r.get("analyst") or {}).get("up")), (r.get("analyst") or {}).get("rm")])
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
        for k in ("pe", "pfcf", "ps", "ev_ebitda", "nm", "gm", "roic", "revg1", "divy", "fcf_yield", "de", "fwd_pe", "fwd_ps"):
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
    load_estimates()
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
        pred = PREDECESSOR.get(cik)
        if pred:
            try:
                old = json.loads(zf.read("CIK%010d.json" % pred)).get("facts", {})
                for ns, tags in old.items():
                    for name, node in tags.items():
                        cur = facts.setdefault(ns, {}).setdefault(name, {"units": {}})
                        for u, arr in node.get("units", {}).items():
                            cur.setdefault("units", {})
                            cur["units"][u] = arr + cur["units"].get(u, [])
                log("merged predecessor", pred, "into", cik)
            except Exception as e:
                log("predecessor merge failed", cik, e)
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
