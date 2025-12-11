#!/usr/bin/env python
"""
Quick test script to verify backend setup.
Run from project root: python backend/test_setup.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    try:
        from app.config import APP_NAME, SQLALCHEMY_DATABASE_URL
        print(f"  ✓ Config loaded: {APP_NAME}")
        print(f"  ✓ Database URL configured")
        
        from app.database import engine, Base, SessionLocal
        print(f"  ✓ Database engine created")
        
        from app.models.project import Project, SurveyorALS
        print(f"  ✓ Project models loaded")
        
        from app.models.title import TitleDocument, Encumbrance
        print(f"  ✓ Title models loaded")
        
        from app.models import DocumentTask, LegalDocument
        print(f"  ✓ Document models loaded")
        
        from app.schemas.project import ProjectResponse
        print(f"  ✓ Schemas loaded")
        
        from app.services.pdf_processor import PDFProcessorService
        print(f"  ✓ Services loaded")
        
        from app.routes import projects, titles, documents
        print(f"  ✓ Routes loaded")
        
        from app.main import app
        print(f"  ✓ FastAPI app loaded")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_database():
    """Test database connection."""
    print("\nTesting database connection...")
    try:
        from app.database import engine
        with engine.connect() as conn:
            print(f"  ✓ Database connection successful")
            return True
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        print(f"    Make sure MSSQL is running and .env is configured correctly")
        return False


def test_models():
    """Test that models are properly defined."""
    print("\nTesting models...")
    try:
        from app.database import Base
        model_count = len(Base.registry.mappers)
        print(f"  ✓ {model_count} models registered")
        
        # List all models
        from app.models.project import Project, SurveyorALS
        from app.models.title import TitleDocument, Encumbrance
        from app.models import DocumentTask, LegalDocument
        from app.models.lookups import (
            EncumbranceAction, EncumbranceStatus, DocumentTaskStatus, DocumentCategory
        )
        
        models = [
            Project, SurveyorALS, TitleDocument, Encumbrance,
            DocumentTask, LegalDocument,
            EncumbranceAction, EncumbranceStatus, DocumentTaskStatus, DocumentCategory
        ]
        
        for model in models:
            print(f"    - {model.__name__}")
        
        return True
    except Exception as e:
        print(f"  ✗ Model registration failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("USSI Backend Setup Verification")
    print("=" * 50)
    
    results = {
        "Imports": test_imports(),
        "Models": test_models(),
        "Database": test_database(),
    }
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ Backend is ready! Run: python run.py")
        return 0
    else:
        print("\n❌ Fix the errors above and try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
