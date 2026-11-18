import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== ALL PROGRAM SECTIONS FOR SCH014 ===")
cur.execute("""
    SELECT ps.section_id, ps.program_id, p.program_name, p.education_level, p.combination_code, ps.academic_year, ps.term_or_year, ps.section_name, ps.capacity, ps.current_strength
    FROM program_sections ps
    LEFT JOIN academic_programs p ON ps.program_id = p.program_id
    WHERE ps.institution_id = 'SCH014'
    ORDER BY ps.academic_year, ps.term_or_year, ps.section_id
""")
rows = cur.fetchall()
print(f"Total sections for SCH014: {len(rows)}")
for r in rows:
    print(dict(r))

conn.close()
