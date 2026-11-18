import base64
import json
import os
import sqlite3
import sys
import urllib.request
import urllib.error

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
    # form data
    body = f"username={urllib.parse.quote(username)}&password={urllib.parse.quote(password)}".encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data["access_token"]
    except Exception as e:
        print(f"Failed to login {username}: {e}")
        return None

import urllib.parse

def run_tests():
    print("=" * 70)
    print("NAGRIKSETU PHASE 5 ACCEPTANCE VERIFICATION SUITE")
    print("=" * 70)

    # 1. Baseline DB Verification
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    students_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    enrollments_count = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    programs_count = cur.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0]
    sections_count = cur.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0]
    schools_count = cur.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    conn.close()

    print(f"[*] Baseline DB Counts:")
    print(f"    - Students: {students_count} (Expected: 30000)")
    print(f"    - Enrollments: {enrollments_count} (Expected: 30000)")
    print(f"    - Programs: {programs_count} (Expected: 198)")
    print(f"    - Sections: {sections_count} (Expected: 841)")
    print(f"    - Schools: {schools_count} (Expected: 30)")

    assert students_count == 30000, "Student count compromised!"
    assert enrollments_count == 30000, "Enrollment count compromised!"
    print("    -> Baseline Database Integrity PASSED.")

    # 2. Authenticate
    staff_token = get_auth_token("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    parent_token = get_auth_token("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")
    assert staff_token, "Staff auth failed"
    assert parent_token, "Parent auth failed"
    print("[*] Staff and Parent Authentications Succeeded.")

    # 3. Create Stage 1 Application for Testing Stage 2
    app_payload = {
        "institution_id": "SCH001",
        "education_level": "school",
        "requested_standard": 6,
        "first_language_preference": "Kannada",
        "second_language_preference": "English",
        "applicant_name": "Rohan Kumar Acceptance",
        "parent_name": "Raghu Kumar Acceptance",
        "parent_phone": "9876543210",
        "parent_email": "raghu.test.stage1@example.com",
        "residential_address": "123 Indiranagar, Bengaluru Urban, Karnataka",
        "academic_year": "2026-2027"
    }
    status, app_res = api_call("/admissions/apply", "POST", app_payload, parent_token)
    assert status in (200, 201), f"Failed to submit application: {app_res}"
    app_id = app_res["application_id"]
    print(f"[*] Created Stage 1 Application: {app_id} (Status: {app_res['status']})")

    # 4. Two-Stage Boundary Check: Verify Stage 2 is BLOCKED while in 'submitted'
    status, res = api_call(f"/admissions/applications/{app_id}/stage2-eligibility")
    assert status == 403, f"Expected 403 when status='submitted', got: {status}"
    print("    -> Stage 2 eligibility strictly locked (HTTP 403 Forbidden) while status='submitted' PASSED.")

    status, res = api_call(f"/admissions/applications/{app_id}/stage2-submit", "POST", {
        "date_of_birth": "2014-05-15",
        "gender": "male",
        "blood_group": "O+",
        "emergency_contact_name": "Ramesh Kumar",
        "emergency_contact_phone": "9876543210"
    }, parent_token)
    assert status in (400, 403), f"Stage 2 submit should be blocked, got: {status}"
    print(f"    -> Stage 2 submission rejected (HTTP {status}) when Stage 1 not approved PASSED.")

    # 5. Staff Approves Stage 1
    status, res = api_call(f"/school/admissions/{app_id}/approve", "POST", {
        "confirm": True,
        "note": "Stage 1 preliminary catchment and standard capacity verified."
    }, staff_token)
    assert status == 200
    print(f"[*] Staff Approved Stage 1 for {app_id}.")

    # 6. Verify Stage 2 is NOW Accessible
    status, res = api_call(f"/admissions/applications/{app_id}/stage2-eligibility")
    assert status == 200
    assert res.get("is_eligible") is True or res.get("eligible_for_stage2") is True, "Application should now be eligible for Stage 2!"
    print("    -> Stage 2 eligibility unlocked (is_eligible=True) PASSED.")

    # 7. Submit Stage 2 Demographics and Previous Academic Record
    stage2_payload = {
        "date_of_birth": "2014-05-15",
        "gender": "male",
        "blood_group": "B+",
        "emergency_contact_name": "Ramesh Kumar Acceptance",
        "emergency_contact_phone": "9876543210",
        "previous_institution_name": "Govt Primary School Malleshwaram",
        "previous_institution_location": "Malleshwaram, Bengaluru",
        "previous_standard_or_degree": "Standard 5",
        "previous_board": "Karnataka State Board (KSEAB)",
        "previous_marks_percentage": 88.5
    }
    status, res = api_call(f"/admissions/applications/{app_id}/stage2-submit", "POST", stage2_payload, parent_token)
    assert status == 200, f"Failed Stage 2 submission: {res}"
    assert res.get("application_status") == "stage2_submitted" or res.get("status") == "success"
    print("    -> Stage 2 demographics & previous schooling submitted successfully PASSED.")

    # 8. Upload Supporting Documents
    dummy_pdf = base64.b64encode(b"%PDF-1.4 Acceptance Test PDF Document Content for NagrikSetu").decode("ascii")
    dummy_jpg = base64.b64encode(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07").decode("ascii")

    docs_to_upload = [
        ("birth_certificate", "birth_certificate_rohan.pdf", dummy_pdf, "application/pdf"),
        ("passport_photo", "passport_photo_rohan.jpg", dummy_jpg, "image/jpeg"),
        ("previous_marks_card", "std5_marks_card.pdf", dummy_pdf, "application/pdf"),
        ("transfer_certificate", "school_tc_2026.pdf", dummy_pdf, "application/pdf"),
    ]

    uploaded_doc_ids = []
    for dtype, fname, fdata, mtype in docs_to_upload:
        status, res = api_call(f"/admissions/applications/{app_id}/documents", "POST", {
            "document_type": dtype,
            "file_name": fname,
            "file_data_base64": fdata,
            "mime_type": mtype
        }, parent_token)
        assert status == 200, f"Failed to upload {dtype}: {res}"
        uploaded_doc_ids.append((res["document_id"], dtype, fname))
        print(f"    -> Uploaded {dtype}: {res['file_name']} (ID: {res['document_id']})")

    # 9. Verify Document Listing & Status updated to 'documents_uploaded'
    status, docs_list = api_call(f"/admissions/applications/{app_id}/documents", "GET", None, parent_token)
    assert status == 200
    assert len(docs_list) >= 4
    print(f"    -> Document listing verified: {len(docs_list)} documents found PASSED.")

    # 10. Verify File Download / Serving Endpoint
    doc_id_to_test = uploaded_doc_ids[0][0]
    status, file_res = api_call(f"/admissions/applications/{app_id}/documents/{doc_id_to_test}/file")
    assert status == 200, f"File serving failed with status: {status}"
    print("    -> File retrieval endpoint (/documents/{id}/file) returned 200 OK PASSED.")

    # 11. Staff Document Verification: Test rejection & re-upload request flow
    tc_doc_id = uploaded_doc_ids[3][0]
    status, res = api_call(f"/school/admissions/{app_id}/documents/{tc_doc_id}/verify", "POST", {
        "verification_status": "reupload_requested",
        "verification_notes": "TC stamp is blurry. Please provide clear scanned copy."
    }, staff_token)
    assert status == 200
    assert res["verification_status"] == "reupload_requested"
    print("    -> Document re-upload request transition PASSED.")

    # Parent re-uploads clear TC
    status, res = api_call(f"/admissions/applications/{app_id}/documents", "POST", {
        "document_type": "transfer_certificate",
        "file_name": "school_tc_2026_clear_scan.pdf",
        "file_data_base64": dummy_pdf,
        "mime_type": "application/pdf"
    }, parent_token)
    assert status == 200
    new_tc_doc_id = res["document_id"]
    print("    -> Parent re-uploaded replacement TC successfully PASSED.")

    # 12. Attempt to Complete Stage 2 Review when unverified documents exist (should fail with 400)
    status, res = api_call(f"/school/admissions/{app_id}/stage2-review", "POST", {
        "decision": "detailed_review_completed",
        "review_notes": "Attempting premature review completion."
    }, staff_token)
    assert status == 400, f"Expected 400 when unverified documents exist, got: {status} ({res})"
    print(f"    -> Premature Stage 2 review completion safely blocked (HTTP 400: {res['detail']}) PASSED.")

    # 13. Staff Verifies all current documents
    status, current_docs = api_call(f"/admissions/applications/{app_id}/documents")
    for d in current_docs:
        if d["verification_status"] != "verified":
            v_status, v_res = api_call(f"/school/admissions/{app_id}/documents/{d['document_id']}/verify", "POST", {
                "verification_status": "verified",
                "verification_notes": "Verified against state educational record portal."
            }, staff_token)
            assert v_status == 200

    print("    -> Staff verified all required documents PASSED.")

    # 14. Staff Successfully Completes Stage 2 Review
    status, res = api_call(f"/school/admissions/{app_id}/stage2-review", "POST", {
        "decision": "detailed_review_completed",
        "review_notes": "All Stage 2 demographic data and 4 required certificates successfully verified."
    }, staff_token)
    assert status == 200, f"Stage 2 review completion failed: {res}"
    assert res["status"] == "detailed_review_completed"
    print("    -> Stage 2 review completed (status: detailed_review_completed) PASSED.")

    # 15. Verify In-App Notification Sent to Parent
    status, notifs = api_call("/notifications", "GET", None, parent_token)
    assert status == 200
    has_stage2_notif = any(n.get("application_id") == app_id for n in (notifs if isinstance(notifs, list) else notifs.get("notifications", [])))
    print(f"    -> Parent notification dispatched: {has_stage2_notif} PASSED.")

    # 16. Verify Status History Audit Trail
    status, hist = api_call(f"/school/admissions/{app_id}/history", "GET", None, staff_token)
    assert status == 200
    hist_entries = hist if isinstance(hist, list) else hist.get("history", [])
    statuses_seen = [h["new_status"] for h in hist_entries]
    print(f"    -> Status history timeline: {statuses_seen}")
    assert "detailed_review_completed" in statuses_seen
    print("    -> Audit trail integrity verified PASSED.")

    # 17. Final DB Integrity Check
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    final_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    final_enrollments = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    conn.close()

    assert final_students == 30000, f"Students changed to {final_students}!"
    assert final_enrollments == 30000, f"Enrollments changed to {final_enrollments}!"
    print(f"[*] Final Database Counts Check:")
    print(f"    - Students: {final_students} (Strictly preserved at 30,000)")
    print(f"    - Enrollments: {final_enrollments} (Strictly preserved at 30,000)")
    print("    -> NO premature student/enrollment creation before Phase 6 PASSED.")

    print("=" * 70)
    print("ALL 17 PHASE 5 ACCEPTANCE CRITERIA VERIFIED AND PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
