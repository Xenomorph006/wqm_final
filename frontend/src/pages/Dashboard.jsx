import { useEffect, useRef, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import bgImage from "../assets/water.jpg";
import LiveChart from "../components/LiveChart";

import FishCompatibility from "../components/FishCompatibility";
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
  // Base the decimal-place decision on the animated value itself, not the
  // target `value` prop — otherwise the digit count flickers mid-animation
  // whenever animated and value straddle an integer/100 boundary.
  const decimals = animated % 1 === 0 && animated < 100 ? 0 : 1;
  return (
    <div className={"card" + (tone ? ` tone-${tone}` : "")}>
      <h3>
        {animated.toFixed(decimals)}
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
  // Tracks the pending fade-out -> advance timeout so it can be cancelled on
  // unmount. Without this, the timeout fires after unmount and calls
  // setState on a dead component (React warning + a flash of stale content).
  const fadeTimeoutRef = useRef(null);

  useEffect(() => {
    if (items.length <= 1) return undefined;
    const cycle = setInterval(() => {
      setVisible(false);
      fadeTimeoutRef.current = setTimeout(() => {
        setIndex((i) => (i + 1) % items.length);
        setVisible(true);
        fadeTimeoutRef.current = null;
      }, 260);
    }, 4200);
    return () => {
      clearInterval(cycle);
      if (fadeTimeoutRef.current) {
        clearTimeout(fadeTimeoutRef.current);
        fadeTimeoutRef.current = null;
      }
    };
  }, [items.length]);

  if (items.length === 0) {
    return (
      <div className="recommend-panel recommend-panel--calm">
        <span className="calm-dot" />
        <p>All parameters are within their safe range — no alerts right now.</p>
      </div>
    );
  }

  // `items` can shrink (e.g. issues resolve) while `index` still points past
  // the new end — clamp so we never read `items[index]` as undefined.
  const safeIndex = index < items.length ? index : 0;

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
        <span>{items[safeIndex]}</span>
      </div>

      {items.length > 1 && (
        <div className="recommend-dots">
          {items.map((_, i) => (
            <span key={i} className={"recommend-progress" + (i === safeIndex ? " active" : "")} />
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
      // fetchHistorySeries() reads from the live buffer — fetchLiveReadings()
      // is the only thing that writes to it. Nothing on this page called it,
      // so the chart was always empty regardless of backend status. Await it
      // first so this cycle's point is in the buffer before history is read.
      try {
        await fetchLiveReadings();

        const [s, h, p] = await Promise.all([
          fetchDashboardStats(),
          fetchHistorySeries(30),
          fetchRecentPredictions(6),
        ]);
        if (cancelled) return;
        setStats(s);
        setSeries(h.series || []);
        // Defensively normalize: never trust the API to always include
        // `items`, or a bad/failed response would crash the whole page
        // at `predictions.items.length` below.
        setPredictions({
          connected: !!p?.connected,
          items: Array.isArray(p?.items) ? p.items : [],
        });
        
      } catch (err) {
        if (cancelled) return;
        console.error("Dashboard poll failed:", err);
      }
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

          <FishCompatibility data={stats.fishRecommendation} />

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