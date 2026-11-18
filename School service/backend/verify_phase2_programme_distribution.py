"""
verify_phase2_programme_distribution.py
Complete verification script for NagrikSetu Phase 2: Programme-Based Student Distribution.
"""
import sqlite3
import urllib.request
import urllib.parse
import json
import sys

DB_PATH = 'C:/Users/callm/nagriksetu/backend/data/nagriksetu.db'
BACKEND_URL = 'http://localhost:8001'
FRONTEND_URL = 'http://localhost:5173'

def test_database():
    print("\n=======================================================")
    print("STEP 1: DATABASE INTEGRITY & SAFETY VERIFICATION")
    print("=======================================================")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Integrity check
    integrity = c.execute('PRAGMA integrity_check').fetchall()
    assert integrity == [('ok',)], f"Integrity check failed: {integrity}"
    print("  [PASS] PRAGMA integrity_check = ok")

    # 2. Foreign keys check
    fk_check = c.execute('PRAGMA foreign_key_check').fetchall()
    assert fk_check == [], f"Foreign key violations found: {fk_check}"
    print("  [PASS] PRAGMA foreign_key_check = [] (Zero violations)")

    # 3. 30,000 Students & Enrollments preserved
    student_count = c.execute('SELECT count(*) FROM students').fetchone()[0]
    enrollment_count = c.execute('SELECT count(*) FROM enrollments').fetchone()[0]
    assert student_count == 30000, f"Expected 30000 students, got {student_count}"
    assert enrollment_count == 30000, f"Expected 30000 enrollments, got {enrollment_count}"
    print(f"  [PASS] Live Students: {student_count} preserved intact")
    print(f"  [PASS] Live Enrollments: {enrollment_count} preserved intact")

    # 4. Check for duplicate enrollments in the same term
    dup_enrollments = c.execute('''
        SELECT permanent_student_id, academic_year, count(*)
        FROM enrollments
        GROUP BY permanent_student_id, academic_year
        HAVING count(*) > 1
    ''').fetchall()
    assert len(dup_enrollments) == 0, f"Duplicate enrollments found: {len(dup_enrollments)}"
    print("  [PASS] Duplicate enrollments in same academic year = 0")

    # 5. Program sections and academic programs counts
    prog_count = c.execute('SELECT count(*) FROM academic_programs').fetchone()[0]
    sec_count = c.execute('SELECT count(*) FROM program_sections').fetchone()[0]
    print(f"  [PASS] Total Academic Programs: {prog_count}")
    print(f"  [PASS] Total Program Sections: {sec_count}")
    conn.close()


def test_higher_secondary_strengths():
    print("\n=======================================================")
    print("STEP 2: STANDARDS 11 & 12 CONFIGURABLE STRENGTHS")
    print("=======================================================")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Required combinations and strengths from user prompt:
    # PCMB: 40 (Sec A), PCMC: 36, PCME: 37, SEBA: 57, HEBA: 46, MEBA: 60
    # Also CEBA: 45, HEPS: 48
    expected_configs = {
        ('PCMB', 'A', 11): 40,
        ('PCMB', 'B', 11): 35,
        ('PCMC', 'A', 11): 36,
        ('PCME', 'A', 11): 37,
        ('SEBA', 'A', 11): 57,
        ('HEBA', 'A', 11): 46,
        ('MEBA', 'A', 11): 60,
        ('CEBA', 'A', 11): 45,
        ('CEBA', 'B', 11): 42,
        ('HEPS', 'A', 11): 48,
    }

    # Verify for SCH011
    rows = c.execute('''
        SELECT p.combination_code, ps.section_name, ps.term_or_year, ps.current_strength, ps.capacity
        FROM program_sections ps
        JOIN academic_programs p ON p.program_id = ps.program_id
        WHERE ps.institution_id = 'SCH011' AND ps.term_or_year = 11
        ORDER BY p.combination_code, ps.section_name
    ''').fetchall()

    actual_map = {(r[0], r[1], r[2]): (r[3], r[4]) for r in rows}

    for (combo, sec, term), exp_str in expected_configs.items():
        assert (combo, sec, term) in actual_map, f"Missing config for {combo} Sec {sec} Term {term}"
        act_str, cap = actual_map[(combo, sec, term)]
        assert act_str == exp_str, f"Mismatch for {combo} Sec {sec}: expected {exp_str}, got {act_str}"
        print(f"  [PASS] Term {term} {combo} Section {sec}: Current Strength = {act_str} (Capacity = {cap})")

    conn.close()


def test_diploma_and_ug_programs():
    print("\n=======================================================")
    print("STEP 3: DIPLOMA & UNDERGRADUATE DEGREE DISTRIBUTION")
    print("=======================================================")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Diploma at COL001
    diploma_rows = c.execute('''
        SELECT p.program_name, p.combination_code, ps.term_or_year, ps.semester, ps.section_name, ps.current_strength, ps.capacity
        FROM program_sections ps
        JOIN academic_programs p ON p.program_id = ps.program_id
        WHERE ps.institution_id = 'COL001' AND p.education_level = 'diploma'
        ORDER BY p.combination_code, ps.term_or_year, ps.section_name
    ''').fetchall()

    assert len(diploma_rows) > 0, "No diploma sections found for COL001"
    print(f"  [PASS] COL001 Polytechnic Diploma Sections: {len(diploma_rows)} sections configured")
    for r in diploma_rows[:5]:
        print(f"    - {r[0]} ({r[1]}) Yr {r[2]} Sem {r[3]} Sec {r[4]}: Strength = {r[5]}, Capacity = {r[6]}")

    # 2. BA Specialisations at COL006
    ba_rows = c.execute('''
        SELECT p.program_name, p.combination_code, ps.term_or_year, ps.section_name, ps.current_strength, ps.capacity
        FROM program_sections ps
        JOIN academic_programs p ON p.program_id = ps.program_id
        WHERE ps.institution_id = 'COL006' AND p.degree_type = 'BA'
        ORDER BY p.combination_code, ps.term_or_year, ps.section_name
    ''').fetchall()

    assert len(ba_rows) >= 15, f"Expected at least 15 BA sections, got {len(ba_rows)}"
    print(f"  [PASS] COL006 Undergraduate BA Specialisation Sections: {len(ba_rows)} sections configured")
    for r in ba_rows[:5]:
        print(f"    - {r[0]} ({r[1]}) Yr {r[2]} Sec {r[3]}: Strength = {r[4]}, Capacity = {r[5]}")

    # 3. BCA, BPharm, BCom, BBA, BE/BTech
    for deg in ['BCA', 'BPharm', 'BCom', 'BBA', 'BE/B.Tech']:
        deg_secs = c.execute('''
            SELECT count(*), sum(ps.current_strength), sum(ps.capacity)
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE p.degree_type = ?
        ''', (deg,)).fetchone()
        assert deg_secs[0] > 0, f"No sections found for degree {deg}"
        print(f"  [PASS] Degree {deg}: {deg_secs[0]} sections | {deg_secs[1]} students | {deg_secs[2]} capacity")

    conn.close()


def test_api_integration():
    print("\n=======================================================")
    print("STEP 4: BACKEND API ENDPOINTS & FILTERING")
    print("=======================================================")
    # Login as staff
    data = urllib.parse.urlencode({
        'username': 'staff.sch001@example.com',
        'password': 'Staff@NagrikSetu2026!'
    }).encode('utf-8')
    req = urllib.request.Request(
        f'{BACKEND_URL}/auth/login',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    resp = urllib.request.urlopen(req)
    token = json.loads(resp.read().decode())['access_token']
    assert token, "Login failed to return token"
    print("  [PASS] Staff authentication successful (JWT obtained)")

    headers = {'Authorization': f'Bearer {token}'}

    # API 1: Filter by PU term 11
    req1 = urllib.request.Request(f'{BACKEND_URL}/schools/SCH011/program-sections?term_or_year=11', headers=headers)
    resp1 = urllib.request.urlopen(req1)
    secs1 = json.loads(resp1.read().decode())
    assert len(secs1) == 10, f"Expected 10 sections for SCH011 term 11, got {len(secs1)}"
    print(f"  [PASS] GET /schools/SCH011/program-sections?term_or_year=11 returned {len(secs1)} sections")

    # API 2: Filter by diploma AUTO-DIP
    req2 = urllib.request.Request(f'{BACKEND_URL}/schools/COL001/program-sections?education_level=diploma&combination_code=AUTO-DIP', headers=headers)
    resp2 = urllib.request.urlopen(req2)
    secs2 = json.loads(resp2.read().decode())
    assert len(secs2) == 3, f"Expected 3 sections for AUTO-DIP, got {len(secs2)}"
    print(f"  [PASS] GET /schools/COL001/program-sections?combination_code=AUTO-DIP returned {len(secs2)} sections")

    # API 3: Global education program sections by degree_type
    req3 = urllib.request.Request(f'{BACKEND_URL}/education/program-sections?degree_type=BCA', headers=headers)
    resp3 = urllib.request.urlopen(req3)
    secs3 = json.loads(resp3.read().decode())
    assert len(secs3) > 0, "Expected BCA sections"
    print(f"  [PASS] GET /education/program-sections?degree_type=BCA returned {len(secs3)} sections")

    # API 4: Global education program sections by stream
    req4 = urllib.request.Request(f'{BACKEND_URL}/education/program-sections?discipline_or_stream=Commerce', headers=headers)
    resp4 = urllib.request.urlopen(req4)
    secs4 = json.loads(resp4.read().decode())
    assert len(secs4) > 0, "Expected Commerce sections"
    print(f"  [PASS] GET /education/program-sections?discipline_or_stream=Commerce returned {len(secs4)} sections")


def test_frontend_serving():
    print("\n=======================================================")
    print("STEP 5: FRONTEND DEPLOYMENT & UI VERIFICATION")
    print("=======================================================")
    req = urllib.request.Request(FRONTEND_URL)
    resp = urllib.request.urlopen(req)
    assert resp.status == 200, f"Frontend returned status {resp.status}"
    body = resp.read().decode('utf-8')
    assert '<div id="root">' in body, "Frontend root div missing"
    print("  [PASS] Frontend container serving HTTP 200 OK")


if __name__ == '__main__':
    try:
        test_database()
        test_higher_secondary_strengths()
        test_diploma_and_ug_programs()
        test_api_integration()
        test_frontend_serving()
        print("\n=======================================================")
        print("ALL VERIFICATION SUITES PASSED SUCCESSFULLY (100%)")
        print("=======================================================\n")
    except Exception as e:
        print(f"\n[FAIL] Verification error: {e}", file=sys.stderr)
        sys.exit(1)
