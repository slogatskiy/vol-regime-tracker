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
# Full 18-month multi-year series from MKTX monthly releases (Table 1A/1B).
SHARE = {
    "2025-01": (17.7, 12.0),
    "2025-02": (17.0, 11.1),
    "2025-03": (19.2, 12.5),
    "2025-04": (19.3, 13.5),
    "2025-05": (19.3, 12.2),
    "2025-06": (19.7, 12.4),
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

# MKTX estimate: electronic trading is ~60% of ALL US high-grade trading. Tradeweb does
# not disclose a comparable %-of-TRACE share (it reports ADV only), so the clean MKTX-vs-TW
# head-to-head is the US-credit ADV/growth comparison in the Tradeweb section, not a share line.
ELECTRONIC_PENETRATION_HG = 60.0

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
        "electronic_penetration_hg": ELECTRONIC_PENETRATION_HG,
        "note": f"Real MKTX estimated US high-grade share, 18 months. Multi-year trend: "
                f"{ANNUAL_HG['2024']}% (FY24) → {ANNUAL_HG['2025']}% (FY25); ran ~19-19.7% in "
                f"mid-2025 then slipped to a {trough['hg_share']}% trough in {trough['month']} on the "
                f"heavy new-issue surge (secondary share falls when primary spikes), now recovering "
                f"({latest['hg_share']}% latest). MKTX flags TRACE duplicate reporting understated "
                f"2026 share ~150-160bp in some months. Tradeweb reports ADV, not a comparable "
                f"%-of-TRACE share — so the MKTX-vs-TW head-to-head is the US-credit ADV/growth "
                f"comparison in the Tradeweb section (electronic is ~{ELECTRONIC_PENETRATION_HG:.0f}% "
                f"of all US HG trading, a MKTX/TW duopoly).",
        "series": series,
    })
    print(f"market share: {len(series)} months, latest HG {latest['hg_share']}%, "
          f"trough {trough['hg_share']}% ({trough['month']})")


if __name__ == "__main__":
    main()
