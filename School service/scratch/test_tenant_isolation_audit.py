import requests
import json

base_url = "http://localhost:8001"

print("==================================================================")
print("SECURITY AUDIT: MULTI-TENANT ISOLATION TESTS (SCH001, SCH011, COL001, COL010)")
print("==================================================================")

# 1. Login to all 4 test institution admins
admins = {}
for code in ["SCH001", "SCH011", "COL001", "COL010"]:
    email = f"admin.{code.lower()}@example.com"
    pwd = f"Admin@NagrikSetu2026!"
    res = requests.post(f"{base_url}/auth/login?institution_id={code}", data={"username": email, "password": pwd})
    if res.status_code == 200:
        admins[code] = res.json().get("access_token")
        print(f"  [+] Logged in as Admin {code}")
    else:
        print(f"  [-] Failed to login as Admin {code}: {res.status_code} {res.text}")

# 2. Staff user for SCH001
res_staff = requests.post(f"{base_url}/auth/login", data={"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"})
staff_token = res_staff.json().get("access_token")

# Test 1: Cross-institution staff list
print("\n--- Test 1: Cross-institution Staff Access ---")
# SCH001 admin requesting /school/admin/staff
res = requests.get(f"{base_url}/school/admin/staff", headers={"Authorization": f"Bearer {admins['SCH001']}"})
sch001_staff = res.json() if res.status_code == 200 else []
print(f"  SCH001 staff count returned: {len(sch001_staff)} (Status: {res.status_code})")

# Verify all staff belong strictly to SCH001
foreign_staff = [s for s in sch001_staff if s.get("school_id") != "SCH001" and s.get("institution_id") != "SCH001"]
print(f"  Foreign staff leaked to SCH001 Admin: {len(foreign_staff)}")

# Test 2: Cross-institution admission applications
print("\n--- Test 2: Cross-institution Admission Applications Access ---")
res = requests.get(f"{base_url}/school/admissions/applications", headers={"Authorization": f"Bearer {admins['SCH001']}"})
sch001_apps = res.json() if res.status_code == 200 else []
print(f"  SCH001 apps count returned: {len(sch001_apps)} (Status: {res.status_code})")
foreign_apps = [a for a in sch001_apps if a.get("institution_id") != "SCH001"]
print(f"  Foreign applications leaked to SCH001 Admin: {len(foreign_apps)}")

# Try to directly access SCH011 application using SCH001 Admin token
res_sch011_apps = requests.get(f"{base_url}/school/admissions/applications", headers={"Authorization": f"Bearer {admins['SCH011']}"})
sch011_apps = res_sch011_apps.json() if res_sch011_apps.status_code == 200 else []
if sch011_apps:
    target_app_id = sch011_apps[0]["application_id"]
    print(f"  Testing IDOR on SCH011 application: {target_app_id} using SCH001 Admin token...")
    idor_res = requests.get(f"{base_url}/school/admissions/applications/{target_app_id}", headers={"Authorization": f"Bearer {admins['SCH001']}"})
    print(f"  IDOR result: Status {idor_res.status_code} (Expected 403 or 404, detail: {idor_res.text[:100]})")

# Test 3: Cross-institution academic attendance
print("\n--- Test 3: Cross-institution Academic Attendance ---")
res = requests.get(f"{base_url}/academic/attendance?date=2026-11-05", headers={"Authorization": f"Bearer {admins['SCH001']}"})
print(f"  SCH001 Attendance query status: {res.status_code}")
if res.status_code == 200:
    foreign_att = [r for r in res.json().get("records", []) if r.get("school_id") != "SCH001"]
    print(f"  Foreign attendance leaked to SCH001 Admin: {len(foreign_att)}")

# Test 4: Cross-institution examinations
print("\n--- Test 4: Cross-institution Examinations ---")
res = requests.get(f"{base_url}/academic/examinations", headers={"Authorization": f"Bearer {admins['SCH001']}"})
print(f"  SCH001 Examinations query status: {res.status_code}")
if res.status_code == 200:
    foreign_exams = [e for e in res.json() if e.get("institution_id") != "SCH001" and e.get("school_id") != "SCH001"]
    print(f"  Foreign examinations leaked to SCH001 Admin: {len(foreign_exams)}")

# Test 5: Staff cross-institution barrier
print("\n--- Test 5: Staff Cross-Institution Access Barrier ---")
if sch011_apps:
    res = requests.get(f"{base_url}/school/admissions/applications/{sch011_apps[0]['application_id']}", headers={"Authorization": f"Bearer {staff_token}"})
    print(f"  Staff (SCH001) accessing SCH011 application: Status {res.status_code}")
