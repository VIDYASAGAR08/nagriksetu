import sqlite3
import os
from datetime import datetime

source_db = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = r'C:\Users\callm\nagriksetu\backend\data\backups'
os.makedirs(backup_dir, exist_ok=True)
backup_db = os.path.join(backup_dir, f'nagriksetu_composite_pre_backup_{timestamp}.db')

print(f"Creating timestamped database backup for composite implementation:")
print(f"  Source: {source_db}")
print(f"  Target: {backup_db}")

src_conn = sqlite3.connect(source_db)
dst_conn = sqlite3.connect(backup_db)
with dst_conn:
    src_conn.backup(dst_conn)
dst_conn.close()
src_conn.close()

size = os.path.getsize(backup_db)
print(f"Backup created successfully! Size: {size / (1024*1024):.2f} MB")
