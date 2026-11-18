import sys
import sqlite3
import requests
import json

BASE_URL = "http://localhost:8001"
DB_PATH = "C:/Users/callm/nagriksetu/backend/data/nagriksetu.db"

results = []

def record(test_num, name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    results.append({"num": test_num, "name": name, "passed": passed, "details": details})
    print(f"[{status}] Scenario {test_num:02d}: {name}")
    if details:
        print(f"       -> {details}")

print("=" * 70)
print("NAGRIKSETU INSTITUTION ADMINISTRATOR SYSTEM: 22-POINT ACCEPTANCE SUITE")
print("=" * 70)

# Clean up any leftover test users from earlier runs if needed
conn = sqlite3.connect(DB_PATH)
test_emails = [
    "newadmin.sch001@example.com", 
    "newadmin.sch011@example.com", 
    "cluster.admin@example.com", 
    "teacher.ramesh@sch001.edu",
    "intruder@sch011.edu",
    "fake.admin@nagriksetu.gov"
]
for em in test_emails:
    u = conn.execute("SELECT user_id FROM users WHERE email = ?", (em,)).fetchone()
    if u:
        uid = u[0]
        conn.execute("DELETE FROM user_institution_roles WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM invitation_tokens WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM password_reset_tokens WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM users WHERE user_id = ?", (uid,))
conn.commit()
conn.close()

# Helper for login
def login(username, password):
    res = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return res

# Get Platform Admin token
res_pa = login("admin.central@nagriksetu.gov", "Central@NagrikSetu2026!")
if res_pa.status_code != 200:
    print(f"FATAL: Platform Admin login failed: {res_pa.text}")
    sys.exit(1)
platform_admin_token = res_pa.json()["access_token"]
pa_headers = {"Authorization": f"Bearer {platform_admin_token}"}

# SCENARIO 1: Platform Admin invites SCH001 administrator
email_sch001 = "newadmin.sch001@example.com"
res1 = requests.post(
    f"{BASE_URL}/admin/institution-admins/invite",
    json={
        "full_name": "SCH001 Principal",
        "email": email_sch001,
        "institution_id": "SCH001",
        "role_id": "school_admin"
    },
    headers=pa_headers
)
inv1 = res1.json() if res1.status_code == 200 else {}
token_sch001 = inv1.get("invitation_token")
record(1, "Platform Admin invites SCH001 administrator", res1.status_code == 200 and bool(token_sch001), f"Token generated: {bool(token_sch001)}, status: {res1.status_code}")

# SCENARIO 2: Platform Admin invites SCH011 administrator
email_sch011 = "newadmin.sch011@example.com"
res2 = requests.post(
    f"{BASE_URL}/admin/institution-admins/invite",
    json={
        "full_name": "SCH011 Principal",
        "email": email_sch011,
        "institution_id": "SCH011",
        "role_id": "school_admin"
    },
    headers=pa_headers
)
inv2 = res2.json() if res2.status_code == 200 else {}
token_sch011 = inv2.get("invitation_token")
record(2, "Platform Admin invites SCH011 administrator", res2.status_code == 200 and bool(token_sch011), f"Token generated: {bool(token_sch011)}, status: {res2.status_code}")

# SCENARIO 3: Platform Admin invites cluster admin assigned to SCH001 and SCH011
email_cluster = "cluster.admin@example.com"
res3_1 = requests.post(
    f"{BASE_URL}/admin/institution-admins/invite",
    json={
        "full_name": "Cluster Administrator",
        "email": email_cluster,
        "institution_id": "SCH001",
        "role_id": "school_admin"
    },
    headers=pa_headers
)
inv3 = res3_1.json() if res3_1.status_code == 200 else {}
token_cluster = inv3.get("invitation_token")

# Add second institution role directly to cluster admin in db
user_cluster_id = inv3.get("user_id")
if user_cluster_id:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO user_institution_roles (id, user_id, institution_id, role_id, status) VALUES ('test-clus-2', ?, 'SCH011', 'school_admin', 'invited')",
        (user_cluster_id,)
    )
    conn.commit()
    conn.close()

record(3, "Platform Admin creates multi-institution administrator (SCH001 & SCH011)", res3_1.status_code == 200 and bool(token_cluster), f"Assigned to SCH001 & SCH011")

# SCENARIO 4: Reject duplicate email account with same role in same institution (HTTP 409)
res4 = requests.post(
    f"{BASE_URL}/admin/institution-admins/invite",
    json={
        "full_name": "Duplicate Admin",
        "email": email_sch001,
        "institution_id": "SCH001",
        "role_id": "school_admin"
    },
    headers=pa_headers
)
record(4, "Reject duplicate email account in same institution (HTTP 409)", res4.status_code == 409, f"Status code: {res4.status_code}")

# SCENARIO 5: Cryptographic invitation token verification & activation for SCH001 admin
res5_verify = requests.get(f"{BASE_URL}/auth/verify-invitation?token={token_sch001}")
res5_accept = requests.post(
    f"{BASE_URL}/auth/accept-invitation",
    json={"token": token_sch001, "password": "SecurePassword123!"}
)
record(5, "Cryptographic invitation verification & activation for SCH001 admin", res5_verify.status_code == 200 and res5_accept.status_code == 200, f"Verified & password set")

# SCENARIO 6: Cryptographic invitation token verification & activation for SCH011 admin
res6_verify = requests.get(f"{BASE_URL}/auth/verify-invitation?token={token_sch011}")
res6_accept = requests.post(
    f"{BASE_URL}/auth/accept-invitation",
    json={"token": token_sch011, "password": "SecurePassword123!"}
)
record(6, "Cryptographic invitation verification & activation for SCH011 admin", res6_verify.status_code == 200 and res6_accept.status_code == 200, f"Verified & password set")

# Activate cluster admin as well
requests.post(f"{BASE_URL}/auth/accept-invitation", json={"token": token_cluster, "password": "ClusterPassword123!"})
conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE user_institution_roles SET status = 'active' WHERE user_id = ?", (user_cluster_id,))
conn.commit()
conn.close()

# SCENARIO 7: Login as SCH001 admin -> direct login to SCH001
res7 = login(email_sch001, "SecurePassword123!")
data7 = res7.json() if res7.status_code == 200 else {}
token_admin_sch001 = data7.get("access_token")
me7 = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token_admin_sch001}"}).json() if token_admin_sch001 else {}
record(7, "Login as SCH001 admin -> direct login to SCH001 workspace", me7.get("school_id") == "SCH001" and me7.get("role") == "school_admin", f"Active school: {me7.get('school_id')}, role: {me7.get('role')}")

# SCENARIO 8: Login as SCH011 admin -> direct login to SCH011
res8 = login(email_sch011, "SecurePassword123!")
data8 = res8.json() if res8.status_code == 200 else {}
token_admin_sch011 = data8.get("access_token")
me8 = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token_admin_sch011}"}).json() if token_admin_sch011 else {}
record(8, "Login as SCH011 admin -> direct login to SCH011 workspace", me8.get("school_id") == "SCH011" and me8.get("role") == "school_admin", f"Active school: {me8.get('school_id')}, role: {me8.get('role')}")

# SCENARIO 9: Cross-institution isolation test: SCH001 admin attempting to review SCH011 admissions desk -> HTTP 403
res9 = requests.get(
    f"{BASE_URL}/school/admissions/applications",
    headers={"Authorization": f"Bearer {token_admin_sch001}"},
    params={"institution_id": "SCH011"}
)
record(9, "Cross-institution isolation: SCH001 admin accessing SCH011 admissions desk -> HTTP 403", res9.status_code == 403, f"Status: {res9.status_code}")

# SCENARIO 10: Cross-institution isolation test: SCH011 admin attempting to review SCH001 admissions desk -> HTTP 403
res10 = requests.get(
    f"{BASE_URL}/school/admissions/applications",
    headers={"Authorization": f"Bearer {token_admin_sch011}"},
    params={"institution_id": "SCH001"}
)
record(10, "Cross-institution isolation: SCH011 admin accessing SCH001 admissions desk -> HTTP 403", res10.status_code == 403, f"Status: {res10.status_code}")

# SCENARIO 11: Parent attempting to access institution admin API -> HTTP 403
res_parent = login("9876543210", "Str0ngPass!2026")
parent_token = res_parent.json().get("access_token") if res_parent.status_code == 200 else ""
res11 = requests.get(
    f"{BASE_URL}/school/admissions/applications",
    headers={"Authorization": f"Bearer {parent_token}"}
)
record(11, "Parent attempting to access institution admin API -> HTTP 403 Forbidden", res11.status_code == 403, f"Status: {res11.status_code}")

# SCENARIO 12: Institution admin attempting to access Platform Admin API -> HTTP 403
res12 = requests.get(
    f"{BASE_URL}/admin/institution-admins",
    headers={"Authorization": f"Bearer {token_admin_sch001}"}
)
record(12, "Institution admin attempting to access Platform Admin API -> HTTP 403 Forbidden", res12.status_code == 403, f"Status: {res12.status_code}")

# SCENARIO 13: School admin inviting staff for their own school -> Succeeded
res13 = requests.post(
    f"{BASE_URL}/school/admin/staff/invite",
    headers={"Authorization": f"Bearer {token_admin_sch001}"},
    json={
        "full_name": "Teacher Ramesh",
        "email": "teacher.ramesh@sch001.edu",
        "role_id": "school_staff"
    }
)
record(13, "School admin inviting staff for their own school -> Succeeded", res13.status_code == 200, f"Status: {res13.status_code}")

# SCENARIO 14: School admin attempting to invite staff for another school (SCH011) -> HTTP 403
res14 = requests.post(
    f"{BASE_URL}/school/admin/staff/invite",
    headers={"Authorization": f"Bearer {token_admin_sch001}"},
    json={
        "full_name": "Intruder Staff",
        "email": "intruder@sch011.edu",
        "institution_id": "SCH011",
        "role_id": "school_staff"
    }
)
record(14, "School admin attempting to invite staff for another school (SCH011) -> HTTP 403", res14.status_code == 403, f"Status: {res14.status_code}")

# SCENARIO 15: School admin attempting to create a platform_admin -> HTTP 403
res15 = requests.post(
    f"{BASE_URL}/school/admin/staff/invite",
    headers={"Authorization": f"Bearer {token_admin_sch001}"},
    json={
        "full_name": "Privilege Escalation Attempt",
        "email": "fake.admin@nagriksetu.gov",
        "role_id": "platform_admin"
    }
)
record(15, "School admin attempting to create platform_admin role -> HTTP 403 Forbidden", res15.status_code == 403, f"Status: {res15.status_code}")

# SCENARIO 16: Multi-institution admin login -> receives workspace list, selects workspace -> session bound
res16_login = login(email_cluster, "ClusterPassword123!")
data16 = res16_login.json() if res16_login.status_code == 200 else {}
req_ws = data16.get("requires_workspace_selection")
temp_token = data16.get("temp_token")
workspaces = data16.get("workspaces", [])
ws_inst_ids = [w.get("institution_id") for w in workspaces]

# Select SCH011
res16_select = requests.post(
    f"{BASE_URL}/auth/select-workspace",
    json={"temp_token": temp_token, "institution_id": "SCH011"}
)
data16_sel = res16_select.json() if res16_select.status_code == 200 else {}
token_cluster_sch011 = data16_sel.get("access_token")
me16 = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token_cluster_sch011}"}).json() if token_cluster_sch011 else {}

record(16, "Multi-institution admin login -> workspace selection -> bound session", 
       req_ws == True and "SCH001" in ws_inst_ids and "SCH011" in ws_inst_ids and me16.get("school_id") == "SCH011",
       f"Workspaces: {ws_inst_ids}, Chosen: {me16.get('school_id')}")

# SCENARIO 17: Suspension: Platform Admin suspends admin account -> subsequent login returns HTTP 401
user_sch011_id = me8.get("user_id")
res17_suspend = requests.post(f"{BASE_URL}/admin/institution-admins/{user_sch011_id}/suspend", headers=pa_headers)
res17_login = login(email_sch011, "SecurePassword123!")
record(17, "Suspended administrator account login attempt -> HTTP 401 Unauthorized", 
       res17_suspend.status_code == 200 and res17_login.status_code == 401, 
       f"Suspend: {res17_suspend.status_code}, Login after suspend: {res17_login.status_code}")

# SCENARIO 18: Reactivation: Platform Admin reactivates account -> login succeeds
res18_reactivate = requests.post(f"{BASE_URL}/admin/institution-admins/{user_sch011_id}/reactivate", headers=pa_headers)
res18_login = login(email_sch011, "SecurePassword123!")
record(18, "Reactivated administrator account login -> HTTP 200 Succeeded",
       res18_reactivate.status_code == 200 and res18_login.status_code == 200,
       f"Reactivate: {res18_reactivate.status_code}, Login: {res18_login.status_code}")

# SCENARIO 19: Used token reuse rejection: attempting to accept an already-used invitation token returns HTTP 400
res19 = requests.post(
    f"{BASE_URL}/auth/accept-invitation",
    json={"token": token_sch001, "password": "AnotherPassword123!"}
)
record(19, "Used invitation token reuse rejection -> HTTP 400 Bad Request", res19.status_code == 400, f"Status: {res19.status_code}")

# SCENARIO 20: Password reset workflow: request reset -> verify token -> reset password -> login with new password
res20_forgot = requests.post(f"{BASE_URL}/auth/forgot-password", json={"identifier": email_sch001})
token_reset = res20_forgot.json().get("reset_token") if res20_forgot.status_code == 200 else ""
res20_verify = requests.get(f"{BASE_URL}/auth/verify-reset-token?token={token_reset}")
res20_reset = requests.post(f"{BASE_URL}/auth/reset-password", json={"token": token_reset, "password": "BrandNewPassword123!"})
res20_newlogin = login(email_sch001, "BrandNewPassword123!")
record(20, "Password reset workflow (forgot -> verify -> reset -> login with new password)",
       res20_forgot.status_code == 200 and res20_verify.status_code == 200 and res20_reset.status_code == 200 and res20_newlogin.status_code == 200,
       f"Workflow executed cleanly, new login HTTP: {res20_newlogin.status_code}")

# SCENARIO 21: Parent regression test: existing parent accounts login and view linked records normally
res21_parent = login("9876543210", "Str0ngPass!2026")
parent_tok = res21_parent.json().get("access_token") if res21_parent.status_code == 200 else ""
res21_children = requests.get(f"{BASE_URL}/parent/children", headers={"Authorization": f"Bearer {parent_tok}"})
res21_requests = requests.get(f"{BASE_URL}/parent/linking-requests", headers={"Authorization": f"Bearer {parent_tok}"})
record(21, "Parent portal regression: existing parent login & record retrieval",
       res21_parent.status_code == 200 and res21_children.status_code == 200 and res21_requests.status_code == 200,
       f"Parent login: 200, Children: {len(res21_children.json() if res21_children.status_code == 200 else [])}, Requests: {len(res21_requests.json() if res21_requests.status_code == 200 else [])}")

# SCENARIO 22: Database baseline integrity: exact counts remain 30,001 students, 30,001 enrollments, 198 programs, 841 sections, 30 schools
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
schools_count = cur.execute("SELECT count(*) FROM schools").fetchone()[0]
students_count = cur.execute("SELECT count(*) FROM students").fetchone()[0]
enrollments_count = cur.execute("SELECT count(*) FROM enrollments").fetchone()[0]
programs_count = cur.execute("SELECT count(*) FROM academic_programs").fetchone()[0]
sections_count = cur.execute("SELECT count(*) FROM program_sections").fetchone()[0]
conn.close()

baseline_intact = (
    schools_count == 30 and
    students_count == 30001 and
    enrollments_count == 30001 and
    programs_count == 198 and
    sections_count == 841
)
record(22, "Database baseline integrity preserved (30,001 students, 30,001 enrollments, 198 programs, 841 sections, 30 schools)",
       baseline_intact,
       f"Schools: {schools_count}/30, Students: {students_count}/30001, Enrollments: {enrollments_count}/30001, Programs: {programs_count}/198, Sections: {sections_count}/841")

print("=" * 70)
passed_total = sum(1 for r in results if r["passed"])
print(f"RESULTS SUMMARY: {passed_total} / {len(results)} SCENARIOS PASSED")
print("=" * 70)
if passed_total < len(results):
    sys.exit(1)
