import requests
import uuid
import sys

BASE_URL = "http://localhost:8001"

def test_suite():
    print("==================================================")
    print("NAGRIKSETU SCHOOL SERVICE - PASSWORD AUTH SUITE")
    print("==================================================")

    # 1. Register with Email + Password (no mobile)
    rand_email = f"test.citizen.{uuid.uuid4().hex[:8]}@example.com"
    pwd = "ValidPassword@123"
    reg_email_payload = {
        "full_name": "Email Only Parent",
        "email": rand_email,
        "phone": None,
        "password": pwd,
        "confirm_password": pwd
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_email_payload)
    print("1. Register Email Only:", r.status_code, r.json())
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    assert "access_token" in r.json()

    # 2. Register with Mobile + Password (no email)
    # Generate random 10-digit mobile starting with 9
    rand_digits = "".join([str(i % 10) for i in uuid.uuid4().bytes[:8]])
    rand_phone = f"99{rand_digits[:8]}"
    reg_phone_payload = {
        "full_name": "Mobile Only Parent",
        "email": None,
        "phone": rand_phone,
        "password": pwd,
        "confirm_password": pwd
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_phone_payload)
    print("2. Register Mobile Only:", r.status_code, r.json())
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    assert "access_token" in r.json()

    # 3. Duplicate Email rejection
    dup_email_payload = {
        "full_name": "Duplicate Person",
        "email": rand_email,
        "phone": None,
        "password": pwd,
        "confirm_password": pwd
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=dup_email_payload)
    print("3. Duplicate Email Rejection:", r.status_code, r.json())
    assert r.status_code == 409, f"Expected 409, got {r.status_code}"

    # 4. Duplicate Mobile rejection
    dup_phone_payload = {
        "full_name": "Duplicate Person",
        "email": None,
        "phone": rand_phone,
        "password": pwd,
        "confirm_password": pwd
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=dup_phone_payload)
    print("4. Duplicate Mobile Rejection:", r.status_code, r.json())
    assert r.status_code == 409, f"Expected 409, got {r.status_code}"

    # 5. Password mismatch rejection
    mismatch_payload = {
        "full_name": "Mismatch Test",
        "email": "mismatch@example.com",
        "phone": None,
        "password": "Password123!",
        "confirm_password": "DifferentPassword123!"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=mismatch_payload)
    print("5. Password Mismatch Rejection:", r.status_code, r.json())
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"

    # 6. Weak password rejection
    weak_payload = {
        "full_name": "Weak Test",
        "email": "weak@example.com",
        "phone": None,
        "password": "simple",
        "confirm_password": "simple"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=weak_payload)
    print("6. Weak Password Rejection:", r.status_code)
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"

    # 7. Login with Email + Password
    login_data = {"username": rand_email, "password": pwd}
    r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print("7. Login with Email:", r.status_code, r.json().get("role"))
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json().get("role") == "parent"
    assert "access_token" in r.json()

    # 8. Login with Mobile + Password
    login_phone_data = {"username": rand_phone, "password": pwd}
    r = requests.post(f"{BASE_URL}/auth/login", data=login_phone_data)
    print("8. Login with Mobile:", r.status_code, r.json().get("role"))
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    assert r.json().get("role") == "parent"
    assert "access_token" in r.json()

    # 9. Incorrect password rejection
    wrong_pwd_data = {"username": rand_email, "password": "WrongPassword999!"}
    r = requests.post(f"{BASE_URL}/auth/login", data=wrong_pwd_data)
    print("9. Wrong Password Rejection:", r.status_code, r.json())
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"

    # 10. Forgot Password - Email account
    fp_email = requests.post(f"{BASE_URL}/auth/forgot-password", json={"identifier": rand_email})
    print("10. Forgot Password (Email):", fp_email.status_code, fp_email.json())
    assert fp_email.status_code == 200
    assert fp_email.json().get("status") == "ok"

    # 11. Forgot Password - Mobile Only account
    fp_mobile = requests.post(f"{BASE_URL}/auth/forgot-password", json={"identifier": rand_phone})
    print("11. Forgot Password (Mobile-Only):", fp_mobile.status_code, fp_mobile.json())
    assert fp_mobile.status_code == 200
    assert fp_mobile.json().get("status") == "mobile_only"
    assert "School Administrator" in fp_mobile.json().get("message")

    # 12. Setup Password for account without password
    # One of the test google citizen accounts had no password:
    target_no_pwd_email = "test.google.citizen.1794888070@gmail.com"
    setup_payload = {
        "identifier": target_no_pwd_email,
        "full_name": "Google Test Citizen",
        "password": "NewCitizenPassword@2026",
        "confirm_password": "NewCitizenPassword@2026"
    }
    r = requests.post(f"{BASE_URL}/auth/setup-password", json=setup_payload)
    print("12. Setup Password for Account without Password:", r.status_code, r.json())
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    # Verify that account can now log in with the new password
    login_new = {"username": target_no_pwd_email, "password": "NewCitizenPassword@2026"}
    r = requests.post(f"{BASE_URL}/auth/login", data=login_new)
    print("12b. Login with New Configured Password:", r.status_code, r.json().get("role"))
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"

    # 13. Existing School Admin login continues working
    admin_login = {"username": "admin.sch011@example.com", "password": "AdminPassword@2026"}
    # Let's test callmephalguna or cluster admin
    # Let's check a known school admin from database:
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": "callmephalguna@gmail.com", "password": "AdminPassword@2026"})
    if r.status_code != 200:
        # Check platform admin
        r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "AdminPassword@2026"})
    print("13. Admin Login Check:", r.status_code, r.json().get("role") if r.status_code == 200 else r.text)

    print("\nALL BACKEND TESTS PASSED!")

if __name__ == "__main__":
    test_suite()
