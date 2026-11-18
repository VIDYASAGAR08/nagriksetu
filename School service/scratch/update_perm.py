import sqlite3
c = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
u = c.execute("SELECT user_id FROM users WHERE email='staff.sch001@example.com'").fetchone()
if u:
    c.execute("UPDATE institution_staff_permissions SET can_manage_academics=1, can_manage_students=1, can_view_applications=1 WHERE user_id=?", (u[0],))
    c.commit()
    print("Updated permissions for staff.sch001!")
c.close()
