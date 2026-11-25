import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("""
    SELECT s.school_id, COUNT(*)
    FROM students s
    WHERE s.permanent_student_id NOT IN (SELECT DISTINCT permanent_student_id FROM student_attendance)
    GROUP BY s.school_id
""")
print("Students missing attendance by school:", cur.fetchall())

cur.execute("""
    SELECT s.school_id, COUNT(*)
    FROM students s
    WHERE s.permanent_student_id NOT IN (SELECT DISTINCT permanent_student_id FROM academic_results)
    GROUP BY s.school_id
""")
print("Students missing results by school:", cur.fetchall())

cur.execute("""
    SELECT s.school_id, COUNT(*)
    FROM students s
    WHERE s.permanent_student_id NOT IN (SELECT DISTINCT permanent_student_id FROM student_documents)
    GROUP BY s.school_id
""")
print("Students missing documents by school:", cur.fetchall())

conn.close()
