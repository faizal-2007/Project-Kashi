import os
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "project-kashi-dev-key-academic-2026")
    
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "project_kashi")
    
    # Pool settings
    DB_POOL_NAME = "kashi_pool"
    DB_POOL_SIZE = 5

class TestConfig(Config):
    TESTING = True
    DB_NAME = os.getenv("TEST_DB_NAME", "project_kashi_test")
