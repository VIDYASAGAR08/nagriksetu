import subprocess
import time
import os
import requests

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\nagriksetu"
base_url = "http://localhost:8001"
frontend_url = "http://localhost:5173"
artifact_out = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"

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
    # Login Platform Admin
    res_adm = requests.post(f"{base_url}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
    assert res_adm.status_code == 200
    token_adm = res_adm.json()["access_token"]

    # 1. Degree College (COL001 - Ramaiah Institute of Technology)
    # Shows Academic Division -> Degree Programme (B.E. in Computer Science...) -> Academic Year -> Semester -> Section
    url_col001 = f"{frontend_url}/auth_bootstrap.html?token={token_adm}&role=platform_admin&school_id=COL001&email=admin.col001@example.com&full_name=Ramaiah+Academic+Admin&target=%2F%23%2Finstitution-admin%3Ftab%3Dstudents"
    capture_screenshot(url_col001, "degree_college_cascading_programme_filters.png", "COL001 - Degree Programme Cascading Filters", "1340,1150", 9000)

    # 2. PU College (SCH011 - Tumakuru Model Pre-University College)
    # Shows PU Level -> Academic Stream (Science / Commerce) -> Subject Combination -> Section
    url_sch011 = f"{frontend_url}/auth_bootstrap.html?token={token_adm}&role=platform_admin&school_id=SCH011&email=admin.sch011@example.com&full_name=Tumakuru+PU+Admin&target=%2F%23%2Finstitution-admin%3Ftab%3Dstudents"
    capture_screenshot(url_sch011, "pu_college_stream_combination_filters.png", "SCH011 - PU Stream and Combination Validation Filters", "1340,1150", 9000)

    # 3. K-10 School (SCH019 - Ballari Education School)
    # Shows Standard 8 Section A with 67 matching students and no stream/combination filters
    url_sch019 = f"{frontend_url}/auth_bootstrap.html?token={token_adm}&role=academic_admin&school_id=SCH019&email=rao@edu.in&full_name=K.S+Rao&target=%2F%23%2Finstitution-admin%3Ftab%3Dstudents"
    capture_screenshot(url_sch019, "school_student_management_desk_std8_secA.png", "SCH019 - K-10 School Standard 8 Section A Matched Students", "1340,1150", 9000)

if __name__ == "__main__":
    run_captures()
