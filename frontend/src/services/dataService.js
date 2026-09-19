/**
 * dataService.js
 * -----------------------------------------------------------------------
 * Single place where every page reads/writes water-quality data.
 *
 * Point VITE_API_URL at your ESP32 / server bridge, e.g. in a .env file:
 *   VITE_API_URL=http://192.168.1.50:5000
 *
 * Until a backend is reachable, every "live" call resolves with a
 * ZERO_METRICS object instead of throwing — so the UI always renders a
 * calm, empty state rather than an error screen. The moment the backend
 * responds, real numbers flow in and the UI animates up from zero.
 *
 * Test reports are always persisted locally (localStorage) as a durable
 * cache, and are also pushed to the backend when one is reachable, so
 * the Reports page never loses history even offline.
 * -----------------------------------------------------------------------
 */

const API_URL = import.meta.env?.VITE_API_URL || "http://localhost:8000";
const REPORTS_KEY = "wqs_reports_v1";
const TIMEOUT_MS = 3500;

export const ZERO_METRICS = {
  ph: 0,
  turbidity: 0,
  dissolvedOxygen: 0,
  temperature: 0,
  tds: 0,
  timestamp: null,
};

export const METRIC_META = {
  ph: { label: "pH Level", unit: "", color: "var(--accent-cyan)", safeRange: [6.5, 8.5] },
  turbidity: { label: "Turbidity", unit: "NTU", color: "var(--accent-violet)", safeRange: [0, 5] },
  dissolvedOxygen: { label: "Dissolved O₂", unit: "mg/L", color: "var(--success)", safeRange: [5, 14] },
  temperature: { label: "Temperature", unit: "°C", color: "var(--warning)", safeRange: [10, 30] },
  tds: { label: "TDS", unit: "ppm", color: "#ff7ad9", safeRange: [0, 500] },
};

export const ZERO_CONFIDENCE = {
  ph: 0,
  turbidity: 0,
  dissolvedOxygen: 0,
  temperature: 0,
  tds: 0,
};

async function safeFetch(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    clearTimeout(timer);
    return null; // caller decides the fallback
  }
}

/** Poll-friendly: current sensor snapshot. Returns ZERO_METRICS if backend is unreachable. */
export async function fetchLiveReadings() {
  const data = await safeFetch("/api/v1/process",{
    method:  "POST",
    body:
    JSON.stringify(sensorData),});
  if (!data) return { ...ZERO_METRICS, connected: false };
  return { ...ZERO_METRICS, ...data, connected: true };
}

/**
 * Dashboard summary: total tests, avg quality score, per-parameter prediction
 * confidence, and the agent's latest recommendation messages.
 *
 * When the backend is unreachable we don't fabricate numbers — instead we
 * derive a best-effort snapshot from the most recently *locally saved* test
 * (if any), so the dashboard still reflects something real. With no local
 * history either, everything holds at zero, matching the rest of the app.
 */
export async function fetchDashboardStats() {
  const data = await safeFetch("/api/v1/ml/status");
  if (data) {
    return {
      connected: true,
      totalTests: 0,
      qualityScore: 0,
      confidence: ZERO_CONFIDENCE,
      recommendations: [],
      issues: [],
      ...data,
    };
  }

  const local = getLocalReports();
  const latest = local[0];

  if (!latest) {
    return {
      connected: false,
      totalTests: 0,
      qualityScore: 0,
      confidence: ZERO_CONFIDENCE,
      recommendations: [],
      issues: [],
    };
  }

  const goodCount = local.filter((r) => r.result === "Good").length;
  const qualityScore = Math.round((goodCount / local.length) * 100);

  return {
    connected: false,
    totalTests: local.length,
    qualityScore,
    confidence: latest.confidence || ZERO_CONFIDENCE,
    // Only real, issue-driven messages — never the "all stable" filler line —
    // so the dashboard can pop these up one at a time as alerts.
    recommendations: latest.issues && latest.issues.length > 0 ? latest.recommendations || [] : [],
    issues: latest.issues || [],
  };
}

/** Most recent N predictions/tests, newest first — sourced from backend DB. */
export async function fetchRecentPredictions(limit = 6) {
  const data = await safeFetch("/api/v1/process-batch",{
    method:  "POST",
    body:
    JSON.stringify(sensorData),});
  if (!data) return { connected: false, items: [] };
  return { connected: true, items: Array.isArray(data) ? data : data.items || [] };
}

/** Historical time-series window for the live chart, e.g. last 30 points. */
export async function fetchHistorySeries(points = 30) {
  const data = await safeFetch(`/api/v1/ml/status`);
  if (!data) return { connected: false, series: [] };
  return { connected: true, series: Array.isArray(data) ? data : data.series || [] };
}

/** Tell the backend a test/session has started (best-effort, ignored if offline). */
export async function notifyTestStart() {
  return safeFetch("/api/tests/start", { method: "POST" });
}

/** Persist a finished test report. Always saved locally; synced to backend if reachable. */
export async function saveReport(report) {
  const local = getLocalReports();
  const withId = { ...report, id: report.id || `local-${Date.now()}` };
  const updated = [withId, ...local];
  localStorage.setItem(REPORTS_KEY, JSON.stringify(updated));

  const remote = await safeFetch("/api/reports", {
    method: "POST",
    body: JSON.stringify(report),
  });

  return remote || withId;
}

function getLocalReports() {
  try {
    return JSON.parse(localStorage.getItem(REPORTS_KEY)) || [];
  } catch {
    return [];
  }
}

/** Wipes every locally cached report from this browser. Does not touch the backend DB. */
export function clearLocalReports() {
  localStorage.removeItem(REPORTS_KEY);
}

/** All reports, backend-first, merged with any local-only cache. */
export async function getReports() {
  const remote = await safeFetch("/api/reports");
  const local = getLocalReports();
  if (!remote) return { connected: false, items: local };

  const remoteItems = Array.isArray(remote) ? remote : remote.items || [];
  const remoteIds = new Set(remoteItems.map((r) => r.id));
  const localOnly = local.filter((r) => !remoteIds.has(r.id));
  return { connected: true, items: [...remoteItems, ...localOnly] };
}

export function classifyQuality({ ph, turbidity, dissolvedOxygen }) {
  const phOk = ph >= 6.5 && ph <= 8.5;
  const turbidityOk = turbidity <= 5;
  const doOk = dissolvedOxygen >= 5;
  const score = [phOk, turbidityOk, doOk].filter(Boolean).length;
  if (score === 3) return "Good";
  if (score === 2) return "Moderate";
  return "Poor";
}

/**
 * Mirrors the water-quality agent's rules (see backend/agent_backend
 * app/agent/water_agent.py) so the frontend can label a test with the same
 * status / risk level / issue list even when it only has the raw averages.
 */
export function evaluateWaterQuality({ ph, turbidity, temperature, dissolvedOxygen, tds }) {
  const issues = [];

  if (ph < 6.5) issues.push("Low pH");
  else if (ph > 8.5) issues.push("High pH");

  if (turbidity > 25) issues.push("High Turbidity");

  if (temperature < 20) issues.push("Low Temperature");
  else if (temperature > 32) issues.push("High Temperature");

  if (dissolvedOxygen < 5) issues.push("Low Dissolved Oxygen");

  if (tds > 500) issues.push("High TDS");

  let status = "Healthy";
  let riskLevel = "LOW";
  if (issues.length === 1) {
    status = "Warning";
    riskLevel = "MEDIUM";
  } else if (issues.length > 1) {
    status = "Critical";
    riskLevel = "HIGH";
  }

  return { status, riskLevel, issues };
}

const RECOMMENDATION_MAP = {
  "Low pH": "pH is trending acidic — consider dosing an alkaline buffer to bring it back toward the 6.5–8.5 safe band.",
  "High pH": "pH is trending alkaline — consider dosing a mild acid to bring it back toward the 6.5–8.5 safe band.",
  "High Turbidity": "Turbidity is elevated — run the filtration/water pump cycle to clear suspended particles.",
  "Low Temperature": "Water is colder than ideal — enable the heater to bring it back into range.",
  "High Temperature": "Water is warmer than ideal — enable the cooling system to bring it back into range.",
  "Low Dissolved Oxygen": "Dissolved oxygen is low — start the aerator to improve oxygenation.",
  "High TDS": "Total dissolved solids are high — consider partial water replacement or filtration.",
};

/** Human-readable recommendation messages, derived from an evaluation's issue list. */
export function generateRecommendations({ issues } = { issues: [] }) {
  if (!issues || issues.length === 0) {
    return ["Water quality is currently stable and within the safe operating range."];
  }
  return issues.map(
    (issue) => RECOMMENDATION_MAP[issue] || `Monitor "${issue}" closely and take corrective action.`
  );
}

/**
 * Heuristic confidence (0-100) for a single metric, based on how tightly the
 * readings held together relative to that metric's safe band — a wide swing
 * during the test lowers confidence in the average being representative.
 */
function estimateConfidence(range, safeRange) {
  if (!range) return 0;
  const [lo, hi] = safeRange;
  const bandSize = Math.max(hi - lo, 1e-6);
  const spread = Math.max(0, (range.max ?? 0) - (range.min ?? 0));
  const noise = Math.min(1, spread / bandSize);
  const score = 96 - noise * 45;
  return Math.round(Math.max(35, Math.min(99, score)));
}

/** Per-parameter confidence map for a finished test's min/max/avg ranges. */
export function estimateConfidenceMap(ranges) {
  const map = {};
  Object.keys(METRIC_META).forEach((k) => {
    map[k] = ranges?.[k] ? estimateConfidence(ranges[k], METRIC_META[k].safeRange) : 0;
  });
  return map;
}
