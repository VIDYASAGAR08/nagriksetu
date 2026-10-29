import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.household import Household
from app.models.hierarchy import AdministrativeUnit
from app.models.event import OutboxEvent
from app.schemas.citizen import (
    CitizenProfileResponse,
    CitizenProfileUpdateRequest,
    AdminCitizenCreateRequest,
    AdminCitizenUpdateRequest,
    AdminStatusUpdateRequest,
)
from app.api.deps import (
    get_current_user,
    get_current_citizen,
    get_current_admin,
    get_current_citizen_profile,
)
from app.core.security import hash_password
from app.core.audit import record_audit_log
from app.core.scope import (
    get_descendant_unit_ids,
    enforce_admin_scope,
    calculate_citizen_completeness,
)

router = APIRouter(prefix="/citizens", tags=["Citizens"])


def generate_citizen_code() -> str:
    return f"CIT-{uuid.uuid4().hex[:8].upper()}"


def _to_citizen_response(p: CitizenProfile) -> CitizenProfileResponse:
    score, missing = calculate_citizen_completeness(p)
    unit_name = p.administrative_unit.name if p.administrative_unit else None

    return CitizenProfileResponse(
        id=p.id,
        citizen_code=p.citizen_code,
        full_name=p.full_name,
        date_of_birth=p.date_of_birth,
        phone_number=p.phone_number,
        preferred_language=p.preferred_language,
        profile_status=p.profile_status,
        household_id=p.household_id,
        household_relationship=p.household_relationship,
        administrative_unit_id=p.administrative_unit_id,
        administrative_unit_name=unit_name,
        completeness_score=score,
        missing_fields=missing,
        user_id=p.user_id,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ==========================================
# CITIZEN SELF-SERVICE ENDPOINTS
# ==========================================

@router.get("/me", response_model=CitizenProfileResponse)
def get_my_profile(
    profile: CitizenProfile = Depends(get_current_citizen_profile)
):
    """
    FR-ADM-007: Retrieve authenticated citizen's own profile.
    Derives identity strictly from authenticated session with completeness metrics (FR-ADM-013).
    """
    return _to_citizen_response(profile)


@router.patch("/me", response_model=CitizenProfileResponse)
def update_my_profile(
    payload: CitizenProfileUpdateRequest,
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-008: Update permitted fields of own profile.
    FR-ADM-012: Records changed fields with actor and timestamp.
    """
    update_data = payload.model_dump(exclude_unset=True)

    # Validate administrative unit if provided
    if "administrative_unit_id" in update_data and update_data["administrative_unit_id"] is not None:
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == update_data["administrative_unit_id"]).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified administrative unit does not exist.")

    diffs = {}
    for field, value in update_data.items():
        old_val = getattr(profile, field, None)
        if old_val != value:
            diffs[field] = {"old": str(old_val), "new": str(value)}
            setattr(profile, field, value)

    if diffs:
        # Audit log (FR-ADM-012 & FR-ADM-024)
        record_audit_log(
            db=db,
            actor=profile.user,
            action="CITIZEN_SELF_UPDATE",
            resource_type="citizen",
            resource_id=profile.citizen_code,
            details={"changes": diffs}
        )

        # Domain event (FR-ADM-025)
        event = OutboxEvent.create(
            event_type="CITIZEN_PROFILE_UPDATED",
            aggregate_type="citizen",
            aggregate_id=profile.citizen_code,
            payload={"citizen_code": profile.citizen_code, "changes": diffs}
        )
        db.add(event)
        db.commit()
        db.refresh(profile)

    return _to_citizen_response(profile)


# ==========================================
# ADMINISTRATOR MANAGEMENT ENDPOINTS
# ==========================================

@router.get("", response_model=List[CitizenProfileResponse])
def list_citizens(
    search: Optional[str] = Query(None, description="Search by full name, citizen code, or phone"),
    status: Optional[str] = Query(None, description="Filter by profile status"),
    household_id: Optional[int] = Query(None, description="Filter by household"),
    administrative_unit_id: Optional[int] = Query(None, description="Filter by administrative unit"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-011: Admin-only search and filtering of citizen profiles.
    FR-ADM-022: Enforces administrative jurisdiction scope.
    """
    query = db.query(CitizenProfile)

    # FR-ADM-022: Scope enforcement
    if current_admin.administrative_unit_id is not None:
        allowed_ids = get_descendant_unit_ids(db, current_admin.administrative_unit_id)
        query = query.filter(CitizenProfile.administrative_unit_id.in_(allowed_ids))

    if status:
        query = query.filter(CitizenProfile.profile_status == status)

    if household_id is not None:
        query = query.filter(CitizenProfile.household_id == household_id)

    if administrative_unit_id is not None:
        query = query.filter(CitizenProfile.administrative_unit_id == administrative_unit_id)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                CitizenProfile.full_name.ilike(search_filter),
                CitizenProfile.citizen_code.ilike(search_filter),
                CitizenProfile.phone_number.ilike(search_filter),
            )
        )

    profiles = query.order_by(CitizenProfile.created_at.desc()).offset(skip).limit(limit).all()
    return [_to_citizen_response(p) for p in profiles]


@router.post("", response_model=CitizenProfileResponse, status_code=status.HTTP_201_CREATED)
def admin_create_citizen(
    payload: AdminCitizenCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-006: Create citizen profile with unique code, mandatory fields, and area mapping.
    FR-ADM-022: Scoped admin can only create citizens in their jurisdiction.
    """
    if payload.administrative_unit_id:
        enforce_admin_scope(current_admin, payload.administrative_unit_id, db, "administrative jurisdiction")
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == payload.administrative_unit_id).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrative unit not found.")
    elif current_admin.administrative_unit_id is not None:
        # Default to the administrator's root scope if not explicitly specified
        payload.administrative_unit_id = current_admin.administrative_unit_id

    user_id = None
    if payload.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User account with this email already exists."
            )
        initial_pwd = payload.initial_password or "Welcome123!@"
        user = User(
            email=payload.email,
            password_hash=hash_password(initial_pwd),
            role=UserRole.CITIZEN.value,
            account_status=UserStatus.ACTIVE.value,
            administrative_unit_id=payload.administrative_unit_id,
        )
        db.add(user)
        db.flush()
        user_id = user.id

    # Check household if provided
    if payload.household_id:
        hh = db.query(Household).filter(Household.id == payload.household_id).first()
        if not hh:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Household ID {payload.household_id} not found."
            )
        enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household dwelling")

    citizen_code = generate_citizen_code()
    while db.query(CitizenProfile).filter(CitizenProfile.citizen_code == citizen_code).first():
        citizen_code = generate_citizen_code()

    new_profile = CitizenProfile(
        user_id=user_id,
        citizen_code=citizen_code,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        phone_number=payload.phone_number,
        preferred_language=payload.preferred_language,
        profile_status=payload.profile_status,
        household_id=payload.household_id,
        household_relationship=payload.household_relationship,
        administrative_unit_id=payload.administrative_unit_id,
    )
    db.add(new_profile)
    db.flush()

    # Record audit log & outbox event
    record_audit_log(
        db=db,
        actor=current_admin,
        action="CITIZEN_CREATE",
        resource_type="citizen",
        resource_id=new_profile.citizen_code,
        details={"name": new_profile.full_name, "status": new_profile.profile_status, "area_id": payload.administrative_unit_id}
    )

    event = OutboxEvent.create(
        event_type="CITIZEN_REGISTERED",
        aggregate_type="citizen",
        aggregate_id=new_profile.citizen_code,
        payload={"citizen_code": new_profile.citizen_code, "name": new_profile.full_name}
    )
    db.add(event)
    db.commit()
    db.refresh(new_profile)

    return _to_citizen_response(new_profile)


@router.get("/{citizen_id}", response_model=CitizenProfileResponse)
def get_citizen_by_id(
    citizen_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """FR-ADM-007: Admin-only retrieval with scope verification."""
    profile = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    enforce_admin_scope(current_admin, profile.administrative_unit_id, db, "citizen profile")
    return _to_citizen_response(profile)


@router.put("/{citizen_id}", response_model=CitizenProfileResponse)
def admin_update_citizen(
    citizen_id: int,
    payload: AdminCitizenUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-008: Admin update of citizen fields, household assignment, and area scope.
    FR-ADM-012: Record field-level diffs in audit history.
    """
    profile = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    enforce_admin_scope(current_admin, profile.administrative_unit_id, db, "citizen profile")

    if payload.administrative_unit_id is not None:
        enforce_admin_scope(current_admin, payload.administrative_unit_id, db, "target administrative unit")
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == payload.administrative_unit_id).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target administrative unit does not exist.")

    if payload.household_id is not None and payload.household_id != profile.household_id:
        hh = db.query(Household).filter(Household.id == payload.household_id).first()
        if not hh:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Household ID {payload.household_id} does not exist."
            )
        enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household dwelling")

    update_data = payload.model_dump(exclude_unset=True)
    diffs = {}
    for field, val in update_data.items():
        old_val = getattr(profile, field, None)
        if old_val != val:
            diffs[field] = {"old": str(old_val), "new": str(val)}
            setattr(profile, field, val)

    if diffs:
        record_audit_log(
            db=db,
            actor=current_admin,
            action="CITIZEN_UPDATE",
            resource_type="citizen",
            resource_id=profile.citizen_code,
            details=diffs
        )

        event = OutboxEvent.create(
            event_type="CITIZEN_PROFILE_UPDATED",
            aggregate_type="citizen",
            aggregate_id=profile.citizen_code,
            payload={"citizen_code": profile.citizen_code, "changes": diffs}
        )
        db.add(event)
        db.commit()
        db.refresh(profile)

    return _to_citizen_response(profile)


@router.patch("/{citizen_id}/status", response_model=CitizenProfileResponse)
def admin_update_citizen_status(
    citizen_id: int,
    payload: AdminStatusUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-010: Support configured states (active, pending_review, archived).
    FR-ADM-012: Audit status changes with actor and timestamp.
    """
    valid_statuses = [s.value for s in ProfileStatus]
    if payload.profile_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid profile status. Allowed: {valid_statuses}"
        )

    profile = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    enforce_admin_scope(current_admin, profile.administrative_unit_id, db, "citizen profile")

    old_status = profile.profile_status
    profile.profile_status = payload.profile_status

    record_audit_log(
        db=db,
        actor=current_admin,
        action="CITIZEN_STATUS_CHANGE",
        resource_type="citizen",
        resource_id=profile.citizen_code,
        details={"from_status": old_status, "to_status": payload.profile_status}
    )

    event = OutboxEvent.create(
        event_type="CITIZEN_STATUS_CHANGED",
        aggregate_type="citizen",
        aggregate_id=profile.citizen_code,
        payload={"from": old_status, "to": payload.profile_status}
    )
    db.add(event)
    db.commit()
    db.refresh(profile)

    return _to_citizen_response(profile)


@router.delete("/{citizen_id}", status_code=status.HTTP_200_OK)
def admin_delete_citizen(
    citizen_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only deletion of citizen profile with audit trail."""
    profile = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    enforce_admin_scope(current_admin, profile.administrative_unit_id, db, "citizen profile")

    code = profile.citizen_code
    name = profile.full_name
    db.delete(profile)
    db.commit()

    record_audit_log(
        db=db,
        actor=current_admin,
        action="CITIZEN_DELETE",
        resource_type="citizen",
        resource_id=code,
        details={"name": name}
    )

    return {"message": f"Citizen profile {code} deleted successfully."}
