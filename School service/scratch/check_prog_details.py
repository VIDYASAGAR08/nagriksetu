import sqlite3

db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- academic_programs for SCH011 ---")
cur.execute("SELECT program_id, program_name, degree_type, discipline_or_stream, combination_code, faculty_name, department_name FROM academic_programs WHERE institution_id = 'SCH011'")
for r in cur.fetchall():
    print(r)

print("\n--- academic_programs for SCH016 ---")
cur.execute("SELECT program_id, program_name, degree_type, discipline_or_stream, combination_code, faculty_name, department_name FROM academic_programs WHERE institution_id = 'SCH016'")
for r in cur.fetchall():
    print(r)

conn.close()
