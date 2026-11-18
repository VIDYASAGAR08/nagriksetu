import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cols = [c[1] for c in cur.execute("PRAGMA table_info(admission_applications)").fetchall()]
print("admission_applications columns:", cols)

sample = cur.execute("SELECT * FROM admission_applications LIMIT 1").fetchone()
if sample:
    print("Sample application:", dict(sample))

conn.close()
