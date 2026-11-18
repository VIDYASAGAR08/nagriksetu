# -*- coding: utf-8 -*-
import subprocess
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

res_parent = requests.post(f"{base_url}/auth/login", data={"username": "9876543210", "password": "Str0ngPass!2026"})
parent_token = res_parent.json().get("access_token")

url = f"http://localhost:5173/auth_bootstrap.html?token={parent_token}&role=parent&email=parent@example.com&full_name=Sri.+Ramesh+Sharma&target=%2F%23%2Fparent%3Fchild_psid%3DNS-FB8336A812DE468FB8E475443CF673EB"
out_modal = os.path.join(artifacts_dir, "phase12_parent_child_academic_records_modal.png")

cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1050",
    "--virtual-time-budget=10000",
    f"--screenshot={out_modal}",
    url
]
print("Capturing Parent Child Academic Modal directly via child_psid...")
subprocess.run(cmd, capture_output=True, timeout=35)
print("Saved modal screenshot size:", os.path.getsize(out_modal))
