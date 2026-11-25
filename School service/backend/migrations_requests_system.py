import sqlite3
import os

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def run_migrations():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 1. service_requests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS service_requests (
        request_id TEXT PRIMARY KEY,
        tracking_number TEXT UNIQUE,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        requester_user_id TEXT NOT NULL,
        requester_role TEXT NOT NULL,
        requester_name TEXT,
        requester_email TEXT,
        requester_phone TEXT,
        affected_person_type TEXT DEFAULT 'self',
        affected_student_id TEXT,
        permanent_student_id TEXT,
        affected_person_name TEXT,
        institution_id TEXT,
        target_module TEXT,
        target_record_id TEXT,
        field_name TEXT,
        current_value TEXT,
        requested_value TEXT,
        status TEXT NOT NULL DEFAULT 'SUBMITTED',
        routing_tier TEXT NOT NULL DEFAULT 'institution',
        assigned_institution_id TEXT,
        assigned_to_user_id TEXT,
        rejection_reason TEXT,
        clarification_prompt TEXT,
        requester_response TEXT,
        is_escalated INTEGER DEFAULT 0,
        escalated_to TEXT,
        escalated_at TEXT,
        submitted_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        resolved_at TEXT,
        closed_at TEXT
    )
    """)

    # Indexes on service_requests
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sr_requester ON service_requests(requester_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sr_inst ON service_requests(assigned_institution_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sr_status ON service_requests(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sr_student ON service_requests(permanent_student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sr_st_id ON service_requests(affected_student_id)")

    # 2. request_attachments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_attachments (
        attachment_id TEXT PRIMARY KEY,
        request_id TEXT NOT NULL,
        uploaded_by_user_id TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_type TEXT,
        file_size INTEGER,
        file_url_or_path TEXT,
        purpose TEXT DEFAULT 'supporting_document',
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ra_req ON request_attachments(request_id)")

    # 3. request_remarks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_remarks (
        remark_id TEXT PRIMARY KEY,
        request_id TEXT NOT NULL,
        author_user_id TEXT NOT NULL,
        author_name TEXT NOT NULL,
        author_role TEXT NOT NULL,
        message TEXT NOT NULL,
        visibility TEXT NOT NULL DEFAULT 'requester_visible',
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rr_req ON request_remarks(request_id)")

    # 4. request_status_history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_status_history (
        history_id TEXT PRIMARY KEY,
        request_id TEXT NOT NULL,
        from_status TEXT,
        to_status TEXT NOT NULL,
        action TEXT NOT NULL,
        actor_user_id TEXT NOT NULL,
        actor_name TEXT,
        actor_role TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rsh_req ON request_status_history(request_id)")

    # 5. request_corrections
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_corrections (
        correction_id TEXT PRIMARY KEY,
        request_id TEXT NOT NULL,
        target_table TEXT NOT NULL,
        target_record_id TEXT NOT NULL,
        field_name TEXT NOT NULL,
        previous_value TEXT,
        corrected_value TEXT NOT NULL,
        correction_reason TEXT NOT NULL,
        administrator_id TEXT NOT NULL,
        administrator_name TEXT,
        administrator_role TEXT,
        verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
        verified_by_user_id TEXT,
        verified_at TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rc_req ON request_corrections(request_id)")

    # 6. request_audit_logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_audit_logs (
        audit_id TEXT PRIMARY KEY,
        request_id TEXT,
        actor_user_id TEXT,
        actor_role TEXT,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        school_id TEXT,
        details_json TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime'))
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ral_req ON request_audit_logs(request_id)")

    conn.commit()
    conn.close()
    print("MIGRATION COMPLETED SUCCESSFULLY: All 6 request management tables created with indexes.")

if __name__ == "__main__":
    run_migrations()
