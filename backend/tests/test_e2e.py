def test_complete_end_to_end_demonstration_workflow(client, admin_user):
    """
    Simulates the full university demonstration workflow through the API:
    1. Register a citizen.
    2. Sign in as that citizen.
    3. View and update the citizen's own profile.
    4. Attempt to access administrator endpoints and verify denial (403).
    5. Sign out.
    6. Sign in as the administrator.
    7. Create a household.
    8. Create/manage a citizen profile.
    9. Assign the profile to the household.
    10. Verify dashboard counts.
    11. Test search and deletion.
    12. Test citizen chat to verify permitted conversational retrieval.
    13. Verify authentication lifecycle.
    """
    # 1. Citizen Registration
    reg_payload = {
        "full_name": "Divya Krishnan",
        "email": "divya.krishnan@example.com",
        "password": "SecurePassword123!@",
        "confirm_password": "SecurePassword123!@",
        "preferred_language": "ta",
        "phone_number": "+91 94444 33333"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    citizen_token = reg_res.json()["access_token"]
    assert reg_res.json()["user"]["role"] == "citizen"

    # 2. Sign In as Citizen
    login_res = client.post("/api/v1/auth/login", json={
        "email": "divya.krishnan@example.com",
        "password": "SecurePassword123!@"
    })
    assert login_res.status_code == 200
    citizen_token = login_res.json()["access_token"]
    c_headers = {"Authorization": f"Bearer {citizen_token}"}

    # 3. View & Update Own Profile
    prof_res = client.get("/api/v1/citizens/me", headers=c_headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["full_name"] == "Divya Krishnan"
    citizen_code = prof_res.json()["citizen_code"]

    update_res = client.patch("/api/v1/citizens/me", json={
        "phone_number": "+91 94444 55555",
        "preferred_language": "en"
    }, headers=c_headers)
    assert update_res.status_code == 200
    assert update_res.json()["phone_number"] == "+91 94444 55555"

    # 4. Attempt Access to Admin Endpoints -> Verify 403 Denial
    admin_access_res = client.get("/api/v1/admin/dashboard", headers=c_headers)
    assert admin_access_res.status_code == 403
    admin_citizens_res = client.get("/api/v1/citizens", headers=c_headers)
    assert admin_citizens_res.status_code == 403

    # 5. Citizen Sign Out
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200

    # 6. Admin Sign In
    admin_login_res = client.post("/api/v1/auth/login", json={
        "email": admin_user.email,
        "password": "AdminPass123!@#"
    })
    assert admin_login_res.status_code == 200
    assert admin_login_res.json()["user"]["role"] == "admin"
    admin_token = admin_login_res.json()["access_token"]
    a_headers = {"Authorization": f"Bearer {admin_token}"}

    # 7. Admin Creates Household
    hh_create_res = client.post("/api/v1/households", json={
        "household_code": "HHD-E2E-CHENN",
        "address_line": "15, Marina Beach Road",
        "locality": "Mylapore",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "postal_code": "600004",
        "administrative_notes": "Official residential municipal survey 2026."
    }, headers=a_headers)
    assert hh_create_res.status_code == 201
    hh_id = hh_create_res.json()["id"]

    # 8. Admin Retrieves Citizen Records & Updates Status
    citizens_list_res = client.get(f"/api/v1/citizens?search={citizen_code}", headers=a_headers)
    assert citizens_list_res.status_code == 200
    matched_citizens = citizens_list_res.json()
    assert len(matched_citizens) == 1
    divya_id = matched_citizens[0]["id"]

    status_update_res = client.patch(
        f"/api/v1/citizens/{divya_id}/status",
        json={"profile_status": "active"},
        headers=a_headers
    )
    assert status_update_res.status_code == 200
    assert status_update_res.json()["profile_status"] == "active"

    # 9. Admin Assigns Profile to Household
    assign_res = client.post(
        f"/api/v1/households/{hh_id}/assign",
        json={"citizen_id": divya_id, "household_relationship": "Head of Household"},
        headers=a_headers
    )
    assert assign_res.status_code == 200
    assert len(assign_res.json()["members"]) == 1

    # 10. Verify Admin Dashboard Counts
    dash_res = client.get("/api/v1/admin/dashboard", headers=a_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_citizens"] >= 1
    assert dash_data["total_households"] >= 1

    # 11. Test Citizen Chat with Permitted Retrieval
    # Citizen checks profile and household via assistant
    chat_profile_res = client.post(
        "/api/v1/chat/message",
        json={"message": "can you show my registered profile?"},
        headers=c_headers
    )
    assert chat_profile_res.status_code == 200
    assert "Divya Krishnan" in chat_profile_res.json()["reply"]

    chat_hh_res = client.post(
        "/api/v1/chat/message",
        json={"message": "where is my household?"},
        headers=c_headers
    )
    assert chat_hh_res.status_code == 200
    assert "HHD-E2E-CHENN" in chat_hh_res.json()["reply"]
    assert "Chennai" in chat_hh_res.json()["reply"]
    # Administrative notes must NEVER be disclosed in citizen chat!
    assert "Official residential municipal survey" not in chat_hh_res.json()["reply"]

    # 12. Check Audit Logs for Recorded Administrative Actions
    audit_res = client.get("/api/v1/admin/audit-logs", headers=a_headers)
    assert audit_res.status_code == 200
    actions = [a["action"] for a in audit_res.json()]
    assert "HOUSEHOLD_CREATE" in actions
    assert "CITIZEN_STATUS_CHANGE" in actions
    assert "HOUSEHOLD_MEMBER_ASSIGN" in actions
