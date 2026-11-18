import json
import os
import shutil
import subprocess
import time
import urllib.request
import urllib.parse

API_URL = "http://localhost:8001"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\callm\nagriksetu\screenshots"
BRAIN_DIR = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def get_auth_token(username, password):
    url = f"{API_URL}/auth/login"
    body = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["access_token"]

def capture():
    print("[*] Obtaining authentication tokens...")
    staff_token = get_auth_token("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    parent_token = get_auth_token("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")

    targets = [
        {
            "name": "Phase 6 - Staff Admission Desk Section Allotment & Enrolment",
            "url": f"http://localhost:5173/auth_bootstrap.html?token={staff_token}&role=school_staff&school_id=SCH001&target=%2Fstaff%3Ftab%3Dadmissions",
            "file": "phase6_staff_enrolment_confirmation.png"
        },
        {
            "name": "Phase 6 - Parent Confirmed Enrolment Dossier Card",
            "url": f"http://localhost:5173/auth_bootstrap.html?token={parent_token}&role=parent&target=%2Fparent%3Ftab%3Dadmissions",
            "file": "phase6_parent_confirmed_enrolment.png"
        }
    ]

    for item in targets:
        dest_local = os.path.join(SCREENSHOT_DIR, item["file"])
        dest_brain = os.path.join(BRAIN_DIR, item["file"])

        print(f"[*] Capturing: {item['name']}...")
        cmd = [
            EDGE_PATH,
            "--headless=new",
            "--disable-gpu",
            "--window-size=1440,1050",
            f"--screenshot={dest_local}",
            "--virtual-time-budget=4000",
            item["url"]
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        except Exception as e:
            print(f"Edge process warning: {e}")

        if os.path.exists(dest_local):
            shutil.copyfile(dest_local, dest_brain)
            print(f"    -> Saved: {dest_local}")
            print(f"    -> Copied to Brain: {dest_brain}")
        else:
            print(f"    -> Warning: Failed to capture {item['file']}")

if __name__ == "__main__":
    capture()
