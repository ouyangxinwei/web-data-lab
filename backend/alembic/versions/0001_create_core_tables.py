"""Create the four core Web Data Lab tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("source_type IN ('api', 'html')", name="ck_data_sources_source_type"),
    )
    op.create_index("ix_data_sources_name", "data_sources", ["name"])
    op.create_table(
        "collection_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("schedule_type", sa.String(length=20), server_default="manual", nullable=False),
        sa.Column("schedule_config", sa.JSON(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["data_sources.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("schedule_type IN ('manual', 'interval', 'cron')", name="ck_collection_tasks_schedule_type"),
    )
    op.create_index("ix_collection_tasks_source_id", "collection_tasks", ["source_id"])
    op.create_table(
        "collection_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["collection_tasks.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('pending', 'running', 'success', 'failed')", name="ck_collection_runs_status"),
    )
    op.create_index("ix_collection_runs_task_id", "collection_runs", ["task_id"])
    op.create_index("ix_collection_runs_status", "collection_runs", ["status"])
    op.create_table(
        "collected_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("data_json", sa.JSON(), nullable=False),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["data_sources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["collection_runs.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_collected_records_source_id", "collected_records", ["source_id"])
    op.create_index("ix_collected_records_run_id", "collected_records", ["run_id"])
    op.create_index("ix_collected_records_external_id", "collected_records", ["external_id"])
    op.create_index("ix_collected_records_content_hash", "collected_records", ["content_hash"])
    op.create_index("ix_collected_records_source_collected", "collected_records", ["source_id", "collected_at"])
    op.create_index("ix_collected_records_run_collected", "collected_records", ["run_id", "collected_at"])


def downgrade() -> None:
    op.drop_table("collected_records")
    op.drop_table("collection_runs")
    op.drop_table("collection_tasks")
    op.drop_table("data_sources")
