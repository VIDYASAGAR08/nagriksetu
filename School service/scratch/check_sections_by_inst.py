import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT institution_id, count(*) FROM program_sections GROUP BY institution_id")
for r in cur.fetchall():
    print(r)

conn.close()
