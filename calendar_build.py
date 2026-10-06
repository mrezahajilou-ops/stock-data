#!/usr/bin/env python3
"""Earnings calendar: last 7 days + next 28 days (Nasdaq earnings calendar API).

Output: calendar/earnings.json on the orphan branch `calendar`:
  {"as_of": "...", "days": {"2026-10-14": [{"t","n","time","mcap","q","f","ly","act","sur","s"}, ...]}}
  time: pre | after | na ; f = consensus EPS forecast, ly = last year's EPS, act/sur = reported EPS / surprise %
  s = our total score (0-5) when the stock is covered on the site.
"""
import json, os, time, datetime as dt, urllib.request

ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
OUT = os.path.join(ROOT, 'calendar')
STOCKS = os.path.join(ROOT, 'data', 'stocks')
HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
       'Accept': 'application/json, text/plain, */*', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}
TIME = {'time-pre-market': 'pre', 'time-after-hours': 'after'}


def num(s):
    if s in (None, '', 'N/A'):
        return None
    s = str(s).replace('$', '').replace(',', '').replace('%', '').strip()
    neg = s.startswith('(') and s.endswith(')')
    try:
        v = float(s.strip('()'))
    except ValueError:
        return None
    return -v if neg else v


def day(d):
    url = 'https://api.nasdaq.com/api/calendar/earnings?date=' + d
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=30) as r:
                return ((json.loads(r.read()).get('data') or {}).get('rows')) or []
        except Exception:
            time.sleep(3 * (a + 1))
    return []


def score(t):
    try:
        return (json.load(open(os.path.join(STOCKS, t + '.json'))).get('scores') or {}).get('total')
    except Exception:
        return None


def main():
    today = dt.date.today()
    days = {}
    for k in range(-7, 29):
        d = today + dt.timedelta(days=k)
        if d.weekday() >= 5:
            continue
        rows = []
        for r in day(d.isoformat()):
            t = (r.get('symbol') or '').strip().upper().replace('.', '-').replace('/', '-')
            mc = num(r.get('marketCap'))
            if not t or not mc or mc < 3e8:  # skip micro caps
                continue
            rows.append({'t': t, 'n': (r.get('name') or '').strip(), 'time': TIME.get(r.get('time'), 'na'), 'mcap': mc,
                         'q': r.get('fiscalQuarterEnding'), 'f': num(r.get('epsForecast')), 'ly': num(r.get('lastYearEPS')),
                         'act': num(r.get('eps')), 'sur': num(r.get('surprise')), 's': score(t)})
        rows.sort(key=lambda x: -x['mcap'])
        days[d.isoformat()] = rows[:200]
        time.sleep(0.4)
    os.makedirs(OUT, exist_ok=True)
    json.dump({'as_of': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'days': days},
              open(os.path.join(OUT, 'earnings.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    print('days', len(days), 'events', sum(len(v) for v in days.values()))


if __name__ == '__main__':
    main()
