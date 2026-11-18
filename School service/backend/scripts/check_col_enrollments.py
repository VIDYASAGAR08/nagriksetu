import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('''
    SELECT school_id, standard, section, count(*) as count
    FROM enrollments
    WHERE school_id LIKE "COL%"
    GROUP BY school_id, standard, section
    ORDER BY school_id, standard, section
''')
rows = c.fetchall()
print(f"Total enrollment groups in COL*: {len(rows)}")
for r in rows:
    print(dict(r))

c.execute('''
    SELECT s.institution_id, p.program_name, p.education_level, s.term_or_year, s.section_name, s.capacity, s.current_strength
    FROM program_sections s
    JOIN academic_programs p ON s.program_id = p.program_id
    WHERE s.institution_id LIKE "COL%"
    ORDER BY s.institution_id, p.program_name, s.term_or_year
''')
sec_rows = c.fetchall()
print(f"\nTotal program sections in COL*: {len(sec_rows)}")
for r in sec_rows[:30]:
    print(dict(r))

conn.close()
