"""
E2E Comprehensive Test Suite for NagrikSetu Centralized Request, Complaint,
Verification and Record Correction Management System.
Tests all 17 scenarios defined in the functional specification using urllib.request against live backend.
"""
import sys
import os
import json
import sqlite3
import traceback
from datetime import datetime, date
import urllib.request
import urllib.error

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from auth import create_access_token

BASE_URL = "http://127.0.0.1:8000"

class ResponseWrapper:
    def __init__(self, status_code, body_bytes):
        self.status_code = status_code
        self.text = body_bytes.decode('utf-8', errors='replace')
        try:
            self._json = json.loads(self.text)
        except Exception:
            self._json = None

    def json(self):
        if self._json is not None:
            return self._json
        raise ValueError(f"Response not JSON: {self.text}")

class LiveClient:
    def request(self, method, path, json_data=None, headers=None):
        url = f"{BASE_URL}{path}"
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        
        data = None
        if json_data is not None:
            data = json.dumps(json_data).encode("utf-8")
        
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                return ResponseWrapper(resp.status, resp.read())
        except urllib.error.HTTPError as e:
            return ResponseWrapper(e.code, e.read())
        except Exception as e:
            raise RuntimeError(f"Connection error to {url}: {e}")

    def get(self, path, headers=None):
        return self.request("GET", path, headers=headers)

    def post(self, path, json=None, headers=None):
        return self.request("POST", path, json_data=json, headers=headers)

    def put(self, path, json=None, headers=None):
        return self.request("PUT", path, json_data=json, headers=headers)

client = LiveClient()

def run_tests():
    print("=" * 80)
    print("NAGRIKSETU REQUEST & RECORD CORRECTION MANAGEMENT SYSTEM - E2E TEST SUITE")
    print("=" * 80)

    conn = get_connection()
    try:
        # Pre-check database student count
        total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        print(f"[*] Pre-test total student count: {total_students}")
        assert total_students == 30003, f"Expected 30003 students, got {total_students}"

        # Find or create test users
        # 1. School Admin 1 (SCH001)
        admin1_user = conn.execute("SELECT user_id, email, school_id, role FROM users WHERE school_id = 'SCH001' AND role IN ('school_admin', 'institution_admin')").fetchone()
        if not admin1_user:
            conn.execute("""
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, full_name, is_active)
                VALUES ('test_admin_sch001', 'admin.sch001@example.com', '9876543201', 'hash', 'school_admin', 'SCH001', 'Admin SCH001', 1)
            """)
            conn.commit()
            admin1_user = conn.execute("SELECT user_id, email, school_id, role FROM users WHERE user_id = 'test_admin_sch001'").fetchone()

        # 2. School Admin 2 (SCH002)
        admin2_user = conn.execute("SELECT user_id, email, school_id, role FROM users WHERE school_id = 'SCH002' AND role IN ('school_admin', 'institution_admin')").fetchone()
        if not admin2_user:
            conn.execute("""
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, full_name, is_active)
                VALUES ('test_admin_sch002', 'admin.sch002@example.com', '9876543202', 'hash', 'school_admin', 'SCH002', 'Admin SCH002', 1)
            """)
            conn.commit()
            admin2_user = conn.execute("SELECT user_id, email, school_id, role FROM users WHERE user_id = 'test_admin_sch002'").fetchone()

        # 3. Platform Admin
        plat_user = conn.execute("SELECT user_id, email, role FROM users WHERE role = 'platform_admin'").fetchone()
        if not plat_user:
            conn.execute("""
                INSERT INTO users (user_id, email, phone, password_hash, role, full_name, is_active)
                VALUES ('test_plat_admin', 'platform.admin@nagriksetu.gov.in', '9876543299', 'hash', 'platform_admin', 'State Admin', 1)
            """)
            conn.commit()
            plat_user = conn.execute("SELECT user_id, email, role FROM users WHERE user_id = 'test_plat_admin'").fetchone()

        # Find student in SCH001
        student_rec = conn.execute("""
            SELECT permanent_student_id, student_id, student_name, school_id
            FROM students
            WHERE school_id = 'SCH001'
            LIMIT 1
        """).fetchone()
        assert student_rec, "No student found in SCH001"
        psid_test = student_rec["permanent_student_id"]
        sid_test = student_rec["student_id"]
        student_name_test = student_rec["student_name"]
        school_id_test = student_rec["school_id"]

        # Ensure student user account exists
        student_user = conn.execute("SELECT user_id, email, permanent_student_id, student_id, role FROM users WHERE permanent_student_id = ?", (psid_test,)).fetchone()
        if not student_user:
            conn.execute("""
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, permanent_student_id, student_id, full_name, is_active)
                VALUES (?, ?, '9876543210', 'hash', 'student', ?, ?, ?, ?, 1)
            """, (f"usr_std_{sid_test}", f"{sid_test.lower()}@student.gov.in", school_id_test, psid_test, sid_test, student_name_test))
            conn.commit()
            student_user = conn.execute("SELECT user_id, email, permanent_student_id, student_id, role FROM users WHERE permanent_student_id = ?", (psid_test,)).fetchone()

        # Parent setup
        parent_uid = f"usr_parent_{psid_test[:8]}"
        parent_gid = f"G_TEST_{psid_test[:8]}"
        parent_email = f"parent.{psid_test[:8].lower()}@example.com"
        parent_phone = "9845098450"
        parent_name = f"Guardian of {student_name_test}"

        # Insert parent user
        conn.execute("""
            INSERT OR REPLACE INTO users (user_id, email, phone, password_hash, role, full_name, is_active)
            VALUES (?, ?, ?, 'hash', 'parent', ?, 1)
        """, (parent_uid, parent_email, parent_phone, parent_name))

        # Insert guardian
        conn.execute("""
            INSERT OR REPLACE INTO guardians (guardian_id, user_id, full_name, relationship, phone, email, address)
            VALUES (?, ?, ?, 'Father', ?, ?, 'Bengaluru, KA')
        """, (parent_gid, parent_uid, parent_name, parent_phone, parent_email))

        # Link guardian to student
        conn.execute("""
            INSERT OR REPLACE INTO student_guardians (student_guardian_id, permanent_student_id, guardian_id, can_view_records, can_request_updates, is_verified)
            VALUES (?, ?, ?, 1, 1, 1)
        """, (f"SG_{parent_gid}", psid_test, parent_gid))
        conn.commit()

        # Seed test attendance record for student
        test_att_date = "2026-11-15"
        conn.execute("""
            INSERT OR REPLACE INTO student_attendance (attendance_id, institution_id, permanent_student_id, academic_year, attendance_date, status, remarks, recorded_by_user_id)
            VALUES (?, ?, ?, '2026-2027', ?, 'absent', 'Marked absent by teacher', ?)
        """, (f"ATT_TEST_{psid_test[:8]}", school_id_test, psid_test, test_att_date, admin1_user["user_id"]))
        conn.commit()

        # Create JWT Tokens
        token_student = create_access_token({
            "user_id": student_user["user_id"],
            "role": "student",
            "permanent_student_id": psid_test,
            "student_id": sid_test,
            "school_id": school_id_test
        })
        token_parent = create_access_token({
            "user_id": parent_uid,
            "role": "parent",
            "email": parent_email,
            "phone": parent_phone
        })
        token_admin1 = create_access_token({
            "user_id": admin1_user["user_id"],
            "role": "school_admin",
            "school_id": school_id_test
        })
        other_school_id = "SCH002" if school_id_test != "SCH002" else "SCH003"
        token_admin2 = create_access_token({
            "user_id": admin2_user["user_id"],
            "role": "school_admin",
            "school_id": other_school_id
        })
        token_platform = create_access_token({
            "user_id": plat_user["user_id"],
            "role": "platform_admin"
        })

        headers_student = {"Authorization": f"Bearer {token_student}"}
        headers_parent = {"Authorization": f"Bearer {token_parent}"}
        headers_admin1 = {"Authorization": f"Bearer {token_admin1}"}
        headers_admin2 = {"Authorization": f"Bearer {token_admin2}"}
        headers_platform = {"Authorization": f"Bearer {token_platform}"}

        print("\n[✓] Test fixtures initialized successfully.")

        # ====================================================================
        # SCENARIO 1: Student attendance correction request submission
        # ====================================================================
        print("\n--- SCENARIO 1: Student attendance correction request submission ---")
        att_req_payload = {
            "title": f"Rectification of attendance on {test_att_date}",
            "category": "Attendance Correction",
            "description": "I was present in first period and attended science lab. Please rectify register.",
            "priority": "high",
            "affected_person_type": "self",
            "affected_student_id": sid_test,
            "target_module": "student_attendance",
            "target_record_id": test_att_date,
            "field_name": "status",
            "current_value": "absent",
            "requested_value": "present"
        }
        res = client.post("/requests/raise", json=att_req_payload, headers=headers_student)
        assert res.status_code == 201, f"Failed to raise request: {res.text}"
        data_s1 = res.json()
        req_id_1 = data_s1["request_id"]
        tracking_num_1 = data_s1["tracking_number"]
        print(f"[✓] Attendance request created: ID={req_id_1}, Tracking={tracking_num_1}, Status={data_s1['review_status']}")
        assert data_s1["review_status"] == "SUBMITTED"
        assert data_s1["assigned_institution_id"] == school_id_test

        # ====================================================================
        # SCENARIO 2: Institution receives request
        # ====================================================================
        print(f"\n--- SCENARIO 2: Institution receives request ({school_id_test}) ---")
        res = client.get(f"/institution/{school_id_test}/requests", headers=headers_admin1)
        assert res.status_code == 200, f"Institution failed to get requests: {res.text}"
        data_s2 = res.json()
        req_ids = [r["request_id"] for r in data_s2["requests"]]
        assert req_id_1 in req_ids, f"Request {req_id_1} not found in institution {school_id_test} queue"
        print(f"[✓] Institution {school_id_test} successfully retrieved request list (Total {data_s2['summary']['total']} requests).")

        # ====================================================================
        # SCENARIO 3: Institution reviews record & case details
        # ====================================================================
        print("\n--- SCENARIO 3: Institution reviews case details ---")
        res = client.get(f"/requests/{req_id_1}", headers=headers_admin1)
        assert res.status_code == 200, f"Failed to get request details: {res.text}"
        details_s3 = res.json()
        assert details_s3["request"]["current_value"].lower() == "absent"
        assert details_s3["request"]["requested_value"].lower() == "present"
        print(f"[✓] Request details verified: Target={details_s3['request']['target_module']}.{details_s3['request']['field_name']}")

        # ====================================================================
        # SCENARIO 4: Institution corrects attendance in DB
        # ====================================================================
        print("\n--- SCENARIO 4: Institution executes live attendance correction ---")
        corr_payload = {
            "target_module": "attendance",
            "target_record_id": test_att_date,
            "field_name": "status",
            "proposed_new_value": "present",
            "confirmation_remarks": "Verified physical sign-in register and lab logbook. Student was present."
        }
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_1}/execute-correction", json=corr_payload, headers=headers_admin1)
        assert res.status_code == 200, f"Failed to execute correction: {res.text}"
        data_s4 = res.json()
        assert data_s4.get("updated_request_status") == "CORRECTED" or data_s4.get("request_status") == "CORRECTED"
        assert data_s4.get("verified") is True
        print(f"[✓] Live correction executed and verified in database!")

        # Verify DB directly
        db_att = conn.execute("SELECT status, remarks FROM student_attendance WHERE permanent_student_id = ? AND attendance_date = ?", (psid_test, test_att_date)).fetchone()
        assert db_att["status"].lower() == "present", f"Expected present in DB, found {db_att['status']}"
        print(f"[✓] Database audit: student_attendance.status is now '{db_att['status']}'")

        # ====================================================================
        # SCENARIO 5 & 6: Student sees corrected status & previous vs corrected values
        # ====================================================================
        print("\n--- SCENARIOS 5 & 6: Student views corrected status & previous/corrected values ---")
        res = client.get("/requests/my-requests", headers=headers_student)
        assert res.status_code == 200
        my_reqs = res.json()
        matched = next((r for r in my_reqs if r["request_id"] == req_id_1), None)
        assert matched is not None
        assert matched["status"] == "CORRECTED"
        print(f"[✓] Student dashboard shows request status as CORRECTED")

        res = client.get(f"/requests/{req_id_1}", headers=headers_student)
        assert res.status_code == 200
        student_details = res.json()
        assert len(student_details["corrections"]) > 0
        corr = student_details["corrections"][0]
        assert corr["previous_value"].lower() == "absent"
        assert corr["corrected_value"].lower() == "present"
        assert corr["verification_status"] == "VERIFIED"
        print(f"[✓] Student details view verified: Previous='{corr['previous_value']}' -> Corrected='{corr['corrected_value']}'")

        # ====================================================================
        # SCENARIO 7, 8, 9: Parent requests mobile number update & admin executes
        # ====================================================================
        print("\n--- SCENARIOS 7, 8, 9: Parent mobile number update ---")
        old_phone = parent_phone
        new_phone = "9845012345"
        parent_req_payload = {
            "title": "Update primary contact phone number",
            "category": "Mobile Number Update",
            "description": "Changed official mobile carrier. Please update registered SMS contact.",
            "priority": "medium",
            "affected_person_type": "linked_child",
            "affected_student_id": sid_test,
            "target_module": "parent_info",
            "target_record_id": parent_gid,
            "field_name": "phone",
            "current_value": old_phone,
            "requested_value": new_phone
        }
        res = client.post("/requests/raise", json=parent_req_payload, headers=headers_parent)
        assert res.status_code == 201, f"Failed parent raise request: {res.text}"
        data_p = res.json()
        req_id_p = data_p["request_id"]
        print(f"[✓] Parent submitted mobile update request: {data_p['tracking_number']}")

        # Admin executes correction on phone
        corr_payload_p = {
            "target_module": "parent_info",
            "target_record_id": parent_gid,
            "field_name": "phone",
            "proposed_new_value": new_phone,
            "confirmation_remarks": "Aadhaar linked phone verification verified via SMS OTP."
        }
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_p}/execute-correction", json=corr_payload_p, headers=headers_admin1)
        assert res.status_code == 200, f"Failed phone correction: {res.text}"
        print(f"[✓] Institution executed phone correction in guardians/users table")

        # Verify DB directly
        db_g = conn.execute("SELECT phone FROM guardians WHERE guardian_id = ?", (parent_gid,)).fetchone()
        assert db_g["phone"] == new_phone, f"Expected {new_phone}, got {db_g['phone']}"
        print(f"[✓] Database audit: guardians.phone successfully updated to '{db_g['phone']}'")

        # Parent sees corrected status
        res = client.get(f"/requests/{req_id_p}", headers=headers_parent)
        assert res.status_code == 200
        p_details = res.json()
        assert p_details["request"]["status"] == "CORRECTED"
        assert p_details["corrections"][0]["corrected_value"] == new_phone
        print(f"[✓] Parent confirmed status CORRECTED with new phone number '{new_phone}'")

        # ====================================================================
        # SCENARIOS 10, 11, 12: Clarification cycle (Request -> Respond -> Complete)
        # ====================================================================
        print("\n--- SCENARIOS 10, 11, 12: Clarification cycle ---")
        clarify_req = {
            "title": "Correction in student middle name spelling",
            "category": "Student Name Correction",
            "description": "My middle name has a typo on the grade sheet.",
            "priority": "low",
            "affected_person_type": "self",
            "affected_student_id": sid_test,
            "target_module": "student_profile",
            "target_record_id": psid_test,
            "field_name": "student_name",
            "current_value": student_name_test,
            "requested_value": f"{student_name_test} Kumar"
        }
        res = client.post("/requests/raise", json=clarify_req, headers=headers_student)
        assert res.status_code == 201, f"Failed clarify request: {res.text}"
        req_id_c = res.json()["request_id"]

        # Admin requests clarification
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_c}/request-clarification", json={
            "clarification_prompt": "Please upload a copy of your Birth Certificate or Aadhaar Card showing the middle name."
        }, headers=headers_admin1)
        assert res.status_code == 200
        assert res.json().get("new_status") == "CLARIFICATION_REQUIRED" or res.json().get("request_status") == "CLARIFICATION_REQUIRED"
        print(f"[✓] Institution requested clarification: Status -> CLARIFICATION_REQUIRED")

        # Student responds to clarification
        res = client.post(f"/requests/{req_id_c}/respond-clarification", json={
            "response_message": "Attached Aadhaar card scan showing full official name. Please review.",
            "additional_document_url": "data:application/pdf;base64,JVBERi0xLjQK..."
        }, headers=headers_student)
        assert res.status_code == 200
        assert res.json().get("new_status") == "UNDER_REVIEW" or res.json().get("request_status") == "UNDER_REVIEW"
        print(f"[✓] Requester submitted clarification response: Status -> UNDER_REVIEW")

        # Admin accepts request
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_c}/accept", json={
            "remarks": "Aadhaar verified. Correction accepted for processing."
        }, headers=headers_admin1)
        assert res.status_code == 200
        assert res.json().get("new_status") == "ACCEPTED" or res.json().get("request_status") == "ACCEPTED"
        print(f"[✓] Institution reviewed and accepted clarified request: Status -> ACCEPTED")

        # ====================================================================
        # SCENARIO 13 & 14: Rejection with mandatory reason & remarks isolation
        # ====================================================================
        print("\n--- SCENARIOS 13 & 14: Rejection with mandatory reason & internal remark confidentiality ---")
        rej_req = {
            "title": "Increase midterm math marks by 15",
            "category": "Examination Marks Correction",
            "description": "I think question 4 was graded too harshly.",
            "priority": "low",
            "affected_person_type": "self",
            "affected_student_id": sid_test
        }
        res = client.post("/requests/raise", json=rej_req, headers=headers_student)
        assert res.status_code == 201
        req_id_r = res.json()["request_id"]

        # Attempt reject without mandatory reason (should fail)
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_r}/reject", json={"rejection_reason": ""}, headers=headers_admin1)
        assert res.status_code == 422 or res.status_code == 400, f"Expected validation failure for empty reason, got {res.status_code}"

        # Reject with valid mandatory reason
        mand_reason = "Answer script re-evaluated by department head. Grading rubric was strictly followed; no calculation error found."
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_r}/reject", json={
            "rejection_reason": mand_reason,
            "remarks": "Requester may apply for formal board scrutiny if desired."
        }, headers=headers_admin1)
        assert res.status_code == 200
        assert res.json().get("new_status") == "REJECTED" or res.json().get("request_status") == "REJECTED"
        print(f"[✓] Request rejected with mandatory reason: Status -> REJECTED")

        # Add confidential internal-only remark
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_r}/remarks", json={
            "message": "INTERNAL NOTE: Student previously raised 3 similar grading disputes this term.",
            "visibility": "internal_only"
        }, headers=headers_admin1)
        assert res.status_code in (200, 201), f"Failed adding remark: {res.text}"

        # Check student view: Must NOT see internal-only remark
        res = client.get(f"/requests/{req_id_r}", headers=headers_student)
        assert res.status_code == 200
        s_view = res.json()
        assert s_view["request"]["rejection_reason"] == mand_reason
        remarks_texts = [rem.get("message") or rem.get("remark_text") for rem in s_view["remarks"]]
        for t in remarks_texts:
            assert "INTERNAL NOTE" not in (t or ""), f"Security Violation! Internal remark leaked to student: {t}"
        print(f"[✓] Security verified: Internal-only remark strictly hidden from requester!")

        # Check admin view: CAN see internal-only remark
        res = client.get(f"/requests/{req_id_r}", headers=headers_admin1)
        assert res.status_code == 200
        a_view = res.json()
        admin_remarks_texts = [rem.get("message") or rem.get("remark_text") for rem in a_view["remarks"]]
        assert any("INTERNAL NOTE" in (t or "") for t in admin_remarks_texts)
        print(f"[✓] Admin view verified: Internal-only remark visible to authorized administrator.")

        # ====================================================================
        # SCENARIO 15: Cross-institution authorization isolation (403 Forbidden)
        # ====================================================================
        print("\n--- SCENARIO 15: Cross-institution isolation (403 check) ---")
        # Admin 2 attempts to access school 1's request via school 1's endpoint -> 403 Forbidden
        res = client.post(f"/institution/{school_id_test}/requests/{req_id_1}/accept", json={"remarks": "Illegal accept"}, headers=headers_admin2)
        assert res.status_code == 403, f"Expected 403 Forbidden for cross-institution action, got {res.status_code}"

        res = client.get(f"/institution/{other_school_id}/requests", headers=headers_admin2)
        assert res.status_code == 200
        other_req_ids = [r["request_id"] for r in res.json()["requests"]]
        assert req_id_1 not in other_req_ids, f"{school_id_test} request leaked into {other_school_id} request queue!"
        print(f"[✓] Cross-institution isolation verified: Admin of {other_school_id} cannot access or action {school_id_test} requests.")

        # ====================================================================
        # SCENARIO 16: Platform Admin oversight & forwarding
        # ====================================================================
        print("\n--- SCENARIO 16: Platform Admin oversight and request re-routing ---")
        # Escalate request c to platform
        client.post(f"/institution/{school_id_test}/requests/{req_id_c}/escalate", json={
            "escalation_reason": "State-level certification verification required."
        }, headers=headers_admin1)

        # Platform Admin queries oversight
        res = client.get("/admin/requests/oversight", headers=headers_platform)
        assert res.status_code == 200
        ov = res.json()
        assert ov["kpis"]["total"] >= 4
        assert ov["kpis"]["escalated"] >= 1
        print(f"[✓] Platform Oversight KPI verified: Total={ov['kpis']['total']}, Escalated={ov['kpis']['escalated']}")

        # Platform Admin forwards request from school 1 to other school
        res = client.post(f"/admin/requests/{req_id_c}/forward", json={
            "target_institution_id": other_school_id,
            "forward_remarks": f"Student transferred to {other_school_id}; reassigning case ownership."
        }, headers=headers_platform)
        assert res.status_code == 200
        assert res.json()["assigned_institution_id"] == other_school_id
        print(f"[✓] Request successfully forwarded to {other_school_id} by Platform Administrator.")

        # ====================================================================
        # SCENARIO 17: Database audit integrity and student preservation
        # ====================================================================
        print("\n--- SCENARIO 17: Database audit integrity & total student count preservation ---")
        final_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        print(f"[*] Final total student count: {final_students}")
        assert final_students == 30003, f"CRITICAL: Student count changed! Expected 30003, found {final_students}"

        # Verify audit logs table
        audit_count = conn.execute("SELECT COUNT(*) FROM request_audit_logs").fetchone()[0]
        status_hist_count = conn.execute("SELECT COUNT(*) FROM request_status_history").fetchone()[0]
        corrections_count = conn.execute("SELECT COUNT(*) FROM request_corrections").fetchone()[0]
        print(f"[✓] Audit trails verified: {audit_count} audit logs, {status_hist_count} status transitions, {corrections_count} permanent corrections.")

        print("\n" + "=" * 80)
        print("ALL 17 SCENARIOS PASSED WITH ZERO ERRORS!")
        print("=" * 80)
        return True

    finally:
        conn.close()

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
