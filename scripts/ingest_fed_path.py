"""Metric 10 (page section 09) — REAL fed funds path: market vs the dot plot.

Snapshot comparison, dated. Two real inputs:
  - FOMC dot-plot median from the June-2026 SEP (Summary of Economic Projections).
  - Market-implied path from fed funds futures (CME FedWatch / OIS), as of the as_of date.

The PM's point: divergence = markets pricing independently of Fed guidance. As of mid-2026
the divergence has FLIPPED hawkish — the market prices higher-for-longer than the dots,
especially in 2027 (futures hold near 4% while the dot median eases to 3.6%).

Update: re-read the latest SEP medians and the current FedWatch-implied levels, edit below.

    python scripts/ingest_fed_path.py
"""
from _common import save, today

AS_OF = "2026-07-13"
CURRENT_MIDPOINT = 3.625   # target range 3.50–3.75% after the June-2026 meeting

# horizon -> (dot_median, market_implied)  ; market None where futures don't extend
# Dot medians: June-2026 SEP (bin midpoints). Market: fed funds futures, as of AS_OF.
PATH = [
    ("Now",       3.625, 3.625),
    ("End-2026",  3.875, 3.95),   # market ~approaching 4% vs 3.875 dot median
    ("End-2027",  3.625, 3.90),   # futures near 4% through mid-2027; dots ease to 3.6%
    ("End-2028",  3.375, None),
    ("Long-run",  3.125, None),
]

SRC = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"


def main():
    series = []
    for horizon, dot, mkt in PATH:
        div = round((mkt - dot) * 100) if mkt is not None else None
        series.append({"horizon": horizon, "dot_median": dot,
                       "market_implied": mkt, "divergence_bps": div})
    divs = [r["divergence_bps"] for r in series if r["divergence_bps"] is not None]
    max_div = max(divs, key=abs) if divs else None
    save("fed_funds_path.json", {
        "last_updated": today(),
        "illustrative": False,
        "as_of": AS_OF,
        "source": "June-2026 FOMC SEP dot plot vs fed funds futures (CME FedWatch)",
        "source_url": SRC,
        "unit": "Implied fed funds rate, %",
        "current_midpoint": CURRENT_MIDPOINT,
        "max_divergence_bps": max_div,
        "note": f"As of {AS_OF}: the market prices HIGHER-for-longer than the dots — a hawkish "
                f"divergence up to ~{max_div}bp in 2027, where fed funds futures hold near 4% "
                f"while the SEP median eases to 3.6%. Markets are pricing independently of the "
                f"dots (the June SEP itself flipped hawkish, raising end-2026 to 3.875% from 3.4%). "
                f"Snapshot — re-run to refresh against the latest futures and SEP.",
        "series": series,
    })
    print(f"fed path: max divergence {max_div}bp (as of {AS_OF})")


if __name__ == "__main__":
    main()
