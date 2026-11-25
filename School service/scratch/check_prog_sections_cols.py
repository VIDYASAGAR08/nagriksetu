import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(program_sections)")
print(cur.fetchall())

cur.execute("SELECT * FROM program_sections LIMIT 2")
print(cur.fetchall())

conn.close()
