import subprocess
import time
import os
import urllib.request
import urllib.parse
import json

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

# Obtain student token for Asha Sharma
data = urllib.parse.urlencode({'username': 'SCH001-STD01-001', 'password': 'Password@2026!'}).encode()
req = urllib.request.Request(f"{base_url}/auth/login", data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    student_token = res["access_token"]

screenshots = [
    # 1. User Category Selection Screen
    (
        "http://localhost:5173/#/login",
        "user_category_selection_screen.png",
        "NagrikSetu User Category Selection Screen"
    ),
    # 2. Student Portal Login & Activation Screen
    (
        "http://localhost:5173/#/login?category=student",
        "student_portal_login_view.png",
        "Dedicated Student Portal Login & Account Activation Screen"
    ),
    # 3. Parent / Guardian Portal Login Screen
    (
        "http://localhost:5173/#/login?category=parent",
        "parent_portal_login_view.png",
        "Parent / Guardian Portal Authentication Screen"
    ),
    # 4. Administrator & Staff Login Screen
    (
        "http://localhost:5173/#/login?category=admin",
        "administrator_staff_login_view.png",
        "Administrator & Staff Authentication Gateway Screen"
    ),
    # 5. Student Academic Dashboard
    (
        f"http://localhost:5173/auth_bootstrap.html?token={student_token}&role=student&school_id=SCH001&email=student.asha@example.com&full_name=Asha+Sharma&target=%2F%23%2Fstudent",
        "student_academic_dashboard.png",
        "Authenticated Student Academic Dashboard (Asha Sharma - SCH001)"
    ),
]

for url, filename, desc in screenshots:
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

print("All screenshots captured successfully!")
