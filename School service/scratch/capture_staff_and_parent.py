# -*- coding: utf-8 -*-
import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

# 1. Staff
res_staff = requests.post(f"{base_url}/auth/login", data={"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"})
staff_token = res_staff.json().get("access_token")
url_staff = f"http://localhost:5173/auth_bootstrap.html?token={staff_token}&role=school_staff&school_id=SCH001&email=staff.sch001@example.com&full_name=Smt.+Shailaja&target=%2F%23%2Fstaff%3Ftab%3Dacademics"
out_staff = os.path.join(artifacts_dir, "phase12_staff_academic_desk.png")

cmd_staff = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1050",
    "--virtual-time-budget=12000",
    f"--screenshot={out_staff}",
    url_staff
]
print("Capturing Staff Academic Desk...")
subprocess.run(cmd_staff, capture_output=True, timeout=40)
print("Staff screenshot size:", os.path.getsize(out_staff))

# 2. Parent
res_parent = requests.post(f"{base_url}/auth/login", data={"username": "9876543210", "password": "Str0ngPass!2026"})
parent_token = res_parent.json().get("access_token")
url_parent = f"http://localhost:5173/auth_bootstrap.html?token={parent_token}&role=parent&email=parent@example.com&full_name=Sri.+Ramesh+Sharma&target=%2F%23%2Fparent"
out_parent = os.path.join(artifacts_dir, "phase12_parent_portal_dashboard.png")

cmd_parent = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1050",
    "--virtual-time-budget=12000",
    f"--screenshot={out_parent}",
    url_parent
]
print("Capturing Parent Dashboard...")
subprocess.run(cmd_parent, capture_output=True, timeout=40)
print("Parent screenshot size:", os.path.getsize(out_parent))
