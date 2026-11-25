import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("--- Check COL003 students ---")
cur.execute("SELECT * FROM students WHERE school_id='COL003'")
for r in cur.fetchall():
    print(r)

print("\n--- Check COL003 enrollments ---")
cur.execute("SELECT * FROM enrollments WHERE school_id='COL003'")
for r in cur.fetchall():
    print(r)

print("\n--- Check COL003 results ---")
cur.execute("SELECT * FROM academic_results WHERE permanent_student_id IN (SELECT permanent_student_id FROM students WHERE school_id='COL003')")
for r in cur.fetchall():
    print(r)

conn.close()
