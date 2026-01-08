"""
Pydantic schemas for title document and encumbrance request/response models.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class EncumbranceActionResponse(BaseModel):
    """Schema for encumbrance action response"""
    id: int
    code: str
    label: str

    class Config:
        from_attributes = True


class EncumbranceStatusResponse(BaseModel):
    """Schema for encumbrance status response"""
    id: int
    code: str
    label: str

    class Config:
        from_attributes = True


class EncumbranceBase(BaseModel):
    """Base encumbrance information"""
    item_no: int
    document_number: Optional[str] = None
    encumbrance_date: Optional[date] = None
    description: Optional[str] = None
    signatories: Optional[str] = None
    circulation_notes: Optional[str] = None
    action_id: Optional[int] = None
    status_id: Optional[int] = None


class EncumbranceCreate(EncumbranceBase):
    """Schema for creating an encumbrance"""
    title_document_id: int


class EncumbranceUpdate(BaseModel):
    """Schema for updating an encumbrance"""
    item_no: Optional[int] = None
    document_number: Optional[str] = None
    encumbrance_date: Optional[date] = None
    description: Optional[str] = None
    signatories: Optional[str] = None
    circulation_notes: Optional[str] = None
    action_id: Optional[int] = None
    status_id: Optional[int] = None


class EncumbranceResponse(EncumbranceBase):
    """Schema for encumbrance response"""
    id: int
    title_document_id: int
    legal_document_id: Optional[int] = None
    action: Optional[EncumbranceActionResponse] = None
    status: Optional[EncumbranceStatusResponse] = None

    class Config:
        from_attributes = True


class TitleDocumentBase(BaseModel):
    """Base title document information"""
    file_path: str
    title_number: Optional[str] = None
    short_legal: Optional[str] = None
    legal_description: Optional[str] = None
    uploaded_by: Optional[str] = None


class TitleDocumentCreate(TitleDocumentBase):
    """Schema for creating a title document"""
    project_id: int


class TitleDocumentUpdate(BaseModel):
    """Schema for updating a title document"""
    title_number: Optional[str] = None
    short_legal: Optional[str] = None
    legal_description: Optional[str] = None


class TitleDocumentResponse(TitleDocumentBase):
    """Schema for title document response"""
    id: int
    project_id: int
    uploaded_at: datetime
    encumbrances: List[EncumbranceResponse] = []

    class Config:
        from_attributes = True
