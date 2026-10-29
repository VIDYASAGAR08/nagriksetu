import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.citizen import CitizenProfile
from app.models.household import Household
from app.schemas.household import (
    HouseholdResponse,
    AdminHouseholdResponse,
    AdminHouseholdCreateRequest,
    AdminHouseholdUpdateRequest,
    HouseholdMemberAssignRequest,
    HouseholdMemberSummary,
)
from app.api.deps import (
    get_current_citizen,
    get_current_admin,
    get_current_citizen_profile,
)
from app.core.audit import record_audit_log

router = APIRouter(prefix="/households", tags=["Households"])


def generate_household_code() -> str:
    return f"HHD-{uuid.uuid4().hex[:8].upper()}"


# ==========================================
# CITIZEN-SCOPED HOUSEHOLD ENDPOINTS
# ==========================================

@router.get("/me", response_model=HouseholdResponse)
def get_my_household(
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Retrieve permitted household information for the authenticated citizen.
    Privacy protection:
    - Never exposes administrative notes.
    - Household member list only displays public names, codes, and relationships;
      no emails, phone numbers, or credentials of co-residents are exposed.
    """
    if not profile.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not currently linked to any registered household."
        )

    household = db.query(Household).filter(Household.id == profile.household_id).first()
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household record not found."
        )

    # Build safe member summaries
    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == household.id).all()
    member_summaries = [
        HouseholdMemberSummary(
            id=m.id,
            citizen_code=m.citizen_code,
            full_name=m.full_name,
            household_relationship=m.household_relationship
        )
        for m in members
    ]

    return HouseholdResponse(
        id=household.id,
        household_code=household.household_code,
        address_line=household.address_line,
        locality=household.locality,
        city=household.city,
        state=household.state,
        postal_code=household.postal_code,
        members=member_summaries,
        created_at=household.created_at,
        updated_at=household.updated_at,
    )


# ==========================================
# ADMINISTRATOR HOUSEHOLD ENDPOINTS
# ==========================================

@router.get("", response_model=List[AdminHouseholdResponse])
def list_households(
    search: Optional[str] = Query(None, description="Search by code, locality, city, or address"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only list of households with member counts and administrative notes."""
    query = db.query(Household)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Household.household_code.ilike(search_filter),
                Household.address_line.ilike(search_filter),
                Household.locality.ilike(search_filter),
                Household.city.ilike(search_filter),
                Household.postal_code.ilike(search_filter),
            )
        )

    households = query.order_by(Household.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for hh in households:
        members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
        member_summaries = [
            HouseholdMemberSummary(
                id=m.id,
                citizen_code=m.citizen_code,
                full_name=m.full_name,
                household_relationship=m.household_relationship
            )
            for m in members
        ]
        result.append(
            AdminHouseholdResponse(
                id=hh.id,
                household_code=hh.household_code,
                address_line=hh.address_line,
                locality=hh.locality,
                city=hh.city,
                state=hh.state,
                postal_code=hh.postal_code,
                administrative_notes=hh.administrative_notes,
                members=member_summaries,
                created_at=hh.created_at,
                updated_at=hh.updated_at,
            )
        )
    return result


@router.post("", response_model=AdminHouseholdResponse, status_code=status.HTTP_201_CREATED)
def create_household(
    payload: AdminHouseholdCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only creation of new household record."""
    code = payload.household_code or generate_household_code()
    # Check uniqueness
    existing = db.query(Household).filter(Household.household_code == code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Household code '{code}' already exists."
        )

    new_hh = Household(
        household_code=code,
        address_line=payload.address_line,
        locality=payload.locality,
        city=payload.city,
        state=payload.state,
        postal_code=payload.postal_code,
        administrative_notes=payload.administrative_notes,
    )
    db.add(new_hh)
    db.commit()
    db.refresh(new_hh)

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_CREATE",
        resource_type="household",
        resource_id=new_hh.household_code,
        details={"address": f"{new_hh.address_line}, {new_hh.city}"}
    )

    return AdminHouseholdResponse(
        id=new_hh.id,
        household_code=new_hh.household_code,
        address_line=new_hh.address_line,
        locality=new_hh.locality,
        city=new_hh.city,
        state=new_hh.state,
        postal_code=new_hh.postal_code,
        administrative_notes=new_hh.administrative_notes,
        members=[],
        created_at=new_hh.created_at,
        updated_at=new_hh.updated_at,
    )


@router.get("/{household_id}", response_model=AdminHouseholdResponse)
def get_household_by_id(
    household_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only detail view of a single household."""
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
    member_summaries = [
        HouseholdMemberSummary(
            id=m.id,
            citizen_code=m.citizen_code,
            full_name=m.full_name,
            household_relationship=m.household_relationship
        )
        for m in members
    ]

    return AdminHouseholdResponse(
        id=hh.id,
        household_code=hh.household_code,
        address_line=hh.address_line,
        locality=hh.locality,
        city=hh.city,
        state=hh.state,
        postal_code=hh.postal_code,
        administrative_notes=hh.administrative_notes,
        members=member_summaries,
        created_at=hh.created_at,
        updated_at=hh.updated_at,
    )


@router.put("/{household_id}", response_model=AdminHouseholdResponse)
def update_household(
    household_id: int,
    payload: AdminHouseholdUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only update of household address and notes."""
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(hh, field, val)

    db.commit()
    db.refresh(hh)

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_UPDATE",
        resource_type="household",
        resource_id=hh.household_code,
        details={"updated_fields": list(update_data.keys())}
    )

    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
    member_summaries = [
        HouseholdMemberSummary(
            id=m.id,
            citizen_code=m.citizen_code,
            full_name=m.full_name,
            household_relationship=m.household_relationship
        )
        for m in members
    ]

    return AdminHouseholdResponse(
        id=hh.id,
        household_code=hh.household_code,
        address_line=hh.address_line,
        locality=hh.locality,
        city=hh.city,
        state=hh.state,
        postal_code=hh.postal_code,
        administrative_notes=hh.administrative_notes,
        members=member_summaries,
        created_at=hh.created_at,
        updated_at=hh.updated_at,
    )


@router.delete("/{household_id}", status_code=status.HTTP_200_OK)
def delete_household(
    household_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only deletion of household.
    Safely unlinks associated citizen profiles (sets household_id to NULL) before deletion.
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    code = hh.household_code
    # Unlink members
    db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).update(
        {"household_id": None, "household_relationship": None}
    )
    db.delete(hh)
    db.commit()

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_DELETE",
        resource_type="household",
        resource_id=code
    )

    return {"message": f"Household {code} deleted successfully."}


@router.post("/{household_id}/assign", response_model=AdminHouseholdResponse)
def assign_member_to_household(
    household_id: int,
    payload: HouseholdMemberAssignRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only assignment of a citizen to a household.
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    citizen = db.query(CitizenProfile).filter(CitizenProfile.id == payload.citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    citizen.household_id = hh.id
    citizen.household_relationship = payload.household_relationship or "Member"
    db.commit()
    db.refresh(citizen)

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_MEMBER_ASSIGN",
        resource_type="household",
        resource_id=hh.household_code,
        details={"citizen_code": citizen.citizen_code, "relationship": citizen.household_relationship}
    )

    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
    member_summaries = [
        HouseholdMemberSummary(
            id=m.id,
            citizen_code=m.citizen_code,
            full_name=m.full_name,
            household_relationship=m.household_relationship
        )
        for m in members
    ]

    return AdminHouseholdResponse(
        id=hh.id,
        household_code=hh.household_code,
        address_line=hh.address_line,
        locality=hh.locality,
        city=hh.city,
        state=hh.state,
        postal_code=hh.postal_code,
        administrative_notes=hh.administrative_notes,
        members=member_summaries,
        created_at=hh.created_at,
        updated_at=hh.updated_at,
    )


@router.post("/{household_id}/unassign/{citizen_id}", response_model=AdminHouseholdResponse)
def unassign_member_from_household(
    household_id: int,
    citizen_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only removal of a citizen from a household.
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    citizen = db.query(CitizenProfile).filter(
        CitizenProfile.id == citizen_id,
        CitizenProfile.household_id == household_id
    ).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen is not assigned to this household."
        )

    citizen.household_id = None
    citizen.household_relationship = None
    db.commit()

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_MEMBER_UNASSIGN",
        resource_type="household",
        resource_id=hh.household_code,
        details={"citizen_code": citizen.citizen_code}
    )

    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
    member_summaries = [
        HouseholdMemberSummary(
            id=m.id,
            citizen_code=m.citizen_code,
            full_name=m.full_name,
            household_relationship=m.household_relationship
        )
        for m in members
    ]

    return AdminHouseholdResponse(
        id=hh.id,
        household_code=hh.household_code,
        address_line=hh.address_line,
        locality=hh.locality,
        city=hh.city,
        state=hh.state,
        postal_code=hh.postal_code,
        administrative_notes=hh.administrative_notes,
        members=member_summaries,
        created_at=hh.created_at,
        updated_at=hh.updated_at,
    )
