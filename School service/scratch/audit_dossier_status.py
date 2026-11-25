import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("--- Database Counts ---")
cur.execute("SELECT COUNT(*) FROM students")
total_students = cur.fetchone()[0]
print(f"Total students in DB: {total_students}")

cur.execute("SELECT COUNT(*) FROM students WHERE blood_group IS NOT NULL")
bg_count = cur.fetchone()[0]
print(f"Students with blood_group: {bg_count}")

cur.execute("SELECT COUNT(*) FROM students WHERE address IS NOT NULL")
addr_count = cur.fetchone()[0]
print(f"Students with address: {addr_count}")

cur.execute("SELECT COUNT(*) FROM enrollments")
enrollments_count = cur.fetchone()[0]
print(f"Total enrollments: {enrollments_count}")

cur.execute("SELECT COUNT(*) FROM academic_results")
results_count = cur.fetchone()[0]
print(f"Total academic_results: {results_count}")

cur.execute("SELECT COUNT(*) FROM student_attendance")
attendance_count = cur.fetchone()[0]
print(f"Total student_attendance: {attendance_count}")

cur.execute("SELECT COUNT(*) FROM student_documents")
docs_count = cur.fetchone()[0]
print(f"Total student_documents: {docs_count}")

cur.execute("SELECT COUNT(*) FROM examinations")
exams_count = cur.fetchone()[0]
print(f"Total examinations: {exams_count}")

cur.execute("SELECT COUNT(DISTINCT permanent_student_id) FROM student_attendance")
distinct_att = cur.fetchone()[0]
print(f"Distinct students with attendance: {distinct_att}")

cur.execute("SELECT COUNT(DISTINCT enrollment_id) FROM academic_results")
distinct_res = cur.fetchone()[0]
print(f"Distinct enrollments with results: {distinct_res}")

cur.execute("SELECT COUNT(DISTINCT permanent_student_id) FROM student_documents")
distinct_docs = cur.fetchone()[0]
print(f"Distinct students with documents: {distinct_docs}")

conn.close()
