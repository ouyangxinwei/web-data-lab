"""Environment-backed application and database configuration."""
import os
from pathlib import Path

from sqlalchemy.engine import make_url

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
ENVIRONMENT = os.getenv("WDL_ENV", "development").strip().lower()

# Production must explicitly provide the managed PostgreSQL connection string.
_configured_database_url = os.getenv("WDL_DATABASE_URL")
if not _configured_database_url and ENVIRONMENT == "production":
    raise RuntimeError("WDL_DATABASE_URL must be configured in production.")

# SQLite remains a convenience for local development only.
DATABASE_URL = _configured_database_url or (
    f"sqlite:///{(Path(os.getenv('WDL_DATA_DIR', str(DEFAULT_DATA_DIR))).expanduser() / 'web_data_lab.db').as_posix()}"
)

# Alembic should use Neon's direct endpoint, not the pooled application endpoint.
MIGRATION_DATABASE_URL = os.getenv("WDL_MIGRATION_DATABASE_URL")
if not MIGRATION_DATABASE_URL:
    if make_url(DATABASE_URL).get_backend_name() == "postgresql":
        raise RuntimeError(
            "WDL_MIGRATION_DATABASE_URL must be configured for PostgreSQL migrations."
        )
    MIGRATION_DATABASE_URL = DATABASE_URL


def _ensure_sqlite_directory() -> None:
    """Create the parent directory for a file-backed SQLite database."""
    database_url = make_url(DATABASE_URL)
    if database_url.get_backend_name() != "sqlite":
        return

    database_path = database_url.database
    if not database_path or database_path == ":memory:":
        return

    Path(database_path).expanduser().resolve().parent.mkdir(
        parents=True,
        exist_ok=True,
    )


_ensure_sqlite_directory()


def allowed_origins() -> list[str]:
    """Return the browser origins allowed to call the backend."""
    raw = os.getenv(
        "WDL_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
