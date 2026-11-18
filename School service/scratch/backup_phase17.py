import sqlite3
import shutil
import os

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
backup_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_phase17_predeployment.db"

# Create physical copy
shutil.copyfile(db_path, backup_path)
print(f"Verified Backup created: {backup_path} ({os.path.getsize(backup_path)} bytes)")

# Test opening the backup
conn = sqlite3.connect(backup_path)
cur = conn.cursor()

inst_count = cur.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
stud_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
enr_count = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
app_count = cur.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0]
user_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
notif_count = cur.execute("SELECT COUNT(*) FROM portal_notifications").fetchone()[0]
cur.execute("PRAGMA integrity_check")
integrity = cur.fetchone()[0]
cur.execute("PRAGMA foreign_key_check")
fks = cur.fetchall()

print(f"Institutions: {inst_count}")
print(f"Students: {stud_count}")
print(f"Enrollments: {enr_count}")
print(f"Applications: {app_count}")
print(f"Users: {user_count}")
print(f"Notifications: {notif_count}")
print(f"Integrity: {integrity}")
print(f"FK violations: {len(fks)}")
conn.close()
