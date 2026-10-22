import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-secret-key-change-me")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "project_kashi")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    JSON_SORT_KEYS = False
