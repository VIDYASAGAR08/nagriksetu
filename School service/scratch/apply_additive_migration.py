import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Create student_record_audits table
cur.execute("""
CREATE TABLE IF NOT EXISTS student_record_audits (
    audit_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    permanent_student_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    admin_user_id TEXT NOT NULL,
    admin_name TEXT,
    field_modified TEXT NOT NULL,
    previous_value TEXT,
    updated_value TEXT,
    reason TEXT NOT NULL,
    source TEXT NOT NULL,
    request_id TEXT,
    created_at TEXT NOT NULL
)
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_sra_student_id ON student_record_audits(student_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sra_psid ON student_record_audits(permanent_student_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sra_inst_id ON student_record_audits(institution_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sra_created_at ON student_record_audits(created_at)")

# 2. Additive columns for students
cur.execute("PRAGMA table_info(students)")
existing_cols = {c[1] for c in cur.fetchall()}

new_cols = [
    ("taluk", "TEXT"),
    ("village_city", "TEXT"),
    ("admission_number", "TEXT"),
    ("updated_at", "TEXT")
]

for col_name, col_type in new_cols:
    if col_name not in existing_cols:
        print(f"Adding column {col_name} to students...")
        cur.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")
    else:
        print(f"Column {col_name} already exists in students.")

# Also ensure enrollments has updated_at if needed
cur.execute("PRAGMA table_info(enrollments)")
existing_enr_cols = {c[1] for c in cur.fetchall()}
if "updated_at" not in existing_enr_cols:
    print("Adding updated_at to enrollments...")
    cur.execute("ALTER TABLE enrollments ADD COLUMN updated_at TEXT")

conn.commit()

# Verify counts
cur.execute("SELECT count(*) FROM students")
print("Total students after schema update:", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM student_record_audits")
print("Total rows in student_record_audits:", cur.fetchone()[0])

conn.close()
print("Additive migration completed successfully.")
