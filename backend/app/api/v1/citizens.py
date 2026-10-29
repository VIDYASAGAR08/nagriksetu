import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.citizen import CitizenProfile, ProfileStatus
from app.models.household import Household
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

router = APIRouter(prefix="/citizens", tags=["Citizens"])


def generate_citizen_code() -> str:
    return f"CIT-{uuid.uuid4().hex[:8].upper()}"


# ==========================================
# CITIZEN SELF-SERVICE ENDPOINTS
# ==========================================

@router.get("/me", response_model=CitizenProfileResponse)
def get_my_profile(
    profile: CitizenProfile = Depends(get_current_citizen_profile)
):
    """
    Retrieve authenticated citizen's own profile.
    The server derives identity strictly from the authenticated session.
    """
    return profile


@router.patch("/me", response_model=CitizenProfileResponse)
def update_my_profile(
    payload: CitizenProfileUpdateRequest,
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Update permitted fields of own profile.
    Protected fields such as role, status, and household assignment are forbidden.
    """
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


# ==========================================
# ADMINISTRATOR MANAGEMENT ENDPOINTS
# ==========================================

@router.get("", response_model=List[CitizenProfileResponse])
def list_citizens(
    search: Optional[str] = Query(None, description="Search by full name, citizen code, or phone"),
    status: Optional[str] = Query(None, description="Filter by profile status"),
    household_id: Optional[int] = Query(None, description="Filter by household"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to list citizen profiles with filtering and search.
    """
    query = db.query(CitizenProfile)

    if status:
        query = query.filter(CitizenProfile.profile_status == status)

    if household_id is not None:
        query = query.filter(CitizenProfile.household_id == household_id)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                CitizenProfile.full_name.ilike(search_filter),
                CitizenProfile.citizen_code.ilike(search_filter),
                CitizenProfile.phone_number.ilike(search_filter),
            )
        )

    return query.order_by(CitizenProfile.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=CitizenProfileResponse, status_code=status.HTTP_201_CREATED)
def admin_create_citizen(
    payload: AdminCitizenCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to create a citizen profile.
    Can optionally provision an account with development password if email is provided.
    """
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
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    # Record audit log
    record_audit_log(
        db=db,
        actor=current_admin,
        action="CITIZEN_CREATE",
        resource_type="citizen",
        resource_id=new_profile.citizen_code,
        details={"name": new_profile.full_name, "status": new_profile.profile_status}
    )

    return new_profile


@router.get("/{citizen_id}", response_model=CitizenProfileResponse)
def get_citizen_by_id(
    citizen_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to get any citizen by database ID."""
    profile = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )
    return profile


@router.put("/{citizen_id}", response_model=CitizenProfileResponse)
def admin_update_citizen(
    citizen_id: int,
    payload: AdminCitizenUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to update citizen details and household assignment."""
    profile = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    # Verify household if being changed
    if payload.household_id is not None and payload.household_id != profile.household_id:
        hh = db.query(Household).filter(Household.id == payload.household_id).first()
        if not hh:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Household ID {payload.household_id} does not exist."
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)

    record_audit_log(
        db=db,
        actor=current_admin,
        action="CITIZEN_UPDATE",
        resource_type="citizen",
        resource_id=profile.citizen_code,
        details={"updated_fields": list(update_data.keys())}
    )

    return profile


@router.patch("/{citizen_id}/status", response_model=CitizenProfileResponse)
def admin_update_citizen_status(
    citizen_id: int,
    payload: AdminStatusUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Administrative review workflow:
    Update citizen profile status (e.g. pending_review -> active or archived).
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

    old_status = profile.profile_status
    profile.profile_status = payload.profile_status
    db.commit()
    db.refresh(profile)

    record_audit_log(
        db=db,
        actor=current_admin,
        action="CITIZEN_STATUS_CHANGE",
        resource_type="citizen",
        resource_id=profile.citizen_code,
        details={"from_status": old_status, "to_status": payload.profile_status}
    )

    return profile


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
