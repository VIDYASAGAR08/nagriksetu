import requests
import json
import pymysql

BASE_URL = "http://127.0.0.1:8003/api"

def audit_multiple_enrollments():
    # 1. Connect to MySQL to inspect citizen CIT-000127 (Mahesh)
    conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
    cur = conn.cursor()

    cur.execute("SELECT id, email, citizen_ref, student_id, full_name FROM accounts WHERE citizen_ref = 'CIT-000127';")
    mahesh_acc = cur.fetchone()
    print("Mahesh Account in MySQL:", mahesh_acc)
    stu_id = mahesh_acc[3]
    assert stu_id == "STU-2026-000081", f"Expected STU-2026-000081, got {stu_id}"

    # Query all enrolments for Mahesh in MySQL
    cur.execute("SELECT id, code, student_id, citizen_ref, status, centre_id FROM enrollments WHERE citizen_ref = 'CIT-000127' AND status IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED');")
    enr_rows = cur.fetchall()
    print(f"Total Enrolled/Completed records for CIT-000127: {len(enr_rows)}")
    for r in enr_rows:
        print(f"  DB Enrolment {r[1]} -> student_id={r[2]} (centre_id={r[5]})")
        assert r[2] == stu_id, f"Enrolment {r[1]} has student_id {r[2]} instead of {stu_id}"

    # 2. Authenticate via Registered Email
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": "mahesh@example.com", "password": "Password@123"})
    if login_res.status_code != 200:
        login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": "mahesh@example.com", "password": "Nagrik@2026"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert login_res.json()["is_student"] == True
    assert login_res.json()["student_id"] == stu_id
    print("[PASS] Authenticated Mahesh via Email + Password")

    # 3. Authenticate via Student ID
    stu_login = requests.post(f"{BASE_URL}/auth/login", json={"email": stu_id, "password": "Password@123"})
    if stu_login.status_code != 200:
        stu_login = requests.post(f"{BASE_URL}/auth/login", json={"email": stu_id, "password": "Nagrik@2026"})
    assert stu_login.status_code == 200
    assert stu_login.json()["student_id"] == stu_id
    assert stu_login.json()["citizen_ref"] == "CIT-000127"
    print("[PASS] Authenticated Mahesh via Student ID + Password")

    # 4. Retrieve Student Dashboard
    dash_res = requests.get(f"{BASE_URL}/student/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["student_id"] == stu_id
    print(f"Dashboard returned {len(dash_data['enrolments'])} enrolled programmes for Mahesh:")
    for idx, e in enumerate(dash_data["enrolments"]):
        print(f"  Program {idx+1}: {e['application_code']} | student_id={e['student_id']} | centre={e['centre']['name']} | status={e['status']}")
        assert e["student_id"] == stu_id, f"Dashboard programme has wrong student_id: {e['student_id']}"

    # 5. Verify Citizen A Applicant (CIT-000002) has unique and preserved STU-2026-000104
    cur.execute("SELECT id, email, citizen_ref, student_id, full_name FROM accounts WHERE citizen_ref = 'CIT-000002';")
    cit_a_acc = cur.fetchone()
    print("Citizen A Account in MySQL:", cit_a_acc)
    assert cit_a_acc[3] == "STU-2026-000104"
    assert cit_a_acc[3] != stu_id, "Different citizens must have different student IDs"

    conn.close()
    print("[ALL CHECKS PASSED] Citizen-to-Student-ID 1-to-1 Mapping Fully Verified!")

if __name__ == "__main__":
    audit_multiple_enrollments()
