"""
Pydantic schemas for lookup tables.
"""
from pydantic import BaseModel


class EncumbranceActionResponse(BaseModel):
    id: int
    code: str
    label: str
    description: str | None = None

    class Config:
        from_attributes = True


class EncumbranceStatusResponse(BaseModel):
    id: int
    code: str
    label: str
    description: str | None = None

    class Config:
        from_attributes = True


class DocumentTaskStatusResponse(BaseModel):
    id: int
    code: str
    label: str

    class Config:
        from_attributes = True


class DocumentCategoryResponse(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True
