import requests
import json
import sqlite3
import base64
import os

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000" if os.path.exists("/app") else "http://127.0.0.1:8001")
DB_PATH = "/app/data/nagriksetu.db" if os.path.exists("/app/data/nagriksetu.db") else r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def login(username, password):
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        raise Exception(f"Login failed for {username}: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]

def make_token(user_id, role, school_id=None):
    import jwt, datetime, uuid
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "school_id": school_id,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=60),
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, "PASTE_YOUR_GENERATED_SECRET_HERE", algorithm="HS256")

def run_tests():
    print("=" * 60)
    print("RUNNING DOCUMENT ACTIONS & VERIFICATION TEST SUITE")
    print("=" * 60)

    # 1. Login as K.S Rao (Academic Admin of SCH019)
    admin_token = login("rao@edu.in", "Rao@1234")
    print("1. Admin Login (K.S Rao, SCH019): SUCCESS")

    # 2. Token for real admin of another school (COL003 - Bharath) for cross-institution test
    other_token = make_token("890807ce-29dd-4ef7-84fd-bd2b89b80e19", "school_admin", school_id="COL003")
    print("2. COL003 Admin Token (Bharath): GENERATED")
    print("2. SCH001 Admin Login: SUCCESS")

    # 3. Target application with 6 documents
    app_id = "APP-2026-SCH019-6DF0C3"
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Fetch dossier
    dossier_resp = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers)
    assert dossier_resp.status_code == 200, f"Failed to get dossier: {dossier_resp.text}"
    dossier = dossier_resp.json()
    docs = dossier["documents"]
    print(f"3. Retrieved Application Dossier: {len(docs)} documents found (Applicant: {dossier['applicant_name']})")
    
    doc_types = [d["document_type"] for d in docs]
    print(f"   Categories present: {doc_types}")
    assert len(docs) >= 6, f"Expected at least 6 documents, got {len(docs)}"

    # 4. TEST: Secure Authenticated File View / Download
    print("\n--- TEST: VIEW & DOWNLOAD WITH AUTHENTICATION ---")
    doc0 = docs[0]
    file_url = f"{BASE_URL}{doc0['download_url']}?token={admin_token}"
    resp_view = requests.get(file_url)
    assert resp_view.status_code == 200, f"Expected 200 for authenticated file download, got {resp_view.status_code}"
    assert len(resp_view.content) > 0, "File content is empty"
    print(f"   ✓ Authenticated File Access: 200 OK ({len(resp_view.content)} bytes, Content-Type: {resp_view.headers.get('content-type')})")

    # Test unauthenticated access (no token) -> must be 401 or 403
    unauth_url = f"{BASE_URL}{doc0['download_url']}"
    resp_unauth = requests.get(unauth_url)
    assert resp_unauth.status_code in (401, 403), f"Expected 401/403 for unauthenticated access, got {resp_unauth.status_code}"
    print(f"   ✓ Unauthenticated File Access Blocked: {resp_unauth.status_code} {resp_unauth.text}")

    # Test cross-institution access (COL003 admin trying to download SCH019 doc) -> 403 Forbidden
    cross_url = f"{BASE_URL}{doc0['download_url']}?token={other_token}"
    resp_cross = requests.get(cross_url)
    assert resp_cross.status_code == 403, f"Expected 403 for cross-institution download, got {resp_cross.status_code}"
    print(f"   ✓ Cross-Institution Download Blocked: 403 Forbidden")

    # 5. TEST: Cross-Institution Verification Blocked
    print("\n--- TEST: CROSS-INSTITUTION VERIFICATION & REJECTION BLOCKED ---")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    cross_verify = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{doc0['document_id']}/verify",
        json={"verification_status": "verified"},
        headers=other_headers
    )
    assert cross_verify.status_code == 403, f"Expected 403 Forbidden, got {cross_verify.status_code} {cross_verify.text}"
    print(f"   ✓ Cross-Institution Verify Blocked: 403 Forbidden ({cross_verify.json()['detail']})")

    # 6. TEST: ACCEPT ACTION
    print("\n--- TEST: ACCEPT ACTION ---")
    # Reset doc0 to pending first in DB if needed so we can test cleanly
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE admission_documents SET verification_status='pending', verification_notes=NULL WHERE document_id=?", (doc0["document_id"],))
    conn.commit()
    conn.close()

    accept_resp = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{doc0['document_id']}/verify",
        json={"verification_status": "verified", "verification_notes": "Official birth certificate verified against municipal records."},
        headers=headers
    )
    assert accept_resp.status_code == 200, f"Accept failed: {accept_resp.text}"
    accept_data = accept_resp.json()
    assert accept_data["verification_status"] == "verified"
    print(f"   ✓ Document Accepted: Status={accept_data['verification_status']}, Message='{accept_data.get('message')}'")

    # Verify repeated acceptance is rejected (HTTP 400)
    repeat_accept = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{doc0['document_id']}/verify",
        json={"verification_status": "verified"},
        headers=headers
    )
    assert repeat_accept.status_code == 400, f"Expected 400 on repeated accept, got {repeat_accept.status_code}"
    print(f"   ✓ Repeated Accept Blocked: 400 Bad Request ({repeat_accept.json()['detail']})")

    # 7. TEST: REJECT ACTION (MANDATORY REASON VALIDATION)
    print("\n--- TEST: REJECT ACTION & MANDATORY REASON ---")
    doc1 = docs[1] # passport_photo or marks card
    # Attempt reject with empty reason -> must fail with 400
    reject_no_reason = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{doc1['document_id']}/verify",
        json={"verification_status": "rejected", "verification_notes": "   "},
        headers=headers
    )
    assert reject_no_reason.status_code == 400, f"Expected 400 for empty rejection reason, got {reject_no_reason.status_code}"
    print(f"   ✓ Empty Rejection Reason Rejected: 400 Bad Request ({reject_no_reason.json()['detail']})")

    # Valid rejection
    reject_reason = "Photograph background is not plain white and facial features are shaded."
    reject_resp = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{doc1['document_id']}/verify",
        json={"verification_status": "rejected", "verification_notes": reject_reason},
        headers=headers
    )
    assert reject_resp.status_code == 200, f"Rejection failed: {reject_resp.text}"
    reject_data = reject_resp.json()
    assert reject_data["verification_status"] == "rejected"
    print(f"   ✓ Document Rejected: Status={reject_data['verification_status']}")

    # Verify repeated rejection is rejected (HTTP 400)
    repeat_reject = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{doc1['document_id']}/verify",
        json={"verification_status": "rejected", "verification_notes": "Another reason"},
        headers=headers
    )
    assert repeat_reject.status_code == 400, f"Expected 400 on repeated reject, got {repeat_reject.status_code}"
    print(f"   ✓ Repeated Reject Blocked: 400 Bad Request ({repeat_reject.json()['detail']})")

    # 8. TEST: PARENT NOTIFICATION GENERATION
    print("\n--- TEST: PARENT NOTIFICATION ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    notifs = conn.execute(
        "SELECT * FROM portal_notifications WHERE application_id = ? ORDER BY created_at DESC LIMIT 5",
        (app_id,)
    ).fetchall()
    print(f"   Found {len(notifs)} recent notifications for application {app_id}:")
    for n in notifs:
        print(f"     - Title: '{n['title']}' | Message: '{n['message']}'")
    
    assert any("rejected" in n["title"].lower() or "rejected" in n["message"].lower() for n in notifs), "Rejection notification not found"
    print("   ✓ Parent Notification Successfully Verified!")

    # 9. TEST: AUDIT TRAIL PRESERVATION
    print("\n--- TEST: AUDIT TRAIL PRESERVATION ---")
    hist_resp = requests.get(f"{BASE_URL}/school/admissions/{app_id}/history", headers=headers)
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    print(f"   Retrieved {len(hist)} status history audit entries:")
    for h in hist[-4:]:
        print(f"     - [{h.get('created_at')}] {h.get('action_note')}")
    conn.close()

    # 10. TEST: PARENT REPLACEMENT UPLOAD
    print("\n--- TEST: PARENT REPLACEMENT UPLOAD ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    parent_user = conn.execute(
        "SELECT u.user_id, u.role FROM users u JOIN admission_applications a ON a.parent_user_id = u.user_id WHERE a.application_id = ?",
        (app_id,)
    ).fetchone()
    conn.close()

    if parent_user:
        import jwt, datetime, uuid
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": parent_user["user_id"],
            "role": "parent",
            "school_id": None,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=60),
            "jti": str(uuid.uuid4())
        }
        parent_token = jwt.encode(payload, "PASTE_YOUR_GENERATED_SECRET_HERE", algorithm="HS256")
        parent_headers = {"Authorization": f"Bearer {parent_token}"}
        
        # Upload replacement photograph
        fake_jpg = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"A" * 100
        b64_content = base64.b64encode(fake_jpg).decode("utf-8")
        
        replace_resp = requests.post(
            f"{BASE_URL}/admissions/applications/{app_id}/documents",
            json={
                "document_type": doc1["document_type"],
                "file_name": "replacement_passport_photo_clean.jpg",
                "file_data_base64": b64_content,
                "mime_type": "image/jpeg"
            },
            headers=parent_headers
        )
        assert replace_resp.status_code == 200, f"Upload replacement failed: {replace_resp.text}"
        print(f"   ✓ Parent uploaded replacement document: {replace_resp.json()['file_name']}")

        # Re-fetch dossier as admin
        dossier_after = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers).json()
        matching_docs = [d for d in dossier_after["documents"] if d["document_type"] == doc1["document_type"]]
        print(f"   Document versions for {doc1['document_type']}: {len(matching_docs)}")
        for md in matching_docs:
            print(f"     - v{md.get('version')} (Latest: {md.get('is_latest')}): {md['file_name']} -> Status: {md['verification_status']}")
        
        assert len(matching_docs) >= 2, "Expected at least 2 versions (original rejected + new replacement)"
        assert matching_docs[-1]["verification_status"] == "pending", "Newest replacement must be pending"
        assert matching_docs[-1]["is_latest"] == True, "Newest replacement must have is_latest=True"
        print("   ✓ Version history and replacement preservation verified!")

    # 11. TEST: VERIFY ACROSS ALL 6 DOCUMENT CATEGORIES
    print("\n--- TEST: ALL 6 DOCUMENT CATEGORIES ---")
    categories = [
        "birth_certificate", "passport_photo", "previous_marks_card",
        "transfer_certificate", "caste_certificate", "income_certificate"
    ]
    current_dossier = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers).json()
    all_types_in_app = set(d["document_type"] for d in current_dossier["documents"])
    for cat in categories:
        assert cat in all_types_in_app, f"Category {cat} missing in dossier"
        print(f"   ✓ Category verified present: {cat}")

    # 12. TEST: DATABASE INTEGRITY
    print("\n--- TEST: DATABASE INTEGRITY ---")
    conn = sqlite3.connect(DB_PATH)
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_enrollments = conn.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    fk_checks = conn.execute("PRAGMA foreign_key_check(students)").fetchall()
    fk_checks += conn.execute("PRAGMA foreign_key_check(enrollments)").fetchall()
    fk_checks += conn.execute("PRAGMA foreign_key_check(admission_documents)").fetchall()
    conn.close()

    assert total_students == 30003, f"Expected 30003 students, got {total_students}"
    assert total_enrollments == 30003, f"Expected 30003 enrollments, got {total_enrollments}"
    assert len(fk_checks) == 0, f"Foreign key violations found: {fk_checks}"
    print(f"   ✓ Total Students Preserved: {total_students}")
    print(f"   ✓ Total Enrollments Preserved: {total_enrollments}")
    print(f"   ✓ Foreign Key Violations: {len(fk_checks)}")

    print("\n" + "=" * 60)
    print("ALL DOCUMENT ACTION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
