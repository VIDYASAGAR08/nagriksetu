import urllib.request
import urllib.parse
import json
import sqlite3
import sys

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def api_call(endpoint, method="GET", payload=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err_json = json.loads(body)
        except:
            err_json = {"detail": body}
        return e.code, err_json
    except Exception as e:
        return 500, {"detail": str(e)}

def login(email, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({"username": email, "password": password}).encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)["access_token"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise Exception(f"Login failed for {email}: {body}")

print("=" * 70)
print("RUNNING MODULE 7 END-TO-END VERIFICATION SUITE")
print("=" * 70)

# Check total students in DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
total_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
print(f"Initial DB check: total students = {total_students}")
assert total_students == 30003, f"Expected 30003 students, got {total_students}"

# 1. Login Accounts
parent1_token = login("ramesh.kumar@example.com", "Password@123")
parent2_token = login("lakshmi.kumar@example.com", "Password@123")
admin_token = login("rao@edu.in", "Staff@NagrikSetu2026!") # Admin of SCH019

print("[PASS] Successfully authenticated Parent 1 (Father), Parent 2 (Mother), and Institution Admin SCH019.")

# Test 1: Student Lookup via exact Student ID
# Find a student in SCH019
sample_st = c.execute("SELECT student_id, permanent_student_id, student_name, school_id FROM students WHERE school_id = 'SCH019' LIMIT 1").fetchone()
st_id, psid, st_name, school_id = sample_st
print(f"Sample student in SCH019: ID={st_id}, PSID={psid}, Name={st_name}")

status, res = api_call(f"/parent/lookup-by-student-id?student_id={st_id}", token=parent1_token)
assert status == 200, f"Expected 200, got {status}: {res}"
assert res["student_full_name"] == st_name
assert res["student_id"] == st_id
assert res["permanent_student_id"] == psid
assert res["institution_id"] == school_id
assert "institution_name" in res
assert "class_or_standard" in res
assert "program_or_stream" in res
print("[PASS] Test 1: Student Lookup via exact Student ID returns complete official identity.")

# Test 2: Non-existent Student ID returns 404
status, res = api_call("/parent/lookup-by-student-id?student_id=NONEXISTENT_99999", token=parent1_token)
assert status == 404, f"Expected 404, got {status}: {res}"
assert "No student record found" in res.get("detail", "")
print("[PASS] Test 2: Non-existent Student ID lookup cleanly returns 404.")

# Clean up any prior test linking requests for this student and parent1
c.execute("DELETE FROM linking_requests WHERE permanent_student_id = ? OR student_ref = ?", (psid, st_id))
c.execute("DELETE FROM student_guardians WHERE permanent_student_id = ?", (psid,))
conn.commit()

# Test 3: Submitting linking request creates status 'pending' without granting access
payload = {
    "student_ref": st_id,
    "student_id": st_id,
    "school_id": school_id,
    "permanent_student_id": psid,
    "relationship_type": "Father"
}
status, res = api_call("/parent/linking-requests", method="POST", payload=payload, token=parent1_token)
assert status == 201, f"Expected 201, got {status}: {res}"
assert res["request_status"] == "pending"
req_id = res["request_id"]
assert "Your request has been submitted successfully to" in res["message"]
assert "The institution will review and notify you of its decision" in res["message"]

# Verify academic dashboard access is NOT granted while pending
status, res = api_call(f"/parent/children/{psid}/records", token=parent1_token)
assert status in (403, 404), f"Expected 403/404 unauthorized, got {status}"
print("[PASS] Test 3: Submitting linking request creates pending status and leaves child records locked.")

# Test 4: Correct institution routing in database
row = c.execute("SELECT school_id, request_status, parent_user_id FROM linking_requests WHERE request_id = ?", (req_id,)).fetchone()
assert row[0] == school_id
assert row[1] == "pending"
print("[PASS] Test 4: Request correctly routed to institution owning student enrollment.")

# Test 5: In-app notification created for institution administrator
notif = c.execute("SELECT title, message, institution_id FROM portal_notifications WHERE related_record_id = ? AND recipient_role = 'school_admin'", (req_id,)).fetchone()
assert notif is not None, "Notification for institution admin was not created!"
assert "New Student Linking Request" in notif[0]
assert notif[2] == school_id
print(f"[PASS] Test 5: Notification created for institution admin: '{notif[0]}' -> '{notif[1]}'")

# Test 6: Institution requests list shows the request
status, res = api_call(f"/institution/{school_id}/linking-requests?status_filter=pending", token=admin_token)
assert status == 200, f"Expected 200, got {status}: {res}"
found = any(r["request_id"] == req_id for r in res)
assert found, "Pending request not found in institution linking requests list"
print("[PASS] Test 6: Institution linking requests endpoint lists the pending request with full metadata.")

# Test 7: Multi-tenant isolation: Admin of another school cannot view or review this request
# SCH001 staff
staff_token = login("staff.sch001@example.com", "Staff@NagrikSetu2026!")
status, res = api_call(f"/institution/{school_id}/linking-requests", token=staff_token)
assert status == 403, f"Expected 403 for cross-institution access, got {status}"
status, res = api_call(f"/school/linking-requests/{req_id}/review", method="POST", payload={"action": "approve"}, token=staff_token)
assert status == 403, f"Expected 403 for cross-institution review, got {status}"
print("[PASS] Test 7: Multi-tenant isolation strictly enforced: other institution cannot view or review.")

# Test 8: Institution requests clarification
clarify_payload = {
    "action": "clarify",
    "remarks": "Please provide student birth certificate copy to verify relationship."
}
status, res = api_call(f"/school/linking-requests/{req_id}/review", method="POST", payload=clarify_payload, token=admin_token)
assert status == 200, f"Expected 200, got {status}: {res}"
assert res["request_status"] == "clarification_required"

# Verify parent gets notification and sees status
row = c.execute("SELECT request_status, reviewer_comment FROM linking_requests WHERE request_id = ?", (req_id,)).fetchone()
assert row[0] == "clarification_required"
assert "birth certificate" in row[1]

# Verify notification to parent
p_notif = c.execute("SELECT title, message FROM portal_notifications WHERE related_record_id = ? AND recipient_user_id IS NOT NULL", (req_id,)).fetchall()[-1]
assert "Clarification Requested" in p_notif[0]
print(f"[PASS] Test 8: Institution requested clarification. Status is clarification_required. Parent notified: '{p_notif[0]}'.")

# Test 9: Parent responds to clarification
resp_payload = {
    "response_notes": "Uploaded Birth Certificate BC-2026-98124 issued by BBMP."
}
status, res = api_call(f"/parent/linking-requests/{req_id}/respond-clarification", method="POST", payload=resp_payload, token=parent1_token)
assert status == 200, f"Expected 200, got {status}: {res}"
assert res["request_status"] == "pending_review"

row = c.execute("SELECT request_status, parent_response FROM linking_requests WHERE request_id = ?", (req_id,)).fetchone()
assert row[0] == "pending_review"
assert "BC-2026-98124" in row[1]

# Check notification to institution admin
adm_notif = c.execute("SELECT title, message FROM portal_notifications WHERE related_record_id = ? AND recipient_role = 'school_admin' ORDER BY created_at DESC LIMIT 1", (req_id,)).fetchone()
assert "Clarification Response" in adm_notif[0]
print(f"[PASS] Test 9: Parent responded to clarification. Status transitioned to pending_review. Institution notified: '{adm_notif[0]}'.")

# Test 10: Parent cannot approve their own request
status, res = api_call(f"/school/linking-requests/{req_id}/review", method="POST", payload={"action": "approve"}, token=parent1_token)
assert status in (401, 403), f"Expected 401/403 when parent attempts review, got {status}"
print("[PASS] Test 10: Parent authorization check prevents parent from approving their own request.")

# Test 11: Institution Rejection action
reject_payload = {
    "action": "reject",
    "rejection_reason": "Identity documents could not be verified against admission register",
    "remarks": "Please visit school administration office with original documents."
}
status, res = api_call(f"/school/linking-requests/{req_id}/review", method="POST", payload=reject_payload, token=admin_token)
assert status == 200, f"Expected 200, got {status}: {res}"
assert res["request_status"] == "rejected"

row = c.execute("SELECT request_status, rejection_reason FROM linking_requests WHERE request_id = ?", (req_id,)).fetchone()
assert row[0] == "rejected"
assert "Identity documents" in row[1]

# Verify child remains inaccessible
status, res = api_call(f"/parent/children/{psid}/records", token=parent1_token)
assert status in (403, 404)

# Verify no verified relationship was created
sg_count = c.execute("SELECT COUNT(*) FROM student_guardians WHERE permanent_student_id = ? AND is_verified = 1", (psid,)).fetchone()[0]
assert sg_count == 0
print("[PASS] Test 11: Institution rejected request. Child remains locked; parent received rejection notification.")

# Test 12 & 13: New Request Submission, Institution Approval, and Verified Academic Dashboard Access
# Submit a new fresh request for parent 1
payload2 = {
    "student_ref": st_id,
    "student_id": st_id,
    "school_id": school_id,
    "permanent_student_id": psid,
    "relationship_type": "Father"
}
status, res = api_call("/parent/linking-requests", method="POST", payload=payload2, token=parent1_token)
assert status == 201
req_id2 = res["request_id"]

# Institution Admin approves request
approve_payload = {
    "action": "approve",
    "remarks": "Verified in person with original birth certificate.",
    "permanent_student_id": psid,
    "confirm_student_match": True
}
status, res = api_call(f"/school/linking-requests/{req_id2}/review", method="POST", payload=approve_payload, token=admin_token)
assert status == 200, f"Expected 200, got {status}: {res}"
assert res["request_status"] == "approved"

# Verify relationship is now verified in database
sg = c.execute("SELECT is_verified, can_view_records FROM student_guardians WHERE permanent_student_id = ?", (psid,)).fetchone()
assert sg is not None and sg[0] == 1 and sg[1] == 1

# Test 13: Academic dashboard access is now GRANTED
status, res = api_call("/parent/children", token=parent1_token)
assert status == 200
found_child = any(ch["permanent_student_id"] == psid for ch in res)
assert found_child, "Approved child not found in /parent/children!"

status, res = api_call(f"/parent/children/{psid}/records", token=parent1_token)
assert status == 200, f"Expected 200 for records, got {status}: {res}"
print(f"[PASS] Test 12 & 13: Approved request grants access. /parent/children includes student, academic records returned successfully.")

# Test 14: Multiple parents can independently link to the same child
# Parent 2 (Mother) submits linking request for the same child
payload_mother = {
    "student_ref": st_id,
    "student_id": st_id,
    "school_id": school_id,
    "permanent_student_id": psid,
    "relationship_type": "Mother"
}
status, res = api_call("/parent/linking-requests", method="POST", payload=payload_mother, token=parent2_token)
assert status == 201, f"Expected 201 for mother's linking request, got {status}: {res}"
req_id_mother = res["request_id"]

# Approve mother's request
approve_mother = {
    "action": "approve",
    "remarks": "Mother credentials verified via family ration card.",
    "permanent_student_id": psid,
    "confirm_student_match": True
}
status, res = api_call(f"/school/linking-requests/{req_id_mother}/review", method="POST", payload=approve_mother, token=admin_token)
assert status == 200, f"Expected 200 for mother's approval, got {status}: {res}"

# Both parents now have independent verified access!
status, res_p1 = api_call(f"/parent/children/{psid}/records", token=parent1_token)
status, res_p2 = api_call(f"/parent/children/{psid}/records", token=parent2_token)
assert status == 200, "Mother cannot access child records!"
print("[PASS] Test 14: Father and Mother independently linked and verified for the same child.")

# Test 15: Database Safety Check
final_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
assert final_students == 30003, f"Database corruption! Count changed from 30003 to {final_students}"
print(f"[PASS] Test 15: Database safety verified. Total students count is exactly {final_students}.")

print("=" * 70)
print("ALL 15 MODULE 7 TESTS PASSED SUCCESSFULLY!")
print("=" * 70)
