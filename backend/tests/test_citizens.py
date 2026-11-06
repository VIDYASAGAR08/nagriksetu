def test_citizen_get_own_profile(client, citizen_token, citizen_user):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    res = client.get("/api/v1/citizens/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["citizen_code"] == citizen_user.citizen_profile.citizen_code
    assert data["full_name"] == citizen_user.citizen_profile.full_name


def test_citizen_update_own_profile(client, citizen_token, citizen_user):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    payload = {
        "full_name": "Updated Citizen One",
        "phone_number": "+91 99999 88888",
        "preferred_language": "hi"
    }

    # 1. Update without OTP must be blocked (FR-ADM-008 & Privacy Policy)
    blocked_res = client.patch("/api/v1/citizens/me", json=payload, headers=headers)
    assert blocked_res.status_code == 403
    assert "OTP verification is mandatory" in blocked_res.json()["detail"]

    # 2. Generate OTP
    otp_gen = client.post("/api/v1/auth/otp/generate", json={"purpose": "CITIZEN_PROFILE_UPDATE"}, headers=headers)
    assert otp_gen.status_code == 200
    otp_data = otp_gen.json()
    ref_id = otp_data["reference_id"]
    demo_code = otp_data["demo_hint"]

    # 3. Verify OTP
    otp_ver = client.post("/api/v1/auth/otp/verify", json={
        "reference_id": ref_id,
        "otp_code": demo_code,
        "purpose": "CITIZEN_PROFILE_UPDATE"
    })
    assert otp_ver.status_code == 200
    assert otp_ver.json()["verified"] is True

    # 4. Perform update with verified OTP reference token
    payload["otp_reference_id"] = ref_id
    res = client.patch("/api/v1/citizens/me", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Updated Citizen One"
    assert data["phone_number"] == "+91 99999 88888"
    assert data["preferred_language"] == "hi"


def test_citizen_cannot_access_admin_citizen_list(client, citizen_token):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    res = client.get("/api/v1/citizens", headers=headers)
    # Must be forbidden with 403
    assert res.status_code == 403


def test_admin_list_and_search_citizens(client, admin_token, citizen_user, second_citizen_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/citizens", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2

    # Search by name
    res_search = client.get("/api/v1/citizens?search=Citizen One", headers=headers)
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert len(search_data) == 1
    assert search_data[0]["citizen_code"] == citizen_user.citizen_profile.citizen_code


def test_admin_create_citizen(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "full_name": "New Admin Created Citizen",
        "email": "new.citizen@example.com",
        "initial_password": "NewCitizen123!@",
        "phone_number": "+91 88888 22222",
        "preferred_language": "en",
        "profile_status": "pending_review"
    }
    res = client.post("/api/v1/citizens", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["full_name"] == "New Admin Created Citizen"
    assert data["profile_status"] == "pending_review"
    assert data["citizen_code"].startswith("CIT-")


def test_admin_update_citizen_status(client, admin_token, citizen_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    profile_id = citizen_user.citizen_profile.id
    payload = {"profile_status": "archived"}
    res = client.patch(f"/api/v1/citizens/{profile_id}/status", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["profile_status"] == "archived"


def test_admin_delete_citizen(client, admin_token, second_citizen_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    profile_id = second_citizen_user.citizen_profile.id
    res = client.delete(f"/api/v1/citizens/{profile_id}", headers=headers)
    assert res.status_code == 200
    assert "deleted successfully" in res.json()["message"]

    # Verify not found afterwards
    res_check = client.get(f"/api/v1/citizens/{profile_id}", headers=headers)
    assert res_check.status_code == 404
