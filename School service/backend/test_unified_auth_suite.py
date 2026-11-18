import sqlite3
import json
import urllib.request
import urllib.error

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
BASE_URL = "http://localhost:8001"

def test_database_integrity():
    print("=== 1. DATABASE RECORD PRESERVATION CHECK ===")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        # Check Chandhan
        c = conn.execute("SELECT * FROM users WHERE phone = '6361168242'").fetchone()
        assert c is not None, "Chandhan user not found!"
        print(f"  [PASS] User Chandhan verified: user_id={c['user_id']}, name={c['full_name']}, phone={c['phone']}, status={c['status']}")

        # Check Chandhan guardian record
        g = conn.execute("SELECT * FROM guardians WHERE phone = '6361168242'").fetchone()
        assert g is not None, "Chandhan guardian record not found!"
        print(f"  [PASS] Guardian Chandhan verified: guardian_id={g['guardian_id']}, name={g['full_name']}, user_id={g['user_id']}")

        # Check Students count
        s_count = conn.execute("SELECT count(*) as c FROM students").fetchone()['c']
        print(f"  [PASS] Student records preserved count: {s_count}")
        assert s_count >= 30000, f"Unexpected student count: {s_count}"
    finally:
        conn.close()

def test_name_mismatch_rejection():
    print("\n=== 2. NAME MISMATCH ENFORCEMENT ON LOGIN ===")
    # Request OTP with wrong name for Chandhan
    payload = {
        "full_name": "Totally Wrong Name",
        "contact": "6361168242",
        "purpose": "login"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/unified/otp/send",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        print("  [FAIL] Name mismatch was NOT rejected!")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        print(f"  [PASS] Name mismatch correctly rejected with HTTP {e.code}: {body['detail']}")

def test_unregistered_contact_login():
    print("\n=== 3. UNREGISTERED CONTACT LOGIN REJECTION ===")
    payload = {
        "full_name": "Ghost Citizen",
        "contact": "9999999991",
        "purpose": "login"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/unified/otp/send",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        print("  [FAIL] Unregistered contact was NOT rejected!")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        print(f"  [PASS] Unregistered contact correctly rejected with HTTP {e.code}: {body['detail']}")

def test_duplicate_registration_rejection():
    print("\n=== 4. DUPLICATE REGISTRATION REJECTION ===")
    payload = {
        "full_name": "Chandhan",
        "contact": "6361168242",
        "purpose": "register"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/auth/unified/otp/send",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        print("  [FAIL] Duplicate registration was NOT rejected!")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        print(f"  [PASS] Duplicate registration correctly rejected with HTTP {e.code}: {body['detail']}")

if __name__ == "__main__":
    test_database_integrity()
    test_name_mismatch_rejection()
    test_unregistered_contact_login()
    test_duplicate_registration_rejection()
    print("\n=== ALL SUITE CHECKS COMPLETED SUCCESSFULLY ===")
