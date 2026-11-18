import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Checking columns named student_id or similar in tables:")
for t in tables:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
    matching = [col for col in cols if "student" in col.lower()]
    if matching:
        print(f"{t:30}: {matching}")

print("\n--- Foreign keys on all tables ---")
for t in tables:
    fks = c.execute(f"PRAGMA foreign_key_list({t})").fetchall()
    for fk in fks:
        if "student" in fk[2].lower() or "student" in fk[3].lower():
            print(f"{t} -> references {fk[2]}({fk[3]}) via {fk[4]}")

print("\n--- Check distinct student_id formats in students table ---")
sample_ids = c.execute("SELECT student_id FROM students LIMIT 10").fetchall()
print("Sample student_ids:", sample_ids)

# Check total count of student IDs
total_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
unique_student_ids = c.execute("SELECT COUNT(DISTINCT student_id) FROM students").fetchone()[0]
print(f"Total students: {total_students}, Unique student_ids: {unique_student_ids}")

# Check users table references
users_with_student_id = c.execute("SELECT user_id, email, role, student_id, permanent_student_id FROM users WHERE student_id IS NOT NULL").fetchall()
print(f"Users with student_id: {users_with_student_id}")

conn.close()
