import sqlite3
import datetime

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Applying Phase 14 Notification schema migrations...")

# Check existing columns of portal_notifications
existing_cols = {col[1] for col in c.execute("PRAGMA table_info(portal_notifications)").fetchall()}
print("Existing columns in portal_notifications:", existing_cols)

new_cols = [
    ("category", "VARCHAR(50) DEFAULT 'general'"),
    ("priority", "VARCHAR(20) DEFAULT 'normal'"),
    ("channel", "VARCHAR(20) DEFAULT 'in_app'"),
    ("delivery_status", "VARCHAR(30) DEFAULT 'delivered'"),
    ("related_record_type", "VARCHAR(50)"),
    ("related_record_id", "VARCHAR(100)"),
    ("read_at", "TIMESTAMP"),
    ("idempotency_key", "VARCHAR(150)")
]

for col_name, col_type in new_cols:
    if col_name not in existing_cols:
        print(f"Adding column {col_name} ({col_type})...")
        c.execute(f"ALTER TABLE portal_notifications ADD COLUMN {col_name} {col_type}")

# Create indexes on portal_notifications
c.execute("CREATE INDEX IF NOT EXISTS idx_portal_notifs_user ON portal_notifications (recipient_user_id, is_read, created_at)")
c.execute("CREATE INDEX IF NOT EXISTS idx_portal_notifs_idemp ON portal_notifications (idempotency_key)")
c.execute("CREATE INDEX IF NOT EXISTS idx_portal_notifs_inst ON portal_notifications (institution_id, recipient_role)")

# Create notification_preferences table
c.execute("""
CREATE TABLE IF NOT EXISTS notification_preferences (
    preference_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    academic_updates INTEGER DEFAULT 1,
    attendance_alerts INTEGER DEFAULT 1,
    examination_alerts INTEGER DEFAULT 1,
    admission_updates INTEGER DEFAULT 1,
    institution_announcements INTEGER DEFAULT 1,
    administrative_alerts INTEGER DEFAULT 1,
    email_enabled INTEGER DEFAULT 1,
    sms_enabled INTEGER DEFAULT 1,
    whatsapp_enabled INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create notification_delivery_logs table
c.execute("""
CREATE TABLE IF NOT EXISTS notification_delivery_logs (
    log_id VARCHAR(50) PRIMARY KEY,
    notification_id VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    recipient_destination VARCHAR(100),
    status VARCHAR(30) NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notification_id) REFERENCES portal_notifications(notification_id)
)
""")
c.execute("CREATE INDEX IF NOT EXISTS idx_notif_logs_notif_id ON notification_delivery_logs (notification_id)")

conn.commit()

# Verify integrity
integrity = c.execute("PRAGMA integrity_check").fetchone()[0]
fk_check = c.execute("PRAGMA foreign_key_check").fetchall()
print(f"Integrity check: {integrity}")
print(f"Foreign key violations: {len(fk_check)}")

conn.close()
print("Phase 14 Notification migration completed successfully.")
