import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("SELECT application_id, institution_id, requested_program_id, status FROM admission_applications WHERE institution_id BETWEEN 'SCH011' AND 'SCH015'")
apps = cur.fetchall()
print(f"Total applications for SCH011-SCH015: {len(apps)}")
for a in apps:
    print(a)
conn.close()
