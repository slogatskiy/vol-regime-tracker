# Fixed-Income Vol-Regime & Market-Structure Tracker

A small GitHub-Pages dashboard for the desk's fixed-income thesis: the rates market
is shifting from an **FOMC-centric** to a **data-centric** volatility regime — and the
turnover benefit accrues to whoever wins market structure (**MarketAxess / MKTX** vs
**Tradeweb / TW**).

> **Thesis.** Higher, data-driven rates volatility raises trading turnover. This tracker
> monitors both halves of the trade: **(A) the vol regime** — MOVE, Treasury reactions to
> CPI/payrolls, primary-dealer capacity, and the Fed's own communication/balance-sheet
> reviews; and **(B) who captures it** — MKTX vs TW volumes, variable fees per million,
> US high-grade share, and new-issue-driven secondary activity.

**Live dashboard:** _enable GitHub Pages (Settings → Pages → Branch: `main`, folder `/docs`), then the URL appears here._

---

## The 10 tracked metrics

| # | Section | Data | Status |
|---|---------|------|--------|
| 1 | **MOVE Index** — watch 90 / 100 | Yahoo `^MOVE` | 🟢 live |
| 2 | **CPI & Payroll day vol** — 2y/10y 3-day window | FRED DGS2/DGS10 | 🟢 live |
| 3 | **Dealer balance sheet** — net UST positions | NY Fed Primary Dealer API | 🟢 live |
| 4 | **New-issue volume** — IG/HY monthly | SIFMA | 🟡 illustrative |
| 5 | **MKTX monthly volume** — ADV vs 9.8% CAGR | MKTX IR releases | 🟢 real |
| 6 | **Variable FPM** — fee compression | MKTX IR (Table 1D) | 🟢 real |
| 7 | **US high-grade share** — MKTX vs TW | TRACE estimates | 🟡 illustrative |
| 8 | **Tradeweb vs MKTX** — US credit e-trading | TW & MKTX IR | 🟢 real |
| 9 | **Fed funds path vs dots** — divergence | FF futures / CME | 🟡 illustrative |
| 10 | **FOMC task forces** — framework/comms/balance-sheet | Fed press | 🟢 tracked (qualitative) |

🟢 **live** = fetched from a free public API on every collector run.
🟡 **illustrative** = seeded, clearly flagged amber on the page, and overwritten when the
sourced report is ingested. Nothing illustrative is presented as a measured value.

## How it's built

```
docs/                 # the static site (GitHub Pages serves this folder)
  index.html          # 10 sections + masthead
  app.js              # renders KPIs + Chart.js charts from data/*.json
  styles.css
  data/               # the data the page reads (versioned in git)
    manifest.json
    move.json data_day_vol.json dealer_balance.json      # live
    new_issue.json mktx_volume.json mktx_fpm.json         # illustrative
    market_share.json tradeweb.json fed_funds_path.json   # illustrative
    fomc_taskforce.json                                   # qualitative
scripts/              # data collectors — you run these to refresh data/
  fetch_move.py             # MOVE (Yahoo ^MOVE)
  build_data_day_vol.py     # CPI/NFP Treasury reactions (FRED)
  fetch_dealer_balance.py   # dealer net UST positions (NY Fed)
  seed_illustrative.py      # seeds the illustrative files (edit / replace)
  snapshot.py               # dated data save points
  _common.py
data_raw/             # (git-ignored) drop sourced CSVs here
snapshots/            # dated copies of docs/data for browsing & rollback
```

Data lives as JSON **inside the repo**, so every refresh is a git commit — the history is
in the git log, and the dashboard is re-runnable and diffable over time.

## Refresh the data

```bash
pip install -r requirements.txt

python scripts/fetch_move.py            # MOVE (no keys)
python scripts/build_data_day_vol.py    # data-day Treasury vol (no keys)
python scripts/fetch_dealer_balance.py  # dealer balance sheet (no keys)
python scripts/ingest_mktx.py           # MKTX monthly volume + FPM (real; add new months)
python scripts/ingest_tradeweb.py       # MKTX vs TW US credit e-trading (real)
python scripts/seed_illustrative.py     # remaining illustrative files (#4, #8, #10)

git add docs/data && git commit -m "data: refresh signals" && git push
```

Preview locally: `python -m http.server 8000 --directory docs` → http://localhost:8000

## Saving & rollback

**Git tags** mark milestones (see `CHANGELOG.md`):

```bash
git tag                 # list save points (v0.1.0, …)
git checkout v0.1.0     # inspect that version
git checkout main       # back to latest
```

**Data snapshots** (browsable files) — before/after any data change:

```bash
python scripts/snapshot.py "what changed"
```

Drops a dated copy of every `docs/data/*.json` into `snapshots/<stamp>/`.

## Roadmap

See `ROADMAP.md`. Next up: replace the illustrative series with sourced ingests
(SIFMA new issue, MKTX/TW IR volumes & fees, TRACE share, FF-futures path).

Internal research. Not investment advice.
