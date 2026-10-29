def test_admin_dashboard_metrics(client, admin_token, citizen_user, test_household):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/admin/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_citizens"] >= 1
    assert data["total_households"] >= 1
    assert "recent_registrations" in data


def test_admin_audit_logs(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Perform an action that logs an audit event
    payload = {
        "full_name": "Audit Tracked Citizen",
        "email": "audit.test@example.com",
        "initial_password": "Password123!@",
        "preferred_language": "en"
    }
    client.post("/api/v1/citizens", json=payload, headers=headers)

    # Fetch audit logs
    res = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 1
    actions = [l["action"] for l in logs]
    assert "CITIZEN_CREATE" in actions


def test_citizen_forbidden_from_admin_endpoints(client, citizen_token):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    res_dash = client.get("/api/v1/admin/dashboard", headers=headers)
    assert res_dash.status_code == 403

    res_audit = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert res_audit.status_code == 403


def test_citizen_chat_features(client, citizen_token, citizen_user, test_household, db_session):
    # Link household to citizen
    citizen_user.citizen_profile.household_id = test_household.id
    citizen_user.citizen_profile.household_relationship = "Head of Household"
    db_session.commit()

    headers = {"Authorization": f"Bearer {citizen_token}"}

    # 1. Profile query
    res1 = client.post("/api/v1/chat/message", json={"message": "can you show my profile?"}, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert citizen_user.citizen_profile.full_name in data1["reply"]
    assert citizen_user.citizen_profile.citizen_code in data1["reply"]

    # 2. Household query
    res2 = client.post("/api/v1/chat/message", json={"message": "who is in my household?"}, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert test_household.household_code in data2["reply"]
    assert test_household.city in data2["reply"]

    # 3. Help query
    res3 = client.post("/api/v1/chat/message", json={"message": "what services are available?"}, headers=headers)
    assert res3.status_code == 200
    data3 = res3.json()
    assert "Identity & Profile Management" in data3["reply"]
