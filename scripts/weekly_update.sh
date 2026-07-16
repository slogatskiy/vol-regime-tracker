#!/usr/bin/env bash
# weekly_update.sh — refresh the tracker's data and push, so GitHub Pages redeploys.
# Run weekly by launchd on the Mac mini (see docs/deploy-macmini.md). Modeled on the
# vc-content-digest weekly job (dedicated service user + system LaunchDaemon).
#
# What actually changes each week: the LIVE public-API feeds — MOVE (Yahoo), CPI/NFP
# data-day vol (FRED), dealer balance (NY Fed). The report-based series (MKTX/TW/SIFMA/
# SEP) are rebuilt idempotently and only move when a new month/quarter has been ingested.
#
# Manual run:            bash scripts/weekly_update.sh
# Dry run (no push):     NO_PUSH=1 bash scripts/weekly_update.sh
set -uo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(pwd)"
STAMP="$(date +%F)"
echo "=== weekly update $STAMP  (repo: $REPO) ==="

# pick a Python: repo venv → uv → system python3
if [ -x ".venv/bin/python" ]; then PY=(.venv/bin/python)
elif command -v uv >/dev/null 2>&1; then PY=(uv run python)
else PY=(python3); fi
echo "python: ${PY[*]}"

run() {  # run a collector; never abort the whole job on one failure
  echo "--- $1"
  "${PY[@]}" "scripts/$1" || echo "WARN: scripts/$1 failed — continuing"
}

# live feeds (genuinely change week to week)
run fetch_move.py
run build_data_day_vol.py
run fetch_dealer_balance.py
# report-based series — idempotent rebuild; picks up any newly-ingested months / SIFMA xlsx
run ingest_mktx.py
run ingest_tradeweb.py
run ingest_market_share.py
run ingest_fed_path.py
run ingest_new_issue.py
run seed_illustrative.py
run analyze_fpm_signal.py

# commit & push only if the data actually changed
if [ -n "$(git status --porcelain docs/data)" ]; then
  git add -A
  git -c user.name="vol-regime bot" -c user.email="bot@vol-regime.local" \
      commit -q -m "data: weekly auto-update $STAMP"
  if [ "${NO_PUSH:-0}" = "1" ]; then
    echo "(NO_PUSH=1 — committed locally, not pushing)"
  else
    git push origin main && echo "pushed — Pages will redeploy."
  fi
else
  echo "no data changes this run."
fi
echo "=== done $STAMP ==="
