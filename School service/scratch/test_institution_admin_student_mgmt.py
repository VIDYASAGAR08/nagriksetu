import requests
import json

base_url = "http://localhost:8001"

def test_full_flow():
    print("==================================================================")
    print("NAGRIKSETU INSTITUTION ADMIN & STUDENT MANAGEMENT TEST SUITE")
    print("==================================================================")

    # 1. Login as K.S Rao
    print("\n--- TEST 1: Academic Administrator Login (K.S Rao) ---")
    login_res = requests.post(f"{base_url}/auth/login", data={
        "username": "rao@edu.in",
        "password": "Rao@1234"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    data = login_res.json()
    token = data["access_token"]
    role = data["role"]
    school_id = data["school_id"]
    print(f"Login successful! Role: {role} | Institution: {school_id}")
    assert role == "academic_admin", f"Expected academic_admin, got {role}"
    assert school_id == "SCH019", f"Expected SCH019, got {school_id}"

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Overview KPI Metrics (7 Cards)
    print("\n--- TEST 2: Authoritative Overview Metrics (7 Real Cards) ---")
    overview_res = requests.get(f"{base_url}/institution/SCH019/dashboard-overview", headers=headers)
    assert overview_res.status_code == 200, f"Overview failed: {overview_res.text}"
    overview = overview_res.json()
    print("Institution Name:", overview.get("institution_name"))
    print("Category:", overview.get("category"))
    print("1. Total Students:", overview.get("total_students"))
    print("2. Total Parents / Guardians:", overview.get("total_parents"))
    print("3. New Admission Applications:", overview.get("new_admission_applications"))
    print("4. Pending Admission Reviews:", overview.get("pending_admission_reviews"))
    print("5. Pending Parent Requests:", overview.get("pending_parent_requests"))
    print("6. Total Academic Programs:", overview.get("total_academic_programs"))
    print("7. Total Sections:", overview.get("total_sections"))

    assert overview.get("total_students") == 2400, f"Expected 2400 students, got {overview.get('total_students')}"
    assert overview.get("total_sections") == 30, f"Expected 30 sections, got {overview.get('total_sections')}"

    # 3. Test Academic Structure
    print("\n--- TEST 3: Academic Structure Discovery ---")
    struct_res = requests.get(f"{base_url}/institution/SCH019/academic-structure", headers=headers)
    assert struct_res.status_code == 200, f"Structure failed: {struct_res.text}"
    struct = struct_res.json()
    print("Category detected:", struct.get("category"))
    print("Standards available:", struct.get("standards"))
    print("Sections available:", struct.get("sections"))
    assert 8 in struct.get("standards", []), "Standard 8 should be available"
    assert "A" in struct.get("sections", []), "Section A should be available"

    # 4. Test Student Query: Standard 8 Section A (Expected: 67 students)
    print("\n--- TEST 4: Query Standard 8 Section A (Expected: 67 students) ---")
    std8_res = requests.get(f"{base_url}/institution/SCH019/students?standard=8&section=A&limit=100", headers=headers)
    assert std8_res.status_code == 200, f"Student query failed: {std8_res.text}"
    std8_data = std8_res.json()
    total_std8 = std8_data.get("total")
    students_list = std8_data.get("students", [])
    print(f"Total students matched in Standard 8 Section A: {total_std8}")
    assert total_std8 == 67, f"Expected exactly 67 students, got {total_std8}"
    assert len(students_list) == 67, f"Expected 67 items returned, got {len(students_list)}"
    
    first_st = students_list[0]
    print(f"First student in roster: {first_st.get('student_name')} ({first_st.get('permanent_student_id')}) - Adm No: {first_st.get('student_id')}")

    # 5. Test Individual Student Profile Dossier
    print("\n--- TEST 5: Comprehensive Student Profile Dossier ---")
    profile_sid = first_st["student_id"]
    prof_res = requests.get(f"{base_url}/institution/SCH019/students/{profile_sid}", headers=headers)
    assert prof_res.status_code == 200, f"Profile failed: {prof_res.text}"
    prof = prof_res.json()
    print("Personal section:", prof.get("personal", {}).get("student_name"))
    print("Academic section:", prof.get("academic", {}).get("standard"), prof.get("academic", {}).get("section"))
    print("Attendance records count:", len(prof.get("attendance_records", [])))
    print("Results records count:", len(prof.get("examination_results", [])))
    print("Guardian info present:", prof.get("parent_guardian") is not None)
    assert prof.get("personal", {}).get("student_name") == first_st.get("student_name")

    # 6. Test Parent Requests Desk
    print("\n--- TEST 6: Parent Update Requests Desk ---")
    req_res = requests.get(f"{base_url}/institution/SCH019/parent-requests", headers=headers)
    assert req_res.status_code == 200, f"Parent requests failed: {req_res.text}"
    req_json = req_res.json()
    req_list = req_json if isinstance(req_json, list) else req_json.get("requests", [])
    print(f"Parent requests returned: {len(req_list)}")

    # 7. Test Parent Directory
    print("\n--- TEST 7: Parent & Guardian Directory ---")
    parent_res = requests.get(f"{base_url}/institution/SCH019/parents", headers=headers)
    assert parent_res.status_code == 200, f"Parents failed: {parent_res.text}"
    parent_json = parent_res.json()
    parent_list = parent_json if isinstance(parent_json, list) else parent_json.get("parents", [])
    print(f"Parents directory records: {len(parent_list)}")

    # 8. Test Cross-Institution Security Isolation (Tenancy boundary)
    print("\n--- TEST 8: Cross-Institution Security Isolation ---")
    cross_res = requests.get(f"{base_url}/institution/SCH001/dashboard-overview", headers=headers)
    print(f"Attempt to query foreign institution SCH001: HTTP {cross_res.status_code} (Expected 403)")
    assert cross_res.status_code == 403, f"Expected 403 Forbidden, got {cross_res.status_code}"

    cross_st = requests.get(f"{base_url}/institution/SCH001/students", headers=headers)
    print(f"Attempt to query foreign students SCH001: HTTP {cross_st.status_code} (Expected 403)")
    assert cross_st.status_code == 403, f"Expected 403 Forbidden, got {cross_st.status_code}"

    print("\n==================================================================")
    print("ALL 8 END-TO-END VERIFICATION TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================================")

if __name__ == "__main__":
    test_full_flow()
