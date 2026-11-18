import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("""
    SELECT program_id, institution_id, education_level, program_name, degree_type
    FROM academic_programs
    WHERE institution_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
    ORDER BY institution_id, education_level, program_id
""")
for row in c.fetchall():
    print(dict(row))

conn.close()
