import pytest
from app.models.user import User, UserRole, UserStatus
from app.models.hierarchy import AdministrativeUnit, AdministrativeUnitType, AdministrativeUnitStatus
from app.models.citizen import CitizenProfile
from app.models.household import Household
from app.core.security import hash_password, create_access_token


@pytest.fixture
def scoped_admin_user(db_session):
    # Create Karnataka and Bengaluru units
    state_unit = AdministrativeUnit(
        identifier="IN-TEST-KA",
        name="Karnataka Test",
        unit_type=AdministrativeUnitType.STATE.value,
        status="active"
    )
    db_session.add(state_unit)
    db_session.flush()

    blr_unit = AdministrativeUnit(
        identifier="IN-TEST-BLR",
        name="Bengaluru Test",
        unit_type=AdministrativeUnitType.DISTRICT.value,
        parent_id=state_unit.id,
        status="active"
    )
    db_session.add(blr_unit)
    db_session.flush()

    admin = User(
        email="blr.admin@nagriksetu.gov.in",
        password_hash=hash_password("AdminPass123!@#"),
        role=UserRole.ADMIN.value,
        account_status=UserStatus.ACTIVE.value,
        administrative_unit_id=blr_unit.id,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin, blr_unit, state_unit


@pytest.fixture
def scoped_admin_token(scoped_admin_user):
    admin, _, _ = scoped_admin_user
    return create_access_token({"sub": str(admin.id), "role": admin.role})


def test_hierarchy_crud_and_validation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # FR-ADM-001: Create root unit
    payload_root = {
        "identifier": "IN-DEL",
        "name": "Delhi National Capital Territory",
        "unit_type": "state",
        "status": "active"
    }
    res_root = client.post("/api/v1/hierarchy/units", json=payload_root, headers=headers)
    assert res_root.status_code == 201
    root_data = res_root.json()
    assert root_data["identifier"] == "IN-DEL"
    assert root_data["name"] == "Delhi National Capital Territory"
    root_id = root_data["id"]

    # FR-ADM-003: Duplicate identifier rejection
    res_dup = client.post("/api/v1/hierarchy/units", json=payload_root, headers=headers)
    assert res_dup.status_code == 409

    # FR-ADM-001: Create child unit
    payload_child = {
        "identifier": "IN-DEL-ND",
        "name": "New Delhi District",
        "unit_type": "district",
        "parent_id": root_id,
        "status": "active"
    }
    res_child = client.post("/api/v1/hierarchy/units", json=payload_child, headers=headers)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # FR-ADM-003: Circular parent-child link rejection
    # Attempt to make root unit's parent its own child!
    res_circular = client.patch(
        f"/api/v1/hierarchy/units/{root_id}",
        json={"parent_id": child_id},
        headers=headers
    )
    assert res_circular.status_code == 422
    assert "Circular parent-child link" in res_circular.json()["detail"]

    # FR-ADM-003: Self-parenting rejection
    res_self = client.patch(
        f"/api/v1/hierarchy/units/{root_id}",
        json={"parent_id": root_id},
        headers=headers
    )
    assert res_self.status_code == 422

    # FR-ADM-002 & FR-ADM-005: List & Search
    res_list = client.get("/api/v1/hierarchy/units?search=Delhi", headers=headers)
    assert res_list.status_code == 200
    assert res_list.json()["total"] >= 2

    # FR-ADM-004: Deactivate unit
    res_deactivate = client.patch(
        f"/api/v1/hierarchy/units/{child_id}",
        json={"status": "inactive"},
        headers=headers
    )
    assert res_deactivate.status_code == 200
    assert res_deactivate.json()["status"] == "inactive"


def test_scope_enforcement_and_overview(client, scoped_admin_user, scoped_admin_token, db_session):
    admin, blr_unit, state_unit = scoped_admin_user
    headers = {"Authorization": f"Bearer {scoped_admin_token}"}

    # FR-ADM-023: Admin overview metrics within scope
    res_dash = client.get("/api/v1/admin/dashboard", headers=headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "Bengaluru Test" in dash_data["admin_scope"]
    assert dash_data["admin_scope_unit_id"] == blr_unit.id

    # FR-ADM-022: Scoped admin attempting to modify outside scope (state unit)
    res_outside = client.patch(
        f"/api/v1/hierarchy/units/{state_unit.id}",
        json={"name": "Tampered Outside Scope"},
        headers=headers
    )
    assert res_outside.status_code == 403
    assert "outside your assigned administrative jurisdiction" in res_outside.json()["detail"]


def test_citizen_completeness_and_missing_fields(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create citizen with minimal fields
    payload = {
        "full_name": "Incomplete Citizen",
        "email": "incomplete@example.com",
        "phone_number": "",  # missing phone
        "date_of_birth": None,  # missing dob
        "household_id": None,  # missing household
    }
    res = client.post("/api/v1/citizens", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["completeness_score"] < 100
    assert "Phone Number" in data["missing_fields"]
    assert "Date of Birth" in data["missing_fields"]
    assert "Household Link" in data["missing_fields"]


def test_household_consistency_and_duplicate_warning(client, admin_token, db_session):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # FR-ADM-014 & FR-ADM-020: Create first household
    payload1 = {
        "household_code": "HHD-DUP-1",
        "address_line": "777 MG Road",
        "locality": "Central",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560001",
    }
    res1 = client.post("/api/v1/households", json=payload1, headers=headers)
    assert res1.status_code == 201
    hh1_id = res1.json()["id"]

    # FR-ADM-019: Consistency flag on empty household
    res_detail = client.get(f"/api/v1/households/{hh1_id}", headers=headers)
    assert res_detail.status_code == 200
    flags = res_detail.json()["consistency_flags"]
    assert any("EMPTY_HOUSEHOLD" in f for f in flags)

    # FR-ADM-020: Create second household with same address and postal code
    payload2 = {
        "household_code": "HHD-DUP-2",
        "address_line": "777 MG Road",
        "locality": "Central",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560001",
    }
    res2 = client.post("/api/v1/households", json=payload2, headers=headers)
    assert res2.status_code == 201
    assert res2.json()["duplicate_warning"] is True
    assert "HHD-DUP-1" in res2.json()["matching_households"]


def test_household_membership_history_and_validation(client, admin_token, citizen_user):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create household
    res_hh = client.post(
        "/api/v1/households",
        json={
            "household_code": "HHD-HIST-TEST",
            "address_line": "100 Brigade Rd",
            "locality": "Ashok Nagar",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560025",
        },
        headers=headers
    )
    hh_id = res_hh.json()["id"]

    # FR-ADM-017: Unsupported relationship rejection
    res_invalid_rel = client.post(
        f"/api/v1/households/{hh_id}/assign",
        json={"citizen_id": citizen_user.citizen_profile.id, "household_relationship": "InvalidAlienRelation"},
        headers=headers
    )
    assert res_invalid_rel.status_code == 422

    # FR-ADM-015: Valid assignment
    res_valid = client.post(
        f"/api/v1/households/{hh_id}/assign",
        json={"citizen_id": citizen_user.citizen_profile.id, "household_relationship": "Head of Household"},
        headers=headers
    )
    assert res_valid.status_code == 200

    # FR-ADM-016: Retrieve membership history
    res_hist = client.get(f"/api/v1/households/{hh_id}/history", headers=headers)
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert len(history) >= 1
    assert history[0]["status"] == "active"
    assert history[0]["relationship_type"] == "Head of Household"

    # End membership
    res_end = client.post(f"/api/v1/households/{hh_id}/members/{citizen_user.citizen_profile.id}/end", headers=headers)
    assert res_end.status_code == 200
    assert len(res_end.json()["members"]) == 0

    # Verify history now records ended status
    res_hist_after = client.get(f"/api/v1/households/{hh_id}/history", headers=headers)
    assert res_hist_after.json()[0]["status"] == "ended"


def test_domain_events_service_integration(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Trigger a domain event by creating an administrative unit
    client.post(
        "/api/v1/hierarchy/units",
        json={
            "identifier": "IN-EVT-TEST",
            "name": "Event Test District",
            "unit_type": "district",
            "status": "active"
        },
        headers=headers
    )

    # FR-ADM-025: Service integration events outbox endpoint
    res_events = client.get("/api/v1/integrations/events", headers=headers)
    assert res_events.status_code == 200
    events_data = res_events.json()
    assert "items" in events_data
    assert "total" in events_data
    assert events_data["total"] >= 1
    assert any(e["event_type"] == "HIERARCHY_UNIT_CREATED" for e in events_data["items"])
