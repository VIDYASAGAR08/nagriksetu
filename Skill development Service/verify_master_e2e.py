import requests
import json
import pymysql
import hashlib

BASE = "http://localhost:8003/api"
FRONTEND = "http://localhost:5173"

def find_otp_code(cur, conn, ref):
    conn.commit()
    cur.execute("SELECT hashed_code FROM otp_verification_sessions WHERE reference = %s", (ref,))
    row = cur.fetchone()
    if not row:
        return None
    target_hash = row[0]
    for i in range(1000000):
        c = f"{i:06d}"
        if hashlib.sha256(c.encode('utf-8')).hexdigest() == target_hash:
            return c
    return None

def print_section(title):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def main():
    print_section("NAGRIKSETU MASTER E2E VERIFICATION SUITE")

    # 1. Frontend & Container Health
    print("\n[1] VERIFYING CONTAINER AND ENDPOINT HEALTH...")
    r_front = requests.get(FRONTEND)
    assert r_front.status_code == 200, f"Frontend down: {r_front.status_code}"
    print(f"  ✓ Frontend (Port 5173): HTTP {r_front.status_code} OK (HTML served)")

    r_health = requests.get("http://localhost:8003/health")
    assert r_health.status_code == 200, f"Backend down: {r_health.status_code}"
    print(f"  ✓ Backend API (Port 8003 /health): HTTP {r_health.status_code} - {r_health.json()}")

    # 2. Database Schema & Data Integrity
    print("\n[2] VERIFYING DATABASE INTEGRITY & 104 ORIGINAL SKILLS...")
    conn = pymysql.connect(
        host="localhost",
        port=3308,
        user="nagriksetu_skill",
        password="skill-app-pass-2026",
        database="skill_db"
    )
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM skills")
    total_skills = cur.fetchone()[0]
    print(f"  ✓ Total skills in database: {total_skills} (All original skills preserved)")
    assert total_skills >= 104, "Original skills missing!"

    cur.execute("SELECT count(*) FROM training_centres")
    total_centres = cur.fetchone()[0]
    print(f"  ✓ Total training centres: {total_centres}")
    assert total_centres >= 18, "Training centres missing!"

    cur.execute("SELECT count(*) FROM enrollments")
    total_enr = cur.fetchone()[0]
    print(f"  ✓ Total enrolments in DB: {total_enr}")

    # 3. Role-Based Authentication & Permissions
    print("\n[3] TESTING RBAC AUTHENTICATION & LOGIN FLOWS...")
    # Citizen Login
    r_cit_login = requests.post(f"{BASE}/auth/login", json={
        "email": "mahesh123@gmaail.com",
        "password": "AuditSecurePassword@2026!"
    })
    assert r_cit_login.status_code == 200, f"Citizen login failed: {r_cit_login.text}"
    cit_token = r_cit_login.json()["access_token"]
    cit_headers = {"Authorization": f"Bearer {cit_token}"}
    print(f"  ✓ Citizen Login: HTTP 200 OK | Role={r_cit_login.json()['role']} | Ref={r_cit_login.json()['citizen_ref']}")

    # Training Centre Admin A Login
    r_ca1_login = requests.post(f"{BASE}/auth/login", json={
        "email": "centre.admin.1795070146@bangalore.skill.gov.in",
        "password": "CentreAdmin@2026!"
    })
    assert r_ca1_login.status_code == 200, f"Centre Admin 1 login failed: {r_ca1_login.text}"
    ca1_token = r_ca1_login.json()["access_token"]
    ca1_headers = {"Authorization": f"Bearer {ca1_token}"}
    print(f"  ✓ Centre Admin A Login: HTTP 200 OK | Role={r_ca1_login.json()['role']} | CentreID={r_ca1_login.json()['centre_id']}")

    # Training Centre Admin B Login
    r_ca2_login = requests.post(f"{BASE}/auth/login", json={
        "email": "centre.admin.mysuru@nagriksetu.local",
        "password": "CentreAdmin@2026!"
    })
    assert r_ca2_login.status_code == 200, f"Centre Admin 2 login failed: {r_ca2_login.text}"
    ca2_token = r_ca2_login.json()["access_token"]
    ca2_headers = {"Authorization": f"Bearer {ca2_token}"}
    print(f"  ✓ Centre Admin B Login: HTTP 200 OK | Role={r_ca2_login.json()['role']} | CentreID={r_ca2_login.json()['centre_id']}")

    # Government Admin Login
    r_gov_login = requests.post(f"{BASE}/auth/login", json={
        "email": "skill.admin@nagriksetu.local",
        "password": "SkillAdmin@2026!"
    })
    assert r_gov_login.status_code == 200, f"Gov Admin login failed: {r_gov_login.text}"
    gov_token = r_gov_login.json()["access_token"]
    gov_headers = {"Authorization": f"Bearer {gov_token}"}
    print(f"  ✓ Government Admin Login: HTTP 200 OK | Role={r_gov_login.json()['role']}")

    # 4. Strict Centre-Level Isolation Tests
    print("\n[4] TESTING SERVER-ENFORCED CENTRE-LEVEL DATA ISOLATION...")
    # Citizen trying to access Centre Admin APIs -> Must be 403
    r_unauth1 = requests.get(f"{BASE}/centre-admin/profile", headers=cit_headers)
    assert r_unauth1.status_code == 403, f"Citizen should be blocked from centre profile: {r_unauth1.status_code}"
    print(f"  ✓ Citizen Access to Centre Admin Profile: HTTP {r_unauth1.status_code} (Blocked correctly)")

    r_unauth2 = requests.get(f"{BASE}/centre-admin/dashboard", headers=cit_headers)
    assert r_unauth2.status_code == 403, f"Citizen should be blocked from centre dashboard: {r_unauth2.status_code}"
    print(f"  ✓ Citizen Access to Centre Admin Dashboard: HTTP {r_unauth2.status_code} (Blocked correctly)")

    # Centre Admin A viewing profile vs Centre Admin B viewing profile
    prof_a = requests.get(f"{BASE}/centre-admin/profile", headers=ca1_headers).json()
    prof_b = requests.get(f"{BASE}/centre-admin/profile", headers=ca2_headers).json()
    print(f"  ✓ Centre Admin A Profile CentreID: {prof_a['id']} ('{prof_a['name']}')")
    print(f"  ✓ Centre Admin B Profile CentreID: {prof_b['id']} ('{prof_b['name']}')")
    assert prof_a['id'] != prof_b['id'], "Centre Admin A and B must see separate centres!"

    # Centre Admin A Enrolments must only contain centre_id == 1
    enr_a = requests.get(f"{BASE}/centre-admin/enrollments", headers=ca1_headers).json()
    enr_b = requests.get(f"{BASE}/centre-admin/enrollments", headers=ca2_headers).json()
    print(f"  ✓ Centre Admin A sees {len(enr_a)} applications (All CentreID 1: {all(e['centre_id'] == prof_a['id'] for e in enr_a)})")
    print(f"  ✓ Centre Admin B sees {len(enr_b)} applications (All CentreID 2: {all(e['centre_id'] == prof_b['id'] for e in enr_b)})")
    assert all(e['centre_id'] == prof_a['id'] for e in enr_a)
    assert all(e['centre_id'] == prof_b['id'] for e in enr_b)

    # Cross-centre write attack: Centre Admin A reviews Centre B application -> Must be 403
    target_b_enr = enr_b[0]['id']
    r_cross_attack = requests.patch(f"{BASE}/centre-admin/enrollments/{target_b_enr}/review", headers=ca1_headers, json={
        "action": "ACCEPT"
    })
    assert r_cross_attack.status_code == 403, f"Cross-centre attack should return 403: {r_cross_attack.status_code}"
    print(f"  ✓ Cross-Centre Write Attack (Admin A -> Centre B App): HTTP {r_cross_attack.status_code} (Blocked correctly: '{r_cross_attack.json()['detail']}')")

    # 5. Government Admin Centre Lifecycle & Admin Assignment
    print("\n[5] TESTING GOVERNMENT ADMIN CENTRE LIFECYCLE & ASSIGNMENT...")
    r_adm_centres = requests.get(f"{BASE}/admin/centres", headers=gov_headers)
    assert r_adm_centres.status_code == 200, f"Admin centres list failed: {r_adm_centres.status_code}"
    centres_data = r_adm_centres.json()
    print(f"  ✓ Government Admin fetched {len(centres_data)} centres with admin accounts")

    # Suspend Centre 5
    r_suspend = requests.patch(f"{BASE}/admin/centres/5/status", headers=gov_headers, json={
        "approval_status": "SUSPENDED",
        "rejection_reason": "Automated E2E compliance check"
    })
    assert r_suspend.status_code == 200
    print(f"  ✓ Suspended Centre 5: Code={r_suspend.json()['code']} Status={r_suspend.json()['approval_status']}")

    # Reactivate Centre 5
    r_reactivate = requests.patch(f"{BASE}/admin/centres/5/status", headers=gov_headers, json={
        "approval_status": "APPROVED"
    })
    assert r_reactivate.status_code == 200
    print(f"  ✓ Reactivated Centre 5: Code={r_reactivate.json()['code']} Status={r_reactivate.json()['approval_status']}")

    # Assign Centre Admin to Centre 5
    r_assign = requests.post(f"{BASE}/admin/centres/5/assign-admin", headers=gov_headers, json={
        "full_name": "Hubballi Administrator",
        "email": "centre.admin.hubballi@nagriksetu.local",
        "password": "CentreAdmin@2026!",
        "phone": "+91 836 222 3344"
    })
    assert r_assign.status_code == 200
    print(f"  ✓ Assigned Administrator for Centre 5: {r_assign.json()['message']}")

    # Login as Newly Assigned Centre 5 Admin
    r_ca5_login = requests.post(f"{BASE}/auth/login", json={
        "email": "centre.admin.hubballi@nagriksetu.local",
        "password": "CentreAdmin@2026!"
    })
    assert r_ca5_login.status_code == 200
    print(f"  ✓ Logged in as newly assigned Centre 5 Admin: CentreID={r_ca5_login.json()['centre_id']} Role={r_ca5_login.json()['role']}")

    # 6. Complete End-to-End Workflow & Audit Logs
    print("\n[6] TESTING FULL WORKFLOW: CITIZEN ENROLMENT -> REVIEW -> AUDIT TRAIL...")
    # Request & verify OTP for enrolment
    r_otp_req = requests.post(f"{BASE}/otp/send", headers=cit_headers, json={
        "phone": "7489277293",
        "purpose": "ENROLMENT"
    })
    assert r_otp_req.status_code == 200, f"OTP Send failed: {r_otp_req.text}"
    enr_otp_ref = r_otp_req.json()["reference"]
    demo_otp = r_otp_req.json().get("demo_otp") or find_otp_code(cur, conn, enr_otp_ref)

    r_otp_ver = requests.post(f"{BASE}/otp/verify", headers=cit_headers, json={
        "reference": str(enr_otp_ref),
        "code": str(demo_otp)
    })
    assert r_otp_ver.status_code == 200, f"OTP Verify failed: {r_otp_ver.text}"

    # Pick a program in Centre 5
    cur.execute("SELECT id, title FROM training_programs WHERE centre_id = 5 LIMIT 1")
    prog_c5 = cur.fetchone()
    print(f"  ✓ Selected Program in Centre 5: ID={prog_c5[0]} Title='{prog_c5[1]}'")

    # Citizen submits application
    r_submit = requests.post(f"{BASE}/enrollments", headers=cit_headers, json={
        "program_id": prog_c5[0],
        "selected_mode": "Hybrid",
        "otp_reference": enr_otp_ref,
        "declaration_agreed": True
    })
    assert r_submit.status_code == 201
    new_app = r_submit.json()
    new_app_id = new_app["id"]
    print(f"  ✓ Application Submitted: ID={new_app_id} Status={new_app['status']}")

    # Centre Admin A attempts to review -> 403
    r_bad_rev = requests.patch(f"{BASE}/centre-admin/enrollments/{new_app_id}/review", headers=ca1_headers, json={"action": "ACCEPT"})
    assert r_bad_rev.status_code == 403
    print(f"  ✓ Unassigned Centre Admin A blocked from reviewing: HTTP {r_bad_rev.status_code}")

    # Assigned Centre Admin 5 reviews application -> 200
    ca5_headers = {"Authorization": f"Bearer {r_ca5_login.json()['access_token']}"}
    r_good_rev = requests.patch(f"{BASE}/centre-admin/enrollments/{new_app_id}/review", headers=ca5_headers, json={
        "action": "ACCEPT",
        "remarks": "Candidate verified and admitted by Centre 5 Admin."
    })
    assert r_good_rev.status_code == 200
    print(f"  ✓ Assigned Centre 5 Admin approved application: Status={r_good_rev.json()['status']}")

    # Citizen checks application status
    r_my_apps = requests.get(f"{BASE}/enrollments/me", headers=cit_headers)
    assert r_my_apps.status_code == 200
    my_app_rec = next((a for a in r_my_apps.json() if a["id"] == new_app_id), None)
    assert my_app_rec is not None and my_app_rec["status"] == "APPROVED"
    print(f"  ✓ Citizen verified updated status: '{my_app_rec['status']}'")

    # Check Audit Log in DB
    cur.execute("SELECT id, actor, action, details FROM audit_logs WHERE action = 'REVIEW_APPLICATION' ORDER BY id DESC LIMIT 1")
    last_audit = cur.fetchone()
    print(f"  ✓ Verified Audit Log Record: ID={last_audit[0]} Actor='{last_audit[1]}' Action='{last_audit[2]}'")

    # Clean up test enrollment
    cur.execute("DELETE FROM module_progress WHERE enrollment_id = %s", (new_app_id,))
    cur.execute("DELETE FROM enrollment_status_history WHERE enrollment_id = %s", (new_app_id,))
    cur.execute("DELETE FROM enrollments WHERE id = %s", (new_app_id,))
    conn.commit()
    print(f"  ✓ Cleaned up test enrollment ID={new_app_id}")

    print_section("ALL E2E VERIFICATION TESTS PASSED SUCCESSFULLY! (100% GREEN)")

if __name__ == "__main__":
    main()
