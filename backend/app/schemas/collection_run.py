"""Validation schemas for collection-run API requests and responses."""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


RunStatus = Literal["pending", "running", "success", "failed"]
RunTransitionStatus = Literal["running", "success", "failed"]


class CollectionRunCreate(BaseModel):
    """Payload for creating a pending execution record."""

    task_id: int = Field(gt=0)


class CollectionRunStatusUpdate(BaseModel):
    """Payload for a legal status transition and its completion metadata."""

    status: RunTransitionStatus
    records_count: int | None = Field(default=None, ge=0)
    error_message: str | None = Field(default=None, max_length=5000)

    @field_validator("error_message", mode="before")
    @classmethod
    def normalize_error_message(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        return value

    @model_validator(mode="after")
    def validate_status_metadata(self):
        if self.status == "failed" and not self.error_message:
            raise ValueError("error_message is required when status is failed.")
        if self.status != "failed" and self.error_message is not None:
            raise ValueError("error_message is only allowed when status is failed.")
        if self.status == "running" and self.records_count is not None:
            raise ValueError("records_count can only be supplied when a run finishes.")
        return self


class CollectionRunRead(BaseModel):
    """Public representation of a collection execution record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    status: RunStatus
    started_at: Any | None
    finished_at: Any | None
    records_count: int
    error_message: str | None
    duration_ms: int | None
    created_at: Any


class CollectionRunList(BaseModel):
    """Paginated collection-run list response."""

    items: list[CollectionRunRead]
    total: int
    limit: int
    offset: int
