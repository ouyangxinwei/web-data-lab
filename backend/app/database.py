"""SQLAlchemy engine, session factory, and database dependencies."""
from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL

database_url = make_url(DATABASE_URL)
is_sqlite = database_url.get_backend_name() == "sqlite"

connect_args = (
    {"check_same_thread": False, "timeout": 30}
    if is_sqlite
    else {"connect_timeout": 10}
)

engine_options = {
    "pool_pre_ping": True,
    # Keep the application pool bounded; the Neon pooled endpoint handles
    # multiplexing between application connections and database backends.
}
if not is_sqlite:
    engine_options.update(
        pool_size=5,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=300,
    )

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_options,
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _configure_sqlite_connection(dbapi_connection, _connection_record) -> None:
        """Apply SQLite settings to every newly opened DBAPI connection."""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=30000")
        finally:
            cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class shared by SQLAlchemy models."""


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per request and always close it.

    This dependency does not commit automatically. Services should define
    explicit transaction boundaries and call commit or rollback as needed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> bool:
    """Run a minimal query to verify that the database is reachable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
