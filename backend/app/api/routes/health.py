from fastapi import APIRouter
from app.database import check_database

router = APIRouter(tags=["system"])

@router.get("/health")
def health_check():
    # Include a database probe so the UI can distinguish API and DB readiness.
    try:
        check_database()
        return {"status": "ok", "database": "ok", "version": "0.1.0"}
    except Exception:
        return {"status": "degraded", "database": "unavailable", "version": "0.1.0"}
