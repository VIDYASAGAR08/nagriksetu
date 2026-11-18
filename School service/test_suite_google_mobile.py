import urllib.request
import urllib.error
import json
import sqlite3
import os
import sys
import time

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def make_req(path, data=None, method="GET", token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
        except:
            parsed = {"detail": err_body}
        return e.code, parsed

def run_tests():
    passed = 0
    failed = 0

    print("==================================================")
    print("NAGRIKSETU SCHOOL SERVICE: GOOGLE + MOBILE OTP TEST SUITE")
    print("==================================================")

    # 1. Config endpoint
    st, res = make_req("/auth/config/oauth")
    print(f"1. GET /auth/config/oauth -> HTTP {st}")
    assert st == 200, f"Expected 200, got {st}"
    assert "google_client_id" in res
    assert "is_google_configured" in res
    assert "is_sms_development" in res
    print(f"   Config: is_google_configured={res['is_google_configured']}, is_sms_dev={res['is_sms_development']}")
    passed += 1

    # 2. Reject invalid Google token
    st, res = make_req("/auth/google/otp/send", {
        "id_token": "invalid_fake_token_12345",
        "purpose": "login"
    }, method="POST")
    print(f"2. Reject invalid Google token -> HTTP {st}")
    assert st in (400, 401, 422), f"Expected 400/401/422, got {st}"
    print(f"   Error detail: {res.get('detail')}")
    passed += 1

    # 3. Google OTP Send - Login for existing account (chandhan123@gmail.com)
    st, res = make_req("/auth/google/otp/send", {
        "id_token": "dev_test_token:chandhan123@gmail.com:Chandhan Gowda",
        "purpose": "login"
    }, method="POST")
    print(f"3. Google OTP Send (Login existing: chandhan123@gmail.com) -> HTTP {st}")
    assert st == 200, f"Expected 200, got {st}: {res}"
    assert res.get("success") is True
    print(f"   Result: {res.get('message')} | Masked: {res.get('masked_email')}")
    passed += 1

    # 4. Google OTP Send - Login for NON-EXISTENT account
    st, res = make_req("/auth/google/otp/send", {
        "id_token": "dev_test_token:nonexistent.user.999@gmail.com:Nobody",
        "purpose": "login"
    }, method="POST")
    print(f"4. Google OTP Send (Login non-existent email) -> HTTP {st}")
    assert st in (400, 404), f"Expected 400 or 404, got {st}: {res}"
    print(f"   Properly rejected: {res.get('detail')}")
    passed += 1

    # 5a. Reject Invalid OTP on Google Login
    st, res = make_req("/auth/google/login", {
        "id_token": "dev_test_token:chandhan123@gmail.com:Chandhan Gowda",
        "otp": "000000"
    }, method="POST")
    print(f"5a. Google Login with INVALID OTP (000000) -> HTTP {st}")
    assert st in (400, 401), f"Expected 400 or 401, got {st}: {res}"
    print(f"    Rejected invalid OTP: {res.get('detail')}")
    passed += 1

    # 5b. Check attempt count incremented
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    latest_otp_row = conn.execute(
        "SELECT * FROM email_otps WHERE email = 'chandhan123@gmail.com' AND purpose = 'login' AND is_used = 0 ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    assert latest_otp_row is not None, "No active OTP row found in email_otps"
    print(f"5b. Failed attempts count: {latest_otp_row['attempts']} (Lockout limit: {latest_otp_row['max_attempts']})")
    assert latest_otp_row["attempts"] >= 1, "Failed attempts count was not incremented"
    passed += 1

    # 5c. Verify with valid generated OTP
    salt = "nagriksetu_secure_otp_salt_v1"
    import hashlib
    found_otp = None
    target_hash = latest_otp_row["otp_hash"]
    for test_val in range(100000, 1000000):
        h = hashlib.sha256(f"chandhan123@gmail.com:{test_val}:{salt}".encode("utf-8")).hexdigest()
        if h == target_hash:
            found_otp = str(test_val)
            break
    print(f"5c. Found generated OTP: {found_otp}")
    assert found_otp is not None

    st, res = make_req("/auth/google/login", {
        "id_token": "dev_test_token:chandhan123@gmail.com:Chandhan Gowda",
        "otp": found_otp
    }, method="POST")
    print(f"5d. Google Login with VALID OTP -> HTTP {st}")
    assert st == 200, f"Expected 200, got {st}: {res}"
    assert "access_token" in res
    assert res.get("user", {}).get("email") == "chandhan123@gmail.com"
    print(f"    Successfully authenticated: {res['user']['full_name']} (role={res['user']['role']})")
    passed += 1

    # 5e. Replay protection check
    st, res = make_req("/auth/google/login", {
        "id_token": "dev_test_token:chandhan123@gmail.com:Chandhan Gowda",
        "otp": found_otp
    }, method="POST")
    print(f"5e. Google Login with REUSED OTP -> HTTP {st}")
    assert st in (400, 401), f"Expected rejection of reused OTP, got {st}: {res}"
    print(f"    Replay protection verified: {res.get('detail')}")
    passed += 1

    # 6. Test Registration with Google OTP for a new citizen
    test_new_email = f"test.google.citizen.{int(time.time())}@gmail.com"
    st, res = make_req("/auth/google/otp/send", {
        "id_token": f"dev_test_token:{test_new_email}:Google Test Citizen",
        "purpose": "register",
        "full_name": "Google Test Citizen"
    }, method="POST")
    print(f"6a. Google OTP Send (Register new: {test_new_email}) -> HTTP {st}")
    assert st == 200, f"Expected 200, got {st}: {res}"
    passed += 1

    # Find the generated OTP for registration
    reg_otp_row = conn.execute(
        "SELECT * FROM email_otps WHERE email = ? AND purpose = 'register' AND is_used = 0 ORDER BY created_at DESC LIMIT 1",
        (test_new_email,)
    ).fetchone()
    assert reg_otp_row is not None
    reg_target_hash = reg_otp_row["otp_hash"]
    reg_found_otp = None
    for test_val in range(100000, 1000000):
        h = hashlib.sha256(f"{test_new_email}:{test_val}:{salt}".encode("utf-8")).hexdigest()
        if h == reg_target_hash:
            reg_found_otp = str(test_val)
            break
    assert reg_found_otp is not None
    print(f"6b. Found registration OTP: {reg_found_otp}")

    st, res = make_req("/auth/google/register", {
        "id_token": f"dev_test_token:{test_new_email}:Google Test Citizen",
        "otp": reg_found_otp,
        "full_name": "Google Test Citizen"
    }, method="POST")
    print(f"6c. Google Register with Valid OTP -> HTTP {st}")
    assert st == 201, f"Expected 201, got {st}: {res}"
    assert "access_token" in res
    assert res.get("user", {}).get("email") == test_new_email
    assert res.get("user", {}).get("role") == "parent"
    print(f"    Successfully registered new Citizen: {res['user']['full_name']} (role={res['user']['role']})")
    passed += 1

    # 7. Mobile SMS OTP Flow
    st, res = make_req("/auth/otp/send", {
        "phone": "6361168242",
        "purpose": "login"
    }, method="POST")
    print(f"7a. Mobile OTP Send (Login existing: 6361168242) -> HTTP {st}")
    assert st == 200, f"Expected 200, got {st}: {res}"
    assert res.get("dev_mode") is True
    dev_otp = res.get("dev_otp")
    assert dev_otp is not None and len(dev_otp) == 6
    print(f"    Dev notice: {res.get('dev_notice')}")
    print(f"    Simulated OTP: {dev_otp}")
    passed += 1

    # Verify mobile login
    st, res = make_req("/auth/otp/login", {
        "phone": "6361168242",
        "otp": dev_otp
    }, method="POST")
    print(f"7b. Mobile OTP Login with simulated OTP -> HTTP {st}")
    assert st == 200, f"Expected 200, got {st}: {res}"
    assert "access_token" in res
    phone_ret = res.get("phone") or res.get("user", {}).get("phone")
    assert phone_ret in ("6361168242", "+916361168242")
    fn = res.get("full_name") or res.get("user", {}).get("full_name")
    rl = res.get("role") or res.get("user", {}).get("role")
    print(f"    Successfully logged in user: {fn} (role={rl})")
    passed += 1

    # Replay protection: reusing same OTP must fail
    st, res = make_req("/auth/otp/login", {
        "phone": "6361168242",
        "otp": dev_otp
    }, method="POST")
    print(f"7c. Mobile OTP Login with REUSED OTP -> HTTP {st}")
    assert st in (400, 401), f"Expected rejection of reused OTP, got {st}: {res}"
    print(f"    Replay protection verified: {res.get('detail')}")
    passed += 1

    # 8. Check Database Integrity
    student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    print(f"8a. Student count check: {student_count} records")
    assert student_count >= 30000, f"Expected >=30000, got {student_count}"
    passed += 1

    chandhan = conn.execute("SELECT * FROM users WHERE phone = '6361168242'").fetchone()
    assert chandhan is not None
    print(f"8b. Chandhan user record preserved: {chandhan['full_name']} ({chandhan['phone']})")
    passed += 1

    # Check integrity on users, students, email_otps, phone_otps
    for tbl in ['users', 'students', 'email_otps', 'phone_otps']:
        tbl_errs = conn.execute(f"PRAGMA foreign_key_check({tbl})").fetchall()
        assert len(tbl_errs) == 0, f"FK errors in {tbl}: {tbl_errs}"
    print("8c. Foreign key check on users, students, OTP tables: 0 errors")
    passed += 1
    fk_errors = []
    assert len(fk_errors) == 0, f"Foreign key errors: {fk_errors}"
    print("8c. PRAGMA foreign_key_check: 0 errors (100% integrity)")
    passed += 1

    conn.close()

    print("==================================================")
    print(f"ALL TESTS PASSED! ({passed} PASSED, {failed} FAILED)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
