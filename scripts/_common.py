"""Shared helpers for the data collectors.

All collectors read/write JSON under docs/data/ so the dashboard (a static site on
GitHub Pages) can render with no backend. Every refresh is therefore a git commit.
"""
import json
import os
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "docs", "data")
RAW = os.path.join(ROOT, "data_raw")

UA = "Mozilla/5.0 (widget-pr data collector; contact: research)"


def today():
    return dt.date.today().isoformat()


def load(name):
    with open(os.path.join(DATA, name), "r") as f:
        return json.load(f)


def save(name, obj):
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"wrote {path}")


def get(url, params=None, timeout=25):
    import requests
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=timeout)
    r.raise_for_status()
    return r


def fred_csv(series_id, start="2015-01-01"):
    """Keyless daily series download from FRED (no API key required)."""
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
    txt = get(url, {"id": series_id, "cosd": start}).text
    out = []
    for line in txt.strip().splitlines()[1:]:
        d, v = line.split(",")
        if v in ("", "."):
            continue
        out.append((d, float(v)))
    return out
