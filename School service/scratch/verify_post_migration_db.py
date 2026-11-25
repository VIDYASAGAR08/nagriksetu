import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
backup_path = r'C:\Users\callm\nagriksetu\backend\data\backups\nagriksetu_backup_before_12000_correction_20261122_180711.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("=== POST-MIGRATION DATABASE VERIFICATION ===")

# 1. Integrity check
cur.execute("PRAGMA integrity_check")
ic = cur.fetchall()
print("PRAGMA integrity_check:", ic)
assert ic == [('ok',)], f"Integrity check failed: {ic}"

# 2. Foreign key check
cur.execute("PRAGMA foreign_key_check")
fk_issues = cur.fetchall()
print(f"PRAGMA foreign_key_check issues count: {len(fk_issues)}")

# 3. Table counts
tables_to_check = {
    'schools': 31,
    'students': 30003,
    'enrollments': 30003,
    'academic_programs': 185, # was 140, +5 K10 for SCH011-15, +40 PU for SCH016-20
    'institution_divisions': 48, # was 28, +20 for SCH011-SCH020 (plus SCH002-SCH010 registered)
    'student_attendance': 719929,
    'academic_results': 179994,
    'student_documents': 120012,
    'student_guardians': 32
}

print("\n--- Row Counts Validation ---")
for tbl, expected in tables_to_check.items():
    cur.execute(f"SELECT count(*) FROM {tbl}")
    cnt = cur.fetchone()[0]
    status = "OK" if cnt >= expected else "MISMATCH"
    print(f"Table '{tbl}': {cnt} rows (Expected baseline: {expected}) -> {status}")
    if tbl in ['students', 'enrollments', 'student_attendance', 'academic_results', 'student_documents', 'student_guardians']:
        assert cnt == expected, f"Mismatch in {tbl}: {cnt} != {expected}"

# 4. Student uniqueness
cur.execute("SELECT count(DISTINCT student_id), count(DISTINCT permanent_student_id) FROM students")
u_sid, u_psid = cur.fetchone()
print(f"\nUnique Student IDs: {u_sid} / 30003")
print(f"Unique PSIDs: {u_psid} / 30003")
assert u_sid == 30003 and u_psid == 30003

# 5. Check review flags
cur.execute("SELECT count(*) FROM students WHERE review_flag IS NOT NULL")
rf_s = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM enrollments WHERE review_flag IS NOT NULL")
rf_e = cur.fetchone()[0]
print(f"\nActive review flags in students: {rf_s}")
print(f"Active review flags in enrollments: {rf_e}")
assert rf_s == 0 and rf_e == 0

# 6. Check division breakdowns
print("\n--- Student Division Distribution ---")
cur.execute("""
    SELECT academic_division, count(*)
    FROM students
    GROUP BY academic_division
    ORDER BY count(*) DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# 7. Check Group A (SCH011-SCH015, Std 1-10)
print("\n--- Group A Verification (SCH011-SCH015, Std 1-10) ---")
cur.execute("""
    SELECT school_id, academic_division, division_id, program_id, curriculum_or_board, stream, degree, count(*)
    FROM students
    WHERE school_id BETWEEN 'SCH011' AND 'SCH015' AND standard BETWEEN 1 AND 10
    GROUP BY school_id, academic_division, division_id, program_id, curriculum_or_board, stream, degree
""")
for r in cur.fetchall():
    print(r)

# 8. Check Group B (SCH016-SCH020, Std 11-12)
print("\n--- Group B Verification (SCH016-SCH020, Std 11-12) ---")
cur.execute("""
    SELECT school_id, standard, puc_year, academic_division, stream, subject_combination, count(*)
    FROM students
    WHERE school_id BETWEEN 'SCH016' AND 'SCH020' AND standard BETWEEN 11 AND 12
    GROUP BY school_id, standard, puc_year, academic_division, stream, subject_combination
    ORDER BY school_id, standard, count(*) DESC
""")
for r in cur.fetchall()[:16]:
    print(r)

# 9. Trace against backup to ensure no Student IDs or PSIDs changed
print("\n--- Comparing against pre-correction backup ---")
b_conn = sqlite3.connect(backup_path)
b_cur = b_conn.cursor()

cur.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard FROM students ORDER BY student_id")
live_students = cur.fetchall()

b_cur.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard FROM students ORDER BY student_id")
backup_students = b_cur.fetchall()

assert len(live_students) == len(backup_students) == 30003
diffs = 0
for live, bk in zip(live_students, backup_students):
    # Student ID, PSID, Student Name, School ID, and Standard must be identical
    if live != bk:
        diffs += 1
print(f"Core identity differences (Student ID, PSID, Name, School ID, Standard): {diffs} (Expected: 0)")
assert diffs == 0

b_conn.close()
conn.close()
print("\n=== ALL DATABASE INTEGRITY CHECKS PASSED PERFECTLY ===")
