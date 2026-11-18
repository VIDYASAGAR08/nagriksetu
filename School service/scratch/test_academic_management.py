# -*- coding: utf-8 -*-
import requests
import json
import sqlite3
import sys

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def print_step(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def login(email_or_user, password):
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email_or_user, "password": password})
    if res.status_code != 200:
        raise Exception(f"Login failed for {email_or_user}: {res.status_code} {res.text}")
    return res.json()["access_token"]

def student_login(permanent_student_id, password):
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": permanent_student_id, "password": password})
    if res.status_code != 200:
        raise Exception(f"Student login failed for {permanent_student_id}: {res.status_code} {res.text}")
    return res.json()["access_token"]

def run_tests():
    print_step("PHASE 12: ACADEMIC MANAGEMENT & STUDENT PERFORMANCE SYSTEM E2E AUDIT")

    # =========================================================================
    # 1. SCHOOL TIER: SCH001 (Government Model School, Mandya)
    # =========================================================================
    print_step("1. TESTING SCHOOL TIER: SCH001")

    # 1.1 Staff Login
    staff_token = login("staff.sch001@example.com", "Staff@NagrikSetu2026!")
    staff_headers = {"Authorization": f"Bearer {staff_token}"}
    print("Staff login successful for staff.sch001@example.com")

    # 1.2 Admin Login
    admin_token = login("admin.sch001@example.com", "Admin@NagrikSetu2026!")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin login successful for admin.sch001@example.com")

    # 1.3 Create Examination
    exam_payload = {
        "institution_id": "SCH001",
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "exam_date": "2026-11-15",
        "standard": 5,
        "description": "State syllabus midterm assessment for Class 5"
    }
    r = requests.post(f"{BASE_URL}/academic/examinations", json=exam_payload, headers=staff_headers)
    assert r.status_code == 201, f"Create exam failed: {r.text}"
    exam_data = r.json()
    exam_id = exam_data["exam_id"]
    print(f"Created examination: {exam_data['exam_name']} (ID: {exam_id})")

    # 1.4 Get enrolled students in SCH001 Class 5-A
    r = requests.get(f"{BASE_URL}/schools/SCH001/students?standard=5&section=A&limit=5", headers=staff_headers)
    assert r.status_code == 200, f"Get students failed: {r.text}"
    res_data = r.json()
    students = res_data if isinstance(res_data, list) else res_data.get("students", [])
    assert len(students) >= 3, f"Expected at least 3 students, got {len(students)}"
    target_student_1 = students[0]["permanent_student_id"]
    target_student_2 = students[1]["permanent_student_id"]
    target_student_3 = students[2]["permanent_student_id"]
    print(f"Target students for attendance & marks: {target_student_1}, {target_student_2}, {target_student_3}")

    # 1.5 Record Batch Attendance across 3 instructional dates
    dates_and_statuses = [
        ("2026-11-01", [
            {"permanent_student_id": target_student_1, "status": "present", "remarks": "On time"},
            {"permanent_student_id": target_student_2, "status": "present", "remarks": "On time"},
            {"permanent_student_id": target_student_3, "status": "absent", "remarks": "Unexcused"}
        ]),
        ("2026-11-02", [
            {"permanent_student_id": target_student_1, "status": "present", "remarks": "Active in Kannada class"},
            {"permanent_student_id": target_student_2, "status": "leave", "remarks": "Medical leave approved"},
            {"permanent_student_id": target_student_3, "status": "present", "remarks": "Present"}
        ]),
        ("2026-11-03", [
            {"permanent_student_id": target_student_1, "status": "present", "remarks": "Lab session"},
            {"permanent_student_id": target_student_2, "status": "present", "remarks": "Lab session"},
            {"permanent_student_id": target_student_3, "status": "present", "remarks": "Lab session"}
        ]),
    ]

    for att_date, records in dates_and_statuses:
        att_payload = {
            "institution_id": "SCH001",
            "attendance_date": att_date,
            "subject_name": "General Instruction",
            "records": records
        }
        r = requests.post(f"{BASE_URL}/academic/attendance/batch", json=att_payload, headers=staff_headers)
        assert r.status_code == 201, f"Record attendance failed for {att_date}: {r.text}"
        print(f"Recorded attendance for {att_date}: {r.json()['records_count']} students saved.")

    # 1.6 Verify Attendance Summary for Student 1 (3 days total, 3 present -> 100.0%)
    r = requests.get(f"{BASE_URL}/academic/attendance/summary/{target_student_1}", headers=staff_headers)
    assert r.status_code == 200, f"Attendance summary failed: {r.text}"
    att_sum = r.json()
    assert att_sum["total_working_days"] == 3, f"Expected 3 working days, got {att_sum['total_working_days']}"
    assert att_sum["present_days"] == 3, f"Expected 3 present days, got {att_sum['present_days']}"
    assert att_sum["attendance_percentage"] == 100.0, f"Expected 100.0%, got {att_sum['attendance_percentage']}"
    print(f"Verified Attendance Summary for {target_student_1}: {att_sum['present_days']}/{att_sum['total_working_days']} days ({att_sum['attendance_percentage']}%)")

    # 1.7 Verify Attendance Summary for Student 2 (3 days total, 2 present, 1 leave -> 66.7%)
    r = requests.get(f"{BASE_URL}/academic/attendance/summary/{target_student_2}", headers=staff_headers)
    assert r.status_code == 200
    att_sum2 = r.json()
    assert att_sum2["total_working_days"] == 3
    assert att_sum2["present_days"] == 2
    assert att_sum2["leave_days"] == 1
    assert att_sum2["attendance_percentage"] == 66.7
    print(f"Verified Attendance Summary for {target_student_2}: {att_sum2['present_days']}/{att_sum2['total_working_days']} days ({att_sum2['attendance_percentage']}%)")

    # 1.8 Record Batch Academic Results (Kannada, Mathematics, English)
    # Clean previous run's test results for this exam if any
    conn_cln = sqlite3.connect(DB_PATH)
    conn_cln.execute("DELETE FROM academic_result_audits WHERE result_id IN (SELECT result_id FROM academic_results WHERE exam_name='Midterm Examination 2026')")
    conn_cln.execute("DELETE FROM academic_results WHERE exam_name='Midterm Examination 2026'")
    conn_cln.commit()
    conn_cln.close()

    # Subject 1: Kannada (Max: 100)
    kannada_payload = {
        "institution_id": "SCH001",
        "exam_id": exam_id,
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "subject_name": "Kannada",
        "maximum_marks": 100.0,
        "records": [
            {"permanent_student_id": target_student_1, "marks_obtained": 88.0},
            {"permanent_student_id": target_student_2, "marks_obtained": 74.0},
            {"permanent_student_id": target_student_3, "marks_obtained": 91.0},
        ]
    }
    r = requests.post(f"{BASE_URL}/academic/results/batch", json=kannada_payload, headers=staff_headers)
    assert r.status_code == 201, f"Record Kannada results failed: {r.text}"
    print(f"Recorded Kannada marks for {r.json()['processed_count']} students")

    # Subject 2: Mathematics (Max: 100)
    maths_payload = {
        "institution_id": "SCH001",
        "exam_id": exam_id,
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "subject_name": "Mathematics",
        "maximum_marks": 100.0,
        "records": [
            {"permanent_student_id": target_student_1, "marks_obtained": 94.0},
            {"permanent_student_id": target_student_2, "marks_obtained": 62.0},
            {"permanent_student_id": target_student_3, "marks_obtained": 82.0},
        ]
    }
    r = requests.post(f"{BASE_URL}/academic/results/batch", json=maths_payload, headers=staff_headers)
    assert r.status_code == 201

    # Subject 3: English (Max: 100) - Student 1 gets 72.0 initially
    english_payload = {
        "institution_id": "SCH001",
        "exam_id": exam_id,
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "subject_name": "English",
        "maximum_marks": 100.0,
        "records": [
            {"permanent_student_id": target_student_1, "marks_obtained": 72.0},
            {"permanent_student_id": target_student_2, "marks_obtained": 80.0},
            {"permanent_student_id": target_student_3, "marks_obtained": 68.0},
        ]
    }
    r = requests.post(f"{BASE_URL}/academic/results/batch", json=english_payload, headers=staff_headers)
    assert r.status_code == 201

    # 1.9 Check initial grade for Student 1 in English (72 -> B+)
    r = requests.get(f"{BASE_URL}/academic/results?institution_id=SCH001&permanent_student_id={target_student_1}&subject_name=English", headers=staff_headers)
    assert r.status_code == 200
    res_json = r.json()
    res_list = res_json if isinstance(res_json, list) else res_json.get("results", [])
    assert len(res_list) == 1
    eng_res = res_list[0]
    eng_result_id = eng_res["result_id"]
    assert eng_res["marks_obtained"] == 72.0
    assert eng_res["grade"] == "B+"
    print(f"Initial English mark for {target_student_1}: 72.0, Grade: B+")

    # 1.10 Perform Mark Correction with Audit Trail
    update_english_payload = {
        "institution_id": "SCH001",
        "exam_id": exam_id,
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "subject_name": "English",
        "maximum_marks": 100.0,
        "records": [
            {
                "permanent_student_id": target_student_1,
                "marks_obtained": 85.0,
                "reason_for_change": "Revaluation of essay & comprehension section"
            }
        ]
    }
    r = requests.post(f"{BASE_URL}/academic/results/batch", json=update_english_payload, headers=staff_headers)
    assert r.status_code == 201

    # Verify updated score & grade (85 -> A)
    r = requests.get(f"{BASE_URL}/academic/results?institution_id=SCH001&permanent_student_id={target_student_1}&subject_name=English", headers=staff_headers)
    assert r.status_code == 200
    res_json2 = r.json()
    res_list2 = res_json2 if isinstance(res_json2, list) else res_json2.get("results", [])
    updated_eng = res_list2[0]
    assert updated_eng["marks_obtained"] == 85.0
    assert updated_eng["grade"] == "A"
    print(f"Updated English mark for {target_student_1}: 85.0, Grade: A")

    # 1.11 Verify Audit Trail Record in academic_result_audits
    r = requests.get(f"{BASE_URL}/academic/results/audits/{eng_result_id}", headers=staff_headers)
    assert r.status_code == 200
    audits = r.json()["audits"]
    assert len(audits) >= 1, f"Expected at least 1 audit entry, got {len(audits)}"
    latest_audit = audits[0]
    assert latest_audit["previous_marks"] == 72.0
    assert latest_audit["new_marks"] == 85.0
    assert "Revaluation" in latest_audit["reason_for_change"]
    print(f"Audit log verified: previous_marks={latest_audit['previous_marks']}, new_marks={latest_audit['new_marks']}, reason='{latest_audit['reason_for_change']}'")

    # 1.12 Post Institution Announcement
    ann_payload = {
        "institution_id": "SCH001",
        "title": "Midterm Examination Results Published",
        "content": "Official midterm assessment scores and subject evaluation cards are now available on the student and parent portals.",
        "target_audience": "all",
        "published_date": "2026-11-03"
    }
    r = requests.post(f"{BASE_URL}/academic/announcements", json=ann_payload, headers=admin_headers)
    assert r.status_code == 201
    print("Institution announcement published by School Admin.")

    # 1.13 Student Academic Performance API Verification
    r = requests.get(f"{BASE_URL}/academic/performance/{target_student_1}", headers=staff_headers)
    assert r.status_code == 200
    perf = r.json()
    assert perf["attendance_summary"]["attendance_percentage"] == 100.0
    assert len(perf["academic_results"]) == 3
    assert len(perf["subject_performance"]) == 3
    assert len(perf["academic_progress"]) >= 1
    assert len(perf["announcements"]) >= 1
    print(f"Student Academic Performance aggregated successfully: {len(perf['academic_results'])} results, {len(perf['announcements'])} announcements.")

    # =========================================================================
    # 2. PU COLLEGE TIER: SCH011 (Government PU College for Boys, Malleshwaram)
    # =========================================================================
    print_step("2. TESTING PU COLLEGE TIER: SCH011")

    pu_admin_token = login("newadmin.sch011@example.com", "Admin@NagrikSetu2026!")
    pu_headers = {"Authorization": f"Bearer {pu_admin_token}"}

    # Create PUC Exam
    pu_exam_payload = {
        "institution_id": "SCH011",
        "exam_name": "PUC 1st Year Midterm Assessment",
        "academic_year": "2025-26",
        "exam_date": "2026-11-20",
        "standard": 11,
        "description": "Pre-University board preparation midterm evaluation"
    }
    r = requests.post(f"{BASE_URL}/academic/examinations", json=pu_exam_payload, headers=pu_headers)
    assert r.status_code == 201
    pu_exam_id = r.json()["exam_id"]
    print(f"Created PU College exam: {r.json()['exam_name']} (ID: {pu_exam_id})")

    # Get PU students (Class 11-A)
    r = requests.get(f"{BASE_URL}/schools/SCH011/students?standard=11&section=A&limit=3", headers=pu_headers)
    assert r.status_code == 200
    pu_res = r.json()
    pu_students = pu_res if isinstance(pu_res, list) else pu_res.get("students", [])
    pu_st_1 = pu_students[0]["permanent_student_id"]
    pu_st_2 = pu_students[1]["permanent_student_id"]

    # Subject-wise attendance: Physics
    pu_att_payload = {
        "institution_id": "SCH011",
        "attendance_date": "2026-11-03",
        "subject_name": "Physics",
        "records": [
            {"permanent_student_id": pu_st_1, "status": "present", "remarks": "Practical Lab A"},
            {"permanent_student_id": pu_st_2, "status": "absent", "remarks": "Sick"}
        ]
    }
    r = requests.post(f"{BASE_URL}/academic/attendance/batch", json=pu_att_payload, headers=pu_headers)
    assert r.status_code == 201
    print("Recorded subject-wise attendance for PU College (Physics)")

    # Record PUC marks (Physics, Chemistry)
    pu_marks_payload = {
        "institution_id": "SCH011",
        "exam_id": pu_exam_id,
        "exam_name": "PUC 1st Year Midterm Assessment",
        "academic_year": "2025-26",
        "subject_name": "Physics",
        "maximum_marks": 70.0,
        "records": [
            {"permanent_student_id": pu_st_1, "marks_obtained": 65.0}, # 92.9% -> A+
            {"permanent_student_id": pu_st_2, "marks_obtained": 52.0}, # 74.3% -> B+
        ]
    }
    r = requests.post(f"{BASE_URL}/academic/results/batch", json=pu_marks_payload, headers=pu_headers)
    assert r.status_code == 201
    print("Recorded PU College Physics marks.")

    # Post PU Announcement
    r = requests.post(f"{BASE_URL}/academic/announcements", json={
        "institution_id": "SCH011",
        "title": "PUC Annual Practical Examination Schedule",
        "content": "All science stream students must submit completed laboratory journals before November 30.",
        "target_audience": "students",
        "published_date": "2026-11-03"
    }, headers=pu_headers)
    assert r.status_code == 201
    print("PU College announcement posted successfully.")

    # =========================================================================
    # 3. DEGREE COLLEGE TIER: COL001 (Govt First Grade College, K.R. Puram)
    # =========================================================================
    print_step("3. TESTING DEGREE COLLEGE TIER: COL001")

    deg_admin_token = login("admin.col001@example.com", "Admin@NagrikSetu2026!")
    deg_headers = {"Authorization": f"Bearer {deg_admin_token}"}

    # Create Degree Exam
    deg_exam_payload = {
        "institution_id": "COL001",
        "exam_name": "Semester 1 Internal Assessment (Degree)",
        "academic_year": "2025-26",
        "exam_date": "2026-11-25",
        "description": "Continuous internal evaluation for undergraduate programmes"
    }
    r = requests.post(f"{BASE_URL}/academic/examinations", json=deg_exam_payload, headers=deg_headers)
    assert r.status_code == 201
    print(f"Created Degree College examination: {r.json()['exam_name']}")

    # Post Degree College Announcement
    r = requests.post(f"{BASE_URL}/academic/announcements", json={
        "institution_id": "COL001",
        "title": "Undergraduate Internal Evaluation Dates",
        "content": "Internal assessment schedule for B.A., B.Sc., and B.Com semester examinations has been notified on the college noticeboard.",
        "target_audience": "all",
        "published_date": "2026-11-03"
    }, headers=deg_headers)
    assert r.status_code == 201
    print("Degree College announcement posted successfully.")

    # Cross-institution access protection: COL001 cannot record marks for SCH001
    cross_hack = {
        "institution_id": "SCH001",
        "exam_name": "Midterm Examination 2026",
        "academic_year": "2025-26",
        "subject_name": "Social Science",
        "maximum_marks": 100.0,
        "records": [{"permanent_student_id": target_student_1, "marks_obtained": 99.0}]
    }
    r = requests.post(f"{BASE_URL}/academic/results/batch", json=cross_hack, headers=deg_headers)
    assert r.status_code == 403, f"Expected 403 for cross-institution breach, got {r.status_code}"
    print("Verified cross-institution access rejection (COL001 admin rejected from SCH001 records: 403 Forbidden).")

    # =========================================================================
    # 4. UNIVERSITY TIER: COL010 (Visvesvaraya Technological University)
    # =========================================================================
    print_step("4. TESTING UNIVERSITY TIER: COL010")

    uni_admin_token = login("admin.col010@example.com", "Admin@NagrikSetu2026!")
    uni_headers = {"Authorization": f"Bearer {uni_admin_token}"}

    # Schedule University Exam
    uni_exam_payload = {
        "institution_id": "COL010",
        "exam_name": "End-Semester University Examination 2026",
        "academic_year": "2025-26",
        "exam_date": "2026-12-10",
        "description": "University central theory and practical examinations"
    }
    r = requests.post(f"{BASE_URL}/academic/examinations", json=uni_exam_payload, headers=uni_headers)
    assert r.status_code == 201
    print(f"Created University examination: {r.json()['exam_name']}")

    # Post University Announcement
    r = requests.post(f"{BASE_URL}/academic/announcements", json={
        "institution_id": "COL010",
        "title": "University Convocation & Grade Card Distribution",
        "content": "Official provisional degree certificates and semester grade sheets will be distributed through regional centres.",
        "target_audience": "all",
        "published_date": "2026-11-03"
    }, headers=uni_headers)
    assert r.status_code == 201
    print("University announcement posted successfully.")

    # =========================================================================
    # 5. DATA PRIVACY & ACCESS CONTROL ENFORCEMENT
    # =========================================================================
    print_step("5. TESTING DATA PRIVACY & ACCESS CONTROL")

    # 5.1 Parent login & child viewing
    parent_token = login("9876543210", "Str0ngPass!2026")
    parent_headers = {"Authorization": f"Bearer {parent_token}"}

    # Ensure target_student_1 is linked to parent in student_guardians for test verification
    conn = sqlite3.connect(DB_PATH)
    parent_user = conn.execute("SELECT user_id FROM users WHERE phone='9876543210'").fetchone()
    if parent_user:
        guardian_row = conn.execute("SELECT guardian_id FROM guardians WHERE user_id=?", (parent_user[0],)).fetchone()
        if guardian_row:
            gid = guardian_row[0]
            import uuid
            conn.execute("INSERT OR IGNORE INTO student_guardians (student_guardian_id, permanent_student_id, guardian_id, can_view_records, can_request_updates, is_verified) VALUES (?, ?, ?, 1, 1, 1)", (str(uuid.uuid4()), target_student_1, gid))
            conn.commit()
    conn.close()

    # Parent requests records for linked child
    r = requests.get(f"{BASE_URL}/parent/children/{target_student_1}/records", headers=parent_headers)
    assert r.status_code == 200, f"Parent viewing linked child failed: {r.text}"
    child_records = r.json()
    assert child_records["student"]["permanent_student_id"] == target_student_1
    assert child_records["attendance_summary"]["attendance_percentage"] == 100.0
    assert len(child_records["academic_results"]) == 3
    print("Verified parent can view linked child's attendance and academic results.")

    # Parent tries to view unlinked student (e.g. SCH001050)
    r = requests.get(f"{BASE_URL}/parent/children/SCH001050/records", headers=parent_headers)
    assert r.status_code in (403, 404), f"Expected 403 or 404 for unlinked student, got {r.status_code}"
    print("Verified parent cannot view unlinked student's records (Access rejected: 403/404 enforced).")

    # Parent cannot write attendance or results
    r = requests.post(f"{BASE_URL}/academic/attendance/batch", json={"institution_id": "SCH001", "attendance_date": "2026-11-03", "records": []}, headers=parent_headers)
    assert r.status_code == 403
    r = requests.post(f"{BASE_URL}/academic/results/batch", json={"institution_id": "SCH001", "exam_name": "Test", "records": []}, headers=parent_headers)
    assert r.status_code == 403
    print("Verified parent account cannot write or alter attendance/results (403 Forbidden).")

    # 5.2 Student login & verification
    # Setup test student password if needed
    conn = sqlite3.connect(DB_PATH)
    sample_hash = conn.execute("SELECT password_hash FROM users WHERE role='student' AND password_hash IS NOT NULL LIMIT 1").fetchone()
    hashed_pwd = sample_hash[0] if sample_hash else "$argon2id$v=19$m=65536,t=3,p=4$AzpS6A6eMXxU27GOaV4+8Q$ZJQbIu+CH6fsBxxu29OWyHTn/E12+bUZHWv95fRhy3M"
    stu_row = conn.execute("SELECT student_id FROM students WHERE permanent_student_id=?", (target_student_1,)).fetchone()
    st_code = stu_row[0] if stu_row else target_student_1
    conn.execute("INSERT OR REPLACE INTO users (user_id, email, password_hash, role, full_name, permanent_student_id, student_id, is_active, created_at) VALUES ('USR_TEST_ST1', 'student1@nagriksetu.gov', ?, 'student', 'Test Student 1', ?, ?, 1, datetime('now'))", (hashed_pwd, target_student_1, st_code))
    conn.commit()
    conn.close()

    st_token = student_login(st_code, "Password@2026!")
    st_headers = {"Authorization": f"Bearer {st_token}"}

    r = requests.get(f"{BASE_URL}/student/profile", headers=st_headers)
    assert r.status_code == 200
    st_profile = r.json()
    assert st_profile["student"]["permanent_student_id"] == target_student_1
    assert st_profile["academic_performance"]["attendance_summary"]["attendance_percentage"] == 100.0
    assert len(st_profile["academic_performance"]["academic_results"]) == 3
    print(f"Verified Student Dashboard: Student views own 100.0% attendance, 3 exam results, and progress.")

    # Student cannot modify attendance or marks
    r = requests.post(f"{BASE_URL}/academic/attendance/batch", json={"institution_id": "SCH001", "attendance_date": "2026-11-03", "records": []}, headers=st_headers)
    assert r.status_code == 403
    r = requests.post(f"{BASE_URL}/academic/results/batch", json={"institution_id": "SCH001", "exam_name": "Test", "records": []}, headers=st_headers)
    assert r.status_code == 403
    print("Verified student cannot modify attendance or marks (403 Forbidden).")

    # Student cannot view another student's academic performance
    r = requests.get(f"{BASE_URL}/academic/performance/{target_student_2}", headers=st_headers)
    assert r.status_code == 403, f"Expected 403 Forbidden for cross-student access, got {r.status_code}"
    print("Verified student cannot access other students' performance records (403 Forbidden enforced).")

    # =========================================================================
    # 6. DATABASE INTEGRITY CHECK
    # =========================================================================
    print_step("6. VERIFYING DATABASE INTEGRITY")
    conn = sqlite3.connect(DB_PATH)
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk_check = conn.execute("PRAGMA foreign_key_check").fetchall()
    total_students = conn.execute("SELECT count(*) FROM students").fetchone()[0]
    total_schools = conn.execute("SELECT count(*) FROM schools").fetchone()[0]
    conn.close()

    assert integrity == "ok", f"Integrity check failed: {integrity}"
    assert len(fk_check) == 0, f"Foreign key check violations: {fk_check}"
    assert total_students >= 30001, f"Expected at least 30001 students, found {total_students}"
    assert total_schools == 30, f"Expected 30 institutions, found {total_schools}"
    print(f"Database Integrity: OK (30 institutions, {total_students} students, 0 FK violations).")

    print_step("ALL ACADEMIC MANAGEMENT E2E TESTS PASSED SUCCESSFULLY! (100% SUCCESS)")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nTEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
