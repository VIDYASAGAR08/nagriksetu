import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

apps = c.execute("SELECT application_id, institution_id, applicant_name, status, enrolled_student_id FROM admission_applications WHERE institution_id IN ('COL001', 'COL004', 'COL010')").fetchall()
for a in apps:
    print(dict(a))

conn.close()
