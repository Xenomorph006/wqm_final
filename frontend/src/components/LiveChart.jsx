import { useMemo, useState } from "react";
import { METRIC_META } from "../services/dataService";
import "./LiveChart.css";

const WIDTH = 640;
const HEIGHT = 220;
const PAD = 24;

/**
 * series: [{ timestamp, ph, turbidity, dissolvedOxygen, temperature, tds }, ...]
 * connected: whether backend is currently reachable
 */
function LiveChart({ series = [], connected = false }) {
  const [active, setActive] = useState(new Set(Object.keys(METRIC_META)));

  const toggle = (key) => {
    setActive((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  const paths = useMemo(() => {
    const points = series.length > 1 ? series : [{}, {}]; // at least a flat zero line
    const n = points.length;

    return Object.entries(METRIC_META).map(([key, meta]) => {
      const values = points.map((p) => Number(p[key]) || 0);
      const max = Math.max(...values, meta.safeRange[1] * 1.2, 1);
      const d = values
        .map((v, i) => {
          const x = PAD + (i / (n - 1)) * (WIDTH - PAD * 2);
          const y = HEIGHT - PAD - (v / max) * (HEIGHT - PAD * 2);
          return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
        })
        .join(" ");
      const last = values[values.length - 1];
      return { key, meta, d, last };
    });
  }, [series]);

  return (
    <div className="live-chart">
      <div className="live-chart-head">
        <div className="live-chart-title">
          <span className={"live-dot" + (connected ? " on" : "")} />
          {connected ? "Live sensor stream" : "Awaiting backend link"}
        </div>
        <div className="live-chart-legend">
          {paths.map(({ key, meta, last }) => (
            <button
              key={key}
              className={"legend-chip" + (active.has(key) ? "" : " off")}
              style={{ "--chip-color": meta.color }}
              onClick={() => toggle(key)}
              type="button"
            >
              <span className="chip-swatch" />
              {meta.label}
              <span className="chip-value">{connected ? last.toFixed(2) : "0.00"}</span>
            </button>
          ))}
        </div>
      </div>

      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="live-chart-svg" preserveAspectRatio="none">
        <defs>
          <pattern id="gridPattern" width="40" height="28" patternUnits="userSpaceOnUse">
            <path d="M40 0 L0 0 0 28" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect x="0" y="0" width={WIDTH} height={HEIGHT} fill="url(#gridPattern)" />
        <line x1={PAD} y1={HEIGHT - PAD} x2={WIDTH - PAD} y2={HEIGHT - PAD} stroke="rgba(255,255,255,0.12)" />

        {paths
          .filter((p) => active.has(p.key))
          .map(({ key, meta, d }) => (
            <path
              key={key}
              d={d}
              fill="none"
              stroke={meta.color}
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="chart-line"
              style={{ filter: connected ? `drop-shadow(0 0 6px ${meta.color})` : "none" }}
            />
          ))}

        {connected && (
          <line
            x1={WIDTH - PAD}
            y1={PAD}
            x2={WIDTH - PAD}
            y2={HEIGHT - PAD}
            stroke="var(--accent-cyan)"
            strokeWidth="1"
            className="sweep-line"
          />
        )}
      </svg>

      {!connected && (
        <p className="chart-empty-note">
          No sensor data yet — all metrics will hold at zero and animate in automatically
          once the ESP32 backend connects.
        </p>
      )}
    </div>
  );
}

export default LiveChart;
