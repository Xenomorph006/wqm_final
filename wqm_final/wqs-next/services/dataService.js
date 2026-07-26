/**
 * dataService.js
 * -----------------------------------------------------------------------
 * Single place where every page reads/writes water-quality data.
 *
 * Point NEXT_PUBLIC_API_URL at your ESP32 / server bridge, e.g. in a
 * .env.local file at the project root:
 *   NEXT_PUBLIC_API_URL=http://192.168.1.50:5000
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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
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
  const data = await safeFetch("/api/live");
  if (!data) return { ...ZERO_METRICS, connected: false };
  return { ...ZERO_METRICS, ...data, connected: true };
}

/** Dashboard summary cards: total tests, good/moderate/poor %, avg quality score. */
export async function fetchDashboardStats() {
  const data = await safeFetch("/api/dashboard/stats");
  if (!data) {
    return {
      connected: false,
      totalTests: 0,
      goodPct: 0,
      moderatePct: 0,
      poorPct: 0,
      qualityScore: 0,
    };
  }
  return { connected: true, ...data };
}

/** Most recent N predictions/tests, newest first — sourced from backend DB. */
export async function fetchRecentPredictions(limit = 6) {
  const data = await safeFetch(`/api/predictions/recent?limit=${limit}`);
  if (!data) return { connected: false, items: [] };
  return { connected: true, items: Array.isArray(data) ? data : data.items || [] };
}

/** Historical time-series window for the live chart, e.g. last 30 points. */
export async function fetchHistorySeries(points = 30) {
  const data = await safeFetch(`/api/history?points=${points}`);
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
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(REPORTS_KEY)) || [];
  } catch {
    return [];
  }
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
