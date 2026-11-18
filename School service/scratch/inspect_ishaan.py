import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

student_id = 'NS-SCH019-STD06-166'

# Query students table
s = cur.execute("""
    SELECT s.*, sch.school_name, sch.school_type, sch.district
    FROM students s
    JOIN schools sch ON sch.school_id = s.school_id
    WHERE s.student_id = ? OR s.permanent_student_id = ?
""", (student_id, student_id)).fetchone()

if s:
    print("Found student record:")
    print(dict(s))
else:
    print(f"Student {student_id} not found in students table!")
    # Look for Ishaan Verma
    matches = cur.execute("SELECT * FROM students WHERE student_name LIKE '%Ishaan%' OR student_name LIKE '%Verma%'").fetchall()
    print("Matches by name:")
    for m in matches:
        print(dict(m))

# Check if an account already exists in users table for this student
u = cur.execute("SELECT * FROM users WHERE student_id = ? OR permanent_student_id = ?", (student_id, student_id)).fetchone()
if u:
    print("\nExisting user account found:")
    print(dict(u))
else:
    print("\nNo user account found in users table for this student (NOT yet activated).")
