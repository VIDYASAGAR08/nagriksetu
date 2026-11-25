import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()
staff1 = c.execute("SELECT password_hash FROM users WHERE email = 'staff.sch001@example.com'").fetchone()[0]
c.execute("UPDATE users SET password_hash = ? WHERE email = 'rao@edu.in'", (staff1,))
conn.commit()
print("Updated rao@edu.in password to Staff@NagrikSetu2026!")
