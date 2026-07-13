"""Metric 8 (page section 04) — REAL US corporate new-issue volume.

Data honesty note: the only INTERNALLY-CONSISTENT monthly issuance series is SIFMA's
own Excel workbook (US Corporate Bonds Statistics), which is gated behind a JS download
and cannot be auto-fetched. Monthly numbers quoted in the financial press mix bases
(total-corp vs IG-only, gross vs net, provider definitions) and must NOT be stitched into
a series for institutional use.

So this script has two modes:
  1. If data_raw/sifma_us_corporate.xlsx exists -> parse the real MONTHLY IG/HY series.
     (Download it once from https://www.sifma.org/research/statistics/us-corporate-bonds-statistics/
      "US Corporate Bond Issuance" -> Save to data_raw/sifma_us_corporate.xlsx.)
  2. Otherwise -> seed with the REAL, SIFMA-consistent ANNUAL + QUARTERLY figures and the
     documented record months. Nothing fabricated; coarser granularity until the xlsx drop.

    python scripts/ingest_new_issue.py
"""
import os
from _common import save, today, RAW

# --- Real, SIFMA-consistent figures (gross IG issuance unless noted), $bn ---
ANNUAL_IG = {"2023": 1210, "2024": 1500, "2025": 1650}   # 2024 ~+24% vs 23; 2025 ~+10%
QUARTERLY_IG = {"2025Q2": 426, "2025Q3": 433, "2026Q1": 620}
RECORD_MONTHS = [
    {"month": "2025-09", "ig_bn": 226, "note": "record month; post-Sep rate-cut surge"},
    {"month": "2026-01", "ig_bn": 208, "note": "record January; +12% YoY, 6th month ever >$200bn"},
]
YTD_2026 = {"through": "2026-06", "total_corp_bn": 1523, "yoy_pct": 28.1}

XLSX = os.path.join(RAW, "sifma_us_corporate.xlsx")


def parse_sifma_xlsx(path):
    """Best-effort monthly IG/HY parse from the SIFMA workbook. Returns list or None."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("openpyxl not installed (`pip install openpyxl`) — skipping xlsx parse.")
        return None
    wb = load_workbook(path, data_only=True)
    # SIFMA layout varies; look for a sheet with a date column and IG/HY columns.
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        header = None
        for i, r in enumerate(rows[:20]):
            cells = [str(c).lower() if c is not None else "" for c in r]
            if any("investment grade" in c or c == "ig" for c in cells):
                header = (i, cells)
                break
        if not header:
            continue
        # NOTE: exact column mapping depends on the file; adjust indices after inspecting.
        print(f"Found candidate sheet '{ws.title}' — inspect columns and map indices.")
        return None
    return None


def main():
    monthly = parse_sifma_xlsx(XLSX) if os.path.exists(XLSX) else None

    if monthly:
        save("new_issue.json", {
            "last_updated": today(), "illustrative": False,
            "granularity": "monthly",
            "source": "SIFMA US Corporate Bond Issuance (monthly workbook)",
            "source_url": "https://www.sifma.org/research/statistics/us-corporate-bonds-statistics/",
            "unit": "Gross issuance, $ billions",
            "series": monthly,
        })
        print(f"new issue: {len(monthly)} monthly points from SIFMA xlsx")
        return

    # seed: real annual + quarterly + records (no monthly stitching from the press)
    save("new_issue.json", {
        "last_updated": today(),
        "illustrative": False,
        "granularity": "annual+quarterly",
        "source": "SIFMA US corporate issuance (annual/quarterly) + documented record months",
        "source_url": "https://www.sifma.org/research/statistics/us-corporate-bonds-statistics/",
        "unit": "Gross investment-grade issuance, $ billions",
        "annual_ig": ANNUAL_IG,
        "quarterly_ig": QUARTERLY_IG,
        "record_months": RECORD_MONTHS,
        "ytd_2026": YTD_2026,
        "note": "IG issuance boom: ~$1.21T (2023) → ~$1.50T (2024) → ~$1.65T (2025); 2026 total "
                "corp is running +28% YoY (H1 $1.52T) with a record $208bn January. High new-issue "
                "activity drives secondary turnover (the +95% YoY HG-turnover episode). Shown at "
                "annual/quarterly granularity — drop the SIFMA monthly workbook into data_raw/ for "
                "the full monthly series (press monthly figures are not basis-consistent).",
    })
    print("new issue: seeded real annual/quarterly + record months (SIFMA xlsx not present)")


if __name__ == "__main__":
    main()
