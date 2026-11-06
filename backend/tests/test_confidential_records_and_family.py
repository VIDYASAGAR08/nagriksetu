import pytest
from app.models.records import MedicalRecord, EducationRecord, LandRecord
from app.models.household import Household


def test_family_member_partial_update_and_privacy_barrier(client, citizen_token, second_citizen_user, db_session, citizen_user):
    """
    Test that a family member in the SAME household can update permitted fields with OTP,
    while an UNRELATED outsider is strictly forbidden (403).
    """
    headers = {"Authorization": f"Bearer {citizen_token}"}
    citizen_profile = citizen_user.citizen_profile
    second_profile = second_citizen_user.citizen_profile

    # Create a test household
    hh = Household(
        household_code="HHD-FAMILY-TEST",
        address_line="123 Family Lane",
        locality="Indiranagar",
        city="Bengaluru",
        state="Karnataka",
        postal_code="560038"
    )
    db_session.add(hh)
    db_session.flush()

    # Place citizen 1 in the household
    citizen_profile.household_id = hh.id
    citizen_profile.household_relationship = "Head of Household"

    # Second citizen is in a DIFFERENT household (or none)
    second_profile.household_id = None
    db_session.commit()

    # 1. Citizen 1 attempts to update Second Citizen (OUTSIDER) -> Expect 403 Forbidden
    res_outsider = client.patch(f"/api/v1/citizens/{second_profile.id}/family-update", json={
        "phone_number": "+91 91111 22222",
        "preferred_language": "ta",
        "otp_reference_id": "FAKE-REF"
    }, headers=headers)
    assert res_outsider.status_code == 403
    assert "Access Denied" in res_outsider.json()["detail"]

    # 2. Now add second citizen to the SAME household as a family member (Spouse)
    second_profile.household_id = hh.id
    second_profile.household_relationship = "Spouse"
    db_session.commit()

    # Generate and verify OTP
    otp_gen = client.post("/api/v1/auth/otp/generate", json={"purpose": "CITIZEN_PROFILE_UPDATE"}, headers=headers).json()
    ref_id = otp_gen["reference_id"]
    code = otp_gen["demo_hint"]

    ver_res = client.post("/api/v1/auth/otp/verify", json={
        "reference_id": ref_id,
        "otp_code": code,
        "purpose": "CITIZEN_PROFILE_UPDATE"
    })
    assert ver_res.status_code == 200

    # 3. Citizen 1 updates family member's phone number with verified OTP -> Expect 200 OK
    res_family = client.patch(f"/api/v1/citizens/{second_profile.id}/family-update", json={
        "phone_number": "+91 97777 88888",
        "preferred_language": "hi",
        "otp_reference_id": ref_id
    }, headers=headers)
    assert res_family.status_code == 200
    assert res_family.json()["phone_number"] == "+91 97777 88888"
    assert res_family.json()["preferred_language"] == "hi"


def test_confidential_medical_and_education_records(client, citizen_token, citizen_user, db_session):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    p_id = citizen_user.citizen_profile.id

    # 1. Fetch Medical Record
    med_res = client.get(f"/api/v1/citizens/{p_id}/medical", headers=headers)
    assert med_res.status_code == 200

    # 2. Generate and Verify OTP for medical update
    otp_gen = client.post("/api/v1/auth/otp/generate", json={"purpose": "CITIZEN_PROFILE_UPDATE"}, headers=headers).json()
    ref_id = otp_gen["reference_id"]
    code = otp_gen["demo_hint"]

    client.post("/api/v1/auth/otp/verify", json={
        "reference_id": ref_id,
        "otp_code": code,
        "purpose": "CITIZEN_PROFILE_UPDATE"
    })

    # 3. Update Medical Record with OTP
    med_up = client.put(f"/api/v1/citizens/{p_id}/medical", json={
        "blood_group": "AB+",
        "chronic_conditions": "None",
        "emergency_hospital": "Narayana Health City",
        "otp_reference_id": ref_id
    }, headers=headers)
    assert med_up.status_code == 200
    assert med_up.json()["blood_group"] == "AB+"

    # 4. Fetch Education Record
    edu_res = client.get(f"/api/v1/citizens/{p_id}/education", headers=headers)
    assert edu_res.status_code == 200
