import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Existing activated students
activated = cur.execute("SELECT u.user_id, u.student_id, u.permanent_student_id, u.full_name, u.role FROM users u WHERE u.role = 'student' LIMIT 3").fetchall()
print("Activated students:")
for a in activated:
    print(dict(a))

# 2. Inactive students
inactive = cur.execute("SELECT student_id, permanent_student_id, student_name, enrollment_status FROM students WHERE enrollment_status != 'active' LIMIT 3").fetchall()
print("\nInactive students:")
for i in inactive:
    print(dict(i))

# 3. Students without DOB
no_dob = cur.execute("SELECT student_id, permanent_student_id, student_name, date_of_birth FROM students WHERE date_of_birth IS NULL OR date_of_birth = '' LIMIT 3").fetchall()
print("\nStudents without DOB:")
for nd in no_dob:
    print(dict(nd))
