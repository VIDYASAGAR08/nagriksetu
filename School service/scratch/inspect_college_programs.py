import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check all degree colleges and universities in schools
colleges = cur.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id LIKE 'COL%'").fetchall()
print(f"Colleges count: {len(colleges)}")
for col in colleges:
    print(dict(col))
    # Count academic programs
    progs = cur.execute("SELECT program_id, program_name, degree_type, discipline_or_stream, duration_years, faculty_name, department_name FROM academic_programs WHERE institution_id = ?", (col["school_id"],)).fetchall()
    print(f"  Academic programs ({len(progs)}):")
    for p in progs:
        print("   ", dict(p))

    # Count program sections
    secs = cur.execute("SELECT * FROM program_sections WHERE institution_id = ? LIMIT 5", (col["school_id"],)).fetchall()
    print(f"  Program sections sample ({len(secs)}):", [dict(s) for s in secs])

conn.close()
