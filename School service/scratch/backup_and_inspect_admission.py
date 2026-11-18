import sqlite3
import shutil
import os

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
backup_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu_backup_admission_redesign_pre.db"

shutil.copyfile(db_path, backup_path)
print(f"Verified Backup created: {backup_path} ({os.path.getsize(backup_path)} bytes)")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

app = cur.execute("SELECT * FROM admission_applications WHERE application_id = ?", ("APP-2026-COL003-38F306",)).fetchone()
print("APP-2026-COL003-38F306 exists:", dict(app) if app else "NOT FOUND")

total_apps = cur.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0]
print(f"Total applications in DB: {total_apps}")

# Check columns of admission_applications
cols = [c[1] for c in cur.execute("PRAGMA table_info(admission_applications)").fetchall()]
print("admission_applications columns:", cols)

# Check columns of admission_status_history
hist_cols = [c[1] for c in cur.execute("PRAGMA table_info(admission_status_history)").fetchall()]
print("admission_status_history columns:", hist_cols)

conn.close()
