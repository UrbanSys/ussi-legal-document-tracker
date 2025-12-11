"""
SQLAlchemy models for title documents and encumbrances.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TitleDocument(Base):
    """PDF title certificate documents uploaded for a project"""
    __tablename__ = "TitleDocument"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Project.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_by = Column(String(200), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="title_documents")
    encumbrances = relationship("Encumbrance", back_populates="title_document", cascade="all, delete-orphan")


class Encumbrance(Base):
    """Existing encumbrances extracted from title documents"""
    __tablename__ = "Encumbrance"

    id = Column(Integer, primary_key=True, index=True)
    title_document_id = Column(Integer, ForeignKey("TitleDocument.id"), nullable=False)
    item_no = Column(Integer, nullable=False)
    document_number = Column(String(100), nullable=True)
    encumbrance_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    signatories = Column(String(500), nullable=True)
    action_id = Column(Integer, ForeignKey("EncumbranceAction.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("EncumbranceStatus.id"), nullable=True)
    circulation_notes = Column(Text, nullable=True)
    legal_document_id = Column(Integer, ForeignKey("LegalDocument.id"), nullable=True)

    # Relationships
    title_document = relationship("TitleDocument", back_populates="encumbrances")
    action = relationship("EncumbranceAction")
    status = relationship("EncumbranceStatus")
    legal_document = relationship("LegalDocument")
