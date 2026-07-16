# Weekly auto-update on the Mac mini

The dashboard is a static site on GitHub Pages fed by JSON in the repo. To keep it fresh
we run one weekly job on the Mac mini that re-pulls the live feeds, rebuilds every
`docs/data/*.json`, and `git push`es — Pages then redeploys itself. Same convention as the
`vc-content-digest` weekly job: a dedicated **standard** user + a system **LaunchDaemon**.

**What refreshes weekly:** the live public-API feeds — MOVE (Yahoo), CPI/NFP data-day vol
(FRED), primary-dealer balance (NY Fed). The report-based series (MKTX/TW volumes, FPM,
share, new issue, fed path, the FPM→earnings signal) are rebuilt idempotently and only move
when you ingest a new month/quarter (they publish monthly, so a weekly cron just keeps the
market-data widgets current and re-commits any manual data edits).

Roles: **owner steps** need `sudo`; **dev steps** run as the service user over SSH. You have
owner-level access, so you can do both.

---

## Inventory (Konstantin's mini)

- Standard service users per project (`ccinspector`, `biai`, `bitrix`, `vcdigest`, …); admin
  is `konstantin` + root. → add `volregime` as another standard user.
- Scheduler: system LaunchDaemons in `/Library/LaunchDaemons/`, reverse-DNS names.
- Runtime: `uv` is global (`/opt/homebrew/bin/uv`); `git` is `/usr/bin/git`. Nothing per-user needed.
- SSH: key-only, access limited to group `com.apple.access_ssh` — a new user must be added to it.
- Time: local **Europe/Podgorica** (matters for the LaunchDaemon schedule).
- Access: Tailscale, host `konstantins-mac-mini`.

---

## A. Owner steps (sudo)

### A1. Create the standard service user
```bash
sudo sysadminctl -addUser volregime -fullName "Vol-Regime Service" -password -
# interactive password; NO -admin = standard user, like bitrix/vcdigest
```

### A2. Allow SSH for the user (required)
```bash
sudo dseditgroup -o edit -a volregime -t user com.apple.access_ssh
dseditgroup -o checkmember -m volregime com.apple.access_ssh   # expect "yes"
```

### A3. Install your SSH public key (so you can log in as the user)
```bash
sudo -u volregime mkdir -p /Users/volregime/.ssh
sudo -u volregime tee /Users/volregime/.ssh/authorized_keys <<'KEY'
<your id_ed25519.pub>
KEY
sudo chmod 700 /Users/volregime/.ssh && sudo chmod 600 /Users/volregime/.ssh/authorized_keys
sudo chown -R volregime:staff /Users/volregime/.ssh
```

### A5. Install the LaunchDaemon (after B is done and smoke-tested)
```bash
sudo cp /Users/volregime/projects/vol-regime-tracker/scripts/com.volregime.weekly.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.volregime.weekly.plist
sudo chmod 644        /Library/LaunchDaemons/com.volregime.weekly.plist
sudo launchctl bootstrap system /Library/LaunchDaemons/com.volregime.weekly.plist
sudo launchctl kickstart -k system/com.volregime.weekly   # run once to verify
```

---

## B. Dev steps (as `volregime`, over SSH)

### B1. Clone into the standard path
```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/slogatskiy/vol-regime-tracker.git
cd vol-regime-tracker
mkdir -p logs            # for the daemon's StandardOut/ErrorPath
```

### B2. Install deps (requests + openpyxl)
```bash
uv venv                                  # creates ./.venv
uv pip install -r requirements.txt       # requests, openpyxl
.venv/bin/python -c "import requests, openpyxl; print('deps ok')"
```
(The runner auto-detects `.venv/bin/python`, else `uv run python`, else `python3`.)

### B3. Give `git push` non-interactive auth  ← the one thing this project needs
The job pushes to GitHub, so the service user needs write auth. Pick one:

**Deploy key (recommended — repo-scoped, revocable):**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""     # as volregime
cat ~/.ssh/id_ed25519.pub
# → GitHub → repo Settings → Deploy keys → Add → paste → tick "Allow write access"
git remote set-url origin git@github.com:slogatskiy/vol-regime-tracker.git
ssh -T git@github.com                                  # expect the success banner
```
**or a fine-grained PAT** (Contents: read/write on this repo) via the macOS keychain helper:
```bash
git config --global credential.helper osxkeychain
git push        # prompts once for username + PAT-as-password; cached thereafter
```

### B4. Smoke-test the whole job WITHOUT pushing, then for real
```bash
NO_PUSH=1 bash scripts/weekly_update.sh    # runs everything, commits locally, no push
bash scripts/weekly_update.sh              # real run: refresh + commit + push
# confirm Pages updated a minute later:
curl -s https://slogatskiy.github.io/vol-regime-tracker/data/move.json | tail -c 120
```

---

## Operate

- **Logs:** `~/projects/vol-regime-tracker/logs/weekly.out.log` and `weekly.err.log`.
- **Run now:** `sudo launchctl kickstart -k system/com.volregime.weekly`
- **Change the time:** edit `StartCalendarInterval` in the plist, re-copy, re-`bootstrap`.
- **Refresh report-based data (monthly, by hand):** add the new month to `ingest_mktx.py` /
  `ingest_market_share.py` / `ingest_tradeweb.py` from the MKTX/TW releases, drop the latest
  SIFMA workbook into `data_raw/sifma_us_corporate.xlsx`, then the next weekly run picks it up
  (or run `bash scripts/weekly_update.sh` immediately).
- **Stop it:** `sudo launchctl bootout system /Library/LaunchDaemons/com.volregime.weekly.plist`

Not investment advice.
