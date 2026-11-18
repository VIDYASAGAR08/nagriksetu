import sqlite3
c = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
print('Asha guardian:', c.execute("SELECT * FROM student_guardians WHERE permanent_student_id='NS-FB8336A812DE468FB8E475443CF673EB'").fetchall())
u = c.execute("SELECT user_id, phone FROM users WHERE phone='9876543210'").fetchone()
print('Parent user:', u)
if u:
    g = c.execute("SELECT guardian_id FROM guardians WHERE user_id=?", (u[0],)).fetchone()
    print('Guardian id:', g)
    if g:
        c.execute("INSERT OR IGNORE INTO student_guardians (student_guardian_id, permanent_student_id, guardian_id, can_view_records, can_request_updates, is_verified) VALUES ('SG-ASHA-001', 'NS-FB8336A812DE468FB8E475443CF673EB', ?, 1, 1, 1)", (g[0],))
        c.commit()
        print('Asha linked to parent 9876543210!')
