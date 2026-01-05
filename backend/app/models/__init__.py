"""
SQLAlchemy models for legal documents and document tasks.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

# Import all models so they're registered with Base.metadata
from app.models.lookups import (
    EncumbranceAction,
    EncumbranceStatus,
    DocumentTaskStatus,
    DocumentCategory,
    LegalDocumentTemplate,
)
from app.models.title import TitleDocument, Encumbrance
from app.models.project import SurveyorALS, Project


class LegalDocument(Base):
    """Generated or registered legal documents"""
    __tablename__ = "LegalDocument"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Project.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(100), nullable=True)
    registered_number = Column(String(100), nullable=True)
    registered_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="legal_documents")


class DocumentTask(Base):
    """Tasks for documents to be created (subdivisions, URW, agreements)"""
    __tablename__ = "DocumentTaskRow"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Project.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("DocumentCategory.id"), nullable=True)  # NULL = New Agreements
    item_no = Column(Integer, nullable=False)
    doc_desc = Column(String(500), nullable=True)
    copies_dept = Column(String(200), nullable=True)
    signatories = Column(String(500), nullable=True)
    condition_of_approval = Column(Text, nullable=True)
    circulation_notes = Column(Text, nullable=True)
    document_status_id = Column(Integer, ForeignKey("DocumentTaskStatus.id"), nullable=True)
    legal_document_template_id = Column(Integer, ForeignKey("LegalDocumentTemplate.id"), nullable=True)
    legal_document_id = Column(Integer, ForeignKey("LegalDocument.id"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="document_tasks")
    category = relationship("DocumentCategory")
    document_status = relationship("DocumentTaskStatus")
    legal_document_template = relationship("LegalDocumentTemplate")
    legal_document = relationship("LegalDocument")
