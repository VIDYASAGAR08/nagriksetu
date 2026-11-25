import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()
c.execute("SELECT email, role, phone FROM users WHERE role = 'parent' LIMIT 10")
for r in c.fetchall():
    print(r)
conn.close()
