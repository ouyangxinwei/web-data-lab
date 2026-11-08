"""Read schemas for collected record snapshots."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CollectedRecordListItem(BaseModel):
    """Compact representation used by the paginated records list."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    run_id: int
    external_id: str | None
    data_json: dict[str, Any]
    content_hash: str | None
    collected_at: datetime


class CollectedRecordRead(CollectedRecordListItem):
    """Full record representation, including the optional original payload."""

    raw_data: Any | None


class CollectedRecordList(BaseModel):
    """Paginated collected-record response."""

    items: list[CollectedRecordListItem]
    total: int
    limit: int
    offset: int
