from typing import List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.hierarchy import AdministrativeUnit
from app.models.citizen import CitizenProfile
from app.models.household import Household


def get_descendant_unit_ids(db: Session, root_unit_id: int) -> Set[int]:
    """
    Returns a set of all unit IDs comprising the root unit and all its children/descendants.
    Used for strict hierarchical scope enforcement (FR-ADM-022).
    """
    descendants: Set[int] = {root_unit_id}
    queue: List[int] = [root_unit_id]

    while queue:
        current_id = queue.pop(0)
        children = db.query(AdministrativeUnit.id).filter(
            AdministrativeUnit.parent_id == current_id
        ).all()
        for (child_id,) in children:
            if child_id not in descendants:
                descendants.add(child_id)
                queue.append(child_id)

    return descendants


def is_within_admin_scope(admin: User, target_unit_id: Optional[int], db: Session) -> bool:
    """Checks whether target_unit_id falls within the administrator's assigned scope."""
    # National / Root scope has unrestricted access
    if admin.administrative_unit_id is None:
        return True

    # If target has no unit and admin is scoped, target is outside this admin's jurisdiction
    if target_unit_id is None:
        return False

    allowed_unit_ids = get_descendant_unit_ids(db, admin.administrative_unit_id)
    return target_unit_id in allowed_unit_ids


def enforce_admin_scope(admin: User, target_unit_id: Optional[int], db: Session, resource_name: str = "resource"):
    """Raises 403 Forbidden if target_unit_id is outside the administrator's assigned scope (FR-ADM-022)."""
    if not is_within_admin_scope(admin, target_unit_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. This {resource_name} is outside your assigned administrative jurisdiction."
        )


def check_circular_hierarchy(db: Session, unit_id: Optional[int], new_parent_id: Optional[int]):
    """
    Prevents circular parent-child links and self-parenting in administrative hierarchy (FR-ADM-003).
    """
    if new_parent_id is None:
        return

    if unit_id is not None and unit_id == new_parent_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="An administrative unit cannot be its own parent."
        )

    parent = db.query(AdministrativeUnit).filter(AdministrativeUnit.id == new_parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent administrative unit with ID {new_parent_id} does not exist."
        )

    # Check ancestors for circular links
    if unit_id is not None:
        visited: Set[int] = set()
        curr = parent
        while curr is not None:
            if curr.id == unit_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Circular parent-child link detected in administrative hierarchy."
                )
            if curr.id in visited:
                break
            visited.add(curr.id)
            curr = curr.parent


def calculate_citizen_completeness(profile: CitizenProfile) -> Tuple[int, List[str]]:
    """
    Calculates completeness score and lists missing fields for a citizen profile (FR-ADM-013).
    """
    checks = [
        ("Full Legal Name", bool(profile.full_name and profile.full_name.strip())),
        ("Phone Number", bool(profile.phone_number and profile.phone_number.strip())),
        ("Date of Birth", bool(profile.date_of_birth)),
        ("Preferred Language", bool(profile.preferred_language)),
        ("Household Link", bool(profile.household_id)),
        ("Administrative Jurisdiction", bool(profile.administrative_unit_id)),
    ]

    missing = [name for name, passed in checks if not passed]
    score = int(((len(checks) - len(missing)) / len(checks)) * 100)
    return score, missing


def audit_household_consistency(household: Household, db: Session) -> List[str]:
    """
    Audits household members for consistency and flags contradictory records (FR-ADM-019).
    """
    flags: List[str] = []
    members = household.members or []

    if not members:
        flags.append("EMPTY_HOUSEHOLD: No citizens currently linked to this dwelling.")
        return flags

    head_count = 0
    unassigned_count = 0

    for m in members:
        rel = (m.household_relationship or "").strip().lower()
        if not rel:
            unassigned_count += 1
        elif "head" in rel:
            head_count += 1

    if head_count == 0:
        flags.append("NO_HEAD_OF_HOUSEHOLD: Household has verified members but no designated Head of Household.")
    elif head_count > 1:
        flags.append(f"MULTIPLE_HEADS_OF_HOUSEHOLD: Found {head_count} members designated as Head of Household.")

    if unassigned_count > 0:
        flags.append(f"UNASSIGNED_RELATIONSHIP: {unassigned_count} member(s) have unclassified household relationships.")

    return flags


def check_duplicate_households(
    db: Session,
    address_line: str,
    postal_code: str,
    exclude_id: Optional[int] = None
) -> Tuple[bool, List[str]]:
    """
    Identifies likely duplicate households using normalized address and postal code (FR-ADM-020).
    """
    clean_addr = address_line.strip().lower()
    clean_zip = postal_code.strip()

    query = db.query(Household).filter(Household.postal_code == clean_zip)
    if exclude_id is not None:
        query = query.filter(Household.id != exclude_id)

    candidates = query.all()
    matching_codes: List[str] = []

    for c in candidates:
        if c.address_line.strip().lower() == clean_addr:
            matching_codes.append(c.household_code)

    return (len(matching_codes) > 0, matching_codes)
