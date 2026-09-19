import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import bgImage from "../assets/water.jpg";
import {
  clearLocalReports,
  evaluateWaterQuality,
  fetchLiveReadings,
  getReports,
  METRIC_META,
} from "../services/dataService";
import "./Reports.css";

const METRIC_KEYS = Object.keys(METRIC_META);
const LIVE_POLL_MS = 2000;

/** Segmented tab bar shared by both report views. Water Reports is the default/home tab. */
function ReportTabs({ active }) {
  return (
    <div className="report-tabs">
      <Link to="/reports" className={"report-tab" + (active === "history" ? " active" : "")}>
        Water Reports
      </Link>
      <Link to="/reports/current" className={"report-tab" + (active === "current" ? " active" : "")}>
        Current Water Reading
      </Link>
    </div>
  );
}

/** Status / Risk Level / Issues, each shown as its own labelled topic — used inside a Water Reports card. */
function VerdictTopics({ status, riskLevel, issues }) {
  return (
    <div className="verdict-topics">
      <div className="verdict-topic">
        <span className="verdict-topic-label">Status</span>
        <span className={"tag status-" + (status || "healthy").toLowerCase()}>{status || "Healthy"}</span>
      </div>
      <div className="verdict-topic">
        <span className="verdict-topic-label">Risk Level</span>
        <span className={"tag risk-" + (riskLevel || "low").toLowerCase()}>{riskLevel || "LOW"}</span>
      </div>
      <div className="verdict-topic verdict-topic--issues">
        <span className="verdict-topic-label">Issues</span>
        <span className="tag issues-tag">
          {issues && issues.length > 0 ? issues.join(", ") : "None detected"}
        </span>
      </div>
    </div>
  );
}

/** Compact Status / Risk Level / Issues table — one row for the live current reading. */
function VerdictTable({ status, riskLevel, issues }) {
  return (
    <table className="verdict-table">
      <thead>
        <tr>
          <th>Status</th>
          <th>Risk Level</th>
          <th>Issues</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <span className={"tag status-" + (status || "healthy").toLowerCase()}>{status || "Healthy"}</span>
          </td>
          <td>
            <span className={"tag risk-" + (riskLevel || "low").toLowerCase()}>{riskLevel || "LOW"}</span>
          </td>
          <td className="col-issues">
            {issues && issues.length > 0 ? issues.join(", ") : "None detected"}
          </td>
        </tr>
      </tbody>
    </table>
  );
}

/** A grid of big metric values — shared visual language for both live and historical readings. */
function MetricGrid({ values }) {
  return (
    <div className="live-grid">
      {METRIC_KEYS.map((k) => (
        <div key={k} className="live-metric">
          <span className="metric-value">
            {(values[k] ?? 0).toFixed(2)}
            <small>{METRIC_META[k].unit}</small>
          </span>
          <span className="metric-label">{METRIC_META[k].label}</span>
        </div>
      ))}
    </div>
  );
}

/** "Current Water Reading" — the live snapshot, with Status/Risk Level/Issues as a compact table row. */
function CurrentReading() {
  const navigate = useNavigate();
  const [live, setLive] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      const reading = await fetchLiveReadings();
      if (cancelled) return;
      setLive(reading);
      setConnected(reading.connected);
    };
    poll();
    const interval = setInterval(poll, LIVE_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const readings = live || { ph: 0, turbidity: 0, dissolvedOxygen: 0, temperature: 0, tds: 0 };
  const evaluation = evaluateWaterQuality(readings);

  return (
    <div
      className="current-reading-card"
      role="button"
      tabIndex={0}
      onClick={() => navigate("/reports")}
      onKeyDown={(e) => e.key === "Enter" && navigate("/reports")}
    >
      <div className="current-reading-head">
        <div>
          <h3>Live Sensor Snapshot</h3>
          <span className="summary-sub">
            {connected ? "Streaming from the ESP32 backend" : "Backend not linked — holding at 0"}
          </span>
        </div>
        <span className={"status-pill" + (connected ? " on" : "")}>
          <span className="status-dot" />
          {connected ? "Live" : "Offline"}
        </span>
      </div>

      <VerdictTable status={evaluation.status} riskLevel={evaluation.riskLevel} issues={evaluation.issues} />
      <MetricGrid values={readings} />

      <span className="current-reading-cta">View all past test reports →</span>
    </div>
  );
}

/** One saved test, rendered as its own numbered card with a metric grid. */
function ReadingCard({ index, report, open, onToggle }) {
  const avg = {};
  METRIC_KEYS.forEach((k) => {
    avg[k] = report.ranges?.[k]?.avg ?? 0;
  });

  return (
    <div className="reading-card">
      <div className="current-reading-head">
        <div>
          <h3>
            <span className="report-index">{index}.</span> {report.date}
          </h3>
          <span className="summary-sub">
            Duration {Math.floor((report.durationSec || 0) / 60)}m {(report.durationSec || 0) % 60}s
          </span>
        </div>
        <span className={"result-badge " + (report.result || "").toLowerCase()}>{report.result}</span>
      </div>

      <MetricGrid values={avg} />

      {report.ranges && (
        <>
          <button className="detail-toggle" onClick={onToggle}>
            {open ? "Hide min / max / confidence −" : "Show min / max / confidence +"}
          </button>

          {open && (
            <table className="range-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Min</th>
                  <th>Max</th>
                  <th>Avg</th>
                  {report.confidence && <th>Confidence</th>}
                </tr>
              </thead>
              <tbody>
                {METRIC_KEYS.map((k) => {
                  const range = report.ranges[k];
                  if (!range) return null;
                  return (
                    <tr key={k}>
                      <td>{METRIC_META[k].label}</td>
                      <td>{range.min.toFixed(2)}</td>
                      <td>{range.max.toFixed(2)}</td>
                      <td>{range.avg.toFixed(2)}</td>
                      {report.confidence && <td>{report.confidence[k] ?? 0}%</td>}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}

/** "Water Reports" — every saved test, numbered, each shown as its own full reading card. */
function WaterReports() {
  const [state, setState] = useState({ connected: false, items: [] });
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getReports().then((res) => {
      if (!cancelled) setState(res);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const toggleDetail = (id) => setOpenId((prev) => (prev === id ? null : id));

  const handleClear = () => {
    if (!window.confirm("Clear all locally saved test reports from this browser? This can't be undone.")) return;
    clearLocalReports();
    getReports().then(setState);
  };

  if (state.items.length === 0) {
    return (
      <div className="empty-reports">
        <p>No reports yet. Run your first test to start building a history.</p>
        <Link to="/prediction" className="btn">Start a Test</Link>
      </div>
    );
  }

  return (
    <>
      <div className="reports-toolbar">
        <span className="reports-count">
          {state.items.length} saved {state.items.length === 1 ? "report" : "reports"}
        </span>
        <button className="clear-history-btn" onClick={handleClear}>Clear local history</button>
      </div>

      <div className="reading-list">
        {state.items.map((r, i) => (
          <ReadingCard
            key={r.id}
            index={i + 1}
            report={r}
            open={openId === r.id}
            onToggle={() => toggleDetail(r.id)}
          />
        ))}
      </div>
    </>
  );
}

function Reports() {
  const location = useLocation();
  const active = location.pathname.endsWith("/current") ? "current" : "history";

  return (
    <div className="page reports-page" style={{ backgroundImage: `url(${bgImage})` }}>
      <div className="overlay"></div>

      <div className="content reports-content">
        <div className="reports-head">
          <h1>Test Reports</h1>
          <p>
            {active === "history"
              ? "Every completed test, numbered and listed with its status, risk level, and detected issues."
              : "This is what your sensors are reading right now — click it any time to jump to the full test history."}
          </p>
        </div>

        <ReportTabs active={active} />

        {active === "history" ? <WaterReports /> : <CurrentReading />}
      </div>
    </div>
  );
}

export default Reports;