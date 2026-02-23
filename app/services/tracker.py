from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.nda import NDA, NDAStatus
from app.schemas.nda import NDAUpdate


def get_nda(db: Session, nda_id: int) -> NDA | None:
    """Get a single NDA by ID."""
    return db.get(NDA, nda_id)


def list_ndas(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: NDAStatus | None = None,
) -> tuple[list[NDA], int]:
    """List NDAs with optional status filter. Returns (items, total_count)."""
    query = select(NDA).order_by(NDA.created_at.desc())

    if status:
        query = query.where(NDA.status == status)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = list(db.scalars(query.offset(skip).limit(limit)).all())
    return items, total or 0


def update_nda(db: Session, nda_id: int, update_data: NDAUpdate) -> NDA | None:
    """Update NDA tracker fields (status, execution_date, notes)."""
    nda = db.get(NDA, nda_id)
    if not nda:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(nda, field, value)

    db.commit()
    db.refresh(nda)
    return nda


def delete_nda(db: Session, nda_id: int) -> bool:
    """Delete an NDA record. Returns True if deleted, False if not found."""
    nda = db.get(NDA, nda_id)
    if not nda:
        return False
    db.delete(nda)
    db.commit()
    return True
