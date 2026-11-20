import pytest
from app.main import app, SessionLocal, Base, engine, hash_password
from app.models import Account, CitizenProfile
from fastapi.testclient import TestClient

client = TestClient(app)

def test_sso_verify_fallback(monkeypatch):
    # Mock verify_via_central_sso
    def mock_verify(identifier, password):
        if identifier == "federated.citizen@example.com" and password == "ValidSecret123!":
            return {
                "valid": True,
                "email": "federated.citizen@example.com",
                "full_name": "Federated Citizen",
                "citizen_code": "CIT-2026-999888",
                "phone_number": "+91 99999 88888"
            }
        return None

    import app.main as main_mod
    monkeypatch.setattr(main_mod, "verify_via_central_sso", mock_verify)

    # Attempt login with non-existent account
    res = client.post("/api/auth/login", json={
        "email": "federated.citizen@example.com",
        "password": "ValidSecret123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "federated.citizen@example.com"
    assert data["role"] == "CITIZEN"
    assert data["citizen_ref"] == "CIT-2026-999888"
    assert "access_token" in data
