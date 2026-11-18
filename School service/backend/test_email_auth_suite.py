import os
import sys
import sqlite3
import datetime
import json
import urllib.request
import urllib.error
import uuid

# Ensure clean utf-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import email_service
from auth import hash_password

DB_PATH = os.getenv("DATABASE_PATH", "/app/data/nagriksetu.db")
if not os.path.exists(DB_PATH):
    # fallback to local path if running outside container
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "nagriksetu.db"))

BASE_URL = "http://127.0.0.1:8000" if os.path.exists("/app") else "http://localhost:8001"

passed_tests = []
failed_tests = []

def record(test_name: str, passed: bool, message: str = ""):
    if passed:
        passed_tests.append(test_name)
        print(f"  [PASS] {test_name}")
    else:
        failed_tests.append((test_name, message))
        print(f"  [FAIL] {test_name}: {message}")

print("==================================================================")
print("  NAGRIKSETU SCHOOL SERVICE: EMAIL AUTHENTICATION TEST SUITE")
print("==================================================================")

# 1. Email normalization & format validation
print("\n--- 1. Email Normalization & Validation ---")
try:
    normalized = email_service.normalize_email("  Test.User@Karnataka.Gov.IN  ")
    assert normalized == "test.user@karnataka.gov.in", f"Unexpected normalized: {normalized}"
    record("Email lowercasing & whitespace trimming", True)
except Exception as e:
    record("Email lowercasing & whitespace trimming", False, str(e))

try:
    try:
        email_service.normalize_email("invalid-email-address")
        record("Invalid email format rejection", False, "Should have raised ValueError")
    except ValueError:
        record("Invalid email format rejection", True)
except Exception as e:
    record("Invalid email format rejection", False, str(e))

# 2. Six-digit OTP generation
print("\n--- 2. Six-Digit OTP Generation ---")
try:
    otps = [email_service.generate_email_otp() for _ in range(50)]
    all_valid = all(len(o) == 6 and o.isdigit() and int(o) >= 100000 for o in otps)
    record("6-digit numeric OTP generation (100000-999999)", all_valid)
except Exception as e:
    record("6-digit numeric OTP generation (100000-999999)", False, str(e))

# 3. Salted SHA-256 Hashing & Verification
print("\n--- 3. Salted SHA-256 OTP Hashing & Verification ---")
try:
    test_email = "citizen.test@example.com"
    plain_otp = "482915"
    h1 = email_service.hash_email_otp(test_email, plain_otp)
    h2 = email_service.hash_email_otp(test_email, plain_otp)
    assert h1 == h2, "Hash should be deterministic for same email + salt + OTP"
    assert email_service.verify_email_otp_hash(test_email, plain_otp, h1), "Verification of correct OTP must succeed"
    assert not email_service.verify_email_otp_hash(test_email, "999999", h1), "Verification of incorrect OTP must fail"
    record("Salted SHA-256 hash & constant-time verify", True)
except Exception as e:
    record("Salted SHA-256 hash & constant-time verify", False, str(e))

# 4. Database schema verification
print("\n--- 4. Database Schema Integrity ---")
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Check users table has is_email_verified
    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]
    assert "is_email_verified" in cols, "Column is_email_verified missing from users table"
    # Check email_otps table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_otps'")
    assert cursor.fetchone() is not None, "Table email_otps missing"
    conn.close()
    record("Schema verification (is_email_verified column & email_otps table)", True)
except Exception as e:
    record("Schema verification (is_email_verified column & email_otps table)", False, str(e))

# 5. API Registration & Security Controls Flow
print("\n--- 5. Email Registration & Security Controls ---")
unique_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
suite_test_email = f"citizen_suite_{unique_suffix}@nagriksetu.internal"
suite_password = "SecurePassword@2026"
mock_otp = "654321"
clean_email = email_service.normalize_email(suite_test_email)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert an OTP record into email_otps with known hash and purpose='register'
    otp_hash = email_service.hash_email_otp(clean_email, mock_otp)
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    expires_str = (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO email_otps (email, otp_hash, purpose, attempts, max_attempts, is_used, expires_at, created_at, ip_address)
        VALUES (?, ?, 'register', 0, 5, 0, ?, ?, '127.0.0.1')
    """, (clean_email, otp_hash, expires_str, now_str))
    conn.commit()
    conn.close()
    record("Pre-staged test OTP record with purpose='register'", True)
except Exception as e:
    record("Pre-staged test OTP record with purpose='register'", False, str(e))

# Test: Registration with wrong OTP rejected
try:
    payload = {
        "full_name": "Suite Test Citizen",
        "email": suite_test_email,
        "password": suite_password,
        "confirm_password": suite_password,
        "otp": "000000"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/email/register",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        record("Wrong OTP registration rejection", False, "Expected 400 Bad Request")
    except urllib.error.HTTPError as he:
        body = he.read().decode("utf-8")
        assert he.code == 400 and "Incorrect verification code" in body, f"Unexpected body: {body}"
        record("Wrong OTP registration rejection", True)
except Exception as e:
    record("Wrong OTP registration rejection", False, str(e))

# Test: Registration with correct OTP succeeds
try:
    payload = {
        "full_name": "Suite Test Citizen",
        "email": suite_test_email,
        "password": suite_password,
        "confirm_password": suite_password,
        "otp": mock_otp
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/email/register",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode("utf-8"))
    assert res.status in (200, 201), f"Expected 200 or 201, got {res.status}"
    assert "access_token" in data, "Response must include JWT access_token"
    assert data["role"] == "parent", "Role must be parent"
    record("Successful registration with valid OTP", True)
except Exception as e:
    record("Successful registration with valid OTP", False, str(e))

# Test: Replay protection (re-submitting same used OTP fails)
try:
    payload = {
        "full_name": "Duplicate Submit",
        "email": suite_test_email,
        "password": suite_password,
        "confirm_password": suite_password,
        "otp": mock_otp
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/email/register",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        record("Replay protection (consumed OTP rejection)", False, "Expected error")
    except urllib.error.HTTPError as he:
        assert he.code in (400, 409), f"Expected 400 or 409, got {he.code}"
        record("Replay protection (consumed OTP rejection)", True)
except Exception as e:
    record("Replay protection (consumed OTP rejection)", False, str(e))

# 6. Email login
print("\n--- 6. Email Login & Password Verification ---")
try:
    payload = {
        "email": suite_test_email,
        "password": suite_password
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/email/login",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    login_data = json.loads(res.read().decode("utf-8"))
    assert res.status == 200, f"Expected 200, got {res.status}"
    assert "access_token" in login_data, "Login response must contain access_token"
    assert login_data["user"]["role"] == "parent", "User role must be parent"
    record("Email & Password Login (POST /auth/email/login)", True)
except Exception as e:
    record("Email & Password Login (POST /auth/email/login)", False, str(e))

# Test: Wrong password rejection
try:
    payload = {
        "email": suite_test_email,
        "password": "WrongPassword999!"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/email/login",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        record("Incorrect password rejection (HTTP 401)", False, "Expected 401 Unauthorized")
    except urllib.error.HTTPError as he:
        assert he.code == 401, f"Expected 401, got {he.code}"
        record("Incorrect password rejection (HTTP 401)", True)
except Exception as e:
    record("Incorrect password rejection (HTTP 401)", False, str(e))

# 7. Unverified email account block
print("\n--- 7. Unverified Email Block Enforcement ---")
unverified_email = f"unverified_{unique_suffix}@nagriksetu.internal"
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    p_hash = hash_password("TestUnverified123!")
    cursor.execute("""
        INSERT INTO users (user_id, full_name, email, password_hash, role, is_active, status, is_email_verified, created_at)
        VALUES (?, 'Unverified Parent', ?, ?, 'parent', 1, 'active', 0, ?)
    """, (f"usr_unv_{unique_suffix[:8]}", unverified_email, p_hash, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

    # Attempt login
    payload = {"email": unverified_email, "password": "TestUnverified123!"}
    req = urllib.request.Request(
        f"{BASE_URL}/auth/email/login",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        record("Unverified account login block (HTTP 403)", False, "Expected 403 Forbidden")
    except urllib.error.HTTPError as he:
        assert he.code == 403, f"Expected 403 Forbidden, got {he.code}"
        record("Unverified account login block (HTTP 403)", True)
except Exception as e:
    record("Unverified account login block (HTTP 403)", False, str(e))

# 8. Preservation of Existing Mobile & Database Accounts
print("\n--- 8. Database Baseline & Existing Accounts Preservation ---")
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, phone, role FROM users WHERE phone = '6361168242'")
    chandhan = cursor.fetchone()
    assert chandhan is not None, "Chandhan account (6361168242) must exist"
    assert chandhan[2] == "parent", f"Expected parent role, got {chandhan[2]}"
    
    # Check student-guardian relationship via guardians join
    cursor.execute("""
        SELECT sg.student_guardian_id, sg.permanent_student_id, sg.is_verified 
        FROM student_guardians sg
        JOIN guardians g ON sg.guardian_id = g.guardian_id
        WHERE g.user_id = ?
    """, (chandhan[0],))
    rel = cursor.fetchone()
    assert rel is not None, "Verified guardian relationship for Asha Sharma must exist"
    assert rel[2] == 1, "Relationship must be verified"
    
    # Check total student count preserved
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]
    assert student_count >= 30000, f"Expected >= 30,000 students, got {student_count}"
    conn.close()
    record(f"Preserved Chandhan (6361168242), Asha Sharma link & {student_count} students", True)
except Exception as e:
    record("Preserved Chandhan (6361168242) & student count", False, str(e))

# Clean up synthetic test records
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email IN (?, ?)", (suite_test_email, unverified_email))
    cursor.execute("DELETE FROM email_otps WHERE email = ?", (clean_email,))
    conn.commit()
    conn.close()
except Exception:
    pass

print("\n==================================================================")
print(f"  TEST SUITE RESULTS: {len(passed_tests)} PASSED, {len(failed_tests)} FAILED")
print("==================================================================")

if failed_tests:
    sys.exit(1)
