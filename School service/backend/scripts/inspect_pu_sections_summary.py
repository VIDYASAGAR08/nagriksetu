import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== PU SECTIONS FOR SCH011 - SCH015 ===")
cur.execute("""
    SELECT ps.institution_id, ps.program_id, p.program_name, p.combination_code, ps.academic_year, ps.term_or_year, ps.section_name, ps.capacity, ps.current_strength
    FROM program_sections ps
    JOIN academic_programs p ON ps.program_id = p.program_id
    WHERE ps.institution_id BETWEEN 'SCH011' AND 'SCH015' AND p.education_level = 'higher_secondary'
    ORDER BY ps.institution_id, ps.term_or_year, ps.program_id
""")
pu_sections = cur.fetchall()
print(f"Total PU sections across SCH011-SCH015: {len(pu_sections)}")

for inst in ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']:
    inst_secs = [s for s in pu_sections if s['institution_id'] == inst]
    tot_cap = sum(s['capacity'] for s in inst_secs)
    tot_cur = sum(s['current_strength'] for s in inst_secs)
    print(f"\n{inst}: {len(inst_secs)} PU sections | Total Capacity: {tot_cap} | Total Enrolled: {tot_cur} | Available: {tot_cap - tot_cur}")
    for s in inst_secs[:4]:
        print(f"  {s['combination_code']} | Term/Yr: {s['term_or_year']} | Sec: {s['section_name']} | Cap: {s['capacity']} | Enr: {s['current_strength']} | AY: {s['academic_year']}")

conn.close()
