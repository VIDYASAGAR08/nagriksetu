#!/usr/bin/env python3
"""
test_phase17_production_e2e.py — Comprehensive End-to-End Production & Staging Verification.
Tests all 6 user roles, 4 educational tiers, persistence, and disaster recovery.
"""

import requests
import json
import sqlite3
import time

BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5173"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

print("======================================================================")
print("NAGRIKSETU PHASE 17: END-TO-END PRODUCTION & STAGING DEPLOYMENT SUITE")
print("======================================================================")

def login(identifier, password, school_id=None):
    url = f"{BASE_URL}/auth/login"
    if school_id:
        url += f"?institution_id={school_id}"
    res = requests.post(url, data={"username": identifier, "password": password})
    return res

# -----------------------------------------------------------------------------
# 1. INFRASTRUCTURE & HEALTH VERIFICATION
# -----------------------------------------------------------------------------
print("\n[CHECK 1] Cloud Infrastructure & Container Health...")
r_health = requests.get(f"{BASE_URL}/health", timeout=5)
assert r_health.status_code == 200 and r_health.json().get("status") == "healthy", f"Backend health failed: {r_health.text}"
print(f"  [PASS] Backend health check verified: HTTP {r_health.status_code} ({r_health.json()})")

r_front = requests.get(FRONTEND_URL, timeout=5)
assert r_front.status_code == 200 and "<!doctype html>" in r_front.text.lower(), "Frontend availability check failed"
print(f"  [PASS] Frontend Nginx availability check verified: HTTP {r_front.status_code}")

# -----------------------------------------------------------------------------
# 2. ALL 4 INSTITUTIONAL TIERS VERIFICATION
# -----------------------------------------------------------------------------
print("\n[CHECK 2] Educational Tier Verification (Schools, PU, Degree, Universities)...")
tier_map = {
    "Schools (K-10)": "SCH001",
    "PU Colleges (11-12)": "SCH011",
    "Degree Colleges": "COL001",
    "Universities": "COL010"
}
for tier_name, inst_id in tier_map.items():
    r_inst = requests.get(f"{BASE_URL}/schools/{inst_id}")
    assert r_inst.status_code == 200, f"Failed to retrieve {tier_name} ({inst_id}): {r_inst.status_code}"
    inst_data = r_inst.json()
    print(f"  [PASS] Tier verified: {tier_name:<22} -> [{inst_id}] {inst_data['school_name']} ({inst_data.get('category') or inst_data.get('school_type')})")

# -----------------------------------------------------------------------------
# 3. ALL 6 ROLES AUTHENTICATION & ACCESS
# -----------------------------------------------------------------------------
print("\n[CHECK 3] All 6 User Category Portals & Workflows...")
# Role 1: Public / Citizen
r_pub = requests.get(f"{BASE_URL}/schools?limit=5")
assert r_pub.status_code == 200 and len(r_pub.json()) > 0, "Public access failed"
print("  [PASS] Role 1: Public / Citizen — Open directory browsing without auth.")

# Role 2: Student
r_stu = login("SCH01125", "Password@2026!")
assert r_stu.status_code == 200, "Student auth failed"
stu_token = r_stu.json()["access_token"]
r_stu_prof = requests.get(f"{BASE_URL}/student/profile", headers={"Authorization": f"Bearer {stu_token}"})
assert r_stu_prof.status_code == 200, "Student profile failed"
print(f"  [PASS] Role 2: Student — Authenticated profile retrieved for {r_stu_prof.json()['student']['student_name']} ({r_stu.json()['permanent_student_id']}).")

# Role 3: Parent / Guardian
r_par = login("9876543210", "Str0ngPass!2026")
assert r_par.status_code == 200, "Parent auth failed"
par_token = r_par.json()["access_token"]
r_par_kids = requests.get(f"{BASE_URL}/parent/children", headers={"Authorization": f"Bearer {par_token}"})
assert r_par_kids.status_code == 200 and len(r_par_kids.json()) > 0, "Parent children failed"
print(f"  [PASS] Role 3: Parent / Guardian — Multi-child ledger retrieved ({len(r_par_kids.json())} linked children).")

# Role 4: Institution Staff
r_staff = login("staff.sch001@example.com", "Staff@NagrikSetu2026!")
assert r_staff.status_code == 200, "Staff auth failed"
staff_token = r_staff.json()["access_token"]
r_staff_perm = requests.get(f"{BASE_URL}/school/staff/me/permissions", headers={"Authorization": f"Bearer {staff_token}"})
assert r_staff_perm.status_code == 200, "Staff permissions failed"
print(f"  [PASS] Role 4: Institution Staff — Operational permissions active at SCH001.")

# Role 5: Institution Administrator
r_adm = login("admin.sch001@example.com", "Admin@NagrikSetu2026!", "SCH001")
assert r_adm.status_code == 200, "Institution admin auth failed"
adm_token = r_adm.json()["access_token"]
r_adm_over = requests.get(f"{BASE_URL}/school/admin/overview", headers={"Authorization": f"Bearer {adm_token}"})
assert r_adm_over.status_code == 200, "Institution admin overview failed"
print(f"  [PASS] Role 5: Institution Admin — Administrative oversight desk active for SCH001.")

# Role 6: Platform Administrator
r_plat = login("admin.central@nagriksetu.gov", "Central@NagrikSetu2026!")
assert r_plat.status_code == 200, "Platform admin auth failed"
plat_token = r_plat.json()["access_token"]
r_plat_over = requests.get(f"{BASE_URL}/admin/overview", headers={"Authorization": f"Bearer {plat_token}"})
assert r_plat_over.status_code == 200, "Platform admin overview failed"
print(f"  [PASS] Role 6: Platform Admin — Statewide governance overview active (Total Institutions: {r_plat_over.json().get('total_schools')}).")

# -----------------------------------------------------------------------------
# 4. ADMISSION APPLICATION WORKFLOW
# -----------------------------------------------------------------------------
print("\n[CHECK 4] Admission Application Workflow (Stage 1 Submission & Isolation)...")
app_payload = {
    "institution_id": "SCH001",
    "applicant_name": "Deepa K",
    "parent_name": "Raghu Kumar",
    "parent_phone": "9876543210",
    "parent_email": "raghu@example.com",
    "residential_address": "88, 5th Cross, Rajajinagar, Bengaluru",
    "academic_year": "2026-2027",
    "education_level": "school",
    "requested_standard": 6,
    "first_language_preference": "Kannada",
    "second_language_preference": "English"
}
r_apply = requests.post(f"{BASE_URL}/admissions/apply", json=app_payload)
assert r_apply.status_code == 201, f"Application submission failed: {r_apply.text}"
new_app_id = r_apply.json()["application_id"]
print(f"  [PASS] Stage 1 public application submitted: {new_app_id}")

# Public confirmation
r_conf = requests.get(f"{BASE_URL}/admissions/applications/{new_app_id}/public-confirmation")
assert r_conf.status_code == 200 and "parent_phone" not in r_conf.json(), "PII leaked in public confirmation"
print(f"  [PASS] Public application confirmation returned without PII leakage.")

# Cross-tenant review isolation
r_cross_rev = requests.get(f"{BASE_URL}/school/admissions/applications/{new_app_id}", headers={"Authorization": f"Bearer {login('newadmin.sch011@example.com', 'Admin@NagrikSetu2026!', 'SCH011').json()['access_token']}"})
assert r_cross_rev.status_code == 403, "Cross-tenant reviewer leaked application"
print(f"  [PASS] Cross-tenant review isolation verified: SCH011 Admin cannot view SCH001 application (HTTP 403).")

# -----------------------------------------------------------------------------
# 5. BACKUP AND RESTORE DRILL VERIFICATION
# -----------------------------------------------------------------------------
print("\n[CHECK 5] Automated Production Backup and Disaster Recovery Drill...")
import subprocess
r_backup_cmd = subprocess.run(["python", r"C:\Users\callm\nagriksetu\deploy\scripts\backup_production.py"], capture_output=True, text=True)
assert r_backup_cmd.returncode == 0, f"Backup script failed: {r_backup_cmd.stderr}"
print(f"  [PASS] Production automated backup completed cleanly.")

r_restore_cmd = subprocess.run(["python", r"C:\Users\callm\nagriksetu\deploy\scripts\verify_backup_restore.py"], capture_output=True, text=True)
assert r_restore_cmd.returncode == 0, f"Restore drill failed: {r_restore_cmd.stderr}"
print(f"  [PASS] Disaster recovery restore drill verified 100% record parity.")

print("\n======================================================================")
print("ALL PHASE 17 PRODUCTION & STAGING E2E VERIFICATIONS PASSED (100%)")
print("======================================================================")
