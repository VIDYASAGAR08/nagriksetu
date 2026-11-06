import pytest
from app.models.user import User


def test_otp_flow_and_security(client, citizen_token):
    headers = {"Authorization": f"Bearer {citizen_token}"}

    # 1. Generate OTP
    res = client.post("/api/v1/auth/otp/generate", json={"purpose": "CITIZEN_PROFILE_UPDATE"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "reference_id" in data
    assert "demo_hint" in data
    assert len(data["demo_hint"]) == 6
    ref_id = data["reference_id"]
    code = data["demo_hint"]

    # 2. Reject wrong code
    wrong_res = client.post("/api/v1/auth/otp/verify", json={
        "reference_id": ref_id,
        "otp_code": "000000" if code != "000000" else "111111",
        "purpose": "CITIZEN_PROFILE_UPDATE"
    })
    assert wrong_res.status_code == 400
    assert "Incorrect verification code" in wrong_res.json()["detail"]

    # 3. Reject non-existent ref
    invalid_res = client.post("/api/v1/auth/otp/verify", json={
        "reference_id": "REF-NONEXISTENT",
        "otp_code": code,
        "purpose": "CITIZEN_PROFILE_UPDATE"
    })
    assert invalid_res.status_code == 404

    # 4. Verify correct code
    verify_res = client.post("/api/v1/auth/otp/verify", json={
        "reference_id": ref_id,
        "otp_code": code,
        "purpose": "CITIZEN_PROFILE_UPDATE"
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["verified"] is True

    # 5. Apply profile update with verified token
    update_res = client.patch("/api/v1/citizens/me", json={
        "phone_number": "+91 91234 56789",
        "otp_reference_id": ref_id
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["phone_number"] == "+91 91234 56789"

    # 6. Replay attack rejection: Using the same OTP ref again must fail
    replay_res = client.patch("/api/v1/citizens/me", json={
        "phone_number": "+91 90000 00000",
        "otp_reference_id": ref_id
    }, headers=headers)
    assert replay_res.status_code == 403


def test_biometric_challenge_and_registration(client, citizen_token, citizen_user):
    headers = {"Authorization": f"Bearer {citizen_token}"}

    # 1. Challenge endpoint
    chal_res = client.get("/api/v1/auth/biometrics/challenge")
    assert chal_res.status_code == 200
    chal_data = chal_res.json()
    assert "challenge" in chal_data
    assert chal_data["rp_id"] == "localhost"

    # 2. Register biometric credential
    cred_id = "cred_webauthn_touch_id_test_12345"
    reg_res = client.post("/api/v1/auth/biometrics/register", json={
        "credential_id": cred_id,
        "public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...",
        "biometric_type": "fingerprint"
    }, headers=headers)
    assert reg_res.status_code == 200
    assert reg_res.json()["success"] is True

    # 3. Biometric login with enrolled credential
    bio_login = client.post("/api/v1/auth/biometrics/login", json={
        "email": citizen_user.email,
        "credential_id": cred_id,
        "biometric_type": "fingerprint"
    })
    assert bio_login.status_code == 200
    assert "access_token" in bio_login.json()
    assert bio_login.json()["user"]["biometric_enabled"] is True

    # 4. Biometric login with mismatched credential fails
    bad_bio_login = client.post("/api/v1/auth/biometrics/login", json={
        "email": citizen_user.email,
        "credential_id": "wrong_unauthorized_key",
        "biometric_type": "fingerprint"
    })
    assert bad_bio_login.status_code == 401


def test_live_face_biometric_matching_and_rejection(client):
    import io, base64, uuid
    from PIL import Image, ImageDraw

    def make_face_b64(skin_color, eye_x):
        im = Image.new("RGB", (160, 160), (20, 35, 55))
        dr = ImageDraw.Draw(im)
        dr.ellipse([30, 20, 130, 140], fill=skin_color)
        dr.ellipse([60, eye_x, 75, eye_x + 15], fill=(0, 0, 0))
        dr.ellipse([85, eye_x, 100, eye_x + 15], fill=(0, 0, 0))
        dr.line([65, 110, 95, 110], fill=(180, 50, 50), width=3)
        buf = io.BytesIO()
        im.save(buf, format="JPEG")
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    face_user_a = make_face_b64((230, 180, 130), 60)
    face_user_a_live = make_face_b64((226, 178, 128), 61)
    face_imposter = make_face_b64((100, 70, 40), 40)

    # Register citizen with face A
    email = f"face.match.{uuid.uuid4().hex[:6]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "full_name": "Face Enrolled Citizen",
        "email": email,
        "password": "CitizenPass123!@",
        "confirm_password": "CitizenPass123!@",
        "face_data": face_user_a
    })
    assert reg_res.status_code == 201

    # 1. Matching face succeeds
    good_login = client.post("/api/v1/auth/biometrics/login", json={
        "email": email,
        "biometric_type": "face",
        "face_data": face_user_a_live
    })
    assert good_login.status_code == 200
    assert good_login.json()["user"]["has_face_enrolled"] is True

    # 2. Imposter face is rejected with 401
    bad_login = client.post("/api/v1/auth/biometrics/login", json={
        "email": email,
        "biometric_type": "face",
        "face_data": face_imposter
    })
    assert bad_login.status_code == 401
    assert "Facial match failed" in bad_login.json()["detail"]


def test_login_with_otp_flow(client, citizen_user):
    """
    Test OTP-based login:
    1. Request OTP using citizen email or mobile number.
    2. Obtain reference_id and verify 6-digit OTP.
    3. Successfully receive JWT token and authenticated user payload.
    4. Invalid OTP or wrong reference is rejected.
    """
    user = citizen_user

    # 1. Request login OTP with citizen email
    req_res = client.post("/api/v1/auth/login-otp/request", json={
        "identifier": user.email
    })
    assert req_res.status_code == 200
    otp_data = req_res.json()
    assert "reference_id" in otp_data
    assert otp_data["purpose"] == "LOGIN"
    otp_code = otp_data["demo_hint"]
    ref_id = otp_data["reference_id"]

    # 2. Rejection with invalid code
    bad_verify = client.post("/api/v1/auth/login-otp/verify", json={
        "identifier": user.email,
        "reference_id": ref_id,
        "otp_code": "000000"
    })
    assert bad_verify.status_code == 400
    assert "Incorrect" in bad_verify.json()["detail"]

    # 3. Successful verification and login
    good_verify = client.post("/api/v1/auth/login-otp/verify", json={
        "identifier": user.email,
        "reference_id": ref_id,
        "otp_code": otp_code
    })
    assert good_verify.status_code == 200
    auth_data = good_verify.json()
    assert "access_token" in auth_data
    assert auth_data["user"]["email"] == user.email
    assert auth_data["user"]["role"] == "citizen"


def test_biometric_login_with_2fa_otp_flow(client, citizen_user):
    """
    Test 2-Factor Authentication: Biometric (Face / Fingerprint) verification followed by OTP verification.
    1. Enroll biometric.
    2. Attempt biometric login with require_otp=True.
    3. Biometric passes, system returns requires_otp=True and reference_id.
    4. Verify OTP using /login-otp/verify.
    5. Returns JWT access_token and logs user in.
    """
    user = citizen_user
    cred_id = f"passkey-2fa-{user.id}"
    user.biometric_credential_id = cred_id
    user.phone_number = "+919876543210"

    # Step 1: Biometric login with require_otp=True
    bio_res = client.post("/api/v1/auth/biometrics/login", json={
        "email": user.email,
        "credential_id": cred_id,
        "biometric_type": "fingerprint",
        "require_otp": True
    })
    assert bio_res.status_code == 200
    res_data = bio_res.json()
    assert res_data["requires_otp"] is True
    assert "reference_id" in res_data
    assert "demo_hint" in res_data
    ref_id = res_data["reference_id"]
    otp_code = res_data["demo_hint"]

    # Step 2: Verify OTP
    verify_res = client.post("/api/v1/auth/login-otp/verify", json={
        "identifier": user.email,
        "reference_id": ref_id,
        "otp_code": otp_code
    })
    assert verify_res.status_code == 200
    auth_data = verify_res.json()
    assert "access_token" in auth_data
    assert auth_data["user"]["email"] == user.email


