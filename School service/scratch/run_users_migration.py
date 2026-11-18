import sqlite3
import uuid
from pwdlib import PasswordHash

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("PRAGMA foreign_keys = OFF")
c.execute("BEGIN TRANSACTION")

# 1. Create new table with updated CHECK constraint allowing 'student'
c.execute("""
CREATE TABLE users_new (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (
        role IN ('parent', 'school_staff', 'school_admin', 'platform_admin', 'student')
    ),
    school_id TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    full_name TEXT,
    status TEXT DEFAULT 'active',
    last_login TEXT,
    permanent_student_id TEXT,
    student_id TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
)
""")

# 2. Copy existing data
c.execute("""
INSERT INTO users_new (
    user_id, email, phone, password_hash, role,
    school_id, is_active, created_at, full_name,
    status, last_login, permanent_student_id, student_id
)
SELECT 
    user_id, email, phone, password_hash, role,
    school_id, is_active, created_at, full_name,
    status, last_login, permanent_student_id, student_id
FROM users
""")

# 3. Swap tables
c.execute("DROP TABLE users")
c.execute("ALTER TABLE users_new RENAME TO users")

# 4. Create index on student_id and permanent_student_id for fast student lookup
c.execute("CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_users_perm_student_id ON users(permanent_student_id)")

# 5. Insert demo student user
demo_student_id = "SCH001-STD01-001"
student_row = c.execute(
    "SELECT student_id, student_name, school_id, standard, section, permanent_student_id FROM students WHERE student_id = ?",
    (demo_student_id,)
).fetchone()

if student_row:
    s_id, s_name, sch_id, std, sec, perm_id = student_row
    password_hash_engine = PasswordHash.recommended()
    hashed_pwd = password_hash_engine.hash("Password@2026!")

    new_user_id = str(uuid.uuid4())
    c.execute(
        """
        INSERT INTO users (
            user_id, email, phone, password_hash, role,
            school_id, is_active, status, full_name,
            permanent_student_id, student_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            new_user_id,
            "student.asha@example.com",
            "9876543299",
            hashed_pwd,
            "student",
            sch_id,
            1,
            "active",
            s_name,
            perm_id,
            s_id
        )
    )
    print(f"Provisioned demo student user {s_name} ({s_id})")

c.execute("COMMIT")
c.execute("PRAGMA foreign_keys = ON")

# Verify integrity
integrity = c.execute("PRAGMA integrity_check").fetchall()
print("Integrity check:", integrity)

fk_violations = c.execute("PRAGMA foreign_key_check").fetchall()
print("Foreign key check:", fk_violations)

print("Total institutions:", c.execute("SELECT COUNT(*) FROM schools").fetchone()[0])
print("Total students in students table:", c.execute("SELECT COUNT(*) FROM students").fetchone()[0])
print("Total enrollments in enrollments table:", c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0])
print("Total applications:", c.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0])
print("Users distribution by role:", c.execute("SELECT role, COUNT(*) FROM users GROUP BY role").fetchall())

conn.close()
