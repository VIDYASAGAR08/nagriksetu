import sqlite3
import requests
import sys
from collections import Counter

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def main():
    print("=" * 70)
    print("NAGRIKSETU - 30 INSTITUTIONS RESTRUCTURING ACCEPTANCE AUDIT")
    print("=" * 70)

    # 1. API Verification
    print("\n[TEST 1] Querying GET /schools?limit=100 API...")
    resp = requests.get(f"{BASE_URL}/schools?limit=100")
    if resp.status_code != 200:
        print(f"FAILED: /schools returned status {resp.status_code}")
        sys.exit(1)
    
    data = resp.json()
    schools = data if isinstance(data, list) else data.get("value", [])
    total_count = len(schools)
    print(f"Total institutions returned by API: {total_count}")
    assert total_count == 30, f"Expected 30 institutions, got {total_count}"

    cat_counter = Counter(s.get("category") for s in schools)
    type_counter = Counter(s.get("school_type") for s in schools)
    print("Categories distribution:", dict(cat_counter))
    print("School types distribution:", dict(type_counter))

    assert cat_counter["Schools (K-10)"] == 15, f"Expected 15 Schools (K-10), got {cat_counter['Schools (K-10)']}"
    assert cat_counter["PU Colleges (11-12)"] == 5, f"Expected 5 PU Colleges (11-12), got {cat_counter['PU Colleges (11-12)']}"
    assert cat_counter["Degree Colleges"] == 5, f"Expected 5 Degree Colleges, got {cat_counter['Degree Colleges']}"
    assert cat_counter["Universities"] == 5, f"Expected 5 Universities, got {cat_counter['Universities']}"
    assert "Diploma" not in cat_counter and "Polytechnic" not in cat_counter, "Diploma/Polytechnic found in categories!"
    print("[OK] TEST 1 PASSED: API returns exactly 30 institutions with 15/5/5/5 distribution and zero diploma.")

    # 2. Specific Institution Inspections
    print("\n[TEST 2] Verifying key restructured institutions...")
    school_map = {s["school_id"]: s for s in schools}

    vtu = school_map.get("COL010")
    assert vtu is not None, "COL010 not found!"
    print(f"COL010: Name='{vtu['school_name']}', Category='{vtu.get('category')}', Type='{vtu.get('school_type')}'")
    assert "Visvesvaraya Technological University" in vtu["school_name"]
    assert vtu["category"] == "Universities"
    assert vtu["school_type"] == "University"

    sch011 = school_map.get("SCH011")
    assert sch011 is not None, "SCH011 not found!"
    print(f"SCH011: Name='{sch011['school_name']}', Category='{sch011.get('category')}', Type='{sch011.get('school_type')}'")
    assert "PU" in sch011["school_name"] or "Pre-University" in sch011["school_name"]
    assert sch011["category"] == "PU Colleges (11-12)"
    assert sch011["school_type"] == "PU College"

    sch001 = school_map.get("SCH001")
    assert sch001 is not None, "SCH001 not found!"
    print(f"SCH001: Name='{sch001['school_name']}', Category='{sch001.get('category')}', Type='{sch001.get('school_type')}'")
    assert sch001["category"] == "Schools (K-10)"
    assert sch001["school_type"] == "School"
    print("[OK] TEST 2 PASSED: Key institutions correctly categorized.")

    # 3. Individual School Endpoints & Seat Availability
    print("\n[TEST 3] Testing individual school endpoints and seat availability...")
    for s_id in ["SCH001", "SCH011", "COL001", "COL010"]:
        r1 = requests.get(f"{BASE_URL}/schools/{s_id}")
        assert r1.status_code == 200, f"Failed GET /schools/{s_id}"
        r2 = requests.get(f"{BASE_URL}/schools/{s_id}/seat-availability")
        assert r2.status_code == 200, f"Failed GET /schools/{s_id}/seat-availability"
        seats = r2.json()
        print(f"  {s_id}: total={seats.get('total_seats')}, available={seats.get('total_available_seats')}")
    print("[OK] TEST 3 PASSED: Individual endpoints and seat availability functioning.")

    # 4. Authentication and Isolation Testing
    print("\n[TEST 4] Testing authentication for institutional accounts...")
    login_tests = [
        ("staff.sch001@example.com", "Staff@NagrikSetu2026!", "SCH001", "school_staff"),
        ("staff.sch011@example.com", "Staff@NagrikSetu2026!", "SCH011", "school_staff"),
        ("admin.central@nagriksetu.gov", "Central@NagrikSetu2026!", None, "platform_admin"),
    ]
    for email, pwd, expected_inst, expected_role in login_tests:
        l_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": pwd})
        assert l_resp.status_code == 200, f"Login failed for {email}: {l_resp.text}"
        user_info = l_resp.json()
        print(f"  Login {email}: role={user_info.get('role')}, school_id={user_info.get('school_id')}")
        assert user_info.get("school_id") == expected_inst, f"Expected {expected_inst}, got {user_info.get('school_id')}"
        assert user_info.get("role") == expected_role, f"Expected {expected_role}, got {user_info.get('role')}"
    print("[OK] TEST 4 PASSED: Institutional accounts login and isolation preserved.")

    # 5. Database Level Deep Verification
    print("\n[TEST 5] Database deep integrity & baseline checks...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    assert integrity == "ok", f"Integrity check failed: {integrity}"

    cur.execute("PRAGMA foreign_key_check")
    fk_violations = cur.fetchall()
    assert len(fk_violations) == 0, f"FK violations: {fk_violations}"

    cur.execute("SELECT count(*) FROM students")
    student_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM enrollments")
    enrolment_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM academic_programs")
    prog_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM program_sections")
    section_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM schools")
    db_school_count = cur.fetchone()[0]

    print(f"  Database records:")
    print(f"    - Schools: {db_school_count}")
    print(f"    - Students: {student_count}")
    print(f"    - Enrolments: {enrolment_count}")
    print(f"    - Academic Programmes: {prog_count}")
    print(f"    - Programme Sections: {section_count}")

    assert db_school_count == 30, f"Expected 30 schools, got {db_school_count}"
    assert student_count == 30001, f"Expected 30,001 students, got {student_count}"
    assert enrolment_count == 30001, f"Expected 30,001 enrolments, got {enrolment_count}"
    assert prog_count == 198, f"Expected 198 programmes, got {prog_count}"
    assert section_count == 841, f"Expected 841 sections, got {section_count}"

    # Detailed category breakdown with student counts
    print("\nDetailed Category Breakdown:")
    cur.execute("""
        SELECT s.category, s.school_type, count(DISTINCT s.school_id) as school_count, count(st.student_id) as student_count
        FROM schools s
        LEFT JOIN students st ON s.school_id = st.school_id
        GROUP BY s.category, s.school_type
        ORDER BY s.category
    """)
    for row in cur.fetchall():
        print(f"  Category: {row['category']:<22} | Type: {row['school_type']:<15} | Institutions: {row['school_count']:<2} | Students: {row['student_count']}")

    conn.close()
    print("[OK] TEST 5 PASSED: Database baseline & integrity 100% verified.")

    print("\n" + "=" * 70)
    print("ALL 5 VERIFICATION AUDIT SUITES PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
