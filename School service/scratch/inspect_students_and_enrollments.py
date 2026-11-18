import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check SCH011 students
print("--- SCH011 Students ---")
cur.execute("SELECT standard, section, count(*) FROM students WHERE school_id = 'SCH011' GROUP BY standard, section")
for r in cur.fetchall():
    print(dict(r))

# Check enrollments for SCH011
print("\n--- SCH011 Enrollments ---")
cur.execute("SELECT standard, section, stream, subject_combination, count(*) FROM enrollments WHERE school_id = 'SCH011' GROUP BY standard, section, stream, subject_combination")
for r in cur.fetchall():
    print(dict(r))

# Check if there are students in collegiate_enrollments or schools starting with COL
print("\n--- COL003 students & enrollments ---")
for s in cur.execute("SELECT * FROM students WHERE school_id = 'COL003'").fetchall():
    print("Student:", dict(s))
for e in cur.execute("SELECT * FROM enrollments WHERE school_id = 'COL003'").fetchall():
    print("Enrollment:", dict(e))

print("\n--- COL001 to COL010 students in students table ---")
for col_id in [f"COL{i:03d}" for i in range(1, 11)]:
    c = cur.execute("SELECT count(*) FROM students WHERE school_id = ?", (col_id,)).fetchone()[0]
    e = cur.execute("SELECT count(*) FROM enrollments WHERE school_id = ?", (col_id,)).fetchone()[0]
    print(f"{col_id}: {c} students, {e} enrollments")

conn.close()
