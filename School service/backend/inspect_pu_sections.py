import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("""
    SELECT ps.institution_id, ps.term_or_year, ps.section_name, p.combination_code, p.discipline_or_stream, p.program_name, ps.current_strength, ps.capacity
    FROM program_sections ps
    JOIN academic_programs p ON p.program_id = ps.program_id
    WHERE ps.institution_id IN ('SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015')
    ORDER BY ps.institution_id, ps.term_or_year, ps.section_name, p.combination_code
""")
rows = c.fetchall()
print(f"Total PU sections in program_sections: {len(rows)}")
for r in rows:
    print(f"  {r[0]} | Term {r[1]} | Sec {r[2]} | Code: {r[3]} | Stream: {r[4]} | Str: {r[6]} | Cap: {r[7]}")

conn.close()
