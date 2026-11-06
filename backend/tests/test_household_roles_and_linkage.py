import pytest
from app.models.household import Household, HouseholdMembership, HouseholdLinkRequest, LinkRequestStatus
from app.models.citizen import CitizenProfile
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password


def test_household_link_request_and_admin_accept_reject(client, db_session, admin_user, admin_token):
    """
    Teacher Feedback Verification:
    - User explicitly specifies relationship, role, and assigned task capabilities.
    - System or admin does NOT auto-assign or mutate them.
    - Admin strictly acts as accept or reject gate.
    """
    # 1. Create a Household and Head Citizen
    hh = Household(
        household_code="HHD-TEACHER-DEMO-01",
        address_line="74 Rajpath Vista",
        locality="Central Sector",
        city="New Delhi",
        state="Delhi",
        postal_code="110001",
    )
    db_session.add(hh)
    db_session.flush()

    head_user = User(
        email="head.citizen@nagriksetu.gov.in",
        password_hash=hash_password("CitizenPass123!@"),
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value
    )
    db_session.add(head_user)
    db_session.flush()

    head_profile = CitizenProfile(
        user_id=head_user.id,
        citizen_code="CTZ-HEAD001",
        full_name="Rajesh Sharma (Head)",
        household_id=hh.id,
        household_relationship="Head of Household",
        household_role="HEAD",
        assigned_tasks='["can_manage_assets", "can_manage_medical", "can_manage_education", "can_manage_members", "can_pay_taxes"]'
    )
    db_session.add(head_profile)

    # 2. Create Target Citizen (Son) who is currently unlinked
    son_user = User(
        email="son.sharma@nagriksetu.gov.in",
        password_hash=hash_password("CitizenPass123!@"),
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value
    )
    db_session.add(son_user)
    db_session.flush()

    son_profile = CitizenProfile(
        user_id=son_user.id,
        citizen_code="CTZ-SON002",
        full_name="Amit Sharma (Son)",
        household_id=None,
        household_relationship=None,
        household_role="MEMBER"
    )
    db_session.add(son_profile)
    db_session.commit()

    # Login as Head Citizen
    login_res = client.post("/api/v1/auth/login", json={
        "email": head_user.email,
        "password": "CitizenPass123!@"
    })
    assert login_res.status_code == 200
    head_token = login_res.json()["access_token"]
    head_headers = {"Authorization": f"Bearer {head_token}"}

    # 3. Head citizen submits link request with user-specified relationship "Son" and specific tasks
    link_res = client.post("/api/v1/households/me/link-requests", headers=head_headers, json={
        "target_citizen_code": "CTZ-SON002",
        "relationship": "Son",
        "household_role": "MEMBER",
        "assigned_tasks": ["can_manage_medical", "can_pay_taxes"]
    })
    assert link_res.status_code == 201
    link_data = link_res.json()
    assert link_data["relationship"] == "Son"
    assert link_data["household_role"] == "MEMBER"
    assert "can_manage_medical" in link_data["assigned_tasks"]
    assert link_data["status"] == "pending_admin_approval"
    req_id = link_data["id"]

    # 4. Admin lists pending link requests
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    list_reqs = client.get("/api/v1/households/link-requests", headers=admin_headers)
    assert list_reqs.status_code == 200
    pending_list = [r for r in list_reqs.json() if r["id"] == req_id]
    assert len(pending_list) == 1
    assert pending_list[0]["target_citizen_name"] == "Amit Sharma (Son)"
    assert pending_list[0]["relationship"] == "Son"

    # 5. Admin approves request: linkage is activated with user-specified data
    approve_res = client.post(
        f"/api/v1/households/link-requests/{req_id}/action",
        headers=admin_headers,
        json={"action": "approve", "admin_notes": "Verified civil identity and relation."}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

    # Verify target citizen is now in household with user-specified relationship and tasks
    db_session.refresh(son_profile)
    assert son_profile.household_id == hh.id
    assert son_profile.household_relationship == "Son"
    assert son_profile.household_role == "MEMBER"
    assert "can_manage_medical" in son_profile.assigned_tasks

    # Verify Household membership record was created
    mem = db_session.query(HouseholdMembership).filter(
        HouseholdMembership.household_id == hh.id,
        HouseholdMembership.citizen_id == son_profile.id
    ).first()
    assert mem is not None
    assert mem.relationship_type == "Son"
    assert mem.status == "active"


def test_household_link_request_rejection(client, db_session, admin_token):
    """
    Verify rejection flow:
    - Target citizen remains unlinked when admin rejects.
    """
    hh = Household(
        household_code="HHD-REJECT-DEMO-02",
        address_line="12 Janpath Road",
        locality="North Sector",
        city="New Delhi",
        state="Delhi",
        postal_code="110001",
    )
    db_session.add(hh)
    db_session.flush()

    head_user = User(
        email="head2.citizen@nagriksetu.gov.in",
        password_hash=hash_password("CitizenPass123!@"),
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value
    )
    db_session.add(head_user)
    db_session.flush()

    head_profile = CitizenProfile(
        user_id=head_user.id,
        citizen_code="CTZ-HEAD002",
        full_name="Vikram Verma (Head)",
        household_id=hh.id,
        household_relationship="Head of Household",
        household_role="HEAD",
        assigned_tasks='["can_manage_assets", "can_manage_medical", "can_manage_education", "can_manage_members", "can_pay_taxes"]'
    )
    db_session.add(head_profile)

    target_user = User(
        email="unrelated.user@nagriksetu.gov.in",
        password_hash=hash_password("CitizenPass123!@"),
        role=UserRole.CITIZEN.value,
        account_status=UserStatus.ACTIVE.value
    )
    db_session.add(target_user)
    db_session.flush()

    target_profile = CitizenProfile(
        user_id=target_user.id,
        citizen_code="CTZ-OTHER999",
        full_name="Unrelated Person",
        household_id=None,
        household_relationship=None,
        household_role="MEMBER"
    )
    db_session.add(target_profile)
    db_session.commit()

    # Login as Head
    login_res = client.post("/api/v1/auth/login", json={
        "email": head_user.email,
        "password": "CitizenPass123!@"
    })
    head_token = login_res.json()["access_token"]
    head_headers = {"Authorization": f"Bearer {head_token}"}

    # Submit link request
    req_res = client.post("/api/v1/households/me/link-requests", headers=head_headers, json={
        "target_citizen_code": "CTZ-OTHER999",
        "relationship": "Relative",
        "household_role": "MEMBER",
        "assigned_tasks": []
    })
    assert req_res.status_code == 201
    req_id = req_res.json()["id"]

    # Admin rejects
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    reject_res = client.post(
        f"/api/v1/households/link-requests/{req_id}/action",
        headers=admin_headers,
        json={"action": "reject", "admin_notes": "Not supported by family documentation."}
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"

    # Verify target citizen remains unlinked
    db_session.refresh(target_profile)
    assert target_profile.household_id is None
    assert target_profile.household_relationship is None

