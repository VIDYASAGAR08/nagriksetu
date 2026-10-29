def test_citizen_household_privacy_protection(client, db_session, citizen_token, citizen_user, test_household, second_citizen_user):
    # Assign citizen_user and second_citizen_user to test_household
    citizen_user.citizen_profile.household_id = test_household.id
    citizen_user.citizen_profile.household_relationship = "Head of Household"
    second_citizen_user.citizen_profile.household_id = test_household.id
    second_citizen_user.citizen_profile.household_relationship = "Spouse"
    db_session.commit()

    headers = {"Authorization": f"Bearer {citizen_token}"}
    res = client.get("/api/v1/households/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["household_code"] == test_household.household_code
    assert data["city"] == test_household.city
    
    # PRIVACY VERIFICATION:
    # 1. administrative_notes must NOT be present in citizen response
    assert "administrative_notes" not in data
    # 2. Members list should have summaries without private emails/phone numbers
    assert len(data["members"]) == 2
    for m in data["members"]:
        assert "phone_number" not in m
        assert "email" not in m
        assert "full_name" in m
        assert "citizen_code" in m
        assert "household_relationship" in m


def test_citizen_without_household_returns_404(client, citizen_token, citizen_user, db_session):
    citizen_user.citizen_profile.household_id = None
    db_session.commit()

    headers = {"Authorization": f"Bearer {citizen_token}"}
    res = client.get("/api/v1/households/me", headers=headers)
    assert res.status_code == 404


def test_citizen_forbidden_admin_household_routes(client, citizen_token, test_household):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    # Attempt to list admin households
    res1 = client.get("/api/v1/households", headers=headers)
    assert res1.status_code == 403

    # Attempt to create household
    res2 = client.post("/api/v1/households", json={"address_line": "123", "locality": "L", "city": "C", "state": "S", "postal_code": "P"}, headers=headers)
    assert res2.status_code == 403

    # Attempt to assign member
    res3 = client.post(f"/api/v1/households/{test_household.id}/assign", json={"citizen_id": 1}, headers=headers)
    assert res3.status_code == 403


def test_admin_create_and_manage_household(client, admin_token, citizen_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create Household
    payload = {
        "household_code": "HHD-NEW-TEST",
        "address_line": "456 Residency Rd",
        "locality": "Central",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560025",
        "administrative_notes": "Official audit scheduled for Q3."
    }
    res_create = client.post("/api/v1/households", json=payload, headers=headers)
    assert res_create.status_code == 201
    hh_data = res_create.json()
    assert hh_data["household_code"] == "HHD-NEW-TEST"
    assert hh_data["administrative_notes"] == "Official audit scheduled for Q3."
    hh_id = hh_data["id"]

    # 2. Duplicate household code test
    res_dup = client.post("/api/v1/households", json=payload, headers=headers)
    assert res_dup.status_code == 409

    # 3. Assign citizen to household
    res_assign = client.post(
        f"/api/v1/households/{hh_id}/assign",
        json={"citizen_id": citizen_user.citizen_profile.id, "household_relationship": "Head of Household"},
        headers=headers
    )
    assert res_assign.status_code == 200
    assert len(res_assign.json()["members"]) == 1

    # 4. Unassign citizen from household
    res_unassign = client.post(
        f"/api/v1/households/{hh_id}/unassign/{citizen_user.citizen_profile.id}",
        headers=headers
    )
    assert res_unassign.status_code == 200
    assert len(res_unassign.json()["members"]) == 0

    # 5. Delete household
    res_del = client.delete(f"/api/v1/households/{hh_id}", headers=headers)
    assert res_del.status_code == 200
    assert "deleted successfully" in res_del.json()["message"]
