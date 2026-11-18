import sqlite3
import shutil
import time
import os
import sys

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
timestamp = int(time.time())
backup_path = f"{db_path}.pre_admissions_backup_{timestamp}"

print(f"=== PHASE 1: ADMISSIONS SCHEMA MIGRATION ===")
print(f"Target Database: {db_path}")

# 1. Create Pre-Migration Snapshot Backup
try:
    shutil.copy2(db_path, backup_path)
    print(f"[OK] Backup snapshot created: {backup_path} ({os.path.getsize(backup_path)} bytes)")
except Exception as e:
    print(f"[ERROR] Failed to create backup: {e}")
    sys.exit(1)

# 2. Connect and execute DDL inside transaction
try:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()

    # Pre-check baseline counts
    initial_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    initial_enrollments = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    initial_programs = c.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0]
    initial_sections = c.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0]
    initial_schools = c.execute("SELECT COUNT(*) FROM schools").fetchone()[0]

    print("\n--- Baseline Counts Prior to Migration ---")
    print(f"Students: {initial_students}")
    print(f"Enrollments: {initial_enrollments}")
    print(f"Programs: {initial_programs}")
    print(f"Sections: {initial_sections}")
    print(f"Schools: {initial_schools}")

    assert initial_students == 30000, "Students baseline mismatch!"
    assert initial_enrollments == 30000, "Enrollments baseline mismatch!"
    assert initial_programs == 198, "Programs baseline mismatch!"
    assert initial_sections == 841, "Sections baseline mismatch!"
    assert initial_schools == 30, "Schools baseline mismatch!"

    # 3. Create Table 1: admission_applications
    c.execute("""
    CREATE TABLE IF NOT EXISTS admission_applications (
        application_id VARCHAR(50) PRIMARY KEY,
        institution_id VARCHAR(20) NOT NULL,
        division_id VARCHAR(50) DEFAULT NULL,
        parent_user_id VARCHAR(50) DEFAULT NULL,
        applicant_name VARCHAR(150) NOT NULL,
        parent_name VARCHAR(150) NOT NULL,
        parent_phone VARCHAR(20) NOT NULL,
        parent_email VARCHAR(100),
        residential_address TEXT NOT NULL,
        academic_year VARCHAR(20) NOT NULL,
        education_level VARCHAR(50) NOT NULL,
        requested_standard INTEGER DEFAULT NULL,
        requested_program_id VARCHAR(50) DEFAULT NULL,
        first_language_preference VARCHAR(50) DEFAULT NULL,
        stream_preference VARCHAR(50) DEFAULT NULL,
        combination_code VARCHAR(20) DEFAULT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'submitted',
        reviewer_user_id VARCHAR(50) DEFAULT NULL,
        rejection_reason TEXT DEFAULT NULL,
        rejection_explanation TEXT DEFAULT NULL,
        institution_contact_phone VARCHAR(50) DEFAULT NULL,
        clarification_request TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (institution_id) REFERENCES schools(school_id) ON DELETE RESTRICT,
        FOREIGN KEY (requested_program_id) REFERENCES academic_programs(program_id) ON DELETE RESTRICT
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_app_inst ON admission_applications(institution_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_app_parent ON admission_applications(parent_user_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_app_phone ON admission_applications(parent_phone);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_app_status ON admission_applications(status);")
    print("[OK] Created table and indexes: admission_applications")

    # 4. Create Table 2: admission_detailed_submissions
    c.execute("""
    CREATE TABLE IF NOT EXISTS admission_detailed_submissions (
        submission_id VARCHAR(50) PRIMARY KEY,
        application_id VARCHAR(50) UNIQUE NOT NULL,
        date_of_birth DATE,
        gender VARCHAR(20),
        blood_group VARCHAR(10),
        previous_institution_name VARCHAR(255),
        previous_institution_location VARCHAR(255),
        previous_standard_or_degree VARCHAR(100),
        previous_board VARCHAR(100),
        previous_marks_percentage REAL,
        emergency_contact_name VARCHAR(100),
        emergency_contact_phone VARCHAR(20),
        custom_fields_json TEXT,
        status VARCHAR(50) NOT NULL DEFAULT 'submitted',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES admission_applications(application_id) ON DELETE CASCADE
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_detailed_app ON admission_detailed_submissions(application_id);")
    print("[OK] Created table and indexes: admission_detailed_submissions")

    # 5. Create Table 3: admission_documents
    c.execute("""
    CREATE TABLE IF NOT EXISTS admission_documents (
        document_id VARCHAR(50) PRIMARY KEY,
        application_id VARCHAR(50) NOT NULL,
        document_type VARCHAR(100) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        mime_type VARCHAR(100) NOT NULL,
        verification_status VARCHAR(50) DEFAULT 'pending',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES admission_applications(application_id) ON DELETE CASCADE
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_doc_app ON admission_documents(application_id);")
    print("[OK] Created table and indexes: admission_documents")

    # 6. Create Table 4: portal_notifications
    c.execute("""
    CREATE TABLE IF NOT EXISTS portal_notifications (
        notification_id VARCHAR(50) PRIMARY KEY,
        recipient_user_id VARCHAR(50) DEFAULT NULL,
        recipient_role VARCHAR(50) DEFAULT NULL,
        institution_id VARCHAR(20) DEFAULT NULL,
        application_id VARCHAR(50) DEFAULT NULL,
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        action_url VARCHAR(255),
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_notif_user ON portal_notifications(recipient_user_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_notif_inst ON portal_notifications(institution_id);")
    print("[OK] Created table and indexes: portal_notifications")

    # 7. Create Table 5: admission_status_history
    c.execute("""
    CREATE TABLE IF NOT EXISTS admission_status_history (
        history_id VARCHAR(50) PRIMARY KEY,
        application_id VARCHAR(50) NOT NULL,
        previous_status VARCHAR(50),
        new_status VARCHAR(50) NOT NULL,
        action_by_user_id VARCHAR(50) NOT NULL,
        action_note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES admission_applications(application_id) ON DELETE CASCADE
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_adm_hist_app ON admission_status_history(application_id);")
    print("[OK] Created table and indexes: admission_status_history")

    # Commit Transaction
    conn.commit()

    # 8. Post-Migration Verification Gate
    print("\n--- Post-Migration Automated Verification Gate ---")
    post_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    post_enrollments = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    post_programs = c.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0]
    post_sections = c.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0]
    post_schools = c.execute("SELECT COUNT(*) FROM schools").fetchone()[0]

    integ = c.execute("PRAGMA integrity_check;").fetchone()[0]
    fk = c.execute("PRAGMA foreign_key_check;").fetchall()

    print(f"Students count: {post_students} (Expected: 30000)")
    print(f"Enrollments count: {post_enrollments} (Expected: 30000)")
    print(f"Programs count: {post_programs} (Expected: 198)")
    print(f"Sections count: {post_sections} (Expected: 841)")
    print(f"Schools count: {post_schools} (Expected: 30)")
    print(f"PRAGMA integrity_check: {integ}")
    print(f"PRAGMA foreign_key_check: {fk}")

    assert post_students == 30000, "CRITICAL ERROR: Students count changed!"
    assert post_enrollments == 30000, "CRITICAL ERROR: Enrollments count changed!"
    assert post_programs == 198, "CRITICAL ERROR: Programs count changed!"
    assert post_sections == 841, "CRITICAL ERROR: Sections count changed!"
    assert post_schools == 30, "CRITICAL ERROR: Schools count changed!"
    assert integ == "ok", f"Integrity check failed: {integ}"
    assert len(fk) == 0, f"Foreign key check failed: {fk}"

    print("\n[SUCCESS] Phase 1 Schema Migration Verified 100% Intact.")
    conn.close()

except Exception as err:
    print(f"\n[FATAL ERROR] Migration failed: {err}")
    print("[ACTION] Initiating automatic rollback from snapshot...")
    if 'conn' in locals() and conn:
        conn.close()
    shutil.copy2(backup_path, db_path)
    print(f"[RECOVERY COMPLETE] Database restored from {backup_path}")
    sys.exit(1)
