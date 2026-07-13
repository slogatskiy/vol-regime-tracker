# Changelog

Named save points. Roll the whole repo back to any of these with `git checkout <tag>`.

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
