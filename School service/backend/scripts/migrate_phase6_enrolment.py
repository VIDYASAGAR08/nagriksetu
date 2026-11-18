import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check existing columns in admission_applications
cols = [c[1] for c in cur.execute('PRAGMA table_info(admission_applications)').fetchall()]

if 'enrolled_student_id' not in cols:
    cur.execute('ALTER TABLE admission_applications ADD COLUMN enrolled_student_id TEXT')
    print("Added enrolled_student_id column.")

if 'enrolled_at' not in cols:
    cur.execute('ALTER TABLE admission_applications ADD COLUMN enrolled_at TEXT')
    print("Added enrolled_at column.")

conn.commit()
conn.close()
print("Migration for Phase 6 enrolment columns completed.")
