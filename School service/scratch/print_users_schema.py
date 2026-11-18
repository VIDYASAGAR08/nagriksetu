import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()
indexes = c.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='users'").fetchall()
print('Users indexes:', indexes)
conn.close()
