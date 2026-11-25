import requests
import json
import pymysql

BASE_URL = "http://127.0.0.1:8003/api"

print("======================================================================")
print("PHASE 4: FULL END-TO-END WORKFLOW VERIFICATION")
print("======================================================================")

# -------------------------------------------------------------------
# 1. CITIZEN WORKFLOW
# -------------------------------------------------------------------
print("\n--- 1. Testing Citizen Workflow ---")

# 1.1 Login Citizen
cit_login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "citizen.a.1794036653893@nagriksetu.local",
    "password": "Password@123"
})
assert cit_login.status_code == 200, f"Citizen login failed: {cit_login.status_code}"
cit_tok = cit_login.json()["access_token"]
cit_headers = {"Authorization": f"Bearer {cit_tok}"}
print("[PASS] 1.1 Citizen Authenticated successfully")

# 1.2 Browse Skills Catalogue
skills_res = requests.get(f"{BASE_URL}/skills")
assert skills_res.status_code == 200
skills_list = skills_res.json()
assert len(skills_list) > 0, "No skills found"
print(f"[PASS] 1.2 Browse Skills Catalogue: {len(skills_list)} skills retrieved")

# 1.3 Browse Training Programmes
progs_res = requests.get(f"{BASE_URL}/programmes")
assert progs_res.status_code == 200
progs_list = progs_res.json()
assert len(progs_list) > 0, "No programmes found"
print(f"[PASS] 1.3 Browse Training Programmes: {len(progs_list)} programmes retrieved")

# 1.4 Browse Training Centres
centres_res = requests.get(f"{BASE_URL}/centres")
assert centres_res.status_code == 200
centres_list = centres_res.json()
assert len(centres_list) > 0, "No centres found"
print(f"[PASS] 1.4 Browse Training Centres: {len(centres_list)} centres retrieved")

# 1.5 Inspect Institutional Profile (Centre 11 - Shivamogga)
centre_detail = requests.get(f"{BASE_URL}/centres/11/profile")
assert centre_detail.status_code == 200
cd_data = centre_detail.json()
print(f"[PASS] 1.5 Inspect Centre Profile: {cd_data.get('name')}, District: {cd_data.get('district')}")

# 1.6 View Batches for Program 19 at Centre 11 (via Program Detail endpoint)
prog_detail = requests.get(f"{BASE_URL}/programmes/19")
assert prog_detail.status_code == 200
p_data = prog_detail.json()
batches_list = p_data.get("batches", [])
assert len(batches_list) > 0, "No batches found for Program 19"
print(f"[PASS] 1.6 Batches for Program 19: {len(batches_list)} batch records (First batch: {batches_list[0]['code']}, Status: {batches_list[0]['status']}, Available Seats: {batches_list[0]['available_seats']})")

# 1.7 View Citizen's My Applications / Enrolments
my_apps_res = requests.get(f"{BASE_URL}/enrollments/me", headers=cit_headers)
assert my_apps_res.status_code == 200
my_apps = my_apps_res.json()
print(f"[PASS] 1.7 My Applications: {len(my_apps)} application records retrieved for Citizen A")

# -------------------------------------------------------------------
# 2. TRAINING CENTRE ADMIN WORKFLOW
# -------------------------------------------------------------------
print("\n--- 2. Testing Training Centre Admin Workflow (Shivamogga - Centre 11) ---")

# 2.1 Login Centre Admin
tc_login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "centre.shivamogga@nagriksetu.local",
    "password": "ShivamoggaMal#2026"
})
assert tc_login.status_code == 200
tc_tok = tc_login.json()["access_token"]
tc_headers = {"Authorization": f"Bearer {tc_tok}", "X-Centre-ID": "11"}
print("[PASS] 2.1 Shivamogga Centre Admin Authenticated successfully")

# 2.2 View Centre-scoped Applications
tc_apps_res = requests.get(f"{BASE_URL}/centre-admin/enrollments", headers=tc_headers)
assert tc_apps_res.status_code == 200
tc_apps = tc_apps_res.json()
assert all(app.get("centre_id") == 11 for app in tc_apps), "Centre isolation breach in applications view!"
print(f"[PASS] 2.2 Centre Applications: {len(tc_apps)} applications, 100% centre-isolated to Centre 11")

# 2.3 Search Students at Centre
tc_stu_res = requests.get(f"{BASE_URL}/centre-admin/enrollments?q=STU-2026-000104", headers=tc_headers)
assert tc_stu_res.status_code == 200
tc_stu_list = tc_stu_res.json()
assert len(tc_stu_list) > 0, "Expected student STU-2026-000104 not found in Centre 11 search"
print(f"[PASS] 2.3 Search Student Record: Found {tc_stu_list[0]['student_id']} ({tc_stu_list[0]['citizen_name']})")

# -------------------------------------------------------------------
# 3. STUDENT PORTAL WORKFLOW
# -------------------------------------------------------------------
print("\n--- 3. Testing Student Portal Workflow ---")

# 3.1 Student Dashboard Access
stu_dash_res = requests.get(f"{BASE_URL}/student/dashboard", headers=cit_headers)
assert stu_dash_res.status_code == 200
dash = stu_dash_res.json()
assert dash["student_id"] == "STU-2026-000104"
assert len(dash["enrolments"]) > 0
enr = dash["enrolments"][0]
print(f"[PASS] 3.1 Student Dashboard Loaded for {dash['student_id']}")
print(f"       Programme: {enr['program_title']}")
print(f"       Assigned Batch: {enr['batch']['batch_name']} (Mode: {enr['batch']['mode']})")
print(f"       Assigned Trainer: {enr['batch']['assigned_trainer']}")
print(f"       Attendance: {enr['attendance_pct']}% ({len(enr['attendance'])} records)")
print(f"       Modules: {len(enr['modules'])} records, overall progress: {enr['training_progress_pct']}%")

print("\n======================================================================")
print("PHASE 4 COMPLETE: ALL WORKFLOW VERIFICATIONS PASSED (100%)")
print("======================================================================")
