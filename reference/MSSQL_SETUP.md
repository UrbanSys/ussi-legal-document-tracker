# MSSQL Database Setup Guide

## Prerequisites Checklist

- [ ] MSSQL Server installed (Express, Standard, or Developer Edition)
- [ ] SQL Server Management Studio (SSMS) installed
- [ ] ODBC Driver 17 for SQL Server installed
- [ ] Network connectivity to MSSQL server

---

## Step 1: Check MSSQL Installation

### Windows Command Line
```powershell
# Check if MSSQL service is running
Get-Service -Name MSSQL* | Select-Object Name, Status

# Should show something like:
# Name              Status
# MSSQLSERVER       Running
```

### SQL Server Management Studio
1. Open SSMS
2. Connect to `localhost` or `.\SQLEXPRESS` (for Express Edition)
3. You should connect successfully

---

## Step 2: Install ODBC Driver 17

### Windows
1. Download from Microsoft:
   https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

2. Choose: **ODBC Driver 17 for SQL Server**

3. Run installer and complete setup

### Verify Installation
```powershell
# In PowerShell, check installed drivers
Get-OdbcDriver | Select-Object Name | Find-Object "ODBC Driver 17 for SQL Server"

# Or test in Python
python -c "import pyodbc; print(pyodbc.drivers())"
# Should list: 'ODBC Driver 17 for SQL Server'
```

---

## Step 3: Create Database

### Option A: Using SSMS (GUI)
1. Open SQL Server Management Studio
2. Connect to your server
3. Right-click **Databases** → **New Database**
4. Name: `ussi_legal_tracker`
5. Click OK

### Option B: Using SQL Command
```sql
CREATE DATABASE ussi_legal_tracker;
GO
```

### Option C: Using PowerShell
```powershell
sqlcmd -S localhost -Q "CREATE DATABASE ussi_legal_tracker;"
```

---

## Step 4: Configure MSSQL Authentication

### Windows Authentication (Recommended)
If your system and MSSQL server are on the same Windows domain:

```env
# .env file
DATABASE_URL=mssql+pyodbc://?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=ussi_legal_tracker;Trusted_Connection=yes
```

**Pros:** Secure, no password storage needed
**Cons:** Requires Windows login

### SQL Server Authentication
If using username/password:

1. First, enable SQL Server Authentication in SSMS:
   - Right-click Server → Properties
   - Security → Server Authentication: Select "SQL Server and Windows Authentication mode"
   - Restart MSSQL service

2. Create a login (in SSMS or SQL):
```sql
CREATE LOGIN ursi_user WITH PASSWORD = 'YourSecurePassword123!';
CREATE USER ursi_user FOR LOGIN ursi_user;
ALTER ROLE db_owner ADD MEMBER ursi_user;
```

3. Update `.env`:
```env
DATABASE_URL=mssql+pyodbc://ursi_user:YourSecurePassword123!@localhost/ussi_legal_tracker?driver=ODBC+Driver+17+for+SQL+Server
```

---

## Step 5: Update .env File

### For Windows Authentication (Recommended):
```env
# Database Configuration
DATABASE_URL=mssql+pyodbc://?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=ussi_legal_tracker;Trusted_Connection=yes

# Server Configuration
HOST=127.0.0.1
PORT=8000
RELOAD=True
DEBUG=False

# File Upload Configuration
UPLOAD_DIRECTORY=uploads/

# Logging
LOG_LEVEL=info
```

### For SQL Server Authentication:
```env
# Database Configuration
DATABASE_URL=mssql+pyodbc://ursi_user:YourPassword@localhost/ussi_legal_tracker?driver=ODBC+Driver+17+for+SQL+Server

# Server Configuration
HOST=127.0.0.1
PORT=8000
RELOAD=True
DEBUG=False

# File Upload Configuration
UPLOAD_DIRECTORY=uploads/

# Logging
LOG_LEVEL=info
```

### For Remote Server:
```env
# Replace 'localhost' with your server name
DATABASE_URL=mssql+pyodbc://?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER_NAME;Database=ussi_legal_tracker;Trusted_Connection=yes
```

---

## Step 6: Initialize Database Schema

### Option A: Using SQL Script
```powershell
# From backend directory
sqlcmd -S localhost -d ussi_legal_tracker -i database_schema.sql
```

### Option B: Python Auto-Creates on Startup
The FastAPI app automatically creates tables when you start the server:
```bash
python run.py
```

The first startup will initialize all tables from SQLAlchemy models.

---

## Step 7: Verify Connection

### Test Script
Create `test_connection.py` in backend folder:

```python
from app.config import SQLALCHEMY_DATABASE_URL
from app.database import engine

print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

try:
    with engine.connect() as conn:
        print("✓ Connection successful!")
        result = conn.execute("SELECT @@VERSION;")
        print(result.fetchone())
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

Run it:
```bash
python backend/test_connection.py
```

---

## Common Issues & Fixes

### Issue: "Named instance not found"
```
ConnectionError: ('28000', '[28000] [Microsoft][ODBC Driver 17 for SQL Server]...')
```

**Solution:**
- Use SSMS to connect and find your exact server name
- Or try: `localhost`, `.\SQLEXPRESS`, `127.0.0.1\SQLEXPRESS`

### Issue: "ODBC Driver 17 not found"
```
pyodbc.Error: ('HY000', '[HY000] [unixODBC]...')
```

**Solution:**
- Reinstall ODBC Driver 17
- Verify with: `python -c "import pyodbc; print(pyodbc.drivers())"`

### Issue: "Login failed for user"
```
DatabaseError: ('28000', '[28000] [Microsoft][ODBC Driver 17 for SQL Server]...')
```

**Solution:**
- Check username/password in DATABASE_URL
- Verify user has database access: `ALTER ROLE db_owner ADD MEMBER username;`
- Check MSSQL Authentication mode (should be "SQL Server and Windows Authentication")

### Issue: "Database does not exist"
```
DatabaseError: ('42P02', '...')
```

**Solution:**
```sql
-- Create it in SSMS or run:
CREATE DATABASE ussi_legal_tracker;
```

### Issue: "Trusted_Connection not working"
```
DatabaseError: ('28000', '[28000] [Microsoft][ODBC Driver 17 for SQL Server]...')
```

**Solution:**
- Ensure your Windows user has MSSQL login privileges
- Use SQL Server Authentication instead (with username/password)
- Or grant Windows user access:

```sql
-- In SSMS, as admin
CREATE LOGIN [DOMAIN\USERNAME] FROM WINDOWS;
CREATE USER [DOMAIN\USERNAME] FOR LOGIN [DOMAIN\USERNAME];
ALTER ROLE db_owner ADD MEMBER [DOMAIN\USERNAME];
```

---

## Quick Setup Summary

```bash
# 1. Open PowerShell as Admin
# 2. Check MSSQL is running
Get-Service -Name MSSQL* | Select-Object Name, Status

# 3. Create database
sqlcmd -S localhost -Q "CREATE DATABASE ussi_legal_tracker;"

# 4. Update .env with connection string

# 5. Test connection
python backend/test_connection.py

# 6. Start backend server
cd backend
python run.py

# 7. Access API
# http://localhost:8000/docs
```

---

## Production Deployment Notes

For production, consider:

1. **Use SQL Server Authentication** (not Windows Trust)
2. **Encrypt connection strings**:
   ```
   Encrypt=yes;TrustServerCertificate=no;
   ```
3. **Use connection pooling**:
   ```python
   engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
   ```
4. **Set proper database permissions** (don't use db_owner)
5. **Use environment variables** for sensitive data (not in .env)

---

## Next Steps

Once connected:
1. Run `python backend/test_setup.py` to verify all models
2. Start server: `python backend/run.py`
3. Access docs: http://localhost:8000/docs
4. Test endpoints in Swagger UI
