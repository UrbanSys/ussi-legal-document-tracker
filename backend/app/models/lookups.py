"""
SQLAlchemy models for lookup tables.
These contain static reference data used throughout the application.
"""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class EncumbranceAction(Base):
    """Possible actions for an encumbrance (Discharge, Consent, etc.)"""
    __tablename__ = "EncumbranceAction"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)


class EncumbranceStatus(Base):
    """Status of an encumbrance (Prepared, Complete, etc.)"""
    __tablename__ = "EncumbranceStatus"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)


class DocumentTaskStatus(Base):
    """Status of a document task (Not Started, Prepared, Completed)"""
    __tablename__ = "DocumentTaskStatus"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(200), nullable=False)


class DocumentCategory(Base):
    """Category of documents (Subdivision, URW, New Agreement)"""
    __tablename__ = "DocumentCategory"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)


class LegalDocumentTemplate(Base):
    """Template files for generating legal documents"""
    __tablename__ = "LegalDocumentTemplate"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(100), nullable=False)
    municipality = Column(String(200), nullable=True)
    version = Column(String(50), nullable=True)
