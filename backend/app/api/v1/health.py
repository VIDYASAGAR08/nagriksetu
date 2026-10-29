from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter(tags=["Health & Readiness"])


@router.get("/health")
def health_check():
    """Liveness probe: verifies that the web service is running."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready")
def readiness_check(response: Response, db: Session = Depends(get_db)):
    """
    Readiness probe: verifies database connectivity and core service readiness.
    Returns HTTP 200 if connected, or 503 Service Unavailable if database is unreachable.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "service": settings.PROJECT_NAME
        }
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": "Database connectivity check failed."
        }
