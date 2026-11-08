"""Read-only endpoints for collected data snapshots."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collected_record import CollectedRecord
from app.schemas.collected_record import (
    CollectedRecordList,
    CollectedRecordRead,
)

router = APIRouter(prefix="/records", tags=["collected records"])


@router.get("", response_model=CollectedRecordList)
def list_collected_records(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    source_id: int | None = Query(default=None, gt=0),
    run_id: int | None = Query(default=None, gt=0),
    external_id: str | None = Query(default=None, max_length=255),
    db: Session = Depends(get_db),
):
    """Return collected records newest first, with pagination and filters.

    The list response omits raw_data to keep list requests reasonably small.
    """
    filters = []
    if source_id is not None:
        filters.append(CollectedRecord.source_id == source_id)
    if run_id is not None:
        filters.append(CollectedRecord.run_id == run_id)
    if external_id is not None:
        filters.append(CollectedRecord.external_id == external_id)

    total = db.scalar(
        select(func.count()).select_from(CollectedRecord).where(*filters)
    ) or 0
    items = db.scalars(
        select(CollectedRecord)
        .where(*filters)
        .order_by(CollectedRecord.collected_at.desc(), CollectedRecord.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return CollectedRecordList(items=items, total=total, limit=limit, offset=offset)


@router.get("/{record_id}", response_model=CollectedRecordRead)
def get_collected_record(record_id: int, db: Session = Depends(get_db)):
    """Fetch one collected record, including its optional raw payload."""
    record = db.get(CollectedRecord, record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collected record not found.",
        )
    return record
