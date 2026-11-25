import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()
rows = c.execute("SELECT user_id, full_name, email, phone, role FROM users WHERE role = 'parent'").fetchall()
print(f"Total parent users: {len(rows)}")
for r in rows[:10]:
    print(r)
conn.close()
