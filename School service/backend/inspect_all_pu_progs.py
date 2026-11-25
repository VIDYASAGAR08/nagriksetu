import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("""
    SELECT institution_id, program_id, combination_code, discipline_or_stream, program_name
    FROM academic_programs
    WHERE institution_id IN ('SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015')
    ORDER BY institution_id, discipline_or_stream, combination_code
""")
for r in c.fetchall():
    print(r)

conn.close()
