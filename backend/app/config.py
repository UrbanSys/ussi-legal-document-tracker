"""
Configuration settings for the FastAPI application.
Handles environment variables and MSSQL connection settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration - SQL Server with username/password from .env
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

# Validate required environment variables
if not all([DB_USERNAME, DB_PASSWORD, DB_SERVER, DB_NAME]):
    raise ValueError(
        "Missing database configuration. Please set these in backend/.env:\n"
        "  DB_USERNAME=your_username\n"
        "  DB_PASSWORD=your_password\n"
        "  DB_SERVER=your_server\n"
        "  DB_NAME=your_database"
    )

DATABASE_URL = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Application Settings
APP_NAME = "USSI Legal Document Tracker API"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"

# File Upload Settings
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads/")
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_DOCX_EXTENSIONS = {".docx", ".doc"}

# CORS Settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
