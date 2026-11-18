import sqlite3
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.execute("DELETE FROM enrollments WHERE permanent_student_id = 'NS-CCA80D1DD5A74CC289EBE75A8562BD8C'")
conn.execute("DELETE FROM students WHERE permanent_student_id = 'NS-CCA80D1DD5A74CC289EBE75A8562BD8C'")
conn.commit()
print("Students count:", conn.execute("SELECT COUNT(*) FROM students").fetchone()[0])
print("Enrollments count:", conn.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0])
print("Applications count:", conn.execute("SELECT COUNT(*) FROM admission_applications").fetchone()[0])
conn.close()
