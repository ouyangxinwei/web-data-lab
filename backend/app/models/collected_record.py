"""SQLAlchemy model for immutable collection snapshots/results."""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CollectedRecord(Base):
    __tablename__ = "collected_records"
    __table_args__ = (
        Index("ix_collected_records_source_collected", "source_id", "collected_at"),
        Index("ix_collected_records_run_collected", "run_id", "collected_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("collection_runs.id", ondelete="RESTRICT"), nullable=False, index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    data_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    raw_data: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    source: Mapped["DataSource"] = relationship(back_populates="records")
    run: Mapped["CollectionRun"] = relationship(back_populates="records")
