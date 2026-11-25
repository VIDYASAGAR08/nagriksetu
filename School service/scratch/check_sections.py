import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT count(*) FROM program_sections")
print("program_sections count:", cur.fetchone()[0])

cur.execute("SELECT * FROM program_sections LIMIT 5")
for r in cur.fetchall():
    print(r)

conn.close()
