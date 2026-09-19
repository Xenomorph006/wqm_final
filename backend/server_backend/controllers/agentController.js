import { getDB } from "../config/db.js";

const AGENT_COLLECTION = process.env.AGENT_COLLECTION || "agent_responses";

// GET /api/agentdata — most recent document the ML agent wrote to Mongo
async function getLatestAgentResponse(req, res) {
    try {
        const db = getDB();
        const [latest] = await db
            .collection(AGENT_COLLECTION)
            .find({})
            .sort({ _id: -1 })
            .limit(1)
            .toArray();

        if (!latest) {
            return res.status(404).json({ success: false, message: "No agent predictions yet" });
        }

        res.json({ success: true, data: latest });
    } catch (err) {
        console.error("getLatestAgentResponse failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

export { getLatestAgentResponse };