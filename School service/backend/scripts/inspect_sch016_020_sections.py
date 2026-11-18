import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("""
    SELECT s.institution_id, p.program_name, p.education_level, count(*) as sec_count
    FROM program_sections s
    JOIN academic_programs p ON s.program_id = p.program_id
    WHERE s.institution_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
    GROUP BY s.institution_id, p.education_level
""")
rows = c.fetchall()
print("Sections for SCH016-020 by level:")
for r in rows:
    print(dict(r))

c.execute("""
    SELECT count(*) as count FROM admission_applications
    WHERE institution_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
    AND (education_level = 'higher_secondary' OR requested_program_id LIKE '%PCMB%' OR requested_program_id LIKE '%CEBA%')
""")
print("Admission applications for PU in SCH016-020:", c.fetchone()['count'])

conn.close()
