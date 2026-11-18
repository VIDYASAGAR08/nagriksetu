import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for inst in ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']:
    cur.execute("SELECT program_id, program_name, education_level, combination_code, discipline_or_stream, duration_years, is_active FROM academic_programs WHERE institution_id = ?", (inst,))
    progs = cur.fetchall()
    print(f"\n=== {inst} Programs ({len(progs)}) ===")
    for p in progs:
        print(f"  {p['program_id']} | {p['education_level']} | {p['combination_code']} | {p['discipline_or_stream']} | {p['program_name']}")

conn.close()
