import subprocess
import time
import os
import requests
import json
import sqlite3

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

# 1. Connect to SQLite to check SCH019 users
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("""
    SELECT u.user_id, u.email, u.full_name, u.role, uir.institution_id, uir.role_id as inst_role, isp.can_approve_stage1
    FROM users u
    JOIN user_institution_roles uir ON u.user_id = uir.user_id
    LEFT JOIN institution_staff_permissions isp ON u.user_id = isp.user_id AND uir.institution_id = isp.institution_id
    WHERE uir.institution_id = 'SCH019'
""")
rows = cur.fetchall()
print("SCH019 Users in DB:")
for r in rows:
    print(dict(r))
conn.close()

# 2. Get tokens
# Admin token for SCH019
res_adm = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "admin.sch019@gmail.com", "password": "Admin@NagrikSetu2026!"}
)
print("Admin login response:", res_adm.status_code)
sch019_admin_token = res_adm.json().get("access_token", "")

# Admissions Officer token for SCH019
res_adm_off = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "test.admissions.sch019@example.com", "password": "Password@1234567!"}
)
print("Admissions Officer login response:", res_adm_off.status_code)
admissions_officer_token = res_adm_off.json().get("access_token", "")

# Student Records Officer token for SCH019
res_rec = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "records.sch019@example.com", "password": "RecordsPassword123!"}
)
print("Records Officer login response:", res_rec.status_code)
records_officer_token = res_rec.json().get("access_token", "")

# Let's find user_id for test.admissions.sch019@example.com
admissions_user_id = ""
for r in rows:
    if r["email"] == "test.admissions.sch019@example.com":
        admissions_user_id = r["user_id"]
        break

print(f"Admissions user id: {admissions_user_id}")

targets = [
    # 1. Staff Management Tab on SCH019 Admin Dashboard
    (
        f"http://localhost:5173/auth_bootstrap.html?token={sch019_admin_token}&role=school_admin&school_id=SCH019&email=admin.sch019@gmail.com&full_name=Admin19&target=%2F%23%2Finstitution-admin%3Ftab%3Dstaff",
        "staff_management_tab_sch019.png",
        "Institution Admin Staff Management Section"
    ),
    # 2. Invite Staff Modal
    (
        f"http://localhost:5173/auth_bootstrap.html?token={sch019_admin_token}&role=school_admin&school_id=SCH019&email=admin.sch019@gmail.com&full_name=Admin19&target=%2F%23%2Finstitution-admin%3Ftab%3Dstaff%26modal%3Dinvite",
        "invite_staff_modal.png",
        "Invite Staff Member Modal with Role & Permissions"
    ),
    # 3. Staff Permissions Modal for Admissions Officer
    (
        f"http://localhost:5173/auth_bootstrap.html?token={sch019_admin_token}&role=school_admin&school_id=SCH019&email=admin.sch019@gmail.com&full_name=Admin19&target=%2F%23%2Finstitution-admin%3Ftab%3Dstaff%26staff_id%3D{admissions_user_id}",
        "staff_permissions_modal.png",
        "Staff Permissions Configuration Modal"
    ),
    # 4. Staff Activity Audit Modal for Admissions Officer
    (
        f"http://localhost:5173/auth_bootstrap.html?token={sch019_admin_token}&role=school_admin&school_id=SCH019&email=admin.sch019@gmail.com&full_name=Admin19&target=%2F%23%2Finstitution-admin%3Ftab%3Dstaff%26staff_id%3D{admissions_user_id}%26subtab%3Dactivity",
        "staff_activity_modal.png",
        "Staff Activity & Audit Trail Modal"
    ),
    # 5. Admissions Officer Dashboard (/staff)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={admissions_officer_token}&role=admissions_officer&school_id=SCH019&email=test.admissions.sch019@example.com&full_name=Test+Admissions+Officer&target=%2F%23%2Fstaff%3Ftab%3Dadmissions",
        "admissions_officer_dashboard.png",
        "Admissions Officer Staff Dashboard"
    ),
    # 6. Student Records Officer Dashboard (/staff)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={records_officer_token}&role=student_records_officer&school_id=SCH019&email=records.sch019@example.com&full_name=Student+Records+Officer&target=%2F%23%2Fstaff%3Ftab%3Dstudents",
        "records_officer_dashboard.png",
        "Student Records Officer Staff Dashboard"
    )
]

for url, filename, desc in targets:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,950",
        "--virtual-time-budget=7000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)

print("All screenshots captured!")
