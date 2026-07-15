"""Metric 7 — REAL MKTX vs Tradeweb, US credit e-trading.

Compares like-for-like US credit electronic ADV:
  - MKTX  = U.S. high-grade + U.S. high-yield ADV (excl. SD PT), from MKTX releases.
  - TW    = fully-electronic U.S. credit ADV, from Tradeweb monthly activity reports.

If TW consistently out-grows MKTX, the vol/turnover benefit is accruing to the
competitor. Levels are broadly comparable; the YoY growth gap is the signal.

    python scripts/ingest_tradeweb.py
"""
from _common import save, today
from ingest_mktx import MKTX

# Tradeweb fully-electronic U.S. credit ADV ($bn) and reported YoY %, by month.
# Source: Tradeweb monthly activity reports / press releases. Feb-2026 not disclosed
# in an accessible release at build time -> left None (shown as a gap).
TW = {
    "2026-01": (9.4, 24.4),
    "2026-02": (None, None),
    "2026-03": (10.7, 12.3),
    "2026-04": (9.2, 3.9),
    "2026-05": (10.0, 20.4),
    "2026-06": (10.5, 29.3),
}

SRC = "https://www.tradeweb.com/newsroom/monthly-activity-reports/"

# 5-year ANNUAL total revenue ($ millions), TW vs MKTX. Source: company results.
# year -> (tw_revenue_mm, mktx_revenue_mm)
ANNUAL_REVENUE = {
    "2021": (1076.0, 698.95),
    "2022": (1189.0, 718.30),
    "2023": (1338.0, 752.55),
    "2024": (1726.0, 817.10),
    "2025": (2052.0, 846.27),
}

# Metric 7b — quarterly TOTAL revenue ($ millions), TW vs MKTX. Source: company results.
# quarter -> (tw_revenue_mm, mktx_revenue_mm)
REVENUE = {
    "2024Q1": (408.74, 210.32),
    "2024Q2": (404.95, 197.66),
    "2024Q3": (448.92, 206.72),
    "2024Q4": (463.34, 202.40),
    "2025Q1": (509.68, 208.58),
    "2025Q2": (512.97, 219.46),
    "2025Q3": (508.60, 208.82),
    "2025Q4": (521.18, 209.41),
    "2026Q1": (617.76, 233.38),
}


def mktx_us_credit(m):
    """MKTX US credit = high-grade + high-yield ADV (both excl. SD PT)."""
    _, hg, hy, _ = MKTX[m]
    if hg is None or hy is None:
        return None
    return round(hg + hy, 2)


def main():
    months = sorted(TW)
    series = []
    for m in months:
        tw_adv, tw_yoy = TW[m]
        mk = mktx_us_credit(m)
        # prior-year MKTX for YoY
        y, mo = m.split("-")
        prev = f"{int(y) - 1}-{mo}"
        mk_prev = mktx_us_credit(prev)
        mk_yoy = round((mk / mk_prev - 1) * 100, 1) if (mk and mk_prev) else None
        series.append({
            "month": m,
            "mktx_us_credit_bn": mk,
            "tw_us_credit_bn": tw_adv,
            "mktx_yoy": mk_yoy,
            "tw_yoy": tw_yoy,
        })

    # growth-gap read on the months where both YoY exist
    gaps = [r["tw_yoy"] - r["mktx_yoy"] for r in series
            if r["tw_yoy"] is not None and r["mktx_yoy"] is not None]
    avg_gap = round(sum(gaps) / len(gaps), 1) if gaps else None

    # ---- revenue trends (TW vs MKTX), quarterly with YoY ----
    quarters = sorted(REVENUE)
    rev = []
    for q in quarters:
        tw_r, mk_r = REVENUE[q]
        yr, qn = q[:4], q[4:]
        prev = f"{int(yr) - 1}{qn}"
        tw_yoy = mk_yoy = None
        if prev in REVENUE:
            tw_yoy = round((tw_r / REVENUE[prev][0] - 1) * 100, 1)
            mk_yoy = round((mk_r / REVENUE[prev][1] - 1) * 100, 1)
        rev.append({"q": q, "tw_rev_mm": tw_r, "mktx_rev_mm": mk_r,
                    "tw_rev_yoy": tw_yoy, "mktx_rev_yoy": mk_yoy})
    latest_rev = rev[-1]
    rev_ratio = round(latest_rev["tw_rev_mm"] / latest_rev["mktx_rev_mm"], 2)

    # 5-year annual revenue
    annual_rev = [{"year": y, "tw_rev_mm": ANNUAL_REVENUE[y][0], "mktx_rev_mm": ANNUAL_REVENUE[y][1]}
                  for y in sorted(ANNUAL_REVENUE)]
    ar0, ar1 = annual_rev[0], annual_rev[-1]
    tw_5y = round((ar1["tw_rev_mm"] / ar0["tw_rev_mm"] - 1) * 100)
    mk_5y = round((ar1["mktx_rev_mm"] / ar0["mktx_rev_mm"] - 1) * 100)

    save("tradeweb.json", {
        "last_updated": today(),
        "illustrative": False,
        "source": "MarketAxess & Tradeweb monthly activity reports + quarterly results",
        "source_url": SRC,
        "unit": "US credit ADV, $ billions/day (electronic)",
        "avg_growth_gap_pp": avg_gap,
        "rev_ratio_latest": rev_ratio,
        "note": "MKTX = US high-grade + high-yield ADV; TW = fully-electronic US credit "
                f"ADV. Tradeweb YoY growth has out-run MKTX by ~{avg_gap}pp on average "
                "across 2026 — the vol benefit is accruing disproportionately to the "
                "competitor, and TW led US credit e-trading outright in June-2026. On "
                f"revenue, TW is now ~{rev_ratio}x MKTX ($" f"{latest_rev['tw_rev_mm']:.0f}M vs "
                f"${latest_rev['mktx_rev_mm']:.0f}M in {latest_rev['q']}) and growing "
                f"{latest_rev['tw_rev_yoy']}% vs {latest_rev['mktx_rev_yoy']}% YoY.",
        "series": series,
        "revenue": rev,
        "annual_revenue": annual_rev,
        "rev_5y_growth": {"tw_pct": tw_5y, "mktx_pct": mk_5y},
    })
    print(f"TW vs MKTX: {len(series)} ADV months (gap {avg_gap}pp), "
          f"{len(rev)} revenue quarters (TW ${latest_rev['tw_rev_mm']:.0f}M = {rev_ratio}x MKTX)")


if __name__ == "__main__":
    main()
