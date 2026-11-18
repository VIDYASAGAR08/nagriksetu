import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

user = cur.execute("SELECT user_id, phone, email, full_name FROM users WHERE phone = '9876543210'").fetchone()
print("User:", dict(user))

guardian = cur.execute("SELECT * FROM guardians WHERE user_id = ?", (user["user_id"],)).fetchone()
if not guardian:
    guardian = cur.execute("SELECT * FROM guardians WHERE phone = '9876543210'").fetchone()
print("Guardian:", dict(guardian) if guardian else None)

if guardian:
    sg = cur.execute("SELECT * FROM student_guardians WHERE guardian_id = ?", (guardian["guardian_id"],)).fetchall()
    print("Linked children:")
    for r in sg:
        print(dict(r))

conn.close()
