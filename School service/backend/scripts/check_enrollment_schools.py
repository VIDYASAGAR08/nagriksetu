import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

c.execute('SELECT school_id, count(*) FROM enrollments GROUP BY school_id ORDER BY school_id')
for row in c.fetchall():
    print(row)

conn.close()
