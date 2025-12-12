"""
API routes for document task and document generation endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DocumentTask, LegalDocument
from app.schemas.document import (
    DocumentTaskCreate,
    DocumentTaskUpdate,
    DocumentTaskResponse,
)
from typing import List

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentTaskResponse)
def create_document_task(
    doc_task: DocumentTaskCreate,
    db: Session = Depends(get_db),
):
    """Create a new document task."""
    db_task = DocumentTask(**doc_task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=List[DocumentTaskResponse])
def list_document_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get all document tasks for a project."""
    tasks = (
        db.query(DocumentTask)
        .filter(DocumentTask.project_id == project_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tasks


@router.get("/{task_id}", response_model=DocumentTaskResponse)
def get_document_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific document task."""
    task = db.query(DocumentTask).filter(DocumentTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document task not found",
        )
    return task


@router.put("/{task_id}", response_model=DocumentTaskResponse)
def update_document_task(
    task_id: int,
    task_update: DocumentTaskUpdate,
    db: Session = Depends(get_db),
):
    """Update a document task."""
    db_task = db.query(DocumentTask).filter(DocumentTask.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document task not found",
        )

    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a document task."""
    db_task = db.query(DocumentTask).filter(DocumentTask.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document task not found",
        )

    db.delete(db_task)
    db.commit()
