import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- Current institution_divisions ---")
cur.execute("SELECT division_id, parent_institution_id, division_name, division_type FROM institution_divisions")
for r in cur.fetchall():
    print(r)

print("\n--- academic_programs count by institution_id ---")
cur.execute("SELECT institution_id, count(*), group_concat(program_id, ', ') FROM academic_programs GROUP BY institution_id")
for r in cur.fetchall():
    print(r[0], r[1], r[2][:80])

conn.close()
