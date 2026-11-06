from fastapi import APIRouter, HTTPException, status

from app.database import check_database

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check():
    """Report API and database readiness using an appropriate HTTP status."""
    try:
        check_database()
    except Exception:
        # Keep the existing response field contract while using HTTP 503
        # so clients and deployment monitors can detect database unavailability.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "degraded",
                "database": "unavailable",
                "version": "0.1.0",
            },
        )

    return {
        "status": "ok",
        "database": "ok",
        "version": "0.1.0",
    }
