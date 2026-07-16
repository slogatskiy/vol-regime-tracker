# Weekly auto-update on the Mac mini (optional — Actions is the default)

> **The default weekly updater is GitHub Actions** (`.github/workflows/weekly-update.yml`) —
> it needs no machine, no sudo, no password. This Mac-mini setup is only an alternative for
> running the same job on a always-on Mac, and it requires admin (sudo) or Full-Disk-Access,
> which a locked-down headless mac may not grant you. Prefer Actions unless you specifically
> want it on the mini.

---


The dashboard is a static GitHub-Pages site fed by JSON in the repo. A weekly job on the
Mac mini re-pulls the live feeds, rebuilds every `docs/data/*.json`, and `git push`es — Pages
redeploys itself. We **reuse the existing `vcdigest` service user** (it already has SSH,
Tailscale and `uv`), so there's no new user to create — just clone, add push access, and
install one LaunchDaemon.

**What refreshes weekly:** the live public-API feeds — MOVE (Yahoo), CPI/NFP data-day vol
(FRED), primary-dealer balance (NY Fed). The report-based series (MKTX/TW volumes, FPM,
share, new issue, fed path, the FPM→earnings signal) are rebuilt idempotently and only move
when you ingest a new month/quarter by hand (they publish monthly).

---

## 1. Clone + deps (as `vcdigest`, over SSH — no sudo)

```bash
ssh vcdigest@konstantins-mac-mini
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/slogatskiy/vol-regime-tracker.git
cd vol-regime-tracker
mkdir -p logs                             # daemon StandardOut/ErrorPath
uv venv                                   # isolated ./.venv (separate from vc-digest)
uv pip install -r requirements.txt        # requests + openpyxl
.venv/bin/python -c "import requests, openpyxl; print('deps ok')"
```

## 2. Give `git push` non-interactive auth (deploy key) — the one thing to set up

```bash
# reuse the user's key if it exists, else make one:
[ -f ~/.ssh/id_ed25519.pub ] || ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```
Add that public key on GitHub → **repo `slogatskiy/vol-regime-tracker` → Settings → Deploy keys
→ Add deploy key → paste → tick "Allow write access"**. Then point the remote at SSH and test:
```bash
git remote set-url origin git@github.com:slogatskiy/vol-regime-tracker.git
ssh -T git@github.com        # expect the GitHub success banner
```
(A repo deploy key is scoped to just this repo and works no matter which GitHub account the
key belongs to — nothing to do with the vc-digest repo.)

## 3. Smoke-test the whole job

```bash
NO_PUSH=1 bash scripts/weekly_update.sh   # runs everything, commits locally, does NOT push
bash scripts/weekly_update.sh             # real run: refresh + commit + push
curl -s https://slogatskiy.github.io/vol-regime-tracker/data/move.json | tail -c 120  # a minute later
```

## 4. Install the LaunchDaemon (one sudo step; you have owner rights)

```bash
sudo cp /Users/vcdigest/projects/vol-regime-tracker/scripts/com.volregime.weekly.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.volregime.weekly.plist
sudo chmod 644        /Library/LaunchDaemons/com.volregime.weekly.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.volregime.weekly.plist
sudo launchctl kickstart -k system/com.volregime.weekly   # run once to verify
```
Runs **Monday 08:00** local (an hour before the vc-digest job, no clash).

---

## Operate

- **Logs:** `~/projects/vol-regime-tracker/logs/weekly.out.log` / `weekly.err.log`.
- **Run now:** `sudo launchctl kickstart -k system/com.volregime.weekly`
- **Monthly hand-refresh** (report data): add the new month to `ingest_mktx.py` /
  `ingest_market_share.py` / `ingest_tradeweb.py` from the MKTX/TW releases and drop the latest
  SIFMA workbook into `data_raw/sifma_us_corporate.xlsx`; the next weekly run picks it up (or run
  `bash scripts/weekly_update.sh` right away).
- **Change the time:** edit `StartCalendarInterval` in the plist, re-copy, re-`bootstrap`.
- **Stop it:** `sudo launchctl bootout system /Library/LaunchDaemons/com.volregime.weekly.plist`

Not investment advice.
