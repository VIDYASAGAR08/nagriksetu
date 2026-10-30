from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.api.deps import get_current_admin, get_current_user
from app.models.user import User
from app.models.hierarchy import AdministrativeUnit, AdministrativeUnitType, AdministrativeUnitStatus
from app.models.citizen import CitizenProfile
from app.models.household import Household
from app.models.event import OutboxEvent
from app.schemas.hierarchy import (
    AdministrativeUnitCreate,
    AdministrativeUnitUpdate,
    AdministrativeUnitResponse,
    AdministrativeUnitListResponse,
)
from app.core.audit import record_audit_log
from app.core.scope import check_circular_hierarchy, is_within_admin_scope, enforce_admin_scope

router = APIRouter(prefix="/hierarchy", tags=["Administrative Hierarchy"])


def _to_unit_response(unit: AdministrativeUnit, db: Session) -> AdministrativeUnitResponse:
    children_cnt = db.query(AdministrativeUnit).filter(AdministrativeUnit.parent_id == unit.id).count()
    citizens_cnt = db.query(CitizenProfile).filter(CitizenProfile.administrative_unit_id == unit.id).count()
    households_cnt = db.query(Household).filter(Household.administrative_unit_id == unit.id).count()

    parent_name = unit.parent.name if unit.parent else None
    parent_ident = unit.parent.identifier if unit.parent else None

    return AdministrativeUnitResponse(
        id=unit.id,
        identifier=unit.identifier,
        name=unit.name,
        unit_type=unit.unit_type,
        parent_id=unit.parent_id,
        parent_name=parent_name,
        parent_identifier=parent_ident,
        status=unit.status,
        created_at=unit.created_at,
        updated_at=unit.updated_at,
        children_count=children_cnt,
        citizens_count=citizens_cnt,
        households_count=households_cnt,
    )


@router.post("", response_model=AdministrativeUnitResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=AdministrativeUnitResponse, status_code=status.HTTP_201_CREATED)
@router.post("/units", response_model=AdministrativeUnitResponse, status_code=status.HTTP_201_CREATED)
def create_administrative_unit(
    payload: AdministrativeUnitCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    FR-ADM-001: Create an administrative unit with identifier, name, unit type, parent, and status.
    FR-ADM-003: Rejects duplicate identifiers, invalid parents, and circular links.
    """
    # 1. Scope check: Scoped admin can only create sub-units inside their assigned jurisdiction
    if admin.administrative_unit_id is not None:
        if payload.parent_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Scoped administrators cannot create root-level administrative units."
            )
        enforce_admin_scope(admin, payload.parent_id, db, "parent administrative unit")

    # 2. Check duplicate identifier
    clean_id = payload.identifier.strip().upper()
    existing = db.query(AdministrativeUnit).filter(AdministrativeUnit.identifier == clean_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Administrative unit identifier '{clean_id}' already exists."
        )

    # 3. Check parent validity and circular links
    if payload.parent_id:
        check_circular_hierarchy(db, unit_id=None, new_parent_id=payload.parent_id)

    # 4. Check unit type validity
    allowed_types = [t.value for t in AdministrativeUnitType]
    clean_type = payload.unit_type.strip().lower()
    if clean_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid unit_type '{clean_type}'. Allowed types: {', '.join(allowed_types)}"
        )

    clean_status = payload.status.strip().lower()
    if clean_status not in ["active", "inactive"]:
        clean_status = "active"

    unit = AdministrativeUnit(
        identifier=clean_id,
        name=payload.name.strip(),
        unit_type=clean_type,
        parent_id=payload.parent_id,
        status=clean_status,
    )
    db.add(unit)
    db.flush()

    # Audit & Domain Event (FR-ADM-024 & FR-ADM-025)
    record_audit_log(
        db=db,
        actor=admin,
        action="CREATE_ADMINISTRATIVE_UNIT",
        resource_type="administrative_unit",
        resource_id=unit.identifier,
        details={"name": unit.name, "unit_type": unit.unit_type, "parent_id": unit.parent_id}
    )

    event = OutboxEvent.create(
        event_type="HIERARCHY_UNIT_CREATED",
        aggregate_type="hierarchy",
        aggregate_id=unit.identifier,
        payload={"id": unit.id, "identifier": unit.identifier, "name": unit.name, "type": unit.unit_type}
    )
    db.add(event)
    db.commit()
    db.refresh(unit)

    return _to_unit_response(unit, db)


@router.get("", response_model=AdministrativeUnitListResponse)
@router.get("/", response_model=AdministrativeUnitListResponse)
@router.get("/units", response_model=AdministrativeUnitListResponse)
def list_administrative_units(
    search: Optional[str] = Query(None, description="Search by name or identifier"),
    unit_type: Optional[str] = Query(None, description="Filter by unit type (state, district, ward, etc.)"),
    parent_id: Optional[int] = Query(None, description="Filter by direct parent unit ID"),
    unit_status: Optional[str] = Query(None, alias="status", description="Filter by active or inactive status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    FR-ADM-002 & FR-ADM-005: Retrieve and search administrative units with filters and pagination.
    Scope-aware for scoped administrators (FR-ADM-022).
    """
    query = db.query(AdministrativeUnit)

    # Scoped admin filter
    if current_user.role == "admin" and current_user.administrative_unit_id is not None:
        from app.core.scope import get_descendant_unit_ids
        allowed_ids = get_descendant_unit_ids(db, current_user.administrative_unit_id)
        query = query.filter(AdministrativeUnit.id.in_(allowed_ids))

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(AdministrativeUnit.name.ilike(s), AdministrativeUnit.identifier.ilike(s)))

    if unit_type:
        query = query.filter(AdministrativeUnit.unit_type == unit_type.strip().lower())

    if parent_id is not None:
        query = query.filter(AdministrativeUnit.parent_id == parent_id)

    if unit_status:
        query = query.filter(AdministrativeUnit.status == unit_status.strip().lower())

    total = query.count()
    units = query.order_by(AdministrativeUnit.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [_to_unit_response(u, db) for u in units]
    return AdministrativeUnitListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{unit_id}", response_model=AdministrativeUnitResponse)
@router.get("/units/{unit_id}", response_model=AdministrativeUnitResponse)
def get_administrative_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-ADM-002: Retrieve an administrative unit with details and counts."""
    unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrative unit not found.")

    if current_user.role == "admin":
        enforce_admin_scope(current_user, unit.id, db, "administrative unit")

    return _to_unit_response(unit, db)


@router.patch("/{unit_id}", response_model=AdministrativeUnitResponse)
@router.patch("/units/{unit_id}", response_model=AdministrativeUnitResponse)
def update_or_deactivate_administrative_unit(
    unit_id: int,
    payload: AdministrativeUnitUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    FR-ADM-004: Update or deactivate a unit without silently deleting historical links.
    FR-ADM-003: Rejects invalid or circular parent-child links.
    """
    unit = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrative unit not found.")

    enforce_admin_scope(admin, unit.id, db, "administrative unit")

    changed_fields = {}

    if payload.name is not None and payload.name.strip():
        new_name = payload.name.strip()
        if new_name != unit.name:
            changed_fields["name"] = {"old": unit.name, "new": new_name}
            unit.name = new_name

    if payload.parent_id is not None:
        if payload.parent_id != unit.parent_id:
            # Check circular link and self-parenting
            check_circular_hierarchy(db, unit_id=unit.id, new_parent_id=payload.parent_id)
            if admin.administrative_unit_id is not None:
                enforce_admin_scope(admin, payload.parent_id, db, "target parent administrative unit")
            changed_fields["parent_id"] = {"old": unit.parent_id, "new": payload.parent_id}
            unit.parent_id = payload.parent_id

    if payload.status is not None:
        new_status = payload.status.strip().lower()
        if new_status in ["active", "inactive"] and new_status != unit.status:
            # Safe deactivation: Retains historical links while marking inactive
            changed_fields["status"] = {"old": unit.status, "new": new_status}
            unit.status = new_status

    if changed_fields:
        record_audit_log(
            db=db,
            actor=admin,
            action="UPDATE_ADMINISTRATIVE_UNIT",
            resource_type="administrative_unit",
            resource_id=unit.identifier,
            details=changed_fields
        )
        event = OutboxEvent.create(
            event_type="HIERARCHY_UNIT_UPDATED",
            aggregate_type="hierarchy",
            aggregate_id=unit.identifier,
            payload={"id": unit.id, "changes": changed_fields}
        )
        db.add(event)
        db.commit()
        db.refresh(unit)

    return _to_unit_response(unit, db)
