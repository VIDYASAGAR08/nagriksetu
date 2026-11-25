import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()

tables = ['student_guardians', 'attendance_records', 'exam_results', 'student_documents']
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cur.fetchall()]
    print(f"Table {t}: {cols}")

conn.close()
