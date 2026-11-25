import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id BETWEEN 'SCH011' AND 'SCH020'")
for r in cur.fetchall():
    print(r)
conn.close()
