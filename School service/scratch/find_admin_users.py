import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()
cur.execute("SELECT user_id, email, role, is_active FROM users WHERE role IN ('platform_admin', 'school_admin', 'institution_admin')")
for r in cur.fetchall():
    print(r)
conn.close()
