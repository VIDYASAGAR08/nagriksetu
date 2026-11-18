import sqlite3
c = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
u = c.execute("SELECT * FROM users WHERE email='staff.sch001@example.com'").fetchone()
print('user:', u)
p = c.execute("SELECT * FROM institution_staff_permissions WHERE user_id=?", (u[0],)).fetchall()
print('perms in institution_staff_permissions:', p)
