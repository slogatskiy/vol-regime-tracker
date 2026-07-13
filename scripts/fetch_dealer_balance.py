"""Metric 9 — Primary dealer balance-sheet capacity (Treasury positions).

Thesis: reduced dealer capacity to warehouse risk amplifies the shift to electronic
platforms (MKTX/TW). We track primary dealers' NET outright positions in U.S.
Treasuries (ex-TIPS), weekly, from the NY Fed Primary Dealer Statistics API (keyless).

Net position = long - short, in $ millions. We sum the maturity buckets to a total
and keep the latest bucket breakdown.

    python scripts/fetch_dealer_balance.py
"""
from _common import get, save, today, fred_csv

# keyid -> short bucket label. Net (long-short) outright UST positions, ex-TIPS.
BUCKETS = [
    ("PDPOSGS-B", "Bills"),
    ("PDPOSGSC-L2", "≤2y"),
    ("PDPOSGSC-G2L3", "2–3y"),
    ("PDPOSGSC-G3L6", "3–6y"),
    ("PDPOSGSC-G6L7", "6–7y"),
    ("PDPOSGSC-G7L11", "7–11y"),
    ("PDPOSGSC-G11L21", "11–21y"),
    ("PDPOSGSC-G21", ">21y"),
]

API = "https://markets.newyorkfed.org/api/pd/get/{kid}.json"


def fetch_series(kid):
    js = get(API.format(kid=kid)).json()
    out = {}
    for row in js["pd"]["timeseries"]:
        v = row.get("value")
        if v in (None, "", "*"):
            continue
        out[row["asofdate"]] = float(v)
    return out


def main():
    series = {kid: fetch_series(kid) for kid, _ in BUCKETS}

    # union of dates, keep only dates present in the bills series (the anchor)
    all_dates = sorted(set().union(*[set(s.keys()) for s in series.values()]))
    total = []
    for d in all_dates:
        vals = [series[kid].get(d) for kid, _ in BUCKETS]
        if any(v is None for v in vals):
            continue
        total.append({"date": d, "value": round(sum(vals))})

    total = total[-260:]  # ~5y of weekly points
    latest_date = total[-1]["date"] if total else None
    breakdown = []
    if latest_date:
        for kid, label in BUCKETS:
            breakdown.append({"bucket": label,
                              "value": round(series[kid].get(latest_date, 0))})

    cur = total[-1]["value"] if total else 0
    yr_ago = total[-52]["value"] if len(total) >= 52 else (total[0]["value"] if total else 0)

    # --- leverage / capacity utilization: dealer inventory vs the total Treasury market ---
    # If dealers don't scale positions with the exploding debt pile, relative capacity is
    # shrinking — the mechanism that pushes price-making onto electronic platforms.
    debt = fred_csv("GFDEBTN", start="2020-01-01")   # total public debt, $millions, quarterly
    util = []
    for p in total:
        d = p["date"]
        prior = [v for dt, v in debt if dt <= d]
        if not prior:
            continue
        util.append({"date": d, "pct": round(p["value"] / prior[-1] * 100, 3)})
    util_cur = util[-1]["pct"] if util else None
    util_2y = util[-104]["pct"] if len(util) >= 104 else (util[0]["pct"] if util else None)

    out = {
        "last_updated": today(),
        "source": "FRBNY Primary Dealer Statistics (net outright UST positions, ex-TIPS)",
        "source_url": "https://www.newyorkfed.org/markets/primarydealer_statistics/financial_condition",
        "unit": "$ millions (net long minus short)",
        "current": cur,
        "current_date": latest_date,
        "yoy_change": cur - yr_ago,
        "breakdown_latest": breakdown,
        "series": total,
        "utilization": {
            "unit": "dealer net UST positions as % of total public debt outstanding",
            "source": "FRBNY positions / FRED GFDEBTN (total public debt)",
            "current_pct": util_cur,
            "two_year_ago_pct": util_2y,
            "series": util,
        },
    }
    save("dealer_balance.json", out)
    print(f"dealer net UST position: {cur:,} $mm as of {latest_date}  "
          f"(YoY {cur - yr_ago:+,}); utilization {util_cur}% vs {util_2y}% (2y ago)")


if __name__ == "__main__":
    main()
