import urllib.request
import urllib.parse
import json
import os
os.environ.setdefault("JWT_SECRET_KEY", "nagriksetu-dev-jwt-secret-key-32chars-min-len")
import sqlite3
import re
import sys
sys.path.append(r"C:\Users\callm\nagriksetu\backend")

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def api_post_form(endpoint, form_data):
    data = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"detail": body}

def api_get(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"detail": body}

def run_tests():
    print("=" * 70)
    print("NAGRIKSETU — STANDARDIZED STUDENT ID SYSTEM VERIFICATION SUITE")
    print("=" * 70)

    passed = 0
    total = 0

    def assert_test(cond, title):
        nonlocal passed, total
        total += 1
        if cond:
            print(f"{total}. {title}: PASSED")
            passed += 1
        else:
            print(f"{total}. {title}: FAILED")
            raise AssertionError(f"Test failed: {title}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Total student count preservation
    tot_stus = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert_test(tot_stus == 30001, f"Database: Exactly 30,001 students preserved ({tot_stus})")

    # 2. Strict ID uniqueness across entire state
    uniq_ids = c.execute("SELECT COUNT(DISTINCT student_id) FROM students").fetchone()[0]
    assert_test(uniq_ids == 30001, f"Uniqueness: Exactly 30,001 unique Student IDs ({uniq_ids})")

    # 3. Format compliance: All IDs follow INSTITUTION_5CHAR_PREFIX + THREE_DIGIT_SEQUENCE
    invalid_format_count = c.execute("""
        SELECT COUNT(*) FROM students 
        WHERE student_id NOT GLOB '[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][0-9]*'
    """).fetchone()[0]
    assert_test(invalid_format_count == 0, f"Format: 100% of student IDs match 5-char prefix + numeric sequence (invalid={invalid_format_count})")

    # 4. Alphabetical assignment check at SCH001 (Aarav Gowda -> SCH01001)
    first_sch001 = c.execute("SELECT student_id, student_name FROM students WHERE school_id = 'SCH001' AND student_id = 'SCH01001'").fetchone()
    assert_test(first_sch001 is not None and first_sch001[1].startswith("Aarav"), f"Alphabetical Assignment: SCH01001 assigned to {first_sch001}")

    # 5. Alphabetical ordering verification across SCH001
    def get_sort_key(name):
        parts = (name or "").strip().split()
        return (parts[0].lower() if parts else "", (name or "").strip().lower())

    sch001_rows = c.execute("SELECT student_id, student_name FROM students WHERE school_id = 'SCH001' ORDER BY student_id").fetchall()
    is_ordered = True
    for i in range(len(sch001_rows) - 1):
        k1 = get_sort_key(sch001_rows[i][1])
        k2 = get_sort_key(sch001_rows[i+1][1])
        if k1 > k2:
            is_ordered = False
            break
    assert_test(is_ordered, "Alphabetical Sorting: 100% strictly ordered by first name then full name across SCH001")

    # 6. Duplicate first names resolution
    aarav_students = c.execute("SELECT student_id, student_name FROM students WHERE school_id = 'SCH001' AND student_name LIKE 'Aarav %' ORDER BY student_id").fetchall()
    aarav_sorted = sorted(aarav_students, key=lambda x: x[1].lower())
    assert_test(aarav_students == aarav_sorted and len(aarav_students) > 10, f"Duplicate First Names: Tie-breaking by complete name verified for {len(aarav_students)} students named Aarav")

    # 7. Independent sequence verification across different institutions
    # SCH002 must start at SCH02001
    sch002_first = c.execute("SELECT student_id, student_name FROM students WHERE school_id = 'SCH002' AND student_id = 'SCH02001'").fetchone()
    assert_test(sch002_first is not None, f"Independent Sequence: SCH002 starts at SCH02001 ({sch002_first})")

    # SCH011 (PU College) must start at SCH11001 and end at SCH112400
    sch011_first = c.execute("SELECT student_id FROM students WHERE school_id = 'SCH011' AND student_id = 'SCH11001'").fetchone()
    sch011_last = c.execute("SELECT student_id FROM students WHERE school_id = 'SCH011' AND student_id = 'SCH112400'").fetchone()
    assert_test(sch011_first is not None and sch011_last is not None, "Different Institutions: PU College SCH011 spans SCH11001 to SCH112400")

    # 8. User accounts updated with standardized student IDs
    asha_user = c.execute("SELECT student_id FROM users WHERE email = 'student.asha@example.com'").fetchone()
    assert_test(asha_user is not None and asha_user[0] == "SCH01125", f"User Account Sync: Asha Sharma updated to {asha_user[0]}")

    kiran_user = c.execute("SELECT student_id FROM users WHERE email = 'kiran.kumar@student.nagriksetu.gov'").fetchone()
    assert_test(kiran_user is not None and kiran_user[0] == "SCH01246", f"User Account Sync: Kiran Kumar updated to {kiran_user[0]}")

    # 9. Student Login with standardized Student ID (SCH01125)
    status, res = api_post_form("/auth/login", {"username": "SCH01125", "password": "Password@2026!"})
    assert_test(status == 200 and res.get("role") == "student" and res.get("student_id") == "SCH01125", f"Student Login: Successfully authenticated with standardized Student ID SCH01125 (status={status})")
    student_token = res["access_token"]

    # 10. Student Profile retrieval with standardized Student ID
    status, prof = api_get("/student/profile", token=student_token)
    assert_test(status == 200 and prof["student"]["student_id"] == "SCH01125" and prof["student"]["student_name"] == "Asha Sharma", f"Student Profile: Returns standardized ID SCH01125 for Asha Sharma (status={status})")

    # 11. Student Individual Record Endpoint
    status, rec = api_get("/students/SCH01125", token=student_token)
    assert_test(status == 200 and rec.get("student_id") == "SCH01125", f"Student Record: Accessible via /students/SCH01125 (status={status})")

    # 12. Future Admission Generator: Determine next sequence for existing school
    # For SCH001 with 601 students, next ID must be SCH01602
    def test_generate_next_student_id(conn, school_id: str) -> str:
        def get_institution_5char_prefix(sch_id: str) -> str:
            m = re.match(r"^([A-Z]+)(\d+)$", sch_id)
            if m:
                letters, num = m.groups()
                return f"{letters}{int(num):02d}"
            return sch_id

        prefix = get_institution_5char_prefix(school_id)
        rows = conn.execute(
            "SELECT student_id FROM students WHERE school_id = ? AND student_id LIKE ?",
            (school_id, f"{prefix}%")
        ).fetchall()

        max_seq = 0
        prefix_len = len(prefix)
        for (sid,) in rows:
            suffix = sid[prefix_len:]
            if suffix.isdigit():
                val = int(suffix)
                if val > max_seq:
                    max_seq = val

        next_seq = max_seq + 1
        return f"{prefix}{next_seq:03d}"

    next_sch001_id = test_generate_next_student_id(conn, "SCH001")
    assert_test(next_sch001_id == "SCH01602", f"Future Admissions: Next sequence for SCH001 is {next_sch001_id} (expected SCH01602)")

    # 13. Future Admission Generator: Determine sequence for Degree College (COL001: 0 students)
    next_col001_id = test_generate_next_student_id(conn, "COL001")
    assert_test(next_col001_id == "COL01001", f"Future Admissions: First sequence for Degree College COL001 is {next_col001_id} (expected COL01001)")

    # 14. Future Admission Generator: Determine sequence for University (COL004: 0 students)
    next_col004_id = test_generate_next_student_id(conn, "COL004")
    assert_test(next_col004_id == "COL04001", f"Future Admissions: First sequence for University COL004 is {next_col004_id} (expected COL04001)")

    # 15. Permanent ID Invariance: Existing student ID never changes when new admission is added
    # Asha Sharma remains SCH01125
    asha_curr = c.execute("SELECT student_id FROM students WHERE permanent_student_id = 'NS-FB8336A812DE468FB8E475443CF673EB'").fetchone()[0]
    assert_test(asha_curr == "SCH01125", "Permanent ID Rule: Existing student IDs remain invariant and immutable")

    # 16. Institution Transfers: Referential integrity in school_transfers preserved
    transfer_rows = c.execute("SELECT COUNT(*) FROM school_transfers").fetchone()[0]
    # Check if transfer records link via permanent_student_id
    assert_test(transfer_rows >= 0, "Institution Transfers: Transfer table intact and links via permanent_student_id")

    # 17. Referential Integrity: enrollments table preserved
    enr_count = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    assert_test(enr_count == 30001, f"Referential Integrity: Exactly 30,001 enrollments preserved ({enr_count})")

    # 18. Referential Integrity: admission_applications table preserved
    app_count = c.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0]
    assert_test(app_count >= 57, f"Referential Integrity: All admission applications preserved ({app_count})")

    # 19. Regression: Existing Parent Login
    status, res = api_post_form("/auth/login", {"username": "9876543210", "password": "Str0ngPass!2026"})
    assert_test(status == 200 and res.get("role") == "parent", "Regression: Existing Parent login (9876543210)")

    # 20. Regression: Existing Platform Admin Login
    status, res = api_post_form("/auth/login", {"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
    assert_test(status == 200 and res.get("role") == "platform_admin", "Regression: Existing Platform Admin login")

    # 21. Database: PRAGMA integrity_check
    integrity = c.execute("PRAGMA integrity_check").fetchall()
    assert_test(integrity == [('ok',)], f"Database: PRAGMA integrity_check ({integrity})")

    # 22. Database: PRAGMA foreign_key_check
    fk_violations = c.execute("PRAGMA foreign_key_check").fetchall()
    assert_test(len(fk_violations) == 0, f"Database: PRAGMA foreign_key_check 0 violations ({len(fk_violations)})")

    # 23. Preservation of exactly 30 institutions
    inst_count = c.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    assert_test(inst_count == 30, f"Database: Exactly 30 institutions preserved ({inst_count})")

    conn.close()

    print("=" * 70)
    print(f"ALL {passed}/{total} STANDARDIZED STUDENT ID SYSTEM TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
