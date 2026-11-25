import urllib.request
import urllib.parse
import json
import sqlite3
import time

BASE_URL = "http://127.0.0.1:8001"

def login_request(username, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            body = json.loads(error_body)
        except Exception:
            body = {"detail": error_body}
        return e.code, body
    except Exception as ex:
        return 500, {"detail": str(ex)}

def get_protected_endpoint(token, path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            body = json.loads(error_body)
        except Exception:
            body = {"detail": error_body}
        return e.code, body

print("=" * 60)
print("COMPREHENSIVE CITIZEN AUTHENTICATION TEST SUITE")
print("=" * 60)

test_citizen_phone = "7485961230"
test_citizen_email = "vikas123@gmail.com"
test_citizen_pw = "Vikas@123"

results = []

# Test 1: Registered phone + password
status, body = login_request(test_citizen_phone, test_citizen_pw)
t1_pass = (status == 200 and body.get("role") == "parent" and bool(body.get("access_token")))
results.append(("Login using registered phone + password", t1_pass, f"Status {status}, role={body.get('role')}"))
print(f"Test 1 - Registered phone + password: {'PASS' if t1_pass else 'FAIL'} ({status})")
phone_token = body.get("access_token")

# Test 2: Registered email + same password
status, body = login_request(test_citizen_email, test_citizen_pw)
t2_pass = (status == 200 and body.get("role") == "parent" and bool(body.get("access_token")))
results.append(("Login using registered email + same password", t2_pass, f"Status {status}, role={body.get('role')}"))
print(f"Test 2 - Registered email + same password: {'PASS' if t2_pass else 'FAIL'} ({status})")
email_token = body.get("access_token")

# Test 3: Uppercase email + password
status, body = login_request("VIKAS123@GMAIL.COM", test_citizen_pw)
t3_pass = (status == 200 and body.get("role") == "parent" and bool(body.get("access_token")))
results.append(("Login using uppercase email + password", t3_pass, f"Status {status}, role={body.get('role')}"))
print(f"Test 3 - Uppercase email + password: {'PASS' if t3_pass else 'FAIL'} ({status})")

# Test 4: Email with surrounding spaces + password
status, body = login_request("   vikas123@gmail.com   ", test_citizen_pw)
t4_pass = (status == 200 and body.get("role") == "parent" and bool(body.get("access_token")))
results.append(("Login using email with surrounding spaces", t4_pass, f"Status {status}, role={body.get('role')}"))
print(f"Test 4 - Email with surrounding spaces: {'PASS' if t4_pass else 'FAIL'} ({status})")

# Test 5: Wrong password
status, body = login_request(test_citizen_email, "WrongPassword@999")
t5_pass = (status == 401)
results.append(("Wrong password rejected", t5_pass, f"Status {status}, detail={body.get('detail')}"))
print(f"Test 5 - Wrong password rejected: {'PASS' if t5_pass else 'FAIL'} ({status})")

# Test 6: Unknown email
status, body = login_request("unknown.citizen.999@example.com", test_citizen_pw)
t6_pass = (status == 401)
results.append(("Unknown email rejected", t6_pass, f"Status {status}, detail={body.get('detail')}"))
print(f"Test 6 - Unknown email rejected: {'PASS' if t6_pass else 'FAIL'} ({status})")

# Test 7: Unknown phone number
status, body = login_request("9999900000", test_citizen_pw)
t7_pass = (status == 401)
results.append(("Unknown phone number rejected", t7_pass, f"Status {status}, detail={body.get('detail')}"))
print(f"Test 7 - Unknown phone number rejected: {'PASS' if t7_pass else 'FAIL'} ({status})")

# Test 8: Duplicate email ambiguity
conn = sqlite3.connect("C:/Users/callm/nagriksetu/backend/data/nagriksetu.db")
dup_email = "ambiguous.test.citizen@karnataka.gov.in"
dup_user1 = "test-dup-user-1"
dup_user2 = "test-dup-user-2"
dup_guardian2 = "test-dup-guardian-2"

conn.execute("DELETE FROM guardians WHERE guardian_id = ?", (dup_guardian2,))
conn.execute("DELETE FROM users WHERE user_id IN (?, ?)", (dup_user1, dup_user2))
conn.execute("INSERT INTO users (user_id, email, phone, password_hash, role, is_active, full_name) VALUES (?, ?, '9111111111', 'hash1', 'parent', 1, 'Dup One')", (dup_user1, dup_email))
conn.execute("INSERT INTO users (user_id, email, phone, password_hash, role, is_active, full_name) VALUES (?, NULL, '9222222222', 'hash2', 'parent', 1, 'Dup Two')", (dup_user2,))
conn.execute("INSERT INTO guardians (guardian_id, user_id, full_name, email, phone, relationship) VALUES (?, ?, 'Dup Two Guardian', ?, '9222222222', 'Parent')", (dup_guardian2, dup_user2, dup_email))
conn.commit()
conn.close()

status, body = login_request(dup_email, "AnyPassword@123")
t8_pass = (status == 409)
results.append(("Duplicate email ambiguity safely rejected", t8_pass, f"Status {status}, detail={body.get('detail')}"))
print(f"Test 8 - Duplicate email ambiguity safely rejected: {'PASS' if t8_pass else 'FAIL'} ({status}) - {body.get('detail')}")

conn = sqlite3.connect("C:/Users/callm/nagriksetu/backend/data/nagriksetu.db")
conn.execute("DELETE FROM guardians WHERE guardian_id = ?", (dup_guardian2,))
conn.execute("DELETE FROM users WHERE user_id IN (?, ?)", (dup_user1, dup_user2))
conn.commit()
conn.close()

# Test 9: JWT Role & Portal Authorization Checks
# A) Citizen calling /auth/me
status, body = get_protected_endpoint(email_token, "/auth/me")
t9a_pass = (status == 200 and body.get("role") == "parent")
results.append(("JWT validation on /auth/me returns role=parent", t9a_pass, f"Status {status}, role={body.get('role')}"))
print(f"Test 9a - JWT /auth/me role=parent: {'PASS' if t9a_pass else 'FAIL'} ({status})")

# B) Citizen trying to access Platform Admin endpoint (/admin/overview)
status, body = get_protected_endpoint(email_token, "/admin/overview")
t9b_pass = (status == 403)
results.append(("Citizen blocked from Platform Admin (/admin/overview)", t9b_pass, f"Status {status}, detail={body.get('detail')}"))
print(f"Test 9b - Citizen blocked from /admin/overview: {'PASS' if t9b_pass else 'FAIL'} ({status})")

# C) Citizen trying to access Institution Admin endpoint (/admin/institution-admins)
status, body = get_protected_endpoint(email_token, "/admin/institution-admins")
t9c_pass = (status == 403)
results.append(("Citizen blocked from Institution Admin endpoint", t9c_pass, f"Status {status}, detail={body.get('detail')}"))
print(f"Test 9c - Citizen blocked from /admin/institution-admins: {'PASS' if t9c_pass else 'FAIL'} ({status})")

# Test 10: Citizen Registration with Email Only
test_reg_email = f"test.citizen.reg.{int(time.time())}@example.com"
reg_payload = {
    "full_name": "Test Citizen Email Reg",
    "email": test_reg_email,
    "phone": None,
    "password": "Password@123!",
    "confirm_password": "Password@123!"
}
req = urllib.request.Request(
    f"{BASE_URL}/auth/register",
    data=json.dumps(reg_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req) as resp:
        reg_status = resp.status
        reg_data = json.loads(resp.read().decode("utf-8"))
        t10_pass = (reg_status == 201 and "user_id" in reg_data)
        results.append(("Citizen registration with Email Only", t10_pass, f"Status {reg_status}"))
        print(f"Test 10 - Registration with Email Only: {'PASS' if t10_pass else 'FAIL'} ({reg_status})")
        
        # Test login with this newly registered email account
        reg_log_status, reg_log_data = login_request(test_reg_email, "Password@123!")
        t10b_pass = (reg_log_status == 200 and reg_log_data.get("role") == "parent")
        results.append(("Login with newly registered email", t10b_pass, f"Status {reg_log_status}"))
        print(f"Test 10b - Login with Newly Registered Email: {'PASS' if t10b_pass else 'FAIL'} ({reg_log_status})")
        
        # Clean up test registration
        cleanup_conn = sqlite3.connect("C:/Users/callm/nagriksetu/backend/data/nagriksetu.db")
        cleanup_conn.execute("DELETE FROM guardians WHERE user_id = ?", (reg_data["user_id"],))
        cleanup_conn.execute("DELETE FROM users WHERE user_id = ?", (reg_data["user_id"],))
        cleanup_conn.commit()
        cleanup_conn.close()
except Exception as ex:
    print(f"Test 10 - Registration with Email Only: FAILED ({ex})")
    results.append(("Citizen registration with Email Only", False, str(ex)))

print("=" * 60)
passed_count = sum(1 for r in results if r[1])
total_count = len(results)
print(f"ALL TESTS SUMMARY: {passed_count}/{total_count} PASSED")
print("=" * 60)
