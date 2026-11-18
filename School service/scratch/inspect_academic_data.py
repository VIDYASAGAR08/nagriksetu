import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check institution_divisions
print("--- institution_divisions ---")
div_cols = [c[1] for c in cur.execute("PRAGMA table_info(institution_divisions)").fetchall()]
print("cols:", div_cols)
for r in cur.execute("SELECT * FROM institution_divisions LIMIT 10").fetchall():
    print(dict(r))

# Check distinct school_type in schools
print("\n--- Schools types & counts ---")
for r in cur.execute("SELECT school_type, count(*) FROM schools GROUP BY school_type").fetchall():
    print(dict(r))

# Check academic_programs breakdown by education_level and degree_type
print("\n--- academic_programs breakdown ---")
for r in cur.execute("SELECT education_level, degree_type, discipline_or_stream, count(*) FROM academic_programs GROUP BY education_level, degree_type, discipline_or_stream").fetchall():
    print(dict(r))

# Check sample academic_programs for PU colleges and Universities / Degree Colleges
print("\n--- Sample academic_programs for non-schools ---")
for r in cur.execute("SELECT * FROM academic_programs WHERE education_level != 'school' LIMIT 15").fetchall():
    print(dict(r))

# Check students table columns and samples for collegiate/PU
print("\n--- students columns ---")
std_cols = [c[1] for c in cur.execute("PRAGMA table_info(students)").fetchall()]
print(std_cols)

print("\n--- Sample students with non-null stream, combination, program_id, etc ---")
sample_std = cur.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard, section, stream, subject_combination, program_id, current_year_or_term, current_semester FROM students WHERE stream IS NOT NULL OR program_id IS NOT NULL LIMIT 10").fetchall()
for s in sample_std:
    print(dict(s))

conn.close()
