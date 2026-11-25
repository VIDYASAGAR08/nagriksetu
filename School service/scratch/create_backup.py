import sqlite3
import shutil
import os
import datetime

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
backup_dir = r'C:\Users\callm\nagriksetu\backend\data\backups'
os.makedirs(backup_dir, exist_ok=True)

now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(backup_dir, f"nagriksetu_backup_before_12000_correction_{now_str}.db")

print(f"Creating timestamped backup at: {backup_path}")

# Safe SQLite backup API
src = sqlite3.connect(db_path)
dst = sqlite3.connect(backup_path)
with dst:
    src.backup(dst, pages=1000)
dst.close()
src.close()

# Verify backup integrity
b_conn = sqlite3.connect(backup_path)
b_cur = b_conn.cursor()
b_cur.execute("PRAGMA integrity_check")
ic_res = b_cur.fetchall()
print("Backup PRAGMA integrity_check:", ic_res)

# Verify counts in backup
for tbl in ['schools', 'students', 'enrollments', 'academic_programs', 'student_attendance', 'academic_results', 'student_documents', 'student_guardians']:
    b_cur.execute(f"SELECT count(*) FROM {tbl}")
    print(f"Backup {tbl} count: {b_cur.fetchone()[0]}")

b_conn.close()

file_size_mb = os.path.getsize(backup_path) / (1024 * 1024)
print(f"Backup created successfully! File size: {file_size_mb:.2f} MB")
