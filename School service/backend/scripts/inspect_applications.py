import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

rows = c.execute('SELECT application_id, institution_id, requested_program_id, applicant_name FROM admission_applications WHERE requested_program_id LIKE "%DIP"').fetchall()
print(f"Found {len(rows)} applications for DIP:")
for r in rows:
    print(r)

conn.close()
