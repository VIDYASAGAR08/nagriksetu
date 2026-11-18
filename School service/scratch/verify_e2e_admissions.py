import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def run_tests():
    print("=" * 60)
    print("NAGRIKSETU ADMISSION WORKFLOW E2E VERIFICATION SUITE")
    print("=" * 60)

    # 1. Login as K.S Rao (Academic Administrator, SCH019)
    print("\n[TEST 1] Authenticating as K.S Rao (SCH019 Academic Admin)...")
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Successfully authenticated. JWT token obtained.")

    # 2. Verify /institution/SCH019/dashboard-overview
    print("\n[TEST 2] Verifying /institution/SCH019/dashboard-overview metrics...")
    res = requests.get(f"{BASE_URL}/institution/SCH019/dashboard-overview", headers=headers)
    assert res.status_code == 200, f"Overview failed: {res.text}"
    ov = res.json()
    print(f"[OK] Overview data: school_id={ov.get('institution_id')}, name={ov.get('institution_name')}")
    print(f"  Total Students: {ov.get('total_students')}")
    print(f"  Pending Admission Reviews: {ov.get('pending_admission_reviews')}")
    assert ov.get("institution_id") == "SCH019", "Institution ID mismatch"
    assert ov.get("pending_admission_reviews") >= 4, f"Expected at least 4 pending reviews, got {ov.get('pending_admission_reviews')}"

    # 3. Verify /school/admissions/applications (All applications)
    print("\n[TEST 3] Fetching all applications via /school/admissions/applications...")
    res = requests.get(f"{BASE_URL}/school/admissions/applications", headers=headers)
    assert res.status_code == 200, f"Applications endpoint failed: {res.text}"
    app_data = res.json()
    apps = app_data.get("applications", [])
    print(f"[OK] Retrieved {len(apps)} total applications for SCH019 (total reported: {app_data.get('total')})")
    assert len(apps) >= 5, f"Expected at least 5 applications for SCH019, got {len(apps)}"
    for a in apps[:5]:
        print(f"  - {a.get('application_id')} | Student: {a.get('applicant_name')} | Std: {a.get('requested_standard')} | Status: {a.get('status')}")

    # 4. Verify status filtering: submitted vs approved
    print("\n[TEST 4] Verifying status filtering (submitted vs approved)...")
    res_sub = requests.get(f"{BASE_URL}/school/admissions/applications?status_filter=submitted", headers=headers)
    assert res_sub.status_code == 200
    submitted_apps = res_sub.json().get("applications", [])
    print(f"[OK] Filter 'submitted': {len(submitted_apps)} application(s)")
    assert len(submitted_apps) >= 4, "Expected at least 4 submitted applications"

    res_appr = requests.get(f"{BASE_URL}/school/admissions/applications?status_filter=approved", headers=headers)
    assert res_appr.status_code == 200
    approved_apps = res_appr.json().get("applications", [])
    print(f"[OK] Filter 'approved': {len(approved_apps)} application(s)")
    assert any(a["applicant_name"] == "Karthik MR" for a in approved_apps), "Karthik MR should be in approved list"

    # 5. Application Detail & History
    print("\n[TEST 5] Verifying application detail and audit history endpoints...")
    test_app_id = "APP-2026-SCH019-30E92E"
    res_det = requests.get(f"{BASE_URL}/school/admissions/applications/{test_app_id}", headers=headers)
    assert res_det.status_code == 200, f"Detail failed: {res_det.text}"
    detail = res_det.json()
    print(f"[OK] Detail loaded for {test_app_id}:")
    print(f"  Applicant: {detail.get('applicant_name')} / {detail.get('student_name')}")
    print(f"  Parent: {detail.get('parent_name')} ({detail.get('parent_phone')})")
    print(f"  Institution: {detail.get('school_name')} ({detail.get('institution_id')})")
    print(f"  Standard: {detail.get('requested_standard')}")

    res_hist = requests.get(f"{BASE_URL}/school/admissions/{test_app_id}/history", headers=headers)
    assert res_hist.status_code == 200
    history = res_hist.json()
    hist_entries = history if isinstance(history, list) else history.get("history", [])
    print(f"[OK] History records retrieved: {len(hist_entries)} events")

    # 6. Cross-Tenant Security Check
    print("\n[TEST 6] Cross-tenant isolation verification (SCH019 trying to access SCH001)...")
    res_cross = requests.get(f"{BASE_URL}/school/admissions/applications/APP-2026-SCH001-C7FD1C", headers=headers)
    print(f"  Response status: {res_cross.status_code}")
    assert res_cross.status_code in (403, 404), f"Expected 403 or 404 for cross-tenant access, got {res_cross.status_code}"
    print(f"[OK] Cross-tenant access successfully blocked with {res_cross.status_code} Forbidden/Not Found!")

    # 7. Parent submission & Institutional Review Workflow (Clarify, Approve, Reject)
    print("\n[TEST 7] Testing full end-to-end parent submission and review actions...")
    parent_email = "testparent.ballari2@gmail.com"
    parent_pass = "Parent@1234"
    parent_phone = "9876501235"
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "full_name": "Suresh Ballari",
        "email": parent_email,
        "phone": parent_phone,
        "password": parent_pass,
        "confirm_password": parent_pass
    })
    # If already registered, login
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": parent_email, "password": parent_pass})
    assert login_res.status_code == 200, f"Parent login failed: {login_res.text}"
    parent_token = login_res.json()["access_token"]
    parent_headers = {"Authorization": f"Bearer {parent_token}"}
    print("[OK] Parent logged in successfully.")

    # Submit a new Stage 1 application to SCH019
    sub_res = requests.post(f"{BASE_URL}/admissions/apply", headers=parent_headers, json={
        "institution_id": "SCH019",
        "applicant_name": "Vijay Suresh",
        "parent_name": "Suresh Ballari",
        "parent_phone": parent_phone,
        "parent_email": parent_email,
        "education_level": "School",
        "requested_standard": "6",
        "academic_year": "2026-2027",
        "first_language_preference": "Kannada",
        "second_language_preference": "English",
        "residential_address": "Cantonment, Ballari, Karnataka"
    })
    assert sub_res.status_code in (200, 201), f"Stage 1 submit failed: {sub_res.text}"
    new_app = sub_res.json()
    new_app_id = new_app.get("application_id")
    print(f"[OK] New Stage 1 Application submitted by parent: {new_app_id}")

    # Admin verifies new application appears in list
    res_list_after = requests.get(f"{BASE_URL}/school/admissions/applications", headers=headers)
    apps_after = res_list_after.json().get("applications", [])
    assert any(a["application_id"] == new_app_id for a in apps_after), f"{new_app_id} should appear in SCH019 admin list"
    print(f"[OK] Application {new_app_id} immediately visible in SCH019 admin applications list!")

    # Admin requests clarification
    print(f"\n[TEST 8] Action: Admin requests clarification on {new_app_id}...")
    clarify_res = requests.post(f"{BASE_URL}/school/admissions/{new_app_id}/request-clarification", headers=headers, json={
        "clarification_message": "Please confirm if transfer certificate from previous school in Ballari is available."
    })
    assert clarify_res.status_code == 200, f"Clarify failed: {clarify_res.text}"
    print("[OK] Clarification request sent successfully.")

    # Parent checks tracking status
    p_track_res = requests.get(f"{BASE_URL}/parent/admissions/applications/{new_app_id}", headers=parent_headers)
    assert p_track_res.status_code == 200, f"Parent tracking failed: {p_track_res.text}"
    p_app = p_track_res.json()
    print(f"[OK] Parent tracking status: {p_app.get('status')} | Clarification request: {p_app.get('clarification_request')}")
    assert p_app.get("status") in ("action_required", "clarification_requested"), f"Unexpected status: {p_app.get('status')}"

    # Admin Approves Stage 1
    print(f"\n[TEST 9] Action: Admin grants Stage 1 Approval on {new_app_id}...")
    appr_res = requests.post(f"{BASE_URL}/school/admissions/{new_app_id}/approve", headers=headers, json={
        "confirm": True,
        "note": "Preliminary criteria satisfied. Stage 2 unlocked for document submission."
    })
    assert appr_res.status_code == 200, f"Approve failed: {appr_res.text}"
    print("[OK] Stage 1 Approved successfully.")

    # Parent checks tracking again -> should see approved / stage 2 unlocked
    p_track_after = requests.get(f"{BASE_URL}/parent/admissions/applications/{new_app_id}", headers=parent_headers)
    assert p_track_after.status_code == 200
    p_app_after = p_track_after.json()
    print(f"[OK] Parent tracking status: {p_app_after.get('status')}")
    assert p_app_after.get("status") == "approved", f"Expected approved, got {p_app_after.get('status')}"

    print("\n" + "=" * 60)
    print("ALL 9 E2E ADMISSIONS VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
