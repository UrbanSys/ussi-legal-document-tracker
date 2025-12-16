from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lookups import EncumbranceAction, EncumbranceStatus
from app.schemas.lookups import (
    EncumbranceActionCreate,
    EncumbranceActionResponse,
    EncumbranceStatusCreate,
    EncumbranceStatusResponse,
)

router = APIRouter(prefix="/lookups", tags=["Lookups"])


@router.post(
    "/encumbrance-actions",
    response_model=EncumbranceActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_encumbrance_action(
    payload: EncumbranceActionCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(EncumbranceAction)
        .filter(EncumbranceAction.code == payload.code)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Encumbrance action with this code already exists",
        )

    action = EncumbranceAction(
        code=payload.code,
        label=payload.label,
        description=payload.description,
    )

    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.post(
    "/encumbrance-statuses",
    response_model=EncumbranceStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_encumbrance_status(
    payload: EncumbranceStatusCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(EncumbranceStatus)
        .filter(EncumbranceStatus.code == payload.code)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Encumbrance status with this code already exists",
        )

    status_obj = EncumbranceStatus(
        code=payload.code,
        label=payload.label,
        description=payload.description,
    )

    db.add(status_obj)
    db.commit()
    db.refresh(status_obj)
    return status_obj


from typing import List

@router.get(
    "/encumbrance-actions",
    response_model=List[EncumbranceActionResponse],
)
def list_encumbrance_actions(db: Session = Depends(get_db)):
    """Get all encumbrance actions."""
    actions = (
        db.query(EncumbranceAction)
        .order_by(EncumbranceAction.id)
        .all()
    )
    return actions


@router.get(
    "/encumbrance-statuses",
    response_model=List[EncumbranceStatusResponse],
)
def list_encumbrance_statuses(db: Session = Depends(get_db)):
    """Get all encumbrance statuses."""
    statuses = (
        db.query(EncumbranceStatus)
        .order_by(EncumbranceStatus.id)
        .all()
    )
    return statuses
