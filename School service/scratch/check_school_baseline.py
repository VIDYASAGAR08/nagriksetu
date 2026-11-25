import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- Standards 1-10 students in SCH016 ---")
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, program_id, review_flag, count(*)
    FROM students
    WHERE school_id = 'SCH016' AND standard BETWEEN 1 AND 10
    GROUP BY standard, puc_year, stream, subject_combination, program_id, review_flag
    ORDER BY standard
""")
for r in cur.fetchall():
    print(r)

print("\n--- Standards 1-10 students in SCH001 ---")
cur.execute("""
    SELECT standard, puc_year, stream, subject_combination, program_id, review_flag, count(*)
    FROM students
    WHERE school_id = 'SCH001' AND standard BETWEEN 1 AND 10
    GROUP BY standard, puc_year, stream, subject_combination, program_id, review_flag
    ORDER BY standard
""")
for r in cur.fetchall():
    print(r)

conn.close()
