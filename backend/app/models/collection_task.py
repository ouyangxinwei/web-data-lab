"""SQLAlchemy model for reusable collection task definitions."""
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CollectionTask(Base):
    __tablename__ = "collection_tasks"
    __table_args__ = (
        CheckConstraint("schedule_type IN ('manual', 'interval', 'cron')", name="ck_collection_tasks_schedule_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual", server_default="manual")
    schedule_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    source: Mapped["DataSource"] = relationship(back_populates="tasks")
    runs: Mapped[list["CollectionRun"]] = relationship(back_populates="task", passive_deletes=True)
