# -*- coding: utf-8 -*-
import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

print("==================================================================")
print("CAPTURING PHASE 12 ACADEMIC MANAGEMENT SCREENSHOTS")
print("==================================================================")

# 1. Login as Student (Asha Sharma SCH01125)
res_student = requests.post(
    f"{base_url}/auth/login",
    data={"username": "SCH01125", "password": "Password@2026!"}
)
student_auth = res_student.json()
student_token = student_auth.get("access_token")

# 2. Login as Parent (9876543210)
res_parent = requests.post(
    f"{base_url}/auth/login",
    data={"username": "9876543210", "password": "Str0ngPass!2026"}
)
parent_auth = res_parent.json()
parent_token = parent_auth.get("access_token")

# 3. Login as Institution Admin (SCH001)
res_admin = requests.post(
    f"{base_url}/auth/login?institution_id=SCH001",
    data={"username": "admin.sch001@example.com", "password": "Admin@NagrikSetu2026!"}
)
admin_auth = res_admin.json()
admin_token = admin_auth.get("access_token")

# 4. Login as Institution Staff (SCH001)
res_staff = requests.post(
    f"{base_url}/auth/login",
    data={"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"}
)
staff_auth = res_staff.json()
staff_token = staff_auth.get("access_token")

screenshots = [
    # 1. Official Student Academic Dashboard
    (
        f"http://localhost:5173/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fstudent",
        "phase12_student_academic_dashboard.png",
        "Official Student Academic & Performance Dashboard (Asha Sharma - SCH01125)"
    ),
    # 2. Institution Admin Academic Supervision Desk
    (
        f"http://localhost:5173/auth_bootstrap.html?token={admin_token}&role=school_admin&school_id=SCH001&email=admin.sch001@example.com&full_name=Sri.+Venkatesh&target=%2F%23%2Finstitution-admin%3Ftab%3Dacademics",
        "phase12_institution_admin_academic_desk.png",
        "Institution Administrator Academic Management & Supervision Desk (SCH001)"
    ),
    # 3. Institution Staff Academic & Attendance Desk
    (
        f"http://localhost:5173/auth_bootstrap.html?token={staff_token}&role=school_staff&school_id=SCH001&email=staff.sch001@example.com&full_name=Smt.+Shailaja&target=%2F%23%2Fstaff%3Ftab%3Dacademics",
        "phase12_staff_academic_desk.png",
        "Institution Staff Daily Attendance & Marks Entry Desk (SCH001)"
    ),
    # 4. Parent Portal Child Academic Records View
    (
        f"http://localhost:5173/auth_bootstrap.html?token={parent_token}&role=parent&email=parent@example.com&full_name=Sri.+Ramesh+Sharma&target=%2F%23%2Fparent",
        "phase12_parent_portal_dashboard.png",
        "Parent Portal Dashboard with Linked Children & Academic Ledgers"
    ),
]

for url, filename, desc in screenshots:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,1050",
        "--virtual-time-budget=8000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)

print("All Phase 12 academic verification screenshots captured successfully!")
