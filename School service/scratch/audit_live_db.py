import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Tables list
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print('Tables in DB:', tables)

# Baselines check
check_tables = [
    'schools', 'students', 'enrollments', 'academic_programs', 
    'institution_divisions', 'student_attendance', 'academic_results', 
    'student_documents', 'student_guardians'
]
for tbl in check_tables:
    if tbl in tables:
        cur.execute(f"SELECT count(*) FROM {tbl}")
        print(f"{tbl}: {cur.fetchone()[0]} rows")
    else:
        print(f"{tbl}: NOT FOUND")

# PRAGMA checks
cur.execute('PRAGMA integrity_check')
print('integrity_check:', cur.fetchall())
cur.execute('PRAGMA foreign_key_check')
print('foreign_key_check:', cur.fetchall())

# Inspect schema of students, enrollments, schools, academic_programs, institution_divisions
for tbl in ['students', 'enrollments', 'schools', 'academic_programs', 'institution_divisions']:
    if tbl in tables:
        cur.execute(f"PRAGMA table_info({tbl})")
        cols = [c[1] for c in cur.fetchall()]
        print(f"Columns in {tbl}:", cols)

# Audit the 12,000 flagged records
cur.execute("""
    SELECT count(*) FROM students 
    WHERE school_id BETWEEN 'SCH011' AND 'SCH015' AND standard BETWEEN 1 AND 10
""")
group_a_students = cur.fetchone()[0]

cur.execute("""
    SELECT count(*) FROM students 
    WHERE school_id BETWEEN 'SCH016' AND 'SCH020' AND standard BETWEEN 11 AND 12
""")
group_b_students = cur.fetchone()[0]

print(f"Group A (SCH011-SCH015, Std 1-10): {group_a_students}")
print(f"Group B (SCH016-SCH020, Std 11-12): {group_b_students}")
print(f"Total flagged candidates: {group_a_students + group_b_students}")

# Check review_flag in students if present
cur.execute("PRAGMA table_info(students)")
cols = [c[1] for c in cur.fetchall()]
if 'review_flag' in cols:
    cur.execute("SELECT review_flag, count(*) FROM students GROUP BY review_flag")
    print("review_flag distribution in students:", cur.fetchall())

conn.close()
