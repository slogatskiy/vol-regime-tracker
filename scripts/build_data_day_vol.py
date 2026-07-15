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
    # 2022
    ("2022-01-07", "NFP"), ("2022-01-12", "CPI"), ("2022-02-04", "NFP"), ("2022-02-10", "CPI"),
    ("2022-03-04", "NFP"), ("2022-03-10", "CPI"), ("2022-04-01", "NFP"), ("2022-04-12", "CPI"),
    ("2022-05-06", "NFP"), ("2022-05-11", "CPI"), ("2022-06-03", "NFP"), ("2022-06-10", "CPI"),
    ("2022-07-08", "NFP"), ("2022-07-13", "CPI"), ("2022-08-05", "NFP"), ("2022-08-10", "CPI"),
    ("2022-09-02", "NFP"), ("2022-09-13", "CPI"), ("2022-10-07", "NFP"), ("2022-10-13", "CPI"),
    ("2022-11-04", "NFP"), ("2022-11-10", "CPI"), ("2022-12-02", "NFP"), ("2022-12-13", "CPI"),
    # 2023
    ("2023-01-06", "NFP"), ("2023-01-12", "CPI"), ("2023-02-03", "NFP"), ("2023-02-14", "CPI"),
    ("2023-03-10", "NFP"), ("2023-03-14", "CPI"), ("2023-04-07", "NFP"), ("2023-04-12", "CPI"),
    ("2023-05-05", "NFP"), ("2023-05-10", "CPI"), ("2023-06-02", "NFP"), ("2023-06-13", "CPI"),
    ("2023-07-07", "NFP"), ("2023-07-12", "CPI"), ("2023-08-04", "NFP"), ("2023-08-10", "CPI"),
    ("2023-09-01", "NFP"), ("2023-09-13", "CPI"), ("2023-10-06", "NFP"), ("2023-10-12", "CPI"),
    ("2023-11-03", "NFP"), ("2023-11-14", "CPI"), ("2023-12-08", "NFP"), ("2023-12-12", "CPI"),
    # 2024
    ("2024-01-05", "NFP"), ("2024-01-11", "CPI"), ("2024-02-02", "NFP"), ("2024-02-13", "CPI"),
    ("2024-03-08", "NFP"), ("2024-03-12", "CPI"), ("2024-04-05", "NFP"), ("2024-04-10", "CPI"),
    ("2024-05-03", "NFP"), ("2024-05-15", "CPI"), ("2024-06-07", "NFP"), ("2024-06-12", "CPI"),
    ("2024-07-05", "NFP"), ("2024-07-11", "CPI"), ("2024-08-02", "NFP"), ("2024-08-14", "CPI"),
    ("2024-09-06", "NFP"), ("2024-09-11", "CPI"), ("2024-10-04", "NFP"), ("2024-10-10", "CPI"),
    ("2024-11-01", "NFP"), ("2024-11-13", "CPI"), ("2024-12-06", "NFP"), ("2024-12-11", "CPI"),
    # 2025
    ("2025-01-10", "NFP"), ("2025-01-15", "CPI"), ("2025-02-07", "NFP"), ("2025-02-12", "CPI"),
    ("2025-03-07", "NFP"), ("2025-03-12", "CPI"), ("2025-04-04", "NFP"), ("2025-04-10", "CPI"),
    ("2025-05-02", "NFP"), ("2025-05-13", "CPI"), ("2025-06-06", "NFP"), ("2025-06-11", "CPI"),
    ("2025-07-03", "NFP"), ("2025-07-15", "CPI"), ("2025-08-01", "NFP"), ("2025-08-12", "CPI"),
    ("2025-09-05", "NFP"),
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
    y2 = fred_csv("DGS2", start="2021-06-01")
    y10 = fred_csv("DGS10", start="2021-06-01")
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
        # recent re-acceleration: last 12 releases vs the 12 before (captures the 2025-26 pickup
        # that the full-5y half-split masks, since 2022's rate-hike vol was far larger).
        if len(rows) >= 24:
            last12 = rows[-12:]
            prev12 = rows[-24:-12]
            summary["recent12_abs_2y"] = avg(last12, "abs2y")
            summary["prev12_abs_2y"] = avg(prev12, "abs2y")
            summary["reaccelerating_2y"] = summary["recent12_abs_2y"] > summary["prev12_abs_2y"]
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
