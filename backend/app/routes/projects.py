"""
API routes for project management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
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
from typing import List, Dict
import io
from app.services.excel_generator import ExcelGeneratorService
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

@router.delete("/surveyors/{surveyor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_surveyor(surveyor_id: int, db: Session = Depends(get_db)):
    """Delete a specific surveyor by ID."""
    surveyor = db.query(SurveyorALS).filter(SurveyorALS.id == surveyor_id).first()
    if not surveyor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surveyor not found",
        )
    db.delete(surveyor)
    db.commit()


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
    projects = db.query(Project).order_by(Project.id).offset(skip).limit(limit).all()
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

@router.get("/by-number/{project_num}", response_model=ProjectDetailResponse)
def get_project_by_number(project_num: str, db: Session = Depends(get_db)):
    """Get a specific project by project number"""

    project = (
        db.query(Project)
        .filter(Project.proj_num == project_num)
        .first()
    )

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


@router.get(
    "/{project_id}/export-excel",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            },
            "description": "Excel export",
        }
    },
)
def export_project_excel(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    encumbrances = {}

    for title_doc in project.title_documents:
        plan_name = f"Title Document {title_doc.id}"

        encumbrances[plan_name] = [
            {
                "Document #": e.document_number,
                "Description": e.description,
                "Signatories": e.signatories,
                "Circulation Notes": e.circulation_notes,
                "Action": e.action.code if e.action else "",
                "Status": e.status.code if e.status else "",
            }
            for e in title_doc.encumbrances
        ]

    plans: Dict[str, list[dict]] = {}
    exist_enc = []

    for d in project.document_tasks:
        if d.category.id == 3:
            #Hardcoded existing encumbrances
            exist_enc.append(
                {
                    "Document/Desc": d.doc_desc,
                    "Copies/Dept": d.copies_dept,
                    "Signatories": d.signatories,
                    "Condition of Approval": d.condition_of_approval,
                    "Circulation Notes": d.circulation_notes,
                    "Status": d.document_status.code if d.document_status else "",
                }
            )
        else:
            category_code = d.category.code if d.category else "UNCATEGORIZED"
            print(category_code)
            if category_code not in plans:
                plans[category_code] = []
            plans[category_code].append(
                {
                    "Document/Desc": d.doc_desc,
                    "Copies/Dept": d.copies_dept,
                    "Signatories": d.signatories,
                    "Condition of Approval": d.condition_of_approval,
                    "Circulation Notes": d.circulation_notes,
                    "Status": d.document_status.code if d.document_status else "",
                }
            )

    buffer = io.BytesIO()

    ExcelGeneratorService.export_as_excel(
        buffer,
        encumbrances=encumbrances,
        plans=plans,
        new_agreements=exist_enc,        # per your note
        proj_num=project.proj_num,
    )

    buffer.seek(0)

    filename = f"{project.proj_num}_document_tracking.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
