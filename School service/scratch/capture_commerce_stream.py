import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifact_out = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

def capture_screenshot(url, filename, desc, window_size="1320,1100", wait_time=8000):
    out_path = os.path.join(artifact_out, filename)
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
    res_adm = requests.post(f"{base_url}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
    assert res_adm.status_code == 200
    token_adm = res_adm.json()["access_token"]

    url_sch011_comm = f"{frontend_url}/auth_bootstrap.html?token={token_adm}&role=platform_admin&school_id=SCH011&email=admin.sch011@example.com&full_name=Tumakuru+PU+Admin&target=%2F%23%2Finstitution-admin%3Ftab%3Dstudents"
    capture_screenshot(url_sch011_comm, "pu_college_commerce_stream_validation.png", "SCH011 - PU College Stream & Combination Strict Partition", "1340,1150", 9000)

if __name__ == "__main__":
    run_captures()
