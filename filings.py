#!/usr/bin/env python3
"""Source text for the company write-ups: the "Business" and "Risk factors" sections of each company's latest
annual report (10-K, or 20-F / 40-F for foreign filers), straight from SEC EDGAR.

Output: filings/<TICKER>.json = {t, cik, form, filed, period, url, business, risks}
The text is only the raw material the write-ups are written from; it is not shown on the sites as is.
Usage: python filings.py ALL | T1,T2   (env SHARD / SHARDS split the list; env HAVE = folder with files already made,
       a company is skipped when its newest annual report is the one already stored)."""
import gzip, html, json, os, re, sys, time, urllib.request, zlib, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
UA = os.environ.get("SEC_USER_AGENT", "SahamAnaliz research contact@sahamanaliz.com")
FORMS = ("10-K", "10-K405", "10-KT", "20-F", "40-F")
OUT = os.path.join(ROOT, "filings")
HAVE = os.environ.get("HAVE", "")
MAX_SEC = int(os.environ.get("MAX_SEC", "19000"))


def fetch(url, retries=4, cap=60_000_000):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read(cap)
                enc = r.headers.get("Content-Encoding", "")
                if enc == "gzip":
                    raw = gzip.decompress(raw)
                elif enc == "deflate":
                    raw = zlib.decompress(raw)
                return raw
        except Exception as ex:
            if "404" in str(ex):
                return None
            time.sleep(3 * (i + 1))
    return None


def to_text(raw):
    s = raw.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style|ix:header)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<(/p|/div|/tr|br|/h\d|/li|/td)\b[^>]*>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f]+", " ", s)
    s = re.sub(r" ?\n ?", "\n", s)
    return re.sub(r"\n{2,}", "\n", s)


def section(text, start_pats, end_pats, limit):
    """The longest stretch between a start heading and the next end heading (the table of contents gives short ones)."""
    best = ""
    starts = [m for p in start_pats for m in re.finditer(p, text, flags=re.I)]
    for m in starts:
        tail = text[m.end():m.end() + 400_000]
        ends = [e.start() for p in end_pats for e in [re.search(p, tail, flags=re.I)] if e]
        body = tail[:min(ends)] if ends else ""
        if len(body) > len(best):
            best = body
    best = best.strip()
    if len(best) < 1500:
        return ""
    best = re.sub(r"\n(?:\d{1,3}|Table of Contents|[A-Z][A-Za-z&.,' ]{2,60} \| \d{4} Form 10-K \| \d+)\n", "\n", best)
    return best[:limit].rsplit(" ", 1)[0]


def prose(text, limit, skip=2500):
    """Fallback when the headings cannot be matched: the first real paragraphs of the document.
    Table-of-contents lines, headings and page numbers are short, so only long lines are kept."""
    lines = [ln for ln in text[skip:].split("\n") if len(ln) > 150]
    out = "\n".join(lines).strip()
    return out[:limit].rsplit(" ", 1)[0] if len(out) > 1500 else ""


def extract(text, form):
    if form.startswith("10-K"):
        starts = [r"\n\s*items?\s*1\s*(?:and\s*2\s*)?[.:\-–—]?\s*(?:and\s*2\s*[.:\-–—]?\s*)?business\b",
                  r"\n\s*item\s*1\s*[.:\-–—]?\s*(?:our\s+|the\s+)?business\b",
                  r"\n\s*item\s*1\s*[.:\-–—]?\s*description\s+of\s+(?:the\s+)?business\b"]
        ends = [r"\n\s*item\s*1a\s*[.:\-–—]?\s*risk", r"\n\s*item\s*1b\b", r"\n\s*item\s*2\s*[.:\-–—]?\s*properties", r"\n\s*item\s*3\s*[.:\-–—]?\s*legal"]
        biz = section(text, starts, ends, 9000)
        risk = section(text, [r"\n\s*items?\s*1a\s*[.:\-–—]?\s*risk\s*factors\b", r"\n\s*risk\s+factors\s*\n"],
                       [r"\n\s*item\s*1b\b", r"\n\s*item\s*1c\b", r"\n\s*item\s*2\s*[.:\-–—]?\s*properties", r"\n\s*item\s*3\s*[.:\-–—]?\s*legal"], 7000)
    else:   # 20-F / 40-F
        biz = section(text, [r"\n\s*item\s*4\s*[.:\-–—]?\s*information\s+on\s+the\s+company\b", r"\n\s*(?:b\.\s*)?business\s+overview\b",
                             r"\n\s*(?:our\s+)?business\s*\n", r"\n\s*description\s+of\s+(?:the\s+)?business\b"],
                      [r"\n\s*item\s*4a\b", r"\n\s*item\s*5\s*[.:\-–—]?\s*operating", r"\n\s*c\.\s*organizational\s+structure"], 9000)
        risk = section(text, [r"\n\s*(?:d\.\s*)?risk\s+factors\b"], [r"\n\s*item\s*4\s*[.:\-–—]?\s*information\s+on", r"\n\s*item\s*4\b", r"\n\s*item\s*5\b"], 7000)
    if not biz:
        biz = prose(text, 9000)
    return biz, risk


def biggest_doc(cik, acc, skip_doc):
    """The largest .htm document of the same filing, which for a cover-page filing holds the annual report."""
    base = "https://www.sec.gov/Archives/edgar/data/%d/%s/" % (cik, acc.replace("-", ""))
    raw = fetch(base + "index.json")
    if not raw:
        return None
    try:
        items = json.loads(raw)["directory"]["item"]
    except Exception:
        return None
    best, size = None, 0
    for it in items:
        name = it.get("name") or ""
        if not name.lower().endswith((".htm", ".html")) or name == skip_doc:
            continue
        try:
            n = int(it.get("size") or 0)
        except Exception:
            n = 0
        if n > size:
            best, size = name, n
    return (base + best) if (best and size > 200_000) else None


def one(t, cik):
    sub = fetch("https://data.sec.gov/submissions/CIK%010d.json" % cik)
    if not sub:
        return None
    r = (json.loads(sub).get("filings") or {}).get("recent") or {}
    pick = None
    for i, f in enumerate(r.get("form") or []):
        if f in FORMS and (r.get("primaryDocument") or [""] * (i + 1))[i]:
            pick = i
            break
    if pick is None:
        return None
    acc, doc = r["accessionNumber"][pick], r["primaryDocument"][pick]
    url = "https://www.sec.gov/Archives/edgar/data/%d/%s/%s" % (cik, acc.replace("-", ""), doc)
    old = os.path.join(HAVE, t + ".json")
    if HAVE and os.path.exists(old):
        try:
            prev = json.load(open(old))
            if prev.get("url") == url and len(prev.get("business") or "") > 1200:
                return "same"
        except Exception:
            pass
    time.sleep(0.15)
    raw = fetch(url)
    if not raw:
        return None
    text = to_text(raw)
    biz, risk = extract(text, r["form"][pick])
    if len(biz) < 1500 or len(text) < 60000:
        # some filings (often 40-F and 20-F) carry a short cover document and the annual report as an exhibit
        alt = biggest_doc(cik, acc, doc)
        if alt:
            time.sleep(0.15)
            raw2 = fetch(alt)
            if raw2:
                t2 = to_text(raw2)
                if len(t2) > len(text):
                    b2, r2 = extract(t2, r["form"][pick])
                    if len(b2) > len(biz):
                        url, biz, risk = alt, b2, (r2 or risk)
    return {"t": t, "cik": cik, "form": r["form"][pick], "filed": r["filingDate"][pick], "period": (r.get("reportDate") or [""] * (pick + 1))[pick],
            "url": url, "business": biz, "risks": risk}


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "ALL"
    tick = {}
    for f in glob.glob(os.path.join(ROOT, "data", "stocks", "*.json")):
        try:
            d = json.load(open(f))
            if d.get("ticker") and d.get("cik"):
                tick[d["ticker"]] = (int(d["cik"]), (d.get("market") or {}).get("mcap") or 0)
        except Exception:
            pass
    names = sorted(tick, key=lambda t: -tick[t][1]) if arg == "ALL" else [x.strip().upper() for x in arg.split(",") if x.strip().upper() in tick]
    sh, n = int(os.environ.get("SHARD", "0")), int(os.environ.get("SHARDS", "1"))
    names = [t for i, t in enumerate(names) if i % n == sh]
    os.makedirs(OUT, exist_ok=True)
    t0, ok, same, empty, fail = time.time(), 0, 0, 0, 0
    for t in names:
        if time.time() - t0 > MAX_SEC:
            print("time limit: stopped at", t)
            break
        try:
            res = one(t, tick[t][0])
        except Exception as ex:
            res = None
            print(t, "error", str(ex)[:80])
        if res == "same":
            same += 1
        elif res:
            json.dump(res, open(os.path.join(OUT, t + ".json"), "w"), ensure_ascii=False)
            ok += 1
            if not res["business"]:
                empty += 1
        else:
            fail += 1
        time.sleep(0.15)
    print("filings: %d written (%d without a business section), %d unchanged, %d not found, of %d" % (ok, empty, same, fail, len(names)))


if __name__ == "__main__":
    main()
