"""Metric 5 — CPI & Payroll day volatility in the Treasury market.

Thesis: as the regime shifts from FOMC-centric to data-centric vol, the 2y/10y
Treasury reaction to CPI and jobs prints should get LARGER relative to a normal day.
We measure the move in a 3-day window (pre -> post) around each release.

Data: FRED DGS2 / DGS10 (keyless daily). Release dates are curated below and are
easy to extend — edit RELEASES and re-run.

    python scripts/build_data_day_vol.py
"""
from _common import fred_csv, save, today

# BLS releases. CPI = Consumer Price Index, NFP = Employment Situation (jobs).
# Dates are the official release DATE (data usually 8:30 ET). Extend as needed.
RELEASES = [
    # 2025
    ("2025-09-11", "CPI"), ("2025-10-03", "NFP"), ("2025-10-15", "CPI"),
    ("2025-11-07", "NFP"), ("2025-11-13", "CPI"), ("2025-12-05", "NFP"),
    ("2025-12-10", "CPI"),
    # 2026
    ("2026-01-09", "NFP"), ("2026-01-13", "CPI"), ("2026-02-06", "NFP"),
    ("2026-02-11", "CPI"), ("2026-03-06", "NFP"), ("2026-03-11", "CPI"),
    ("2026-04-03", "NFP"), ("2026-04-10", "CPI"), ("2026-05-08", "NFP"),
    ("2026-05-13", "CPI"), ("2026-06-05", "NFP"), ("2026-06-10", "CPI"),
    ("2026-07-02", "NFP"), ("2026-07-10", "CPI"),
]


def as_map(series):
    return {d: v for d, v in series}, [d for d, _ in series]


def surrounding(dates, target):
    """Return (pre_date, on_date, post_date) around a release using trading days."""
    before = [d for d in dates if d < target]
    onafter = [d for d in dates if d >= target]
    if not before or not onafter:
        return None
    pre = before[-1]
    on = onafter[0]
    post = onafter[1] if len(onafter) > 1 else onafter[0]
    return pre, on, post


def main():
    y2 = fred_csv("DGS2", start="2025-06-01")
    y10 = fred_csv("DGS10", start="2025-06-01")
    m2, d2 = as_map(y2)
    m10, d10 = as_map(y10)

    rows = []
    for date, kind in RELEASES:
        s2 = surrounding(d2, date)
        s10 = surrounding(d10, date)
        if not s2 or not s10:
            continue
        pre2, on2, post2 = s2
        pre10, on10, post10 = s10
        # window move (post - pre), and 1-day move (on - pre), in basis points
        win2 = round((m2[post2] - m2[pre2]) * 100)
        win10 = round((m10[post10] - m10[pre10]) * 100)
        day2 = round((m2[on2] - m2[pre2]) * 100)
        day10 = round((m10[on10] - m10[pre10]) * 100)
        rows.append({
            "date": date, "kind": kind,
            "d2y_window_bps": win2, "d10y_window_bps": win10,
            "d2y_day_bps": day2, "d10y_day_bps": day10,
            "abs2y": abs(win2), "abs10y": abs(win10),
        })

    # simple regime read: average absolute window move, recent vs earlier half
    if rows:
        half = len(rows) // 2 or 1
        early = rows[:half]
        recent = rows[half:]
        def avg(rs, k):
            return round(sum(r[k] for r in rs) / len(rs), 1) if rs else 0
        summary = {
            "avg_abs_2y_recent": avg(recent, "abs2y"),
            "avg_abs_2y_early": avg(early, "abs2y"),
            "avg_abs_10y_recent": avg(recent, "abs10y"),
            "avg_abs_10y_early": avg(early, "abs10y"),
        }
        summary["accelerating_2y"] = summary["avg_abs_2y_recent"] > summary["avg_abs_2y_early"]
        summary["accelerating_10y"] = summary["avg_abs_10y_recent"] > summary["avg_abs_10y_early"]
    else:
        summary = {}

    out = {
        "last_updated": today(),
        "source": "FRED DGS2 / DGS10 (daily constant-maturity Treasury yields)",
        "source_url": "https://fred.stlouisfed.org/series/DGS2",
        "note": "Move = change in yield (bps) across a 3-day window (pre -> post) "
                "bracketing each release; day = release-day move vs prior close.",
        "summary": summary,
        "rows": rows,
    }
    save("data_day_vol.json", out)
    print(f"data-day vol rows={len(rows)}  summary={summary}")


if __name__ == "__main__":
    main()
