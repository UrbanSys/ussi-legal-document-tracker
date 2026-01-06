"""
API routes for title document and encumbrance management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.title import TitleDocument, Encumbrance
from app.schemas.title import (
    TitleDocumentCreate,
    TitleDocumentResponse,
    EncumbranceCreate,
    EncumbranceUpdate,
    EncumbranceResponse,
)
from app.services.pdf_processor import PDFProcessorService, TitleDocumentService
from pypdf import PdfReader
import os
from typing import List
from app.config import UPLOAD_DIRECTORY

router = APIRouter(prefix="/api/titles", tags=["titles"])


@router.post("", response_model=TitleDocumentResponse)
def create_title_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process a title document PDF.
    Automatically extracts encumbrances and stores them.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as f:
            contents = file.file.read()
            f.write(contents)

        # Create title document record
        title_doc = TitleDocument(
            project_id=project_id,
            file_path=file_path,
            uploaded_by="system",  # TODO: Get from auth context
        )
        db.add(title_doc)
        db.commit()
        db.refresh(title_doc)

        # Process PDF and extract encumbrances
        pdf_reader = PdfReader(file_path)
        extracted_data = PDFProcessorService.process_title_cert(pdf_reader)
        TitleDocumentService.save_extracted_data(db, title_doc.id, extracted_data)

        db.refresh(title_doc)
        return title_doc

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}",
        )


@router.get("/{title_id}", response_model=TitleDocumentResponse)
def get_title_document(title_id: int, db: Session = Depends(get_db)):
    """Get a specific title document with its encumbrances."""
    title_doc = db.query(TitleDocument).filter(TitleDocument.id == title_id).first()
    if not title_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title document not found",
        )
    return title_doc


@router.get("", response_model=List[TitleDocumentResponse])
def list_title_documents(
    project_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get all title documents for a project."""
    title_docs = (
        db.query(TitleDocument)
        .filter(TitleDocument.project_id == project_id)
        .order_by(TitleDocument.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return title_docs


# Encumbrance Endpoints
@router.get("/{title_id}/encumbrances", response_model=List[EncumbranceResponse])
def get_encumbrances(title_id: int, db: Session = Depends(get_db)):
    """Get all encumbrances for a title document."""
    encumbrances = (
        db.query(Encumbrance)
        .filter(Encumbrance.title_document_id == title_id)
        .all()
    )
    return encumbrances


@router.get("/encumbrances/{encumbrance_id}", response_model=EncumbranceResponse)
def get_encumbrance(encumbrance_id: int, db: Session = Depends(get_db)):
    """Get a specific encumbrance."""
    encumbrance = (
        db.query(Encumbrance)
        .filter(Encumbrance.id == encumbrance_id)
        .first()
    )
    if not encumbrance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encumbrance not found",
        )
    return encumbrance

@router.post("/encumbrances", response_model=EncumbranceResponse)
def create_encumbrance(
    encumbrance: EncumbranceCreate,
    db: Session = Depends(get_db),
):
    """Create a new encumbrance for a title document."""
    # Verify title document exists
    title_doc = db.query(TitleDocument).filter(TitleDocument.id == encumbrance.title_document_id).first()
    if not title_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title document not found",
        )

    db_encumbrance = Encumbrance(**encumbrance.dict())
    db.add(db_encumbrance)
    db.commit()
    db.refresh(db_encumbrance)
    return db_encumbrance


@router.put("/encumbrances/{encumbrance_id}", response_model=EncumbranceResponse)
def update_encumbrance(
    encumbrance_id: int,
    encumbrance_update: EncumbranceUpdate,
    db: Session = Depends(get_db),
):
    """Update an encumbrance."""
    db_encumbrance = (
        db.query(Encumbrance)
        .filter(Encumbrance.id == encumbrance_id)
        .first()
    )
    if not db_encumbrance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encumbrance not found",
        )

    update_data = encumbrance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_encumbrance, field, value)

    db.commit()
    db.refresh(db_encumbrance)
    return db_encumbrance

@router.delete(
    "/{title_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_title_document(title_id: int, db: Session = Depends(get_db)):
    """
    Delete a title document and all associated encumbrances.
    """
    title_doc = (
        db.query(TitleDocument)
        .filter(TitleDocument.id == title_id)
        .first()
    )

    if not title_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title document not found",
        )

    try:
        # Delete encumbrances explicitly
        db.query(Encumbrance).filter(
            Encumbrance.title_document_id == title_id
        ).delete(synchronize_session=False)

        # Optionally delete the file from disk
        if title_doc.file_path and os.path.exists(title_doc.file_path):
            os.remove(title_doc.file_path)

        # Delete the title document
        db.delete(title_doc)
        db.commit()

        return None  # 204 No Content

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete title document: {str(e)}",
        )

@router.delete("/encumbrances/{encumbrance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_encumbrance(
    encumbrance_id: int,
    db: Session = Depends(get_db),
):
    """Delete an encumbrance."""
    db_encumbrance = (
        db.query(Encumbrance)
        .filter(Encumbrance.id == encumbrance_id)
        .first()
    )
    if not db_encumbrance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encumbrance not found",
        )

    db.delete(db_encumbrance)
    db.commit()
