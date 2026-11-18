import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

print("--- Tables ---")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(tables)

print("\n--- Distinct User Roles ---")
print(c.execute("SELECT DISTINCT role, count(*) FROM users GROUP BY role").fetchall())

print("\n--- Users Columns ---")
print([col[1] for col in c.execute("PRAGMA table_info(users)").fetchall()])

print("\n--- Students Columns ---")
print([col[1] for col in c.execute("PRAGMA table_info(students)").fetchall()])

print("\n--- Sample Student ---")
sample_stu = c.execute("SELECT * FROM students LIMIT 2").fetchall()
for s in sample_stu:
    print(s)

print("\n--- Student Enrollments Sample ---")
if 'enrollments' in tables:
    print([col[1] for col in c.execute("PRAGMA table_info(enrollments)").fetchall()])
    for e in c.execute("SELECT * FROM enrollments LIMIT 2").fetchall():
        print(e)

print("\n--- Check if student user exists in users table ---")
print(c.execute("SELECT * FROM users WHERE role='student' LIMIT 5").fetchall())

conn.close()
