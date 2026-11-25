import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()
print(c.execute("SELECT sql FROM sqlite_master WHERE name = 'linking_requests'").fetchone()[0])
