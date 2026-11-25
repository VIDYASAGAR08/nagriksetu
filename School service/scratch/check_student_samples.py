import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- Existing PU students in SCH011 (Standard 11-12) ---")
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, program_id, count(*)
    FROM students
    WHERE school_id = 'SCH011' AND standard IN (11, 12)
    GROUP BY standard, puc_year, stream, subject_combination, program_id
    ORDER BY standard, count(*) DESC
""")
for r in cur.fetchall():
    print(r)

print("\n--- Flagged PU students in SCH011 (Standard 1-10) ---")
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, program_id, review_flag, count(*)
    FROM students
    WHERE school_id = 'SCH011' AND standard BETWEEN 1 AND 10
    GROUP BY standard, puc_year, stream, subject_combination, program_id, review_flag
    ORDER BY standard
""")
for r in cur.fetchall():
    print(r)

print("\n--- Flagged School students in SCH016 (Standard 11-12) ---")
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, program_id, review_flag, count(*)
    FROM students
    WHERE school_id = 'SCH016' AND standard IN (11, 12)
    GROUP BY standard, puc_year, stream, subject_combination, program_id, review_flag
    ORDER BY standard
""")
for r in cur.fetchall():
    print(r)

conn.close()
