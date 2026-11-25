import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("=== CHECKING DEPENDENT RECORDS FOR 12,000 FLAGGED STUDENTS ===")

cur.execute("""
    SELECT 
        count(DISTINCT s.permanent_student_id) as student_count,
        count(a.attendance_id) as attendance_count,
        count(DISTINCT a.permanent_student_id) as students_with_attendance,
        count(r.result_id) as results_count,
        count(DISTINCT r.permanent_student_id) as students_with_results,
        count(d.document_id) as docs_count,
        count(DISTINCT d.permanent_student_id) as students_with_docs
    FROM students s
    LEFT JOIN student_attendance a ON a.permanent_student_id = s.permanent_student_id
    LEFT JOIN academic_results r ON r.permanent_student_id = s.permanent_student_id
    LEFT JOIN student_documents d ON d.permanent_student_id = s.permanent_student_id
    WHERE s.review_flag IS NOT NULL
""")
row = cur.fetchone()
print(f"Flagged students: {row[0]}")
print(f"Attendance count: {row[1]}, Students with attendance: {row[2]}")
print(f"Results count: {row[3]}, Students with results: {row[4]}")
print(f"Docs count: {row[5]}, Students with docs: {row[6]}")

# Also check guardians
cur.execute("""
    SELECT count(sg.student_guardian_id)
    FROM students s
    JOIN student_guardians sg ON sg.permanent_student_id = s.permanent_student_id
    WHERE s.review_flag IS NOT NULL
""")
print(f"Flagged students with linked guardians: {cur.fetchone()[0]}")

conn.close()
