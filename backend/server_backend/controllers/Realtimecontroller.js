// Pulls the latest reading from the Raspberry Pi / Flask backend
// (BACKEND_URL) and forwards it to the agent server (DEST_URL).
import dotenv from "dotenv";

dotenv.config();

const BACKEND_URL = process.env.BACKEND_URL;
const DEST_URL = process.env.DEST_URL;

/**
 * GET {BACKEND_URL}
 * Throws if the request fails or the backend responds with a non-2xx status.
 */
async function fetchRealtimeData() {
    if (!BACKEND_URL) {
        throw new Error("BACKEND_URL is not configured");
    }

    const response = await fetch(`${BACKEND_URL}`);
    const json = await response.json();

    if (!response.ok) {
        throw new Error(json?.message || `Backend responded ${response.status}`);
    }

    // Flask returns { status: "success", data: { ...sensor fields... } } —
    // the actual reading is nested under `data`, not top-level.
    const reading = json.data ?? json;

    const sendableData = {
        temperature: reading.temperature,
        tds: reading.tds,
        ph: reading.ph,
        turbidity: reading.turbidity,
        dissolved_oxygen: reading.dissolved_oxygen,
    };
    console.log("Fetched data from backend:", sendableData);

    return sendableData;
}

/**
 * POST the given payload to {DEST_URL} (the agent server).
 * Throws if the request fails or the destination responds with a non-2xx status.
 */
async function forwardToAgent(payload) {
    if (!DEST_URL) {
        throw new Error("DEST_URL is not configured");
    }

    const response = await fetch(DEST_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        throw new Error(`Agent server responded ${response.status}`);
    }

    return data;
}

/**
 * One full cycle: collect from the backend, forward to the agent server.
 * Returns { source, forwarded } on success.
 */
async function collectAndForward() {
    const data = await fetchRealtimeData();
    const forwarded = await forwardToAgent(data);
    console.log("Collected reading and forwarded it to agent server:", data);
    return { source: data, forwarded };
}

export { fetchRealtimeData, forwardToAgent, collectAndForward };