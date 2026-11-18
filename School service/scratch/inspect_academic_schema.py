import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row

# Look for all tables related to academics, attendance, examinations, announcements
for row in conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall():
    t_name = row['name']
    if any(k in t_name.lower() for k in ['academic', 'result', 'exam', 'attend', 'mark', 'announc', 'section', 'grade', 'schedule']):
        print(f"--- Table: {t_name} ---")
        print(row['sql'])
        print()

conn.close()
