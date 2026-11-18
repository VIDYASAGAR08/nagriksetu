import requests
import time
import uuid

base_url = "http://localhost:8001"

print("==================================================================")
print("RUNNING NAGRIKSETU THREE-LEVEL WORKFLOW & GAP VERIFICATION SUITE")
print("==================================================================")

# 1. Platform Admin Login
res_pa = requests.post(
    f"{base_url}/auth/login",
    data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"}
)
assert res_pa.status_code == 200, f"Platform Admin login failed: {res_pa.text}"
pa_token = res_pa.json()["access_token"]
pa_headers = {"Authorization": f"Bearer {pa_token}"}
print("1. Platform Admin login: PASSED")

# 2. Level 1: Platform Admin -> Institution Admin (Test for University COL010)
admin_email = f"newadmin.col010.{uuid.uuid4().hex[:4]}@example.com"
res_inv_adm = requests.post(
    f"{base_url}/admin/institution-admins/invite",
    headers=pa_headers,
    json={
        "full_name": "Dr. Vishwanath VTU",
        "email": admin_email,
        "phone": "9876000001",
        "institution_id": "COL010",
        "role_id": "school_admin"
    }
)
assert res_inv_adm.status_code == 200, f"Invite admin failed: {res_inv_adm.text}"
adm_inv_data = res_inv_adm.json()
adm_raw_token = adm_inv_data["invitation_token"]
print("2. Platform Admin invited Institution Admin (COL010): PASSED")

# 3. Institution Admin accepts invitation and sets password
res_acc_adm = requests.post(
    f"{base_url}/auth/accept-invitation",
    json={
        "token": adm_raw_token,
        "password": "SecureAdminPass2026!"
    }
)
assert res_acc_adm.status_code == 200, f"Accept admin invitation failed: {res_acc_adm.text}"
print("3. Institution Admin accepted invitation & set password: PASSED")

# 4. Login as newly activated Institution Admin (COL010)
res_adm_login = requests.post(
    f"{base_url}/auth/login?institution_id=COL010",
    data={"username": admin_email, "password": "SecureAdminPass2026!"}
)
assert res_adm_login.status_code == 200, f"New Institution Admin login failed: {res_adm_login.text}"
col010_admin_token = res_adm_login.json()["access_token"]
col010_headers = {"Authorization": f"Bearer {col010_admin_token}"}
print("4. New Institution Admin login: PASSED")

# Also obtain tokens for School (SCH019), PU College (SCH011), and Degree College (COL001)
res_sch019 = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": "admin.sch019@gmail.com", "password": "Admin@NagrikSetu2026!"}
)
assert res_sch019.status_code == 200
sch019_headers = {"Authorization": f"Bearer {res_sch019.json()['access_token']}"}

res_sch011 = requests.post(
    f"{base_url}/auth/login?institution_id=SCH011",
    data={"username": "newadmin.sch011@example.com", "password": "Admin@NagrikSetu2026!"}
)
assert res_sch011.status_code == 200
sch011_headers = {"Authorization": f"Bearer {res_sch011.json()['access_token']}"}

res_col001 = requests.post(
    f"{base_url}/auth/login?institution_id=COL001",
    data={"username": "admin.col001@example.com", "password": "Admin@NagrikSetu2026!"}
)
assert res_col001.status_code == 200
col001_headers = {"Authorization": f"Bearer {res_col001.json()['access_token']}"}

print("5. Authenticated Admins for School (SCH019), PU (SCH011), Degree (COL001), University (COL010): PASSED")

# 6. Level 2: Institution Admin -> Staff Candidate (SCH019 School)
candidate_email_sch = f"cand.sch019.{uuid.uuid4().hex[:4]}@example.com"
res_cand_inv = requests.post(
    f"{base_url}/school/admin/staff-applications/invite",
    headers=sch019_headers,
    json={
        "candidate_name": "Suresh Kumar",
        "candidate_email": candidate_email_sch,
        "candidate_phone": "9845011223",
        "role_id": "admissions_officer",
        "institution_id": "SCH019"
    }
)
assert res_cand_inv.status_code == 200, f"Invite candidate failed: {res_cand_inv.text}"
cand_data = res_cand_inv.json()
cand_token = cand_data["candidate_token"]
sch_app_id = cand_data["application_id"]
print(f"6. SCH019 Admin invited candidate ({sch_app_id}): PASSED")

# 7. Candidate retrieves application via public endpoint
res_cand_view = requests.get(f"{base_url}/auth/staff-candidate/application?token={cand_token}")
assert res_cand_view.status_code == 200, f"Candidate view failed: {res_cand_view.text}"
assert res_cand_view.json()["status"] == "invited"
print("7. Candidate retrieved application via public invitation token: PASSED")

# 8. Candidate submits credentials & documents (Status -> submitted)
res_cand_sub = requests.post(
    f"{base_url}/auth/staff-candidate/submit",
    json={
        "token": cand_token,
        "candidate_name": "Suresh Kumar",
        "candidate_phone": "9845011223",
        "qualifications": [
            {"degree": "M.Sc. Mathematics", "institution": "Bangalore University", "year": 2020},
            {"degree": "B.Ed.", "institution": "Mysore University", "year": 2022}
        ],
        "employment_details": {
            "current_employer": "National Public School",
            "experience_years": 4,
            "designation": "Admissions Coordinator"
        },
        "documents": [
            {"doc_type": "resume", "filename": "suresh_cv.pdf"},
            {"doc_type": "id_proof", "filename": "aadhaar.pdf"}
        ]
    }
)
assert res_cand_sub.status_code == 200, f"Candidate submit failed: {res_cand_sub.text}"
assert res_cand_sub.json()["status"] == "submitted"
print("8. Candidate submitted qualifications, employment, and documents: PASSED")

# 9. Institution Admin inspects application details
res_adm_insp = requests.get(
    f"{base_url}/school/admin/staff-applications/{sch_app_id}",
    headers=sch019_headers
)
assert res_adm_insp.status_code == 200
insp_data = res_adm_insp.json()
assert len(insp_data["qualifications"]) == 2
assert insp_data["status"] == "submitted"
print("9. Institution Admin inspected candidate dossier: PASSED")

# 10. Institution Admin requests correction
res_corr = requests.post(
    f"{base_url}/school/admin/staff-applications/{sch_app_id}/request-correction",
    headers=sch019_headers,
    json={"correction_notes": "Please attach your official B.Ed. marks certificate and confirm notice period."}
)
assert res_corr.status_code == 200
assert res_corr.json()["status"] == "correction_requested"
print("10. Institution Admin requested correction from candidate: PASSED")

# 11. Candidate resubmits updated information (Status -> resubmitted)
res_resub = requests.post(
    f"{base_url}/auth/staff-candidate/submit",
    json={
        "token": cand_token,
        "qualifications": [
            {"degree": "M.Sc. Mathematics", "institution": "Bangalore University", "year": 2020},
            {"degree": "B.Ed.", "institution": "Mysore University", "year": 2022, "marks_percentage": "82%"}
        ],
        "employment_details": {
            "current_employer": "National Public School",
            "experience_years": 4,
            "notice_period": "30 days"
        },
        "documents": [
            {"doc_type": "resume", "filename": "suresh_cv.pdf"},
            {"doc_type": "id_proof", "filename": "aadhaar.pdf"},
            {"doc_type": "degree_certificate", "filename": "bed_certificate.pdf"}
        ]
    }
)
assert res_resub.status_code == 200
assert res_resub.json()["status"] == "resubmitted"
print("11. Candidate updated and resubmitted dossier: PASSED")

# 12. Institution Admin approves application
res_appr = requests.post(
    f"{base_url}/school/admin/staff-applications/{sch_app_id}/approve",
    headers=sch019_headers,
    json={"review_notes": "All credentials verified. Appointed as Admissions Officer."}
)
assert res_appr.status_code == 200
appr_data = res_appr.json()
activation_token = appr_data["activation_token"]
print("12. Institution Admin approved application & issued activation token: PASSED")

# 13. Candidate activates account with password
cand_pwd = "SureshPass2026!#"
res_act = requests.post(
    f"{base_url}/auth/staff-candidate/activate",
    json={
        "activation_token": activation_token,
        "password": cand_pwd
    }
)
assert res_act.status_code == 200, f"Activation failed: {res_act.text}"
print("13. Candidate activated account with secure 12+ char password: PASSED")

# 14. Activated staff member logs in
res_staff_login = requests.post(
    f"{base_url}/auth/login?institution_id=SCH019",
    data={"username": candidate_email_sch, "password": cand_pwd}
)
assert res_staff_login.status_code == 200, f"Staff login failed: {res_staff_login.text}"
print("14. Newly onboarded Admissions Officer authenticated successfully: PASSED")

# 15. Test decline workflow: PU College (SCH011)
cand_pu_email = f"pu.cand.{uuid.uuid4().hex[:4]}@example.com"
res_pu_inv = requests.post(
    f"{base_url}/school/admin/staff-applications/invite",
    headers=sch011_headers,
    json={
        "candidate_name": "Meera Rao",
        "candidate_email": cand_pu_email,
        "role_id": "general_staff",
        "institution_id": "SCH011"
    }
)
pu_app_id = res_pu_inv.json()["application_id"]
pu_token = res_pu_inv.json()["candidate_token"]

# Candidate submits
requests.post(
    f"{base_url}/auth/staff-candidate/submit",
    json={
        "token": pu_token,
        "qualifications": [{"degree": "B.A.", "year": 2018}]
    }
)

# SCH011 Admin declines application
res_pu_dec = requests.post(
    f"{base_url}/school/admin/staff-applications/{pu_app_id}/decline",
    headers=sch011_headers,
    json={"reason": "Candidate does not meet statutory experience prerequisites for this role."}
)
assert res_pu_dec.status_code == 200
assert res_pu_dec.json()["status"] == "declined"
print("15. PU College (SCH011) Admin declined application with reason: PASSED")

# 16. Test Degree College (COL001) Candidate Onboarding
col_cand_email = f"col.cand.{uuid.uuid4().hex[:4]}@example.com"
res_col_inv = requests.post(
    f"{base_url}/school/admin/staff-applications/invite",
    headers=col001_headers,
    json={
        "candidate_name": "Prof. Arvind Rao",
        "candidate_email": col_cand_email,
        "role_id": "academic_admin",
        "institution_id": "COL001"
    }
)
col_app_id = res_col_inv.json()["application_id"]
col_token = res_col_inv.json()["candidate_token"]
requests.post(
    f"{base_url}/auth/staff-candidate/submit",
    json={
        "token": col_token,
        "qualifications": [{"degree": "Ph.D. Computer Science", "year": 2015}]
    }
)
res_col_appr = requests.post(
    f"{base_url}/school/admin/staff-applications/{col_app_id}/approve",
    headers=col001_headers,
    json={"review_notes": "Approved for Academic Administration at MSRIT."}
)
col_act_token = res_col_appr.json()["activation_token"]
res_col_act = requests.post(
    f"{base_url}/auth/staff-candidate/activate",
    json={"activation_token": col_act_token, "password": "ArvindPass2026!"}
)
assert res_col_act.status_code == 200
print("16. Degree College (COL001) candidate onboarding & approval: PASSED")

# 17. Cross-Institution Isolation Attack (SCH019 Admin attempts to inspect COL001 application)
res_cross_insp = requests.get(
    f"{base_url}/school/admin/staff-applications/{col_app_id}",
    headers=sch019_headers
)
assert res_cross_insp.status_code == 403, f"Expected 403 Forbidden, got {res_cross_insp.status_code}"
print("17. Cross-institution inspection attack blocked (HTTP 403): PASSED")

# 18. Token Replay Protection on Activation
res_replay_act = requests.post(
    f"{base_url}/auth/staff-candidate/activate",
    json={"activation_token": col_act_token, "password": "ArvindPass2026!"}
)
assert res_replay_act.status_code == 400, f"Expected 400 for replayed activation token, got {res_replay_act.status_code}"
print("18. Replayed activation token rejected (HTTP 400): PASSED")

# 19. Level 3: Platform Admin Global Staff Monitoring
res_mon = requests.get(
    f"{base_url}/admin/staff-monitoring",
    headers=pa_headers
)
assert res_mon.status_code == 200, f"Monitoring failed: {res_mon.text}"
mon_data = res_mon.json()
print("Global Monitoring Summary:", mon_data["summary"])
assert mon_data["summary"]["monitored_institutions"] == 30
assert len(mon_data["applications"]) >= 3
assert len(mon_data["audit_events"]) >= 5
print("19. Platform Admin Global Monitoring verified across all 30 institutions: PASSED")

# 20. Audit Trail Permanence on Suspension
# Suspend the COL001 staff account
col_user_id = res_col_act.json()["user_id"]
res_susp = requests.post(
    f"{base_url}/school/admin/staff/{col_user_id}/suspend",
    headers=col001_headers
)
assert res_susp.status_code == 200

# Re-check global monitoring: audit events must NOT disappear
res_mon_after = requests.get(
    f"{base_url}/admin/staff-monitoring",
    headers=pa_headers
)
events_after = res_mon_after.json()["audit_events"]
assert len(events_after) >= len(mon_data["audit_events"])
print("20. Audit trail permanence verified upon account suspension: PASSED")

# 21. Suspended Account Login Rejection
res_susp_login = requests.post(
    f"{base_url}/auth/login?institution_id=COL001",
    data={"username": col_cand_email, "password": "ArvindPass2026!"}
)
assert res_susp_login.status_code == 401, f"Expected 401 for suspended staff, got {res_susp_login.status_code}"
print("21. Suspended staff login rejected (HTTP 401): PASSED")

# 22. Parent Regression Check
res_parent = requests.post(
    f"{base_url}/auth/login",
    data={"username": "9876543210", "password": "Str0ngPass!2026"}
)
assert res_parent.status_code == 200
assert res_parent.json()["role"] == "parent"
print("22. Parent login regression check: PASSED")

print("==================================================================")
print("ALL 22/22 THREE-LEVEL WORKFLOW & GAP VERIFICATION TESTS PASSED!")
print("==================================================================")
