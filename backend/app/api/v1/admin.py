from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.household import Household
from app.models.audit import AuditLog
from app.models.hierarchy import AdministrativeUnit, AdministrativeUnitStatus
from app.models.event import OutboxEvent
from app.schemas.admin import AdminDashboardMetrics, AuditLogResponse, AdminScopeAssignRequest
from app.schemas.citizen import CitizenProfileResponse
from app.api.deps import get_current_admin
from app.core.audit import record_audit_log
from app.core.scope import get_descendant_unit_ids, calculate_citizen_completeness

router = APIRouter(prefix="/admin", tags=["Administrator Operations"])


@router.get("/dashboard", response_model=AdminDashboardMetrics)
def get_admin_dashboard(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-023: Admin overview showing permitted counts for units, citizens, and households within scope.
    Strictly scoped according to FR-ADM-022.
    """
    scope_name = "National (All Areas)"
    scope_unit_id = current_admin.administrative_unit_id

    citizens_query = db.query(CitizenProfile)
    households_query = db.query(Household)
    units_query = db.query(AdministrativeUnit)

    # FR-ADM-022: Enforce scope if administrator is jurisdiction-assigned
    if scope_unit_id is not None:
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == scope_unit_id).first()
        if unit:
            scope_name = f"{unit.unit_type.title()}: {unit.name} ({unit.identifier})"
        allowed_ids = get_descendant_unit_ids(db, scope_unit_id)
        citizens_query = citizens_query.filter(CitizenProfile.administrative_unit_id.in_(allowed_ids))
        households_query = households_query.filter(Household.administrative_unit_id.in_(allowed_ids))
        units_query = units_query.filter(AdministrativeUnit.id.in_(allowed_ids))

    total_citizens = citizens_query.count()
    active_citizens = citizens_query.filter(CitizenProfile.profile_status == ProfileStatus.ACTIVE.value).count()
    pending_citizens = citizens_query.filter(CitizenProfile.profile_status == ProfileStatus.PENDING_REVIEW.value).count()
    total_households = households_query.count()
    total_units = units_query.count()
    active_units = units_query.filter(AdministrativeUnit.status == AdministrativeUnitStatus.ACTIVE.value).count()

    recent_profiles = (
        citizens_query
        .order_by(CitizenProfile.created_at.desc())
        .limit(5)
        .all()
    )

    recent_responses = []
    for p in recent_profiles:
        score, missing = calculate_citizen_completeness(p)
        resp = CitizenProfileResponse.model_validate(p)
        resp.completeness_score = score
        resp.missing_fields = missing
        resp.administrative_unit_name = p.administrative_unit.name if p.administrative_unit else None
        recent_responses.append(resp)

    return AdminDashboardMetrics(
        total_citizens=total_citizens,
        active_citizens=active_citizens,
        pending_citizens=pending_citizens,
        total_households=total_households,
        total_administrative_units=total_units,
        active_units=active_units,
        admin_scope=scope_name,
        admin_scope_unit_id=scope_unit_id,
        recent_registrations=recent_responses
    )


@router.post("/scope/assign")
def assign_administrative_scope(
    payload: AdminScopeAssignRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-021: Associate admin users with allowed roles and administrative units.
    FR-ADM-024: Record audit events for scope changes.
    """
    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    if target_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrative scope can only be assigned to accounts with the 'admin' role."
        )

    old_scope = target_user.administrative_unit_id

    if payload.administrative_unit_id is not None:
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == payload.administrative_unit_id).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target administrative unit does not exist.")
        target_user.administrative_unit_id = unit.id
        unit_name = unit.name
    else:
        target_user.administrative_unit_id = None
        unit_name = "National (Unrestricted)"

    # Audit & Domain Event (FR-ADM-024 & FR-ADM-025)
    record_audit_log(
        db=db,
        actor=current_admin,
        action="ASSIGN_ADMIN_SCOPE",
        resource_type="user",
        resource_id=str(target_user.id),
        details={"user_email": target_user.email, "old_scope_id": old_scope, "new_scope_id": payload.administrative_unit_id}
    )

    event = OutboxEvent.create(
        event_type="ADMIN_SCOPE_ASSIGNED",
        aggregate_type="scope",
        aggregate_id=str(target_user.id),
        payload={"user_id": target_user.id, "email": target_user.email, "scope_unit_id": payload.administrative_unit_id}
    )
    db.add(event)
    db.commit()

    return {
        "message": f"Administrative scope successfully updated for {target_user.email}.",
        "user_id": target_user.id,
        "assigned_scope": unit_name,
        "administrative_unit_id": target_user.administrative_unit_id,
    }


@router.get("/admins")
def list_admin_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List administrators with their current administrative scope assignment."""
    admins = db.query(User).filter(User.role == UserRole.ADMIN.value).all()
    results = []
    for a in admins:
        scope_title = a.administrative_unit.name if a.administrative_unit else "National (All Areas)"
        results.append({
            "id": a.id,
            "email": a.email,
            "role": a.role,
            "account_status": a.account_status,
            "administrative_unit_id": a.administrative_unit_id,
            "administrative_scope": scope_title,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    return results


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None, description="Filter by action code"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to view immutable audit trails of administrative actions (FR-ADM-024).
    """
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action.strip().upper())

    logs = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs
