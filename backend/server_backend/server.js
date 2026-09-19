import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { collectAndForward, getLatestReading } from "./controllers/Realtimecontroller.js";
import { startTest } from "./controllers/testController.js";
import { getReports, getReportById, createReport } from "./controllers/reportController.js";
import { getLatestAgentResponse } from "./controllers/agentController.js";
import { connectDB } from "./config/db.js";
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;
const BACKEND_URL = process.env.BACKEND_URL;
const DEST_URL = process.env.DEST_URL;
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS ?? 5000);

app.use(cors());
app.use(express.json());

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
        res.status(502).json({ status: "error", message: "Could not reach the sensor backend" });
    }
});

app.post("/api/datasend", async (req, res) => {
    try {
        if (!DEST_URL) {
            return res.status(500).json({ success: false, message: "Destination URL is not configured" });
        }
        const response = await fetch(DEST_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(req.body),
        });
        const data = await response.json();
        return res.status(response.status).json({
            success: response.ok,
            message: "Data sent successfully",
            destination_response: data,
        });
    } catch (error) {
        console.error("Data forwarding error:", error);
        return res.status(500).json({ success: false, message: "Failed to send data", error: error.message });
    }
});

app.get("/api/data", (req, res) => {
    const latest = getLatestReading();
    if (!latest) {
        return res.status(404).json({ success: false, message: "No data collected yet" });
    }
    res.json({ success: true, data: latest });
});

// Latest ML agent prediction (pH/turbidity/temperature/DO/TDS + per-parameter confidence)
app.get("/api/agentdata", getLatestAgentResponse);

app.post("/api/collect", async (req, res) => {
    try {
        const result = await collectAndForward();
        res.json({ success: true, ...result });
    } catch (err) {
        console.error("Collect-and-forward failed:", err.message);
        res.status(502).json({ success: false, message: err.message });
    }
});

app.post("/api/tests/start", startTest);

app.get("/api/reports", getReports);
app.get("/api/reports/:id", getReportById);
app.post("/api/reports", createReport);

async function start() {
    try {
        await connectDB();
    } catch (err) {
        console.error("Failed to connect to MongoDB:", err.message);
        process.exit(1);
    }

    app.listen(PORT, () => {
        console.log(`Realtime proxy server running at http://localhost:${PORT}`);
        console.log(`Forwarding to backend: ${BACKEND_URL}`);
        if (POLL_INTERVAL_MS > 0) {
            console.log(`Auto-collecting every ${POLL_INTERVAL_MS}ms -> ${DEST_URL}`);
            setInterval(() => {
                collectAndForward().catch((err) => {
                    console.error("Auto collect-and-forward failed:", err.message);
                });
            }, POLL_INTERVAL_MS);
        }
    });
}

start();