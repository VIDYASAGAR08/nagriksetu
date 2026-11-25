import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check initial row count
initial_count = c.execute("SELECT COUNT(*) FROM linking_requests").fetchone()[0]
print(f"Initial linking_requests count: {initial_count}")

c.execute("PRAGMA foreign_keys = OFF;")
conn.commit()

c.execute("BEGIN TRANSACTION;")

create_table_sql = """
CREATE TABLE linking_requests_new (
    request_id TEXT PRIMARY KEY,
    parent_user_id TEXT NOT NULL,
    school_id TEXT NOT NULL,
    student_ref TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    verification_doc_id TEXT,
    additional_notes TEXT,
    request_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (request_status IN (
            'pending', 'approved', 'rejected', 'cancelled', 'clarification_required', 'pending_review'
        )),
    reviewer_user_id TEXT,
    reviewer_comment TEXT,
    permanent_student_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TEXT,
    rejection_reason TEXT,
    parent_response TEXT,
    clarification_requested_at TEXT,
    clarification_responded_at TEXT,
    CHECK (
        request_status != 'approved'
        OR permanent_student_id IS NOT NULL
    ),
    FOREIGN KEY (parent_user_id) REFERENCES users(user_id),
    FOREIGN KEY (school_id) REFERENCES schools(school_id),
    FOREIGN KEY (reviewer_user_id) REFERENCES users(user_id),
    FOREIGN KEY (permanent_student_id) REFERENCES students(permanent_student_id)
);
"""

c.execute(create_table_sql)

# Copy all data
c.execute("""
INSERT INTO linking_requests_new (
    request_id, parent_user_id, school_id, student_ref, relationship_type,
    verification_doc_id, additional_notes, request_status, reviewer_user_id,
    reviewer_comment, permanent_student_id, created_at, reviewed_at,
    rejection_reason, parent_response, clarification_requested_at, clarification_responded_at
)
SELECT
    request_id, parent_user_id, school_id, student_ref, relationship_type,
    verification_doc_id, additional_notes, request_status, reviewer_user_id,
    reviewer_comment, permanent_student_id, created_at, reviewed_at,
    rejection_reason, parent_response, clarification_requested_at, clarification_responded_at
FROM linking_requests;
""")

c.execute("DROP TABLE linking_requests;")
c.execute("ALTER TABLE linking_requests_new RENAME TO linking_requests;")

# Recreate indices
c.execute("""
CREATE UNIQUE INDEX idx_linking_requests_pending_unique
ON linking_requests(parent_user_id, school_id, student_ref)
WHERE request_status IN ('pending', 'clarification_required', 'pending_review');
""")

c.execute("""
CREATE INDEX idx_linking_requests_school_status
ON linking_requests(school_id, request_status);
""")

c.execute("""
CREATE INDEX idx_linking_requests_parent_status
ON linking_requests(parent_user_id, request_status);
""")

conn.commit()

c.execute("PRAGMA foreign_keys = ON;")
conn.commit()

final_count = c.execute("SELECT COUNT(*) FROM linking_requests").fetchone()[0]
print(f"Final linking_requests count: {final_count}")
assert initial_count == final_count, "Row count mismatch!"

# Test inserting clarification_required status
test_id = "test-check-status-id"
c.execute("""
INSERT INTO linking_requests (
    request_id, parent_user_id, school_id, student_ref, relationship_type, request_status
) VALUES (?, 'user1', 'sch1', 'st1', 'Father', 'clarification_required')
""", (test_id,))
conn.commit()
print("Successfully inserted clarification_required status!")

# Delete test row
c.execute("DELETE FROM linking_requests WHERE request_id = ?", (test_id,))
conn.commit()

# Verify total students
st_count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
print(f"Verified students count: {st_count}")
assert st_count == 30003

conn.close()
print("Migration completed successfully!")
