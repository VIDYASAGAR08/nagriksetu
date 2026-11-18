import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

student_id = 'NS-SCH019-STD06-166'

# PRAGMA table_info of students
print("students columns:")
for col in cur.execute("PRAGMA table_info(students)").fetchall():
    print(" ", col[1], col[2])

# Check student_guardians or guardians
guardians = cur.execute("""
    SELECT sg.*, g.full_name, g.phone, g.email, g.relationship
    FROM student_guardians sg
    JOIN guardians g ON g.guardian_id = sg.guardian_id
    WHERE sg.permanent_student_id = ?
""", (student_id,)).fetchall()
print("\nLinked guardians:")
for g in guardians:
    print(" ", dict(g))

# Check any other tables with permanent_student_id or student_id
tables_with_sid = []
for t in [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})").fetchall()]
    if 'student_id' in cols or 'permanent_student_id' in cols:
        tables_with_sid.append((t, cols))
print("\nTables with student_id / permanent_student_id:")
for t, cols in tables_with_sid:
    print(f" {t}")
