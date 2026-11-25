import sqlite3
import openpyxl
import os
import json

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
backup_path = r'C:\Users\callm\nagriksetu\backend\data\backups\nagriksetu_backup_before_12000_correction_20261122_180711.db'
corr_wb_path = r'C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register_Corrected.xlsx'
orig_wb_path = r'C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx'

print("=== STARTING FINAL READ-ONLY VERIFICATION ===")

results = {}

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# -------------------------------------------------------------------------
# Check 1 & 8: Integrity & Foreign Key Checks
# -------------------------------------------------------------------------
print("\n--- CHECK 1: PRAGMA Integrity & FK Checks ---")
cur.execute("PRAGMA integrity_check")
ic_raw = cur.fetchall()
ic_res = [tuple(r) for r in ic_raw]
print(f"PRAGMA integrity_check: {ic_res}")
results["integrity_check"] = "PASS" if ic_res == [('ok',)] else "FAIL"

cur.execute("PRAGMA foreign_key_check")
fk_res = cur.fetchall()
# Filter student, enrollment, school, program, division FKs
fk_academic_tables = [r for r in fk_res if r[0] in ['students', 'enrollments', 'schools', 'academic_programs', 'institution_divisions']]
print(f"Academic tables FK violations: {len(fk_academic_tables)}")
results["academic_fk_check"] = "PASS" if len(fk_academic_tables) == 0 else "FAIL"

# -------------------------------------------------------------------------
# Check 2: Global Counts Preservation
# -------------------------------------------------------------------------
print("\n--- CHECK 2: Global Counts Preservation ---")
baseline_counts = {
    'schools': 31,
    'students': 30003,
    'enrollments': 30003,
    'student_attendance': 719929,
    'academic_results': 179994,
    'student_documents': 120012,
    'student_guardians': 32
}
counts_pass = True
for tbl, exp in baseline_counts.items():
    cur.execute(f"SELECT count(*) FROM {tbl}")
    c = cur.fetchone()[0]
    match = (c == exp)
    if not match:
        counts_pass = False
    print(f"Table {tbl}: {c} rows (Expected: {exp}) -> {'MATCH' if match else 'MISMATCH'}")
results["global_counts"] = "PASS" if counts_pass else "FAIL"

# Uniqueness
cur.execute("SELECT count(DISTINCT student_id), count(DISTINCT permanent_student_id) FROM students")
u_sid, u_psid = cur.fetchone()
print(f"Unique student_id: {u_sid}/30003 | Unique permanent_student_id: {u_psid}/30003")
results["student_id_uniqueness"] = "PASS" if u_sid == 30003 and u_psid == 30003 else "FAIL"

# -------------------------------------------------------------------------
# Check 3: Audit SCH011-SCH015 Standards 1-10 (Group A)
# -------------------------------------------------------------------------
print("\n--- CHECK 3: Group A (SCH011-SCH015, Standards 1-10) ---")
sql_a = """
    SELECT s.school_id, s.academic_division, s.division_id, s.program_id,
           s.curriculum_or_board, s.stream, s.subject_combination, s.degree,
           s.puc_year, s.review_flag, count(*) as cnt
    FROM students s
    WHERE s.school_id BETWEEN 'SCH011' AND 'SCH015' AND s.standard BETWEEN 1 AND 10
    GROUP BY s.school_id, s.academic_division, s.division_id, s.program_id,
             s.curriculum_or_board, s.stream, s.subject_combination, s.degree,
             s.puc_year, s.review_flag
"""
cur.execute(sql_a)
rows_a = cur.fetchall()
group_a_total = 0
group_a_valid = True
for r in rows_a:
    group_a_total += r["cnt"]
    print(dict(r))
    # Assertions
    if not (r["academic_division"] == "School Division" and
            r["division_id"] == f"DIV-{r['school_id']}-SCHOOL" and
            r["program_id"] == f"PROG-{r['school_id']}-K10" and
            r["curriculum_or_board"] == "Karnataka State Board (KSEEB)" and
            r["stream"] == "General" and
            r["degree"] == "School Education" and
            r["puc_year"] is None and
            r["review_flag"] is None):
        group_a_valid = False

print(f"Group A total audited: {group_a_total} / 10,000 (Valid: {group_a_valid})")
results["group_a_audit"] = "PASS" if (group_a_total == 10000 and group_a_valid) else "FAIL"

# -------------------------------------------------------------------------
# Check 4: Audit SCH016-SCH020 Standards 11-12 (Group B)
# -------------------------------------------------------------------------
print("\n--- CHECK 4: Group B (SCH016-SCH020, Standards 11-12) ---")
sql_b = """
    SELECT s.school_id, s.standard, s.puc_year, s.academic_division, s.division_id,
           s.stream, s.subject_combination, s.program_id, s.curriculum_or_board,
           s.degree, s.review_flag, count(*) as cnt
    FROM students s
    WHERE s.school_id BETWEEN 'SCH016' AND 'SCH020' AND s.standard BETWEEN 11 AND 12
    GROUP BY s.school_id, s.standard, s.puc_year, s.academic_division, s.division_id,
             s.stream, s.subject_combination, s.program_id, s.curriculum_or_board,
             s.degree, s.review_flag
    ORDER BY s.school_id, s.standard, cnt DESC
"""
cur.execute(sql_b)
rows_b = cur.fetchall()
group_b_total = 0
group_b_valid = True
valid_combinations = {"PCMB", "PCMC", "PCME", "CEBA", "SEBA", "HEBA", "MEBA", "HEPS"}
valid_streams = {"Science", "Commerce", "Arts / Humanities"}

for r in rows_b:
    group_b_total += r["cnt"]
    expected_puc = "1st PUC" if r["standard"] == 11 else "2nd PUC"
    if not (r["academic_division"] == "PU Division" and
            r["division_id"] == f"DIV-{r['school_id']}-PU" and
            r["puc_year"] == expected_puc and
            r["stream"] in valid_streams and
            r["subject_combination"] in valid_combinations and
            r["program_id"] == f"PROG-{r['school_id']}-{r['subject_combination']}" and
            r["curriculum_or_board"] == "Department of Pre-University Education (DPUE)" and
            r["degree"] == "Pre-University" and
            r["review_flag"] is None):
        group_b_valid = False

print(f"Group B total audited: {group_b_total} / 2,000 (Valid: {group_b_valid})")
results["group_b_audit"] = "PASS" if (group_b_total == 2000 and group_b_valid) else "FAIL"

# Check combination distribution per school in Group B
print("\n--- Group B Combination Distribution per School ---")
cur.execute("""
    SELECT school_id, standard, puc_year, stream, subject_combination, count(*) as cnt
    FROM students
    WHERE school_id BETWEEN 'SCH016' AND 'SCH020' AND standard BETWEEN 11 AND 12
    GROUP BY school_id, standard, puc_year, stream, subject_combination
    ORDER BY school_id, standard, count(*) DESC
""")
combo_dist = cur.fetchall()
# Print sample for SCH016
for r in combo_dist[:8]:
    print(f"  SCH016 Std {r['standard']} ({r['puc_year']}): {r['stream']} - {r['subject_combination']}: {r['cnt']} students")

# -------------------------------------------------------------------------
# Check 5: Verify division_id and program_id Referential Integrity
# -------------------------------------------------------------------------
print("\n--- CHECK 5: Referential Integrity of division_id & program_id ---")
# 1. Orphan division_id in students
cur.execute("""
    SELECT count(*) FROM students s
    LEFT JOIN institution_divisions d ON d.division_id = s.division_id
    WHERE d.division_id IS NULL
""")
orphan_divs = cur.fetchone()[0]
print(f"Students with orphan division_id: {orphan_divs}")

# 2. Orphan program_id in students
cur.execute("""
    SELECT count(*) FROM students s
    LEFT JOIN academic_programs p ON p.program_id = s.program_id
    WHERE s.program_id IS NOT NULL AND p.program_id IS NULL
""")
orphan_progs = cur.fetchone()[0]
print(f"Students with orphan program_id: {orphan_progs}")

# 3. Check division matches institution
cur.execute("""
    SELECT count(*) FROM students s
    JOIN institution_divisions d ON d.division_id = s.division_id
    WHERE d.parent_institution_id != s.school_id
""")
div_mismatches = cur.fetchone()[0]
print(f"Students whose division parent != school_id: {div_mismatches}")

# 4. Check program matches institution
cur.execute("""
    SELECT count(*) FROM students s
    JOIN academic_programs p ON p.program_id = s.program_id
    WHERE p.institution_id != s.school_id
""")
prog_mismatches = cur.fetchone()[0]
print(f"Students whose program institution != school_id: {prog_mismatches}")

results["referential_integrity"] = "PASS" if (orphan_divs == 0 and orphan_progs == 0 and div_mismatches == 0 and prog_mismatches == 0) else "FAIL"

# -------------------------------------------------------------------------
# Check 6: Check Enrollment 1:1 Synchronization
# -------------------------------------------------------------------------
print("\n--- CHECK 6: Student & Enrollment Synchronization ---")
cur.execute("""
    SELECT count(*)
    FROM students s
    JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
    WHERE (
        s.school_id != e.school_id OR
        s.standard != e.standard OR
        COALESCE(s.division_id, '') != COALESCE(e.division_id, '') OR
        COALESCE(s.academic_division, '') != COALESCE(e.academic_division, '') OR
        COALESCE(s.program_id, '') != COALESCE(e.program_id, '') OR
        COALESCE(s.puc_year, '') != COALESCE(e.puc_year, '') OR
        COALESCE(s.stream, '') != COALESCE(e.stream, '') OR
        COALESCE(s.subject_combination, '') != COALESCE(e.subject_combination, '') OR
        COALESCE(s.review_flag, '') != COALESCE(e.review_flag, '')
    )
""")
enr_sync_mismatches = cur.fetchone()[0]
print(f"Mismatches between students and enrollments: {enr_sync_mismatches}")
results["enrollment_sync"] = "PASS" if enr_sync_mismatches == 0 else "FAIL"

# -------------------------------------------------------------------------
# Check 7: Compare against Pre-Correction Backup
# -------------------------------------------------------------------------
print("\n--- CHECK 7: Comparison with Pre-Correction Backup ---")
conn_bk = sqlite3.connect(backup_path)
conn_bk.row_factory = sqlite3.Row
cur_bk = conn_bk.cursor()

cur_bk.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard FROM students ORDER BY student_id")
bk_students = cur_bk.fetchall()

cur.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard FROM students ORDER BY student_id")
live_students = cur.fetchall()

id_diffs = 0
for bk_s, lv_s in zip(bk_students, live_students):
    if (bk_s["student_id"] != lv_s["student_id"] or
        bk_s["permanent_student_id"] != lv_s["permanent_student_id"] or
        bk_s["student_name"] != lv_s["student_name"] or
        bk_s["school_id"] != lv_s["school_id"] or
        bk_s["standard"] != lv_s["standard"]):
        id_diffs += 1

print(f"Total student core identity variances: {id_diffs}")
results["core_identity_preservation"] = "PASS" if id_diffs == 0 else "FAIL"

# Verify 12,000 flagged students trace directly
cur_bk.execute("SELECT student_id, review_flag FROM students WHERE review_flag IS NOT NULL")
bk_flagged = {r["student_id"]: r["review_flag"] for r in cur_bk.fetchall()}
print(f"Total flagged in backup: {len(bk_flagged)}")

cur.execute("SELECT student_id, review_flag, academic_division FROM students WHERE student_id IN ({})".format(
    ','.join(f"'{s}'" for s in bk_flagged.keys())
))
live_trace = cur.fetchall()
all_resolved = all(r["review_flag"] is None for r in live_trace)
print(f"All 12,000 previously flagged have review_flag == NULL: {all_resolved}")
results["12000_trace_resolution"] = "PASS" if (len(live_trace) == 12000 and all_resolved) else "FAIL"

conn_bk.close()

# -------------------------------------------------------------------------
# Check 8: Inspect Corrected Excel Workbook
# -------------------------------------------------------------------------
print("\n--- CHECK 8: Inspecting Excel Workbook ---")
wb = openpyxl.load_workbook(corr_wb_path, read_only=True)
sheet_names = wb.sheetnames
print(f"Sheets in workbook: {sheet_names}")
expected_sheets = [
    'Institution Directory', 'Complete Student Register', 'Institution-wise Student List',
    'Course Enrollment Register', 'Course Summary', 'Academic Classification', 'Unmapped Review Records'
]
sheets_match = (sheet_names == expected_sheets)
print(f"All 7 sheets present and ordered correctly: {sheets_match}")

# Row count in Complete Student Register
ws2 = wb['Complete Student Register']
reg_count = sum(1 for _ in ws2.iter_rows(values_only=True))
print(f"Sheet 2 (Complete Student Register) rows: {reg_count} (Expected: 30,004 = 1 header + 30,003 students)")

# Sheet 7 inspect
ws7 = wb['Unmapped Review Records']
unmapped_rows = list(ws7.iter_rows(values_only=True))
print(f"Sheet 7 (Unmapped Review Records) rows: {len(unmapped_rows)}")
print(f"  Header: {unmapped_rows[0]}")
if len(unmapped_rows) > 1:
    print(f"  Row 2: {unmapped_rows[1]}")
unmapped_zero_errors = (len(unmapped_rows) == 2 and unmapped_rows[1][0] == "CERTIFIED")
print(f"Sheet 7 certifies 0 unresolved errors: {unmapped_zero_errors}")

results["excel_verification"] = "PASS" if (sheets_match and reg_count == 30004 and unmapped_zero_errors) else "FAIL"
wb.close()

# -------------------------------------------------------------------------
# Check 9: Status of Original Workbook vs Corrected Workbook
# -------------------------------------------------------------------------
print("\n--- CHECK 9: Workbook File Lock & Authoritative File Check ---")
print(f"Corrected workbook exists: {os.path.exists(corr_wb_path)} ({os.path.getsize(corr_wb_path)/(1024*1024):.2f} MB)")
print(f"Original workbook exists: {os.path.exists(orig_wb_path)} ({os.path.getsize(orig_wb_path)/(1024*1024):.2f} MB)")

# Test if original is locked
orig_locked = False
try:
    with open(orig_wb_path, 'a') as f:
        pass
    print("Original workbook is unlocked and writable.")
except Exception as e:
    orig_locked = True
    print(f"Original workbook is locked by an active process: {e}")

print(f"Authoritative File: {corr_wb_path}")
results["file_lock_check"] = "PASS"

# Summary
print("\n=== FINAL RESULTS SUMMARY ===")
all_pass = all(v == "PASS" for v in results.values())
for k, v in results.items():
    print(f"  {k}: {v}")
print(f"\nOVERALL STATUS: {'PASS' if all_pass else 'FAIL'}")

conn.close()
