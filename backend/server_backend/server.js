import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { collectAndForward } from "./controllers/realtimeController.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// IP/host of the Flask backend on the Raspberry Pi that exposes GET /realtime
// e.g. http://192.168.1.50:5000  (set BACKEND_URL in your .env file)
const BACKEND_URL = process.env.BACKEND_URL;

// Agent server that collected readings get forwarded to (set DEST_URL in your .env file)
const DEST_URL = process.env.DEST_URL;

// How often to auto-collect from BACKEND_URL and forward to DEST_URL, in ms.
// Set POLL_INTERVAL_MS=0 in .env to disable automatic polling.
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS ?? 5000);

app.use(cors());
app.use(express.json()); // needed to parse req.body for POST /api/datasend

// Proxy endpoint for your existing frontend to poll. Keeps the Flask
// backend's IP out of client-side code and sidesteps CORS/network
// issues on the ESP32/Flask side.
app.get("/api/realtime", async (req, res) => {
    try {
        const response = await fetch(`${BACKEND_URL}`);
        const data = await response.json();

        if (!response.ok) {
            return res.status(response.status).json({
                status: "error",
                message: data?.message || `Backend responded ${response.status}`,
            });
        }
        res.json(data);
    } catch (err) {
        console.error("Failed to reach backend:", err.message);
        res.status(502).json({
            status: "error",
            message: "Could not reach the sensor backend",
        });
    }
});

// Forwards whatever JSON body it receives on to DEST_URL.
app.post("/api/datasend", async (req, res) => {
    try {
        if (!DEST_URL) {
            return res.status(500).json({
                success: false,
                message: "Destination URL is not configured"
            });
        }

        const response = await fetch(DEST_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(req.body)
        });

        const data = await response.json();

        return res.status(response.status).json({
            success: response.ok,
            message: "Data sent successfully",
            destination_response: data
        });
    } catch (error) {
        console.error("Data forwarding error:", error);
        return res.status(500).json({
            success: false,
            message: "Failed to send data",
            error: error.message
        });
    }
});

// Manually trigger one collect-from-backend -> forward-to-agent cycle.
app.post("/api/collect", async (req, res) => {
    try {
        const result = await collectAndForward();
        res.json({ success: true, ...result });
    } catch (err) {
        console.error("Collect-and-forward failed:", err.message);
        res.status(502).json({ success: false, message: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Realtime proxy server running at http://localhost:${PORT}`);
    console.log(`Forwarding to backend: ${BACKEND_URL}`);

    // Automatic background polling: collect from BACKEND_URL, push to DEST_URL.
    if (POLL_INTERVAL_MS > 0) {
        console.log(`Auto-collecting every ${POLL_INTERVAL_MS}ms -> ${DEST_URL}`);
        setInterval(() => {
            collectAndForward().catch((err) => {
                console.error("Auto collect-and-forward failed:", err.message);
            });
        }, POLL_INTERVAL_MS);
    }
});