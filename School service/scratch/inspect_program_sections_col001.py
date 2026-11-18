import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- program_sections for COL001 ---")
rows = cur.execute("""
    SELECT ps.section_id, ps.program_id, ps.academic_year, ps.term_or_year, ps.semester, ps.section_name, ps.capacity, ps.current_strength,
           ap.program_name, ap.degree_type, ap.discipline_or_stream, ap.faculty_name
    FROM program_sections ps
    JOIN academic_programs ap ON ap.program_id = ps.program_id
    WHERE ps.institution_id = 'COL001'
    ORDER BY ap.program_name, ps.term_or_year, ps.semester, ps.section_name
""").fetchall()

print(f"Total sections for COL001: {len(rows)}")
by_prog = {}
for r in rows:
    pname = r["program_name"]
    if pname not in by_prog:
        by_prog[pname] = {"years": set(), "semesters": set(), "sections": set(), "academic_years": set()}
    by_prog[pname]["years"].add(r["term_or_year"])
    by_prog[pname]["semesters"].add(r["semester"])
    by_prog[pname]["sections"].add(r["section_name"])
    by_prog[pname]["academic_years"].add(r["academic_year"])

for pname, data in by_prog.items():
    print(f"Programme: {pname}")
    print(f"  Years: {sorted(list(data['years']))}")
    print(f"  Semesters: {sorted(list(data['semesters']))}")
    print(f"  Sections: {sorted(list(data['sections']))}")
    print(f"  Academic Years: {sorted(list(data['academic_years']))}")

# Also check institution_divisions for COL001
print("\n--- institution_divisions for COL001 ---")
divs = cur.execute("SELECT * FROM institution_divisions WHERE parent_institution_id = 'COL001'").fetchall()
for d in divs:
    print(dict(d))

conn.close()
