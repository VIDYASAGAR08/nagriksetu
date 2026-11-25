import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(student_id), COUNT(DISTINCT student_id), COUNT(permanent_student_id), COUNT(DISTINCT permanent_student_id) FROM students')
print("Counts:", cur.fetchone())
conn.close()
