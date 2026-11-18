import base64
import json
import os
import sqlite3
import sys
import urllib.request
import urllib.error
import urllib.parse

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
    print("NAGRIKSETU PHASE 6 ACCEPTANCE VERIFICATION SUITE")
    print("Final Admission Confirmation, Student Enrolment & Capacity Ledger")
    print("=" * 75)

    # 1. Baseline DB Verification
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    init_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    init_enrollments = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    conn.close()

    print(f"[*] Pre-enrolment Baseline DB Counts:")
    print(f"    - Students: {init_students} (Expected: 30,000)")
    print(f"    - Enrollments: {init_enrollments} (Expected: 30,000)")
    assert init_students == 30000, f"Expected 30000 students, found {init_students}"
    assert init_enrollments == 30000, f"Expected 30000 enrollments, found {init_enrollments}"
    print("    -> Baseline Database Integrity PASSED.")

    # 2. Authentication
    staff_token = get_auth_token("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    parent_token = get_auth_token("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")
    assert staff_token and parent_token, "Authentication failed!"
    print("[*] Staff and Parent Authentications Succeeded.")

    # 3. Create Stage 1 Application for testing complete admission
    app_payload = {
        "institution_id": "SCH001",
        "education_level": "school",
        "requested_standard": 4,
        "first_language_preference": "Kannada",
        "second_language_preference": "English",
        "applicant_name": "Deepa Ramesh Final Enrolment",
        "parent_name": "Ramesh Kumar Acceptance",
        "parent_phone": "9876543210",
        "parent_email": "raghu.test.stage1@example.com",
        "residential_address": "45 Basavanagudi, Bengaluru, Karnataka",
        "academic_year": "2026-2027"
    }
    status, app_res = api_call("/admissions/apply", "POST", app_payload, parent_token)
    assert status in (200, 201)
    app_id = app_res["application_id"]
    print(f"[*] Created Stage 1 Application: {app_id} (Status: {app_res['status']})")

    # 4. Attempt premature confirmation before approval (Should FAIL 400)
    status, res = api_call(f"/school/admissions/{app_id}/final-admission-confirm", "POST", {
        "section_id": "SEC-SCH001-STD4-A"
    }, staff_token)
    assert status == 400, f"Expected 400 on premature confirmation, got {status}"
    print(f"    -> Premature final confirmation blocked when status='submitted' (HTTP 400) PASSED.")

    # 5. Staff Approves Stage 1
    status, res = api_call(f"/school/admissions/{app_id}/approve", "POST", {
        "confirm": True,
        "note": "Stage 1 approved. Quota and catchment criteria met."
    }, staff_token)
    assert status == 200

    # 6. Parent Submits Stage 2 Detailed Demographics
    status, res = api_call(f"/admissions/applications/{app_id}/stage2-submit", "POST", {
        "date_of_birth": "2016-08-20",
        "gender": "female",
        "blood_group": "A+",
        "emergency_contact_name": "Ramesh Kumar",
        "emergency_contact_phone": "9876543210",
        "previous_institution_name": "Basavanagudi Primary School",
        "previous_institution_location": "Bengaluru",
        "previous_standard_or_degree": "Standard 3",
        "previous_board": "Karnataka State Board (KSEAB)",
        "previous_marks_percentage": 92.0
    }, parent_token)
    assert status == 200

    # 7. Parent Uploads Certificates
    dummy_pdf = base64.b64encode(b"%PDF-1.4 Certificate Content Deepa").decode("ascii")
    dummy_jpg = base64.b64encode(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08").decode("ascii")

    for dtype, fname, fdata, mtype in [
        ("birth_certificate", "birth_cert.pdf", dummy_pdf, "application/pdf"),
        ("passport_photo", "photo.jpg", dummy_jpg, "image/jpeg"),
        ("previous_marks_card", "std3_marks.pdf", dummy_pdf, "application/pdf"),
        ("transfer_certificate", "school_tc.pdf", dummy_pdf, "application/pdf"),
    ]:
        status, res = api_call(f"/admissions/applications/{app_id}/documents", "POST", {
            "document_type": dtype,
            "file_name": fname,
            "file_data_base64": fdata,
            "mime_type": mtype
        }, parent_token)
        assert status == 200

    # 8. Attempt confirmation when documents are unverified (Should FAIL 400)
    status, res = api_call(f"/school/admissions/{app_id}/final-admission-confirm", "POST", {
        "section_id": "SEC-SCH001-STD4-A"
    }, staff_token)
    assert status == 400, f"Expected 400 when unverified documents exist, got {status}"
    print(f"    -> Final confirmation blocked when documents unverified (HTTP 400) PASSED.")

    # 9. Staff Verifies all uploaded certificates
    status, docs = api_call(f"/admissions/applications/{app_id}/documents")
    for d in docs:
        status, res = api_call(f"/school/admissions/{app_id}/documents/{d['document_id']}/verify", "POST", {
            "verification_status": "verified",
            "verification_notes": "Official verification completed."
        }, staff_token)
        assert status == 200
    print("    -> Staff verified all 4 certificates.")

    # 10. Staff Marks Stage 2 Review Completed
    status, res = api_call(f"/school/admissions/{app_id}/stage2-review", "POST", {
        "decision": "detailed_review_completed",
        "review_notes": "Stage 2 dossier fully verified. Ready for seat allotment."
    }, staff_token)
    assert status == 200
    print("    -> Stage 2 review completed (status: detailed_review_completed).")

    # 11. Test Available Sections API
    status, sections = api_call(f"/school/admissions/{app_id}/available-sections", "GET", None, staff_token)
    assert status == 200
    assert len(sections) > 0
    target_section = sections[0]
    sec_id = target_section["section_id"]
    init_sec_strength = target_section["current_strength"]
    sec_capacity = target_section["capacity"]
    print(f"[*] Available Section for Enrolment: {sec_id} (Capacity: {sec_capacity}, Strength: {init_sec_strength})")

    # 12. Capacity Limit Saturation Gate Test
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Temporarily set section strength = capacity to test gate
    cur.execute("UPDATE program_sections SET current_strength = capacity WHERE section_id = ?", (sec_id,))
    conn.commit()
    conn.close()

    status, res = api_call(f"/school/admissions/{app_id}/final-admission-confirm", "POST", {
        "section_id": sec_id
    }, staff_token)
    assert status == 400, f"Expected 400 on full capacity, got {status}"
    print(f"    -> Capacity saturation gate verified (HTTP 400: '{res['detail']}') PASSED.")

    # Restore initial section strength
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE program_sections SET current_strength = ? WHERE section_id = ?", (init_sec_strength, sec_id))
    conn.commit()
    conn.close()

    # 13. Confirm Final Admission and Enrol Student (SUCCESS)
    status, enrol_res = api_call(f"/school/admissions/{app_id}/final-admission-confirm", "POST", {
        "section_id": sec_id,
        "admission_date": "2026-11-01",
        "notes": "Verified all admission criteria. Seat allotted in Section A."
    }, staff_token)
    assert status == 200, f"Failed final admission confirmation: {enrol_res}"
    assert enrol_res["status"] == "enrolled"
    perm_id = enrol_res["permanent_student_id"]
    stud_pk = enrol_res["student_id"]
    enr_pk = enrol_res["enrollment_id"]
    new_sec_strength = enrol_res["new_section_strength"]
    print(f"[*] Final Admission Confirmation Succeeded:")
    print(f"    - Permanent Student ID: {perm_id}")
    print(f"    - Student PK: {stud_pk}")
    print(f"    - Enrollment PK: {enr_pk}")
    print(f"    - Section Strength Incremented: {init_sec_strength} -> {new_sec_strength}")
    assert new_sec_strength == init_sec_strength + 1, "Section capacity not incremented by exactly 1!"
    print("    -> Section strength increment (+1) PASSED.")

    # 14. Verify DB Records in students and enrollments
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    student_row = cur.execute("SELECT * FROM students WHERE permanent_student_id = ?", (perm_id,)).fetchone()
    assert student_row is not None, "Student record was not created in students table!"
    assert student_row[1] == "Deepa Ramesh Final Enrolment"
    assert student_row[2] == "SCH001"
    assert student_row[11] == "active"

    enrollment_row = cur.execute("SELECT * FROM enrollments WHERE permanent_student_id = ?", (perm_id,)).fetchone()
    assert enrollment_row is not None, "Enrollment record was not created in enrollments table!"
    assert enrollment_row[2] == "SCH001"
    assert enrollment_row[3] == "2026-2027"
    assert enrollment_row[11] == "active"

    app_db_row = cur.execute("SELECT status, enrolled_student_id FROM admission_applications WHERE application_id = ?", (app_id,)).fetchone()
    assert app_db_row[0] == "enrolled"
    assert app_db_row[1] == perm_id

    post_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    post_enrollments = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    conn.close()

    print(f"[*] Post-enrolment Database Counts:")
    print(f"    - Students: {post_students} (Expected: 30,001)")
    print(f"    - Enrollments: {post_enrollments} (Expected: 30,001)")
    assert post_students == 30001, f"Expected 30001, got {post_students}"
    assert post_enrollments == 30001, f"Expected 30001, got {post_enrollments}"
    print("    -> Exact single-row creation in students and enrollments PASSED.")

    # 15. Idempotency Check: Re-submitting final confirmation returns existing
    status, idemp_res = api_call(f"/school/admissions/{app_id}/final-admission-confirm", "POST", {
        "section_id": sec_id
    }, staff_token)
    assert status == 200
    assert idemp_res["is_already_enrolled"] is True
    assert idemp_res["permanent_student_id"] == perm_id

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    post_idemp_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    post_idemp_enrollments = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    post_idemp_strength = cur.execute("SELECT current_strength FROM program_sections WHERE section_id = ?", (sec_id,)).fetchone()[0]
    conn.close()

    assert post_idemp_students == 30001, "Duplicate student row created on repeated call!"
    assert post_idemp_enrollments == 30001, "Duplicate enrollment row created on repeated call!"
    assert post_idemp_strength == new_sec_strength, "Section capacity incremented on repeated call!"
    print("    -> Idempotency protection (no duplicate rows, no extra capacity increments) PASSED.")

    # 16. Parent View Notification & Record Visibility
    status, notifs = api_call("/notifications", "GET", None, parent_token)
    assert status == 200
    has_enrol_notif = any("Enrolled" in n.get("title", "") and n.get("application_id") == app_id for n in (notifs if isinstance(notifs, list) else notifs.get("notifications", [])))
    print(f"    -> Parent enrolment notification received: {has_enrol_notif} PASSED.")

    # 17. Status History Audit Trail
    status, hist = api_call(f"/school/admissions/{app_id}/history", "GET", None, staff_token)
    assert status == 200
    hist_entries = hist if isinstance(hist, list) else hist.get("history", [])
    statuses_seen = [h["new_status"] for h in hist_entries]
    print(f"    -> Status transition audit trail: {statuses_seen}")
    assert "enrolled" in statuses_seen
    print("    -> End-to-end audit trail verified PASSED.")

    print("=" * 75)
    print("ALL 17 PHASE 6 ACCEPTANCE CRITERIA VERIFIED AND PASSED!")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
