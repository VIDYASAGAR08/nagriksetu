import requests
import json

base_url = "http://localhost:8001"

# 1. Login as Platform Admin
login_res = requests.post(f"{base_url}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
assert login_res.status_code == 200
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[PASS] Platform Admin Login OK")

# 2. Test Degree College (COL001) Academic Structure
res = requests.get(f"{base_url}/institution/COL001/academic-structure", headers=headers)
print("COL001 Structure Status:", res.status_code)
assert res.status_code == 200
data_col = res.json()
print("COL001 Category Type:", data_col.get("category_type"))
print("COL001 Divisions count:", len(data_col.get("divisions", [])))
print("COL001 Programs count:", len(data_col.get("programs", [])))
for p in data_col.get("programs", [])[:3]:
    print(f"  Program: '{p['program_name']}' | Code: '{p['program_code']}' | Years: {p['years']} | Secs: {p['sections']}")
    assert p["program_name"], "Program name must not be empty or zero!"
    assert not str(p["program_name"]).isdigit(), "Program name must not be a digit!"

# 3. Test PU College (SCH011) Academic Structure
res_pu = requests.get(f"{base_url}/institution/SCH011/academic-structure", headers=headers)
print("\nSCH011 Structure Status:", res_pu.status_code)
assert res_pu.status_code == 200
data_pu = res_pu.json()
print("SCH011 Streams:", data_pu.get("streams"))
print("SCH011 Commerce combinations:", [c["code"] for c in data_pu.get("combinations_by_stream", {}).get("Commerce", [])])
print("SCH011 Science combinations:", [c["code"] for c in data_pu.get("combinations_by_stream", {}).get("Science", [])])
assert "PCMB" in [c["code"] for c in data_pu.get("combinations_by_stream", {}).get("Science", [])]
assert "PCMB" not in [c["code"] for c in data_pu.get("combinations_by_stream", {}).get("Commerce", [])]

# 4. Test Backend Validation: Commerce + PCMB -> MUST REJECT (400)
res_inv = requests.get(f"{base_url}/institution/SCH011/students?standard=11&stream=Commerce&combination=PCMB", headers=headers)
print("\nSCH011 Commerce + PCMB Status:", res_inv.status_code)
print("Response:", res_inv.json())
assert res_inv.status_code == 400
assert "Science combination" in res_inv.json()["detail"]
print("[PASS] Commerce + PCMB successfully rejected by backend!")

# 5. Test Backend Validation: Commerce + CEBA -> MUST ACCEPT (200)
res_ceba = requests.get(f"{base_url}/institution/SCH011/students?standard=11&stream=Commerce&combination=CEBA", headers=headers)
print("\nSCH011 Commerce + CEBA Status:", res_ceba.status_code)
assert res_ceba.status_code == 200
print("[PASS] Commerce + CEBA successfully accepted by backend!")

# 6. Test Backend Validation: Science + PCMB -> MUST ACCEPT (200)
res_pcmb = requests.get(f"{base_url}/institution/SCH011/students?standard=11&stream=Science&combination=PCMB", headers=headers)
print("\nSCH011 Science + PCMB Status:", res_pcmb.status_code)
assert res_pcmb.status_code == 200
print("[PASS] Science + PCMB successfully accepted by backend!")

# 7. Test School Filter Validation: SCH019 with Stream -> MUST REJECT (400)
res_sch_inv = requests.get(f"{base_url}/institution/SCH019/students?standard=8&stream=Science", headers=headers)
print("\nSCH019 School with Stream Status:", res_sch_inv.status_code)
print("Response:", res_sch_inv.json())
assert res_sch_inv.status_code == 400
print("[PASS] School with PU Stream successfully rejected by backend!")

# 8. Test School Standard 8 Section A -> MUST SUCCEED WITH STUDENTS (200)
res_sch = requests.get(f"{base_url}/institution/SCH019/students?standard=8&section=A", headers=headers)
print("\nSCH019 Std 8 Sec A Status:", res_sch.status_code)
assert res_sch.status_code == 200
data_sch = res_sch.json()
print(f"Total students matched: {data_sch['total']}")
assert data_sch["total"] > 0
print("Sample student:", data_sch["students"][0]["student_name"], data_sch["students"][0]["permanent_student_id"])
print("[PASS] School Std 8 Sec A student querying OK!")

print("\nALL BACKEND VALIDATION TESTS PASSED!")
