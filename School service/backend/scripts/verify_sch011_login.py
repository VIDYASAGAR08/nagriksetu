import os
import shutil
import subprocess
import time
import json
import urllib.request
import urllib.parse

API_URL = "http://localhost:8001"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\callm\nagriksetu\screenshots"
BRAIN_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

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

def main():
    print("[*] Logging in as staff.sch011@example.com with Staff@NagrikSetu2026!...")
    token = get_auth_token("staff.sch011@example.com", "Staff@NagrikSetu2026!")
    print(f"    -> Token acquired: {token[:30]}...")

    # Verify /auth/me
    req_me = urllib.request.Request(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req_me, timeout=10) as res:
        me_data = json.loads(res.read().decode("utf-8"))
        print(f"    -> /auth/me: user_id={me_data.get('user_id')}, email={me_data.get('email')}, role={me_data.get('role')}, school_id={me_data.get('school_id')}")

    kill_edge()
    dest_local = os.path.join(SCREENSHOT_DIR, "sch011_staff_dashboard_verified.png")
    dest_brain = os.path.join(BRAIN_DIR, "sch011_staff_dashboard_verified.png")

    target_url = f"http://localhost:5173/auth_bootstrap.html?token={token}&role=school_staff&school_id=SCH011&email=staff.sch011%40example.com&full_name=Admissions+Officer+SCH011&target=%2F%23%2Fstaff%3Ftab%3Dqueue"
    print(f"[*] Navigating Edge headless to: {target_url}...")

    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1050",
        f"--screenshot={dest_local}",
        target_url
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    time.sleep(1)

    if os.path.exists(dest_local):
        shutil.copyfile(dest_local, dest_brain)
        print(f"    -> Verified screenshot saved: {dest_local}")
        print(f"    -> Copied to brain artifact dir: {dest_brain}")
    else:
        print("    -> ERROR: Screenshot failed.")

if __name__ == "__main__":
    main()
