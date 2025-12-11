"""
API routes for project management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project, SurveyorALS
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    SurveyorCreate,
    SurveyorResponse,
)
from typing import List

router = APIRouter(prefix="/api/projects", tags=["projects"])


# Surveyor Endpoints
@router.get("/surveyors", response_model=List[SurveyorResponse])
def list_surveyors(db: Session = Depends(get_db)):
    """Get all surveyors in the system."""
    surveyors = db.query(SurveyorALS).all()
    return surveyors


@router.get("/surveyors/{surveyor_id}", response_model=SurveyorResponse)
def get_surveyor(surveyor_id: int, db: Session = Depends(get_db)):
    """Get a specific surveyor by ID."""
    surveyor = db.query(SurveyorALS).filter(SurveyorALS.id == surveyor_id).first()
    if not surveyor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surveyor not found",
        )
    return surveyor


@router.post("/surveyors", response_model=SurveyorResponse)
def create_surveyor(surveyor: SurveyorCreate, db: Session = Depends(get_db)):
    """Create a new surveyor."""
    db_surveyor = SurveyorALS(**surveyor.dict())
    db.add(db_surveyor)
    db.commit()
    db.refresh(db_surveyor)
    return db_surveyor


# Project Endpoints
@router.get("", response_model=List[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all projects with pagination."""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project with all related data."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.post("", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    # Check if project number already exists
    existing = db.query(Project).filter(Project.proj_num == project.proj_num).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project number already exists",
        )

    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    db.delete(db_project)
    db.commit()
