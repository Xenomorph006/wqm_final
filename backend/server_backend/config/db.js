import { MongoClient } from "mongodb";
import dotenv from "dotenv";
dotenv.config();

const MONGO_URI = process.env.MONGO_URI;
const MONGO_DB = process.env.MONGO_DB;

let client;
let db;

async function connectDB() {
    if (db) return db;

    if (!MONGO_URI) throw new Error("MONGO_URI is not configured");
    if (!MONGO_DB) throw new Error("MONGO_DB is not configured");

    client = new MongoClient(MONGO_URI);
    await client.connect();
    db = client.db(MONGO_DB);

    console.log(`Connected to MongoDB database: ${MONGO_DB}`);
    return db;
}

function getDB() {
    if (!db) throw new Error("DB not initialized — call connectDB() first");
    return db;
}

export { connectDB, getDB };