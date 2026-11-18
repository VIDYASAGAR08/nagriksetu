# -*- coding: utf-8 -*-
import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

res_staff = requests.post(
    f"{base_url}/auth/login",
    data={"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"}
)
staff_auth = res_staff.json()
staff_token = staff_auth.get("access_token")

url = f"http://localhost:5173/auth_bootstrap.html?token={staff_token}&role=school_staff&school_id=SCH001&email=staff.sch001@example.com&full_name=Smt.+Shailaja&target=%2F%23%2Fstaff%3Ftab%3Dacademics"
out_path = os.path.join(artifacts_dir, "phase12_staff_academic_desk.png")

cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1050",
    "--virtual-time-budget=10000",
    f"--screenshot={out_path}",
    url
]
print("Capturing staff desk...")
subprocess.run(cmd, capture_output=True, timeout=35)
print("File size:", os.path.getsize(out_path))
