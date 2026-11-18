import urllib.request
import urllib.parse
import json
import uuid
import sqlite3

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

results = []

def record(test_num, name, passed, detail=""):
    status_str = "PASS" if passed else "FAIL"
    results.append((test_num, name, status_str, detail))
    print(f"[{status_str}] Test {test_num}: {name} - {detail}")

def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed

def post_form(endpoint, form_data):
    data_bytes = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data_bytes,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed

def run():
    print("=" * 60)
    print("RUNNING FINAL TASK CHECKLIST VERIFICATION")
    print("=" * 60)

    test_pwd = "SecureParentPass@2026"

    # Test 1: New user registers using email and password
    email_user = f"citizen.email.{uuid.uuid4().hex[:6]}@karnataka.gov.in"
    code, resp = post_json("/auth/register", {
        "full_name": "Email Registered Citizen",
        "email": email_user,
        "phone": None,
        "password": test_pwd,
        "confirm_password": test_pwd
    })
    passed = code == 201 and "access_token" in resp and resp.get("role") == "parent"
    record(1, "New user registers using email and password", passed, f"Status: {code}, User ID: {resp.get('user_id')}")

    # Test 2: New user registers using mobile number and password
    rand_phone = f"98{str(uuid.uuid4().int)[:8]}"
    code, resp = post_json("/auth/register", {
        "full_name": "Mobile Registered Citizen",
        "email": None,
        "phone": rand_phone,
        "password": test_pwd,
        "confirm_password": test_pwd
    })
    passed = code == 201 and "access_token" in resp and resp.get("role") == "parent"
    record(2, "New user registers using mobile number and password", passed, f"Status: {code}, User ID: {resp.get('user_id')}")

    # Test 3: User logs in using email and password
    code, resp = post_form("/auth/login", {
        "username": email_user,
        "password": test_pwd
    })
    passed = code == 200 and "access_token" in resp and resp.get("role") == "parent"
    record(3, "User logs in using email and password", passed, f"Status: {code}, Role: {resp.get('role')}")

    # Test 4: User logs in using mobile number and password
    code, resp = post_form("/auth/login", {
        "username": rand_phone,
        "password": test_pwd
    })
    passed = code == 200 and "access_token" in resp and resp.get("role") == "parent"
    record(4, "User logs in using mobile number and password", passed, f"Status: {code}, Role: {resp.get('role')}")

    # Test 5: Incorrect password is rejected
    code, resp = post_form("/auth/login", {
        "username": email_user,
        "password": "CompletelyWrongPassword!123"
    })
    passed = code == 401 and resp.get("detail") == "Incorrect username or password."
    record(5, "Incorrect password is rejected", passed, f"Status: {code}, Detail: {resp.get('detail')}")

    # Test 6: Duplicate email registration is rejected
    code, resp = post_json("/auth/register", {
        "full_name": "Another Citizen",
        "email": email_user,
        "phone": None,
        "password": test_pwd,
        "confirm_password": test_pwd
    })
    passed = code == 409 and "already exists" in resp.get("detail", "")
    record(6, "Duplicate email registration is rejected", passed, f"Status: {code}, Detail: {resp.get('detail')}")

    # Test 7: Duplicate mobile registration is rejected
    code, resp = post_json("/auth/register", {
        "full_name": "Another Citizen",
        "email": None,
        "phone": rand_phone,
        "password": test_pwd,
        "confirm_password": test_pwd
    })
    passed = code == 409 and "already exists" in resp.get("detail", "")
    record(7, "Duplicate mobile registration is rejected", passed, f"Status: {code}, Detail: {resp.get('detail')}")

    # Test 8: Password confirmation validation works
    code, resp = post_json("/auth/register", {
        "full_name": "Mismatch Test",
        "email": "mismatch.test@example.com",
        "phone": None,
        "password": test_pwd,
        "confirm_password": "MismatchPassword@999"
    })
    passed = code == 422 and "Passwords do not match" in resp.get("detail", "")
    record(8, "Password confirmation validation works", passed, f"Status: {code}, Detail: {resp.get('detail')}")

    # Test 9: Existing users and guardians retain their records
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    chandhan = c.execute("SELECT user_id, email, phone, role, full_name FROM users WHERE phone = '6361168242'").fetchone()
    guardian = c.execute("SELECT guardian_id, user_id, full_name, phone FROM guardians WHERE user_id = ?", (chandhan["user_id"],)).fetchone() if chandhan else None
    user_count = c.execute("SELECT COUNT(1) as cnt FROM users").fetchone()["cnt"]
    guardian_count = c.execute("SELECT COUNT(1) as cnt FROM guardians").fetchone()["cnt"]
    passed = chandhan is not None and guardian is not None and user_count >= 87 and guardian_count >= 1
    record(9, "Existing users and guardians retain their records", passed, f"Chandhan: {dict(chandhan) if chandhan else None}, Guardian: {dict(guardian) if guardian else None}, Total Users: {user_count}, Total Guardians: {guardian_count}")

    # Test 10: Existing students and admissions remain accessible
    student_count = c.execute("SELECT COUNT(1) as cnt FROM students").fetchone()["cnt"]
    enrollment_count = c.execute("SELECT COUNT(1) as cnt FROM enrollments").fetchone()["cnt"]
    asha = c.execute("SELECT student_id, student_name, school_id, standard FROM students WHERE student_id = 'SCH01001'").fetchone()
    passed = student_count == 30003 and enrollment_count >= 30003 and asha is not None
    record(10, "Existing students and admissions remain accessible", passed, f"Students: {student_count}, Enrollments: {enrollment_count}, Asha Record: {dict(asha) if asha else None}")

    # Test 11: Existing school administrator login continues working
    code, resp = post_form("/auth/login", {
        "username": "staff.sch001@example.com",
        "password": "Staff@NagrikSetu2026!"
    })
    passed = code == 200 and "access_token" in resp and resp.get("role") in ("school_staff", "school_admin")
    record(11, "Existing school administrator login continues working", passed, f"Status: {code}, Role: {resp.get('role')}")

    # Test 12: Existing platform administrator login continues working
    code, resp = post_form("/auth/login", {
        "username": "admin.central@nagriksetu.gov",
        "password": "Central@NagrikSetu2026!"
    })
    passed = code == 200 and "access_token" in resp and resp.get("role") == "platform_admin"
    record(12, "Existing platform administrator login continues working", passed, f"Status: {code}, Role: {resp.get('role')}")

    # Test 13 & 14: Inspect frontend bundle for absence of Google button and OTP screens in citizen flow
    with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\RegisterPage.jsx", "r", encoding="utf-8") as f:
        reg_code = f.read()
    with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx", "r", encoding="utf-8") as f:
        login_code = f.read()
    no_google_btn = "GoogleIcon" not in reg_code and "GoogleIcon" not in login_code
    no_otp_screens = "one-time-code" not in reg_code and "login-google-otp" not in login_code
    record(13, "No OTP screens or OTP requests appear in Citizen login or registration", no_otp_screens, f"No OTP input in citizen forms: {no_otp_screens}")
    record(14, "No Google login button appears", no_google_btn, f"No Google Icon/button component: {no_google_btn}")

    # Test 15: Forgot Password works securely (email reset token & mobile explanation)
    code_fp_email, resp_fp_email = post_json("/auth/forgot-password", {"identifier": email_user})
    code_fp_mob, resp_fp_mob = post_json("/auth/forgot-password", {"identifier": rand_phone})
    passed = (
        code_fp_email == 200 and resp_fp_email.get("status") == "ok" and
        code_fp_mob == 200 and resp_fp_mob.get("status") == "mobile_only"
    )
    record(15, "Forgot Password works only if securely implemented", passed, f"Email status: {resp_fp_email.get('status')}, Mobile status: {resp_fp_mob.get('status')}")

    conn.close()

    print("=" * 60)
    all_passed = all(r[2] == "PASS" for r in results)
    print(f"OVERALL SUMMARY: {'ALL 15 TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    run()
