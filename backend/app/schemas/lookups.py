from pydantic import BaseModel
from typing import Optional


class EncumbranceActionCreate(BaseModel):
    code: str
    label: str
    description: Optional[str] = None


class EncumbranceActionResponse(BaseModel):
    id: int
    code: str
    label: str
    description: Optional[str]

    class Config:
        from_attributes = True


class EncumbranceStatusCreate(BaseModel):
    code: str
    label: str
    description: Optional[str] = None


class EncumbranceStatusResponse(BaseModel):
    id: int
    code: str
    label: str
    description: Optional[str]

    class Config:
        from_attributes = True

class DocumentStatusCreate(BaseModel):
    code: str
    label: str


class DocumentStatusResponse(BaseModel):
    id: int
    code: str
    label: str

    class Config:
        from_attributes = True
