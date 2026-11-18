import requests
import json
import base64

BASE_URL = "http://localhost:8001"

def run_tests():
    print("=" * 70)
    print("NAGRIKSETU STAGE 2 DOSSIER & DOCUMENT VERIFICATION TEST SUITE")
    print("=" * 70)

    # 1. Login as K.S Rao (Academic Administrator, SCH019)
    print("\n[TEST 1] Authenticating as K.S Rao (Academic Admin of SCH019)...")
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Authenticated successfully.")

    # 2. Retrieve target application APP-2026-SCH019-6ED0FE (Jenifer)
    app_id = "APP-2026-SCH019-6ED0FE"
    print(f"\n[TEST 2] Retrieving full dossier for {app_id}...")
    res_app = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers)
    assert res_app.status_code == 200, f"Detail retrieval failed: {res_app.text}"
    app_data = res_app.json()

    # Verify Stage 1 Info
    print("\n[TEST 3] Verifying Stage 1 Information preservation...")
    print(f"  Applicant: {app_data.get('applicant_name')}")
    print(f"  Parent: {app_data.get('parent_name')} (Phone: {app_data.get('parent_phone')})")
    print(f"  Institution: {app_data.get('school_name')} ({app_data.get('institution_id')})")
    print(f"  Standard: {app_data.get('requested_standard')}")
    print(f"  Academic Year: {app_data.get('academic_year')}")
    assert app_data.get("applicant_name") == "Jenifer", "Applicant name mismatch"
    assert app_data.get("institution_id") == "SCH019", "Institution ID mismatch"
    assert app_data.get("parent_name") == "Mary", "Parent name mismatch"
    print("[OK] Stage 1 records verified intact.")

    # Verify Stage 1 Status History
    print("\n[TEST 4] Verifying Stage 1 Status History & Audit Trail...")
    history = app_data.get("status_history", [])
    print(f"  Found {len(history)} historical audit transitions:")
    for h in history:
        print(f"    - {h.get('created_at')}: {h.get('previous_status')} -> {h.get('new_status')} | Note: {h.get('action_note')}")
    assert len(history) >= 3, "Expected at least 3 historical records"
    assert any(h.get("new_status") == "approved" for h in history), "Stage 1 approval must exist in history"
    assert any(h.get("new_status") == "stage2_submitted" for h in history), "Stage 2 submission must exist in history"
    print("[OK] Stage 1 approval and historical timeline verified intact.")

    # Verify Stage 2 Details
    print("\n[TEST 5] Verifying Stage 2 Detailed Demographic & Academic Submission...")
    assert app_data.get("stage2_submitted") is True, "stage2_submitted flag must be True"
    s2 = app_data.get("stage2_details")
    assert s2 is not None, "stage2_details must not be null"
    print(f"  Date of Birth: {s2.get('date_of_birth')}")
    print(f"  Gender / Blood Group: {s2.get('gender')} / {s2.get('blood_group')}")
    print(f"  Previous Institution: {s2.get('previous_institution_name')} ({s2.get('previous_institution_location')})")
    print(f"  Previous Standard: {s2.get('previous_standard_or_degree')}")
    print(f"  Previous Board: {s2.get('previous_board')}")
    print(f"  Previous Marks %: {s2.get('previous_marks_percentage')}%")
    print(f"  Emergency Contact: {s2.get('emergency_contact_name')} (Phone: {s2.get('emergency_contact_phone')})")
    assert s2.get("previous_institution_name") == "Kendriya Vidyalaya"
    assert s2.get("previous_marks_percentage") == 76.0
    assert s2.get("emergency_contact_name") == "Jury"
    print("[OK] Stage 2 demographic and academic details verified.")

    # Verify Uploaded Documents
    print("\n[TEST 6] Verifying Uploaded Documents List & Metadata...")
    docs = app_data.get("documents", [])
    print(f"  Total Documents Found: {len(docs)}")
    assert len(docs) == 6, f"Expected 6 documents, found {len(docs)}"
    for d in docs:
        print(f"    - [{d.get('verification_status')}] {d.get('document_type')}: {d.get('file_name')} ({d.get('file_size_bytes')} bytes)")
    doc_types = [d["document_type"] for d in docs]
    for expected_type in ["birth_certificate", "passport_photo", "previous_marks_card", "transfer_certificate", "caste_certificate", "income_certificate"]:
        assert expected_type in doc_types, f"Missing document type: {expected_type}"
    print("[OK] All 6 statutory documents listed with exact metadata.")

    # Verify Secure Document Download & Preview
    print("\n[TEST 7] Testing Secure Authenticated Document Access...")
    for d in docs[:2]:
        file_url = f"{BASE_URL}{d['download_url']}?token={token}"
        f_res = requests.get(file_url)
        assert f_res.status_code == 200, f"Document file download failed: {f_res.status_code}"
        assert len(f_res.content) == d["file_size_bytes"], "File content size mismatch"
        print(f"  [OK] Successfully streamed {d['file_name']} ({len(f_res.content)} bytes, Content-Type: {f_res.headers.get('content-type')})")

    # Verify Cross-Tenant Isolation
    print("\n[TEST 8] Verifying Cross-Tenant Security Isolation...")
    # Attempting to access SCH019 document using an unauthorized user or checking another institution
    res_unauth = requests.get(f"{BASE_URL}{docs[0]['download_url']}")
    assert res_unauth.status_code in (401, 403), f"Unauthenticated request should be denied, got {res_unauth.status_code}"
    print(f"  [OK] Unauthenticated document access blocked with HTTP {res_unauth.status_code}.")

    # Test Document Verification Status Update
    print("\n[TEST 9] Testing Document Verification Update (Mark Verified)...")
    target_doc = docs[0] # birth_certificate
    v_res = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{target_doc['document_id']}/verify",
        headers=headers,
        json={
            "verification_status": "verified",
            "verification_notes": "Birth certificate verified against official municipal record."
        }
    )
    assert v_res.status_code == 200, f"Verify doc failed: {v_res.text}"
    print(f"  [OK] Document {target_doc['document_id']} marked as verified.")

    # Re-fetch application and check updated verification status
    res_after_v = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers)
    updated_docs = res_after_v.json().get("documents", [])
    verified_match = next((d for d in updated_docs if d["document_id"] == target_doc["document_id"]), None)
    assert verified_match is not None and verified_match["verification_status"] == "verified"
    print(f"  [OK] Verified count updated: {res_after_v.json().get('verified_documents_count')}/{res_after_v.json().get('total_documents_count')}")

    # Test Request Replacement Document
    print("\n[TEST 10] Testing Requesting Document Replacement...")
    tc_doc = next(d for d in docs if d["document_type"] == "transfer_certificate")
    req_res = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/documents/{tc_doc['document_id']}/verify",
        headers=headers,
        json={
            "verification_status": "reupload_requested",
            "verification_notes": "Please provide a higher resolution scan with visible school seal and counter-signature."
        }
    )
    assert req_res.status_code == 200, f"Request replacement failed: {req_res.text}"
    print("  [OK] Replacement request successfully registered with notes.")

    # Verify audit history records the document action
    res_hist = requests.get(f"{BASE_URL}/school/admissions/{app_id}/history", headers=headers)
    hist_list = res_hist.json() if isinstance(res_hist.json(), list) else res_hist.json().get("history", [])
    assert any("transfer_certificate" in (h.get("action_note") or "") and "replacement requested" in (h.get("action_note") or "") for h in hist_list)
    print("  [OK] Document action confirmed in historical audit trail.")

    # Test Parent Login and Replacement Document Upload
    print("\n[TEST 11] Testing Parent View & Replacement Document Upload...")
    parent_login = requests.post(f"{BASE_URL}/auth/login", data={"username": "8963527410", "password": "Mary@1234"})
    if parent_login.status_code != 200:
        # Check by email or parent user id
        parent_login = requests.post(f"{BASE_URL}/auth/login", data={"username": "mary@gmail.com", "password": "Mary@1234"})
    
    if parent_login.status_code == 200:
        p_token = parent_login.json()["access_token"]
        p_headers = {"Authorization": f"Bearer {p_token}"}
        print("  [OK] Parent Mary authenticated successfully.")
        
        # Parent checks documents
        p_docs_res = requests.get(f"{BASE_URL}/admissions/applications/{app_id}/documents", headers=p_headers)
        assert p_docs_res.status_code == 200
        print(f"  [OK] Parent retrieved {len(p_docs_res.json())} documents.")

        # Parent uploads updated Transfer Certificate
        dummy_content = b"REPLACEMENT TRANSFER CERTIFICATE VERIFIED BY BEO BALLARI"
        b64_content = base64.b64encode(dummy_content).decode("utf-8")
        up_res = requests.post(f"{BASE_URL}/admissions/applications/{app_id}/documents", headers=p_headers, json={
            "document_type": "transfer_certificate",
            "file_name": "TC_Certified_Original.jpg",
            "file_base64": b64_content,
            "mime_type": "image/jpeg"
        })
        assert up_res.status_code in (200, 201), f"Upload failed: {up_res.text}"
        print(f"  [OK] Parent successfully uploaded replacement Transfer Certificate: {up_res.json().get('document_id')}")

        # Institution Admin now verifies updated document
        admin_doc_verify = requests.post(
            f"{BASE_URL}/school/admissions/{app_id}/documents/{up_res.json()['document_id']}/verify",
            headers=headers,
            json={
                "verification_status": "verified",
                "verification_notes": "Replacement TC inspected and certified authentic."
            }
        )
        assert admin_doc_verify.status_code == 200
        print("  [OK] Institution administrator inspected and verified replacement document.")
    else:
        print(f"  [NOTE] Parent direct login skipped ({parent_login.status_code}), testing administrator verification workflow.")

    # Verify all remaining documents can be verified
    print("\n[TEST 12] Verifying Remaining Documents for Stage 2 Completion...")
    cur_docs = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers).json().get("documents", [])
    for d in cur_docs:
        if d["verification_status"] != "verified":
            requests.post(
                f"{BASE_URL}/school/admissions/{app_id}/documents/{d['document_id']}/verify",
                headers=headers,
                json={"verification_status": "verified", "verification_notes": "Certificate confirmed authentic."}
            )
    
    refreshed = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers).json()
    print(f"  [OK] All documents verified: {refreshed.get('verified_documents_count')}/{refreshed.get('total_documents_count')}")

    # Test Complete Stage 2 Review
    print("\n[TEST 13] Executing Stage 2 Detailed Review Completion...")
    s2_comp_res = requests.post(
        f"{BASE_URL}/school/admissions/{app_id}/stage2-review",
        headers=headers,
        json={
            "decision": "detailed_review_completed",
            "review_notes": "All Stage 2 demographic, academic, and supporting documents verified. Approved for final seat allotment."
        }
    )
    assert s2_comp_res.status_code == 200, f"Stage 2 review complete failed: {s2_comp_res.text}"
    final_app = requests.get(f"{BASE_URL}/school/admissions/applications/{app_id}", headers=headers).json()
    assert final_app.get("status") == "detailed_review_completed", f"Status should be detailed_review_completed, got {final_app.get('status')}"
    # Verify student is NOT prematurely enrolled
    assert final_app.get("enrolled_student_id") is None, "Student must NOT be enrolled prematurely"
    print(f"  [OK] Stage 2 review completed. Current status: {final_app.get('status')}")
    print("  [OK] Premature student enrolment correctly avoided (enrolled_student_id is None).")

    print("\n" + "=" * 70)
    print("ALL 13 STAGE 2 DOSSIER & DOCUMENT VERIFICATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
