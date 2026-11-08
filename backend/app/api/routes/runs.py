"""Query and manage collection execution records."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collection_run import CollectionRun
from app.models.collection_task import CollectionTask
from app.models.data_source import DataSource
from app.schemas.collection_run import (
    CollectionRunCreate,
    CollectionRunList,
    CollectionRunRead,
    CollectionRunStatusUpdate,
)

router = APIRouter(prefix="/runs", tags=["collection runs"])


def _duration_ms(started_at: datetime, finished_at: datetime) -> int:
    """Calculate elapsed milliseconds, tolerating naive SQLite test timestamps."""
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    if finished_at.tzinfo is None:
        finished_at = finished_at.replace(tzinfo=timezone.utc)
    return max(0, int((finished_at - started_at).total_seconds() * 1000))


@router.get("", response_model=CollectionRunList)
def list_collection_runs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    task_id: int | None = Query(default=None, gt=0),
    run_status: str | None = Query(
        default=None,
        alias="status",
        pattern="^(pending|running|success|failed)$",
    ),
    db: Session = Depends(get_db),
):
    """Return execution records newest first, with pagination and filters."""
    filters = []
    if task_id is not None:
        filters.append(CollectionRun.task_id == task_id)
    if run_status is not None:
        filters.append(CollectionRun.status == run_status)

    total = db.scalar(
        select(func.count()).select_from(CollectionRun).where(*filters)
    ) or 0
    items = db.scalars(
        select(CollectionRun)
        .where(*filters)
        .order_by(CollectionRun.created_at.desc(), CollectionRun.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return CollectionRunList(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=CollectionRunRead, status_code=status.HTTP_201_CREATED)
def create_collection_run(
    payload: CollectionRunCreate,
    db: Session = Depends(get_db),
):
    """Create a pending run record for an enabled task and active source.

    This records a run request only; it does not execute a collector.
    """
    task = db.get(CollectionTask, payload.task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection task not found.",
        )
    if not task.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The collection task is disabled and cannot be run.",
        )

    source = db.get(DataSource, task.source_id)
    if source is None or not source.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The task's data source is missing or inactive; enable it before creating a run.",
        )

    run = CollectionRun(task_id=task.id, status="pending")
    db.add(run)
    try:
        db.commit()
        db.refresh(run)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The collection run conflicts with an existing database constraint.",
        ) from exc
    return run


@router.get("/{run_id}", response_model=CollectionRunRead)
def get_collection_run(run_id: int, db: Session = Depends(get_db)):
    """Fetch one execution record or return 404."""
    run = db.get(CollectionRun, run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection run not found.",
        )
    return run


@router.patch("/{run_id}/status", response_model=CollectionRunRead)
def update_collection_run_status(
    run_id: int,
    payload: CollectionRunStatusUpdate,
    db: Session = Depends(get_db),
):
    """Apply pending -> running -> success/failed transitions only."""
    run = db.scalar(
        select(CollectionRun)
        .where(CollectionRun.id == run_id)
        .with_for_update()
    )
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection run not found.",
        )

    if run.status == "pending" and payload.status == "running":
        now = datetime.now(timezone.utc)
        run.status = "running"
        run.started_at = now
        task = db.get(CollectionTask, run.task_id)
        if task is not None:
            task.last_run_at = now
    elif run.status == "running" and payload.status in {"success", "failed"}:
        now = datetime.now(timezone.utc)
        if run.started_at is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A running collection run must have started_at before it can finish.",
            )
        run.status = payload.status
        run.finished_at = now
        run.duration_ms = _duration_ms(run.started_at, now)
        if payload.records_count is not None:
            run.records_count = payload.records_count
        run.error_message = payload.error_message
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid collection run status transition: {run.status} -> {payload.status}.",
        )

    try:
        db.commit()
        db.refresh(run)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The collection run conflicts with an existing database constraint.",
        ) from exc
    return run
