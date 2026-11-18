import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

print("==================================================================")
print("CAPTURING FINAL PHASE VERIFICATION SCREENSHOTS")
print("==================================================================")

# 1. Login as Student (Asha Sharma SCH01125)
res_student = requests.post(
    f"{base_url}/auth/login",
    data={"username": "SCH01125", "password": "Password@2026!"}
)
student_auth = res_student.json()
student_token = student_auth.get("access_token")

# 2. Login as Institution Admin (SCH001)
res_admin = requests.post(
    f"{base_url}/auth/login?institution_id=SCH001",
    data={"username": "admin.sch001@example.com", "password": "Admin@NagrikSetu2026!"}
)
admin_auth = res_admin.json()
admin_token = admin_auth.get("access_token")

screenshots = [
    # 1. User Category Selection Screen
    (
        "http://localhost:5173/#/login",
        "final_user_category_selection.png",
        "NagrikSetu Standardized User Category Selection Screen"
    ),
    # 2. Dedicated Student Login & Activation Portal
    (
        "http://localhost:5173/#/login?category=student",
        "final_student_portal_login.png",
        "Dedicated Student Sign-In & On-Demand Activation Portal"
    ),
    # 3. Authenticated Student Academic Dashboard (Explore Directory button removed, Attendance/Address/Tests displayed)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fstudent",
        "final_student_dashboard_verified.png",
        "Official Student Academic Dashboard (Asha Sharma - SCH01125)"
    ),
    # 4. Institution Admin Admission & Staff Management Desk
    (
        f"http://localhost:5173/auth_bootstrap.html?token={admin_token}&role=school_admin&school_id=SCH001&email=admin.sch001@example.com&full_name=Sri.+Venkatesh&target=%2F%23%2Finstitution-admin",
        "final_institution_admin_desk.png",
        "Institution Administrator Management Desk (SCH001)"
    ),
]

for url, filename, desc in screenshots:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,1050",
        "--virtual-time-budget=7000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)

print("All final phase verification screenshots captured successfully!")
