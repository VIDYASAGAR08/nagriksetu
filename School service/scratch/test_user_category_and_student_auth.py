import urllib.request
import urllib.parse
import json
import sqlite3

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

def api_post_json(endpoint, json_data, token=None):
    data = json.dumps(json_data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", data=data, headers=headers)
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
    print("=" * 65)
    print("NAGRIKSETU — USER CATEGORY & STUDENT AUTHENTICATION TEST SUITE")
    print("=" * 65)

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

    # 1. Public Directory Access (No Auth Required)
    status, schools = api_get("/schools")
    assert_test(status == 200 and len(schools) == 30, f"Public Directory: 30 institutions accessible without login (status={status}, count={len(schools)})")

    # 2. Student Login via Student ID
    status, res = api_post_form("/auth/login", {"username": "SCH001-STD01-001", "password": "Password@2026!"})
    assert_test(status == 200 and res.get("role") == "student" and res.get("student_id") == "SCH001-STD01-001", "Student Login via Student ID (SCH001-STD01-001)")
    student_token = res["access_token"]

    # 3. Student Login via Registered Email
    status, res_email = api_post_form("/auth/login", {"username": "student.asha@example.com", "password": "Password@2026!"})
    assert_test(status == 200 and res_email.get("role") == "student", "Student Login via Email (student.asha@example.com)")

    # 4. Student Profile API
    status, profile = api_get("/student/profile", token=student_token)
    assert_test(
        status == 200 and profile["student"]["student_name"] == "Asha Sharma" and profile["school"]["school_id"] == "SCH001",
        f"Student Profile endpoint returns Asha Sharma at SCH001 (status={status})"
    )

    # 5. Student Account Activation: Reject < 8 characters password
    status, res = api_post_json("/auth/student/register", {
        "student_identifier": "SCH001-STD01-002",
        "full_name": "Kiran Kumar",
        "email": "kiran.short@student.test",
        "password": "Pass12!", # 7 chars
        "confirm_password": "Pass12!"
    })
    assert_test(status == 422, f"Student Activation: 7-character password rejected (status={status})")

    # 6. Student Account Activation: Reject non-existent student record
    status, res = api_post_json("/auth/student/register", {
        "student_identifier": "NON-EXISTENT-STUDENT-9999",
        "full_name": "Fake Student",
        "email": "fake.student@example.com",
        "password": "ValidPassword@2026!",
        "confirm_password": "ValidPassword@2026!"
    })
    assert_test(status == 404, f"Student Activation: Non-existent student rejected with 404 (status={status})")

    # 7. Student Account Activation: Successful provisioning for unprovisioned student (SCH001-STD01-002)
    # Check if already registered in previous test run; if so, clear only this test student
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM users WHERE student_id = 'SCH001-STD01-002'")
    conn.commit()
    conn.close()

    status, res = api_post_json("/auth/student/register", {
        "student_identifier": "SCH001-STD01-002",
        "full_name": "Kiran Kumar",
        "email": "kiran.kumar@student.nagriksetu.gov",
        "phone": "9876543202",
        "password": "KiranPassword@2026!",
        "confirm_password": "KiranPassword@2026!"
    })
    assert_test(
        status == 201 and res["student_id"] == "SCH001-STD01-002" and res["full_name"] == "Kiran Kumar",
        f"Student Activation: On-demand provisioning of Kiran Kumar (SCH001-STD01-002) (status={status})"
    )

    # 8. Newly Activated Student Login
    status, res = api_post_form("/auth/login", {"username": "SCH001-STD01-002", "password": "KiranPassword@2026!"})
    assert_test(status == 200 and res.get("role") == "student", "Newly Activated Student Login with Student ID")
    kiran_token = res["access_token"]

    # 9. Student Activation: Reject duplicate activation of already registered student
    status, res = api_post_json("/auth/student/register", {
        "student_identifier": "SCH001-STD01-002",
        "full_name": "Kiran Kumar",
        "email": "another.email@example.com",
        "password": "AnotherPassword@2026!",
        "confirm_password": "AnotherPassword@2026!"
    })
    assert_test(status == 400, f"Student Activation: Duplicate activation blocked with HTTP 400 (status={status})")

    # 10. Security: Student blocked from Parent endpoints
    status, res = api_get("/parent/children", token=student_token)
    assert_test(status == 403, f"Security: Student blocked from /parent/children (status={status})")

    # 11. Security: Student blocked from Parent linking requests
    status, res = api_get("/parent/linking-requests", token=student_token)
    assert_test(status == 403, f"Security: Student blocked from /parent/linking-requests (status={status})")

    # 12. Security: Parent blocked from Student profile
    status, res = api_post_form("/auth/login", {"username": "9876543210", "password": "Str0ngPass!2026"})
    parent_token = res["access_token"]
    status, res = api_get("/student/profile", token=parent_token)
    assert_test(status == 403, f"Security: Parent blocked from /student/profile (status={status})")

    # 13. Security: Cross-student record access strictly forbidden
    # Asha Sharma (SCH001-STD01-001) attempting to access Kiran Kumar (SCH001-STD01-002)
    status, res = api_get("/students/SCH001-STD01-002", token=student_token)
    assert_test(status == 403, f"Security: Cross-student record access blocked with HTTP 403 (status={status})")

    # 14. Security: Own student record access permitted
    # Asha Sharma accessing SCH001-STD01-001
    status, res = api_get("/students/SCH001-STD01-001", token=student_token)
    assert_test(status == 200 and res.get("student_id") == "SCH001-STD01-001", "Security: Own student record accessible with HTTP 200")

    # 15. Regression: Existing Parent Login
    status, res = api_post_form("/auth/login", {"username": "9876543210", "password": "Str0ngPass!2026"})
    assert_test(status == 200 and res.get("role") == "parent", "Regression: Existing Parent Login (9876543210)")

    # 16. Regression: Existing Platform Admin Login
    status, res = api_post_form("/auth/login", {"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
    assert_test(status == 200 and res.get("role") == "platform_admin", "Regression: Existing Platform Admin Login")

    # 17. Regression: Existing Institution Admin Login (SCH019)
    status, res = api_post_form("/auth/login?institution_id=SCH019", {"username": "admin.sch019@gmail.com", "password": "Admin@NagrikSetu2026!"})
    assert_test(status == 200 and res.get("role") == "school_admin", "Regression: Existing Institution Admin Login (SCH019)")

    # 18. Regression: Existing Institution Staff Login (SCH001)
    status, res = api_post_form("/auth/login", {"username": "staff.sch001@example.com", "password": "Staff@NagrikSetu2026!"})
    assert_test(status == 200 and res.get("role") == "school_staff", "Regression: Existing Institution Staff Login (staff.sch001@example.com)")

    # 19. Security: Argon2id password hash verification
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    student_users = c.execute("SELECT user_id, email, password_hash, role FROM users WHERE role = 'student'").fetchall()
    all_argon = all(u[2].startswith("$argon2id$") for u in student_users)
    assert_test(all_argon and len(student_users) >= 2, f"Security: Student users use Argon2id hashes, zero plaintext (count={len(student_users)})")

    # 20. Database: Integrity check
    integrity = c.execute("PRAGMA integrity_check").fetchall()
    assert_test(integrity == [('ok',)], f"Database: PRAGMA integrity_check ok ({integrity})")

    # 21. Database: Foreign key check
    fk_violations = c.execute("PRAGMA foreign_key_check").fetchall()
    assert_test(len(fk_violations) == 0, f"Database: PRAGMA foreign_key_check 0 violations ({len(fk_violations)})")

    # 22. Database: Preservation of 30 institutions
    inst_count = c.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    assert_test(inst_count == 30, f"Database: Exactly 30 institutions preserved ({inst_count})")

    # 23. Database: Preservation of 30,001 students
    stu_count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert_test(stu_count == 30001, f"Database: Exactly 30,001 students preserved ({stu_count})")

    # 24. Database: Preservation of 30,001 enrollments
    enr_count = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    assert_test(enr_count == 30001, f"Database: Exactly 30,001 enrollments preserved ({enr_count})")

    # 25. Database: Preservation of 57 applications
    app_count = c.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0]
    assert_test(app_count == 57, f"Database: Exactly 57 admission applications preserved ({app_count})")

    conn.close()

    print("=" * 65)
    print(f"ALL {passed}/{total} USER CATEGORY & STUDENT AUTHENTICATION TESTS PASSED!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
