import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

print("==================================================================")
print("CAPTURING PHASE 14 NOTIFICATION MANAGEMENT TELEMETRY SCREENSHOTS")
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

# 4. Login as Platform Admin
res_platform = requests.post(
    f"{base_url}/auth/login",
    data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"}
)
platform_auth = res_platform.json()
platform_token = platform_auth.get("access_token")

screenshots = [
    # 1. Notification Center Ledger (Student View)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fnotifications",
        "phase14_notification_center_student.png",
        "Unified Notification & Communication Center (Student Ledger)"
    ),
    # 2. Student Dashboard with Notification Bell in Header
    (
        f"http://localhost:5173/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fstudent",
        "phase14_student_header_notification_bell.png",
        "Student Dashboard Header with Active Notification Bell"
    ),
    # 3. Parent Notification Center (Verified Child Updates)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={parent_token}&role=parent&email=raghu@example.com&full_name=Raghu+Kumar&target=%2F%23%2Fnotifications",
        "phase14_parent_notification_center.png",
        "Parent Notification Center with Linked Child Academic & Attendance Alerts"
    ),
    # 4. Institution Admin Notification Center (Gradebook Audits & Operational Notices)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={admin_token}&role=school_admin&school_id=SCH001&email=admin.sch001@example.com&full_name=Sri.+Venkatesh&target=%2F%23%2Fnotifications",
        "phase14_institution_admin_notifications.png",
        "Institution Admin Notification Desk with Gradebook Modification Audits"
    ),
    # 5. Platform Admin Notification Center (Operational & Security Alerts)
    (
        f"http://localhost:5173/auth_bootstrap.html?token={platform_token}&role=platform_admin&email=admin.central@nagriksetu.gov&full_name=Central+Platform+Administrator&target=%2F%23%2Fnotifications",
        "phase14_platform_admin_security_notifications.png",
        "Platform Admin Security & Operational Audit Notification Ledger"
    )
]

for url, filename, desc in screenshots:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,1050",
        "--virtual-time-budget=9000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)

print("All Phase 14 notification screenshots captured successfully!")
