"""FPM -> results signal: does MKTX's fee compression predict a revenue miss?

MarketAxess commission revenue (~87% of total revenue) is, mechanically,
    commissions ≈ Σ (variable FPM × volume) + fixed distribution fees.
So a credit-commission PROXY = credit_FPM × credit_ADV should track reported revenue.

The edge: MKTX publishes monthly VOLUME + FPM ~5 weeks before the earnings print, so the
proxy is a genuine leading indicator. We validate it on 2026Q1 (proxy tracked actual), then
read the ALREADY-KNOWN 2026Q2 volume/FPM to flag miss risk vs the Street's number.

    python scripts/analyze_fpm_signal.py
"""
from collections import defaultdict
from _common import save, today

# monthly credit ADV ($bn) and total-credit FPM ($/mm) — from MKTX volume releases
MKTX = {
    "2025-01": (14.473, 141), "2025-02": (15.493, 143), "2025-03": (17.800, 135),
    "2025-04": (18.360, 138), "2025-05": (16.348, 138), "2025-06": (15.660, 138),
    "2025-07": (14.342, 140), "2025-08": (13.086, 141), "2025-09": (16.157, 140),
    "2025-10": (15.999, 140), "2025-11": (16.808, 139), "2025-12": (13.546, 138),
    "2026-01": (18.593, 132), "2026-02": (17.261, 136), "2026-03": (19.900, 131),
    "2026-04": (15.887, 134), "2026-05": (16.997, 128), "2026-06": (17.670, 125),
}
# reported total revenue ($M) and YoY (%) — company results
REV = {
    "2025Q1": (208.58, -0.83), "2025Q2": (219.46, 11.03), "2025Q3": (208.82, 1.02),
    "2025Q4": (209.41, 3.46), "2026Q1": (233.38, 11.89),
}
# 2025 quarters that MISSED the revenue consensus (EPS was squeezed out on costs)
REV_MISSES = ["2025Q3", "2025Q4"]

# Q2-2026 Street consensus (Zacks) and the earnings date
CONSENSUS_Q2 = {"rev_mm": 220.43, "rev_yoy": 0.4, "eps": 1.90, "eps_yoy": -5.0,
                "report_date": "2026-08-07"}
COMMISSIONS_PCT = 87        # commissions as % of total revenue
CREDIT_VAR_SHARE = 0.70     # credit variable fees as ~share of total commissions


def q_of(m):
    y, mo = m.split("-")
    return f"{y}Q{(int(mo) - 1) // 3 + 1}"


def main():
    adv, fpm = defaultdict(list), defaultdict(list)
    for m, (a, f) in MKTX.items():
        adv[q_of(m)].append(a)
        fpm[q_of(m)].append(f)

    rows, proxy = [], {}
    for Q in sorted(adv):
        A = sum(adv[Q]) / len(adv[Q])
        F = sum(fpm[Q]) / len(fpm[Q])
        p = A * F
        proxy[Q] = p
        prev = f"{int(Q[:4]) - 1}Q{Q[-1]}"
        pyoy = round((p / proxy[prev] - 1) * 100, 1) if prev in proxy else None
        rev = REV.get(Q)
        rows.append({
            "q": Q, "credit_adv": round(A, 2), "credit_fpm": round(F, 1),
            "proxy_yoy": pyoy,
            "reported_rev_mm": rev[0] if rev else None,
            "rev_yoy": rev[1] if rev else None,
            "missed": Q in REV_MISSES,
        })

    # --- 2026Q2 prediction from the already-published volume/FPM ---
    q2 = next(r for r in rows if r["q"] == "2026Q2")
    proxy_yoy = q2["proxy_yoy"]                      # credit variable-fee proxy YoY
    # translate credit-variable YoY into TOTAL commission YoY, then total revenue
    comm_yoy = CREDIT_VAR_SHARE * (proxy_yoy / 100)  # other 30% (fixed distr., rates, info) ~ flat
    base_rev = REV["2025Q2"][0]
    base_comm = base_rev * COMMISSIONS_PCT / 100
    base_other = base_rev - base_comm
    est_comm = base_comm * (1 + comm_yoy)
    est_other = base_other * 1.03                    # non-commission segments ~+3%
    est_rev = est_comm + est_other
    miss_pct = round((est_rev / CONSENSUS_Q2["rev_mm"] - 1) * 100, 1)

    prediction = {
        "q": "2026Q2",
        "proxy_yoy": proxy_yoy,
        "est_rev_mm": round(est_rev, 1),
        "est_rev_low": round(est_rev * 0.985, 1),
        "est_rev_high": round(est_rev * 1.015, 1),
        "est_rev_yoy": round((est_rev / base_rev - 1) * 100, 1),
        "consensus_rev_mm": CONSENSUS_Q2["rev_mm"],
        "consensus_rev_yoy": CONSENSUS_Q2["rev_yoy"],
        "implied_vs_consensus_pct": miss_pct,
        "consensus_eps": CONSENSUS_Q2["eps"],
        "consensus_eps_yoy": CONSENSUS_Q2["eps_yoy"],
        "report_date": CONSENSUS_Q2["report_date"],
        "call": "revenue miss risk" if miss_pct < -1 else "in-line",
    }

    # validation: how well the proxy tracked the last reported quarter
    v = next(r for r in rows if r["q"] == "2026Q1")
    validation = {"q": "2026Q1", "proxy_yoy": v["proxy_yoy"], "actual_rev_yoy": v["rev_yoy"]}

    save("mktx_earnings_signal.json", {
        "last_updated": today(),
        "illustrative": False,
        "source": "MKTX monthly volume/FPM releases + reported results + Zacks consensus",
        "source_url": "https://investor.marketaxess.com/",
        "commissions_pct_of_rev": COMMISSIONS_PCT,
        "quarters": rows,
        "validation": validation,
        "prediction": prediction,
        "recent_revenue_misses": REV_MISSES,
        "note": (
            f"The credit-commission proxy (FPM×volume) tracked reported revenue in 2026Q1 "
            f"(proxy {validation['proxy_yoy']:+}% vs actual {validation['actual_rev_yoy']:+}%). "
            f"2026Q2 volume+FPM are already public: the proxy swung to {proxy_yoy:+}% YoY "
            f"(flat volume, FPM −6.5%). That maps to ~${prediction['est_rev_mm']:.0f}M revenue "
            f"({prediction['est_rev_yoy']:+}% YoY) vs the ${CONSENSUS_Q2['rev_mm']:.0f}M Street "
            f"number — a ~{abs(miss_pct):.0f}% shortfall. With revenue already missed in "
            f"{', '.join(REV_MISSES)}, a revenue miss (EPS possibly rescued by cost/buybacks) "
            f"is the base case into the Aug-7 print. NOT investment advice."
        ),
    })
    print(f"Q2-2026: proxy {proxy_yoy:+}% -> est rev ${est_rev:.0f}M vs cons ${CONSENSUS_Q2['rev_mm']:.0f}M "
          f"({miss_pct:+}% ) | validation Q1 proxy {v['proxy_yoy']:+}% vs actual {v['rev_yoy']:+}%")


if __name__ == "__main__":
    main()
