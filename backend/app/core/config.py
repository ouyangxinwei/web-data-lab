import os
from pathlib import Path

# Keep SQLite data in a predictable directory; hosted deployments can override it.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("WDL_DATA_DIR", PROJECT_ROOT / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("WDL_DATABASE_URL", f"sqlite:///{(DATA_DIR / 'web_data_lab.db').as_posix()}")

def allowed_origins() -> list[str]:
    raw = os.getenv("WDL_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
