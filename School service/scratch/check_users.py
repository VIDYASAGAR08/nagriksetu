import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Find admin users
admins = c.execute("SELECT user_id, email, phone, role, school_id, is_active FROM users WHERE role IN ('school_admin', 'platform_admin', 'admissions_officer') LIMIT 15").fetchall()
for a in admins:
    print(dict(a))

# Find linking requests
links = c.execute("SELECT * FROM linking_requests LIMIT 5").fetchall()
print("Linking requests:", [dict(l) for l in links])

conn.close()
