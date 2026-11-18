import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"

def capture_screenshot(url, filename, desc, window_size="1320,1000", wait_time=8000):
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
    # Login as K.S Rao to get live token
    login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    print("Obtained token for K.S Rao")

    # 1. Overview Dashboard
    url_overview = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Doverview"
    capture_screenshot(url_overview, "phase20_institution_admin_dashboard_overview.png", "Institution Admin Dashboard Overview (7 Metric Cards & 14 Tabs)", "1320,1050", 10000)

    # 2. Student Management Desk (Standard 8, Section A - 67 students)
    url_students = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dstudents"
    capture_screenshot(url_students, "phase20_student_management_standard8_sectionA.png", "Student Management Dynamic Academic Selector & Roster Table", "1320,1050", 10000)

    # 3. Parent Requests Desk
    url_parent_reqs = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dparent_requests"
    capture_screenshot(url_parent_reqs, "phase20_parent_requests_desk.png", "Parent Demographic Update & Correction Review Desk", "1320,1000", 9000)

    # 4. Parents Directory
    url_parents = f"{frontend_url}/auth_bootstrap.html?token={token}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dparents"
    capture_screenshot(url_parents, "phase20_parents_directory.png", "Verified Parents & Legal Guardians Directory", "1320,1000", 9000)

if __name__ == "__main__":
    run_captures()
