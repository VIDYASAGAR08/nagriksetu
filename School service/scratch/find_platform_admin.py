import sqlite3
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()
cur.execute("SELECT user_id, email, phone, role, is_active, status FROM users WHERE role = 'platform_admin'")
for r in cur.fetchall():
    print(r)
conn.close()
