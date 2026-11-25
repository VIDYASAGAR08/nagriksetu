import json
import urllib.request
import urllib.error
from database import get_connection
from auth import create_access_token

conn = get_connection()
cur = conn.cursor()

# Get SCH001 admin
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE email = 'government.model@edu.in'")
u = dict(cur.fetchone())

# Fetch test student
cur.execute("SELECT * FROM students WHERE school_id = 'SCH001' AND student_id = 'SCH01125'")
stu = dict(cur.fetchone())
original_blood = stu.get("blood_group") or "O+"
original_phone = stu.get("contact_number") or ""
perm_id = stu["permanent_student_id"]

# Fetch test student attendance record
cur.execute("SELECT * FROM student_attendance WHERE permanent_student_id = ? LIMIT 1", (perm_id,))
att = dict(cur.fetchone())
att_id = att["attendance_id"]
original_att_status = att["status"]

# Fetch test student exam result
cur.execute("SELECT * FROM academic_results WHERE permanent_student_id = ? LIMIT 1", (perm_id,))
res = dict(cur.fetchone())
res_id = res["result_id"]
original_marks = res["marks_obtained"]

conn.close()

token = create_access_token(u, school_id="SCH001")

print("--- Testing Write Operations ---")

# 1. Test Student Record Edit
edit_payload = {
    "blood_group": "AB+",
    "contact_number": "9876501234",
    "reason": "Administrative correction based on verified blood bank report and parent mobile update",
    "source": "Direct Admin Edit"
}
req = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps(edit_payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print("Test 1 (Edit Student):", data)

# 2. Test Attendance Correction
att_payload = {
    "new_status": "present" if original_att_status == "absent" else "absent",
    "remarks": "Verified manual attendance register correction",
    "reason": "Student attended classroom session; biometric/manual record mismatch corrected"
}
req2 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125/attendance/{att_id}",
    data=json.dumps(att_payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req2) as resp:
    data2 = json.loads(resp.read().decode())
    print("Test 2 (Attendance Correction):", data2)

# 3. Test Exam Result Correction
exam_payload = {
    "marks_obtained": 88.0,
    "maximum_marks": 100.0,
    "grade": "A+",
    "reason": "Subject teacher re-evaluation after student representation on Question 4"
}
req3 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125/results/{res_id}",
    data=json.dumps(exam_payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req3) as resp:
    data3 = json.loads(resp.read().decode())
    print("Test 3 (Exam Result Correction):", data3)

# 4. Check Audit History for SCH01125
req4 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125/audit-history",
    headers={"Authorization": f"Bearer {token}"}
)
with urllib.request.urlopen(req4) as resp:
    data4 = json.loads(resp.read().decode())
    print("\nTest 4 (Audit History): Total events =", data4["total_audit_events"])
    for ev in data4["audit_trail"][:5]:
        print(f"  Field: {ev['field_modified']} | {ev['previous_value']} -> {ev['updated_value']} | Reason: {ev['reason']}")

# 5. Clean Revert of test student values back to original
revert_payload = {
    "blood_group": original_blood,
    "contact_number": original_phone,
    "reason": "Reverting test verification modifications back to canonical state"
}
req5 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps(revert_payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req5) as resp:
    pass

# Revert attendance
revert_att = {
    "new_status": original_att_status,
    "remarks": att.get("remarks") or "",
    "reason": "Reverting test verification attendance back to canonical state"
}
req6 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125/attendance/{att_id}",
    data=json.dumps(revert_att).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req6) as resp:
    pass

# Revert exam
revert_exam = {
    "marks_obtained": original_marks,
    "maximum_marks": res.get("maximum_marks") or 100.0,
    "grade": res.get("grade") or "A",
    "reason": "Reverting test verification exam results back to canonical state"
}
req7 = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/SCH01125/results/{res_id}",
    data=json.dumps(revert_exam).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req7) as resp:
    pass

print("\n--- ALL WRITE TESTS & REVERSIONS COMPLETED SUCCESSFULLY ---")
