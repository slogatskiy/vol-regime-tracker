# Changelog

Named save points. Roll the whole repo back to any of these with `git checkout <tag>`.

## v0.7.0 — 2026-07-15 — FPM → results: earnings-miss signal (Georgy's ask)
New "FPM → results" widget answering: does the FPM decline signal an MKTX revenue miss?

- Mechanism: commissions ≈ FPM × volume (~87% of MKTX revenue); MKTX publishes volume+FPM
  ~5 weeks before earnings, so the FPM×volume proxy is a genuine leading indicator.
- Validation: 2026Q1 proxy +11.2% ≈ actual revenue +11.9%.
- Signal: 2026Q2 volume+FPM already public → proxy −6.2% YoY (flat volume, FPM −6.5%) →
  est. revenue ~$212M vs $220.4M Street consensus = ~−3.8% shortfall. With revenue already
  missed in Q3-25 and Q4-25, a revenue miss into the Aug-7 print is the base case (EPS may
  still squeak via cost/buybacks). New KPI tile + `analyze_fpm_signal.py` + section.
- Not investment advice; caveats (credit-only proxy, one quarter) noted on the widget.

## v0.6.0 — 2026-07-15 — per-widget explanations + 5-year chart spans
Georgy's two asks: a plain-English one-liner per widget, and 5-year coverage on the charts.

- **One-liner on every widget:** a `.oneliner` "In one line:" callout under each section header
  explaining what it shows in plain English.
- **5-year spans** where the data is clean at that horizon:
  - MOVE → 5y daily (Yahoo range=5y), captures the 2022 vol peak.
  - MKTX volume → 5y annual ADV ($10.4B '21 → $15.7B '25) + recent monthly YoY vs CAGR.
  - MKTX FPM → 5y annual ($181 '21 → $131 '26 YTD compression) + recent monthly.
  - Tradeweb vs MKTX → 5y annual revenue (TW +91% vs MKTX +21%; TW now 2.6× MKTX).
  - New issue → annual already spans 2015-2025; dealer already ~5y weekly.
  - Data-day vol → extended to a ~5y BLS release calendar (Jan-2022→). **This flipped the
    read honestly:** reactions peaked ~14bp in the 2022 hiking cycle and have COOLED to ~5bp,
    so the data-centric shift is a forward watch, not yet visible in magnitude. Manifest
    bottom-line and KPI updated to say so.
- **Deliberately NOT 5y:** market share stays an 18-month consistent series — MKTX changed its
  share basis (SD-PT split) in 2025, so a 5y line would mix methodologies (~21% old vs ~18% now)
  and overstate the decline; noted on the page. Fed path is a forward projection, not a history.
- New annual data added to ingest_mktx.py / ingest_tradeweb.py; data-day calendar extended.
  Render harness passes.

## v0.5.0 — 2026-07-13 — #8 new issue now real MONTHLY (SIFMA workbook)
Parsed SIFMA's official "US Corporate Bonds Statistics" Excel (Issuance tab, source Refinitiv)
into real monthly IG/HY gross issuance — the last coarser-than-asked series is now monthly.

- `ingest_new_issue.py` rewritten to parse the real workbook layout (annual / quarterly /
  monthly blocks under the IG/HY/Total header). 13 monthly points (Jun-2025…Jun-2026),
  9 quarterly, 11 annual (2015-2025).
- Section 04: monthly IG+HY stacked bars + annual IG bars. Real prints: Jan-2026 IG $231bn,
  Sep-2025 $211bn, Dec-2025 year-end lull $35bn; 2025 record IG year $1.73T.
- Source file lives in `data_raw/` (git-ignored); refresh by dropping the newest SIFMA xlsx
  and re-running. **Every one of the PM's 10 metrics is now real at the asked-for granularity.**

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
