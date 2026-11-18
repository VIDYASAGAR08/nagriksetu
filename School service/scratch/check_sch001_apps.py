import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

apps = cur.execute("SELECT application_id, institution_id, status FROM admission_applications WHERE institution_id = 'SCH001'").fetchall()
print("SCH001 applications:")
for a in apps[:5]:
    print(dict(a))

conn.close()
