import pytest
from fastapi.testclient import TestClient


def test_citizen_dossier_report_access(client: TestClient, admin_token: str, citizen_token: str, citizen_user):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

    # 1. Citizen can access their own dossier report
    cit_id = citizen_user.citizen_profile.id
    resp = client.get(f"/api/v1/reports/citizen/{cit_id}/dossier", headers=citizen_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "metadata" in data
    assert "citizen" in data
    assert "medical_health_passport" in data
    assert "education_credentials" in data
    assert data["metadata"]["verification_status"] == "OFFICIALLY AUTHENTICATED"
    assert "digital_checksum_sha256" in data["metadata"]
    assert "qr_verification_payload" in data["metadata"]
    assert data["citizen"]["full_name"] == citizen_user.citizen_profile.full_name

    # 2. Admin can access any citizen dossier report
    admin_resp = client.get(f"/api/v1/reports/citizen/{cit_id}/dossier", headers=admin_headers)
    assert admin_resp.status_code == 200, admin_resp.text

    # 3. Check admin census summary report
    summary_resp = client.get("/api/v1/reports/admin/census-summary", headers=admin_headers)
    assert summary_resp.status_code == 200, summary_resp.text
    summary_data = summary_resp.json()
    assert "statistics" in summary_data
    assert "relationship_distribution" in summary_data
    assert summary_data["statistics"]["total_registered_citizens"] >= 1
