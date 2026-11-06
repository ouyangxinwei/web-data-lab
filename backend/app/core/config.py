import os
from pathlib import Path

from sqlalchemy.engine import make_url

# The backend directory is the project root for local SQLite storage.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

# Allow deployments to place the database on a persistent mounted volume.
DATA_DIR = Path(os.getenv("WDL_DATA_DIR", str(DEFAULT_DATA_DIR))).expanduser()
DATABASE_URL = os.getenv(
    "WDL_DATABASE_URL",
    f"sqlite:///{(DATA_DIR / 'web_data_lab.db').as_posix()}",
)

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
