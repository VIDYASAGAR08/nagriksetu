import uuid
import json
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.citizen import CitizenProfile
from app.models.household import Household, HouseholdMembership, MembershipStatus, HouseholdLinkRequest, LinkRequestStatus
from app.models.hierarchy import AdministrativeUnit
from app.models.event import OutboxEvent
from app.models.records import LandRecord, MedicalRecord, EducationRecord
from app.schemas.household import (
    HouseholdResponse,
    AdminHouseholdResponse,
    AdminHouseholdCreateRequest,
    AdminHouseholdUpdateRequest,
    HouseholdMemberAssignRequest,
    HouseholdMemberSummary,
    HouseholdMembershipResponse,
    HouseholdMembershipEndRequest,
    HouseholdLinkSubmitRequest,
    HouseholdLinkActionRequest,
    HouseholdLinkRequestResponse,
)
from app.schemas.records import (
    LandRecordResponse,
    LandRecordCreateRequest,
    HouseholdDossierResponse,
)
from app.api.deps import (
    get_current_citizen,
    get_current_admin,
    get_current_citizen_profile,
)
from app.core.audit import record_audit_log
from app.core.scope import (
    get_descendant_unit_ids,
    enforce_admin_scope,
    audit_household_consistency,
    check_duplicate_households,
)

router = APIRouter(prefix="/households", tags=["Households"])

ALLOWED_RELATIONSHIPS = [
    "Head of Household",
    "Spouse",
    "Child",
    "Parent",
    "Sibling",
    "Relative",
    "Member"
]


def generate_household_code() -> str:
    return f"HHD-{uuid.uuid4().hex[:8].upper()}"


def parse_assigned_tasks(raw) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return [t.strip() for t in str(raw).split(",") if t.strip()]


def _build_admin_household_response(hh: Household, db: Session) -> AdminHouseholdResponse:
    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).all()
    member_summaries = []
    for m in members:
        role_val = getattr(m, "household_role", "MEMBER") or "MEMBER"
        if m.household_relationship == "Head of Household":
            role_val = "HEAD"
        tasks_val = parse_assigned_tasks(getattr(m, "assigned_tasks", "[]"))
        if role_val == "HEAD" and not tasks_val:
            tasks_val = ["can_manage_assets", "can_manage_medical", "can_manage_education", "can_manage_members", "can_pay_taxes"]
        member_summaries.append(
            HouseholdMemberSummary(
                id=m.id,
                citizen_code=m.citizen_code,
                full_name=m.full_name,
                household_relationship=m.household_relationship,
                household_role=role_val,
                assigned_tasks=tasks_val,
            )
        )

    consistency_flags = audit_household_consistency(hh, db)
    has_dup, matching_codes = check_duplicate_households(db, hh.address_line, hh.postal_code, exclude_id=hh.id)
    unit_name = hh.administrative_unit.name if hh.administrative_unit else None

    return AdminHouseholdResponse(
        id=hh.id,
        household_code=hh.household_code,
        address_line=hh.address_line,
        locality=hh.locality,
        city=hh.city,
        state=hh.state,
        postal_code=hh.postal_code,
        administrative_unit_id=hh.administrative_unit_id,
        administrative_unit_name=unit_name,
        administrative_notes=hh.administrative_notes,
        members=member_summaries,
        consistency_flags=consistency_flags,
        duplicate_warning=has_dup,
        matching_households=matching_codes,
        created_at=hh.created_at,
        updated_at=hh.updated_at,
    )


# ==========================================
# CITIZEN-SCOPED HOUSEHOLD ENDPOINTS
# ==========================================

@router.get("/me", response_model=HouseholdResponse)
def get_my_household(
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-018: Retrieve permitted household information for the authenticated citizen.
    Strict privacy protection:
    - Never exposes administrative notes.
    - Household member list displays public names, codes, and relationships only.
    - No co-resident phone numbers, emails, or account credentials are leaked.
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

    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == household.id).all()
    member_summaries = []
    for m in members:
        role_val = getattr(m, "household_role", "MEMBER") or "MEMBER"
        if m.household_relationship == "Head of Household":
            role_val = "HEAD"
        tasks_val = parse_assigned_tasks(getattr(m, "assigned_tasks", "[]"))
        if role_val == "HEAD" and not tasks_val:
            tasks_val = ["can_manage_assets", "can_manage_medical", "can_manage_education", "can_manage_members", "can_pay_taxes"]
        member_summaries.append(
            HouseholdMemberSummary(
                id=m.id,
                citizen_code=m.citizen_code,
                full_name=m.full_name,
                household_relationship=m.household_relationship,
                household_role=role_val,
                assigned_tasks=tasks_val,
            )
        )

    unit_name = household.administrative_unit.name if household.administrative_unit else None

    return HouseholdResponse(
        id=household.id,
        household_code=household.household_code,
        address_line=household.address_line,
        locality=household.locality,
        city=household.city,
        state=household.state,
        postal_code=household.postal_code,
        administrative_unit_id=household.administrative_unit_id,
        administrative_unit_name=unit_name,
        members=member_summaries,
        created_at=household.created_at,
        updated_at=household.updated_at,
    )


@router.get("/me/dossier", response_model=HouseholdDossierResponse)
def get_my_household_dossier(
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Retrieve full comprehensive household dossier for authenticated citizen:
    - Household metadata
    - Land & Property records
    - Family members with associated confidential Medical & Educational records
    Strictly isolated: Citizens cannot view dossiers of other households.
    """
    if not profile.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not currently linked to any registered household dwelling."
        )

    household = db.query(Household).filter(Household.id == profile.household_id).first()
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household record not found."
        )

    # 1. Fetch land records
    lands = db.query(LandRecord).filter(LandRecord.household_id == household.id).all()
    land_responses = [LandRecordResponse.model_validate(l) for l in lands]

    # 2. Fetch all household members with confidential profiles
    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == household.id).all()
    family_members_data = []

    for m in members:
        # Fetch or default medical record
        med = db.query(MedicalRecord).filter(MedicalRecord.citizen_id == m.id).first()
        med_dict = {
            "blood_group": med.blood_group if med else "Unknown",
            "chronic_conditions": med.chronic_conditions if med else "None Reported",
            "allergies": med.allergies if med else "None",
            "vaccination_status": med.vaccination_status if med else "Up to date",
            "disability_status": med.disability_status if med else "None",
            "abha_id": med.abha_id if med else None,
            "emergency_hospital": med.emergency_hospital if med else None,
            "emergency_contact_name": med.emergency_contact_name if med else None,
            "emergency_contact_phone": med.emergency_contact_phone if med else None,
        }

        # Fetch or default education record
        edu = db.query(EducationRecord).filter(EducationRecord.citizen_id == m.id).first()
        edu_dict = {
            "highest_qualification": edu.highest_qualification if edu else "Secondary (10th)",
            "institution_name": edu.institution_name if edu else None,
            "specialization": edu.specialization if edu else None,
            "year_of_completion": edu.year_of_completion if edu else None,
            "literacy_status": edu.literacy_status if edu else "Literate",
            "certificate_number": edu.certificate_number if edu else None,
        }

        role_val = getattr(m, "household_role", "MEMBER") or "MEMBER"
        if m.household_relationship == "Head of Household":
            role_val = "HEAD"
        tasks_val = parse_assigned_tasks(getattr(m, "assigned_tasks", "[]"))
        if role_val == "HEAD" and not tasks_val:
            tasks_val = ["can_manage_assets", "can_manage_medical", "can_manage_education", "can_manage_members", "can_pay_taxes"]

        family_members_data.append({
            "id": m.id,
            "citizen_code": m.citizen_code,
            "full_name": m.full_name,
            "phone_number": m.phone_number,
            "date_of_birth": str(m.date_of_birth) if m.date_of_birth else None,
            "preferred_language": m.preferred_language,
            "profile_status": m.profile_status,
            "household_relationship": m.household_relationship or "Member",
            "household_role": role_val,
            "assigned_tasks": tasks_val,
            "is_self": m.id == profile.id,
            "medical_record": med_dict,
            "education_record": edu_dict,
        })

    return HouseholdDossierResponse(
        household_id=household.id,
        household_code=household.household_code,
        address_line=household.address_line,
        locality=household.locality,
        city=household.city,
        state=household.state,
        postal_code=household.postal_code,
        members_count=len(members),
        land_records=land_responses,
        family_members=family_members_data,
    )


@router.post("/me/land", response_model=LandRecordResponse, status_code=status.HTTP_201_CREATED)
def add_household_land_record(
    payload: LandRecordCreateRequest,
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Register a land or immovable property asset for the citizen's verified household.
    """
    if not profile.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not linked to any household. Cannot register land record."
        )

    new_land = LandRecord(
        household_id=profile.household_id,
        survey_number=payload.survey_number,
        land_type=payload.land_type,
        area_measurement=payload.area_measurement,
        patta_passbook_number=payload.patta_passbook_number,
        district_sub_registrar=payload.district_sub_registrar,
        property_tax_status=payload.property_tax_status,
        market_valuation_inr=payload.market_valuation_inr,
    )
    db.add(new_land)
    db.commit()
    db.refresh(new_land)

    record_audit_log(
        db=db,
        actor=profile.user,
        action="LAND_RECORD_REGISTERED",
        resource_type="land_record",
        resource_id=f"LAND-{new_land.id}",
        details={"survey_number": payload.survey_number, "area": payload.area_measurement}
    )

    return new_land


def _build_link_request_response(req: HouseholdLinkRequest) -> HouseholdLinkRequestResponse:
    tasks = parse_assigned_tasks(req.assigned_tasks)
    return HouseholdLinkRequestResponse(
        id=req.id,
        household_id=req.household_id,
        household_code=req.household.household_code if req.household else "",
        requester_citizen_id=req.requester_citizen_id,
        requester_name=req.requester.full_name if req.requester else "Unknown Citizen",
        target_citizen_id=req.target_citizen_id,
        target_citizen_code=req.target.citizen_code if req.target else "N/A",
        target_citizen_name=req.target.full_name if req.target else "Unknown Citizen",
        relationship=req.relationship,
        household_role=req.household_role,
        assigned_tasks=tasks,
        status=req.status,
        admin_notes=req.admin_notes,
        created_at=req.created_at,
        reviewed_at=req.reviewed_at,
    )


@router.post("/me/link-requests", response_model=HouseholdLinkRequestResponse, status_code=status.HTTP_201_CREATED)
def submit_member_link_request(
    payload: HouseholdLinkSubmitRequest,
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Teacher Feedback Requirement:
    - User initiates linking of family member to their registered household.
    - User EXPLICITLY specifies the exact relationship (e.g. Father, Mother, Spouse, Son, Daughter).
    - User EXPLICITLY defines the household role and individual assigned tasks/jobs.
    - System or admin does NOT auto-assign or mutate relationship or roles.
    - Submitted request enters 'pending_admin_approval' awaiting admin verification gate.
    """
    if not profile.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not linked to any household. Cannot request member linkage."
        )

    # Permission check: Caller must be HEAD, DEPUTY, or have 'can_manage_members'
    user_role = getattr(profile, "household_role", "MEMBER")
    if profile.household_relationship == "Head of Household":
        user_role = "HEAD"
    user_tasks = parse_assigned_tasks(getattr(profile, "assigned_tasks", "[]"))
    if user_role not in ("HEAD", "DEPUTY") and "can_manage_members" not in user_tasks:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your assigned household role is not authorized to request member linkages. Authorization from the Head of Household is required."
        )

    # Locate target citizen
    target_ident = payload.target_citizen_code.strip()
    target = db.query(CitizenProfile).filter(
        (CitizenProfile.citizen_code == target_ident.upper()) |
        (CitizenProfile.phone_number == target_ident)
    ).first()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen with code or phone '{target_ident}' was not found in the civil registry."
        )

    if target.id == profile.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot submit a member linkage request for yourself."
        )

    if target.household_id == profile.household_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{target.full_name} ({target.citizen_code}) is already an active member of this household."
        )

    # Check for existing pending request
    existing_req = db.query(HouseholdLinkRequest).filter(
        HouseholdLinkRequest.household_id == profile.household_id,
        HouseholdLinkRequest.target_citizen_id == target.id,
        HouseholdLinkRequest.status == LinkRequestStatus.PENDING.value
    ).first()
    if existing_req:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A linkage request for {target.full_name} is already pending administrator approval."
        )

    # Create link request with user-specified relationship, role, and tasks
    clean_rel = payload.relationship.strip()
    clean_role = payload.household_role.strip().upper()
    if clean_role not in ("HEAD", "DEPUTY", "MEMBER", "DEPENDENT"):
        clean_role = "MEMBER"

    tasks_json = json.dumps(payload.assigned_tasks)

    link_req = HouseholdLinkRequest(
        household_id=profile.household_id,
        requester_citizen_id=profile.id,
        target_citizen_id=target.id,
        relationship=clean_rel,
        household_role=clean_role,
        assigned_tasks=tasks_json,
        status=LinkRequestStatus.PENDING.value
    )
    db.add(link_req)
    db.commit()
    db.refresh(link_req)

    record_audit_log(
        db=db,
        actor=profile.user,
        action="HOUSEHOLD_LINK_REQUEST_SUBMITTED",
        resource_type="household_link_request",
        resource_id=str(link_req.id),
        details={
            "household_id": profile.household_id,
            "target_code": target.citizen_code,
            "user_specified_relationship": clean_rel,
            "role": clean_role,
            "tasks": payload.assigned_tasks
        }
    )

    return _build_link_request_response(link_req)


@router.get("/me/link-requests", response_model=List[HouseholdLinkRequestResponse])
def get_my_household_link_requests(
    profile: CitizenProfile = Depends(get_current_citizen_profile),
    db: Session = Depends(get_db)
):
    """
    Retrieve linkage requests submitted for the authenticated citizen's household.
    """
    if not profile.household_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not linked to any household."
        )

    requests = (
        db.query(HouseholdLinkRequest)
        .filter(HouseholdLinkRequest.household_id == profile.household_id)
        .order_by(HouseholdLinkRequest.created_at.desc())
        .all()
    )
    return [_build_link_request_response(r) for r in requests]


# ==========================================
# ADMINISTRATOR HOUSEHOLD ENDPOINTS
# ==========================================

@router.get("", response_model=List[AdminHouseholdResponse])
def list_households(
    search: Optional[str] = Query(None, description="Search by code, locality, city, or address"),
    administrative_unit_id: Optional[int] = Query(None, description="Filter by administrative unit"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-018: List households with member summaries, consistency flags, and duplicate warnings.
    FR-ADM-022: Enforces administrative jurisdiction scope.
    """
    query = db.query(Household)

    # Scope enforcement
    if current_admin.administrative_unit_id is not None:
        allowed_ids = get_descendant_unit_ids(db, current_admin.administrative_unit_id)
        query = query.filter(Household.administrative_unit_id.in_(allowed_ids))

    if administrative_unit_id is not None:
        query = query.filter(Household.administrative_unit_id == administrative_unit_id)

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
    return [_build_admin_household_response(hh, db) for hh in households]


@router.post("", response_model=AdminHouseholdResponse, status_code=status.HTTP_201_CREATED)
def create_household(
    payload: AdminHouseholdCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-014: Create a household with unique ID and permitted attributes.
    FR-ADM-020: Warns about likely duplicate households using matching address & postal code.
    FR-ADM-022: Scoped admin can only create households in their jurisdiction.
    """
    if payload.administrative_unit_id:
        enforce_admin_scope(current_admin, payload.administrative_unit_id, db, "administrative jurisdiction")
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == payload.administrative_unit_id).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrative unit not found.")
    elif current_admin.administrative_unit_id is not None:
        payload.administrative_unit_id = current_admin.administrative_unit_id

    code = payload.household_code or generate_household_code()
    existing = db.query(Household).filter(Household.household_code == code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Household code '{code}' already exists."
        )

    # Check for duplicate warning (FR-ADM-020)
    has_dup, matching_codes = check_duplicate_households(db, payload.address_line, payload.postal_code)

    new_hh = Household(
        household_code=code,
        address_line=payload.address_line,
        locality=payload.locality,
        city=payload.city,
        state=payload.state,
        postal_code=payload.postal_code,
        administrative_unit_id=payload.administrative_unit_id,
        administrative_notes=payload.administrative_notes,
    )
    db.add(new_hh)
    db.flush()

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_CREATE",
        resource_type="household",
        resource_id=new_hh.household_code,
        details={"address": f"{new_hh.address_line}, {new_hh.city}", "duplicate_warning": has_dup}
    )

    event = OutboxEvent.create(
        event_type="HOUSEHOLD_CREATED",
        aggregate_type="household",
        aggregate_id=new_hh.household_code,
        payload={"household_code": new_hh.household_code, "city": new_hh.city}
    )
    db.add(event)
    db.commit()
    db.refresh(new_hh)

    return _build_admin_household_response(new_hh, db)


@router.get("/link-requests", response_model=List[HouseholdLinkRequestResponse])
def list_household_link_requests(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending_admin_approval, approved, rejected"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Teacher Feedback Requirement:
    - Lists family member linkage requests submitted by citizens.
    - Admin reviews requests within their administrative jurisdiction.
    """
    query = db.query(HouseholdLinkRequest).join(Household, HouseholdLinkRequest.household_id == Household.id)

    if current_admin.administrative_unit_id is not None:
        allowed_ids = get_descendant_unit_ids(db, current_admin.administrative_unit_id)
        query = query.filter(Household.administrative_unit_id.in_(allowed_ids))

    if status_filter:
        query = query.filter(HouseholdLinkRequest.status == status_filter)

    requests = query.order_by(HouseholdLinkRequest.created_at.desc()).all()
    return [_build_link_request_response(r) for r in requests]


@router.post("/link-requests/{request_id}/action", response_model=HouseholdLinkRequestResponse)
def review_household_link_request(
    request_id: int,
    payload: HouseholdLinkActionRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Teacher Feedback Requirement:
    - Admin strictly acts as an approval/activation gate (ACCEPT or REJECT only).
    - The admin will NOT select or assign roles.
    - The admin will NOT mutate the user-specified relationship.
    - Follows administrative scope and functional requirements.
    """
    req = db.query(HouseholdLinkRequest).filter(HouseholdLinkRequest.id == request_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household link request not found."
        )

    household = db.query(Household).filter(Household.id == req.household_id).first()
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated household not found."
        )

    enforce_admin_scope(current_admin, household.administrative_unit_id, db, "household link request")

    if req.status != LinkRequestStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request has already been finalized with status '{req.status}'."
        )

    now_utc = datetime.now(timezone.utc)

    if payload.action == "approve":
        # Activate target citizen into the household with USER-SPECIFIED relationship & role
        target = db.query(CitizenProfile).filter(CitizenProfile.id == req.target_citizen_id).first()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target citizen profile not found."
            )

        # End any previous active membership if previously linked
        prev_memberships = db.query(HouseholdMembership).filter(
            HouseholdMembership.citizen_id == target.id,
            HouseholdMembership.status == MembershipStatus.ACTIVE.value
        ).all()
        for pm in prev_memberships:
            pm.status = MembershipStatus.ENDED.value
            pm.end_date = date.today()
            pm.notes = f"Reassigned to household {household.household_code}"

        # Assign with user-specified relationship & role
        target.household_id = household.id
        target.household_relationship = req.relationship
        target.household_role = req.household_role
        target.assigned_tasks = req.assigned_tasks

        # Create active membership history record
        new_membership = HouseholdMembership(
            household_id=household.id,
            citizen_id=target.id,
            relationship_type=req.relationship,
            start_date=date.today(),
            status=MembershipStatus.ACTIVE.value,
            notes="Activated via citizen link request approval",
        )
        db.add(new_membership)

        req.status = LinkRequestStatus.APPROVED.value
        req.admin_notes = payload.admin_notes or "Approved by administrator"
        req.reviewed_by_admin_id = current_admin.id
        req.reviewed_at = now_utc

        record_audit_log(
            db=db,
            actor=current_admin,
            action="HOUSEHOLD_LINK_REQUEST_APPROVED",
            resource_type="household_link_request",
            resource_id=str(req.id),
            details={
                "household_code": household.household_code,
                "target_code": target.citizen_code,
                "relationship": req.relationship,
                "role": req.household_role
            }
        )

        event = OutboxEvent.create(
            event_type="HOUSEHOLD_MEMBER_LINKED",
            aggregate_type="household",
            aggregate_id=household.household_code,
            payload={
                "household_code": household.household_code,
                "citizen_code": target.citizen_code,
                "relationship": req.relationship,
                "role": req.household_role
            }
        )
        db.add(event)

    elif payload.action == "reject":
        req.status = LinkRequestStatus.REJECTED.value
        req.admin_notes = payload.admin_notes or "Rejected by administrator"
        req.reviewed_by_admin_id = current_admin.id
        req.reviewed_at = now_utc

        record_audit_log(
            db=db,
            actor=current_admin,
            action="HOUSEHOLD_LINK_REQUEST_REJECTED",
            resource_type="household_link_request",
            resource_id=str(req.id),
            details={
                "household_code": household.household_code,
                "reason": payload.admin_notes
            }
        )

    db.commit()
    db.refresh(req)
    return _build_link_request_response(req)


@router.get("/{household_id}", response_model=AdminHouseholdResponse)
def get_household_by_id(
    household_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-018: Detail view of household with member summaries and consistency flags.
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household")
    return _build_admin_household_response(hh, db)


@router.put("/{household_id}", response_model=AdminHouseholdResponse)
def update_household(
    household_id: int,
    payload: AdminHouseholdUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only update of household address, administrative unit, and notes."""
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household")

    if payload.administrative_unit_id is not None:
        enforce_admin_scope(current_admin, payload.administrative_unit_id, db, "target administrative unit")
        unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == payload.administrative_unit_id).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target administrative unit does not exist.")

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

    return _build_admin_household_response(hh, db)


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

    enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household")

    code = hh.household_code
    # Unlink active members
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
    FR-ADM-015: Associate existing citizen with household and relationship type.
    FR-ADM-016: Maintain membership history in HouseholdMembership log.
    FR-ADM-017: Reject nonexistent citizen references and unsupported relationship values.
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found."
        )

    enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household")

    # FR-ADM-017: Validate citizen existence
    citizen = db.query(CitizenProfile).filter(CitizenProfile.id == payload.citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen profile not found."
        )

    enforce_admin_scope(current_admin, citizen.administrative_unit_id, db, "citizen profile")

    # FR-ADM-017: Validate supported relationship values
    clean_rel = (payload.household_relationship or "Member").strip()
    if clean_rel not in ALLOWED_RELATIONSHIPS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported relationship '{clean_rel}'. Allowed relationships: {', '.join(ALLOWED_RELATIONSHIPS)}"
        )

    # FR-ADM-016: End previous active membership history if citizen was previously assigned elsewhere
    existing_memberships = db.query(HouseholdMembership).filter(
        HouseholdMembership.citizen_id == citizen.id,
        HouseholdMembership.status == MembershipStatus.ACTIVE.value
    ).all()

    for em in existing_memberships:
        em.status = MembershipStatus.ENDED.value
        em.end_date = date.today()
        em.notes = f"Reassigned to household {hh.household_code}"

    # Create new active membership record
    new_mem = HouseholdMembership(
        household_id=hh.id,
        citizen_id=citizen.id,
        relationship_type=clean_rel,
        start_date=date.today(),
        status=MembershipStatus.ACTIVE.value,
        notes="Administrative assignment",
    )
    db.add(new_mem)

    # Update citizen profile link
    citizen.household_id = hh.id
    citizen.household_relationship = clean_rel
    db.commit()
    db.refresh(citizen)

    # Record audit log & domain event
    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_MEMBER_ASSIGN",
        resource_type="household",
        resource_id=hh.household_code,
        details={"citizen_code": citizen.citizen_code, "relationship": clean_rel}
    )

    event = OutboxEvent.create(
        event_type="HOUSEHOLD_MEMBER_ASSIGNED",
        aggregate_type="household",
        aggregate_id=hh.household_code,
        payload={"citizen_code": citizen.citizen_code, "household_code": hh.household_code, "role": clean_rel}
    )
    db.add(event)
    db.commit()

    return _build_admin_household_response(hh, db)


@router.post("/{household_id}/members/{citizen_id}/end", response_model=AdminHouseholdResponse)
@router.post("/{household_id}/end-membership/{citizen_id}", response_model=AdminHouseholdResponse)
def end_household_membership(
    household_id: int,
    citizen_id: int,
    payload: HouseholdMembershipEndRequest = HouseholdMembershipEndRequest(),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-016: End a citizen's membership in a household while retaining history.
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found.")

    enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household")

    citizen = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not citizen or citizen.household_id != hh.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citizen is not an active member of this household.")

    # Retain history in HouseholdMembership
    active_mem = db.query(HouseholdMembership).filter(
        HouseholdMembership.household_id == hh.id,
        HouseholdMembership.citizen_id == citizen.id,
        HouseholdMembership.status == MembershipStatus.ACTIVE.value
    ).first()

    end_d = payload.end_date or date.today()
    if active_mem:
        active_mem.status = MembershipStatus.ENDED.value
        active_mem.end_date = end_d
        active_mem.notes = payload.notes or "Membership ended by administrator"
    else:
        # Create historical record of ended membership
        ended_mem = HouseholdMembership(
            household_id=hh.id,
            citizen_id=citizen.id,
            relationship_type=citizen.household_relationship or "Member",
            start_date=citizen.created_at.date() if citizen.created_at else date.today(),
            end_date=end_d,
            status=MembershipStatus.ENDED.value,
            notes=payload.notes or "Membership ended",
        )
        db.add(ended_mem)

    # Unlink citizen from current dwelling
    old_role = citizen.household_relationship
    citizen.household_id = None
    citizen.household_relationship = None
    db.commit()

    record_audit_log(
        db=db,
        actor=current_admin,
        action="HOUSEHOLD_MEMBER_END",
        resource_type="household",
        resource_id=hh.household_code,
        details={"citizen_code": citizen.citizen_code, "ended_role": old_role}
    )

    event = OutboxEvent.create(
        event_type="HOUSEHOLD_MEMBER_ENDED",
        aggregate_type="household",
        aggregate_id=hh.household_code,
        payload={"citizen_code": citizen.citizen_code, "household_code": hh.household_code}
    )
    db.add(event)
    db.commit()

    return _build_admin_household_response(hh, db)


@router.get("/{household_id}/history", response_model=List[HouseholdMembershipResponse])
@router.get("/{household_id}/memberships", response_model=List[HouseholdMembershipResponse])
def get_household_membership_history(
    household_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    FR-ADM-016: Retrieve complete membership audit history (active and past members).
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found.")

    enforce_admin_scope(current_admin, hh.administrative_unit_id, db, "household")

    records = (
        db.query(HouseholdMembership)
        .filter(HouseholdMembership.household_id == hh.id)
        .order_by(HouseholdMembership.created_at.desc())
        .all()
    )

    results = []
    for r in records:
        citizen_name = r.citizen.full_name if r.citizen else "Unknown Citizen"
        citizen_code = r.citizen.citizen_code if r.citizen else "N/A"
        results.append(
            HouseholdMembershipResponse(
                id=r.id,
                household_id=r.household_id,
                citizen_id=r.citizen_id,
                citizen_code=citizen_code,
                citizen_name=citizen_name,
                relationship_type=r.relationship_type,
                start_date=r.start_date,
                end_date=r.end_date,
                status=r.status,
                notes=r.notes,
                created_at=r.created_at,
            )
        )
    return results


@router.delete("/{household_id}/members/{citizen_id}", response_model=AdminHouseholdResponse)
@router.post("/{household_id}/unassign/{citizen_id}", response_model=AdminHouseholdResponse)
def remove_member_from_household(
    household_id: int,
    citizen_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Convenience alias for ending a citizen's membership in a household.
    """
    return end_household_membership(
        household_id=household_id,
        citizen_id=citizen_id,
        current_admin=current_admin,
        db=db
    )
