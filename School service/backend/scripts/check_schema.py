import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
for table in ['academic_programs', 'program_sections']:
    print(f"Table: {table}")
    cur.execute(f"PRAGMA table_info({table})")
    for col in cur.fetchall():
        print(f"  {col[1]} ({col[2]})")
conn.close()
