import sqlite3
import os

DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
BACKUP_PATH = r"C:\Users\callm\nagriksetu\backend\data\backups\nagriksetu_composite_pre_backup_20261122_103046.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Schema of academic_programs:")
cur.execute("PRAGMA table_info(academic_programs)")
for col in cur.fetchall():
    print(f"  {col[1]} ({col[2]})")

print("\nSchema of enrollments:")
cur.execute("PRAGMA table_info(enrollments)")
for col in cur.fetchall():
    print(f"  {col[1]} ({col[2]})")

conn.close()
