import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("""
    SELECT ps.institution_id, p.education_level, p.combination_code, p.discipline_or_stream, p.program_name, 
           ps.term_or_year, ps.semester, ps.section_name, ps.current_strength, ps.capacity
    FROM program_sections ps
    JOIN academic_programs p ON p.program_id = ps.program_id
    ORDER BY ps.institution_id, ps.term_or_year, ps.section_name
""")
sections = c.fetchall()
print(f"Total program_sections: {len(sections)}")

inst_sections = {}
for s in sections:
    inst = s[0]
    inst_sections.setdefault(inst, []).append(s)

print("\nSections count per institution:")
for inst, secs in sorted(inst_sections.items()):
    print(f"  {inst}: {len(secs)} sections")

print("\nSample PU College (SCH011) sections:")
for s in inst_sections.get('SCH011', [])[:15]:
    print(f"  Term: {s[5]} | Sem: {s[6]} | Sec: {s[7]} | Code: {s[2]} | Stream: {s[3]} | Prog: {s[4]} | Str: {s[8]}")

print("\nSample Degree / Engineering College (COL003) sections:")
for s in inst_sections.get('COL003', [])[:15]:
    print(f"  Term: {s[5]} | Sem: {s[6]} | Sec: {s[7]} | Code: {s[2]} | Stream: {s[3]} | Prog: {s[4]} | Str: {s[8]}")

conn.close()
