"""
SQLAlchemy database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import SQLALCHEMY_DATABASE_URL, DEBUG

# Create engine
# For MSSQL: use pyodbc
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=DEBUG,  # Log SQL queries if DEBUG=True
    connect_args={
        "check_same_thread": False,
    } if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    pool_pre_ping=True,  # Validate connections before using them
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to inject database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Create all tables defined in models."""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
