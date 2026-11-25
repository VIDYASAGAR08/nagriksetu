import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(program_sections)")
print([c[1] for c in cur.fetchall()])

cur.execute("SELECT * FROM program_sections WHERE institution_id = 'SCH016' LIMIT 5")
for r in cur.fetchall():
    print(r)

conn.close()
