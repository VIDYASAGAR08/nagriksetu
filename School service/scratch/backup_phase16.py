import sqlite3
import shutil
import os

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
backup_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_phase16_preaudit.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in DB:", tables)

inst_count = cur.execute("SELECT COUNT(*) FROM schools").fetchone()[0] if "schools" in tables else 0
stud_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] if "students" in tables else 0
enr_count = cur.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0] if "enrollments" in tables else (
    cur.execute("SELECT COUNT(*) FROM student_enrollment").fetchone()[0] if "student_enrollment" in tables else 0
)
app_count = cur.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0] if "admission_applications" in tables else (
    cur.execute("SELECT COUNT(*) FROM applications").fetchone()[0] if "applications" in tables else 0
)
user_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] if "users" in tables else 0
notif_count = cur.execute("SELECT COUNT(*) FROM portal_notifications").fetchone()[0] if "portal_notifications" in tables else 0

cur.execute("PRAGMA integrity_check")
integrity = cur.fetchone()[0]
cur.execute("PRAGMA foreign_key_check")
fks = cur.fetchall()

print(f"Institutions: {inst_count}")
print(f"Students: {stud_count}")
print(f"Enrollments (or table name): {enr_count}")
print(f"Applications: {app_count}")
print(f"Users: {user_count}")
print(f"Notifications: {notif_count}")
print(f"Integrity: {integrity}")
print(f"FK violations: {len(fks)}")
conn.close()
