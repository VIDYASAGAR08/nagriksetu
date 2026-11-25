import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()

for t in ['student_attendance', 'academic_results', 'examinations', 'guardians']:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [f"{c[1]} ({c[2]})" for c in cur.fetchall()]
    print(f"Table {t}: {cols}\n")

conn.close()
