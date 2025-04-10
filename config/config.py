import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"

# Create directories if they don't exist
(DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Database
DEFAULT_DB_PATH = DATA_DIR / "processed" / "ehr_database.db"

EHR_DATABASE_URL = os.getenv("EHR_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# AI Model Settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0"))

# Application Settings
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = APP_ENV == "development"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")