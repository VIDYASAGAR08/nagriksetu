import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

# Find students from SCH001 or SCH011
students = c.execute("""
    SELECT student_id, permanent_student_id, student_name, school_id, standard, section
    FROM students
    WHERE school_id IN ('SCH001', 'SCH011')
    ORDER BY student_id ASC
    LIMIT 20
""").fetchall()

for s in students:
    print(s)

conn.close()
