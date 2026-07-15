"""Metrics 2 & 3 — REAL MarketAxess monthly data, transcribed from the company's
monthly "Trading Volume Statistics" press releases (investor.marketaxess.com).

Each row is sourced from the official monthly release (Table 1 = ADV, Table 1D = FPM).
To update: add the new month below from the latest release and re-run. Values are
$ billions (ADV) and $/million (FPM); "excl. SD PT" (single-dealer portfolio trades),
matching the company's headline basis.

    python scripts/ingest_mktx.py
"""
from _common import save, today

CAGR_5Y = 9.8  # MKTX 5-year credit ADV CAGR (per the PM / company disclosure)

# month -> (total_credit_adv, us_high_grade_adv, us_high_yield_adv, total_credit_fpm)
# Source: MarketAxess monthly Trading Volume Statistics press releases.
# HY is left None for H2-2025 (not transcribed; not needed downstream).
MKTX = {
    "2025-01": (14.473, 6.912, 1.284, 141),
    "2025-02": (15.493, 7.061, 1.438, 143),
    "2025-03": (17.800, 8.700, 1.700, 135),
    "2025-04": (18.360, 8.595, 1.968, 138),
    "2025-05": (16.348, 7.649, 1.602, 138),
    "2025-06": (15.660, 7.170, 1.570, 138),
    "2025-07": (14.342, 6.389, None, 140),
    "2025-08": (13.086, 5.934, None, 141),
    "2025-09": (16.157, 7.358, None, 140),
    "2025-10": (15.999, 7.042, None, 140),
    "2025-11": (16.808, 7.594, None, 139),
    "2025-12": (13.546, 6.043, None, 138),
    "2026-01": (18.593, 8.110, 1.592, 132),
    "2026-02": (17.261, 7.779, 1.480, 136),
    "2026-03": (19.900, 9.200, 1.800, 131),
    "2026-04": (15.887, 6.802, 1.541, 134),
    "2026-05": (16.997, 7.728, 1.547, 128),
    "2026-06": (17.670, 8.230, 1.850, 125),  # HG June reported incl. SD PT in source
}

SRC = "https://investor.marketaxess.com/"

# 5-year ANNUAL history (for the multi-year view). Total credit ADV ($bn) and total-credit
# variable FPM ($). 2023/2024 exact from MKTX full-year results; 2021/2022 from reported
# annual/YoY figures (~); 2025 & 2026-YTD computed from the monthly rows above.
ANNUAL_ADV = {"2021": 10.4, "2022": 11.8, "2023": 12.545, "2024": 14.173}   # +2025/26 computed
ANNUAL_FPM = {"2021": 181.0, "2022": 165.0, "2023": 158.61, "2024": 150.26}  # +2025/26 computed


def main():
    months = sorted(MKTX)
    adv = {m: MKTX[m][0] for m in months}

    # ---- Metric 2: monthly total credit ADV + YoY ----
    vol_series = []
    for i, m in enumerate(months):
        yoy = None
        # year-ago month
        y, mo = m.split("-")
        prev = f"{int(y) - 1}-{mo}"
        if prev in adv:
            yoy = round((adv[m] / adv[prev] - 1) * 100, 1)
        vol_series.append({
            "month": m,
            "adv_bn": round(adv[m], 2),
            "us_high_grade_bn": round(MKTX[m][1], 2),
            "yoy_pct": yoy,
        })
    yoys = [r["yoy_pct"] for r in vol_series if r["yoy_pct"] is not None]
    avg_yoy = round(sum(yoys) / len(yoys), 1) if yoys else None

    # build 5y annual ADV/FPM, computing the years covered by the monthly rows
    def annual_from_monthly(idx):
        out = {}
        for m in months:
            yr = m[:4]
            out.setdefault(yr, []).append(MKTX[m][idx])
        return {y: round(sum(v) / len(v), 2) for y, v in out.items()}
    adv_by_year = annual_from_monthly(0)
    fpm_by_year = annual_from_monthly(3)
    annual_adv = [{"year": y, "adv_bn": v, "partial": y == "2026"}
                  for y, v in sorted({**ANNUAL_ADV, **adv_by_year}.items())]
    annual_fpm = [{"year": y, "credit_fpm": v, "partial": y == "2026"}
                  for y, v in sorted({**ANNUAL_FPM, **fpm_by_year}.items())]

    save("mktx_volume.json", {
        "last_updated": today(),
        "illustrative": False,
        "source": "MarketAxess monthly Trading Volume Statistics (Table 1)",
        "source_url": SRC,
        "unit": "Total credit ADV, $ billions/day (excl. SD PT)",
        "cagr_5y_pct": CAGR_5Y,
        "avg_yoy_2026_pct": avg_yoy,
        "annual_adv": annual_adv,
        "note": f"Real monthly ADV from MKTX releases. 2026 YTD YoY averages "
                f"~{avg_yoy}% vs the {CAGR_5Y}% 5-year CAGR — bull signal is YoY "
                f"sustained above the CAGR line. Apr-2026 dipped (-13% YoY) on a tough "
                f"comp vs the Apr-2025 tariff-vol surge.",
        "series": vol_series,
    })

    # ---- Metric 3: monthly total-credit FPM ----
    fpm_series = [{"month": m, "credit_fpm": MKTX[m][3]} for m in months]
    first = fpm_series[0]["credit_fpm"]
    last = fpm_series[-1]["credit_fpm"]
    save("mktx_fpm.json", {
        "last_updated": today(),
        "illustrative": False,
        "source": "MarketAxess monthly Trading Volume Statistics (Table 1D)",
        "source_url": SRC,
        "unit": "Total-credit variable transaction fees per $ million",
        "annual_fpm": annual_fpm,
        "note": f"Real monthly total-credit FPM. Compression from ${first} (Jan-2025) "
                f"to ${last} (Jun-2026) — mix shift toward lower-fee protocols "
                f"(portfolio trading, dealer-RFQ, Open Trading) and products. "
                f"Total-rates FPM has moved the other way (rising), a real offset.",
        "series": fpm_series,
    })
    print(f"MKTX: {len(months)} months. 2026 avg YoY {avg_yoy}%. FPM {first}->{last}.")


if __name__ == "__main__":
    main()
