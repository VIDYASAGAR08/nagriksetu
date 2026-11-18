import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('Existing tables:', tables)

for t in tables:
    if any(k in t.lower() for k in ['faculty', 'department', 'program', 'academic', 'college', 'division', 'school', 'seat', 'course']):
        print(f'\n--- Table: {t} ---')
        cur.execute(f'PRAGMA table_info({t})')
        for c in cur.fetchall():
            print(f'  {c[1]} ({c[2]})')

conn.close()
