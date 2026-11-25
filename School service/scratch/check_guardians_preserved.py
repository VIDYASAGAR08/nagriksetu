import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM student_guardians")
sg_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM guardians")
g_count = cur.fetchone()[0]

print(f"Verified student guardians links: {sg_count}")
print(f"Guardians records: {g_count}")

cur.execute("""
    SELECT sg.permanent_student_id, s.student_id, s.student_name, g.full_name, g.relationship, g.email, g.phone
    FROM student_guardians sg
    JOIN students s ON sg.permanent_student_id = s.permanent_student_id
    JOIN guardians g ON sg.guardian_id = g.guardian_id
""")
for r in cur.fetchall():
    print("Linked guardian:", r)

conn.close()
