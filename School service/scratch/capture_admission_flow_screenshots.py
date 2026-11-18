import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

def capture_screenshot(url, filename, desc, window_size="1320,1050", wait_time=9000):
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        f"--virtual-time-budget={wait_time}",
        f"--screenshot={out_path}",
        url
    ]
    print(f"  [SCREENSHOT] {desc} -> {filename}")
    subprocess.run(cmd, capture_output=True, timeout=45)
    time.sleep(1)
    if os.path.exists(out_path):
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  [SUCCESS] {filename} saved ({size_kb:.1f} KB)")
    else:
        print(f"  [WARNING] {filename} was not created!")

def run_captures():
    # 1. Login as K.S Rao to get live token
    login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    print("Obtained token for K.S Rao")

    # Screenshot 1: Overview tab showing Live Stage 1 Feed with pending applications
    url_overview = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Doverview"
    capture_screenshot(url_overview, "admission_stage1_overview_feed.png", "Overview Tab - Live Stage 1 Applications Feed", "1320,1100", 9000)

    # Screenshot 2: Admission Applications Management tab
    url_apps = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications"
    capture_screenshot(url_apps, "admission_stage1_management_desk.png", "Admission Management Tab - Comprehensive Table and Filters", "1320,1050", 9000)

    # Screenshot 3: Application Review Modal (Auto-open Srikar APP-2026-SCH019-30E92E)
    url_modal = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications%26app_id%3DAPP-2026-SCH019-30E92E"
    capture_screenshot(url_modal, "admission_stage1_review_dossier.png", "Stage 1 Application Review Modal - Applicant Dossier & Action Controls", "1320,1050", 9000)

    # Screenshot 4: Parent Portal tracking
    # Login as Parent
    p_login = requests.post(f"{base_url}/auth/login", data={"username": "testparent.ballari2@gmail.com", "password": "Parent@1234"})
    if p_login.status_code == 200:
        p_token = p_login.json()["access_token"]
        url_parent = f"{frontend_url}/auth_bootstrap.html?token={p_token}&role=parent&school_id=&email=testparent.ballari2@gmail.com&full_name=Suresh+Ballari&target=%2F%23%2Fparent-dashboard"
        capture_screenshot(url_parent, "parent_dashboard_admission_status.png", "Parent Dashboard - Live Application Status Tracking", "1320,1050", 9000)

if __name__ == "__main__":
    run_captures()
