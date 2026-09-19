/**
 * dataService.js (FIXED)
 * -----------------------------------------------------------------------
 * Single place where every page reads/writes water-quality data.
 *
 * Points to ESP32/backend bridge at 192.168.1.9:4000
 * Actual endpoint: POST /api/data
 * Response format: { success: true, data: { temperature, tds, ph, turbidity, dissolved_oxygen } }
 *
 * Offline-first: if backend unreachable, returns ZERO_METRICS so UI never crashes.
 * Reports always persist to localStorage; synced to backend when reachable.
 * -----------------------------------------------------------------------
 */

const API_URL = import.meta.env?.VITE_API_URL || "http://192.168.1.9:4000";
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
    console.warn(`API call failed: ${err.message}`);
    return null; // caller decides the fallback
  }
}

/** 
 * Poll-friendly: current sensor snapshot from ESP32.
 * Hits GET /api/data (backend reads directly from sensors).
 * Returns ZERO_METRICS if backend unreachable.
 */
export async function fetchLiveReadings() {
  const response = await safeFetch("/api/data", { method: "GET" });
  
  if (!response) {
    return { ...ZERO_METRICS, connected: false };
  }

  // Backend response: { success: true, data: { temperature, tds, ph, turbidity, dissolved_oxygen } }
  if (!response.success || !response.data) {
    return { ...ZERO_METRICS, connected: false };
  }

  const { temperature, tds, ph, turbidity, dissolved_oxygen } = response.data;
  
  return {
    ph: ph ?? 0,
    turbidity: turbidity ?? 0,
    dissolvedOxygen: dissolved_oxygen ?? 0,
    temperature: temperature ?? 0,
    tds: tds ?? 0,
    timestamp: new Date().toISOString(),
    connected: true,
  };
}

/**
 * Dashboard summary: total tests, quality score, confidence per parameter,
 * recommendations, and issues.
 *
 * When backend is unreachable, derives best-effort snapshot from most recent
 * locally saved test. With no local history, everything holds at zero.
 */
export async function fetchDashboardStats() {
  // Try to get fresh data from backend
  const data = await safeFetch("/api/data", { method: "GET" });
  
  if (data && data.success && data.data) {
    const { temperature, tds, ph, turbidity, dissolved_oxygen } = data.data;
    const evaluation = evaluateWaterQuality({ ph, turbidity, temperature, dissolvedOxygen: dissolved_oxygen, tds });
    const recommendations = generateRecommendations(evaluation);
    const confidence = estimateConfidenceMap({
      ph: { min: ph, max: ph },
      turbidity: { min: turbidity, max: turbidity },
      dissolvedOxygen: { min: dissolved_oxygen, max: dissolved_oxygen },
      temperature: { min: temperature, max: temperature },
      tds: { min: tds, max: tds },
    });

    return {
      connected: true,
      totalTests: 1,
      qualityScore: evaluation.status === "Healthy" ? 100 : evaluation.status === "Warning" ? 60 : 30,
      confidence,
      recommendations,
      issues: evaluation.issues,
    };
  }

  // Fallback: use local reports
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
    recommendations: latest.issues && latest.issues.length > 0 ? latest.recommendations || [] : [],
    issues: latest.issues || [],
  };
}

/** Most recent N test reports from localStorage. */
export async function fetchRecentPredictions(limit = 6) {
  const local = getLocalReports();
  return {
    connected: true,
    items: local.slice(0, limit),
  };
}

/** Historical time-series for the live chart (last 30 points from local cache). */
export async function fetchHistorySeries(points = 30) {
  const local = getLocalReports();
  const series = local.slice(0, points).map((r) => ({
    timestamp: r.timestamp,
    ph: r.ph,
    turbidity: r.turbidity,
    temperature: r.temperature,
    dissolvedOxygen: r.dissolvedOxygen,
    tds: r.tds,
  }));
  return { connected: true, series };
}

/** Notify backend that a test session has started (best-effort). */
export async function notifyTestStart() {
  return safeFetch("/api/tests/start", { method: "POST" });
}

/** Persist a finished test report. Always saved locally; synced to backend if reachable. */
export async function saveReport(report) {
  const local = getLocalReports();
  const withId = { ...report, id: report.id || `local-${Date.now()}` };
  const updated = [withId, ...local];
  localStorage.setItem(REPORTS_KEY, JSON.stringify(updated));

  // Try to sync to backend (best-effort)
  await safeFetch("/api/reports", {
    method: "POST",
    body: JSON.stringify(report),
  });

  return withId;
}

function getLocalReports() {
  try {
    return JSON.parse(localStorage.getItem(REPORTS_KEY)) || [];
  } catch {
    return [];
  }
}

/** Wipes every locally cached report from this browser. */
export function clearLocalReports() {
  localStorage.removeItem(REPORTS_KEY);
}

/** All reports: backend-first, merged with local-only cache. */
export async function getReports() {
  const remote = await safeFetch("/api/reports");
  const local = getLocalReports();
  if (!remote) return { connected: false, items: local };

  const remoteItems = Array.isArray(remote) ? remote : remote.items || [];
  const remoteIds = new Set(remoteItems.map((r) => r.id));
  const localOnly = local.filter((r) => !remoteIds.has(r.id));
  return { connected: true, items: [...remoteItems, ...localOnly] };
}

/** Classify water quality based on three key metrics. */
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
 * Evaluate water quality against safe ranges.
 * Returns: { status, riskLevel, issues }
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

/** Human-readable recommendations derived from issues. */
export function generateRecommendations({ issues } = { issues: [] }) {
  if (!issues || issues.length === 0) {
    return ["Water quality is currently stable and within the safe operating range."];
  }
  return issues.map(
    (issue) => RECOMMENDATION_MAP[issue] || `Monitor "${issue}" closely and take corrective action.`
  );
}

/**
 * Heuristic confidence (0-100) for a single metric, based on spread
 * relative to the safe range.
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

/** Per-parameter confidence map for a test's min/max/avg ranges. */
export function estimateConfidenceMap(ranges) {
  const map = {};
  Object.keys(METRIC_META).forEach((k) => {
    map[k] = ranges?.[k] ? estimateConfidence(ranges[k], METRIC_META[k].safeRange) : 0;
  });
  return map;
}