import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM students")
print("Total students:", cur.fetchone()[0])

cur.execute("SELECT review_flag, COUNT(*) FROM students GROUP BY review_flag")
print("Review flags:", cur.fetchall())

cur.execute("SELECT COUNT(*) FROM enrollments")
print("Enrollments:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM student_attendance")
print("Attendance rows:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM academic_results")
print("Academic result rows:", cur.fetchone()[0])

conn.close()
