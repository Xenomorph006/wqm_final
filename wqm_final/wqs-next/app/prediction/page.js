"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  classifyQuality,
  fetchLiveReadings,
  METRIC_META,
  notifyTestStart,
  saveReport,
} from "../../services/dataService";
import "./Prediction.css";

const POLL_MS = 1500;
const METRIC_KEYS = Object.keys(METRIC_META);

function emptyStats() {
  const s = {};
  METRIC_KEYS.forEach((k) => (s[k] = { min: Infinity, max: -Infinity, sum: 0, count: 0 }));
  return s;
}

function elapsedLabel(seconds) {
  const m = String(Math.floor(seconds / 60)).padStart(2, "0");
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}

export default function Prediction() {
  const [status, setStatus] = useState("idle"); // idle | running | done
  const [connected, setConnected] = useState(false);
  const [live, setLive] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [report, setReport] = useState(null);

  const statsRef = useRef(emptyStats());
  const intervalRef = useRef(null);
  const timerRef = useRef(null);

  const startTest = async () => {
    statsRef.current = emptyStats();
    setElapsed(0);
    setReport(null);
    setStatus("running");
    await notifyTestStart();

    intervalRef.current = setInterval(async () => {
      const reading = await fetchLiveReadings();
      setLive(reading);
      setConnected(reading.connected);
      METRIC_KEYS.forEach((k) => {
        const v = Number(reading[k]) || 0;
        const st = statsRef.current[k];
        st.min = Math.min(st.min, v);
        st.max = Math.max(st.max, v);
        st.sum += v;
        st.count += 1;
      });
    }, POLL_MS);

    timerRef.current = setInterval(() => setElapsed((e) => e + 1), 1000);
  };

  const stopTest = async () => {
    clearInterval(intervalRef.current);
    clearInterval(timerRef.current);
    setStatus("done");

    const ranges = {};
    METRIC_KEYS.forEach((k) => {
      const st = statsRef.current[k];
      const hasData = st.count > 0;
      ranges[k] = {
        min: hasData && isFinite(st.min) ? st.min : 0,
        max: hasData && isFinite(st.max) ? st.max : 0,
        avg: hasData ? st.sum / st.count : 0,
      };
    });

    const result = classifyQuality({
      ph: ranges.ph.avg,
      turbidity: ranges.turbidity.avg,
      dissolvedOxygen: ranges.dissolvedOxygen.avg,
    });

    const finalReport = {
      id: `test-${Date.now()}`,
      date: new Date().toLocaleString(),
      durationSec: elapsed,
      ranges,
      result,
      backendConnected: connected,
    };

    const saved = await saveReport(finalReport);
    setReport(saved);
  };

  const resetTest = () => {
    setStatus("idle");
    setReport(null);
    setLive(null);
    setElapsed(0);
  };

  useEffect(() => {
    return () => {
      clearInterval(intervalRef.current);
      clearInterval(timerRef.current);
    };
  }, []);

  return (
    <div className="page" style={{ backgroundImage: "url(/water.jpg)" }}>
      <div className="overlay"></div>

      <div className="content predict-content">
        {status !== "done" ? (
          <div className="form-container test-panel">
            <h2>Water Quality Test</h2>
            <p className="panel-sub">
              {status === "idle"
                ? "Press start to begin sampling from your ESP32 sensor array. We'll track the min, max and average of every metric until you stop the test."
                : "Sampling in progress — keep the sensor submerged until you stop the test."}
            </p>

            {status === "running" && (
              <>
                <div className="live-status-row">
                  <span className={"live-badge" + (connected ? " on" : "")}>
                    <span className="dot" /> {connected ? "Reading live sensor" : "No backend — holding at 0"}
                  </span>
                  <span className="timer">{elapsedLabel(elapsed)}</span>
                </div>

                <div className="live-grid">
                  {METRIC_KEYS.map((k) => (
                    <div key={k} className="live-metric">
                      <span className="metric-value">
                        {(live?.[k] ?? 0).toFixed(2)}
                        <small>{METRIC_META[k].unit}</small>
                      </span>
                      <span className="metric-label">{METRIC_META[k].label}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {status === "idle" ? (
              <button onClick={startTest} className="start-btn">▶ Start Test</button>
            ) : (
              <button onClick={stopTest} className="stop-btn">■ Stop &amp; Save Report</button>
            )}
          </div>
        ) : (
          <div className="form-container report-panel">
            <h2>Test Complete</h2>
            <span className={"result-badge " + report.result.toLowerCase()}>{report.result}</span>
            <p className="panel-sub">
              Duration {elapsedLabel(report.durationSec)} · {report.date}
            </p>

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
                {METRIC_KEYS.map((k) => (
                  <tr key={k}>
                    <td>{METRIC_META[k].label}</td>
                    <td>{report.ranges[k].min.toFixed(2)}</td>
                    <td>{report.ranges[k].max.toFixed(2)}</td>
                    <td>{report.ranges[k].avg.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="report-actions">
              <button onClick={resetTest} className="btn ghost">Run Another Test</button>
              <Link href="/reports" className="btn">View All Reports</Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
