import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== ALL INSTITUTIONS IN NAGRIKSETU ===")
cur.execute("SELECT school_id, school_name, school_type, category, district FROM schools ORDER BY school_id")
for r in cur.fetchall():
    print(r)

conn.close()
