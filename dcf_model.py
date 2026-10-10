#!/usr/bin/env python3
"""DCF engine shared by the nightly build (screener 'fair value' column, value score) and the DCF page.

The page (web/dcf.html) runs the SAME math in JavaScript (function `value` there); test_dcf.py checks that both
give identical results. If you change the model here, change it there too.

Inputs ("dcf" block written into every data/stocks/<T>.json):
  base   freshest trailing-twelve-month figures in USD: rev, ni, fcf, div, end (period end), src (sec|yahoo|annual)
  cash, debt   latest balance sheet (USD);  sh  shares the market price refers to (market cap / price)
  hist   history columns [TTM, 1y, 5y, 10y] for growth, net margin, FCF margin, ROIC, share count change
  an     analyst consensus: g (average yearly revenue growth over the next ~2 years), nm (forward net margin)
  mode   all | earn (banks/insurers/brokers: P/E only) | cash (REITs: FCF methods only)
  d      default assumptions per scenario [bear, medium, bull] in percent / multiples

Model, year by year for N years (5 or 10):
  revenue growth  years 1-2 = g1 (near term, analyst based), then the gap to the long-run rate g2 shrinks
                  by 25% a year (year 3: g2 + 75% of the gap, year 4: 56%, ... year 10: 10%)
  margins         move in a straight line from today's TTM margin to the target margin by year 5
  share count     changes by `sh` % a year (negative = buybacks)
  dividends       today's payout ratio of each year's profit, counted while you hold the stock
  three methods   1) P/E exit:   EPS(N) x P/E, discounted + dividends received
                  2) P/FCF exit: FCF per share(N) x P/FCF, discounted + dividends received
                  3) classic DCF: every year's free cash flow discounted + terminal value FCF(N)x(1+tg)/(r-tg),
                     per today's share (buybacks are paid from that FCF, so only dilution counts)
                  Profit and FCF are after interest, so debt is already paid for and interest earned on cash
                  is already counted: net cash is NOT added by default (optional on the page, b["nc"]).
  fair value      average of the methods that apply
"""
import datetime as dt
import math

K_NEAR = 2      # years at the near-term growth rate
FADE = 0.75     # after that the gap between growth and the long-run rate g2 shrinks 25% a year
M_YEARS = 5     # years for margins to reach their target


def clamp(x, a, b):
    return max(a, min(b, x))


def half(x):
    """Round to 0.5 (what the page shows in the inputs)."""
    return round(x * 2) / 2


# ---------------------------------------------------------------- model
def project(b, N, g1, g2, pm, fm, shg):
    """Yearly path. b = base block. Rates as fractions. Returns list of dicts per year 1..N."""
    rev, sh0 = b["rev"], b["sh"]
    pm0 = b["ni"] / rev if b.get("ni") is not None and rev else pm
    fm0 = b["fcf"] / rev if b.get("fcf") is not None and rev else fm
    out = []
    mN = min(M_YEARS, N)
    for t in range(1, N + 1):
        g = g1 if t <= K_NEAR else g2 + (g1 - g2) * FADE ** (t - K_NEAR)
        rev = rev * (1 + g)
        w = min(1.0, t / mN)
        p, f = pm0 + (pm - pm0) * w, fm0 + (fm - fm0) * w
        out.append({"g": g, "rev": rev, "ni": rev * p, "fcf": rev * f, "sh": sh0 * (1 + shg) ** t})
    return out


def value(b, N, g1, g2, pm, fm, pe, pf, r, shg, tg):
    """Fair value per share (USD) with the three methods. Rates as fractions."""
    sh0 = b["sh"]
    if not b.get("rev") or not sh0 or r <= -0.99:
        return None
    ys = project(b, N, g1, g2, pm, fm, shg)
    payout = b.get("payout") or 0
    nc = (b.get("nc") or 0) / sh0
    dps_pv, fcf_pv = 0.0, 0.0
    for t, y in enumerate(ys, 1):
        disc = (1 + r) ** t
        dps_pv += max(y["ni"], 0) * payout / y["sh"] / disc
        fcf_pv += y["fcf"] / disc
    L, discN = ys[-1], (1 + r) ** N
    mode = b.get("mode") or "all"
    v_pe = (L["ni"] / L["sh"] * pe / discN + dps_pv + nc) if (L["ni"] > 0 and mode != "cash") else None
    v_pf = (L["fcf"] / L["sh"] * pf / discN + dps_pv + nc) if (L["fcf"] > 0 and mode != "earn") else None
    v_dcf = None
    if L["fcf"] > 0 and mode != "earn" and r - tg >= 0.01:
        tv = L["fcf"] * (1 + tg) / (r - tg)
        v_dcf = (fcf_pv + tv / discN + (b.get("nc") or 0)) / sh0 / (1 + max(shg, 0)) ** N
    vals = [v for v in (v_pe, v_pf, v_dcf) if v is not None]
    fair = sum(vals) / len(vals) if vals else None
    # value of one share in year N (exit methods) + dividends received, for the buy-and-hold return
    ex = [v for v in ((L["ni"] / L["sh"] * pe) if v_pe is not None else None,
                      (L["fcf"] / L["sh"] * pf) if v_pf is not None else None) if v is not None]
    return {"fair": fair, "pe": v_pe, "pf": v_pf, "dcf": v_dcf, "exit": (sum(ex) / len(ex)) if ex else None, "path": ys}


def scen(b, d, i, N=10):
    """Value of scenario i (0 bear, 1 medium, 2 bull) from the default block d (percent units)."""
    p = lambda k: d[k][i] / 100.0
    return value(b, N, p("g1"), p("g2"), p("pm"), p("fm"), d["pe"][i], d["pf"][i], p("ret"), p("sh"), p("tg"))


# ---------------------------------------------------------------- inputs

# Country risk premium added to the default required return (percentage points), after Damodaran's country risk
# premiums (rating-based default spread x equity/bond volatility), rounded. Developed markets = 0.
CRP = {"China": 1.0, "Hong Kong": 1.0, "Taiwan": 0.7, "South Korea": 0.7, "Japan": 0.7, "India": 2.0,
       "Indonesia": 2.0, "Philippines": 2.0, "Thailand": 1.5, "Malaysia": 1.2, "Vietnam": 3.5, "Singapore": 0.0,
       "Brazil": 3.5, "Mexico": 2.5, "Argentina": 6.0, "Chile": 1.0, "Colombia": 3.0, "Peru": 2.0, "Uruguay": 2.0,
       "Panama": 2.5, "Kazakhstan": 2.5, "Turkey": 5.0, "Greece": 2.0, "Italy": 2.0, "Spain": 1.0, "Portugal": 1.0,
       "Israel": 1.5, "South Africa": 3.5, "Nigeria": 6.0, "Egypt": 6.0, "Poland": 1.0, "Hungary": 2.0,
       "Cyprus": 2.0, "Russia": 6.0, "Ukraine": 6.0, "Kenya": 5.0, "Saudi Arabia": 0.8, "United Arab Emirates": 0.6}
# where the business really is, when the listing country is only the legal home (Cayman, Luxembourg, ...)
COUNTRY_OVERRIDE = {"NU": "Brazil", "MELI": "Brazil", "XP": "Brazil", "STNE": "Brazil", "PAGS": "Brazil",
                    "VTEX": "Brazil", "DLO": "Uruguay", "SE": "Indonesia", "GRAB": "Indonesia", "PDD": "China",
                    "BABA": "China", "JD": "China", "BIDU": "China", "TCOM": "China", "BEKE": "China", "NTES": "China",
                    "YUMC": "China", "TME": "China", "VIPS": "China", "ZTO": "China", "LI": "China", "NIO": "China",
                    "XPEV": "China", "CPNG": "South Korea", "KSPI": "Kazakhstan", "GLOB": "Argentina",
                    "ARCO": "Brazil", "CIB": "Colombia", "BAP": "Peru", "FMX": "Mexico", "AMX": "Mexico"}

EARN_RE = ("bank", "savings", "insur", "finance compan", "blank check", "diversified financial", "trusts")


def _ts_last(ts, key, fx):
    """Latest value of a Yahoo series in USD -> (asOfDate, value) or (None, None)."""
    v = (ts or {}).get(key)
    if not v:
        return None, None
    d, val, cur = v[-1]
    if val is None:
        return None, None
    rate = 1.0 if (cur or "USD") == "USD" else fx.get(cur)
    if not rate:
        return None, None
    return d, val / rate


def _ts_annual(ts, key, fx):
    out = {}
    for d, val, cur in (ts or {}).get(key) or []:
        rate = 1.0 if (cur or "USD") == "USD" else fx.get(cur)
        if val is not None and rate:
            out[d] = val / rate
    return out


def days(a, b):
    return (dt.date.fromisoformat(b[:10]) - dt.date.fromisoformat(a[:10])).days


def block(rec, mk, est, fx, peer=None, today=None):
    """Build the dcf input block for one company. est = estimates entry (or {}), fx = units per USD,
    peer = industry medians {"pe", "pf"} used for the exit multiples."""
    today = today or dt.date.today()
    tiso = today.isoformat()
    mk = mk or {}
    price, mcap = mk.get("price"), mk.get("mcap")
    if not price or not mcap or not rec.get("annual"):
        return None
    sh = mcap / price
    a = rec["annual"]
    last = a[-1]
    t = rec.get("ttm") or {}
    ts = est.get("ts") or {}
    # ---- annual history (SEC), extended with newer Yahoo annual reports when SEC lags (foreign 20-F filers)
    ind = ((mk.get("industry") or "") + " ").lower()
    # REITs: buildings bought are growth, not upkeep; their cash earnings (~FFO) = operating cash flow
    reit = "real estate" in ind or "reit" in ind
    FC = "cfo" if reit else "fcf"
    hist = [{"end": r["fy_end"], "rev": r.get("revenue"), "ni": r.get("net_income"), "fcf": r.get(FC),
             "sh": r.get("shares_diluted"), "roic": r.get("roic")} for r in a if r.get("revenue")]
    y_rev, y_ni = _ts_annual(ts, "annualTotalRevenue", fx), _ts_annual(ts, "annualNetIncomeCommonStockholders", fx) or _ts_annual(ts, "annualNetIncome", fx)
    y_fcf = _ts_annual(ts, "annualOperatingCashFlow" if reit else "annualFreeCashFlow", fx)
    added = 0
    for d in sorted(y_rev):
        if hist and days(hist[-1]["end"], d) < 300:
            continue
        if not y_rev[d] or y_rev[d] <= 0:
            continue
        hist.append({"end": d, "rev": y_rev[d], "ni": y_ni.get(d), "fcf": y_fcf.get(d), "sh": None, "roic": None})
        added += 1
    if not hist:
        return None

    # ---- base: the freshest trailing twelve months (SEC quarters or 10-K, else Yahoo, else last annual report)
    ref = est.get("ref") or {}
    cur = est.get("cur") or "USD"
    rate = 1.0 if cur == "USD" else fx.get(cur)
    base = None
    sec_end, sec = None, None
    if t.get("revenue"):
        sec_end, sec = t["end"], t
    if last.get("revenue") and (not sec_end or last["fy_end"] >= sec_end):  # the 10-K is the latest 12 months
        sec_end, sec = last["fy_end"], {"revenue": last["revenue"], "net_income": last.get("net_income"),
                                        "fcf": last.get(FC), "dividends": last.get("dividends")}
    elif sec is not None and reit:
        sec = dict(sec, fcf=sec.get("cfo"))
    yd, yrev = _ts_last(ts, "trailingTotalRevenue", fx)
    # no time series, SEC figures 100+ days old and Yahoo's trailing revenue clearly different: a newer quarter exists
    ref_newer = ((not yd or days(sec_end or yd, yd) <= 45) and sec_end and days(sec_end, tiso) > 100 and rate and isinstance(ref.get("rev"), (int, float))
                 and ref["rev"] > 0 and 0.08 < abs(ref["rev"] / rate / sec["revenue"] - 1) and 0.67 < ref["rev"] / rate / sec["revenue"] < 1.6)
    # Yahoo's series only replaces SEC data when the revenue definition matches (hotels: fee vs total revenue)
    if yd and yrev and sec_end and days(sec_end, yd) < 200 and not (0.67 < yrev / sec["revenue"] < 1.6):
        yd, yrev = None, None
    if sec_end and (not yd or days(yd, sec_end) >= -45) and days(sec_end, tiso) <= 135 and not ref_newer:
        fcf = sec.get("fcf")
        if fcf is None and last.get("fcf_margin") is not None:
            fcf = last["fcf_margin"] * sec["revenue"]
        div = sec.get("dividends") if sec.get("dividends") is not None else (last.get("dividends") or 0)
        ni = sec.get("net_income")
        base = {"src": "sec", "end": sec_end, "rev": sec["revenue"],
                "ni": ni if ni is not None else (last.get("net_margin") or 0) * sec["revenue"], "fcf": fcf, "div": div}
    elif yd and yrev and yrev > 0 and days(yd, tiso) <= 200 and not ref_newer:
        _, yni = _ts_last(ts, "trailingNetIncomeCommonStockholders", fx)
        if yni is None:
            _, yni = _ts_last(ts, "trailingNetIncome", fx)
        _, yfcf = _ts_last(ts, "trailingOperatingCashFlow" if reit else "trailingFreeCashFlow", fx)
        if yfcf is None and not reit:
            _, ycfo = _ts_last(ts, "trailingOperatingCashFlow", fx)
            _, ycap = _ts_last(ts, "trailingCapitalExpenditure", fx)
            if ycfo is not None and ycap is not None:
                yfcf = ycfo - abs(ycap)
        _, ydiv = _ts_last(ts, "trailingCashDividendsPaid", fx)
        if yni is None:
            yni = (last.get("net_margin") or 0) * yrev
        if yfcf is None and last.get("fcf_margin") is not None:
            yfcf = last["fcf_margin"] * yrev
        base = {"src": "yahoo", "end": yd, "rev": yrev, "ni": yni, "fcf": yfcf, "div": abs(ydiv) if ydiv is not None else None}
    elif rate and isinstance(ref.get("rev"), (int, float)) and ref["rev"] > 0 and (not sec_end or days(sec_end, tiso) > 135 or ref_newer):
        # no time series: Yahoo's trailing summary figures (revenue, profit); FCF at the last known margin
        rv = ref["rev"] / rate
        ni = ref["ni"] / rate if isinstance(ref.get("ni"), (int, float)) else (last.get("net_margin") or 0) * rv
        if t.get(FC) is not None and t.get("revenue"):
            fm_last = t[FC] / t["revenue"]
        else:
            fm_last = hist[-1]["fcf"] / hist[-1]["rev"] if hist[-1].get("fcf") is not None else None
        base = {"src": "yahoo", "end": tiso, "rev": rv, "ni": ni, "fcf": fm_last * rv if fm_last is not None else None, "div": None}
    if base is None:
        h = hist[-1]
        base = {"src": "annual", "end": h["end"], "rev": h["rev"], "ni": h["ni"], "fcf": h["fcf"],
                "div": last.get("dividends") if h["end"] == last["fy_end"] else None}
    if base.get("div") is None:
        base["div"] = ref["divy"] * mcap if isinstance(ref.get("divy"), (int, float)) else (last.get("dividends") or 0)
    if not base["rev"] or base["rev"] <= 0:
        return None
    # ---- latest balance sheet
    bs = rec.get("bs") or {}
    cash = bs.get("cash") if bs.get("cash") is not None else last.get("cash")
    debt = bs.get("debt") if bs.get("debt") is not None else last.get("debt")
    bs_end = bs.get("end") or last["fy_end"]
    cd, ycash = _ts_last(ts, "quarterlyCashCashEquivalentsAndShortTermInvestments", fx)
    dd, ydebt = _ts_last(ts, "quarterlyTotalDebt", fx)
    if cd and ycash is not None and days(bs_end, cd) > 45:
        cash, debt, bs_end = ycash, (ydebt if (dd == cd and ydebt is not None) else debt), cd
    cash, debt = cash or 0, debt or 0

    # ---- history columns [TTM, 1y, 5y, 10y]
    def cagr(k, n):
        if len(hist) <= n:
            return None
        x, y = hist[-1 - n][k], hist[-1][k]
        if not x or y is None or x <= 0 or y <= 0:
            return None
        return (y / x) ** (1 / n) - 1

    def avg(f, n):
        if len(hist) < n:
            return None
        v = [f(r) for r in hist[-n:]]
        v = [x for x in v if x is not None]
        return sum(v) / len(v) if v else None

    nm = lambda r: r["ni"] / r["rev"] if r.get("ni") is not None and r.get("rev") else None
    fmr = lambda r: r["fcf"] / r["rev"] if r.get("fcf") is not None and r.get("rev") else None
    q = rec.get("quarterly") or []
    g_ttm = None
    if base["src"] == "sec" and len(q) >= 8 and all(x[1] for x in q[-8:]):
        prev = sum(x[1] for x in q[-8:-4])
        g_ttm = sum(x[1] for x in q[-4:]) / prev - 1 if prev > 0 else None
    elif hist and days(hist[-1]["end"], base["end"]) <= 20 and len(hist) >= 2 and hist[-2]["rev"]:
        g_ttm = base["rev"] / hist[-2]["rev"] - 1
    pm_t = base["ni"] / base["rev"] if base.get("ni") is not None else None
    fm_t = base["fcf"] / base["rev"] if base.get("fcf") is not None else None
    H = {"g": [g_ttm, cagr("rev", 1), cagr("rev", 5), cagr("rev", 10)],
         "pm": [pm_t, avg(nm, 1), avg(nm, 5), avg(nm, 10)],
         "fm": [fm_t, avg(fmr, 1), avg(fmr, 5), avg(fmr, 10)],
         "roic": [None, avg(lambda r: r.get("roic"), 1), avg(lambda r: r.get("roic"), 5), avg(lambda r: r.get("roic"), 10)],
         "sh": [None] + [None if rec.get("foreign") or rec.get("per_share_basis") == "market" else cagr("sh", n) for n in (1, 5, 10)]}

    # ---- analyst consensus (revenue growth over the next ~2 years, forward net margin). Growth is measured
    # against the same provider's trailing revenue so the revenue definitions match (banks, insurers).
    an = {}
    r0, r1 = est.get("r0"), est.get("r1")
    w = 0.5
    _, y_ttm = _ts_last(ts, "trailingTotalRevenue", fx)
    # analysts forecast reported (GAAP / IFRS) revenue, the same figure as our base; only an old annual base is
    # replaced by the provider's trailing revenue
    rev_ref = base["rev"]
    if base["src"] == "annual":
        rev_ref = y_ttm or (ref["rev"] / rate if (rate and isinstance(ref.get("rev"), (int, float)) and ref["rev"] > 0) else None) or base["rev"]
    fy0_past = bool(est.get("fy0")) and est["fy0"] < (today - dt.timedelta(days=20)).isoformat()
    e0, e1 = est.get("e0"), est.get("e1")
    if rate and r1 and r1 > 0:
        R0, R1 = (r0 / rate if r0 else None), r1 / rate
        g_in = R1 / R0 - 1 if R0 and R0 > 0 else None        # next year vs this year: same analysts, same definition
        # growth from today's trailing revenue to next fiscal year's estimate (annualised over the time between)
        fy1 = est.get("fy1") or ((est["fy0"][:4] and str(int(est["fy0"][:4]) + 1) + est["fy0"][4:]) if est.get("fy0") else None)
        span = max(0.75, days(base["end"], fy1) / 365.0) if fy1 else 1.5
        if fy0_past:
            span = max(0.75, span - 1)                         # stale fiscal-year labels (the 0y year is already over)
        g_tr = (R1 / rev_ref) ** (1 / span) - 1
        same_def = R0 is not None and 0.75 <= R0 / rev_ref <= 2.5
        gg = g_tr if (same_def or R0 is None) and -0.6 < g_tr < 3.0 else g_in
        g_eps = e1 / e0 - 1 if (e0 and e1 and e0 > 0 and e1 > 0) else None
        if gg is not None and -0.6 < gg < 3.0:
            an["g"] = gg
            an["g_eps"] = g_eps
            an["n"] = est.get("n")
            if cur == "USD" and e1 and same_def:
                if fy0_past or e0 is None:
                    eps_n, rev_n = e1, R1
                else:
                    w = clamp(days(tiso, est["fy0"]) / 365.0, 0, 1) if est.get("fy0") else 0.5
                    eps_n, rev_n = w * e0 + (1 - w) * e1, w * R0 + (1 - w) * R1
                m = eps_n * sh / (rev_n * base["rev"] / rev_ref)
                if -1 < m < 0.8:
                    an["nm"] = m

    # ---- valuation mode
    sector = mk.get("sector") or ""
    mode = "all"
    last5 = hist[-5:]
    neg_fcf = sum(1 for r in last5 if r.get("fcf") is not None and r["fcf"] < 0)
    pos_ni = sum(1 for r in last5 if r.get("ni") is not None and r["ni"] > 0)
    if reit:
        mode = "cash"
    elif any(k in ind for k in EARN_RE):
        mode = "earn"
    elif sector == "Finance":
        f5, p5 = H["fm"][2], H["pm"][2]
        if f5 is None or p5 is None or p5 <= 0 or not (0.4 <= f5 / p5 <= 2.5):
            mode = "earn"   # brokers / lenders: cash flow swings with client money and loan books
    if mode == "all" and len(last5) >= 4 and neg_fcf >= 3 and pos_ni >= 4:
        mode = "earn"       # profitable but capex funded with debt for years (utilities, pipelines)

    # ---- defaults
    g5 = H["g"][2] if H["g"][2] is not None else H["g"][1]
    g_1y = H["g"][0] if H["g"][0] is not None else H["g"][1]
    if g5 is not None and g_1y is not None:
        gh = 0.8 * (0.5 * g5 + 0.5 * clamp(g_1y, -0.3, 0.5))
    elif g5 is not None or g_1y is not None:
        gh = 0.8 * (g5 if g5 is not None else clamp(g_1y, -0.3, 0.5))
    else:
        gh = 0.05
    ga = an.get("g")
    if mode == "earn" and an.get("g_eps") is not None and an["g_eps"] > -0.5:
        ga = an["g_eps"]                                       # banks / insurers: profit growth, not "revenue"
    if ga is not None:
        g1 = 0.75 * ga + 0.25 * clamp(gh, ga - 0.10, ga + 0.10)
    else:
        g1 = gh
    g1 = clamp(g1, -0.15, 0.35)
    g2 = clamp(min(g1, max(0.3 * g1, 0.03)), -0.02, 0.08)

    def wavg(pairs):
        v = [(x, w_) for x, w_ in pairs if x is not None]
        return sum(x * w_ for x, w_ in v) / sum(w_ for _, w_ in v) if v else None

    p5 = H["pm"][2] if H["pm"][2] is not None else H["pm"][1]
    hi_g = g1 > 0.15     # fast growers: today's margin is depressed by growth spending, lean on the analysts
    pm5 = [nm(r) for r in hist[-6:] if nm(r) is not None]
    rev_fell = any(y["rev"] and x["rev"] and y["rev"] < 0.95 * x["rev"] for x, y in zip(hist[-7:-1], hist[-6:]))
    cyc = rev_fell and len(pm5) >= 4 and (max(pm5) - min(pm5) > 0.25 or (min(pm5) < 0 < max(pm5) and max(pm5) > 0.1))
    an_nm = an.get("nm")
    one_off = pm_t is not None and an_nm is not None and an_nm > 0 and pm_t > 1.35 * max(an_nm, p5 or 0)
    if one_off:          # today's profit inflated by one-off gains (investment gains, tax benefits): trust the forecast
        pm_c = wavg([(pm_t, 0.15), (max(p5, 0) if p5 is not None else None, 0.25), (an_nm, 0.6)])
    elif cyc:            # cyclical (memory, energy, airlines): steer to the through-cycle average, not today's peak/trough
        pm_c = wavg([(pm_t, 0.25), (max(p5, 0) if p5 is not None else None, 0.5), (an.get("nm"), 0.25)])
    else:
        pm_c = wavg([(pm_t, 0.3 if hi_g else 0.5), (max(p5, 0) if p5 is not None else None, 0.1 if hi_g else 0.2),
                     (an.get("nm"), 0.6 if hi_g else 0.3)])
    if mode == "earn" and pm_t is not None and pm_t > 0.005:
        pm_c = pm_t      # banks / insurers: keep today's profit margin, growth comes from profit growth
    loss = False
    if pm_c is None or pm_c <= 0.005:
        pos = [x for x in (an.get("nm"), H["pm"][2], H["pm"][3], pm_t) if x is not None and x > 0.005]
        pm_c = max(pos) if pos else 0.05
        loss = True
    pm_c = clamp(pm_c, 0.002, 0.6)
    f5 = H["fm"][2] if H["fm"][2] is not None else H["fm"][1]
    fm_c = wavg([(fm_t, 0.3 if cyc else 0.5), (max(f5, 0) if f5 is not None else None, 0.7 if cyc else 0.5)])
    if fm_c is None:
        fm_c = pm_c                                            # no cash-flow data: assume FCF = profit
    elif fm_c <= 0.005:
        fm_c = H["fm"][3] if (H["fm"][3] or 0) > 0.005 else 0.5 * pm_c
    # FCF far above profit is usually stock pay (not a cash cost) or customer money: cap it near the profit margin
    fm_c = clamp(min(fm_c, max(1.6 * pm_c, pm_c + (0.05 if hi_g else 0.03))), 0.002, 0.6)
    # heavy investment years (AI data centres, factories) depress today's FCF; over a full cycle free cash flow
    # converges towards profit (capex ~ depreciation + growth), so the long-run FCF margin is at least 60% of profit
    fm_c = max(fm_c, 0.6 * pm_c)
    # share count: median yearly change of the last 5 years (one-off mergers / spin-offs don't set the trend)
    chg = []
    if not (rec.get("foreign") or rec.get("per_share_basis") == "market"):
        for x, y in zip(hist[-6:-1], hist[-5:]):
            if x.get("sh") and y.get("sh"):
                chg.append(y["sh"] / x["sh"] - 1)
    shs = sorted(chg)[len(chg) // 2] if chg else 0.0
    shs = clamp(shs, -0.04, 0.04)
    q5 = H["roic"][2]
    prem = 3 if (q5 or 0) > 0.20 else (1.5 if (q5 or 0) > 0.12 else 0)
    if mode == "earn":
        mult = clamp(9 + 80 * g2 + prem / 2, 8, 16)   # banks / insurers / utilities trade on lower multiples
    else:
        mult = clamp(13 + 120 * g2 + prem, 10, 28)
    # exit multiples: half growth-based, half what the market pays today for the industry (median of peers)
    peer = peer or {}
    m_pe = 0.5 * mult + 0.5 * clamp(peer["pe"], 7, 35) if peer.get("pe") else mult
    m_pf = 0.5 * mult + 0.5 * clamp(peer["pf"], 7, 35) if peer.get("pf") else m_pe
    m_pe, m_pf = clamp(m_pe, 6, 32), clamp(m_pf, 6, 32)
    country = COUNTRY_OVERRIDE.get(rec["ticker"]) or mk.get("country") or ""
    crp = CRP.get(country, 0.0)
    ret = half(10 + crp)

    P = lambda x: half(x * 100)
    g1m, g2m = P(g1), P(g2)
    d = {"g1": [half(g1m - max(3, 0.35 * abs(g1m))), g1m, half(g1m + max(3, 0.25 * abs(g1m)))],
         "g2": [half(max(g2m - 2, -3)), g2m, half(min(g2m + 2, 10))],
         "pm": [half(P(pm_c) * 0.75), P(pm_c), half(min(P(pm_c) * 1.15, 60))],
         "fm": [half(P(fm_c) * 0.75), P(fm_c), half(min(P(fm_c) * 1.15, 60))],
         "pe": [round(max(m_pe * 0.8, 5)), round(m_pe), round(m_pe * 1.2)],
         "pf": [round(max(m_pf * 0.8, 5)), round(m_pf), round(m_pf * 1.2)],
         "sh": [half(P(shs) + 1), P(shs), half(P(shs) - 1)],
         "ret": [ret, ret, ret],
         "tg": [2.5, 3, 3.5]}
    if d["pm"][0] <= 0:
        d["pm"][0] = 0.5
    if d["fm"][0] <= 0:
        d["fm"][0] = 0.5
    ni_b = base.get("ni")
    payout = clamp(base["div"] / ni_b, 0, 1) if (base.get("div") and ni_b and ni_b > 0) else 0
    flags = []
    if loss:
        flags.append("loss")
    if added:
        flags.append("yahoo_annual")
    if cyc:
        flags.append("cyclical")
    if fm_t is not None and pm_t and pm_t > 0 and fm_t > 2.5 * pm_t:
        flags.append("fcf_high")
    if g5 is not None and H["g"][1] is not None and H["g"][1] < 0 < g5:
        flags.append("rev_drop")
    if base["src"] == "annual" and days(base["end"], tiso) > 200:
        flags.append("stale")
    R = lambda x: None if x is None else round(x, 4)
    blk = {"base": {k: (round(v, 0) if isinstance(v, float) and k not in ("end", "src") else v) for k, v in base.items()},
           "cash": round(cash), "debt": round(debt), "bs_end": bs_end, "sh": round(sh), "price": price,
           "payout": round(payout, 4), "nc": 0 if mode == "earn" else round(cash - debt), "mode": mode, "crp": crp,
           "hist": {k: [R(x) for x in v] for k, v in H.items()},
           "an": {k: (R(v) if k != "n" else v) for k, v in an.items()},
           "d": d, "flags": flags}
    return blk


def bvals(blk, with_cash=False):
    """The flat base dict value() needs. Net cash only when asked for (see the model notes)."""
    b = blk["base"]
    return {"rev": b["rev"], "ni": b.get("ni"), "fcf": b.get("fcf"), "sh": blk["sh"], "nc": blk["nc"] if with_cash else 0,
            "payout": blk["payout"], "mode": blk["mode"]}


def fair_mcap(blk):
    """Medium-scenario fair value of the whole company (fair value per share x shares)."""
    if not blk:
        return None
    v = scen(bvals(blk), blk["d"], 1)
    if not v or v["fair"] is None:
        return None
    return v["fair"] * blk["sh"]
