import sqlite3
import uuid
from pwdlib import PasswordHash

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Check existing columns in users
cols = [col[1] for col in c.execute("PRAGMA table_info(users)").fetchall()]
print("Current users columns:", cols)

if "permanent_student_id" not in cols:
    print("Adding permanent_student_id column to users...")
    c.execute("ALTER TABLE users ADD COLUMN permanent_student_id TEXT")

if "student_id" not in cols:
    print("Adding student_id column to users...")
    c.execute("ALTER TABLE users ADD COLUMN student_id TEXT")

conn.commit()

# 2. Check if demo student exists
demo_student_id = "SCH001-STD01-001"
student_row = c.execute(
    "SELECT student_id, student_name, school_id, standard, section, permanent_student_id FROM students WHERE student_id = ?",
    (demo_student_id,)
).fetchone()

print("Found student record in students:", student_row)
if student_row:
    s_id, s_name, sch_id, std, sec, perm_id = student_row
    existing_user = c.execute(
        "SELECT user_id, email, role FROM users WHERE student_id = ? OR permanent_student_id = ?",
        (s_id, perm_id)
    ).fetchone()

    password_hash_engine = PasswordHash.recommended()
    hashed_pwd = password_hash_engine.hash("Password@2026!")

    if not existing_user:
        new_user_id = str(uuid.uuid4())
        print(f"Creating demo student user {new_user_id} for {s_name}...")
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
        conn.commit()
        print("Demo student user created successfully.")
    else:
        print("Demo student user already exists:", existing_user)

# 3. Verify counts
print("Total institutions:", c.execute("SELECT COUNT(*) FROM schools").fetchone()[0])
print("Total students in students table:", c.execute("SELECT COUNT(*) FROM students").fetchone()[0])
print("Total enrollments:", c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0])
print("Total applications:", c.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0])
print("Total student users:", c.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0])

conn.close()
