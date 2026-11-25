import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- Sample student in SCH001 ---")
cur.execute("SELECT student_id, standard, curriculum_or_board, degree, branch, department, semester, puc_year, stream, subject_combination, program_id, review_flag FROM students WHERE school_id = 'SCH001' LIMIT 2")
for r in cur.fetchall():
    print(r)

print("\n--- Sample enrollment in SCH001 ---")
cur.execute("SELECT enrollment_id, permanent_student_id, standard, curriculum_or_board, degree, branch, department, semester, puc_year, stream, subject_combination, program_id, review_flag FROM enrollments WHERE school_id = 'SCH001' LIMIT 2")
for r in cur.fetchall():
    print(r)

print("\n--- Sample student in SCH011 (PU student: std 11) ---")
cur.execute("SELECT student_id, standard, curriculum_or_board, degree, branch, department, semester, puc_year, stream, subject_combination, program_id, review_flag FROM students WHERE school_id = 'SCH011' AND standard = 11 LIMIT 2")
for r in cur.fetchall():
    print(r)

print("\n--- Sample enrollment in SCH011 (PU student: std 11) ---")
cur.execute("SELECT enrollment_id, permanent_student_id, standard, curriculum_or_board, degree, branch, department, semester, puc_year, stream, subject_combination, program_id, review_flag FROM enrollments WHERE school_id = 'SCH011' AND standard = 11 LIMIT 2")
for r in cur.fetchall():
    print(r)

conn.close()
