import os
import sys
import sqlite3
import json
import urllib.request
import urllib.parse
from auth import create_access_token

BASE_URL = "http://localhost:8000"
DB_PATH = "/app/data/nagriksetu.db" if os.path.exists("/app/data/nagriksetu.db") else "C:/Users/callm/nagriksetu/backend/data/nagriksetu.db"

def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def test_e2e():
    print("=================================================================")
    print("NAGRIKSETU ACADEMIC CLASSIFICATION END-TO-END VALIDATION")
    print("=================================================================")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 1. Inspect target sample students in DB
    print("\n--- 1. Selecting Representative Test Students from DB ---")
    
    # School student
    school_st = conn.execute("""
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, s.standard,
               e.curriculum_or_board, e.program_id
        FROM students s
        JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
        WHERE s.school_id = 'SCH001' AND s.standard = 8
        LIMIT 1
    """).fetchone()
    print(f"School Sample (SCH001): {school_st['student_id']} - {school_st['student_name']} (Std {school_st['standard']}, Board: {school_st['curriculum_or_board']})")

    # 1st PUC PCMB student
    puc1_pcmb = conn.execute("""
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, s.standard,
               e.puc_year, e.stream, e.subject_combination, e.curriculum_or_board
        FROM students s
        JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
        WHERE s.school_id = 'SCH011' AND e.puc_year = '1st PUC' AND e.subject_combination = 'PCMB'
        LIMIT 1
    """).fetchone()
    print(f"1st PUC PCMB Sample (SCH011): {puc1_pcmb['student_id']} - {puc1_pcmb['student_name']} ({puc1_pcmb['puc_year']}, Stream: {puc1_pcmb['stream']}, Combo: {puc1_pcmb['subject_combination']})")

    # 2nd PUC PCMC student
    puc2_pcmc = conn.execute("""
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, s.standard,
               e.puc_year, e.stream, e.subject_combination, e.curriculum_or_board
        FROM students s
        JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
        WHERE s.school_id = 'SCH012' AND e.puc_year = '2nd PUC' AND e.subject_combination = 'PCMC'
        LIMIT 1
    """).fetchone()
    print(f"2nd PUC PCMC Sample (SCH012): {puc2_pcmc['student_id']} - {puc2_pcmc['student_name']} ({puc2_pcmc['puc_year']}, Stream: {puc2_pcmc['stream']}, Combo: {puc2_pcmc['subject_combination']})")

    # 1st PUC Commerce student
    puc1_comm = conn.execute("""
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, s.standard,
               e.puc_year, e.stream, e.subject_combination, e.curriculum_or_board
        FROM students s
        JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
        WHERE s.school_id = 'SCH013' AND e.puc_year = '1st PUC' AND e.stream = 'Commerce'
        LIMIT 1
    """).fetchone()
    print(f"1st PUC Commerce Sample (SCH013): {puc1_comm['student_id']} - {puc1_comm['student_name']} ({puc1_comm['puc_year']}, Stream: {puc1_comm['stream']}, Combo: {puc1_comm['subject_combination']})")

    # Engineering student
    eng_st = conn.execute("""
        SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, s.standard,
               e.degree, e.branch, e.department, e.semester
        FROM students s
        JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
        WHERE s.school_id = 'COL003'
        LIMIT 1
    """).fetchone()
    print(f"Engineering Sample (COL003 BMSCE): {eng_st['student_id']} - {eng_st['student_name']} ({eng_st['degree']} {eng_st['branch']}, Sem {eng_st['semester']})")

    # 2. Test Parent Student Lookup API for Each Category
    print("\n--- 2. Testing Parent Student Lookup API (/parent/lookup-by-student-id) ---")
    parent_user = conn.execute("SELECT user_id, email, role FROM users WHERE role = 'parent' LIMIT 1").fetchone()
    parent_token = create_access_token({"user_id": parent_user["user_id"], "role": parent_user["role"]})
    parent_headers = {"Authorization": f"Bearer {parent_token}"}

    test_cases = [
        ("School Student", school_st['student_id'], "School", "Standard 8"),
        ("1st PUC PCMB Student", puc1_pcmb['student_id'], "PU College", "1st PUC"),
        ("2nd PUC PCMC Student", puc2_pcmc['student_id'], "PU College", "2nd PUC"),
        ("1st PUC Commerce Student", puc1_comm['student_id'], "PU College", "1st PUC"),
        ("Engineering Student", eng_st['student_id'], "Engineering College", "B.E."),
    ]

    for label, sid, expected_tier, expected_val in test_cases:
        url = f"{BASE_URL}/parent/lookup-by-student-id?student_id={urllib.parse.quote(sid)}"
        status, data = http_get(url, headers=parent_headers)
        assert status == 200, f"Failed lookup for {sid}: {status} {data}"
        
        tier = data.get("institution_tier")
        print(f"\n[PASS] Lookup: {label} (ID: {sid})")
        print(f"       Institution: {data.get('institution_name')} ({data.get('institution_id')})")
        print(f"       Tier: {tier} (Expected: {expected_tier})")
        
        assert tier == expected_tier, f"Tier mismatch for {sid}: got {tier}, expected {expected_tier}"
        
        if tier == "School":
            print(f"       Class/Standard: {data.get('class_or_standard')}")
            print(f"       Board: {data.get('board')}")
            assert data.get("board") == "Karnataka State Board (KSEEB)"
        elif tier == "PU College":
            print(f"       PUC Year: {data.get('puc_year')}")
            print(f"       Stream: {data.get('stream')}")
            print(f"       Subject Combination: {data.get('subject_combination')}")
            print(f"       Board: {data.get('board')}")
            assert data.get("puc_year") == expected_val
            assert data.get("stream") in ["Science", "Commerce", "Arts / Humanities"]
            assert data.get("board") == "Department of Pre-University Education (DPUE)"
        elif tier == "Engineering College":
            print(f"       Degree: {data.get('degree')}")
            print(f"       Branch: {data.get('branch')}")
            print(f"       Department: {data.get('department')}")
            print(f"       Semester: {data.get('semester')}")
            assert "B.E." in data.get("degree")
            assert data.get("branch") == "Civil Engineering"

    # 3. Test Institution Administrator Dossier API
    print("\n--- 3. Testing Institution Administrator Dossier Academic Info ---")
    admin_samples = [
        ("SCH001", school_st['student_id']),
        ("SCH011", puc1_pcmb['student_id']),
        ("COL003", eng_st['student_id']),
    ]
    
    plat_admin = conn.execute("SELECT user_id, email, role FROM users WHERE role = 'platform_admin' LIMIT 1").fetchone()

    for sch_id, st_id in admin_samples:
        inst_admin = conn.execute("SELECT user_id, email, role, school_id FROM users WHERE school_id = ? AND role IN ('school_admin', 'academic_admin') LIMIT 1", (sch_id,)).fetchone()
        user_to_use = inst_admin or plat_admin
        token = create_access_token({"user_id": user_to_use["user_id"], "role": user_to_use["role"], "school_id": sch_id})
        url = f"{BASE_URL}/institution/{sch_id}/students/{st_id}"
        status, dossier = http_get(url, headers={"Authorization": f"Bearer {token}"})
        assert status == 200, f"Failed dossier for {st_id}: {status} {dossier}"
        acad = dossier.get("academic_info") or dossier.get("academic") or {}
        print(f"\n[PASS] Dossier: Institution {sch_id} - Student {st_id}")
        print(f"       Name: {dossier.get('personal', {}).get('student_name')}")
        print(f"       Tier: {acad.get('institution_tier')}")
        print(f"       Class/Programme: {acad.get('class_or_standard') or acad.get('programme') or acad.get('degree')}")
        if acad.get("puc_year"):
            print(f"       PUC Year: {acad.get('puc_year')}, Stream: {acad.get('stream')}, Combo: {acad.get('subject_combination')}")
        if acad.get("degree"):
            print(f"       Degree: {acad.get('degree')}, Branch: {acad.get('branch')}, Semester: {acad.get('semester')}")

    print("\n=================================================================")
    print("ALL ACADEMIC CLASSIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    test_e2e()
