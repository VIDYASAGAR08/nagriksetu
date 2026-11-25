import json
import urllib.request
import urllib.error
from database import get_connection
from auth import create_access_token

conn = get_connection()
cur = conn.cursor()

# Get an institution admin for SCH001 (Government Model Primary School)
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE email = 'government.model@edu.in'")
u = dict(cur.fetchone())
print("Found school admin:", u)

# Also check platform admin
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE role = 'platform_admin'")
pa = dict(cur.fetchone())
print("Found platform admin:", pa)

# Fetch a sample student in SCH001
cur.execute("SELECT student_id, permanent_student_id, student_name, standard, section FROM students WHERE school_id = 'SCH001' LIMIT 1")
sample_stu = dict(cur.fetchone())
print("Sample student in SCH001:", sample_stu)
sample_sid = sample_stu["student_id"]

conn.close()

# Generate valid JWT token for the school admin (SCH001)
token_sch001 = create_access_token(u, school_id="SCH001")
print("Generated token for SCH001 admin.")

# Test 1: GET /institution/SCH001/student-management/stats
req = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/student-management/stats",
    headers={"Authorization": f"Bearer {token_sch001}"}
)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("\n--- Test 1: Student Management Stats ---")
        print("Status code:", resp.status)
        print("Institution:", data["institution_name"])
        print("Total students:", data["total_students"])
        print("Active students:", data["active_students"])
        print("Pending requests count:", data["pending_correction_requests_count"])
except Exception as e:
    print("Test 1 FAILED:", e)

# Test 2: GET /institution/SCH001/students (filter by standard and pagination)
req2 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/students?standard=1&limit=5",
    headers={"Authorization": f"Bearer {token_sch001}"}
)
try:
    with urllib.request.urlopen(req2) as resp:
        data2 = json.loads(resp.read().decode())
        print("\n--- Test 2: List Students Standard 1 ---")
        print("Total matching:", data2["total"])
        sample = data2["students"][0]
        print("Sample student:", sample["student_id"], sample["student_name"], sample["academic_division"], sample["class_or_standard_display"])
except Exception as e:
    print("Test 2 FAILED:", e)

# Test 3: Search by Parent Name
req3 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/students?search=Kumar",
    headers={"Authorization": f"Bearer {token_sch001}"}
)
try:
    with urllib.request.urlopen(req3) as resp:
        data3 = json.loads(resp.read().decode())
        print("\n--- Test 3: Search by Parent Name 'Kumar' ---")
        print("Total found:", data3["total"])
except Exception as e:
    print("Test 3 FAILED:", e)

# Test 4: Cross-institution authorization check
# Try to access SCH002 using SCH001 token -> MUST FAIL WITH 403
req4 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH002/student-management/stats",
    headers={"Authorization": f"Bearer {token_sch001}"}
)
try:
    with urllib.request.urlopen(req4) as resp:
        print("Test 4 FAILED: Cross-institution request should have been rejected!")
except urllib.error.HTTPError as he:
    print("\n--- Test 4: Cross-Institution Security Check ---")
    print(f"Correctly rejected with HTTP {he.code}: {he.reason}")

# Test 5: GET /institution/SCH001/students/{sample_sid} (Profile + Record History)
req5 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/{sample_sid}",
    headers={"Authorization": f"Bearer {token_sch001}"}
)
try:
    with urllib.request.urlopen(req5) as resp:
        data5 = json.loads(resp.read().decode())
        print("\n--- Test 5: Student Profile ---")
        print("Status code:", resp.status)
        print("Student Name:", data5["personal_info"]["student_name"])
        print("Taluk:", data5["personal_info"].get("taluk"))
        print("Record History entries:", len(data5.get("record_history", [])))
        print("Pending Requests entries:", len(data5.get("pending_requests", [])))
except Exception as e:
    print("Test 5 FAILED:", e)
