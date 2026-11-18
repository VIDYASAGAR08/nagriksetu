import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.execute("PRAGMA foreign_keys = ON")

with conn:
    # 1. Student attendance table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_attendance (
            attendance_id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            permanent_student_id TEXT NOT NULL,
            academic_year TEXT NOT NULL DEFAULT '2026-2027',
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'leave')),
            subject_name TEXT,
            remarks TEXT,
            recorded_by_user_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES schools(school_id),
            FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id),
            FOREIGN KEY (recorded_by_user_id) REFERENCES users(user_id)
        )
    """)
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique
        ON student_attendance(institution_id, permanent_student_id, attendance_date, COALESCE(subject_name, ''))
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_student_date
        ON student_attendance(permanent_student_id, attendance_date)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_attendance_inst_date
        ON student_attendance(institution_id, attendance_date)
    """)

    # 2. Examinations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS examinations (
            exam_id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            academic_year TEXT NOT NULL DEFAULT '2026-2027',
            exam_name TEXT NOT NULL,
            standard_or_level TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'ongoing', 'completed', 'cancelled')),
            description TEXT,
            created_by_user_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES schools(school_id),
            FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_examinations_inst
        ON examinations(institution_id, academic_year)
    """)

    # 3. Add columns to academic_results if missing
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(academic_results)").fetchall()}
    for col, ctype in [
        ("permanent_student_id", "TEXT"),
        ("exam_id", "TEXT"),
        ("grade", "TEXT"),
        ("percentage", "REAL"),
        ("recorded_by_user_id", "TEXT"),
        ("updated_at", "TEXT")
    ]:
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE academic_results ADD COLUMN {col} {ctype}")

    # 4. Result audits table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS academic_result_audits (
            audit_id TEXT PRIMARY KEY,
            result_id TEXT NOT NULL,
            previous_marks REAL,
            new_marks REAL,
            previous_max_marks REAL,
            new_max_marks REAL,
            reason_for_change TEXT NOT NULL,
            modified_by_user_id TEXT NOT NULL,
            modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (result_id) REFERENCES academic_results(result_id),
            FOREIGN KEY (modified_by_user_id) REFERENCES users(user_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_result_audits
        ON academic_result_audits(result_id)
    """)

    # 5. Announcements table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS institution_announcements (
            announcement_id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            target_audience TEXT NOT NULL DEFAULT 'all' CHECK(target_audience IN ('all', 'students', 'parents', 'staff')),
            published_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by_user_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES schools(school_id),
            FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_announcements_inst
        ON institution_announcements(institution_id)
    """)

# Verify integrity and foreign keys
print("Integrity check:", conn.execute("PRAGMA integrity_check").fetchone()[0])
print("FK violations:", conn.execute("PRAGMA foreign_key_check").fetchall())

conn.close()
print("Phase 12 tables and columns successfully configured!")
