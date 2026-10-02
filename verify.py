#!/usr/bin/env python3
"""Compare built data against independently published reference values (stockanalysis.com, Oct 2026).
Prints a table and writes data/verify.json. Tolerance: 2% for USD figures, 3% for EPS (rounding)."""
import json, os
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
M = 1_000_000
# ticker -> fiscal year -> {metric: reference}
REF = {
  "AAPL": {2025: dict(revenue=416161*M, net_income=112010*M, eps_diluted=7.46, fcf=98767*M),
           2024: dict(revenue=391035*M, net_income=93736*M, eps_diluted=6.08, fcf=108807*M),
           2023: dict(revenue=383285*M, net_income=96995*M, eps_diluted=6.13, fcf=99584*M)},
  "NVDA": {2026: dict(revenue=215938*M, op_income=130387*M, net_income=120067*M, eps_diluted=4.90, fcf=96676*M),
           2025: dict(revenue=130497*M, op_income=81453*M, net_income=72880*M, eps_diluted=2.94, fcf=60853*M),
           2024: dict(revenue=60922*M, op_income=32972*M, net_income=29760*M, eps_diluted=1.19, fcf=27021*M)},
  "MSFT": {2026: dict(revenue=331839*M, op_income=155237*M, net_income=133749*M, eps_diluted=17.95, fcf=66987*M),
           2025: dict(revenue=281724*M, op_income=128528*M, net_income=101832*M, eps_diluted=13.64, fcf=71611*M),
           2024: dict(revenue=245122*M, op_income=109433*M, net_income=88136*M, eps_diluted=11.80, fcf=74071*M)},
  "SE":   {2025: dict(revenue=22938*M, op_income=1985*M, net_income=1578*M, eps_diluted=2.52, fcf=4511*M),
           2024: dict(revenue=16820*M, op_income=662.15*M, net_income=444.32*M, eps_diluted=0.74, fcf=2959*M),
           2023: dict(revenue=13064*M, op_income=342.65*M, net_income=150.73*M, eps_diluted=0.25, fcf=1838*M)},
  "MELI": {2025: dict(revenue=28893*M, op_income=3201*M, net_income=1997*M, eps_diluted=39.39, fcf=10773*M),
           2024: dict(revenue=20777*M, op_income=2631*M, net_income=1911*M, eps_diluted=37.69, fcf=7058*M),
           2023: dict(revenue=15107*M, op_income=2207*M, net_income=987*M, eps_diluted=19.46, fcf=4631*M)},
  "HOOD": {2025: dict(revenue=4473*M, op_income=2094*M, net_income=1883*M, eps_diluted=2.05, fcf=1623*M),
           2024: dict(revenue=2951*M, op_income=1054*M, net_income=1411*M, eps_diluted=1.56, fcf=-170*M),
           2023: dict(revenue=1865*M, op_income=-536*M, net_income=-541*M, eps_diluted=-0.61, fcf=1179*M)},
  "HIMS": {2025: dict(revenue=2348*M, op_income=121.16*M, net_income=128.37*M, eps_diluted=0.51, fcf=73.96*M),
           2024: dict(revenue=1477*M, op_income=65.88*M, net_income=126.04*M, eps_diluted=0.53, fcf=209.43*M),
           2023: dict(revenue=872*M, op_income=-26.44*M, net_income=-23.55*M, eps_diluted=-0.11, fcf=56.26*M)},
}

def pct(a, b):
    if a is None or b is None: return None
    base = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / base

def main():
    results, ok, bad, missing = [], 0, 0, 0
    for t, years in REF.items():
        p = os.path.join(OUT, "stocks", f"{t}.json")
        if not os.path.exists(p):
            print(f"{t}: NOT BUILT"); missing += len(years); continue
        rec = json.load(open(p))
        rows = {r["fy"]: r for r in rec["annual"]}
        # fy label may be off by one for Jan fiscal year ends; also match by fy_end year
        by_endyear = {int(r["fy_end"][:4]): r for r in rec["annual"]}
        for fy, metrics in years.items():
            row = rows.get(fy) or by_endyear.get(fy)
            for k, ref in metrics.items():
                got = row.get(k) if row else None
                d = pct(got, ref)
                tol = 0.03 if k == "eps_diluted" else 0.02
                status = "MISSING" if got is None else ("OK" if d <= tol else "DIFF")
                if status == "OK": ok += 1
                elif status == "DIFF": bad += 1
                else: missing += 1
                results.append(dict(ticker=t, fy=fy, metric=k, ours=got, ref=ref, diff=None if d is None else round(d, 4), status=status))
                if status != "OK":
                    print(f"{t} FY{fy} {k}: ours={got} ref={ref} -> {status}")
    print(f"\nOK {ok} / DIFF {bad} / MISSING {missing}")
    json.dump(dict(ok=ok, diff=bad, missing=missing, rows=results), open(os.path.join(OUT, "verify.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
