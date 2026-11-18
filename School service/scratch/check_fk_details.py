import sqlite3
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT rowid, * FROM student_guardians WHERE rowid IN (5, 6)").fetchall()
for r in rows:
    print(dict(r))

# Check foreign key definition on student_guardians
print(conn.execute("PRAGMA foreign_key_list(student_guardians)").fetchall())

# Let's also check our backup database created at the start of this session!
backup_conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db.bak_final_phase_20261103_083812")
print("Backup FK violations:", backup_conn.execute("PRAGMA foreign_key_check").fetchall())
backup_rows = backup_conn.execute("SELECT rowid, * FROM student_guardians WHERE rowid IN (5, 6)").fetchall()
for r in backup_rows:
    print("Backup row:", dict(r))
backup_conn.close()

conn.close()
