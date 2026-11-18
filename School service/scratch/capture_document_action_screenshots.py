import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

def capture_screenshot(url, filename, desc, window_size="1440,1200", wait_time=8000):
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

def run():
    # Login K.S Rao
    login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    print("Token obtained for K.S Rao (Ballari Education School - SCH019)")

    app_id = "APP-2026-SCH019-6DF0C3"

    # 1. Main dossier with document table
    url_dossier = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications%26app_id%3D{app_id}"
    capture_screenshot(
        url_dossier,
        "document_actions_dossier_table.png",
        "Uploaded Verification Documents & Certificates Table with View, Accept, Reject buttons",
        window_size="1440,1250",
        wait_time=9000
    )

    # 2. Preview Modal with Zoom controls & Download
    url_preview = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications%26app_id%3D{app_id}%26preview_doc_id%3Db4da2850-b49f-412d-8e7e-d1d2199e3144"
    capture_screenshot(
        url_preview,
        "document_actions_preview_zoom_modal.png",
        "Document Preview Modal with Zoom Controls, Category & Download Option",
        window_size="1440,1100",
        wait_time=9000
    )

    # 3. Accept Confirmation Modal
    url_accept = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications%26app_id%3D{app_id}%26accept_doc_id%3D7a4d733f-bd9f-4d7d-abca-5cb0e8e672c4"
    capture_screenshot(
        url_accept,
        "document_actions_accept_modal.png",
        "Accept Confirmation Modal with Administrator Signature Notice",
        window_size="1440,1100",
        wait_time=9000
    )

    # 4. Reject Modal with Mandatory Reason
    url_reject = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dapplications%26app_id%3D{app_id}%26reject_doc_id%3Df79d2b94-e42a-43b3-8f21-6598510aa729"
    capture_screenshot(
        url_reject,
        "document_actions_reject_modal.png",
        "Document Reject Modal with Mandatory Reason & Parent Notification Notice",
        window_size="1440,1100",
        wait_time=9000
    )

if __name__ == "__main__":
    run()
