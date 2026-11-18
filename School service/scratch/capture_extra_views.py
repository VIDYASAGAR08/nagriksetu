import sys
import io
import subprocess
import time
import os
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def capture_screenshot(url, filename, desc, window_size="1280,1050"):
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
    print(f"  [SCREENSHOT] {desc} -> {filename}")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)
    if os.path.exists(out_path):
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  [SUCCESS] {filename} saved ({size_kb:.1f} KB)")
    else:
        print(f"  [WARNING] {filename} was not created!")

def capture_extra_views():
    # 1. Platform Admin login
    res_platform = requests.post(f"{base_url}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
    platform_token = res_platform.json().get("access_token")
    headers = {"Authorization": f"Bearer {platform_token}"}

    # Invite administrator for SCH019
    invite_res = requests.post(
        f"{base_url}/admin/institution-admins/invite",
        json={
            "institution_id": "SCH019",
            "full_name": "Dr. K. V. Shailaja",
            "email": "shailaja.ballari@nagriksetu.gov",
            "role_id": "academic_admin"
        },
        headers=headers
    )
    raw_token = invite_res.json().get("invitation_token")

    # Step 2 Credential Setup Form (using token)
    capture_screenshot(
        f"{frontend_url}/#/accept-invitation?token={raw_token}",
        "phase19_direct_setup_step2_credential_setup.png",
        "Step 2: Credential Configuration with prefilled, non-editable locked identity fields"
    )

    # Clean up assignments
    requests.post(f"{base_url}/admin/institution-admins/reset-assignments", headers=headers)
    print("Cleanup done.")

if __name__ == "__main__":
    capture_extra_views()
