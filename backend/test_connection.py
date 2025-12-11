#!/usr/bin/env python
"""
Test MSSQL database connection.
Run from backend directory: python test_connection.py
"""
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_odbc_drivers():
    """Check available ODBC drivers."""
    print("Checking ODBC Drivers...")
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        print(f"  Available drivers: {len(drivers)}")
        for driver in drivers:
            if "ODBC" in driver or "SQL" in driver:
                print(f"    ✓ {driver}")
        
        if not any("ODBC Driver 17" in d for d in drivers):
            print("  ⚠ WARNING: ODBC Driver 17 not found!")
            print("    Download from: https://docs.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Error checking drivers: {e}")
        return False


def test_database_url():
    """Check DATABASE_URL is set."""
    print("\nChecking DATABASE_URL...")
    try:
        from app.config import SQLALCHEMY_DATABASE_URL
        
        # Mask password if present
        masked_url = SQLALCHEMY_DATABASE_URL
        if "password" in masked_url.lower() or "pwd" in masked_url.lower():
            # Simple masking
            import re
            masked_url = re.sub(r'://.*?@', '://***:***@', masked_url)
        
        print(f"  URL: {masked_url}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
        return False


def test_sqlalchemy_engine():
    """Test SQLAlchemy engine creation."""
    print("\nTesting SQLAlchemy Engine...")
    try:
        from app.database import engine
        print(f"  Engine dialect: {engine.dialect.name}")
        print(f"  Driver: {engine.dialect.driver}")
        return True
    except Exception as e:
        print(f"  ✗ Engine creation failed: {e}")
        return False


def test_connection():
    """Test actual database connection."""
    print("\nTesting Database Connection...")
    try:
        from sqlalchemy import text
        from app.database import engine
        
        with engine.connect() as conn:
            print(f"  ✓ Connection successful!")
            
            # Get SQL Server version
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()[0]
            print(f"  SQL Server Version: {version.split(',')[0]}")
            
            # Get database info
            result = conn.execute(text("SELECT DB_NAME() as DatabaseName"))
            db_name = result.fetchone()[0]
            print(f"  Current Database: {db_name}")
            
            return True
    except Exception as e:
        print(f"  ✗ Connection failed!")
        print(f"  Error: {str(e)}")
        print(f"\n  Troubleshooting:")
        print(f"    1. Check MSSQL Server is running: Get-Service -Name MSSQL*")
        print(f"    2. Verify DATABASE_URL in .env file")
        print(f"    3. Check ODBC Driver 17 is installed")
        print(f"    4. Review MSSQL_SETUP.md for configuration steps")
        return False


def test_create_tables():
    """Test creating tables."""
    print("\nTesting Table Creation...")
    try:
        from app.database import create_all_tables
        create_all_tables()
        print(f"  ✓ All tables created successfully!")
        
        # List tables
        from app.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"  Tables created ({len(tables)}):")
        for table in sorted(tables):
            print(f"    - {table}")
        
        return True
    except Exception as e:
        print(f"  ✗ Table creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("MSSQL Database Connection Test")
    print("=" * 60)
    
    results = {
        "ODBC Drivers": test_odbc_drivers(),
        "DATABASE_URL": test_database_url(),
        "SQLAlchemy Engine": test_sqlalchemy_engine(),
        "Database Connection": test_connection(),
        "Create Tables": test_create_tables(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ MSSQL connection is ready!")
        print("   Run: python run.py")
        return 0
    else:
        print("\n❌ Fix the errors above and try again")
        print("   See MSSQL_SETUP.md for troubleshooting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
