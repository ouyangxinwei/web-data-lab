"""CRUD endpoints for collection task definitions."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collection_run import CollectionRun
from app.models.collection_task import CollectionTask
from app.models.data_source import DataSource
from app.schemas.collection_task import (
    CollectionTaskCreate,
    CollectionTaskList,
    CollectionTaskRead,
    CollectionTaskReplace,
)

router = APIRouter(prefix="/tasks", tags=["collection tasks"])


def _require_active_source(db: Session, source_id: int) -> DataSource:
    """Require an existing, enabled source before attaching a task to it."""
    source = db.get(DataSource, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified data source does not exist.",
        )
    if not source.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified data source is inactive; enable it before creating or updating a task.",
        )
    return source


@router.get("", response_model=CollectionTaskList)
def list_collection_tasks(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    source_id: int | None = Query(default=None, gt=0),
    schedule_type: str | None = Query(default=None, pattern="^(manual|interval|cron)$"),
    is_enabled: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return tasks newest first, with pagination and optional filters."""
    filters = []
    if source_id is not None:
        filters.append(CollectionTask.source_id == source_id)
    if schedule_type is not None:
        filters.append(CollectionTask.schedule_type == schedule_type)
    if is_enabled is not None:
        filters.append(CollectionTask.is_enabled == is_enabled)

    total = db.scalar(
        select(func.count()).select_from(CollectionTask).where(*filters)
    ) or 0
    items = db.scalars(
        select(CollectionTask)
        .where(*filters)
        .order_by(CollectionTask.created_at.desc(), CollectionTask.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return CollectionTaskList(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=CollectionTaskRead, status_code=status.HTTP_201_CREATED)
def create_collection_task(
    payload: CollectionTaskCreate,
    db: Session = Depends(get_db),
):
    """Create a task only when its source exists and is active."""
    _require_active_source(db, payload.source_id)
    task = CollectionTask(**payload.model_dump())
    db.add(task)
    try:
        db.commit()
        db.refresh(task)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The collection task conflicts with an existing database constraint.",
        ) from exc
    return task


@router.get("/{task_id}", response_model=CollectionTaskRead)
def get_collection_task(task_id: int, db: Session = Depends(get_db)):
    """Fetch one task or return 404 when it does not exist."""
    task = db.get(CollectionTask, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection task not found.",
        )
    return task


@router.put("/{task_id}", response_model=CollectionTaskRead)
def replace_collection_task(
    task_id: int,
    payload: CollectionTaskReplace,
    db: Session = Depends(get_db),
):
    """Replace editable task fields after validating the selected source."""
    task = db.get(CollectionTask, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection task not found.",
        )

    _require_active_source(db, payload.source_id)
    for field, value in payload.model_dump().items():
        setattr(task, field, value)

    try:
        db.commit()
        db.refresh(task)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The collection task conflicts with an existing database constraint.",
        ) from exc
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task only when it has no execution history."""
    task = db.get(CollectionTask, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection task not found.",
        )

    run_exists = db.scalar(
        select(CollectionRun.id).where(CollectionRun.task_id == task_id).limit(1)
    )
    if run_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This collection task has execution history and cannot be deleted.",
        )

    db.delete(task)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This collection task is still referenced and cannot be deleted.",
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
