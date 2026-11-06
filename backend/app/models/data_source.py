"""SQLAlchemy model for configured API and HTML data sources."""
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"
    __table_args__ = (
        CheckConstraint("source_type IN ('api', 'html')", name="ck_data_sources_source_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Store non-secret settings here. API credentials must not be stored in this JSON.
    config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tasks: Mapped[list["CollectionTask"]] = relationship(back_populates="source", passive_deletes=True)
    records: Mapped[list["CollectedRecord"]] = relationship(back_populates="source", passive_deletes=True)
