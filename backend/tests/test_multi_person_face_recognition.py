import io, base64, uuid
from PIL import Image, ImageDraw
import pytest

def make_test_face(skin_rgb, eye_y, eye_spacing, mouth_y, mouth_width):
    im = Image.new("RGB", (200, 240), (240, 240, 245))
    dr = ImageDraw.Draw(im)
    # Head outline
    dr.ellipse([40, 20, 160, 200], fill=skin_rgb, outline=(30, 30, 30), width=2)
    # Hair
    dr.chord([38, 15, 162, 100], 180, 360, fill=(40, 25, 15))
    # Eyes
    cx = 100
    dr.ellipse([cx - eye_spacing - 10, eye_y, cx - eye_spacing + 10, eye_y + 12], fill=(255, 255, 255), outline=(0, 0, 0))
    dr.ellipse([cx - eye_spacing - 4, eye_y + 2, cx - eye_spacing + 4, eye_y + 10], fill=(20, 20, 20))
    dr.ellipse([cx + eye_spacing - 10, eye_y, cx + eye_spacing + 10, eye_y + 12], fill=(255, 255, 255), outline=(0, 0, 0))
    dr.ellipse([cx + eye_spacing - 4, eye_y + 2, cx + eye_spacing + 4, eye_y + 10], fill=(20, 20, 20))
    # Nose
    dr.polygon([(cx, eye_y + 15), (cx - 6, eye_y + 40), (cx + 6, eye_y + 40)], outline=(120, 80, 50))
    # Mouth
    dr.arc([cx - mouth_width, mouth_y - 10, cx + mouth_width, mouth_y + 10], 0, 180, fill=(180, 50, 50), width=3)
    buf = io.BytesIO()
    im.save(buf, format="JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def test_five_peoples_faces_1_to_n_recognition(client):
    """
    Test 1:N Facial Recognition across 5 registered people:
    1. Register Person 1, Person 2, Person 3, Person 4, Person 5 each with their distinct facial biometrics.
    2. Present Person 1's live face with NO email/phone -> System recognizes Person 1 and issues OTP for Person 1.
    3. Present Person 3's live face with NO email/phone -> System recognizes Person 3 and issues OTP for Person 3.
    4. Present Person 5's live face with NO email/phone -> System recognizes Person 5 and issues OTP for Person 5.
    5. Complete 2FA OTP verification for Person 3 -> Authenticated as Person 3!
    """
    # 5 Distinct faces
    f1 = make_test_face((240, 200, 160), 80, 25, 150, 20)
    f2 = make_test_face((200, 150, 100), 90, 32, 160, 26)
    f3 = make_test_face((120, 80, 50), 75, 22, 145, 18)
    f4 = make_test_face((220, 175, 130), 85, 28, 140, 22)
    f5 = make_test_face((250, 215, 185), 92, 30, 165, 30)

    # Live versions of Person 1, 3, 5 with minor camera jitter/lighting shift
    f1_live = make_test_face((236, 198, 158), 81, 25, 149, 21)
    f3_live = make_test_face((118, 78, 48), 75, 22, 146, 18)
    f5_live = make_test_face((248, 212, 182), 92, 30, 164, 30)

    registered_users = []
    for i, (name, face) in enumerate([
        ("Citizen One", f1),
        ("Citizen Two", f2),
        ("Citizen Three", f3),
        ("Citizen Four", f4),
        ("Citizen Five", f5)
    ], 1):
        email = f"person{i}.{uuid.uuid4().hex[:6]}@example.com"
        phone = f"+91987654321{i}"
        res = client.post("/api/v1/auth/register", json={
            "full_name": name,
            "email": email,
            "phone_number": phone,
            "password": "CitizenPass123!@",
            "confirm_password": "CitizenPass123!@",
            "face_data": face,
        })
        assert res.status_code == 201
        registered_users.append((name, email, phone))

    # --- Test 1: Present Person 1 live face without email ---
    login_p1 = client.post("/api/v1/auth/biometrics/login", json={
        "biometric_type": "face",
        "face_data": f1_live,
        "require_otp": True
    })
    assert login_p1.status_code == 200
    p1_data = login_p1.json()
    assert p1_data["requires_otp"] is True
    # Verify recognized user is Citizen One!
    assert p1_data["identifier"] == registered_users[0][1]

    # --- Test 2: Present Person 3 live face without email ---
    login_p3 = client.post("/api/v1/auth/biometrics/login", json={
        "biometric_type": "face",
        "face_data": f3_live,
        "require_otp": True
    })
    assert login_p3.status_code == 200
    p3_data = login_p3.json()
    assert p3_data["requires_otp"] is True
    # Verify recognized user is Citizen Three!
    assert p3_data["identifier"] == registered_users[2][1]

    # --- Test 3: Present Person 5 live face without email ---
    login_p5 = client.post("/api/v1/auth/biometrics/login", json={
        "biometric_type": "face",
        "face_data": f5_live,
        "require_otp": True
    })
    assert login_p5.status_code == 200
    p5_data = login_p5.json()
    assert p5_data["requires_otp"] is True
    # Verify recognized user is Citizen Five!
    assert p5_data["identifier"] == registered_users[4][1]

    # --- Test 4: Complete OTP verification for Citizen Three ---
    verify_res = client.post("/api/v1/auth/login-otp/verify", json={
        "identifier": registered_users[2][1],
        "reference_id": p3_data["reference_id"],
        "otp_code": p3_data["demo_hint"]
    })
    assert verify_res.status_code == 200
    auth = verify_res.json()
    assert auth["user"]["email"] == registered_users[2][1]
    assert "access_token" in auth
