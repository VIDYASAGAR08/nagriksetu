import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(schools)")
cols = [c[1] for c in cur.fetchall()]
print("schools columns containing seat/cap:", [c for c in cols if 'seat' in c or 'cap' in c])
conn.close()
