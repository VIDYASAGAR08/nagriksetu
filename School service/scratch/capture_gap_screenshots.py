import subprocess
import time
import os
import requests
import json
import uuid

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
artifacts_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
base_url = "http://localhost:8001"

print("==================================================================")
print("CAPTURING GAP AUDIT SCREENSHOTS FOR THREE-LEVEL ONBOARDING")
print("==================================================================")

# 1. Login Platform Admin
res_pa = requests.post(
    f"{base_url}/auth/login",
    data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"}
)
pa_token = res_pa.json()["access_token"]
pa_headers = {"Authorization": f"Bearer {pa_token}"}

# 2. Login SCH019 Admin
res_sch019 = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "admin.sch019@gmail.com", "password": "Admin@NagrikSetu2026!"}
)
sch019_token = res_sch019.json()["access_token"]
sch019_headers = {"Authorization": f"Bearer {sch019_token}"}

# 3. Create a fresh candidate application for SCH019 to photograph
cand_email = f"audit.cand.{uuid.uuid4().hex[:4]}@example.com"
res_cand_inv = requests.post(
    f"{base_url}/school/admin/staff-applications/invite",
    headers=sch019_headers,
    json={
        "candidate_name": "Dr. Sunitha Varma",
        "candidate_email": cand_email,
        "candidate_phone": "9845099887",
        "role_id": "admissions_officer",
        "institution_id": "SCH019"
    }
)
cand_data = res_cand_inv.json()
cand_token = cand_data["candidate_token"]
cand_app_id = cand_data["application_id"]

# Candidate submits dossier
requests.post(
    f"{base_url}/auth/staff-candidate/submit",
    json={
        "token": cand_token,
        "candidate_name": "Dr. Sunitha Varma",
        "candidate_phone": "9845099887",
        "qualifications": [
            {"degree": "Ph.D. Education & Assessment", "institution": "Bangalore University", "year": "2019", "marks_percentage": "Distinction"},
            {"degree": "M.Ed. Institutional Management", "institution": "Mysore University", "year": "2015", "marks_percentage": "88%"}
        ],
        "employment_details": {
            "current_employer": "Delhi Public School (Bangalore)",
            "experience_years": 8,
            "designation": "Head of Admissions & Student Records",
            "notice_period": "30 days"
        },
        "documents": [
            {"doc_type": "curriculum_vitae", "filename": "sunitha_varma_cv.pdf"},
            {"doc_type": "doctoral_degree", "filename": "phd_certificate.pdf"},
            {"doc_type": "identity_proof", "filename": "aadhaar_card.pdf"}
        ]
    }
)

# Admin approves to generate activation token
res_appr = requests.post(
    f"{base_url}/school/admin/staff-applications/{cand_app_id}/approve",
    headers=sch019_headers,
    json={"review_notes": "Exemplary credentials and 8 years admissions experience. Appointed as Admissions Officer."}
)
act_token = res_appr.json()["activation_token"]

screenshots = [
    # 1. Platform Admin Global Staff Monitoring Tab
    (
        f"http://localhost:5173/auth_bootstrap.html?token={pa_token}&role=platform_admin&school_id=SCH001&email=admin.central@nagriksetu.gov&full_name=Central+Platform+Admin&target=%2F%23%2Fadmin%3Ftab%3Dstaff-monitoring",
        "platform_admin_global_staff_monitoring.png",
        "Platform Admin Statewide Staff Governance & Lifecycle Monitoring"
    ),
    # 2. Candidate Application Dossier Submission Portal
    (
        f"http://localhost:5173/#/staff-application?token={cand_token}",
        "staff_candidate_application_portal.png",
        "Staff Candidate Dossier Submission Portal (Public Link)"
    ),
    # 3. Staff Candidate Activation & Password Setup
    (
        f"http://localhost:5173/#/staff-activation?token={act_token}",
        "staff_candidate_activation_page.png",
        "Staff Candidate Account Activation & Password Setup (Post-Approval Only)"
    ),
    # 4. Institution Admin Candidates Tab on SCH019
    (
        f"http://localhost:5173/auth_bootstrap.html?token={sch019_token}&role=school_admin&school_id=SCH019&email=admin.sch019@gmail.com&full_name=Admin19&target=%2F%23%2Finstitution-admin%3Ftab%3Dstaff",
        "institution_admin_staff_candidates_tab.png",
        "Institution Admin Staff Management & Candidate Onboarding"
    )
]

for url, filename, desc in screenshots:
    out_path = os.path.join(artifacts_dir, filename)
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1280,950",
        "--virtual-time-budget=7000",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing: {desc} -> {filename}...")
    subprocess.run(cmd, capture_output=True, timeout=35)
    time.sleep(1)

print("All gap audit screenshots captured successfully!")
