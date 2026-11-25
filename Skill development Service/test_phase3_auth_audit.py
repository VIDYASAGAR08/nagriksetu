import requests
import json
import pymysql
import uuid

BASE_URL = "http://127.0.0.1:8003/api"

print("======================================================================")
print("PHASE 3: COMPREHENSIVE AUTHENTICATION & ACCOUNT MANAGEMENT AUDIT")
print("======================================================================")

# 1. Citizen Registration with Email OTP
unique_id = uuid.uuid4().hex[:8]
cit_email = f"audit.citizen.{unique_id}@nagriksetu.local"
cit_pass = "AuditPassword@123"

# Request OTP
otp_req = requests.post(f"{BASE_URL}/otp/send", json={"email": cit_email, "purpose": "REGISTRATION"})
print(f"1.1 OTP Request status: {otp_req.status_code}")
assert otp_req.status_code == 200, f"OTP request failed: {otp_req.text}"

# Retrieve OTP from database
conn = pymysql.connect(host="127.0.0.1", port=3308, user="nagriksetu_skill", password="skill-app-pass-2026", database="skill_db")
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT otp_code FROM email_otps WHERE email = %s ORDER BY id DESC LIMIT 1", (cit_email,))
otp_row = cur.fetchone()
assert otp_row is not None, "OTP not recorded in database"
otp_code = otp_row["otp_code"]
print(f"1.2 Retrieved OTP code from DB: {otp_code}")

# Register Citizen
reg_payload = {
    "full_name": f"Audit Citizen {unique_id}",
    "email": cit_email,
    "password": cit_pass,
    "otp_code": otp_code,
    "phone": "9876543210"
}
reg_res = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
print(f"1.3 Citizen registration status: {reg_res.status_code}")
assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
reg_data = reg_res.json()
assert reg_data["role"] == "CITIZEN", f"Expected CITIZEN role, got {reg_data.role}"
assert reg_data.get("is_student") == False, "New citizen must not have is_student=True"
assert reg_data.get("student_id") is None, "New citizen must not have student_id"
print(f"    Citizen registered: {reg_data['email']}, Ref: {reg_data['citizen_ref']}")

# Duplicate Registration Prevention
dup_res = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
print(f"1.4 Duplicate registration status: {dup_res.status_code} (Expected 400 or 409)")
assert dup_res.status_code in (400, 409), f"Duplicate allowed: {dup_res.status_code}"

# 1.5 Citizen Normal Login
login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": cit_email, "password": cit_pass})
print(f"1.5 Citizen Login status: {login_res.status_code}")
assert login_res.status_code == 200, f"Login failed: {login_res.text}"

# 2. Student Authentication Dual Identifier Check
# Citizen A Applicant has STU-2026-000104 and email citizen.a.1794036653893@nagriksetu.local
stu_email = "citizen.a.1794036653893@nagriksetu.local"
stu_id = "STU-2026-000104"
stu_pass = "Password@123"

# 2.1 Login via Email
stu_login_email = requests.post(f"{BASE_URL}/auth/login", json={"email": stu_email, "password": stu_pass})
assert stu_login_email.status_code == 200
data_e = stu_login_email.json()
assert data_e["is_student"] == True
assert data_e["student_id"] == stu_id
print(f"2.1 Student login via Email: PASS (is_student=True, student_id={data_e['student_id']})")

# 2.2 Login via Student ID
stu_login_id = requests.post(f"{BASE_URL}/auth/login", json={"email": stu_id, "password": stu_pass})
assert stu_login_id.status_code == 200
data_i = stu_login_id.json()
assert data_i["is_student"] == True
assert data_i["student_id"] == stu_id
assert data_i["email"] == stu_email
print(f"2.2 Student login via Student ID: PASS (Resolved email: {data_i['email']})")

# 2.3 Non-enrolled Citizen blocked from Student Dashboard
cit_tok = login_res.json()["access_token"]
dash_blocked = requests.get(f"{BASE_URL}/student/dashboard", headers={"Authorization": f"Bearer {cit_tok}"})
print(f"2.3 Non-enrolled citizen dashboard access status: {dash_blocked.status_code} (Expected 403)")
assert dash_blocked.status_code == 403, f"Non-enrolled citizen not blocked: {dash_blocked.status_code}"

# 3. Training Centre Admin Login & Centre Isolation
# Centre Admin Mysuru (centre_id = 2)
tc_login_mysuru = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "centre.admin.mysuru@nagriksetu.local",
    "password": "Password@123"
})
assert tc_login_mysuru.status_code == 200
tc_mysuru_data = tc_login_mysuru.json()
assert tc_mysuru_data["role"] == "TRAINING_CENTRE_ADMIN"
assert tc_mysuru_data["centre_id"] == 2
print(f"3.1 Mysuru Centre Admin login: PASS (centre_id={tc_mysuru_data['centre_id']})")

# Centre Admin Bengaluru (centre_id = 1)
tc_login_blr = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "centre.bengaluru@nagriksetu.local",
    "password": "Password@123"
})
assert tc_login_blr.status_code == 200
tc_blr_tok = tc_login_blr.json()["access_token"]

# Bengaluru tries to access Shivamogga student search
blr_cross_search = requests.get(
    f"{BASE_URL}/centre-admin/students/search?q=STU-2026-000104",
    headers={"Authorization": f"Bearer {tc_blr_tok}", "X-Centre-ID": "1"}
)
assert blr_cross_search.status_code == 200
assert len(blr_cross_search.json()) == 0, f"Centre isolation breach! Bengaluru saw Shivamogga student: {blr_cross_search.json()}"
print("3.2 Centre isolation check: PASS (Bengaluru centre received 0 results for Shivamogga student)")

# 4. Platform Admin Strict View-Only Check
adm_login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "skill.admin@nagriksetu.local",
    "password": "SkillAdmin@2026!"
})
assert adm_login.status_code == 200
adm_tok = adm_login.json()["access_token"]

# Platform admin attempt write
adm_write = requests.post(
    f"{BASE_URL}/admin/skills",
    headers={"Authorization": f"Bearer {adm_tok}"},
    json={
        "name": "Audit Blocked Skill", "category_id": 1, "category_name": "IT",
        "level": "Basic", "duration_weeks": 2, "duration_hours": 20, "summary": "s",
        "details": "d", "prerequisites": "p", "learning_objectives": "o",
        "learning_outcomes": "out", "relevant_industries": "ind"
    }
)
assert adm_write.status_code == 403, f"Platform admin write not blocked with 403: {adm_write.status_code}"
print(f"4.1 Platform Admin write blocked: PASS (Status 403)")

# 5. Project Owner Authentication Check
po_login = requests.post(f"{BASE_URL}/auth/project-owner-login", json={
    "owner_secret": "NAGRIKSETU_PROJECT_OWNER_MASTER_2026_AUTHORISED"
})
print(f"5.1 Project Owner login status: {po_login.status_code}")
assert po_login.status_code == 200
po_data = po_login.json()
assert po_data["role"] == "PROJECT_OWNER"
print(f"    Project Owner authenticated: {po_data['role']}, Name: {po_data['full_name']}")

conn.close()
print("======================================================================")
print("PHASE 3 COMPLETE: ALL AUTHENTICATION & RBAC CHECKS PASSED (100%)")
print("======================================================================")
