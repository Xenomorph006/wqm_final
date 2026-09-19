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
            .find({}, { projection: { samples: 0 } })
            .sort({ savedAt: -1 })
            .limit(limit)
            .toArray();

        res.json({ success: true, count: reports.length, data: reports });
    } catch (err) {
        console.error("getReports failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

// GET /api/reports/:id
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

// POST /api/reports — persists the report Prediction.jsx computed client-side
async function createReport(req, res) {
    try {
        const report = req.body;
        if (!report || typeof report !== "object" || Array.isArray(report)) {
            return res.status(400).json({ success: false, message: "Report body is required" });
        }

        const doc = { ...report, savedAt: new Date() };
        delete doc._id; // never trust a client-supplied _id

        const result = await collection().insertOne(doc);
        res.status(201).json({ success: true, id: result.insertedId, data: doc });
    } catch (err) {
        console.error("createReport failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

// DELETE /api/reports/:id — matches either Mongo's _id or the client-generated testId/id
async function deleteReport(req, res) {
    try {
        const { id } = req.params;
        const query = ObjectId.isValid(id) ? { _id: new ObjectId(id) } : { testId: id };
        const result = await collection().deleteOne(query);

        if (result.deletedCount === 0) {
            return res.status(404).json({ success: false, message: "Report not found" });
        }
        res.json({ success: true, id });
    } catch (err) {
        console.error("deleteReport failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

// DELETE /api/reports — wipes every saved report from this collection
async function deleteAllReports(req, res) {
    try {
        const result = await collection().deleteMany({});
        res.json({ success: true, deletedCount: result.deletedCount });
    } catch (err) {
        console.error("deleteAllReports failed:", err.message);
        res.status(500).json({ success: false, message: err.message });
    }
}

export { getReports, getReportById, createReport, deleteReport, deleteAllReports };