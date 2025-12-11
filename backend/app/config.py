"""
Configuration settings for the FastAPI application.
Handles environment variables and MSSQL connection settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# Check if DATABASE_URL is directly set in .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Build from individual components if DATABASE_URL not set
    db_user = os.getenv("username")
    db_password = os.getenv("password")
    db_server = os.getenv("server")
    db_name = os.getenv("database")
    
    if db_user and db_password and db_server and db_name:
        # Use SQL Server authentication with username/password
        DATABASE_URL = f"mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
    else:
        # Fallback to Windows authentication
        DATABASE_URL = "mssql+pyodbc:///?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=USLDEV\TESTING;Database=LegalDocumentTracker;Trusted_Connection=yes"

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
    "http://localhost:8000",
    "http://127.0.0.1:3000",
]

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
