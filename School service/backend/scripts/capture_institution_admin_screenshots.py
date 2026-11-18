import os
import shutil
import subprocess
import time
import json
import urllib.request
import urllib.parse
import sqlite3

API_URL = "http://localhost:8001"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\callm\nagriksetu\screenshots"
BRAIN_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

def kill_edge():
    try:
        subprocess.run(["powershell", "-Command", "Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force"], timeout=5)
    except Exception:
        pass
    time.sleep(0.5)

def get_auth_token(username, password):
    url = f"{API_URL}/auth/login"
    body = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["access_token"]

def capture_target(url, filename, desc=""):
    kill_edge()
    dest_local = os.path.join(SCREENSHOT_DIR, filename)
    dest_brain = os.path.join(BRAIN_DIR, filename)

    print(f"[*] Capturing: {desc} ({filename}) from {url}...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1050",
        f"--screenshot={dest_local}",
        url
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    except Exception as e:
        print(f"Edge process warning: {e}")

    time.sleep(1)
    if os.path.exists(dest_local):
        shutil.copyfile(dest_local, dest_brain)
        print(f"    -> Saved local: {dest_local}")
        print(f"    -> Copied to Brain: {dest_brain}")
    else:
        print(f"    -> FAILED to capture {filename}")

def main():
    print("=" * 70)
    print("CAPTURING NAGRIKSETU INSTITUTION ADMINISTRATOR SYSTEM SCREENSHOTS")
    print("=" * 70)

    # 1. Obtain tokens
    pa_token = get_auth_token("admin.central@nagriksetu.gov", "Central@NagrikSetu2026!")
    sch001_token = get_auth_token("admin.sch001@example.com", "Admin@NagrikSetu2026!")
    sch011_token = get_auth_token("staff.sch011@example.com", "Staff@NagrikSetu2026!")

    # 2. Generate a fresh invitation token for SCH001 so the Accept Invitation page is valid & verified
    req = urllib.request.Request(
        f"{API_URL}/admin/institution-admins/invite",
        data=json.dumps({
            "full_name": "Prof. S. R. Narayan",
            "email": "sr.narayan@sch001.edu",
            "institution_id": "SCH001",
            "role_id": "school_admin"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {pa_token}"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        invite_data = json.loads(res.read().decode("utf-8"))
        inv_token = invite_data.get("invitation_token")

    # Target 1: Platform Admin Administrator Accounts tab
    capture_target(
        f"http://localhost:5173/auth_bootstrap.html?token={pa_token}&role=platform_admin&target=%2F%23%2Fadmin%3Ftab%3Dadmins",
        "admin_accounts_desk.png",
        "Platform Admin Administrator Accounts Tab"
    )

    # Target 2: Invite Institution Administrator Modal
    capture_target(
        f"http://localhost:5173/auth_bootstrap.html?token={pa_token}&role=platform_admin&target=%2F%23%2Fadmin%3Ftab%3Dadmins%26modal%3Dinvite",
        "invite_admin_modal.png",
        "Platform Admin - Invite Administrator Modal"
    )

    # Target 3: Accept Invitation & Password Setup Page
    capture_target(
        f"http://localhost:5173/#/accept-invitation?token={inv_token}",
        "accept_invitation_page.png",
        "Accept Invitation & Setup Password Page"
    )

    # Target 4: Multi-institution Workspace Selector
    capture_target(
        "http://localhost:5173/#/select-workspace?demo=1",
        "select_workspace_page.png",
        "Multi-Institution Workspace Selector"
    )

    # Target 5: SCH001 Institution Admin workspace
    capture_target(
        f"http://localhost:5173/auth_bootstrap.html?token={sch001_token}&role=school_admin&school_id=SCH001&full_name=Headmaster+SCH001&target=%2F%23%2Fstaff%3Ftab%3Dadmin-overview",
        "sch001_admin_dashboard.png",
        "SCH001 Institution Admin Workspace"
    )

    # Target 6: SCH011 Institution Admin workspace
    capture_target(
        f"http://localhost:5173/auth_bootstrap.html?token={sch011_token}&role=school_admin&school_id=SCH011&full_name=Principal+SCH011&target=%2F%23%2Fstaff%3Ftab%3Dadmin-overview",
        "sch011_admin_dashboard.png",
        "SCH011 Institution Admin Workspace"
    )

    print("=" * 70)
    print("SCREENSHOT CAPTURE PROCESS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
