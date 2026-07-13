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
- [x] **MKTX monthly volume:** ingested 18 months of IR releases → real ADV + YoY (`ingest_mktx.py`).
- [x] **Variable FPM:** real monthly total-credit FPM from the releases (Table 1D).
- [x] **Tradeweb:** real fully-electronic US credit ADV vs MKTX HG+HY (`ingest_tradeweb.py`).
- [ ] **New issue (SIFMA):** parse monthly US corporate issuance tables → `new_issue.json`
      (real anchor known: Jan-2026 IG $208.4bn, record, +12% YoY).
- [ ] **US high-grade share:** need a TRACE total-market denominator to turn MKTX/TW
      absolute ADV (already real) into share → `market_share.json`.
- [ ] **FPM segment split:** add HG/HY FPM from the 10-Q for a mix-shift decomposition.
- [ ] Backfill TW Feb-2026 US credit ADV (currently a gap) and extend both series back through 2024.

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
