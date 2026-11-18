import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

pu_schools = ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']
for ps in pu_schools:
    print(f"\n================ {ps} ================")
    progs = cur.execute("SELECT program_id, program_name, discipline_or_stream, combination_code FROM academic_programs WHERE institution_id = ?", (ps,)).fetchall()
    print(f"Academic programs ({len(progs)}):")
    for p in progs:
        print("  ", dict(p))

    secs = cur.execute("SELECT section_id, program_id, term_or_year, section_name FROM program_sections WHERE institution_id = ?", (ps,)).fetchall()
    print(f"Program sections ({len(secs)}):")
    for s in secs:
        print("  ", dict(s))

conn.close()
