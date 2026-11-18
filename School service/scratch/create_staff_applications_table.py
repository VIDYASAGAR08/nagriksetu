import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS staff_applications (
    application_id TEXT PRIMARY KEY,
    candidate_token TEXT UNIQUE NOT NULL,
    institution_id TEXT NOT NULL,
    candidate_email TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    candidate_phone TEXT,
    role_id TEXT NOT NULL DEFAULT 'school_staff',
    status TEXT NOT NULL DEFAULT 'invited',
    qualifications_json TEXT DEFAULT '[]',
    employment_details_json TEXT DEFAULT '{}',
    documents_json TEXT DEFAULT '[]',
    correction_notes TEXT,
    review_notes TEXT,
    created_by_user_id TEXT,
    reviewed_by_user_id TEXT,
    reviewed_at TIMESTAMP,
    activation_token TEXT UNIQUE,
    activation_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES schools(school_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_staff_app_inst ON staff_applications(institution_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_staff_app_token ON staff_applications(candidate_token);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_staff_app_act_token ON staff_applications(activation_token);")

conn.commit()

# Verify
cur.execute("PRAGMA integrity_check")
print("Integrity check:", cur.fetchall())
cur.execute("PRAGMA foreign_key_check")
print("Foreign key check:", cur.fetchall())
conn.close()
print("staff_applications table created successfully!")
