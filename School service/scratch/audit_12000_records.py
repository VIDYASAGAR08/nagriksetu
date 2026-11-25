import sqlite3
import pandas as pd

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== RECORD-LEVEL PRE-CORRECTION AUDIT ===")

# 1. Total counts
cur.execute("SELECT count(*) FROM students")
total_students = cur.fetchone()[0]
cur.execute("SELECT count(DISTINCT student_id), count(DISTINCT permanent_student_id) FROM students")
dist_sid, dist_psid = cur.fetchone()
print(f"Total students: {total_students}, Distinct Student IDs: {dist_sid}, Distinct PSIDs: {dist_psid}")

# 2. Check review flags in students
cur.execute("SELECT review_flag, count(*) FROM students GROUP BY review_flag")
print("\nStudents review_flag counts:")
for r in cur.fetchall():
    print(f"  {r['review_flag']}: {r[1]}")

# 3. Check review flags in enrollments
cur.execute("SELECT review_flag, count(*) FROM enrollments GROUP BY review_flag")
print("\nEnrollments review_flag counts:")
for r in cur.fetchall():
    print(f"  {r['review_flag']}: {r[1]}")

# 4. Check Group A: SCH011-SCH015
print("\n--- Group A: SCH011-SCH015 (PU Colleges with Standards 1-10) ---")
cur.execute("""
    SELECT school_id, standard, count(*), 
           min(student_id), max(student_id),
           count(DISTINCT student_id), count(DISTINCT permanent_student_id)
    FROM students
    WHERE school_id BETWEEN 'SCH011' AND 'SCH015' AND standard BETWEEN 1 AND 10
    GROUP BY school_id, standard
    ORDER BY school_id, standard
""")
group_a_rows = cur.fetchall()
df_a = pd.DataFrame([dict(r) for r in group_a_rows])
print(df_a.groupby('school_id')['count(*)'].sum())
print(f"Group A total records: {df_a['count(*)'].sum()}")

# 5. Check Group B: SCH016-SCH020
print("\n--- Group B: SCH016-SCH020 (Schools with Standards 11-12) ---")
cur.execute("""
    SELECT school_id, standard, count(*), 
           min(student_id), max(student_id),
           count(DISTINCT student_id), count(DISTINCT permanent_student_id)
    FROM students
    WHERE school_id BETWEEN 'SCH016' AND 'SCH020' AND standard BETWEEN 11 AND 12
    GROUP BY school_id, standard
    ORDER BY school_id, standard
""")
group_b_rows = cur.fetchall()
df_b = pd.DataFrame([dict(r) for r in group_b_rows])
print(df_b.groupby('school_id')['count(*)'].sum())
print(f"Group B total records: {df_b['count(*)'].sum()}")

# 6. Any other potential mismatches across entire DB?
cur.execute("""
    SELECT sc.school_id, sc.school_name, sc.category, sc.school_type, s.standard, count(*)
    FROM students s
    JOIN schools sc ON sc.school_id = s.school_id
    WHERE (
        -- School with std > 10 outside SCH016-SCH020
        (sc.category LIKE '%School%' AND s.standard > 10 AND sc.school_id NOT BETWEEN 'SCH016' AND 'SCH020')
        OR
        -- PU College with std <= 10 outside SCH011-SCH015
        (sc.category LIKE '%PU%' AND s.standard <= 10 AND sc.school_id NOT BETWEEN 'SCH011' AND 'SCH015')
        OR
        -- College/University with school standards
        (sc.category IN ('Degree Colleges', 'Universities') AND s.standard <= 10)
    )
    GROUP BY sc.school_id, s.standard
""")
other_mismatches = cur.fetchall()
print(f"\nOther unexpected mismatches outside SCH011-SCH020: {len(other_mismatches)}")
for r in other_mismatches:
    print(dict(r))

# 7. Check correlation between students and enrollments for the 12,000
cur.execute("""
    SELECT count(*)
    FROM students s
    JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
    WHERE (
        (s.school_id BETWEEN 'SCH011' AND 'SCH015' AND s.standard BETWEEN 1 AND 10)
        OR
        (s.school_id BETWEEN 'SCH016' AND 'SCH020' AND s.standard BETWEEN 11 AND 12)
    )
    AND s.standard = e.standard
    AND s.school_id = e.school_id
""")
matched_enrollments = cur.fetchone()[0]
print(f"\nFlagged students whose enrollments match 1:1 on PSID, School ID and Standard: {matched_enrollments} / 12000")

conn.close()
