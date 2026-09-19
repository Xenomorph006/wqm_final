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
    // Ensure we always have at least 2 points for a valid line
    const points = series && series.length > 1 ? series : [{}, {}];
    const n = points.length;

    return Object.entries(METRIC_META).map(([key, meta]) => {
      // Extract numeric values from all points
      const values = points.map((p) => {
        const val = Number(p[key]);
        return isNaN(val) || val === null || val === undefined ? 0 : val;
      });

      // Calculate dynamic max based on actual data + safe range
      const dataMax = Math.max(...values);
      const safeMax = meta.safeRange[1] * 1.2;
      const minScale = 1;
      const max = Math.max(dataMax, safeMax, minScale);

      // Build SVG path
      const d = values
        .map((v, i) => {
          const x = PAD + (i / Math.max(n - 1, 1)) * (WIDTH - PAD * 2);
          const y = HEIGHT - PAD - (v / max) * (HEIGHT - PAD * 2);
          return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
        })
        .join(" ");

      const last = values[values.length - 1] || 0;

      return { key, meta, d, last, max };
    });
  }, [series]);

  const hasData = series && series.length > 0;

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
              <span className="chip-value">
                {hasData && connected ? last.toFixed(2) : "0.00"}
              </span>
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
        <line
          x1={PAD}
          y1={HEIGHT - PAD}
          x2={WIDTH - PAD}
          y2={HEIGHT - PAD}
          stroke="rgba(255,255,255,0.12)"
          strokeWidth="1"
        />

        {/* Render active metric lines */}
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
              style={{
                filter: connected && hasData ? `drop-shadow(0 0 6px ${meta.color})` : "none",
              }}
            />
          ))}

        {/* Sweep line (right edge, only when live) */}
        {connected && hasData && (
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

      {connected && !hasData && (
        <p className="chart-empty-note">
          Connected, waiting for first sensor reading...
        </p>
      )}
    </div>
  );
}

export default LiveChart;