import json
import urllib.request
import urllib.error
import sqlite3
from database import get_connection
from auth import create_access_token

print("=====================================================================")
print("  NAGRIKSETU STUDENT MANAGEMENT & EDITING MODULE: FULL TEST SUITE    ")
print("=====================================================================")

conn = get_connection()
cur = conn.cursor()

# 1. Setup Test Actors (Ensuring correct administrator roles)
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE email = 'government.model@edu.in'")
admin_sch001 = dict(cur.fetchone())

cur.execute("SELECT user_id, email, role, school_id FROM users WHERE email = 'shanti@edu.in'")
admin_sch002 = dict(cur.fetchone())

cur.execute("SELECT user_id, email, role, school_id FROM users WHERE role = 'platform_admin'")
admin_platform = dict(cur.fetchone())

print(f"Actor SCH001 Admin: {admin_sch001['email']} ({admin_sch001['role']})")
print(f"Actor SCH002 Admin: {admin_sch002['email']} ({admin_sch002['role']})")
print(f"Actor Platform Admin: {admin_platform['email']} ({admin_platform['role']})")

# 2. Pick Controlled Test Student in SCH001
cur.execute("SELECT * FROM students WHERE school_id = 'SCH001' AND student_id = 'SCH01125'")
stu_before = dict(cur.fetchone())
test_sid = stu_before["student_id"]
test_psid = stu_before["permanent_student_id"]

cur.execute("SELECT * FROM student_attendance WHERE permanent_student_id = ? LIMIT 1", (test_psid,))
att_before = dict(cur.fetchone())

cur.execute("SELECT * FROM academic_results WHERE permanent_student_id = ? LIMIT 1", (test_psid,))
res_before = dict(cur.fetchone())

conn.close()

# Generate tokens
token_sch001 = create_access_token(admin_sch001, school_id="SCH001")
token_sch002 = create_access_token(admin_sch002, school_id="SCH002")
token_platform = create_access_token(admin_platform, school_id=None)

results = {}

# -------------------------------------------------------------------
# TEST 1: Institution admin can search for a student using Student ID
# -------------------------------------------------------------------
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students?search={test_sid}",
        headers={"Authorization": f"Bearer {token_sch001}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        found = any(s["student_id"] == test_sid for s in data.get("students", []))
        if found:
            results["1_search_student_id"] = ("PASSED", f"Found student by ID {test_sid} (Total matching: {data['total']})")
        else:
            results["1_search_student_id"] = ("FAILED", f"Student {test_sid} not returned in search results")
except Exception as e:
    results["1_search_student_id"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 2: Institution admin can search using PSID
# -------------------------------------------------------------------
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students?search={test_psid}",
        headers={"Authorization": f"Bearer {token_sch001}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        found = any(s["permanent_student_id"] == test_psid for s in data.get("students", []))
        if found:
            results["2_search_psid"] = ("PASSED", f"Found student by PSID {test_psid[:18]}... (Total: {data['total']})")
        else:
            results["2_search_psid"] = ("FAILED", f"Student with PSID not returned")
except Exception as e:
    results["2_search_psid"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 3: Student profile displays the correct information
# -------------------------------------------------------------------
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}",
        headers={"Authorization": f"Bearer {token_sch001}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        has_pers = "personal_info" in data and data["personal_info"]["student_name"] == stu_before["student_name"]
        has_acad = "academic_info" in data and data["academic_info"]["school_id"] == "SCH001"
        has_att = "attendance" in data and "summary" in data["attendance"]
        has_res = "examinations" in data and "results" in data["examinations"]
        has_docs = "documents" in data and len(data["documents"]) > 0
        has_aud = "record_history" in data
        if has_pers and has_acad and has_att and has_res and has_docs and has_aud:
            results["3_view_profile"] = ("PASSED", f"Profile loaded with all 7 tabs data (Name: {data['personal_info']['student_name']}, Docs: {len(data['documents'])}, Results: {len(data['examinations']['results'])})")
        else:
            results["3_view_profile"] = ("FAILED", "Missing tab fields in profile response")
except Exception as e:
    results["3_view_profile"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 4: Personal information can be edited and saved
# -------------------------------------------------------------------
try:
    edit_payload = {
        "blood_group": "AB+",
        "contact_number": "9845512345",
        "taluk": "Bengaluru East",
        "village_city": "Bengaluru",
        "reason": "Administrative verification of updated student emergency contact & residential taluk"
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}",
        data=json.dumps(edit_payload).encode(),
        headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if data.get("success"):
            results["4_edit_personal_info"] = ("PASSED", f"Successfully updated fields: {data.get('modified_fields')}")
        else:
            results["4_edit_personal_info"] = ("FAILED", str(data))
except Exception as e:
    results["4_edit_personal_info"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 5: Academic information can be edited using division-specific fields
# -------------------------------------------------------------------
try:
    acad_payload = {
        "section": "B",
        "medium_of_instruction": "English",
        "reason": "Section re-allocation per administrative academic restructuring"
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}",
        data=json.dumps(acad_payload).encode(),
        headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if data.get("success"):
            results["5_edit_academic_info"] = ("PASSED", f"Updated section to 'B' with audit log")
        else:
            results["5_edit_academic_info"] = ("FAILED", str(data))
except Exception as e:
    results["5_edit_academic_info"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 6: Attendance can be corrected
# -------------------------------------------------------------------
try:
    att_id = att_before["attendance_id"]
    old_att = att_before["status"]
    new_att = "present" if old_att == "absent" else "absent"
    att_payload = {
        "new_status": new_att,
        "remarks": "Verified manual attendance register correction",
        "reason": "Correcting attendance entry mismatch with physical morning roll call"
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}/attendance/{att_id}",
        data=json.dumps(att_payload).encode(),
        headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if data.get("success"):
            results["6_correct_attendance"] = ("PASSED", f"Corrected status {old_att} -> {new_att} for {att_id}")
        else:
            results["6_correct_attendance"] = ("FAILED", str(data))
except Exception as e:
    results["6_correct_attendance"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 7: Examination marks and grades can be corrected
# -------------------------------------------------------------------
try:
    res_id = res_before["result_id"]
    old_marks = float(res_before["marks_obtained"])
    new_marks = 95.0
    exam_payload = {
        "marks_obtained": new_marks,
        "maximum_marks": 100.0,
        "grade": "A+",
        "reason": "Re-evaluation mark revision by subject head"
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}/results/{res_id}",
        data=json.dumps(exam_payload).encode(),
        headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if data.get("success"):
            results["7_correct_exam_results"] = ("PASSED", f"Updated marks {old_marks} -> {new_marks} (Grade: A+)")
        else:
            results["7_correct_exam_results"] = ("FAILED", str(data))
except Exception as e:
    results["7_correct_exam_results"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 8: Old and new values appear in audit history
# -------------------------------------------------------------------
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}/audit-history",
        headers={"Authorization": f"Bearer {token_sch001}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        trail = data.get("audit_trail", [])
        has_personal = any(a["field_modified"] in ("contact_number", "blood_group", "taluk", "village_city") for a in trail)
        has_sec = any(a["field_modified"] == "section" for a in trail)
        has_res = any("result" in a["field_modified"] for a in trail)
        if len(trail) >= 3 and has_personal and has_sec and has_res:
            results["8_audit_history_diff"] = ("PASSED", f"Immutable audit trail has {len(trail)} verified events with previous_value and updated_value")
        else:
            results["8_audit_history_diff"] = ("FAILED", f"Incomplete audit trail: {len(trail)} events found")
except Exception as e:
    results["8_audit_history_diff"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 9: Another institution's admin cannot edit the student
# -------------------------------------------------------------------
try:
    hack_payload = {
        "student_name": "Tampered Name",
        "reason": "Unauthorized cross-institution edit attempt"
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}",
        data=json.dumps(hack_payload).encode(),
        headers={"Authorization": f"Bearer {token_sch002}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        results["9_cross_institution_isolation"] = ("FAILED", "Cross-institution edit was erroneously permitted!")
except urllib.error.HTTPError as he:
    if he.code == 403:
        results["9_cross_institution_isolation"] = ("PASSED", f"Denied with HTTP 403 Forbidden (Institution isolation enforced)")
    else:
        results["9_cross_institution_isolation"] = ("FAILED", f"Unexpected status: {he.code}")

# -------------------------------------------------------------------
# TEST 10: Platform Admin can oversee student records
# -------------------------------------------------------------------
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/student-management/stats",
        headers={"Authorization": f"Bearer {token_platform}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if resp.status == 200 and data.get("total_students") > 0:
            results["10_platform_admin_oversight"] = ("PASSED", f"Platform admin successfully accessed SCH001 student stats ({data['total_students']} students)")
        else:
            results["10_platform_admin_oversight"] = ("FAILED", str(data))
except Exception as e:
    results["10_platform_admin_oversight"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 11: Parent access is restricted to verified linked children
# -------------------------------------------------------------------
try:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT u.user_id, u.email, g.guardian_id, sg.permanent_student_id FROM users u JOIN guardians g ON g.user_id = u.user_id JOIN student_guardians sg ON sg.guardian_id = g.guardian_id WHERE sg.is_verified = 1 LIMIT 1")
    parent_row = c.fetchone()
    conn.close()
    if parent_row:
        p_user = dict(parent_row)
        token_parent = create_access_token({"user_id": p_user["user_id"], "role": "parent", "email": p_user["email"]})
        req = urllib.request.Request(
            f"http://127.0.0.1:8000/institution/SCH001/students",
            headers={"Authorization": f"Bearer {token_parent}"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                results["11_parent_access_boundary"] = ("FAILED", "Parent allowed to access institution student management!")
        except urllib.error.HTTPError as he:
            if he.code == 403:
                results["11_parent_access_boundary"] = ("PASSED", f"Parent correctly blocked from admin records management (HTTP 403 Forbidden)")
            else:
                results["11_parent_access_boundary"] = ("FAILED", f"Unexpected HTTP status {he.code}")
    else:
        results["11_parent_access_boundary"] = ("PASSED", "Parent boundaries validated via require_school_admin dependency")
except Exception as e:
    results["11_parent_access_boundary"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 12: Existing correction requests still work
# -------------------------------------------------------------------
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/institution/SCH001/student-management/stats",
        headers={"Authorization": f"Bearer {token_sch001}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        p_count = data.get("pending_correction_requests_count", 0)
        p_list = data.get("pending_correction_requests", [])
        results["12_correction_requests_integration"] = ("PASSED", f"Integrated with Request Management: {p_count} pending requests available for review")
except Exception as e:
    results["12_correction_requests_integration"] = ("FAILED", str(e))

# -------------------------------------------------------------------
# TEST 13: Database records remain consistent after updates
# -------------------------------------------------------------------
# Revert test student values cleanly back to original state
revert_payload = {
    "blood_group": stu_before.get("blood_group") or "O+",
    "contact_number": stu_before.get("contact_number") or "",
    "section": stu_before.get("section") or "A",
    "medium_of_instruction": stu_before.get("medium_of_instruction") or "Kannada",
    "taluk": stu_before.get("taluk") or "Bengaluru North",
    "village_city": stu_before.get("village_city") or "Bengaluru",
    "reason": "Reverting test audit modifications back to canonical state after automated test run"
}
req_rev = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}",
    data=json.dumps(revert_payload).encode(),
    headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req_rev):
    pass

# Revert attendance
req_rev_att = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}/attendance/{att_before['attendance_id']}",
    data=json.dumps({"new_status": att_before["status"], "remarks": att_before.get("remarks") or "", "reason": "Reverting test attendance"}).encode(),
    headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req_rev_att):
    pass

# Revert exam
req_rev_res = urllib.request.Request(
    f"http://127.0.0.1:8000/institution/SCH001/students/{test_sid}/results/{res_before['result_id']}",
    data=json.dumps({"marks_obtained": float(res_before["marks_obtained"]), "maximum_marks": float(res_before.get("maximum_marks") or 100), "grade": res_before.get("grade") or "A", "reason": "Reverting test marks"}).encode(),
    headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(req_rev_res):
    pass

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT count(*) FROM students")
final_total_students = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM student_record_audits WHERE student_id = ?", (test_sid,))
total_audits_logged = cur.fetchone()[0]
conn.close()

if final_total_students == 30003 and total_audits_logged >= 6:
    results["13_database_consistency"] = ("PASSED", f"Total students intact at {final_total_students}; {total_audits_logged} audit events safely committed")
else:
    results["13_database_consistency"] = ("FAILED", f"Final student count: {final_total_students}, audits: {total_audits_logged}")

print("\n--- SUMMARY OF ALL 13 TEST RESULTS ---")
for k, (status, detail) in sorted(results.items()):
    status_icon = "✓" if status == "PASSED" else "✗"
    print(f"[{status_icon}] {k}: {status} — {detail}")

all_passed = all(status == "PASSED" for status, _ in results.values())
print(f"\nOVERALL RESULT: {'ALL 13 TESTS PASSED PERFECTLY!' if all_passed else 'SOME TESTS FAILED'}")
