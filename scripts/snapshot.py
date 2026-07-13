"""Dated save points for the data. Drops a copy of every docs/data/*.json into
snapshots/<stamp>/ so specific results are easy to find, diff and restore.

    python scripts/snapshot.py "what changed"
"""
import os
import sys
import shutil
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "docs", "data")
SNAP = os.path.join(ROOT, "snapshots")


def main():
    note = sys.argv[1] if len(sys.argv) > 1 else ""
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest = os.path.join(SNAP, stamp)
    os.makedirs(dest, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(DATA)):
        if f.endswith(".json"):
            shutil.copy2(os.path.join(DATA, f), os.path.join(dest, f))
            n += 1
    readme = os.path.join(SNAP, "README.md")
    line = f"- `{stamp}/` — {n} files — {note}\n"
    header = "" if os.path.exists(readme) else "# Data snapshots\n\nDated copies of `docs/data/*.json` for browsing and rollback.\n\n"
    with open(readme, "a") as fh:
        if header:
            fh.write(header)
        fh.write(line)
    print(f"snapshot {stamp}: {n} files -> {dest}")


if __name__ == "__main__":
    main()
