"""Metric 1 — ICE BofA MOVE Index (bond-market implied volatility).

Live, keyless: Yahoo Finance ^MOVE. Writes docs/data/move.json with a daily series
plus the current level and the two watch thresholds (90 = sustained-break watch,
100 = significant vol-regime change).

    python scripts/fetch_move.py
"""
import datetime as dt
from _common import get, save, today

THRESH_WATCH = 90     # sustained break above -> elevated regime
THRESH_REGIME = 100   # above -> significant vol-regime change


def main():
    # ~5y of daily closes
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EMOVE"
    js = get(url, {"range": "5y", "interval": "1d"}).json()
    res = js["chart"]["result"][0]
    ts = res["timestamp"]
    closes = res["indicators"]["quote"][0]["close"]
    meta = res["meta"]

    series = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        d = dt.datetime.utcfromtimestamp(t).date().isoformat()
        series.append({"date": d, "value": round(c, 2)})

    current = round(meta.get("regularMarketPrice", series[-1]["value"]), 2)
    last90 = [p["value"] for p in series[-90:]]

    out = {
        "last_updated": today(),
        "source": "ICE BofA MOVE Index via Yahoo Finance (^MOVE)",
        "source_url": "https://finance.yahoo.com/quote/%5EMOVE",
        "current": current,
        "week52_high": round(meta.get("fiftyTwoWeekHigh", 0), 2),
        "week52_low": round(meta.get("fiftyTwoWeekLow", 0), 2),
        "avg_90d": round(sum(last90) / len(last90), 1),
        "thresholds": {"watch": THRESH_WATCH, "regime": THRESH_REGIME},
        "days_above_watch_90d": sum(1 for v in last90 if v > THRESH_WATCH),
        "series": series,
    }
    save("move.json", out)
    print(f"MOVE current={current}  90d avg={out['avg_90d']}  "
          f"days>90 (90d)={out['days_above_watch_90d']}")


if __name__ == "__main__":
    main()
