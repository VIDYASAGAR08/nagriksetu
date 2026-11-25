import os
import sys
import sqlite3
import json
import hashlib
import time
import urllib.request
import urllib.error
import urllib.parse

from auth import create_access_token

BASE_URL = "http://localhost:8000"
DB_PATH = "/app/data/nagriksetu.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_token_for_user(user_id, school_id=None):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not u:
        raise Exception(f"User {user_id} not found in DB")
    user_dict = dict(u)
    return create_access_token(user_dict, school_id=school_id or user_dict.get("school_id")), user_dict

def api_call(method, endpoint, payload=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"detail": err_body}

def run_tests():
    print("=" * 70)
    print("STARTING NAGRIKSETU PARENT-CHILD LINKING VERIFICATION SECURITY AUDIT")
    print("=" * 70)

    conn = get_db()
    c = conn.cursor()

    # Find two distinct parent users
    parents = c.execute("SELECT user_id, email, full_name FROM users WHERE role = 'parent' LIMIT 2").fetchall()
    assert len(parents) >= 2, "Need at least 2 parents in DB"
    parent_1_id = parents[0]["user_id"]
    parent_2_id = parents[1]["user_id"]

    parent_token, parent_user = get_token_for_user(parent_1_id)
    parent_2_token, parent_user_2 = get_token_for_user(parent_2_id)

    # Find staff for SCH001 and staff for another school SCH019
    staff_1 = c.execute("SELECT user_id, email, role, school_id FROM users WHERE role IN ('school_admin', 'school_staff') AND school_id = 'SCH001' LIMIT 1").fetchone()
    if not staff_1:
        staff_1 = c.execute("SELECT user_id, email, role, school_id FROM users WHERE role IN ('school_admin', 'school_staff') AND school_id IS NOT NULL LIMIT 1").fetchone()

    target_school_id = staff_1["school_id"]
    staff_token, staff_user = get_token_for_user(staff_1["user_id"], school_id=target_school_id)

    # Find staff from a DIFFERENT school
    staff_2 = c.execute("SELECT user_id, email, role, school_id FROM users WHERE role IN ('school_admin', 'school_staff') AND school_id IS NOT NULL AND school_id != ? LIMIT 1", (target_school_id,)).fetchone()
    other_school_id = staff_2["school_id"]
    other_staff_token, other_staff_user = get_token_for_user(staff_2["user_id"], school_id=other_school_id)

    print(f"[TEST SETUP] Parent 1 (Father): {parent_user['full_name']} ({parent_user['user_id']})")
    print(f"[TEST SETUP] Parent 2 (Mother): {parent_user_2['full_name']} ({parent_user_2['user_id']})")
    print(f"[TEST SETUP] School Staff ({target_school_id}): {staff_user['email']} ({staff_user['user_id']})")
    print(f"[TEST SETUP] Other School Staff ({other_school_id}): {other_staff_user['email']} ({other_staff_user['user_id']})")

    # Find an enrolled student at target_school_id that is NOT yet linked to parent 1 or parent 2
    student = c.execute("""
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, sc.school_name
        FROM students s
        JOIN schools sc ON sc.school_id = s.school_id
        WHERE s.school_id = ?
        AND s.permanent_student_id NOT IN (
            SELECT permanent_student_id FROM student_guardians WHERE guardian_id IN (
                SELECT guardian_id FROM guardians WHERE user_id IN (?, ?)
            )
        )
        ORDER BY s.student_id ASC
        LIMIT 1
    """, (target_school_id, parent_1_id, parent_2_id)).fetchone()
    assert student, f"No unlinked student found in {target_school_id}"
    print(f"[TEST SETUP] Target Student: {student['student_name']} (ID: {student['student_id']}, PSID: {student['permanent_student_id']}, School: {student['school_name']})")
    conn.close()

    print("\n--- TEST 1: Lookup Child by Exact Student ID ---")
    status, lookup_data = api_call("GET", f"/parent/lookup-by-student-id?student_id={student['student_id']}", token=parent_token)
    assert status == 200, f"Lookup failed: {status} {lookup_data}"
    assert lookup_data["student_id"] == student["student_id"]
    assert lookup_data["student_full_name"] == student["student_name"]
    assert lookup_data["institution_id"] == target_school_id
    assert lookup_data["is_already_linked"] == False
    print("✓ TEST 1 PASSED: Exact Student ID lookup succeeded with accurate institution details.")

    print("\n--- TEST 2: Request Linking Code & Verify Zero Plaintext Exposure ---")
    status, req_data = api_call("POST", "/parent/request-linking-code", payload={"student_id": student["student_id"], "relationship_type": "Father"}, token=parent_token)
    assert status == 200, f"Request linking code failed: {status} {req_data}"

    # CRITICAL SECURITY CHECKS:
    # A. Parent response MUST NOT contain verification_code, plain_code, or code
    assert "verification_code" not in req_data, "SECURITY VIOLATION: verification_code leaked in parent response!"
    assert "plain_code" not in req_data, "SECURITY VIOLATION: plain_code leaked in parent response!"
    assert "code" not in req_data, "SECURITY VIOLATION: code leaked in parent response!"
    assert "Your child-linking request has been submitted to the institution" in req_data["message"]
    print("✓ Parent response contains required message and ZERO code fields.")

    # B. DB check: institution_linking_codes MUST NOT store plaintext code
    conn = get_db()
    c = conn.cursor()
    code_record = c.execute("""
        SELECT code_id, permanent_student_id, student_id, institution_id, parent_user_id,
               code_hash, plain_code, attempts, max_attempts, is_used, expires_at
        FROM institution_linking_codes
        WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
        ORDER BY created_at DESC LIMIT 1
    """, (student["permanent_student_id"], parent_1_id)).fetchone()
    assert code_record, "No code record found in DB"
    assert code_record["plain_code"] is None, f"SECURITY VIOLATION: plain_code column is not NULL! Value: {code_record['plain_code']}"
    assert len(code_record["code_hash"]) == 64, f"Invalid SHA-256 hash length: {len(code_record['code_hash'])}"
    assert code_record["attempts"] == 0
    assert code_record["max_attempts"] == 5
    assert code_record["is_used"] == 0
    print("✓ Database record verified: code_hash is 64-char SHA256 hex; plain_code is strictly NULL.")

    # C. linking_requests check: pending request created for institution desk
    lr_record = c.execute("""
        SELECT request_id, parent_user_id, school_id, student_ref, request_status
        FROM linking_requests
        WHERE permanent_student_id = ? AND parent_user_id = ? AND request_status = 'pending'
    """, (student["permanent_student_id"], parent_1_id)).fetchone()
    assert lr_record, "Pending linking request record was not created for institution admin"
    print(f"✓ Institution linking request created: Request ID {lr_record['request_id']} (Status: {lr_record['request_status']})")
    conn.close()
    print("✓ TEST 2 PASSED: Code generation is secure; zero plaintext code exposed in API or DB.")

    print("\n--- TEST 3: Rate Limiting on Code Request ---")
    status, rate_data = api_call("POST", "/parent/request-linking-code", payload={"student_id": student["student_id"]}, token=parent_token)
    assert status == 429, f"Expected 429 Rate Limit, got {status}"
    print(f"✓ TEST 3 PASSED: Rate limit enforced properly (HTTP 429: {rate_data.get('detail')})")

    print("\n--- TEST 4: Institution Multi-Tenant Security & Isolation ---")
    # A. Other institution's staff CANNOT access linking requests for target_school_id
    status, _ = api_call("GET", f"/institution/{target_school_id}/linking-requests", token=other_staff_token)
    assert status == 403, f"Expected 403 Forbidden for cross-institution view, got {status}"
    print("✓ Multi-tenant check: Other institution staff receives HTTP 403 Forbidden on request listing.")

    # B. Other institution's staff CANNOT issue code for this request
    status, _ = api_call("POST", f"/school/linking-requests/{lr_record['request_id']}/issue-code", payload={}, token=other_staff_token)
    assert status == 403, f"Expected 403 Forbidden for cross-institution issue-code, got {status}"
    print("✓ Multi-tenant check: Other institution staff receives HTTP 403 Forbidden on issuing code.")

    # C. Correct institution staff CAN view the request
    status, inst_requests = api_call("GET", f"/institution/{target_school_id}/linking-requests", token=staff_token)
    assert status == 200, f"Staff failed to list linking requests: {status}"
    matched_req = next((x for x in inst_requests if x["request_id"] == lr_record["request_id"]), None)
    assert matched_req, "Institution staff could not find the pending request"
    assert matched_req["parent_user_id"] == parent_1_id
    assert matched_req["student_id"] == student["student_id"]
    print("✓ Multi-tenant check: Authorized institution staff retrieves request with Parent Account ID and Student ID.")

    # D. Correct institution staff issues official 6-digit code
    status, issue_data = api_call("POST", f"/school/linking-requests/{lr_record['request_id']}/issue-code", payload={}, token=staff_token)
    assert status == 200, f"Staff failed to issue code: {status} {issue_data}"
    assert "verification_code" in issue_data
    official_code = issue_data["verification_code"]
    assert len(official_code) == 6 and official_code.isdigit()
    print(f"✓ Authorized administrator issued code: {official_code} (Valid for {issue_data['expires_in_minutes']} mins)")

    # Verify that in DB, plain_code is STILL NULL!
    conn = get_db()
    c = conn.cursor()
    new_code_rec = c.execute("""
        SELECT code_hash, plain_code, is_used FROM institution_linking_codes
        WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
        ORDER BY created_at DESC LIMIT 1
    """, (student["permanent_student_id"], parent_1_id)).fetchone()
    assert new_code_rec["plain_code"] is None, "SECURITY VIOLATION: plain_code stored in DB during staff issue-code!"
    assert hashlib.sha256(official_code.encode("utf-8")).hexdigest() == new_code_rec["code_hash"]
    print("✓ DB verification: Staff-issued code hash matches SHA-256; plain_code remains NULL.")
    conn.close()
    print("✓ TEST 4 PASSED: Multi-tenant institution isolation verified.")

    print("\n--- TEST 5: Failed Verification Attempts & Code Invalidation ---")
    # A. 1st wrong attempt
    status, res = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": "000000"}, token=parent_token)
    assert status == 400
    assert "4 attempt(s) remaining" in res.get("detail", "")
    print("✓ Attempt 1 rejected, 4 attempts remaining.")

    # B. 2nd, 3rd, 4th wrong attempts
    for i in range(3):
        status, res = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": f"11111{i}"}, token=parent_token)
        assert status == 400

    # C. 5th wrong attempt -> should lock code
    status, res = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": "999999"}, token=parent_token)
    assert status == 400
    assert "Maximum attempts exceeded" in res.get("detail", "") or "invalidated" in res.get("detail", "")
    print("✓ Attempt 5 rejected: Maximum attempts exceeded and code invalidated.")

    # D. Attempt with correct code now fails because code has been invalidated
    status, res = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": official_code}, token=parent_token)
    assert status == 400
    print("✓ Invalidation verified: Code cannot be used after 5 failed attempts.")
    print("✓ TEST 5 PASSED: Failed attempt counter & automatic invalidation work perfectly.")

    print("\n--- TEST 6: Expired Code Handling ---")
    # Generate new code via staff
    status, issue_res = api_call("POST", f"/school/linking-requests/{lr_record['request_id']}/issue-code", payload={}, token=staff_token)
    assert status == 200
    expired_code = issue_res["verification_code"]

    # Manually expire this code in DB for testing
    conn = get_db()
    conn.execute("UPDATE institution_linking_codes SET expires_at = '2020-01-01T00:00:00' WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0", (student["permanent_student_id"], parent_1_id))
    conn.commit()
    conn.close()

    status, res = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": expired_code}, token=parent_token)
    assert status == 400
    assert "expired" in res.get("detail", "").lower()
    print("✓ TEST 6 PASSED: Expired code rejected with clear expiration message.")

    print("\n--- TEST 7: Successful Parent-Child Verification & Authorization ---")
    # Generate fresh valid code via staff
    status, issue_res = api_call("POST", f"/school/linking-requests/{lr_record['request_id']}/issue-code", payload={}, token=staff_token)
    assert status == 200
    valid_code = issue_res["verification_code"]

    # Parent verifies with valid code
    status, success_data = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": valid_code, "relationship_type": "Father"}, token=parent_token)
    assert status == 200, f"Verification failed: {status} {success_data}"
    assert success_data["status"] == "success"
    assert student["student_name"] in success_data["message"]
    print("✓ Parent verification succeeded.")

    # Verify student_guardians entry
    conn = get_db()
    c = conn.cursor()
    sg_entry = c.execute("""
        SELECT sg.is_verified, sg.can_view_records, g.relationship
        FROM student_guardians sg
        JOIN guardians g ON g.guardian_id = sg.guardian_id
        WHERE sg.permanent_student_id = ? AND g.user_id = ?
    """, (student["permanent_student_id"], parent_1_id)).fetchone()
    assert sg_entry, "No student_guardians record found"
    assert sg_entry["is_verified"] == 1
    assert sg_entry["can_view_records"] == 1
    print("✓ DB check: student_guardians verified=1, can_view_records=1.")

    # Verify code marked as used
    used_code = c.execute("SELECT is_used FROM institution_linking_codes WHERE permanent_student_id = ? AND parent_user_id = ? ORDER BY created_at DESC LIMIT 1", (student["permanent_student_id"], parent_1_id)).fetchone()
    assert used_code["is_used"] == 1
    print("✓ DB check: institution_linking_codes marked is_used=1.")

    # Verify linking_requests marked approved
    req_updated = c.execute("SELECT request_status FROM linking_requests WHERE request_id = ?", (lr_record["request_id"],)).fetchone()
    assert req_updated["request_status"] == "approved"
    print("✓ DB check: linking_requests marked approved.")

    # Verify audit_logs recorded
    audit_log = c.execute("SELECT action, actor_role, entity_id FROM audit_logs WHERE action = 'PARENT_CHILD_VERIFIED_AND_LINKED' AND entity_id = ? ORDER BY created_at DESC LIMIT 1", (student["permanent_student_id"],)).fetchone()
    assert audit_log, "Audit log was not recorded"
    print("✓ DB check: Audit log PARENT_CHILD_VERIFIED_AND_LINKED created.")
    conn.close()

    # B. Prevent Code Reuse
    status, res = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": valid_code}, token=parent_token)
    assert status in (400, 409), f"Code reuse should fail, got {status}"
    print("✓ Code reuse prevention verified: Used code cannot be reused.")

    # C. Prevent Duplicate Link
    status, res = api_call("GET", f"/parent/lookup-by-student-id?student_id={student['student_id']}", token=parent_token)
    assert status == 200
    assert res["is_already_linked"] == True
    print("✓ Duplicate link prevention: lookup-by-student-id returns is_already_linked=True.")
    print("✓ TEST 7 PASSED: Verification, relationship creation, and reuse prevention confirmed.")

    print("\n--- TEST 8: Independent Parent Linking (Mother & Father) ---")
    # Parent 2 (Mother) requests to link to the SAME student
    status, _ = api_call("POST", "/parent/request-linking-code", payload={"student_id": student["student_id"], "relationship_type": "Mother"}, token=parent_2_token)
    assert status == 200, f"Parent 2 request failed: {status}"

    # Get new linking request id
    conn = get_db()
    lr2 = conn.execute("SELECT request_id FROM linking_requests WHERE permanent_student_id = ? AND parent_user_id = ? AND request_status = 'pending'", (student["permanent_student_id"], parent_2_id)).fetchone()
    assert lr2, "Pending request for Parent 2 not found"
    conn.close()

    # Staff issues code for Parent 2
    status, p2_issue = api_call("POST", f"/school/linking-requests/{lr2['request_id']}/issue-code", payload={}, token=staff_token)
    assert status == 200
    p2_code = p2_issue["verification_code"]

    # Parent 2 verifies
    status, _ = api_call("POST", "/parent/verify-and-link-child", payload={"student_id": student["student_id"], "verification_code": p2_code, "relationship_type": "Mother"}, token=parent_2_token)
    assert status == 200

    # Verify both parents are linked to the same student in DB
    conn = get_db()
    parents_linked = conn.execute("""
        SELECT g.user_id, g.full_name, sg.is_verified
        FROM student_guardians sg
        JOIN guardians g ON g.guardian_id = sg.guardian_id
        WHERE sg.permanent_student_id = ? AND sg.is_verified = 1
    """, (student["permanent_student_id"],)).fetchall()
    conn.close()

    assert len(parents_linked) >= 2, f"Expected at least 2 linked guardians, found {len(parents_linked)}"
    user_ids_linked = [p["user_id"] for p in parents_linked]
    assert parent_1_id in user_ids_linked
    assert parent_2_id in user_ids_linked
    print(f"✓ Independent linking verified: Both Father ({parent_1_id}) and Mother ({parent_2_id}) successfully linked to student {student['student_name']}.")
    print("✓ TEST 8 PASSED: Multi-guardian independent authorization verified.")

    print("\n--- TEST 9: Check Parent /parent/children Academic Enrichment ---")
    status, children = api_call("GET", "/parent/children", token=parent_token)
    assert status == 200
    linked_child = next((c for c in children if c["student_id"] == student["student_id"]), None)
    assert linked_child, "Newly linked child not found in /parent/children list"
    assert linked_child["is_verified"] == 1
    assert "institution_name" in linked_child
    assert "program_or_stream" in linked_child
    print(f"✓ Parent portal reflects child: {linked_child['student_name']} ({linked_child['program_or_class']}) at {linked_child['institution_name']}.")
    print("✓ TEST 9 PASSED: Children list returns enriched academic records.")

    print("\n" + "=" * 70)
    print("ALL 9 SECURITY AUDIT TESTS PASSED WITH ZERO FAILURES!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
