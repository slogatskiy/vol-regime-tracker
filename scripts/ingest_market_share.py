"""Metric 4 (page section 07) — REAL MKTX US high-grade estimated market share.

MarketAxess reports its estimated market share of US high-grade and high-yield TRACE
volume in Table 1B of each monthly Trading Volume Statistics release. Figures are the
excl-SD-PT (single-dealer portfolio trade) basis, MKTX's standard aggregated basis.

The PM's watch-item: "January 2026 share declined due to new-issue activity — watch for
recovery." That shows up directly below (Feb-2026 trough 16.7% -> recovery toward ~18%).

    python scripts/ingest_market_share.py
"""
from _common import save, today

# month -> (us_high_grade_share_pct, us_high_yield_share_pct)  % of TRACE, excl SD PT
SHARE = {
    "2025-07": (17.7, 11.5),
    "2025-08": (18.8, 12.7),
    "2025-09": (17.0, 11.5),
    "2025-10": (18.1, 13.1),
    "2025-11": (18.5, 13.2),
    "2025-12": (18.9, 13.5),   # Dec HG excl≈18.9 (incl 19.3); HY approx
    "2026-01": (17.6, 13.2),
    "2026-02": (16.7, 12.5),   # trough — heavy new issue depresses secondary share
    "2026-03": (18.7, 15.4),
    "2026-04": (16.8, 13.6),   # TRACE duplicate reports inflated HG volumes ~8% this month
    "2026-05": (17.8, 13.9),
    "2026-06": (17.9, 14.9),
}

# Full-year estimated US high-grade share (multi-year context).
ANNUAL_HG = {"2024": 19.0, "2025": 18.4}

SRC = "https://investor.marketaxess.com/"


def main():
    months = sorted(SHARE)
    series = [{"month": m, "hg_share": SHARE[m][0], "hy_share": SHARE[m][1]} for m in months]
    latest = series[-1]
    trough = min(series, key=lambda r: r["hg_share"])
    save("market_share.json", {
        "last_updated": today(),
        "illustrative": False,
        "source": "MarketAxess estimated market share of US high-grade/high-yield TRACE (Table 1B, excl SD PT)",
        "source_url": SRC,
        "unit": "% of US high-grade TRACE volume (est.)",
        "annual_hg": ANNUAL_HG,
        "note": f"Real MKTX estimated US high-grade share. Multi-year trend: {ANNUAL_HG['2024']}% "
                f"(FY24) → {ANNUAL_HG['2025']}% (FY25). 2026 dipped to a {trough['hg_share']}% "
                f"trough in {trough['month']} on the heavy new-issue surge (secondary share falls "
                f"when primary spikes) and is recovering ({latest['hg_share']}% latest). MKTX flags "
                f"that TRACE duplicate reporting understated 2026 share by ~150-160bp in some months. "
                f"Head-to-head vs Tradeweb is in the US-credit-e-trading section.",
        "series": series,
    })
    print(f"market share: {len(series)} months, latest HG {latest['hg_share']}%, "
          f"trough {trough['hg_share']}% ({trough['month']})")


if __name__ == "__main__":
    main()
