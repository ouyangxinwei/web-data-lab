"""Alembic environment using a dedicated migration database URL."""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_migration_database_url
from app.database import Base
import app.models  # noqa: F401 - register all model tables

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
MIGRATION_DATABASE_URL = get_migration_database_url()


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""
    context.configure(
        url=MIGRATION_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Use a short-lived direct connection for schema migration work."""
    connectable = create_engine(
        MIGRATION_DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10}
        if not MIGRATION_DATABASE_URL.startswith("sqlite")
        else {},
    )
    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
