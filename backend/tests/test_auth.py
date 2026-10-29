import pytest
from app.models.user import User, UserRole, UserStatus


def test_health_and_readiness(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"


def test_successful_citizen_registration(client, db_session):
    payload = {
        "full_name": "Meera Iyer",
        "email": "meera.iyer@example.com",
        "password": "Password123!@",
        "confirm_password": "Password123!@",
        "preferred_language": "ta",
        "phone_number": "+91 98888 77777"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "meera.iyer@example.com"
    # Verify strict role assignment: role MUST be citizen
    assert data["user"]["role"] == UserRole.CITIZEN.value

    # Verify database state
    user = db_session.query(User).filter(User.email == "meera.iyer@example.com").first()
    assert user is not None
    assert user.role == "citizen"
    assert user.citizen_profile is not None
    assert user.citizen_profile.full_name == "Meera Iyer"


def test_registration_duplicate_email(client):
    payload = {
        "full_name": "First User",
        "email": "duplicate@example.com",
        "password": "Password123!@",
        "confirm_password": "Password123!@",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt registration with uppercase variant to test case-insensitive normalization
    payload["email"] = "DUPLICATE@example.com"
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_registration_password_mismatch(client):
    payload = {
        "full_name": "Mismatch User",
        "email": "mismatch@example.com",
        "password": "Password123!@",
        "confirm_password": "DifferentPassword123!@",
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 400
    assert "do not match" in res.json()["detail"]


def test_registration_weak_password(client):
    payload = {
        "full_name": "Weak Pwd User",
        "email": "weak@example.com",
        "password": "onlylowercasepassword",
        "confirm_password": "onlylowercasepassword",
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 400
    assert "uppercase" in res.json()["detail"].lower()


def test_login_successful(client, citizen_user):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": citizen_user.email, "password": "CitizenPass123!@"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == citizen_user.email


def test_login_invalid_password(client, citizen_user):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": citizen_user.email, "password": "WrongPassword!@#"}
    )
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_login_suspended_account(client, db_session, citizen_user):
    citizen_user.account_status = UserStatus.SUSPENDED.value
    db_session.commit()

    res = client.post(
        "/api/v1/auth/login",
        json={"email": citizen_user.email, "password": "CitizenPass123!@"}
    )
    assert res.status_code == 403
    assert "suspended" in res.json()["detail"]


def test_auth_me_authenticated(client, citizen_token, citizen_user):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["email"] == citizen_user.email
    assert data["citizen_profile"]["citizen_code"] == citizen_user.citizen_profile.citizen_code


def test_auth_me_unauthenticated(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_logout_endpoint(client):
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200
    assert "logged out" in res.json()["message"]
