import os
from pathlib import Path

from dotenv import load_dotenv


# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# Agent Backend
HOST = os.getenv("AGENT_HOST", "0.0.0.0")
PORT = int(os.getenv("AGENT_PORT", 8000))


# Project paths
PROJECT_ROOT = BASE_DIR.parent.parent.parent

ML_PATH = PROJECT_ROOT / "ml"


# Model settings
DEVICE = os.getenv("MODEL_DEVICE", "cpu")