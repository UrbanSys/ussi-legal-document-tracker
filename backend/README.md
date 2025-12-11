# USSI Legal Document Tracker - Backend Setup

## Quick Start

### 1. Prerequisites
- Python 3.10+
- MSSQL Server (with ODBC Driver 17 installed)
- pip or conda

### 2. Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create .env file from template
copy .env.example .env

# Update .env with your database connection details
# For Windows Authentication (recommended):
# DATABASE_URL=mssql+pyodbc://?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=ussi_legal_tracker;Trusted_Connection=yes
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Using conda (if in conda environment)
conda install -r requirements.txt
```

### 4. Initialize Database

The database tables will be created automatically on first server startup. Ensure your MSSQL database exists:

```sql
-- Run this in SQL Server Management Studio
CREATE DATABASE ussi_legal_tracker;
```

### 5. Run the Server

```bash
# From the backend directory
python run.py

# Or use uvicorn directly
uvicorn app.main:app --reload

# Access the API
# - Interactive API docs: http://localhost:8000/docs
# - Alternative API docs: http://localhost:8000/redoc
# - Health check: http://localhost:8000/health
```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration & settings
│   ├── database.py                # SQLAlchemy setup
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py           # DocumentTask & LegalDocument
│   │   ├── lookups.py            # Reference tables
│   │   ├── project.py            # Project & Surveyor
│   │   └── title.py              # TitleDocument & Encumbrance
│   │
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── title.py
│   │   └── document.py
│   │
│   ├── routes/                    # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── projects.py            # /api/projects/*
│   │   ├── titles.py              # /api/titles/*
│   │   └── documents.py           # /api/documents/*
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── pdf_processor.py       # PDF extraction
│   │   └── doc_generator.py       # Document generation
│   │
│   └── utils/                     # Utilities
│       └── __init__.py
│
├── run.py                         # Entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── database_schema.sql            # MSSQL schema
```

---

## API Endpoints

### Health & Info
- `GET /` — Welcome message
- `GET /health` — Health check

### Projects
- `GET /api/projects` — List projects
- `GET /api/projects/{id}` — Get project details
- `POST /api/projects` — Create project
- `PUT /api/projects/{id}` — Update project
- `DELETE /api/projects/{id}` — Delete project

### Surveyors
- `GET /api/projects/surveyors` — List surveyors
- `GET /api/projects/surveyors/{id}` — Get surveyor
- `POST /api/projects/surveyors` — Create surveyor

### Title Documents
- `GET /api/titles` — List title documents (by project)
- `GET /api/titles/{id}` — Get title document with encumbrances
- `POST /api/titles` — Upload title PDF (auto-extracts encumbrances)

### Encumbrances
- `GET /api/titles/{title_id}/encumbrances` — List encumbrances
- `GET /api/titles/encumbrances/{id}` — Get encumbrance
- `PUT /api/titles/encumbrances/{id}` — Update encumbrance

### Documents (WIP)
- `GET /api/documents/categories` — List document categories
- `GET /api/documents/statuses` — List document statuses
- `POST /api/documents/generate` — Generate document from template

---

## Database Setup

### Create Database
```sql
CREATE DATABASE ussi_legal_tracker;
GO
USE ussi_legal_tracker;
```

### Run Schema
Execute `database_schema.sql` to create all tables and seed lookup data:
```bash
sqlcmd -S SERVER_NAME -d ussi_legal_tracker -i database_schema.sql
```

Or import through SQL Server Management Studio (SSMS).

---

## Configuration

Edit `.env` to customize:
- `DATABASE_URL` — MSSQL connection string
- `HOST` — Server host (default: 127.0.0.1)
- `PORT` — Server port (default: 8000)
- `RELOAD` — Auto-reload on code changes (default: True)
- `DEBUG` — Debug mode (default: False)
- `UPLOAD_DIRECTORY` — Where to store uploaded PDFs

---

## Common Issues

### MSSQL Connection Issues
```
"pyodbc.DatabaseError: ('28000', '[28000]...')"
```
**Solution:** Ensure ODBC Driver 17 is installed:
```bash
# Windows: Download from Microsoft
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Port Already in Use
```bash
# Use a different port
python run.py --port 8001
# Or update PORT in .env
```

### Database Not Found
Ensure the database exists and connection string is correct. Test with:
```bash
python -c "from app.database import engine; print(engine.url)"
```

---

## Development

### Format Code
```bash
pip install black
black app/
```

### Lint
```bash
pip install flake8
flake8 app/
```

### Type Checking
```bash
pip install mypy
mypy app/
```

---

## Next Steps

1. ✅ **Backend Framework** — FastAPI + SQLAlchemy
2. ✅ **Database Models** — All tables mapped
3. ✅ **API Routes** — Projects, Titles, Documents
4. ✅ **PDF Processing** — Extract encumbrances
5. ✅ **Document Generation** — From templates
6. 🔲 **Frontend** — React/Vue integration
7. 🔲 **Authentication** — JWT tokens
8. 🔲 **Testing** — Unit & integration tests

---

## Support

For issues or questions, check:
- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy docs: https://docs.sqlalchemy.org
- PyODBC docs: https://github.com/mkleehammer/pyodbc/wiki
