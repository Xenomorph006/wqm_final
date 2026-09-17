# app/database/mongodb.py

import os
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

# Get project root directory (agent_backend)
BASE_DIR = Path(__file__).resolve().parents[2]

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Read environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "water_quality")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "agent_responses")

# Debug (remove after testing)
print(f"MONGO_URI: {MONGO_URI}")
print(f"MONGO_DB: {MONGO_DB}")
print(f"MONGO_COLLECTION: {MONGO_COLLECTION}")

# Validate MONGO_URI
if not MONGO_URI:
    raise ValueError(
        f"MONGO_URI not found in {BASE_DIR / '.env'}"
    )

# MongoDB connection
client = MongoClient(MONGO_URI)

db = client[MONGO_DB]
agent_responses = db[MONGO_COLLECTION]


def save_agent_response(response: dict):
    document = response.copy()

    result = agent_responses.insert_one(document)

    return str(result.inserted_id)