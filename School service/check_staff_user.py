import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

row = c.execute("SELECT user_id, email, full_name, role, school_id FROM users WHERE user_id = 'staff-sch001-uid'").fetchone()
print("staff-sch001-uid:", row)

conn.close()
