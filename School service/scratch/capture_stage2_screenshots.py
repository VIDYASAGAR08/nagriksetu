import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

def capture_screenshot(url, filename, desc, window_size="1320,1100", wait_time=8000):
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
    login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    print("Obtained token for K.S Rao")

    # Target: Jenifer APP-2026-SCH019-6ED0FE
    app_id = "APP-2026-SCH019-6ED0FE"

    # Screenshot 1: Dossier with Stage 2 Demographics and Uploaded Documents visible
    url_dossier = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications%26app_id%3D{app_id}"
    capture_screenshot(url_dossier, "stage2_dossier_detailed_records.png", "Institution Admin Dossier - Stage 2 Demographics & Uploaded Documents", "1320,1200", 9000)

    # Screenshot 2: Admission Management list showing documents_uploaded / detailed_review_completed status
    url_apps = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications"
    capture_screenshot(url_apps, "stage2_applications_list_status.png", "Admission Management Table - Jenifer Stage 2 Status", "1320,1050", 8000)

if __name__ == "__main__":
    run_captures()
