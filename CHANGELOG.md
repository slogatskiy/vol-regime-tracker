# Changelog

Named save points. Roll the whole repo back to any of these with `git checkout <tag>`.

## v0.4.0 — 2026-07-13 — closed every gap vs the PM's brief
Filled the remaining pieces where the build was thinner than the PM's exact wording.

- **#7 Tradeweb — revenue added:** real quarterly total revenue, TW vs MKTX, 9 quarters
  (Q1-24…Q1-26). TW is ~2.6× MKTX ($618M vs $233M) and growing 13-27% vs MKTX 0-12%.
  The section now covers BOTH volume and revenue, as asked.
- **#4 Market share — now multi-year:** extended MKTX estimated US HG/HY share to a full
  18 months (Jan-2025…Jun-2026), showing the ~19.7% → 16.7% slide and recovery. Documented
  that Tradeweb discloses ADV, not a comparable %-of-TRACE share, so the TW head-to-head is
  the ADV/revenue comparison (no fabricated TW share line).
- **#9 Dealer — leverage/utilization added:** dealer net USTs as % of total public debt
  (FRBNY ÷ FRED GFDEBTN). Currently 1.10% vs 0.82% two years ago — dealers absorbing more.
- **#10 Fed path — incremental divergence tracked:** added the end-2026 dot-plot migration
  across SEPs (3.4% → 3.875% hawkish jump) and a dated market-vs-dots divergence log that
  appends on each run.
- Node render harness added to CI-style checks; passes on all real data.

## v0.3.0 — 2026-07-13 — no illustrative left; all metrics real
Converted the last three placeholder metrics to real, sourced data. **Nothing on the page
is fabricated anymore.**

- **US high-grade share (#7) → real:** MKTX estimated US HG/HY TRACE share, monthly
  Jul-2025…Jun-2026 (Table 1B) + FY24 19.0% / FY25 18.4% anchors. Shows the early-2026
  dip (16.7% Feb trough) on the new-issue surge, then recovery — the PM's watch-item.
- **Fed funds path (#9) → real:** June-2026 SEP dot medians vs fed funds futures (as of
  2026-07-13). Divergence flipped hawkish: market prices ~+27bp above the dots in 2027.
- **New issue (#4) → real:** SIFMA-consistent annual IG ($1.21T→$1.50T→$1.65T, 2023-25) +
  quarterly + record months. Monthly left to a SIFMA-xlsx ingest by design — press monthly
  numbers mix bases and aren't safe to stitch.
- New scripts: `ingest_market_share.py`, `ingest_fed_path.py`, `ingest_new_issue.py`
  (with an optional SIFMA `.xlsx` monthly parser). `seed_illustrative.py` now only emits the
  qualitative FOMC tracker. Render + Node runtime check pass on all real data.

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
