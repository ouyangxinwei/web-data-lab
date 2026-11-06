"""Validation schemas for collection-task API requests and responses."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ScheduleType = Literal["manual", "interval", "cron"]


class CollectionTaskBase(BaseModel):
    """Fields shared by task creation and full replacement."""

    source_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    schedule_type: ScheduleType = "manual"
    schedule_config: dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("name must not be empty")
        return value


class CollectionTaskCreate(CollectionTaskBase):
    """Payload accepted when creating a collection task."""


class CollectionTaskReplace(CollectionTaskBase):
    """Complete replacement payload for PUT /api/tasks/{task_id}."""


class CollectionTaskRead(BaseModel):
    """Public representation of a collection task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    name: str
    schedule_type: ScheduleType
    schedule_config: dict[str, Any]
    is_enabled: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CollectionTaskList(BaseModel):
    """Paginated collection-task list response."""

    items: list[CollectionTaskRead]
    total: int
    limit: int
    offset: int
