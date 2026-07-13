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
  $("dataday-note").textContent =
    `Avg |Δ2y| recent ${s.avg_abs_2y_recent} vs earlier ${s.avg_abs_2y_early} bps — ` +
    `${s.accelerating_2y ? "accelerating (data-centric)" : "not accelerating"}. ` +
    `10y: ${s.avg_abs_10y_recent} vs ${s.avg_abs_10y_early} bps.`;
  const tb = $("dataday-table").querySelector("tbody");
  tb.innerHTML = rows.slice().reverse().map(r => {
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
  return d;
}

/* ---------- 04 New issue (real annual + quarterly) ---------- */
function renderNewIssue(d) {
  const yrs = Object.keys(d.annual_ig).sort();
  new Chart($("newIssueChart"), {
    type: "bar",
    data: { labels: yrs, datasets: [
      { label: "IG gross issuance ($bn)", data: yrs.map(y => d.annual_ig[y]),
        backgroundColor: C.accent },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("annual IG issuance, $bn"), beginAtZero: true } } }),
  });
  const qs = Object.keys(d.quarterly_ig).sort();
  new Chart($("newIssueYoyChart"), {
    type: "bar",
    data: { labels: qs, datasets: [
      { label: "IG gross ($bn)", data: qs.map(q => d.quarterly_ig[q]), backgroundColor: C.amber },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("quarterly IG issuance, $bn"), beginAtZero: true } } }),
  });
  const recs = (d.record_months || []).map(r => `${monthLbl(r.month)} $${r.ig_bn}bn`).join(" · ");
  $("newissue-note").innerHTML =
    `IG issuance boom: $${d.annual_ig["2023"]}bn (2023) → $${d.annual_ig["2024"]}bn (2024) → $${d.annual_ig["2025"]}bn (2025). ` +
    `2026 total corp running +${d.ytd_2026.yoy_pct}% YoY (H1 $${(d.ytd_2026.total_corp_bn/1000).toFixed(2)}T). ` +
    `Record months: ${recs}. <span style="color:var(--amber)">Monthly detail via SIFMA xlsx drop (see script) — press monthly figures aren't basis-consistent.</span>`;
  return d;
}

/* ---------- 05 MKTX volume ---------- */
function renderMktxVolume(d) {
  const labels = d.series.map(p => monthLbl(p.month));
  new Chart($("mktxAdvChart"), {
    type: "line",
    data: { labels, datasets: [
      { label: "Total credit ADV ($bn)", data: d.series.map(p => p.adv_bn), borderColor: C.accent,
        backgroundColor: "rgba(79,140,255,.10)", borderWidth: 2, pointRadius: 0, fill: true, tension: .15 },
    ]},
    options: base({ plugins: { legend: { display: false } }, scales: {
      x: { grid: { color: C.grid }, ticks: { color: C.text, maxTicksLimit: 8 } },
      y: { grid: { color: C.grid }, ticks: { color: C.text }, title: axT("ADV, $ bn/day") } } }),
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
  const last = d.series[d.series.length - 1];
  $("volume-note").textContent =
    `Latest ADV ~$${last.adv_bn}bn (${last.yoy_pct != null ? sign(last.yoy_pct) + "% YoY" : "—"}); ` +
    `bull signal is YoY sustained above the ${d.cagr_5y_pct}% CAGR line.`;
  return d;
}

/* ---------- 06 FPM ---------- */
function renderFpm(d) {
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
    `MKTX flags TRACE duplicate reports understated 2026 share ~150-160bp in some months.`;
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
    manifest, move, dataday, dealer, newissue, volume, fpm, share, tradeweb, fedpath, fomc,
  ] = await Promise.all([
    "manifest", "move", "data_day_vol", "dealer_balance", "new_issue", "mktx_volume",
    "mktx_fpm", "market_share", "tradeweb", "fed_funds_path", "fomc_taskforce",
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
    kpiCard("Data-day |Δ2y|", `${s.avg_abs_2y_recent}bp`,
      `recent vs ${s.avg_abs_2y_early}bp earlier`,
      { t: s.accelerating_2y ? "accelerating" : "steady", cls: s.accelerating_2y ? "bad" : "good" }),
    kpiCard("Dealer USTs", `$${bn(dealer.current)}bn`,
      `${dealer.yoy_change >= 0 ? "+" : "−"}$${Math.abs(bn(dealer.yoy_change))}bn YoY`, null),
    kpiCard("MKTX ADV YoY '26", `${sign(volume.avg_yoy_2026_pct)}%`,
      `vs ${volume.cagr_5y_pct}% 5y CAGR`,
      { t: atCagr ? "at/above CAGR" : "below CAGR", cls: atCagr ? "good" : "bad" }),
    kpiCard("TW vs MKTX", `+${tradeweb.avg_growth_gap_pp}pp`,
      "TW out-growing MKTX · US credit",
      { t: "TW leads", cls: "bad" }),
  ].join("");

  renderMove(move);
  renderDataDay(dataday);
  renderDealer(dealer);
  renderNewIssue(newissue);
  renderMktxVolume(volume);
  renderFpm(fpm);
  renderShare(share);
  renderTradeweb(tradeweb);
  renderFedPath(fedpath);
  renderFomc(fomc);
}

main().catch(e => {
  console.error(e);
  const el = $("exec"); if (el) el.textContent = "Failed to load data: " + e.message;
});
