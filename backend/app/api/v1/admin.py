from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.household import Household
from app.models.audit import AuditLog
from app.schemas.admin import AdminDashboardMetrics, AuditLogResponse
from app.schemas.citizen import CitizenProfileResponse
from app.api.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["Administrator Operations"])


@router.get("/dashboard", response_model=AdminDashboardMetrics)
def get_admin_dashboard(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns live database-derived statistics for the Administrative Service.
    No hardcoded numbers or decorative false metrics.
    """
    total_citizens = db.query(CitizenProfile).count()
    active_citizens = db.query(CitizenProfile).filter(
        CitizenProfile.profile_status == ProfileStatus.ACTIVE.value
    ).count()
    pending_citizens = db.query(CitizenProfile).filter(
        CitizenProfile.profile_status == ProfileStatus.PENDING_REVIEW.value
    ).count()
    total_households = db.query(Household).count()

    recent_profiles = (
        db.query(CitizenProfile)
        .order_by(CitizenProfile.created_at.desc())
        .limit(5)
        .all()
    )

    return AdminDashboardMetrics(
        total_citizens=total_citizens,
        active_citizens=active_citizens,
        pending_citizens=pending_citizens,
        total_households=total_households,
        recent_registrations=[CitizenProfileResponse.model_validate(p) for p in recent_profiles]
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to view immutable audit trails of administrative actions.
    """
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs
