"""
Pydantic schemas for project-related request/response models.
"""
from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.title import TitleDocumentResponse
    from app.schemas.document import DocumentTaskResponse


class SurveyorBase(BaseModel):
    """Base surveyor information"""
    name: str
    ftp_number: Optional[str] = None
    city: Optional[str] = None


class SurveyorCreate(SurveyorBase):
    """Schema for creating a surveyor"""
    pass


class SurveyorResponse(SurveyorBase):
    """Schema for surveyor response"""
    id: int

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project information"""
    proj_num: str
    name: str
    municipality: Optional[str] = None
    surveyor_id: Optional[int] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = None
    municipality: Optional[str] = None
    surveyor_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    surveyor: Optional[SurveyorResponse] = None

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with related data"""
    title_documents: List["TitleDocumentResponse"] = []
    document_tasks: List["DocumentTaskResponse"] = []

    class Config:
        from_attributes = True


# Delayed imports to avoid circular imports - resolved by Pydantic at runtime
from app.schemas.title import TitleDocumentResponse  # noqa: E402, F401
from app.schemas.document import DocumentTaskResponse  # noqa: E402, F401

# Update forward references for Pydantic v2
ProjectDetailResponse.model_rebuild()
