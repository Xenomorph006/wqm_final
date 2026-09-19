import { getDB } from "../config/db.js";
import { fetchRealtimeData } from "./Realtimecontroller.js";

// In-memory registry of tests currently in progress, keyed by test id.
const activeTests = new Map();

const DEFAULT_DURATION_MS = Number(process.env.TEST_DURATION_MS ?? 30000);
const SAMPLE_INTERVAL_MS = Number(process.env.TEST_SAMPLE_INTERVAL_MS ?? 5000);

function average(nums) {
    const valid = nums.filter((n) => typeof n === "number" && !Number.isNaN(n));
    if (!valid.length) return null;
    return valid.reduce((a, b) => a + b, 0) / valid.length;
}

// Very rough potability heuristic — tune thresholds to your sensor calibration.
function scorePotability({ ph, turbidity, tds, dissolved_oxygen }) {
    let ok = true;
    const reasons = [];

    if (ph !== null && (ph < 6.5 || ph > 8.5)) { ok = false; reasons.push("pH out of range"); }
    if (turbidity !== null && turbidity > 5) { ok = false; reasons.push("turbidity too high"); }
    if (tds !== null && tds > 500) { ok = false; reasons.push("TDS too high"); }
    if (dissolved_oxygen !== null && dissolved_oxygen < 4) { ok = false; reasons.push("dissolved oxygen too low"); }

    return { potable: ok, reasons };
}

async function runTestSession(testId, durationMs) {
    const samples = [];
    const startedAt = new Date();
    const endAt = Date.now() + durationMs;

    activeTests.set(testId, { status: "running", startedAt, samples: 0 });

    while (Date.now() < endAt) {
        try {
            const reading = await fetchRealtimeData();
            samples.push(reading);
            activeTests.set(testId, { status: "running", startedAt, samples: samples.length });
        } catch (err) {
            console.error(`Test ${testId} sample failed:`, err.message);
        }
        const remaining = endAt - Date.now();
        if (remaining <= 0) break;
        await new Promise((r) => setTimeout(r, Math.min(SAMPLE_INTERVAL_MS, remaining)));
    }

    const summary = {
        temperature: average(samples.map((s) => s.temperature)),
        tds: average(samples.map((s) => s.tds)),
        ph: average(samples.map((s) => s.ph)),
        turbidity: average(samples.map((s) => s.turbidity)),
        dissolved_oxygen: average(samples.map((s) => s.dissolved_oxygen)),
    };

    const verdict = scorePotability(summary);
    const finishedAt = new Date();

    const report = {
        testId,
        startedAt,
        finishedAt,
        durationMs,
        sampleCount: samples.length,
        samples,
        summary,
        verdict,
    };

    const db = getDB();
    const collectionName = process.env.MONGO_COLLECTION;
    if (!collectionName) throw new Error("MONGO_COLLECTION is not configured");
    await db.collection(collectionName).insertOne(report);

    activeTests.set(testId, { status: "complete", startedAt, finishedAt, samples: samples.length, summary, verdict });
    return report;
}

// POST /api/tests/start
// Body (optional): { duration: <ms> }
// Runs synchronously and returns the finished report. For long durations,
// switch to fire-and-forget + GET /api/tests/:id/status polling instead.
async function startTest(req, res) {
    try {
        const duration = Number(req.body?.duration) || DEFAULT_DURATION_MS;
        const testId = `test_${Date.now()}`;

        const report = await runTestSession(testId, duration);

        res.json({ success: true, ...report });
    } catch (err) {
        console.error("startTest failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

// GET /api/tests/:id/status — poll progress of a running/completed test
function getTestStatus(req, res) {
    const { id } = req.params;
    const status = activeTests.get(id);
    if (!status) {
        return res.status(404).json({ success: false, message: "Unknown test id" });
    }
    res.json({ success: true, testId: id, ...status });
}

export { startTest, getTestStatus };