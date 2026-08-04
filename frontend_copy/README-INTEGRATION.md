# Water Quality System — Upgrade Notes

## What changed
- **New design system** — deep-sea "sonar" theme (colors/fonts/spacing) lives entirely in
  `src/index.css` as CSS variables, so every page shares one look.
- **Navbar** extracted to `src/components/Navbar.jsx`, now includes a **Reports** link and
  a glass 3D pill nav. **Footer** added (`src/components/Footer.jsx`) with quick links so
  every page can reach every other page (Home now also links out via three quick-link cards).
- **Dashboard** (`src/pages/Dashboard.jsx`) polls the backend every 5s for stats, a 30-point
  history series, and recent predictions. Cards count up gradually via `useAnimatedValue`
  instead of snapping straight to a number.
- **Live chart** (`src/components/LiveChart.jsx`) is a dependency-free animated SVG chart
  plotting all 5 metrics (pH, turbidity, dissolved O₂, temperature, TDS) at once, with a
  toggleable legend and a "LIVE" pulse indicator.
- **Start Test flow** (`src/pages/Prediction.jsx`) — pressing **Start Test** begins polling
  `/api/live` every 1.5s and tracks min/max/avg for all 5 metrics client-side. **Stop & Save
  Report** ends the run, classifies the result (Good/Moderate/Poor), and saves the report.
- **Reports page** (new — `src/pages/Reports.jsx`) lists every saved report as an expandable
  card showing the full min/max/avg range per metric.
- **Zero-state by design**: `src/services/dataService.js` is the only file that talks to
  your backend. Every fetch has a 3.5s timeout and, if the backend is unreachable, resolves
  to zeroed data instead of throwing — so the UI never breaks, it just waits quietly at 0
  and animates up the moment real numbers start arriving.

## Wiring up your ESP32 / backend

Set the API base URL once, e.g. create a `.env` file at the project root:

```
VITE_API_URL=http://<your-server-ip>:5000
```

Expected endpoints (adjust paths in `dataService.js` to match your actual API — these are
just the contract the frontend currently expects):

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/live` | `{ ph, turbidity, dissolvedOxygen, temperature, tds, timestamp }` — current sensor snapshot |
| GET | `/api/history?points=30` | `{ series: [{ timestamp, ph, turbidity, dissolvedOxygen, temperature, tds }, ...] }` |
| GET | `/api/dashboard/stats` | `{ totalTests, goodPct, moderatePct, poorPct, qualityScore }` |
| GET | `/api/predictions/recent?limit=6` | `[{ id, date, ph, turbidity, result }, ...]` |
| POST | `/api/tests/start` | fire-and-forget notice that a test session began |
| POST | `/api/reports` | body = finished report object; persist to DB |
| GET | `/api/reports` | `[{ id, date, durationSec, ranges, result }, ...]` — full history |

Reports are always also cached in `localStorage` (`wqs_reports_v1`) so the Reports page
keeps working offline and never loses a test even before the backend exists.

## Notes
- No new npm dependencies were added — the chart is hand-built SVG, so `npm install` /
  `npm run dev` should work exactly as before.
- Keep your existing `src/assets/water.jpg` — it's still referenced by every page background.
  `react.svg` is no longer used (replaced by the animated sonar signature element on Home).
