# Roadmap

Goal: a shareable, versioned dashboard for the vol-regime / market-structure thesis,
moving each metric from **illustrative → sourced/live** while keeping the git history
as the audit trail.

## v0.1.0 — MVP skeleton (done)
- [x] Repo scaffold (BBW pattern): `docs/` site, `scripts/` collectors, snapshots, tags.
- [x] All 10 sections rendered on GitHub Pages with Chart.js.
- [x] **Live** feeds: MOVE (Yahoo), CPI/NFP data-day vol (FRED), dealer balance (NY Fed).
- [x] Illustrative-but-flagged seeds for the report-based metrics.
- [x] Live KPI strip computed from the data.

## v0.2 — ingest the market-structure data (MKTX vs TW core)
- [ ] **New issue (SIFMA):** parse monthly US corporate issuance tables → `new_issue.json`.
- [ ] **MKTX monthly volume:** ingest the monthly IR press releases → real ADV + YoY.
- [ ] **US high-grade share:** build TRACE-based estimate for MKTX & TW → `market_share.json`.
- [ ] **Tradeweb:** ingest TW monthly activity reports + quarterly revenue.
- [ ] **Variable FPM:** pull the FPM table from MKTX 10-Q/10-K each quarter.

## v0.3 — sharpen the rates side
- [ ] **Fed funds path:** derive implied path from CME FF futures settlements; overlay live SEP dots.
- [ ] **Dealer leverage:** add a leverage/utilization proxy alongside raw positions.
- [ ] **Data-day vol:** auto-pull the BLS release calendar instead of the hardcoded list;
      add an "vs typical day" baseline so acceleration is normalized.
- [ ] **MOVE:** add realized-vs-implied and a regime shading band.

## v0.4 — tracking & automation
- [ ] **FOMC task forces:** wire a light news check so status changes surface automatically.
- [ ] GitHub Actions cron: run the keyless collectors weekly and commit.
- [ ] Alerts: MOVE > 90 sustained, dealer capacity roll, share crossover MKTX↔TW.

## Open questions for the PM
- Preferred share definition for #7 (electronic-only vs all TRACE-eligible)?
- Which FPM cut matters most — reported blended, or segment-level (HG/HY/EM)?
- Do we want EM and munis in the MKTX volume view, or credit-only?

Not investment advice.
