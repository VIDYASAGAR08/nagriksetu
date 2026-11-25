import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

names = c.execute("""
    SELECT student_id, permanent_student_id, student_name, standard, section, school_id
    FROM students
    WHERE student_name LIKE '%Kumar%' OR student_name LIKE '%Sharma%' OR student_name LIKE '%Patil%'
    LIMIT 25
""").fetchall()

for n in names:
    print(n)

conn.close()
