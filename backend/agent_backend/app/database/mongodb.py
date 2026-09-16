# app/database/mongodb.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("MONGO_DB", "water_quality")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "agent_responses")

client = MongoClient(MONGO_URI)


db = client[MONGO_DB]
agent_responses = db[MONGO_COLLECTION]


def save_agent_response(response: dict):
    result = agent_responses.insert_one(response)
    return str(result.inserted_id)