import base64
import io
import json
import os
import sqlite3
import sys
import urllib.request
import urllib.error
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

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
        with urllib.request.urlopen(req, timeout=15) as res:
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

def generate_test_certificate_image(name, dob, reg_no, authority):
    """
    Renders a realistic educational certificate image using Pillow.
    """
    img = Image.new("RGB", (900, 500), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Simple clean text drawing
    lines = [
        (authority.upper(), 50, 40),
        ("OFFICIAL TRANSFER CERTIFICATE", 220, 80),
        (f"Certificate No: {reg_no}", 50, 150),
        (f"Name of Candidate: {name}", 50, 200),
        (f"Date of Birth: {dob}", 50, 250),
        ("Qualifying Standard: Standard 5 Passed", 50, 300),
        ("Academic Performance: 88.5% First Class", 50, 350),
        ("Issued by Registrar of Examination", 50, 420),
    ]

    for text, x, y in lines:
        draw.text((x, y), text, fill="#000000")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode("ascii")

def run_tests():
    print("=" * 75)
    print("NAGRIKSETU PHASE 8 ACCEPTANCE VERIFICATION SUITE")
    print("Real IDP / OCR Document Intelligence, Field Extraction & Human Audit")
    print("=" * 75)

    # 1. Baseline DB Verification
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    students_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    enrollments_count = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    conn.close()

    print(f"[*] Baseline DB Check: {students_count} students, {enrollments_count} enrollments.")
    assert students_count >= 30000 and enrollments_count >= 30000
    print("    -> Baseline Database Integrity PASSED.")

    # 2. Authentication
    staff_token = get_auth_token("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    parent_token = get_auth_token("raghu.test.stage1@example.com", "Staff@NagrikSetu2026!")
    assert staff_token and parent_token, "Auth failed!"
    print("[*] Staff and Parent Authentications Succeeded.")

    # 3. Create Application for OCR Testing
    app_payload = {
        "institution_id": "SCH001",
        "education_level": "school",
        "requested_standard": 6,
        "first_language_preference": "Kannada",
        "second_language_preference": "English",
        "applicant_name": "Rohan Kumar Acceptance",
        "parent_name": "Ramesh Kumar Acceptance",
        "parent_phone": "9876543210",
        "parent_email": "raghu.test.stage1@example.com",
        "residential_address": "Indiranagar, Bengaluru, Karnataka",
        "academic_year": "2026-2027"
    }
    status, app_res = api_call("/admissions/apply", "POST", app_payload, parent_token)
    assert status in (200, 201)
    app_id = app_res["application_id"]
    print(f"[*] Created Admission Application: {app_id}")

    # Approve Stage 1 and submit Stage 2 Demographics
    status, _ = api_call(f"/school/admissions/{app_id}/approve", "POST", {"confirm": True, "note": "Stage 1 approved."}, staff_token)
    assert status == 200

    status, _ = api_call(f"/admissions/applications/{app_id}/stage2-submit", "POST", {
        "date_of_birth": "2014-05-15",
        "gender": "male",
        "blood_group": "O+",
        "emergency_contact_name": "Ramesh Kumar",
        "emergency_contact_phone": "9876543210",
        "previous_institution_name": "Govt Primary School",
        "previous_standard_or_degree": "Standard 5",
        "previous_board": "Karnataka State Board (KSEAB)",
        "previous_marks_percentage": 88.5
    }, parent_token)
    assert status == 200

    # 4. Generate Real Certificate Image with Matching Entities
    match_b64 = generate_test_certificate_image(
        name="Rohan Kumar Acceptance",
        dob="15/05/2014",
        reg_no="TC-2026-88741",
        authority="Karnataka School Examination and Assessment Board (KSEAB)"
    )

    # Upload Matching Certificate Document
    status, doc_res = api_call(f"/admissions/applications/{app_id}/documents", "POST", {
        "document_type": "transfer_certificate",
        "file_name": "kseab_transfer_certificate.jpg",
        "file_data_base64": match_b64,
        "mime_type": "image/jpeg"
    }, parent_token)
    assert status == 200
    doc_id = doc_res["document_id"]
    print(f"[*] Uploaded Real Certificate Document: {doc_id}")

    # 5. Run Real OCR Intelligence Analysis via Tesseract
    status, ocr_res = api_call(f"/school/admissions/{app_id}/documents/{doc_id}/ocr-analyze", "POST", None, staff_token)
    assert status == 200, f"OCR analysis failed: {ocr_res}"

    print(f"[*] Real OCR Analysis Output:")
    print(f"    - Engine: {ocr_res['ocr_engine']}")
    print(f"    - Measured Word Confidence: {ocr_res['confidence_percentage']}%")
    print(f"    - Extracted Entities: {ocr_res['extracted_entities']}")
    print(f"    - Match Status: {ocr_res['match_status']}")
    print(f"    - Audit Notes: {ocr_res['discrepancy_notes']}")

    assert ocr_res["ocr_engine"] == "tesseract_5.5.0_ocr", "Expected real Tesseract 5.5.0 engine!"
    assert ocr_res["confidence_percentage"] > 50.0, "Expected valid confidence score from OCR!"
    entities = ocr_res["extracted_entities"]
    assert "Rohan" in (entities.get("candidate_name") or ""), f"Candidate name not detected: {entities.get('candidate_name')}"
    assert "15/05/2014" in (entities.get("date_of_birth") or "") or "2014" in (entities.get("date_of_birth") or ""), "DOB not detected correctly!"
    assert entities.get("registration_number") is not None, "Registration number not parsed!"
    assert ocr_res["match_status"] == "verified_match", f"Expected verified_match, got: {ocr_res['match_status']}"
    print("    -> Real Tesseract OCR, confidence calculation & verified match PASSED.")

    # 6. Test Discrepancy Detection: Upload Mismatched Certificate
    mismatch_b64 = generate_test_certificate_image(
        name="Suresh Ramarao Patil", # Mismatched name
        dob="01/01/2005",             # Mismatched DOB
        reg_no="TC-2019-99881",
        authority="Central Board of Secondary Education (CBSE)"
    )

    status, doc_mismatch = api_call(f"/admissions/applications/{app_id}/documents", "POST", {
        "document_type": "birth_certificate",
        "file_name": "mismatched_birth_cert.jpg",
        "file_data_base64": mismatch_b64,
        "mime_type": "image/jpeg"
    }, parent_token)
    assert status == 200
    mismatch_doc_id = doc_mismatch["document_id"]

    status, ocr_mismatch_res = api_call(f"/school/admissions/{app_id}/documents/{mismatch_doc_id}/ocr-analyze", "POST", None, staff_token)
    assert status == 200
    print(f"[*] Discrepancy Test Output:")
    print(f"    - Match Status: {ocr_mismatch_res['match_status']}")
    print(f"    - Discrepancy Notes: {ocr_mismatch_res['discrepancy_notes']}")
    assert ocr_mismatch_res["match_status"] == "discrepancy_detected", "Discrepancy was not flagged!"
    assert "Discrepancy" in ocr_mismatch_res["discrepancy_notes"]
    print("    -> Real Discrepancy Detection (Name/DOB mismatch flagged) PASSED.")

    # 7. Test Human-In-The-Loop Staff Review & Override
    status, override_res = api_call(f"/school/admissions/{app_id}/documents/{mismatch_doc_id}/ocr-override", "POST", {
        "override_notes": "Staff visually inspected municipal stamp; discrepancy resolved via family affidavit.",
        "verified_match_status": "verified_match"
    }, staff_token)
    assert status == 200
    assert override_res["match_status"] == "verified_match"
    print("    -> Human-in-the-loop staff override completed PASSED.")

    # 8. Test OCR Result Retrieval Endpoint
    status, stored_ocr = api_call(f"/school/admissions/{app_id}/documents/{doc_id}/ocr-result", "GET", None, staff_token)
    assert status == 200
    assert stored_ocr["has_ocr_result"] is True
    assert stored_ocr["ocr_engine"] == "tesseract_5.5.0_ocr"
    print("    -> Stored OCR extraction retrieval endpoint (/ocr-result) PASSED.")

    # 9. Final Database Verification
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    final_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    final_enrollments = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    ocr_rows_count = cur.execute("SELECT COUNT(*) FROM document_ocr_extractions").fetchone()[0]
    conn.close()

    assert final_students == students_count, "Student records modified during OCR testing!"
    assert final_enrollments == enrollments_count, "Enrollment records modified during OCR testing!"
    assert ocr_rows_count >= 2, "OCR extraction records not saved in DB!"
    print(f"[*] Database Counts Check: {final_students} students, {final_enrollments} enrollments strictly preserved.")
    print(f"[*] Stored OCR Extractions: {ocr_rows_count} records archived.")

    print("=" * 75)
    print("ALL 9 PHASE 8 ACCEPTANCE CRITERIA VERIFIED AND PASSED!")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
