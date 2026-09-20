// controllers/hardwareController.js
//
// Polls this server's own `/api/agentdata` route for a `hardware_control`
// command, dispatches that command to the correct ESP32 endpoint, then
// waits the required duration (interpreted as a fraction of one minute)
// plus a fixed buffer before polling again.
//
// Timing convention:
//   time = 0.333  -> 1/3 of a minute  -> 20 seconds
//   time = 0.0333 -> 1/30 of a minute -> ~2 seconds
//   actualWaitMs = time * 60 * 1000
//
// Message -> ESP32 endpoint mapping:
//   "Start Cooling System" -> /cooling
//   "release base"         -> /base
//   "release acid"         -> /acid

const ESP_BASE_URL = process.env.ESP_BASE_URL || "https://192.168.1.5";
const EXTRA_DELAY_MS = Number(process.env.HW_EXTRA_DELAY_MS ?? 2000);
const POLL_RETRY_DELAY_MS = Number(process.env.HW_RETRY_DELAY_MS ?? 5000);
const VERIFY_TLS = process.env.HW_VERIFY_TLS === "true"; // default false: self-signed ESP32 certs

const ESP_ENDPOINTS = {
    "start cooling system": `${ESP_BASE_URL}/cooling`,
    "release base": `${ESP_BASE_URL}/base`,
    "release acid": `${ESP_BASE_URL}/acid`,
};

// Node's fetch respects NODE_TLS_REJECT_UNAUTHORIZED for self-signed certs.
// Only disable verification when explicitly opted out via HW_VERIFY_TLS.
if (!VERIFY_TLS) {
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
}

let state = {
    running: false,
    lastPollAt: null,
    lastMessage: null,
    lastDispatchedEndpoint: null,
    lastError: null,
    cyclesCompleted: 0,
};

function log(...args) {
    console.log(new Date().toISOString(), "[hardware]", ...args);
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchAgentData(agentDataUrl) {
    const response = await fetch(agentDataUrl);
    if (!response.ok) {
        throw new Error(`agentdata responded ${response.status}`);
    }
    return response.json();
}

async function dispatchToEsp(message, duration) {
    const key = String(message).trim().toLowerCase();
    const endpoint = ESP_ENDPOINTS[key];

    if (!endpoint) {
        log(`No ESP endpoint mapped for message: "${message}" — skipping.`);
        return false;
    }

    const payload = { message, time: duration };
    log(`Dispatching "${message}" -> ${endpoint} (payload=${JSON.stringify(payload)})`);

    const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const text = await response.text().catch(() => "");
    log(`ESP responded ${response.status}: ${text.slice(0, 200)}`);
    state.lastDispatchedEndpoint = endpoint;
    return true;
}

async function pollCycle(agentDataUrl) {
    try {
        const data = await fetchAgentData(agentDataUrl);
        const result = data.data || data; // handle wrapped/unwrapped shapes

        state.lastPollAt = new Date().toISOString();
        state.lastError = null;

        const hw = result.hardware_control;
        if (!hw) {
            log("No hardware_control payload in this cycle. Retrying shortly.");
            await sleep(POLL_RETRY_DELAY_MS);
            return;
        }

        const { message, time: duration = 0 } = hw;
        state.lastMessage = message;

        if (!message) {
            log("hardware_control had no message. Retrying shortly.");
            await sleep(POLL_RETRY_DELAY_MS);
            return;
        }

        await dispatchToEsp(message, duration);

        const waitMs = duration * 60 * 1000 + EXTRA_DELAY_MS;
        log(
            `Waiting ${(waitMs / 1000).toFixed(2)}s ` +
                `(${duration} min x 60 + ${EXTRA_DELAY_MS / 1000}s buffer) before next poll.`
        );
        state.cyclesCompleted += 1;
        await sleep(waitMs);
    } catch (err) {
        state.lastError = err.message;
        log(`Error during poll cycle: ${err.message}. Retrying in ${POLL_RETRY_DELAY_MS / 1000}s.`);
        await sleep(POLL_RETRY_DELAY_MS);
    }
}

/**
 * Starts the polling/dispatch loop. Call once from server.js after app.listen.
 * @param {number} port - the port this Express server is listening on
 */
export function startHardwareLoop(port) {
    if (state.running) {
        log("startHardwareLoop called again but loop is already running — ignoring.");
        return;
    }
    state.running = true;

    const agentDataUrl = process.env.HW_AGENT_URL || `http://localhost:${port}/api/agentdata`;
    log(`Starting hardware controller loop. Polling ${agentDataUrl}`);

    (async function runForever() {
        // eslint-disable-next-line no-constant-condition
        while (true) {
            await pollCycle(agentDataUrl);
        }
    })();
}

/** Returns a snapshot of the controller's current status (for a /status route, etc). */
export function getHardwareStatus() {
    return { ...state };
}