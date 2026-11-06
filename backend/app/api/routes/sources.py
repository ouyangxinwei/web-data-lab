"""CRUD endpoints for configured API and HTML data sources."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collected_record import CollectedRecord
from app.models.collection_task import CollectionTask
from app.models.data_source import DataSource
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceList,
    DataSourceRead,
    DataSourceReplace,
)

router = APIRouter(prefix="/sources", tags=["data sources"])


@router.get("", response_model=DataSourceList)
def list_data_sources(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    source_type: str | None = Query(default=None, pattern="^(api|html)$"),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return data sources newest first, with simple pagination and filters."""
    filters = []
    if source_type is not None:
        filters.append(DataSource.source_type == source_type)
    if is_active is not None:
        filters.append(DataSource.is_active == is_active)

    total = db.scalar(select(func.count()).select_from(DataSource).where(*filters)) or 0
    items = db.scalars(
        select(DataSource)
        .where(*filters)
        .order_by(DataSource.created_at.desc(), DataSource.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return DataSourceList(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=DataSourceRead, status_code=status.HTTP_201_CREATED)
def create_data_source(
    payload: DataSourceCreate,
    db: Session = Depends(get_db),
):
    """Validate and persist one new data source."""
    source = DataSource(**payload.model_dump())
    db.add(source)
    try:
        db.commit()
        db.refresh(source)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The data source conflicts with an existing database constraint.",
        ) from exc
    return source


@router.get("/{source_id}", response_model=DataSourceRead)
def get_data_source(source_id: int, db: Session = Depends(get_db)):
    """Fetch one data source or return 404 when it does not exist."""
    source = db.get(DataSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found.")
    return source


@router.put("/{source_id}", response_model=DataSourceRead)
def replace_data_source(
    source_id: int,
    payload: DataSourceReplace,
    db: Session = Depends(get_db),
):
    """Replace editable fields of a data source using a complete request body."""
    source = db.get(DataSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found.")

    for field, value in payload.model_dump().items():
        setattr(source, field, value)

    try:
        db.commit()
        db.refresh(source)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The data source conflicts with an existing database constraint.",
        ) from exc
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_source(source_id: int, db: Session = Depends(get_db)):
    """Delete an unused data source; preserve sources referenced by tasks or records."""
    source = db.get(DataSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found.")

    task_exists = db.scalar(
        select(CollectionTask.id).where(CollectionTask.source_id == source_id).limit(1)
    )
    record_exists = db.scalar(
        select(CollectedRecord.id).where(CollectedRecord.source_id == source_id).limit(1)
    )
    if task_exists is not None or record_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This data source is referenced by collection tasks or records and cannot be deleted.",
        )

    db.delete(source)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This data source is still referenced and cannot be deleted.",
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
