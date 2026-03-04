from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from nda_app.config import settings
from nda_app.database import get_db
from nda_app.models.nda import NDAStatus
from nda_app.schemas.nda import NDACreate, NDAListResponse, NDAResponse, NDAUpdate
from nda_app.services.generator import generate_nda
from nda_app.services.tracker import delete_nda, get_nda, list_ndas, update_nda

router = APIRouter()

DbDep = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=NDAResponse, status_code=201)
def create_nda(nda_data: NDACreate, db: DbDep):
    """Generate a new NDA document and create a registry entry."""
    nda = generate_nda(db, nda_data)
    return nda


@router.get("/", response_model=NDAListResponse)
def read_ndas(
    db: DbDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: NDAStatus | None = None,
):
    """List all NDAs with optional status filter."""
    items, total = list_ndas(db, skip=skip, limit=limit, status=status)
    return NDAListResponse(items=items, total=total)


@router.get("/{nda_id}", response_model=NDAResponse)
def read_nda(nda_id: int, db: DbDep):
    """Get a single NDA by ID."""
    nda = get_nda(db, nda_id)
    if not nda:
        raise HTTPException(status_code=404, detail="NDA not found")
    return nda


@router.patch("/{nda_id}", response_model=NDAResponse)
def update_nda_endpoint(nda_id: int, update_data: NDAUpdate, db: DbDep):
    """Update NDA tracker fields (status, execution_date, notes)."""
    nda = update_nda(db, nda_id, update_data)
    if not nda:
        raise HTTPException(status_code=404, detail="NDA not found")
    return nda


@router.delete("/{nda_id}", status_code=204)
def delete_nda_endpoint(nda_id: int, db: DbDep):
    """Delete an NDA record."""
    if not delete_nda(db, nda_id):
        raise HTTPException(status_code=404, detail="NDA not found")


@router.get("/{nda_id}/download")
def download_nda(nda_id: int, db: DbDep):
    """Download the generated NDA .docx file."""
    nda = get_nda(db, nda_id)
    if not nda:
        raise HTTPException(status_code=404, detail="NDA not found")
    if not nda.file_path:
        raise HTTPException(status_code=404, detail="No file available for this NDA")

    file_path = settings.output_dir.parent / nda.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
