/* Fixed-Income Vol-Regime & Market-Structure Tracker.
   Loads data/*.json and renders the dashboard with Chart.js. All data is static
   JSON, so the page runs on GitHub Pages with no backend. */

const C = {
  accent: "#4f8cff", amber: "#f5a623", good: "#38c793", bad: "#ff6b6b",
  grid: "rgba(255,255,255,.05)", text: "#9aa6cc", muted: "#66719c",
};
const $ = (id) => document.getElementById(id);
const fmt = (n) => Number(n).toLocaleString("en-US");
const MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const monthLbl = (d) => { if (!d) return ""; const [y, m] = d.split("-"); return `${MON[+m]} '${y.slice(2)}`; };
const sign = (n) => (n > 0 ? "+" : "") + n;

async function loadJSON(p) {
  const r = await fetch(p, { cache: "no-store" });
  if (!r.ok) throw new Error(`${p}: ${r.status}`);
  return r.json();
}

function base(extra = {}) {
  return {
    responsive: true, maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { labels: { color: C.text, usePointStyle: true, boxWidth: 8, font: { size: 12 } } },
      tooltip: { backgroundColor: "#0a0d18", borderColor: "#232e52", borderWidth: 1,
        titleColor: "#eef1fa", bodyColor: "#cfd6f0", padding: 10 },
    },
    scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 10, font: { size: 11 } } },
      y: { grid: { color: C.grid }, ticks: { color: C.text, font: { size: 11 } } },
    },
    ...extra,
  };
}
const axT = (text) => ({ display: true, text, color: C.muted, font: { size: 11, weight: "500" } });
function thresholdLine(y, color, label) {
  return {
    label, data: null, borderColor: color, borderWidth: 1.5, borderDash: [6, 5],
    pointRadius: 0, fill: false, _yval: y,
  };
}

/* ---------- KPI strip (computed live from the data) ---------- */
function kpiCard(label, value, sub, chip) {
  const chipHtml = chip ? `<span class="chip ${chip.cls || ""}">${chip.t}</span>` : "";
  return `<div class="kpi"><div class="k-label">${label}</div>
    <div class="k-value">${value} ${chipHtml}</div><div class="k-sub">${sub}</div></div>`;
}

/* ---------- 01 MOVE ---------- */
function renderMove(d) {
  const labels = d.series.map(p => p.date);
  const vals = d.series.map(p => p.value);
  new Chart($("moveChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "MOVE", data: vals, borderColor: C.accent, backgroundColor: "rgba(79,140,255,.10)",
        borderWidth: 2, pointRadius: 0, fill: true, tension: .15 },
      { label: "Watch (90)", data: labels.map(() => d.thresholds.watch), borderColor: C.amber,
        borderWidth: 1.3, borderDash: [6, 5], pointRadius: 0, fill: false },
      { label: "Regime (100)", data: labels.map(() => d.thresholds.regime), borderColor: C.bad,
        borderWidth: 1.3, borderDash: [6, 5], pointRadius: 0, fill: false },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 8 } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("MOVE index level") } } }),
  });
  const above = d.current >= d.thresholds.regime ? "above the 100 regime line" :
    d.current >= d.thresholds.watch ? "above the 90 watch line" : "below the 90 watch line";
  $("move-note").textContent =
    `Current ${d.current}, ${above}. 90-day average ${d.avg_90d}; ${d.days_above_watch_90d} of the last 90 sessions closed above 90.`;
  $("move-readout").innerHTML =
    `<div class="r"><div class="rl">Current</div><div class="rv">${d.current}</div><div class="rs">${above}</div></div>
     <div class="r"><div class="rl">90-day avg</div><div class="rv">${d.avg_90d}</div><div class="rs">trailing quarter</div></div>
     <div class="r"><div class="rl">52w range</div><div class="rv">${d.week52_low}–${d.week52_high}</div><div class="rs">low–high</div></div>
     <div class="r"><div class="rl">Days &gt;90</div><div class="rv">${d.days_above_watch_90d}</div><div class="rs">of last 90</div></div>`;
  return d;
}

/* ---------- 02 Data-day vol ---------- */
function renderDataDay(d) {
  const rows = d.rows;
  const labels = rows.map(r => `${r.kind} ${r.date.slice(5)}`);
  new Chart($("dataDayChart"), {
    type: "bar",
    data: { labels, datasets: [
      { label: "|Δ2y|", data: rows.map(r => r.abs2y), backgroundColor: C.accent },
      { label: "|Δ10y|", data: rows.map(r => r.abs10y), backgroundColor: C.amber },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 12 } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("|move| over 3-day window (bps)"), beginAtZero: true } } }),
  });
  const s = d.summary || {};
  const peak = rows.reduce((a, r) => r.abs2y > a.abs2y ? r : a, rows[0]);
  $("dataday-note").textContent =
    `Reactions peaked ~${peak.abs2y}bp around ${peak.date.slice(0, 7)} (the 2022 hiking cycle) and have since cooled to ` +
    `~${s.recent12_abs_2y ?? s.avg_abs_2y_recent}bp (last 12 prints) — so the data-centric shift is a forward watch, ` +
    `not yet visible in raw reaction size. 5y avg |Δ2y| ${s.avg_abs_2y_recent} (recent half) vs ${s.avg_abs_2y_early} (2022-23).`;
  const tb = $("dataday-table").querySelector("tbody");
  tb.innerHTML = rows.slice(-15).reverse().map(r => {
    const c2 = r.d2y_window_bps >= 0 ? "pos" : "neg";
    const c10 = r.d10y_window_bps >= 0 ? "pos" : "neg";
    return `<tr><td>${r.date}</td><td><span class="kind-tag kind-${r.kind}">${r.kind}</span></td>
      <td class="${c2}">${sign(r.d2y_window_bps)}</td><td class="${c10}">${sign(r.d10y_window_bps)}</td></tr>`;
  }).join("");
  return d;
}

/* ---------- 03 Dealer balance sheet ---------- */
function renderDealer(d) {
  const bn = v => Math.round(v / 1000);
  const labels = d.series.map(p => p.date);
  new Chart($("dealerChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "Net UST position ($bn)", data: d.series.map(p => bn(p.value)),
        borderColor: C.good, backgroundColor: "rgba(56,199,147,.10)", borderWidth: 2, pointRadius: 0, fill: true, tension: .12 },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 8 } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("$ billions, net long−short") } } }),
  });
  new Chart($("dealerBucketChart"), {
    type: "bar",
    data: { labels: d.breakdown_latest.map(b => b.bucket), datasets: [
      { label: "Net position ($bn)", data: d.breakdown_latest.map(b => bn(b.value)),
        backgroundColor: d.breakdown_latest.map(b => b.value >= 0 ? C.accent : C.bad) },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("$ billions") } } }),
  });
  $("dealer-note").textContent =
    `Net $${bn(d.current)}bn as of ${d.current_date}, ${d.yoy_change >= 0 ? "up" : "down"} $${Math.abs(bn(d.yoy_change))}bn YoY. ` +
    `Rising inventory can reflect either willing intermediation or forced warehousing into heavy supply — read alongside issuance.`;

  // leverage / capacity utilization
  const u = d.utilization;
  if (u && u.series) {
    new Chart($("dealerUtilChart"), {
      type: "line",
      data: { labels: u.series.map(p => p.date), datasets: [
        { label: "Dealer USTs ÷ public debt (%)", data: u.series.map(p => p.pct), borderColor: C.amber,
          backgroundColor: "rgba(245,166,35,.10)", borderWidth: 2, pointRadius: 0, fill: true, tension: .12 },
      ]},
      options: base({ plugins: { legend: { display: false } }, scales: {
        x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 8 } },
        y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("% of total public debt") } } }),
    });
    const dir = u.current_pct >= u.two_year_ago_pct ? "up from" : "down from";
    $("dealer-util-note").textContent =
      `Dealers hold ${u.current_pct}% of total public debt, ${dir} ${u.two_year_ago_pct}% two years ago.`;
    $("dealer-util-readout").innerHTML =
      `<div class="r"><div class="rl">Utilization</div><div class="rv">${u.current_pct}%</div><div class="rs">USTs ÷ public debt</div></div>
       <div class="r"><div class="rl">2y ago</div><div class="rv">${u.two_year_ago_pct}%</div><div class="rs">${dir.split(" ")[0]}</div></div>`;
  }
  return d;
}

/* ---------- 04 New issue (real monthly + annual, SIFMA) ---------- */
function renderNewIssue(d) {
  // monthly IG + HY (stacked)
  const m = d.monthly || [];
  new Chart($("newIssueChart"), {
    type: "bar",
    data: { labels: m.map(p => monthLbl(p.month)), datasets: [
      { label: "IG", data: m.map(p => p.ig_bn), backgroundColor: C.accent },
      { label: "HY", data: m.map(p => p.hy_bn), backgroundColor: C.amber },
    ]},
    options: base({ scales: {
      x: { stacked: true, grid: { color: C.grid }, ticks: { color: C.text } },
      y: { stacked: true, grid: { color: C.grid }, ticks: { color: C.text }, title: axT("$ bn / month"), beginAtZero: true } } }),
  });
  // annual IG issuance (last ~10 years)
  const a = (d.annual || []).filter(r => +r.year >= 2016);
  new Chart($("newIssueYoyChart"), {
    type: "bar",
    data: { labels: a.map(r => r.year), datasets: [
      { label: "IG gross ($bn)", data: a.map(r => r.ig_bn), backgroundColor: C.accent },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("annual IG issuance, $bn"), beginAtZero: true } } }),
  });
  const peak = m.reduce((x, p) => p.ig_bn > x.ig_bn ? p : x, m[0]);
  const trough = m.reduce((x, p) => p.ig_bn < x.ig_bn ? p : x, m[0]);
  const a25 = (d.annual || []).find(r => r.year === "2025");
  $("newissue-note").innerHTML =
    `Real SIFMA monthly gross issuance. IG peaked at $${peak.ig_bn}bn (${monthLbl(peak.month)}) ` +
    `and troughed at $${trough.ig_bn}bn (${monthLbl(trough.month)}, year-end lull). ` +
    (a25 ? `2025 was a record year at $${a25.ig_bn}bn IG. ` : "") +
    `High new-issue activity drives the secondary-turnover surge.`;
  return d;
}

/* ---------- 05 MKTX volume ---------- */
function renderMktxVolume(d) {
  // 5-year annual ADV bars
  const ann = d.annual_adv || [];
  new Chart($("mktxAdvChart"), {
    type: "bar",
    data: { labels: ann.map(a => a.year + (a.partial ? " YTD" : "")), datasets: [
      { label: "Total credit ADV ($bn)", data: ann.map(a => a.adv_bn),
        backgroundColor: ann.map(a => a.partial ? "rgba(79,140,255,.45)" : C.accent) },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("annual ADV, $ bn/day"), beginAtZero: true } } }),
  });
  const yoy = d.series.filter(p => p.yoy_pct != null);
  new Chart($("mktxYoyChart"), {
    type: "line",
    data: { labels: yoy.map(p => monthLbl(p.month)), datasets: [
      { label: "ADV YoY %", data: yoy.map(p => p.yoy_pct), borderColor: C.good,
        backgroundColor: "rgba(56,199,147,.10)", borderWidth: 2, pointRadius: 2, fill: true, tension: .15 },
      { label: `5y CAGR (${d.cagr_5y_pct}%)`, data: yoy.map(() => d.cagr_5y_pct), borderColor: C.amber,
        borderWidth: 1.5, borderDash: [6, 5], pointRadius: 0, fill: false },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 8 } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("YoY %") } } }),
  });
  const a0 = ann[0], aLast = ann.find(a => a.year === "2025") || ann[ann.length - 1];
  const grow = a0 ? Math.round((aLast.adv_bn / a0.adv_bn - 1) * 100) : null;
  $("volume-note").textContent =
    `Annual ADV grew from $${a0.adv_bn}bn (${a0.year}) to $${aLast.adv_bn}bn (${aLast.year})` +
    (grow != null ? `, +${grow}% over the span` : "") +
    `; 2026 YTD ~$${(ann.find(a => a.partial) || aLast).adv_bn}bn. Bull signal is YoY sustained above the ${d.cagr_5y_pct}% CAGR line (right).`;
  return d;
}

/* ---------- 06 FPM ---------- */
function renderFpm(d) {
  // 5-year annual FPM
  const ann = d.annual_fpm || [];
  if (ann.length) {
    new Chart($("fpmAnnualChart"), {
      type: "line",
      data: { labels: ann.map(a => a.year + (a.partial ? " YTD" : "")), datasets: [
        { label: "Total-credit FPM", data: ann.map(a => a.credit_fpm), borderColor: C.accent,
          backgroundColor: "rgba(79,140,255,.10)", borderWidth: 2, pointRadius: 4, fill: true, tension: .1 },
      ]},
      options: base({ plugins: { legend: { display: false } }, scales: {
        x: { grid: { color: C.grid }, ticks: { color: C.text } },
        y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("annual FPM, $/mm") } } }),
    });
    const f = ann[0], l = ann[ann.length - 1];
    $("fpm-annual-note").textContent =
      `Steady multi-year compression: $${f.credit_fpm} (${f.year}) → $${l.credit_fpm} (${l.year}${l.partial ? " YTD" : ""}), ` +
      `${Math.round((l.credit_fpm / f.credit_fpm - 1) * 100)}% — driven by protocol/product mix shift.`;
  }
  const labels = d.series.map(p => monthLbl(p.month));
  new Chart($("fpmChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "Total-credit FPM", data: d.series.map(p => p.credit_fpm), borderColor: C.accent,
        backgroundColor: "rgba(79,140,255,.10)", borderWidth: 2, pointRadius: 2, fill: true, tension: .15 },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 10 } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("$ per million traded") } } }),
  });
  const f = d.series[0], l = d.series[d.series.length - 1];
  const drop = Math.round((l.credit_fpm / f.credit_fpm - 1) * 100);
  $("fpm-note").textContent =
    `Total-credit FPM ${f.credit_fpm}→${l.credit_fpm} $/mm (${drop}% from ${monthLbl(f.month)} to ${monthLbl(l.month)}) — real compression on mix shift toward lower-fee protocols; total-rates FPM has risen over the same window.`;
  return d;
}

/* ---------- 06+ FPM -> results: earnings-miss signal ---------- */
function renderSignal(d) {
  const p = d.prediction, v = d.validation;
  // show recent quarters: reported revenue YoY (Q2 = estimate) + proxy YoY overlay
  const qs = ["2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2"];
  const byq = Object.fromEntries(d.quarters.map(r => [r.q, r]));
  const revBars = qs.map(q => q === "2026Q2" ? p.est_rev_yoy : (byq[q] ? byq[q].rev_yoy : null));
  const proxyLine = qs.map(q => byq[q] ? byq[q].proxy_yoy : null);
  new Chart($("signalChart"), {
    data: { labels: qs, datasets: [
      { type: "bar", label: "Reported revenue YoY", data: revBars,
        backgroundColor: qs.map(q => q === "2026Q2" ? "rgba(255,107,107,.55)" : C.accent),
        order: 2 },
      { type: "line", label: "Commission proxy YoY (FPM×vol)", data: proxyLine,
        borderColor: C.amber, borderWidth: 2, pointRadius: 4, spanGaps: true, order: 1 },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("YoY %") } } }),
  });
  $("signal-note").textContent =
    `Validation: ${v.q} proxy ${sign(v.proxy_yoy)}% ≈ actual revenue ${sign(v.actual_rev_yoy)}%. ` +
    `${p.q} bar is the estimate (revenue not yet reported).`;
  const missCls = p.implied_vs_consensus_pct < -1 ? "bad" : "good";
  $("signal-readout").innerHTML =
    `<div class="r"><div class="rl">Q2-26 proxy YoY</div><div class="rv down">${sign(p.proxy_yoy)}%</div><div class="rs">FPM×volume, already public</div></div>
     <div class="r"><div class="rl">Est. revenue</div><div class="rv">$${p.est_rev_mm}M</div><div class="rs">${sign(p.est_rev_yoy)}% YoY · $${p.est_rev_low}–${p.est_rev_high}M</div></div>
     <div class="r"><div class="rl">Consensus</div><div class="rv">$${p.consensus_rev_mm}M</div><div class="rs">${sign(p.consensus_rev_yoy)}% YoY · EPS $${p.consensus_eps}</div></div>
     <div class="r"><div class="rl">vs consensus</div><div class="rv ${p.implied_vs_consensus_pct < 0 ? 'down' : 'up'}">${sign(p.implied_vs_consensus_pct)}%</div><div class="rs">reports ${p.report_date}</div></div>`;
  $("signal-answer").innerHTML =
    `<b>Yes — it points to a revenue miss.</b> ${d.note}`;
  return d;
}

/* ---------- 07 Market share (real MKTX estimated share) ---------- */
function renderShare(d) {
  const labels = d.series.map(p => monthLbl(p.month));
  const fy25 = d.annual_hg["2025"];
  new Chart($("shareChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "US high-grade share", data: d.series.map(p => p.hg_share), borderColor: C.accent,
        backgroundColor: "rgba(79,140,255,.10)", borderWidth: 2, pointRadius: 3, fill: true, tension: .15 },
      { label: "US high-yield share", data: d.series.map(p => p.hy_share), borderColor: C.amber,
        borderWidth: 2, pointRadius: 2, fill: false, tension: .15 },
      { label: `FY2025 HG avg (${fy25}%)`, data: labels.map(() => fy25), borderColor: C.muted,
        borderWidth: 1.3, borderDash: [6, 5], pointRadius: 0, fill: false },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("MKTX estimated share of TRACE, %") } } }),
  });
  const l = d.series[d.series.length - 1];
  const trough = d.series.reduce((a, p) => p.hg_share < a.hg_share ? p : a, d.series[0]);
  $("share-note").textContent =
    `MKTX US high-grade share ${l.hg_share}% latest (FY24 ${d.annual_hg["2024"]}% → FY25 ${fy25}%). ` +
    `Dipped to a ${trough.hg_share}% trough in ${monthLbl(trough.month)} on the new-issue surge, now recovering. ` +
    `Shown as a consistent 18-month window on purpose: MKTX changed its share basis in 2025 (split out single-dealer portfolio trades), so a 5-year line would mix methodologies (~21% old-basis vs ~18% now) and overstate the decline.`;
  return d;
}

/* ---------- 08 Tradeweb vs MKTX (US credit e-trading) ---------- */
function renderTradeweb(d) {
  const labels = d.series.map(p => monthLbl(p.month));
  new Chart($("twRevChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "MKTX (HG+HY)", data: d.series.map(p => p.mktx_us_credit_bn), borderColor: C.accent,
        borderWidth: 2, pointRadius: 3, tension: .15, spanGaps: true },
      { label: "Tradeweb", data: d.series.map(p => p.tw_us_credit_bn), borderColor: C.amber,
        borderWidth: 2, pointRadius: 3, tension: .15, spanGaps: true },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("US credit ADV, $bn") } } }),
  });
  new Chart($("twVolChart"), {
    type: "bar",
    data: { labels, datasets: [
      { label: "MKTX YoY", data: d.series.map(p => p.mktx_yoy), backgroundColor: C.accent },
      { label: "Tradeweb YoY", data: d.series.map(p => p.tw_yoy), backgroundColor: C.amber },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("US credit ADV YoY %") } } }),
  });
  $("tradeweb-note").textContent =
    `Across 2026, Tradeweb's US credit e-trading has grown ~${d.avg_growth_gap_pp}pp/yr faster than MKTX ` +
    `and led US credit e-trading outright in June — the vol benefit is accruing disproportionately to the competitor. ` +
    `(MKTX = HG+HY ADV; TW = fully-electronic US credit ADV; Feb shown as a gap — not disclosed.)`;

  // 5-year annual revenue (TW vs MKTX)
  const arev = d.annual_revenue || [];
  new Chart($("revLevelChart"), {
    type: "bar",
    data: { labels: arev.map(r => r.year), datasets: [
      { label: "Tradeweb", data: arev.map(r => r.tw_rev_mm), backgroundColor: C.amber },
      { label: "MKTX", data: arev.map(r => r.mktx_rev_mm), backgroundColor: C.accent },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("annual revenue, $M"), beginAtZero: true } } }),
  });
  const rev = d.revenue || [];
  const ry = rev.filter(r => r.tw_rev_yoy != null);
  new Chart($("revYoyChart"), {
    type: "line",
    data: { labels: ry.map(r => r.q), datasets: [
      { label: "Tradeweb", data: ry.map(r => r.tw_rev_yoy), borderColor: C.amber, borderWidth: 2, pointRadius: 3, tension: .15 },
      { label: "MKTX", data: ry.map(r => r.mktx_rev_yoy), borderColor: C.accent, borderWidth: 2, pointRadius: 3, tension: .15 },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("revenue YoY %") } } }),
  });
  const g = d.rev_5y_growth || {};
  const r0 = arev[0], r1 = arev[arev.length - 1];
  $("revenue-note").textContent =
    `Over 5 years TW revenue grew +${g.tw_pct}% ($${(r0.tw_rev_mm/1000).toFixed(2)}B→$${(r1.tw_rev_mm/1000).toFixed(2)}B) vs MKTX +${g.mktx_pct}% ($${r0.mktx_rev_mm.toFixed(0)}M→$${r1.mktx_rev_mm.toFixed(0)}M) — TW is now ~${d.rev_ratio_latest}× MKTX. The gap keeps widening.`;
  return d;
}

/* ---------- 09 Fed funds path (real snapshot) ---------- */
function renderFedPath(d) {
  const labels = d.series.map(p => p.horizon);
  new Chart($("fedPathChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "Market-implied (futures)", data: d.series.map(p => p.market_implied), borderColor: C.accent,
        borderWidth: 2, pointRadius: 3, tension: .1, spanGaps: false },
      { label: "Dot median (SEP)", data: d.series.map(p => p.dot_median), borderColor: C.amber,
        borderWidth: 2, stepped: true, pointRadius: 3 },
    ]},
    options: base({ scales: { x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("fed funds rate, %") } } }),
  });
  const div = d.series.filter(p => p.divergence_bps != null);
  new Chart($("fedDivChart"), {
    type: "bar",
    data: { labels: div.map(p => p.horizon), datasets: [
      { label: "Market − dots (bps)", data: div.map(p => p.divergence_bps),
        backgroundColor: div.map(p => p.divergence_bps >= 0 ? C.bad : C.accent) },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("market − dots, bps") } } }),
  });
  $("fedpath-note").textContent =
    `As of ${d.as_of}: market prices higher-for-longer than the dots — up to ${sign(d.max_divergence_bps)}bp in 2027 ` +
    `(futures near 4% vs a 3.6% dot median). Hawkish divergence = markets pricing independently of guidance.`;

  // dot-plot migration (end-2026 median across SEPs)
  const dh = d.dot_history || [];
  new Chart($("dotMigrationChart"), {
    type: "line",
    data: { labels: dh.map(p => p.meeting), datasets: [
      { label: "End-2026 dot median", data: dh.map(p => p.end2026_median), borderColor: C.amber,
        backgroundColor: "rgba(245,166,35,.10)", borderWidth: 2, pointRadius: 4, fill: true, stepped: false, tension: 0 },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("end-2026 median, %") } } }),
  });
  if (dh.length >= 2)
    $("dotmig-note").textContent =
      `The FOMC's own end-2026 median jumped ${dh[0].end2026_median}% → ${dh[dh.length-1].end2026_median}% ` +
      `at the June-2026 SEP — a hawkish repricing of the Fed's path itself.`;

  // incremental divergence tracking over time
  const dt = d.divergence_track || [];
  new Chart($("divTrackChart"), {
    type: "bar",
    data: { labels: dt.map(p => p.date), datasets: [
      { label: "Market − dots (bps)", data: dt.map(p => p.divergence_bps),
        backgroundColor: dt.map(p => p.divergence_bps >= 0 ? C.bad : C.accent) },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("end-2026 divergence, bps") } } }),
  });
  if (dt.length)
    $("divtrack-note").textContent =
      `Tracked snapshots: divergence moved ${sign(dt[0].divergence_bps)}bp → ${sign(dt[dt.length-1].divergence_bps)}bp ` +
      `as the market swung from below to above the dots. Re-run the collector to append new dated readings.`;
  return d;
}

/* ---------- 10 FOMC task forces ---------- */
function renderFomc(d) {
  const cls = s => s === "In progress" ? "progress" : s === "Watch" ? "watch" : "done";
  $("fomc-grid").innerHTML = d.items.map(it =>
    `<div class="status"><div class="st-top"><span class="st-name">${it.name}</span>
      <span class="pill ${cls(it.status)}">${it.status} · ${it.expected}</span></div>
      <div class="st-detail">${it.detail}</div></div>`).join("");
  return d;
}

/* ---------- boot ---------- */
async function main() {
  const [
    manifest, move, dataday, dealer, newissue, volume, fpm, share, tradeweb, fedpath, fomc, signal,
  ] = await Promise.all([
    "manifest", "move", "data_day_vol", "dealer_balance", "new_issue", "mktx_volume",
    "mktx_fpm", "market_share", "tradeweb", "fed_funds_path", "fomc_taskforce", "mktx_earnings_signal",
  ].map(n => loadJSON(`data/${n}.json`)));

  $("tickers").textContent = manifest.tickers;
  $("generated").textContent = manifest.generated;
  $("exec").textContent = manifest.thesis;
  $("bottomline").innerHTML = `<b>Bottom line.</b> ${manifest.bottom_line}`;
  $("method-body").textContent = manifest.thesis;

  // KPI strip — live figures pulled from the data
  const bn = v => Math.round(v / 1000);
  const s = dataday.summary || {};
  const atCagr = volume.avg_yoy_2026_pct >= volume.cagr_5y_pct;
  $("kpi-strip").innerHTML = [
    kpiCard("MOVE index", move.current,
      move.current >= 90 ? "above 90 watch line" : `below 90 · 90d avg ${move.avg_90d}`,
      { t: move.current >= 90 ? "elevated" : "calm", cls: move.current >= 90 ? "bad" : "good" }),
    kpiCard("Data-day |Δ2y|", `${s.recent12_abs_2y ?? s.avg_abs_2y_recent}bp`,
      `last 12 prints · ~${s.avg_abs_2y_early}bp in '22-23`,
      { t: "subdued", cls: "good" }),
    kpiCard("Dealer USTs", `$${bn(dealer.current)}bn`,
      `${dealer.yoy_change >= 0 ? "+" : "−"}$${Math.abs(bn(dealer.yoy_change))}bn YoY`, null),
    kpiCard("MKTX ADV YoY '26", `${sign(volume.avg_yoy_2026_pct)}%`,
      `vs ${volume.cagr_5y_pct}% 5y CAGR`,
      { t: atCagr ? "at/above CAGR" : "below CAGR", cls: atCagr ? "good" : "bad" }),
    kpiCard("TW vs MKTX", `+${tradeweb.avg_growth_gap_pp}pp`,
      "TW out-growing MKTX · US credit",
      { t: "TW leads", cls: "bad" }),
    kpiCard("MKTX Q2-26 signal", `${sign(signal.prediction.implied_vs_consensus_pct)}%`,
      `est $${signal.prediction.est_rev_mm}M vs cons $${signal.prediction.consensus_rev_mm}M`,
      { t: "miss risk", cls: "bad" }),
  ].join("");

  renderMove(move);
  renderDataDay(dataday);
  renderDealer(dealer);
  renderNewIssue(newissue);
  renderMktxVolume(volume);
  renderFpm(fpm);
  renderSignal(signal);
  renderShare(share);
  renderTradeweb(tradeweb);
  renderFedPath(fedpath);
  renderFomc(fomc);
}

main().catch(e => {
  console.error(e);
  const el = $("exec"); if (el) el.textContent = "Failed to load data: " + e.message;
});
