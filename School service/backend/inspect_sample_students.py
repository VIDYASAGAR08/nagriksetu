import sqlite3

conn = sqlite3.connect("data/nagriksetu.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- STUDENTS TABLE SCHEMA ---")
for col in cursor.execute("PRAGMA table_info(students)").fetchall():
    print(f"  {col['name']} ({col['type']})")

print("\n--- SAMPLE STUDENT FROM SCH001 (School) ---")
s1 = cursor.execute("SELECT * FROM students WHERE school_id = 'SCH001' LIMIT 1").fetchone()
print(dict(s1))

print("\n--- SAMPLE STUDENT FROM SCH011 (PU College) ---")
s2 = cursor.execute("SELECT * FROM students WHERE school_id = 'SCH011' LIMIT 1").fetchone()
print(dict(s2))

print("\n--- SAMPLE STUDENT FROM COL003 (Degree College) ---")
s3 = cursor.execute("SELECT * FROM students WHERE school_id = 'COL003' LIMIT 1").fetchone()
print(dict(s3))

print("\n--- ENROLLMENTS TABLE SCHEMA ---")
for col in cursor.execute("PRAGMA table_info(enrollments)").fetchall():
    print(f"  {col['name']} ({col['type']})")

print("\n--- SAMPLE ENROLLMENTS ---")
e1 = cursor.execute("SELECT * FROM enrollments WHERE permanent_student_id = ?", (s1["permanent_student_id"],)).fetchone()
print("School enrollment:", dict(e1) if e1 else "None")
e2 = cursor.execute("SELECT * FROM enrollments WHERE permanent_student_id = ?", (s2["permanent_student_id"],)).fetchone()
print("PU enrollment:", dict(e2) if e2 else "None")
e3 = cursor.execute("SELECT * FROM enrollments WHERE permanent_student_id = ?", (s3["permanent_student_id"],)).fetchone()
print("Degree enrollment:", dict(e3) if e3 else "None")

conn.close()
