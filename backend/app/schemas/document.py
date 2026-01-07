"""
Pydantic schemas for document task and legal document request/response models.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class DocumentCategoryResponse(BaseModel):
    """Schema for document category response"""
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class DocumentTaskStatusResponse(BaseModel):
    """Schema for document task status response"""
    id: int
    code: str
    label: str

    class Config:
        from_attributes = True


class LegalDocumentTemplateResponse(BaseModel):
    """Schema for legal document template response"""
    id: int
    file_path: str
    document_type: str
    municipality: Optional[str] = None
    version: Optional[str] = None

    class Config:
        from_attributes = True


class LegalDocumentBase(BaseModel):
    """Base legal document information"""
    file_path: str
    document_type: Optional[str] = None
    registered_number: Optional[str] = None
    registered_date: Optional[date] = None
    notes: Optional[str] = None


class LegalDocumentCreate(LegalDocumentBase):
    """Schema for creating a legal document"""
    project_id: int


class LegalDocumentResponse(LegalDocumentBase):
    """Schema for legal document response"""
    id: int
    project_id: int

    class Config:
        from_attributes = True


class DocumentTaskBase(BaseModel):
    """Base document task information"""
    item_no: int
    doc_desc: Optional[str] = None
    copies_dept: Optional[str] = None
    signatories: Optional[str] = None
    condition_of_approval: Optional[str] = None
    circulation_notes: Optional[str] = None
    category_id: Optional[int] = None  # NULL = New Agreements
    document_status_id: Optional[int] = None
    legal_document_template_id: Optional[int] = None
    legal_document_id: Optional[int] = None


class DocumentTaskCreate(DocumentTaskBase):
    """Schema for creating a document task"""
    project_id: int


class DocumentTaskUpdate(BaseModel):
    """Schema for updating a document task"""
    item_no: Optional[int] = None
    doc_desc: Optional[str] = None
    copies_dept: Optional[str] = None
    signatories: Optional[str] = None
    condition_of_approval: Optional[str] = None
    circulation_notes: Optional[str] = None
    category_id: Optional[int] = None
    document_status_id: Optional[int] = None
    legal_document_template_id: Optional[int] = None
    legal_document_id: Optional[int] = None

class DocumentTaskResponse(DocumentTaskBase):
    """Schema for document task response"""
    id: int
    project_id: int
    category: Optional[DocumentCategoryResponse] = None
    document_status: Optional[DocumentTaskStatusResponse] = None
    legal_document_template: Optional[LegalDocumentTemplateResponse] = None
    legal_document: Optional[LegalDocumentResponse] = None

    class Config:
        from_attributes = True


# Pydantic schema
class DocumentCategoryCreate(BaseModel):
    code: str
    name: str

class DocumentCategoryResponse(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True