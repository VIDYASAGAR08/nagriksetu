import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

print("==================================================================")
print("PHASE 15: CAPTURING COMPLETE TELEMETRIC UI/UX SCREENSHOTS")
print("==================================================================")

# 1. Acquire tokens for all roles
# Student (SCH01125)
res_student = requests.post(f"{base_url}/auth/login", data={"username": "SCH01125", "password": "Password@2026!"})
student_token = res_student.json().get("access_token")

# Parent (9876543210)
res_parent = requests.post(f"{base_url}/auth/login", data={"username": "9876543210", "password": "Str0ngPass!2026"})
parent_token = res_parent.json().get("access_token")

# Institution Admin (SCH001)
res_admin = requests.post(f"{base_url}/auth/login?institution_id=SCH001", data={"username": "admin.sch001@example.com", "password": "Admin@NagrikSetu2026!"})
admin_token = res_admin.json().get("access_token")

# Staff (SCH001)
res_staff = requests.post(f"{base_url}/auth/login", data={"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"})
staff_token = res_staff.json().get("access_token")

# Platform Admin
res_platform = requests.post(f"{base_url}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
platform_token = res_platform.json().get("access_token")

desktop_tasks = [
    # 1. Homepage Category Cards
    (
        f"{frontend_url}/#/",
        "phase15_desktop_homepage_categories.png",
        "Homepage with Modernized 4 Citizen & Stakeholder Category Cards",
        "1280,1050"
    ),
    # 2. Login Page Admin/Staff
    (
        f"{frontend_url}/#/login?category=admin",
        "phase15_desktop_login_admin_staff.png",
        "Modernized Administrator & Staff Sign In Page",
        "1280,1050"
    ),
    # 3. Public Directory
    (
        f"{frontend_url}/#/schools",
        "phase15_desktop_public_directory.png",
        "Public Institutional Directory with 4 Educational Tiers",
        "1280,1050"
    ),
    # 4. Student Dashboard
    (
        f"{frontend_url}/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fstudent",
        "phase15_desktop_student_dashboard.png",
        "Student Academic Dashboard with Performance and Attendance KPIs",
        "1280,1050"
    ),
    # 5. Parent Dashboard
    (
        f"{frontend_url}/auth_bootstrap.html?token={parent_token}&role=parent&email=raghu@example.com&full_name=Raghu+Kumar&target=%2F%23%2Fparent",
        "phase15_desktop_parent_dashboard.png",
        "Parent Portal Dashboard with Verified Child Switcher & Academic Overview",
        "1280,1050"
    ),
    # 6. Institution Admin Dashboard
    (
        f"{frontend_url}/auth_bootstrap.html?token={admin_token}&role=school_admin&school_id=SCH001&email=admin.sch001@example.com&full_name=Sri.+Venkatesh&target=%2F%23%2Fadmin",
        "phase15_desktop_institution_admin_dashboard.png",
        "Institution Administrator Dashboard with Admissions & Staff Oversight",
        "1280,1050"
    ),
    # 7. Staff Dashboard
    (
        f"{frontend_url}/auth_bootstrap.html?token={staff_token}&role=school_staff&school_id=SCH001&email=staff.sch001@example.com&full_name=Smt.+Shailaja&target=%2F%23%2Fstaff",
        "phase15_desktop_staff_dashboard.png",
        "Institution Staff Operations Desk",
        "1280,1050"
    ),
    # 8. Platform Central Admin Dashboard
    (
        f"{frontend_url}/auth_bootstrap.html?token={platform_token}&role=platform_admin&email=admin.central@nagriksetu.gov&full_name=Central+Platform+Administrator&target=%2F%23%2Fsuperadmin",
        "phase15_desktop_platform_admin_dashboard.png",
        "Platform Central Admin Statewide Management & Security Oversight",
        "1280,1050"
    ),
    # 9. Notification Center
    (
        f"{frontend_url}/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fnotifications",
        "phase15_desktop_notification_center.png",
        "Centralized In-App Notification Center Ledger",
        "1280,1050"
    )
]

mobile_tasks = [
    # 1. Homepage Mobile
    (
        f"{frontend_url}/#/",
        "phase15_mobile_homepage_categories.png",
        "Mobile Viewport (390px) Homepage Category Stacking",
        "390,844"
    ),
    # 2. Login Page Mobile
    (
        f"{frontend_url}/#/login?category=admin",
        "phase15_mobile_login_page.png",
        "Mobile Viewport (390px) Login Interface",
        "390,844"
    ),
    # 3. Student Dashboard Mobile
    (
        f"{frontend_url}/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fstudent",
        "phase15_mobile_student_dashboard.png",
        "Mobile Viewport (390px) Student Dashboard",
        "390,844"
    ),
    # 4. Parent Dashboard Mobile
    (
        f"{frontend_url}/auth_bootstrap.html?token={parent_token}&role=parent&email=raghu@example.com&full_name=Raghu+Kumar&target=%2F%23%2Fparent",
        "phase15_mobile_parent_dashboard.png",
        "Mobile Viewport (390px) Parent Portal",
        "390,844"
    ),
    # 5. Institution Admin Mobile
    (
        f"{frontend_url}/auth_bootstrap.html?token={admin_token}&role=school_admin&school_id=SCH001&email=admin.sch001@example.com&full_name=Sri.+Venkatesh&target=%2F%23%2Fadmin",
        "phase15_mobile_institution_admin_dashboard.png",
        "Mobile Viewport (390px) Institution Admin Desk",
        "390,844"
    )
]

all_tasks = desktop_tasks + mobile_tasks

for url, filename, desc, window_size in all_tasks:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        "--virtual-time-budget=9000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing ({window_size}): {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)

print("\nAll Phase 15 desktop & mobile screenshots captured successfully!")
