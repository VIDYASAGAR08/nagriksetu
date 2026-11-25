import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("SELECT COUNT(*), review_flag FROM students GROUP BY review_flag")
print(cur.fetchall())
conn.close()
