import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import bgImage from "../assets/water.jpg";
import LiveChart from "../components/LiveChart";
import { useAnimatedValue } from "../hooks/useAnimatedValue";
import {
  fetchDashboardStats,
  fetchHistorySeries,
  fetchRecentPredictions,
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

function Dashboard() {
  const [stats, setStats] = useState({
    connected: false,
    totalTests: 0,
    goodPct: 0,
    moderatePct: 0,
    poorPct: 0,
    qualityScore: 0,
  });
  const [series, setSeries] = useState([]);
  const [predictions, setPredictions] = useState({ connected: false, items: [] });

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
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

          <div className="cards">
            <StatCard label="Total Tests" value={stats.totalTests} />
            <StatCard label="Good Water" value={stats.goodPct} suffix="%" tone="good" />
            <StatCard label="Moderate" value={stats.moderatePct} suffix="%" tone="moderate" />
            <StatCard label="Poor" value={stats.poorPct} suffix="%" tone="poor" />
            <StatCard label="Quality Score" value={stats.qualityScore} suffix="/100" />
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
