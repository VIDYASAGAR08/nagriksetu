import json
import sqlite3
import sys
import urllib.request
import urllib.error
import urllib.parse
import uuid

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
API_URL = "http://localhost:8001"

def api_call(path, method="GET", data=None, token=None):
    url = f"{API_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            raw = res.read()
            try:
                text = raw.decode("utf-8")
                return res.status, json.loads(text) if text else None
            except Exception:
                return res.status, raw
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
            return e.code, parsed
        except Exception:
            return e.code, {"detail": err_body}
    except Exception as e:
        return 500, {"detail": str(e)}

def get_auth_token(username, password):
    url = f"{API_URL}/auth/login"
    body = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data["access_token"]
    except Exception as e:
        print(f"Failed to login {username}: {e}")
        return None

def run_tests():
    print("=" * 75)
    print("NAGRIKSETU PHASE 7 ACCEPTANCE VERIFICATION SUITE")
    print("Parent-Student Verification, Multi-Child, Multi-Guardian & School Routing")
    print("=" * 75)

    # 1. Baseline Integrity & Test Cleanup
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    students_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    enrollments_count = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]

    # Clean up test parent linking requests
    cur.execute("DELETE FROM linking_requests WHERE parent_user_id IN (SELECT user_id FROM users WHERE email IN ('raghu.test.stage1@example.com', 'sunitha.mother@example.com'))")
    # Clean up test student_guardians for test parents
    cur.execute("DELETE FROM student_guardians WHERE guardian_id IN (SELECT guardian_id FROM guardians WHERE user_id IN (SELECT user_id FROM users WHERE email IN ('raghu.test.stage1@example.com', 'sunitha.mother@example.com')))")
    conn.commit()

    print(f"[*] Baseline DB Check: {students_count} students, {enrollments_count} enrollments.")
    assert students_count >= 30000 and enrollments_count >= 30000
    print("    -> Baseline Database Integrity PASSED.")

    # 2. Authentications
    staff_hash = cur.execute("SELECT password_hash FROM users WHERE email = 'staff.sch001@example.com'").fetchone()[0]

    p2_uid = "user-parent-mother-sunitha"
    cur.execute("""
        INSERT OR REPLACE INTO users (user_id, email, phone, password_hash, role, school_id, is_active, full_name)
        VALUES (?, 'sunitha.mother@example.com', '9845011223', ?, 'parent', NULL, 1, 'Sunitha Ramesh (Mother)')
    """, (p2_uid, staff_hash))

    s_sch011_uid = "staff-sch011-audit-uid"
    cur.execute("""
        INSERT OR REPLACE INTO users (user_id, email, phone, password_hash, role, school_id, is_active, full_name)
        VALUES (?, 'staff.sch011@example.com', '9845099887', ?, 'school_staff', 'SCH011', 1, 'Admissions Officer SCH011')
    """, (s_sch011_uid, staff_hash))
    conn.commit()
    conn.close()

    staff_001_token = get_auth_token("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    staff_011_token = get_auth_token("staff.sch011@example.com", "Staff@NagrikSetu2026!")
    parent_1_token = get_auth_token("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")
    parent_2_token = get_auth_token("sunitha.mother@example.com", "Staff@NagrikSetu2026!")

    assert staff_001_token and staff_011_token and parent_1_token and parent_2_token, "Auth tokens acquisition failed!"
    print("[*] Multi-tenant Authentication Successful (2 Parents, 2 Distinct School Staff).")

    # 3. Pick two existing students from SCH001 and SCH011 for testing linking
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    stud_sch001 = cur.execute("SELECT student_id, permanent_student_id, student_name, school_id FROM students WHERE school_id = 'SCH001' AND standard = 2 LIMIT 1").fetchone()
    stud_sch011 = cur.execute("SELECT student_id, permanent_student_id, student_name, school_id FROM students WHERE school_id = 'SCH011' AND standard = 3 LIMIT 1").fetchone()
    conn.close()

    print(f"[*] Test Students Selected:")
    print(f"    - Child 1: {stud_sch001[2]} (PID: {stud_sch001[1]}, School: {stud_sch001[3]})")
    print(f"    - Child 2: {stud_sch011[2]} (PID: {stud_sch011[1]}, School: {stud_sch011[3]})")

    # 4. Multi-Child: Parent 1 submits linking requests for Child 1 (SCH001) and Child 2 (SCH011)
    status, req1 = api_call("/parent/linking-requests", "POST", {
        "school_id": "SCH001",
        "student_ref": stud_sch001[2],
        "relationship_type": "Father",
        "verification_doc_id": "AADHAAR-FATHER-001",
        "additional_notes": "Linking my child studying in Std 2 Section A"
    }, parent_1_token)
    assert status == 201, f"Failed linking request 1: {req1}"
    req1_id = req1["request_id"]
    print(f"    -> Parent 1 submitted linking request for Child 1 ({stud_sch001[3]}): {req1_id}")

    status, req2 = api_call("/parent/linking-requests", "POST", {
        "school_id": "SCH011",
        "student_ref": stud_sch011[2],
        "relationship_type": "Father",
        "verification_doc_id": "AADHAAR-FATHER-002",
        "additional_notes": "Linking second child studying in Tumakuru school"
    }, parent_1_token)
    assert status == 201, f"Failed linking request 2: {req2}"
    req2_id = req2["request_id"]
    print(f"    -> Parent 1 submitted linking request for Child 2 ({stud_sch011[3]}): {req2_id}")

    # 5. Verification Request Routing & Cross-School Multi-Tenant Isolation
    # Staff SCH001 lists requests: should see req1, must NOT see req2
    status, sch001_reqs = api_call("/school/linking-requests", "GET", None, staff_001_token)
    assert status == 200
    sch001_ids = [r["request_id"] for r in (sch001_reqs if isinstance(sch001_reqs, list) else sch001_reqs.get("requests", []))]
    assert req1_id in sch001_ids, "SCH001 staff cannot see its own school's request!"
    assert req2_id not in sch001_ids, "Data leak! SCH001 staff can see request for SCH011!"
    print("    -> Multi-tenant boundary verified: Staff SCH001 sees only SCH001 requests PASSED.")

    # Staff SCH001 attempts to review / approve req2 (SCH011): MUST BE FORBIDDEN (HTTP 403)
    status, res = api_call(f"/school/linking-requests/{req2_id}/review", "POST", {
        "decision": "approved",
        "permanent_student_id": stud_sch011[1],
        "confirm_student_match": True,
        "review_comment": "Attempted illegal cross-school approval"
    }, staff_001_token)
    assert status == 403, f"Cross-school review should return 403 Forbidden, got: {status}"
    print(f"    -> Cross-school unauthorized approval blocked (HTTP 403: {res['detail']}) PASSED.")

    # Staff SCH001 approves req1 (Child 1)
    status, res = api_call(f"/school/linking-requests/{req1_id}/review", "POST", {
        "decision": "approved",
        "permanent_student_id": stud_sch001[1],
        "confirm_student_match": True,
        "review_comment": "Verified parent Aadhaar and family ration card."
    }, staff_001_token)
    assert status == 200, f"Approval of req1 failed: {res}"
    print("    -> Staff SCH001 approved linking request for Child 1.")

    # Staff SCH011 approves req2 (Child 2)
    status, res = api_call(f"/school/linking-requests/{req2_id}/review", "POST", {
        "decision": "approved",
        "permanent_student_id": stud_sch011[1],
        "confirm_student_match": True,
        "review_comment": "Verified Tumakuru municipal school records."
    }, staff_011_token)
    assert status == 200, f"Approval of req2 failed: {res}"
    print("    -> Staff SCH011 approved linking request for Child 2.")

    # 6. Multi-Child Verification in Parent 1 Portal
    status, p1_children = api_call("/parent/children", "GET", None, parent_1_token)
    assert status == 200
    child_pids = [c["permanent_student_id"] for c in p1_children]
    print(f"[*] Parent 1 Linked Children Count: {len(p1_children)}")
    assert stud_sch001[1] in child_pids, "Child 1 (SCH001) not listed for Parent 1!"
    assert stud_sch011[1] in child_pids, "Child 2 (SCH011) not listed for Parent 1!"
    print("    -> Multi-child across distinct institutions (SCH001 & SCH011) verified PASSED.")

    # 7. Multi-Guardian Verification: Parent 2 (Mother) links to Child 1 as well
    status, req_mother = api_call("/parent/linking-requests", "POST", {
        "school_id": "SCH001",
        "student_ref": stud_sch001[1],
        "relationship_type": "Mother",
        "verification_doc_id": "MOTH-DOC-1122",
        "additional_notes": "Mother account linking to existing student"
    }, parent_2_token)
    assert status == 201
    req_mother_id = req_mother["request_id"]

    # Staff SCH001 approves Mother linking request
    status, res = api_call(f"/school/linking-requests/{req_mother_id}/review", "POST", {
        "decision": "approved",
        "permanent_student_id": stud_sch001[1],
        "confirm_student_match": True,
        "review_comment": "Mother relationship verified."
    }, staff_001_token)
    assert status == 200

    # Verify Child 1 is listed for BOTH Parent 1 (Father) and Parent 2 (Mother)
    status, p2_children = api_call("/parent/children", "GET", None, parent_2_token)
    assert status == 200
    assert any(c["permanent_student_id"] == stud_sch001[1] for c in p2_children)
    print("    -> Multi-guardian (Mother & Father both linked to same student) verified PASSED.")

    # 8. Student Records Privacy Gate
    # Parent 2 (Mother) CAN view Child 1 records
    status, rec1 = api_call(f"/parent/children/{stud_sch001[1]}/records", "GET", None, parent_2_token)
    assert status == 200
    print(f"    -> Authorized Parent 2 accessed Child 1 records: {len(rec1.get('academic_results', []))} evaluations found.")

    # Parent 2 (Mother) CANNOT view Child 2 records (only Father is linked to Child 2)
    status, rec2 = api_call(f"/parent/children/{stud_sch011[1]}/records", "GET", None, parent_2_token)
    assert status in (403, 404), f"Expected 403/404 on unlinked child record access, got: {status}"
    print(f"    -> Unauthorized child record access blocked (HTTP {status}: {rec2.get('detail')}) PASSED.")

    # 9. Final Database Verification
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    final_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    final_enrollments = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    conn.close()

    assert final_students == students_count, "Student records modified during parent verification!"
    assert final_enrollments == enrollments_count, "Enrollment records modified during parent verification!"
    print(f"[*] Final Database Counts Check: {final_students} students, {final_enrollments} enrollments strictly preserved.")

    print("=" * 75)
    print("ALL 9 PHASE 7 ACCEPTANCE CRITERIA VERIFIED AND PASSED!")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
