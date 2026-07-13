# Changelog

Named save points. Roll the whole repo back to any of these with `git checkout <tag>`.

## v0.2.0 — 2026-07-13 — real MKTX/Tradeweb data
Replaced the three market-structure metrics with **real, sourced data** transcribed
from the companies' monthly reports (ingest scripts included, so updates = add a month).

- **MKTX monthly volume (#2) → real:** 18 months (Jan-2025…Jun-2026) of total-credit ADV
  + US high-grade + high-yield, with YoY. 2026 YoY averages ~9.2% vs the 9.8% CAGR.
- **Variable FPM (#3) → real:** monthly total-credit FPM, $141 (Jan-25) → $125 (Jun-26)
  — clear compression on protocol mix shift.
- **Tradeweb vs MKTX (#7) → real:** like-for-like US credit e-trading ADV (MKTX HG+HY vs
  TW fully-electronic US credit). TW out-grew MKTX by ~14pp on average across 2026.
- KPI strip reworked to five all-real tiles; manifest bottom-line updated with the numbers.
- Still illustrative (flagged): market share (#4), new issue (#8), fed funds path (#10) —
  need TRACE / SIFMA / CME sources, tracked in ROADMAP.
- New scripts: `ingest_mktx.py`, `ingest_tradeweb.py`.

## v0.1.0 — 2026-07-13 — MVP skeleton
First working dashboard covering all 10 tracked metrics on the BBW project pattern
(static `docs/` site + Chart.js + Python collectors + JSON-in-git + snapshots/tags).

- **Live** (public APIs, refresh on collector run):
  - MOVE index vs 90/100 thresholds (Yahoo `^MOVE`).
  - CPI & payroll data-day Treasury vol, 3-day 2y/10y window (FRED DGS2/DGS10).
  - Primary-dealer net UST positions + maturity breakdown (NY Fed PD API).
- **Illustrative** (seeded, flagged amber, to be ingested): new issue (SIFMA),
  MKTX monthly volume, variable FPM, US high-grade share vs TW, Tradeweb growth,
  fed funds path vs dots.
- **Qualitative tracker:** FOMC framework / communications / balance-sheet task forces.
- Live KPI strip computed from the data; nav, methodology, data-honesty note.
