import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
token = login_res.json()["access_token"]

out_path = os.path.join(artifacts_dir, "phase20_student_management_standard8_sectionA.png")
target_url = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=/institution-admin?tab=students"

cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1320,1100",
    "--virtual-time-budget=2500",
    f"--screenshot={out_path}",
    target_url
]
print("Running capture for student management...")
subprocess.run(cmd, capture_output=True, timeout=35)
time.sleep(1)
if os.path.exists(out_path):
    print("SUCCESS: saved size", os.path.getsize(out_path) / 1024, "KB")
else:
    print("WARNING: file not found")
