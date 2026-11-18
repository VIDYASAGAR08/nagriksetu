import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== SCHOOLS COL001 - COL010 ===")
cur.execute("SELECT school_id, school_name, category, school_type, affiliation FROM schools WHERE school_id LIKE 'COL%' ORDER BY school_id")
for r in cur.fetchall():
    print(f"{r['school_id']} | {r['school_name']} | {r['category']} | {r['school_type']} | Affil: {r['affiliation']}")

print("\n=== INSTITUTION DIVISIONS FOR COL001 - COL010 ===")
cur.execute("SELECT * FROM institution_divisions WHERE parent_institution_id LIKE 'COL%' ORDER BY parent_institution_id")
divs = cur.fetchall()
print(f"Total divisions: {len(divs)}")
for d in divs:
    print(f"{d['parent_institution_id']} | Div: {d['division_id']} | Name: {d['division_name']} | Type: {d['division_type']}")

print("\n=== ACADEMIC PROGRAMS FOR COL001 - COL010 ===")
cur.execute("SELECT program_id, institution_id, education_level, program_name, degree_type, discipline_or_stream FROM academic_programs WHERE institution_id LIKE 'COL%' ORDER BY institution_id, program_id")
progs = cur.fetchall()
print(f"Total academic programs: {len(progs)}")
for p in progs:
    print(f"{p['institution_id']} | {p['program_id']} | {p['education_level']} | {p['program_name']} | {p['degree_type']} | {p['discipline_or_stream']}")

print("\n=== PROGRAM SECTIONS CAPACITY/ENROLLMENT FOR COL001 - COL010 ===")
cur.execute("""
    SELECT institution_id, count(section_id) as section_count, sum(capacity) as total_cap, sum(current_strength) as total_enrolled
    FROM program_sections
    WHERE institution_id LIKE 'COL%'
    GROUP BY institution_id
""")
for s in cur.fetchall():
    print(f"{s['institution_id']} | Sections: {s['section_count']} | Capacity: {s['total_cap']} | Enrolled: {s['total_enrolled']}")

conn.close()
