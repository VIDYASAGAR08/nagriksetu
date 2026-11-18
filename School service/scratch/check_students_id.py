import sqlite3
c = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
print([col[1] for col in c.execute('PRAGMA table_info(students)').fetchall()])
row = c.execute("SELECT student_id, permanent_student_id, student_name FROM students WHERE school_id='SCH001' LIMIT 5").fetchall()
print(row)
