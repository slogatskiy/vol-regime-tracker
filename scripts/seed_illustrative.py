"""Seed the ILLUSTRATIVE data files (metrics that lack a free public API and must be
ingested from company reports / SIFMA / CME). Every series written here is flagged
`"illustrative": true` so the dashboard labels it clearly. Real anchor points that we
are confident about are marked in each file's `anchors`/notes.

Replace these by dropping sourced CSVs into data_raw/ and writing a proper ingest_*.py,
or by editing the JSON directly. This script just gives the page a coherent first paint.

    python scripts/seed_illustrative.py
"""
from _common import save, today

CAGR_5Y = 9.8  # MKTX 5-year ADV CAGR, given by the PM


def months(start_year, start_month, n):
    out = []
    y, m = start_year, start_month
    for _ in range(n):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def mktx_volume():
    """Metric 2 — MKTX monthly total credit ADV ($bn) and YoY growth."""
    lbls = months(2023, 1, 42)  # Jan-2023 .. Jun-2026
    # illustrative ADV path trending up with seasonality; ~$13.5bn -> ~$16.5bn
    base = 13.4
    adv = []
    for i, _ in enumerate(lbls):
        seasonal = 0.8 if (i % 12) in (0, 1, 2) else (-0.4 if (i % 12) in (6, 7) else 0)
        adv.append(round(base + i * 0.075 + seasonal, 2))
    series = []
    for i, lbl in enumerate(lbls):
        yoy = None
        if i >= 12:
            yoy = round((adv[i] / adv[i - 12] - 1) * 100, 1)
        series.append({"month": lbl, "adv_bn": adv[i], "yoy_pct": yoy})
    save("mktx_volume.json", {
        "last_updated": today(),
        "illustrative": True,
        "source": "MarketAxess monthly volume press releases (to be ingested)",
        "source_url": "https://investor.marketaxess.com/",
        "unit": "Total credit ADV, $ billions",
        "cagr_5y_pct": CAGR_5Y,
        "note": "Watch YoY growth accelerating ABOVE the 5-year CAGR of "
                f"{CAGR_5Y}% as the bull signal. Series is illustrative until the "
                "monthly IR releases are ingested; shape/scale approximate.",
        "series": series,
    })


def mktx_fpm():
    """Metric 3 — Variable transaction fees per million ($/mm), by segment (quarterly)."""
    q = ["2023Q1", "2023Q2", "2023Q3", "2023Q4", "2024Q1", "2024Q2",
         "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1"]
    # illustrative compression: high-grade FPM drifting down on mix shift to lower-fee protocols
    hg = [172, 170, 168, 166, 165, 163, 160, 158, 156, 153, 151, 149, 147]
    hy = [325, 322, 318, 315, 312, 308, 305, 300, 297, 293, 290, 286, 283]
    blended = [round(h * 0.55 + y * 0.45) for h, y in zip(hg, hy)]
    series = [{"q": q[i], "high_grade": hg[i], "high_yield": hy[i], "blended": blended[i]}
              for i in range(len(q))]
    save("mktx_fpm.json", {
        "last_updated": today(),
        "illustrative": True,
        "source": "MarketAxess 10-Q / 10-K & earnings decks (Variable transaction FPM)",
        "source_url": "https://investor.marketaxess.com/",
        "unit": "Variable transaction fees per $ million traded",
        "note": "Compression signals mix shift toward lower-fee protocols "
                "(portfolio trading, dealer RFQ, Open Trading). Illustrative trend "
                "until quarterly filings are ingested.",
        "series": series,
    })


def market_share():
    """Metric 4 — US High-Grade estimated market share, MKTX vs Tradeweb (quarterly)."""
    q = ["2023Q1", "2023Q2", "2023Q3", "2023Q4", "2024Q1", "2024Q2",
         "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1"]
    mktx = [20.8, 20.3, 20.1, 19.7, 19.9, 19.4, 19.1, 18.8, 19.2, 18.9, 18.6, 18.9, 17.9]
    tw = [12.1, 12.6, 12.9, 13.4, 13.2, 13.8, 14.1, 14.6, 14.3, 14.9, 15.3, 15.1, 15.8]
    series = [{"q": q[i], "mktx_pct": mktx[i], "tradeweb_pct": tw[i]} for i in range(len(q))]
    save("market_share.json", {
        "last_updated": today(),
        "illustrative": True,
        "source": "MKTX & Tradeweb estimated share of US high-grade TRACE volume",
        "source_url": "https://www.finra.org/finra-data/fixed-income",
        "unit": "% of US high-grade electronic + TRACE-eligible volume (est.)",
        "note": "Jan-2026 MKTX share dipped on heavy new-issue activity (secondary "
                "share falls when primary surges) — watch for recovery. Tradeweb "
                "trend is the competitive watch-item. Illustrative until TRACE-based "
                "estimates are ingested.",
        "series": series,
    })


def tradeweb():
    """Metric 7 — Tradeweb vs MKTX growth (quarterly YoY, %) for volume & revenue."""
    q = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2",
         "2025Q3", "2025Q4", "2026Q1"]
    tw_rev = [33, 36, 32, 25, 24, 23, 22, 21, 20]
    mktx_rev = [8, 11, 4, 6, 7, 5, 4, 6, 3]
    tw_vol = [50, 55, 40, 32, 30, 28, 26, 24, 23]
    mktx_vol = [12, 15, 9, 10, 11, 8, 7, 9, 6]
    series = [{"q": q[i], "tw_rev_yoy": tw_rev[i], "mktx_rev_yoy": mktx_rev[i],
               "tw_vol_yoy": tw_vol[i], "mktx_vol_yoy": mktx_vol[i]}
              for i in range(len(q))]
    save("tradeweb.json", {
        "last_updated": today(),
        "illustrative": True,
        "source": "Tradeweb (TW) & MarketAxess (MKTX) quarterly reports",
        "source_url": "https://www.tradeweb.com/newsroom/monthly-activity-reports/",
        "unit": "YoY growth, %",
        "note": "If TW consistently outpaces MKTX, the vol benefit is accruing to the "
                "competitor. Illustrative until both IR feeds are ingested.",
        "series": series,
    })


def new_issue():
    """Metric 8 — US corporate new-issue volume ($bn/month), IG & HY, with YoY."""
    lbls = months(2023, 1, 42)
    ig_base = [135, 150, 165, 120, 130, 110, 95, 100, 140, 120, 95, 60]
    hy_base = [28, 32, 30, 22, 26, 20, 15, 18, 30, 25, 18, 10]
    series = []
    ig_hist, hy_hist = [], []
    for i, lbl in enumerate(lbls):
        mi = i % 12
        drift = 1.0 + i * 0.004
        ig = round(ig_base[mi] * drift)
        hy = round(hy_base[mi] * drift)
        # Jan-2026 surge (+95% YoY high-grade turnover narrative)
        if lbl == "2026-01":
            ig = round(ig * 1.9)
            hy = round(hy * 1.5)
        ig_hist.append(ig)
        hy_hist.append(hy)
        yoy = None
        if i >= 12:
            yoy = round((ig / ig_hist[i - 12] - 1) * 100)
        series.append({"month": lbl, "ig_bn": ig, "hy_bn": hy, "ig_yoy_pct": yoy})
    save("new_issue.json", {
        "last_updated": today(),
        "illustrative": True,
        "source": "SIFMA US corporate issuance (monthly)",
        "source_url": "https://www.sifma.org/resources/research/us-corporate-bonds-statistics/",
        "unit": "Gross new-issue volume, $ billions/month",
        "note": "High new-issue activity drives secondary turnover. Jan-2026 spike "
                "reflects the +95% YoY high-grade turnover episode. Illustrative until "
                "SIFMA monthly tables are ingested.",
        "series": series,
    })


def fed_funds_path():
    """Metric 10 — market-implied fed funds path vs the FOMC dot plot (SEP median)."""
    meetings = ["2026-01", "2026-03", "2026-04", "2026-06", "2026-07",
                "2026-09", "2026-10", "2026-12"]
    market = [4.13, 4.00, 3.88, 3.70, 3.63, 3.50, 3.45, 3.38]  # implied from FF futures
    dots = [4.13, 4.13, 3.88, 3.88, 3.63, 3.63, 3.63, 3.38]    # SEP median (step function)
    series = [{"meeting": meetings[i], "market_implied": market[i], "dot_median": dots[i],
               "divergence_bps": round((market[i] - dots[i]) * 100)}
              for i in range(len(meetings))]
    save("fed_funds_path.json", {
        "last_updated": today(),
        "illustrative": True,
        "source": "Fed funds futures (implied path) vs FOMC SEP dot plot",
        "source_url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html",
        "unit": "Implied fed funds rate, %",
        "note": "Divergence between the market path and the dots indicates markets are "
                "pricing independently — a hallmark of the post-guidance era. "
                "Illustrative until FF futures settlements are ingested.",
        "series": series,
    })


def fomc_taskforce():
    """Metric 6 — FOMC task-force tracker (qualitative; public info)."""
    save("fomc_taskforce.json", {
        "last_updated": today(),
        "illustrative": False,
        "source": "Federal Reserve communications & press",
        "source_url": "https://www.federalreserve.gov/newsevents/pressreleases.htm",
        "note": "Two Fed reviews are the medium-term regime drivers. Recommendations "
                "expected by year-end 2026. Update status as announcements land.",
        "items": [
            {"name": "Monetary-policy framework review",
             "status": "In progress", "expected": "2026",
             "detail": "Five-year review of strategy, tools and communications "
                       "(the '2%/average-inflation-targeting' framework)."},
            {"name": "Communications task force",
             "status": "Watch", "expected": "H2 2026",
             "detail": "Forward-guidance & SEP/dot-plot communication practices — "
                       "central to the FOMC-centric → data-centric vol shift."},
            {"name": "Balance-sheet task force",
             "status": "Watch", "expected": "H2 2026",
             "detail": "Ample-reserves regime, QT end-state and SOMA composition — "
                       "shapes dealer capacity and rates vol."},
        ],
    })


def main():
    # NOTE: mktx_volume, mktx_fpm, market_share, tradeweb, new_issue, fed_funds_path are
    # now produced by the REAL ingest scripts (ingest_*.py) and must NOT be overwritten here.
    # Only the qualitative FOMC task-force tracker is seeded from this file.
    fomc_taskforce()
    print("seeded fomc_taskforce.json (all other metrics now come from real ingest_*.py).")


if __name__ == "__main__":
    main()
