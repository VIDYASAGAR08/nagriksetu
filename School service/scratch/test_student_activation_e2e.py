import requests
import sqlite3
import json

BASE_URL = "http://localhost:8001"

def run_e2e():
    print("=== NagrikSetu Student Activation E2E Test ===")
    
    # 0. Check DB student count before
    conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM students")
    count_before = cur.fetchone()[0]
    print(f"Total students in DB before: {count_before}")
    
    # Check if user already exists for Ishaan Verma / SCH19956, clean up for test if needed
    cur.execute("SELECT user_id, email, permanent_student_id, student_id FROM users WHERE permanent_student_id IN ('NS-SCH019-STD06-166', 'SCH19956') OR student_id IN ('NS-SCH019-STD06-166', 'SCH19956') OR email = 'ishaan.verma@example.com'")
    existing_users = cur.fetchall()
    if existing_users:
        print(f"Cleaning existing test user records: {existing_users}")
        for uid, email, psid, sid in existing_users:
            cur.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        conn.commit()
    conn.close()

    # 1. Step 1 Lookup
    print("\n[Step 1] Student Lookup for NS-SCH019-STD06-166")
    resp = requests.post(f"{BASE_URL}/auth/student/lookup", json={"student_identifier": "NS-SCH019-STD06-166"})
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print("Response:", json.dumps(data, indent=2))
    assert resp.status_code == 200
    assert data["official_student_name"] == "Ishaan Verma"
    assert data["institution_id"] == "SCH019"
    assert data["institution_name"] == "Ballari Education School"
    assert data["standard_display"] == "Standard 6"
    assert data["section_display"] == "Section C"
    print("[PASS] Step 1 Lookup PASSED")

    # 2. Step 2 Wrong DOB Activation
    print("\n[Step 2] Identity Verification with incorrect DOB (2015-01-01)")
    resp_wrong = requests.post(f"{BASE_URL}/auth/student/register", json={
        "student_identifier": "NS-SCH019-STD06-166",
        "date_of_birth": "2015-01-01",
        "password": "Password@123",
        "confirm_password": "Password@123",
        "email": "ishaan.verma@example.com",
        "phone": "9876543210"
    })
    print(f"Status: {resp_wrong.status_code}")
    print("Response:", resp_wrong.json())
    assert resp_wrong.status_code == 400
    assert "Identity verification failed" in resp_wrong.json()["detail"]
    print("[PASS] Step 2 Identity verification rejection PASSED")

    # 3. Step 3 Correct DOB Activation
    print("\n[Step 3] Activation with matching DOB (2015-06-15)")
    resp_correct = requests.post(f"{BASE_URL}/auth/student/register", json={
        "student_identifier": "NS-SCH019-STD06-166",
        "date_of_birth": "2015-06-15",
        "password": "Password@123",
        "confirm_password": "Password@123",
        "email": "ishaan.verma@example.com",
        "phone": "9876500166"
    })
    print(f"Status: {resp_correct.status_code}")
    print("Response:", resp_correct.json())
    assert resp_correct.status_code == 201
    act_data = resp_correct.json()
    assert act_data["full_name"] == "Ishaan Verma"
    assert act_data["permanent_student_id"] == "NS-SCH019-STD06-166"
    print("[PASS] Step 3 Account Activation PASSED")

    # 4. Step 4 Re-lookup should report already activated
    print("\n[Step 4] Re-lookup for NS-SCH019-STD06-166")
    resp_relookup = requests.post(f"{BASE_URL}/auth/student/lookup", json={"student_identifier": "NS-SCH019-STD06-166"})
    print(f"Status: {resp_relookup.status_code}")
    print("Response:", resp_relookup.json())
    assert resp_relookup.status_code == 400
    assert "Student account already activated" in resp_relookup.json()["detail"]
    print("[PASS] Step 4 Duplicate activation prevention PASSED")

    # 5. Step 5 Login with newly activated credentials
    print("\n[Step 5] Login with student identifier and password")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "NS-SCH019-STD06-166",
        "password": "Password@123"
    })
    print(f"Status: {login_resp.status_code}")
    login_data = login_resp.json()
    print("Login Data:", json.dumps({k: v for k, v in login_data.items() if k != "access_token"}, indent=2))
    assert login_resp.status_code == 200
    assert login_data["role"] == "student"
    assert login_data["school_id"] == "SCH019"
    assert login_data["permanent_student_id"] == "NS-SCH019-STD06-166"
    assert "access_token" in login_data

    # Test /auth/me with access_token
    token = login_data["access_token"]
    me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    print("User /auth/me:", json.dumps(me_data, indent=2))
    assert me_data["role"] == "student"
    assert me_data["full_name"] == "Ishaan Verma"
    assert me_data["permanent_student_id"] == "NS-SCH019-STD06-166"
    print("[PASS] Step 5 Student Portal Login & /auth/me PASSED")

    # 6. Check DB student count after
    conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM students")
    count_after = cur.fetchone()[0]
    print(f"\nTotal students in DB after: {count_after}")
    assert count_before == count_after, "Student count changed!"
    print("[PASS] DB integrity check PASSED (No duplicate student records created)")
    conn.close()

if __name__ == "__main__":
    run_e2e()
