"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getReports, METRIC_META } from "../../services/dataService";
import "./Reports.css";

export default function Reports() {
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

  const toggle = (id) => setOpenId((prev) => (prev === id ? null : id));

  return (
    <div className="page reports-page" style={{ backgroundImage: "url(/water.jpg)" }}>
      <div className="overlay"></div>

      <div className="content reports-content">
        <div className="reports-head">
          <h1>Test Reports</h1>
          <p>
            Every completed test is saved here with its full min / max / average
            range for each sensor metric.
          </p>
          <span className={"status-pill" + (state.connected ? " on" : "")}>
            <span className="status-dot" />
            {state.connected ? "Synced with backend database" : "Showing locally cached reports"}
          </span>
        </div>

        {state.items.length === 0 ? (
          <div className="empty-reports">
            <p>No reports yet. Run your first test to start building a history.</p>
            <Link href="/prediction" className="btn">Start a Test</Link>
          </div>
        ) : (
          <div className="reports-list">
            {state.items.map((r) => (
              <div key={r.id} className="report-card">
                <button className="report-summary" onClick={() => toggle(r.id)}>
                  <div className="summary-left">
                    <span className={"result-dot " + (r.result || "").toLowerCase()} />
                    <div>
                      <h3>{r.date}</h3>
                      <span className="summary-sub">
                        Duration {Math.floor((r.durationSec || 0) / 60)}m {(r.durationSec || 0) % 60}s
                      </span>
                    </div>
                  </div>
                  <div className="summary-right">
                    <span className={"result-badge " + (r.result || "").toLowerCase()}>{r.result}</span>
                    <span className="chevron">{openId === r.id ? "−" : "+"}</span>
                  </div>
                </button>

                {openId === r.id && r.ranges && (
                  <table className="range-table">
                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Avg</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.keys(METRIC_META).map((k) => {
                        const range = r.ranges[k];
                        if (!range) return null;
                        return (
                          <tr key={k}>
                            <td>{METRIC_META[k].label}</td>
                            <td>{range.min.toFixed(2)}</td>
                            <td>{range.max.toFixed(2)}</td>
                            <td>{range.avg.toFixed(2)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
