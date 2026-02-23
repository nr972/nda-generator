from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.nda import Jurisdiction
from app.schemas.nda import (
    JurisdictionCreate,
    JurisdictionListResponse,
    JurisdictionResponse,
)

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]

TOP_COUNT = 3


@router.get("/", response_model=JurisdictionListResponse)
def list_jurisdictions(db: DbDep):
    """Get all jurisdictions: top 3 by usage + full sorted list."""
    top_query = (
        select(Jurisdiction)
        .order_by(Jurisdiction.usage_count.desc(), Jurisdiction.display_name)
        .limit(TOP_COUNT)
    )
    top = list(db.scalars(top_query).all())

    all_query = select(Jurisdiction).order_by(
        Jurisdiction.country, Jurisdiction.subdivision.nulls_first()
    )
    all_jurisdictions = list(db.scalars(all_query).all())

    return JurisdictionListResponse(
        top_jurisdictions=top,
        all_jurisdictions=all_jurisdictions,
    )


@router.post("/", response_model=JurisdictionResponse, status_code=201)
def create_jurisdiction(data: JurisdictionCreate, db: DbDep):
    """Add a custom jurisdiction. Persists for future use."""
    existing = db.scalar(
        select(Jurisdiction).where(Jurisdiction.display_name == data.display_name)
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Jurisdiction '{data.display_name}' already exists",
        )

    jurisdiction = Jurisdiction(
        country=data.country,
        subdivision=data.subdivision,
        display_name=data.display_name,
        is_preset=False,
        usage_count=0,
    )
    db.add(jurisdiction)
    db.commit()
    db.refresh(jurisdiction)
    return jurisdiction
