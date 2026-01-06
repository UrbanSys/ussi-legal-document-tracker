"""
SQLAlchemy models - imports all models so they're registered with Base.metadata.
"""
from app.models.lookups import (
    EncumbranceAction,
    EncumbranceStatus,
    DocumentTaskStatus,
    DocumentCategory,
    LegalDocumentTemplate,
)
from app.models.title import TitleDocument, Encumbrance
from app.models.project import SurveyorALS, Project
from app.models.document import LegalDocument, DocumentTask

__all__ = [
    # Lookups
    "EncumbranceAction",
    "EncumbranceStatus",
    "DocumentTaskStatus",
    "DocumentCategory",
    "LegalDocumentTemplate",
    # Title
    "TitleDocument",
    "Encumbrance",
    # Project
    "SurveyorALS",
    "Project",
    # Document
    "LegalDocument",
    "DocumentTask",
]
