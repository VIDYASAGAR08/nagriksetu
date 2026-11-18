"""
apply_institution_admin_schema.py
Applies normalized institution administration tables, invitation tokens,
password reset tokens, and backfills existing institutional accounts.
"""

import sqlite3
import uuid
import sys

DB_PATH = "backend/data/nagriksetu.db"

def apply_migration():
    print("[*] Connecting to SQLite database at", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor = conn.cursor()

        # 1. Inspect existing columns in users
        user_cols = [c[1] for c in cursor.execute("PRAGMA table_info(users)").fetchall()]
        if "status" not in user_cols:
            print("[+] Adding 'status' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
        if "last_login" not in user_cols:
            print("[+] Adding 'last_login' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")

        # 2. Create user_institution_roles table
        print("[+] Ensuring user_institution_roles table exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_institution_roles (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            institution_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (institution_id) REFERENCES schools(school_id) ON DELETE CASCADE
        );
        """)
        cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_inst_role 
        ON user_institution_roles(user_id, institution_id, role_id);
        """)

        # 3. Create invitation_tokens table
        print("[+] Ensuring invitation_tokens table exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitation_tokens (
            token_id TEXT PRIMARY KEY,
            token_hash TEXT NOT NULL UNIQUE,
            user_id TEXT NOT NULL,
            institution_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_used INTEGER DEFAULT 0,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (institution_id) REFERENCES schools(school_id) ON DELETE CASCADE
        );
        """)

        # 4. Create password_reset_tokens table
        print("[+] Ensuring password_reset_tokens table exists...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            reset_id TEXT PRIMARY KEY,
            token_hash TEXT NOT NULL UNIQUE,
            user_id TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_used INTEGER DEFAULT 0,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)

        # 5. Backfill existing school_admin and school_staff users
        print("[+] Backfilling existing institutional users into user_institution_roles...")
        users = cursor.execute("""
            SELECT user_id, role, school_id 
            FROM users 
            WHERE school_id IS NOT NULL AND role IN ('school_admin', 'school_staff')
        """).fetchall()

        backfilled = 0
        for uid, role, sch_id in users:
            # Check if mapping already exists
            existing = cursor.execute("""
                SELECT id FROM user_institution_roles 
                WHERE user_id = ? AND institution_id = ? AND role_id = ?
            """, (uid, sch_id, role)).fetchone()

            if not existing:
                role_pk = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
                    VALUES (?, ?, ?, ?, 'active', 'system_migration')
                """, (role_pk, uid, sch_id, role))
                backfilled += 1

        print(f"    -> Backfilled {backfilled} institutional user roles.")

        conn.commit()

        # 6. Integrity check
        print("[*] Running PRAGMA integrity_check...")
        integrity = cursor.execute("PRAGMA integrity_check").fetchall()
        assert integrity == [("ok",)], f"Integrity check failed: {integrity}"

        print("[*] Running PRAGMA foreign_key_check...")
        fk_check = cursor.execute("PRAGMA foreign_key_check").fetchall()
        assert fk_check == [], f"Foreign key violations found: {fk_check}"

        # 7. Baseline verification
        stud_cnt = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        enr_cnt = cursor.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
        sch_cnt = cursor.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
        print(f"[*] Verified counts: {stud_cnt} students, {enr_cnt} enrollments, {sch_cnt} schools.")
        assert stud_cnt == 30001, f"Expected 30001 students, got {stud_cnt}"
        assert enr_cnt == 30001, f"Expected 30001 enrollments, got {enr_cnt}"
        assert sch_cnt == 30, f"Expected 30 schools, got {sch_cnt}"

        print("\n[SUCCESS] Institution administration schema applied and verified successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
