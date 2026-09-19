import { getDB } from "../config/db.js";
import { ObjectId } from "mongodb";

function collection() {
    const db = getDB();
    const collectionName = process.env.MONGO_COLLECTION;
    if (!collectionName) throw new Error("MONGO_COLLECTION is not configured");
    return db.collection(collectionName);
}

// GET /api/reports?limit=20
async function getReports(req, res) {
    try {
        const limit = Math.min(Number(req.query.limit) || 20, 100);
        const reports = await collection()
            .find({}, { projection: { samples: 0 } }) // omit raw samples in the list view
            .sort({ finishedAt: -1 })
            .limit(limit)
            .toArray();

        res.json({ success: true, count: reports.length, data: reports });
    } catch (err) {
        console.error("getReports failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

// GET /api/reports/:id — full detail including raw samples
async function getReportById(req, res) {
    try {
        const { id } = req.params;
        const query = ObjectId.isValid(id) ? { _id: new ObjectId(id) } : { testId: id };
        const report = await collection().findOne(query);

        if (!report) {
            return res.status(404).json({ success: false, message: "Report not found" });
        }
        res.json({ success: true, data: report });
    } catch (err) {
        console.error("getReportById failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

export { getReports, getReportById };