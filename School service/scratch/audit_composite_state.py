import sqlite3
import os

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
BACKUP_PATH = r"C:\Users\callm\nagriksetu\backend\data\backups\nagriksetu_composite_pre_backup_20261122_103046.db"

print("=====================================================================")
print("     NAGRIKSETU COMPOSITE INSTITUTION STRUCTURE AUDIT (READ-ONLY)    ")
print("=====================================================================")

# 8. Confirm the backup file exists and is valid
print("\n[AUDIT ITEM 8] BACKUP FILE VERIFICATION")
if os.path.exists(BACKUP_PATH):
    size_mb = os.path.getsize(BACKUP_PATH) / (1024 * 1024)
    print(f"  Backup Path: {BACKUP_PATH}")
    print(f"  Backup File Size: {size_mb:.2f} MB")
    try:
        conn_b = sqlite3.connect(BACKUP_PATH)
        cur_b = conn_b.cursor()
        cur_b.execute("SELECT count(*) FROM students")
        b_students = cur_b.fetchone()[0]
        cur_b.execute("SELECT count(*) FROM schools")
        b_schools = cur_b.fetchone()[0]
        cur_b.execute("SELECT count(*) FROM enrollments")
        b_enr = cur_b.fetchone()[0]
        cur_b.execute("SELECT count(*) FROM student_attendance")
        b_att = cur_b.fetchone()[0]
        cur_b.execute("SELECT count(*) FROM academic_results")
        b_res = cur_b.fetchone()[0]
        cur_b.execute("SELECT count(*) FROM student_documents")
        b_docs = cur_b.fetchone()[0]
        cur_b.execute("SELECT count(*) FROM student_guardians")
        b_sg = cur_b.fetchone()[0]
        conn_b.close()
        print(f"  Backup Database Status: VALID SQLite3")
        print(f"  Backup Counts:")
        print(f"    - Students: {b_students}")
        print(f"    - Schools: {b_schools}")
        print(f"    - Enrollments: {b_enr}")
        print(f"    - Attendance Records: {b_att}")
        print(f"    - Academic Results: {b_res}")
        print(f"    - Student Documents: {b_docs}")
        print(f"    - Student-Guardian Links: {b_sg}")
    except Exception as e:
        print(f"  Backup Validation ERROR: {e}")
else:
    print(f"  Backup file MISSING at: {BACKUP_PATH}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Check whether migrate_composite_structure.py was actually executed
print("\n[AUDIT ITEM 1] CHECK WHETHER migrate_composite_structure.py WAS EXECUTED")
cur.execute("PRAGMA table_info(students)")
student_cols = [c[1] for c in cur.fetchall()]
has_div_id_students = 'division_id' in student_cols
has_acad_div_students = 'academic_division' in student_cols

cur.execute("PRAGMA table_info(enrollments)")
enroll_cols = [c[1] for c in cur.fetchall()]
has_div_id_enroll = 'division_id' in enroll_cols
has_acad_div_enroll = 'academic_division' in enroll_cols

cur.execute("SELECT count(*) FROM students WHERE review_flag IS NOT NULL")
flagged_students = cur.fetchone()[0]

cur.execute("SELECT count(*) FROM institution_divisions WHERE parent_institution_id BETWEEN 'SCH011' AND 'SCH020'")
composite_divs_count = cur.fetchone()[0]

cur.execute("SELECT school_id, school_type FROM schools WHERE school_id BETWEEN 'SCH011' AND 'SCH020'")
school_types = cur.fetchall()
composite_schools_count = sum(1 for s in school_types if 'Composite' in s[1])

print(f"  students table has 'division_id': {has_div_id_students}")
print(f"  students table has 'academic_division': {has_acad_div_students}")
print(f"  enrollments table has 'division_id': {has_div_id_enroll}")
print(f"  enrollments table has 'academic_division': {has_acad_div_enroll}")
print(f"  institution_divisions for SCH011-SCH020: {composite_divs_count} (Expected if migrated: 20)")
print(f"  schools with 'Composite' in school_type: {composite_schools_count} (Expected if migrated: 10)")
print(f"  Students with review_flag active: {flagged_students} (Expected if migrated: 0; Pre-migration: 12000)")

migration_executed = (has_div_id_students and composite_divs_count == 20 and flagged_students == 0)
print(f"\n  -> VERDICT: migrate_composite_structure.py execution status = {'EXECUTED' if migration_executed else 'NOT EXECUTED'}")
if not migration_executed:
    print("     The migration script exists on disk (C:\\Users\\callm\\nagriksetu\\scratch\\migrate_composite_structure.py),")
    print("     but has NOT yet been run against the database.")

# 2. Verify composite academic divisions for SCH011-SCH020
print("\n[AUDIT ITEM 2] COMPOSITE ACADEMIC DIVISIONS FOR SCH011-SCH020")
cur.execute("SELECT school_id, school_name, school_type FROM schools WHERE school_id BETWEEN 'SCH011' AND 'SCH020' ORDER BY school_id")
schools = cur.fetchall()
for s in schools:
    print(f"  {s[0]}: {s[1]} | Current Type: '{s[2]}'")

cur.execute("SELECT division_id, parent_institution_id, division_name, division_type FROM institution_divisions WHERE parent_institution_id BETWEEN 'SCH011' AND 'SCH020' ORDER BY parent_institution_id, division_id")
div_rows = cur.fetchall()
print(f"  institution_divisions rows for SCH011-SCH020: {len(div_rows)}")

# Academic programs check for SCH011-SCH020
cur.execute("SELECT program_id, institution_id, education_level, program_name, discipline_or_stream, combination_code FROM academic_programs WHERE institution_id BETWEEN 'SCH011' AND 'SCH020' ORDER BY institution_id, program_id")
progs = cur.fetchall()
print(f"  Total academic_programs entries for SCH011-SCH020: {len(progs)}")
sch11_15_k10_progs = [p for p in progs if p[1] <= 'SCH015' and 'K10' in p[0]]
sch16_20_pu_progs = [p for p in progs if p[1] >= 'SCH016']
print(f"    SCH011-SCH015 K-10 programs: {len(sch11_15_k10_progs)} (Expected: 5)")
print(f"    SCH016-SCH020 PU programs: {len(sch16_20_pu_progs)} (Expected: 40)")

# 3. Verify school standards 1-10 and PU 1st/2nd PUC classifications
print("\n[AUDIT ITEM 3] SCHOOL STANDARDS 1-10 AND PU 1ST/2ND PUC CLASSIFICATIONS")
print("  Current distribution of standards across SCH011-SCH020:")
for s in schools:
    sid = s[0]
    cur.execute("SELECT count(*) FROM students WHERE school_id = ?", (sid,))
    tot = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM students WHERE school_id = ? AND standard BETWEEN 1 AND 10", (sid,))
    std1_10 = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM students WHERE school_id = ? AND standard BETWEEN 11 AND 12", (sid,))
    std11_12 = cur.fetchone()[0]
    cur.execute("SELECT puc_year, count(*) FROM students WHERE school_id = ? GROUP BY puc_year", (sid,))
    puc_years = dict(cur.fetchall())
    print(f"    {sid} ({s[1][:25]}): Total={tot} | Std 1-10: {std1_10} | Std 11-12: {std11_12} | puc_year col: {puc_years}")

# 4. Check PU streams and subject combinations
print("\n[AUDIT ITEM 4] PU STREAMS AND SUBJECT COMBINATIONS")
# In SCH011-SCH015 (original PU colleges, standards 11-12)
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, count(*)
    FROM students
    WHERE school_id BETWEEN 'SCH011' AND 'SCH015' AND standard IN (11, 12)
    GROUP BY standard, puc_year, stream, subject_combination
    ORDER BY standard, stream, subject_combination
""")
pu_original_combos = cur.fetchall()
print(f"  SCH011-SCH015 (Valid PU Students in Standards 11-12, total {sum(r[4] for r in pu_original_combos)}):")
for r in pu_original_combos:
    print(f"    Std {r[0]} ({r[1]}) | Stream: {r[2]} | Combo: {r[3]} | Count: {r[4]}")

# In SCH016-SCH020 (standards 11-12 currently unassigned)
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, count(*)
    FROM students
    WHERE school_id BETWEEN 'SCH016' AND 'SCH020' AND standard IN (11, 12)
    GROUP BY standard, puc_year, stream, subject_combination
    ORDER BY standard, stream, subject_combination
""")
school_pu_combos = cur.fetchall()
print(f"  SCH016-SCH020 (PU Students in Standards 11-12, total {sum(r[4] for r in school_pu_combos)}):")
for r in school_pu_combos:
    print(f"    Std {r[0]} ({r[1]}) | Stream: {r[2]} | Combo: {r[3]} | Count: {r[4]}")

# 5. Verify total student count remains 30,003
print("\n[AUDIT ITEM 5] TOTAL STUDENT COUNT")
cur.execute("SELECT count(*) FROM students")
total_students = cur.fetchone()[0]
print(f"  Current Total Student Count: {total_students}")
print(f"  Target Total Student Count:  30003")
print(f"  Status: {'MATCH (30,003)' if total_students == 30003 else 'MISMATCH'}")

# 6. Verify Student IDs, PSIDs, institution IDs, enrollments, guardians, attendance, exams
print("\n[AUDIT ITEM 6] RECORD PRESERVATION & INTEGRITY CHECKS")
cur.execute("SELECT count(DISTINCT student_id) FROM students")
dist_sids = cur.fetchone()[0]
cur.execute("SELECT count(DISTINCT permanent_student_id) FROM students")
dist_psids = cur.fetchone()[0]
print(f"  Distinct student_id in students: {dist_sids} (Expected: 30003)")
print(f"  Distinct permanent_student_id:  {dist_psids} (Expected: 30003)")

cur.execute("SELECT count(*), count(DISTINCT permanent_student_id) FROM enrollments")
tot_enroll, dist_enr_psid = cur.fetchone()
print(f"  Total enrollments: {tot_enroll} | Distinct PSID in enrollments: {dist_enr_psid} (Expected: 30003)")

cur.execute("SELECT count(*), count(DISTINCT permanent_student_id) FROM student_guardians")
tot_guard, dist_guard_psid = cur.fetchone()
print(f"  Total student_guardians: {tot_guard} | Distinct PSID linked: {dist_guard_psid} (Expected: 30003)")

cur.execute("SELECT count(*), count(DISTINCT permanent_student_id) FROM student_attendance")
tot_att, dist_att_psid = cur.fetchone()
print(f"  Total student_attendance records: {tot_att} | Distinct PSID with attendance: {dist_att_psid} (Expected: 30003)")

cur.execute("SELECT count(*), count(DISTINCT permanent_student_id) FROM academic_results")
tot_exams, dist_exam_psid = cur.fetchone()
print(f"  Total academic_results: {tot_exams} | Distinct PSID with results: {dist_exam_psid} (Expected: 30003)")

cur.execute("SELECT count(*), count(DISTINCT permanent_student_id) FROM student_documents")
tot_docs, dist_doc_psid = cur.fetchone()
print(f"  Total student_documents: {tot_docs} | Distinct PSID with documents: {dist_doc_psid} (Expected: 30003)")

# 7. Check for missing, duplicate or incorrectly classified records
print("\n[AUDIT ITEM 7] DUPLICATES, ORPHANS, AND ANOMALIES")
cur.execute("SELECT student_id, count(*) FROM students GROUP BY student_id HAVING count(*) > 1")
dupe_s = cur.fetchall()
cur.execute("SELECT permanent_student_id, count(*) FROM students GROUP BY permanent_student_id HAVING count(*) > 1")
dupe_p = cur.fetchall()
print(f"  Duplicate student_id: {len(dupe_s)}")
print(f"  Duplicate permanent_student_id: {len(dupe_p)}")

cur.execute("SELECT count(*) FROM students WHERE school_id IS NULL OR student_id IS NULL OR permanent_student_id IS NULL")
null_essentials = cur.fetchone()[0]
print(f"  Missing essential student fields (NULL school/id/psid): {null_essentials}")

cur.execute("SELECT count(*) FROM students WHERE school_id NOT IN (SELECT school_id FROM schools)")
orphan_schools = cur.fetchone()[0]
print(f"  Orphan students (school_id not in schools): {orphan_schools}")

# Flagged records review
cur.execute("SELECT review_flag, count(*) FROM students GROUP BY review_flag")
flag_counts = cur.fetchall()
print(f"  Review Flag Breakdown:")
for fc in flag_counts:
    print(f"    Flag '{fc[0]}': {fc[1]}")

conn.close()
print("\n=====================================================================")
print("                   AUDIT DATA EXTRACTION COMPLETE                     ")
print("=====================================================================")
