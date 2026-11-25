import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== academic_programs for SCH011 - SCH020 ===")
cur.execute("SELECT program_id, institution_id, education_level, program_name, degree_type, discipline_or_stream FROM academic_programs WHERE institution_id BETWEEN 'SCH011' AND 'SCH020'")
for r in cur.fetchall():
    print(r)

conn.close()
