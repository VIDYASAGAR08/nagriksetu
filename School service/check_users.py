import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()
row = c.execute("SELECT user_id, email, role, school_id, is_active, status FROM users WHERE email = 'rao@edu.in'").fetchone()
print(row)
