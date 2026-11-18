import sqlite3
c = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
print('users student sample:', c.execute("SELECT user_id, permanent_student_id, student_id FROM users WHERE role='student' LIMIT 5").fetchall())
print('student_guardians sample:', c.execute("SELECT permanent_student_id, guardian_id FROM student_guardians LIMIT 5").fetchall())
print('enrollments sample:', c.execute("SELECT student_id, permanent_student_id FROM enrollments LIMIT 5").fetchall())
