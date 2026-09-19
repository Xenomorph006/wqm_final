import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import bgImage from "../assets/water.jpg";
import LiveChart from "../components/LiveChart";
import { useAnimatedValue } from "../hooks/useAnimatedValue";
import {
  fetchDashboardStats,
  fetchHistorySeries,
  fetchLiveReadings,
  fetchRecentPredictions,
  METRIC_META,
} from "../services/dataService";
import "./Dashboard.css";

const SIDEBAR_LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: "◈" },
  { to: "/prediction", label: "Start Test", icon: "▶" },
  { to: "/reports", label: "Reports", icon: "▤" },
  { to: "/about", label: "About", icon: "ⓘ" },
  { to: "/contact", label: "Contact", icon: "✉" },
];

function StatCard({ label, value, suffix = "", tone = "" }) {
  const animated = useAnimatedValue(value);
  return (
    <div className={"card" + (tone ? ` tone-${tone}` : "")}>
      <h3>
        {animated.toFixed(value % 1 === 0 && value < 100 ? 0 : 1)}
        {suffix}
      </h3>
      <p>{label}</p>
    </div>
  );
}

/** Confidence card for a single sensor parameter — replaces the old good/moderate/poor split. */
function ConfidenceCard({ paramKey, value }) {
  const meta = METRIC_META[paramKey];
  const animated = useAnimatedValue(value || 0);
  return (
    <div className="confidence-card">
      <div className="confidence-top">
        <span className="confidence-label">{meta.label}</span>
        <span className="confidence-value" style={{ color: meta.color }}>
          {animated.toFixed(0)}%
        </span>
      </div>
      <div className="confidence-bar-track">
        <div
          className="confidence-bar-fill"
          style={{ width: `${Math.min(100, Math.max(0, animated))}%`, background: meta.color }}
        />
      </div>
    </div>
  );
}

/**
 * Recommendation pop-up — shows exactly ONE alert at a time, and only when a
 * real parameter is out of its safe range (never a generic "all good" line).
 * With more than one active issue it auto-advances through them like a toast
 * queue, with small dots underneath showing how many more are waiting.
 */
function RecommendationFeed({ connected, recommendations }) {
  const items = recommendations || [];
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (items.length <= 1) return undefined;
    const cycle = setInterval(() => {
      setVisible(false);
      setTimeout(() => {
        setIndex((i) => (i + 1) % items.length);
        setVisible(true);
      }, 260);
    }, 4200);
    return () => clearInterval(cycle);
  }, [items.length]);

  if (items.length === 0) {
    return (
      <div className="recommend-panel recommend-panel--calm">
        <span className="calm-dot" />
        <p>All parameters are within their safe range — no alerts right now.</p>
      </div>
    );
  }

  return (
    <div className="recommend-panel recommend-panel--alert">
      <div className="recommend-head">
        <span className="recommend-alert-label">⚠ Alert</span>
        <span className={"status-pill" + (connected ? " on" : "")}>
          <span className="status-dot" />
          {connected ? "Live from agent" : "Local estimate"}
        </span>
      </div>

      <div className={"recommend-toast" + (visible ? " show" : "")}>
        <span className="recommend-dot" />
        <span>{items[index]}</span>
      </div>

      {items.length > 1 && (
        <div className="recommend-dots">
          {items.map((_, i) => (
            <span key={i} className={"recommend-progress" + (i === index ? " active" : "")} />
          ))}
        </div>
      )}
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState({
    connected: false,
    totalTests: 0,
    qualityScore: 0,
    confidence: {},
    recommendations: [],
    issues: [],
  });
  const [series, setSeries] = useState([]);
  const [predictions, setPredictions] = useState({ connected: false, items: [] });

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      // No fetchLiveReadings() call here anymore — TestSessionProvider,
      // mounted at the app root, polls continuously regardless of which
      // page is active, so the buffer fetchHistorySeries() reads from is
      // already populated.
      const [s, h, p] = await Promise.all([
        fetchDashboardStats(),
        fetchHistorySeries(30),
        fetchRecentPredictions(6),
      ]);
      if (cancelled) return;
      setStats(s);
      setSeries(h.series);
      setPredictions(p);
    };

    poll();
    const interval = setInterval(poll, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);
  return (
    <div className="dashboard" style={{ backgroundImage: `url(${bgImage})` }}>
      <div className="overlay"></div>

      <div className="dashboard-content">
        <div className="sidebar">
          <h2 className="logo">💧 WQS</h2>
          <ul>
            {SIDEBAR_LINKS.map((link) => (
              <li key={link.to}>
                <NavLink
                  to={link.to}
                  className={({ isActive }) => (isActive ? "active" : "")}
                >
                  <span className="side-icon">{link.icon}</span>
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>

        <div className="main">
          <div className="topbar">
            <h2>Overview</h2>
            <span className={"status-pill" + (stats.connected ? " on" : "")}>
              <span className="status-dot" />
              {stats.connected ? "Backend connected" : "Backend not linked"}
            </span>
          </div>

          <RecommendationFeed
            key={(stats.issues || []).join("|")}
            connected={stats.connected}
            recommendations={stats.issues?.length ? stats.recommendations : []}
          />

          <div className="cards cards-compact cards-single">
            <StatCard label="Total Tests" value={stats.totalTests} />
          </div>

          <div className="confidence-section">
            <h3>Prediction Confidence</h3>
            <div className="confidence-grid">
              {Object.keys(METRIC_META).map((k) => (
                <ConfidenceCard key={k} paramKey={k} value={stats.confidence?.[k] ?? 0} />
              ))}
            </div>
          </div>

          <div className="chart-section">
            <h3>Water Quality — Live Stream</h3>
            <LiveChart series={series} connected={stats.connected} />
          </div>

          <div className="table-section">
            <div className="table-head">
              <h3>Recent Predictions</h3>
              <Link to="/reports" className="see-all">
                View all reports →
              </Link>
            </div>

            {predictions.items.length === 0 ? (
              <div className="empty-state">
                <p>
                  {predictions.connected
                    ? "No predictions recorded yet — run a test to see it here."
                    : "Waiting for the backend database — recorded tests will appear here automatically."}
                </p>
                <Link to="/prediction" className="btn ghost">Start a Test</Link>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>pH</th>
                    <th>Turbidity</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.items.map((row, i) => (
                    <tr key={row.id || i}>
                      <td>{row.date}</td>
                      <td>{row.ph}</td>
                      <td>{row.turbidity} NTU</td>
                      <td className={row.result?.toLowerCase()}>{row.result}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


export default Dashboard;
