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
    # Screenshot 1: Step 1 Lookup View
    url_step1 = f"{frontend_url}/#/login?category=student&tab=activate&student_id=NS-SCH019-STD06-166"
    capture_screenshot(url_step1, "student_activation_step1_lookup.png", "Student Activation - Initial Lookup by Student ID", "1320,950", 6000)

    # Screenshot 2: Step 2 Confirmed Official Record Card with Read-only Name and DOB verification
    url_step2 = f"{frontend_url}/#/login?category=student&tab=activate&student_id=NS-SCH019-STD06-166&auto_lookup=true"
    capture_screenshot(url_step2, "student_activation_step2_verified_record.png", "Student Activation - Database-Verified Record & Identity Verification", "1320,1200", 7000)

    # Screenshot 3: Authenticated Student Portal Dashboard
    # Sign in as Ishaan Verma to obtain JWT token
    login_res = requests.post(f"{base_url}/auth/login", data={"username": "NS-SCH019-STD06-166", "password": "Password@123"})
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        url_student_portal = f"{frontend_url}/auth_bootstrap.html?token={token}&role=student&school_id=SCH019&email=ishaan.verma@example.com&full_name=Ishaan+Verma&target=%2F%23%2Fstudent"
        capture_screenshot(url_student_portal, "student_activation_step3_portal_dashboard.png", "Authenticated Student Portal - Ishaan Verma Dashboard", "1320,1050", 8000)
    else:
        print("Could not log in as Ishaan Verma for screenshot 3:", login_res.text)

if __name__ == "__main__":
    run_captures()
