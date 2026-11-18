import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== SCHOOLS SCH011 - SCH015 ===")
cur.execute("SELECT school_id, school_name, category, school_type FROM schools WHERE school_id BETWEEN 'SCH011' AND 'SCH015'")
for r in cur.fetchall():
    print(f"{r['school_id']} | {r['school_name']} | {r['category']} | {r['school_type']}")

print("\n=== ACADEMIC PROGRAMS FOR SCH011 - SCH015 ===")
cur.execute("SELECT * FROM academic_programs WHERE institution_id BETWEEN 'SCH011' AND 'SCH015'")
progs = cur.fetchall()
print(f"Total academic_programs: {len(progs)}")
for p in progs:
    print(dict(p))

print("\n=== PROGRAM SECTIONS FOR SCH011 - SCH015 ===")
cur.execute("SELECT * FROM program_sections WHERE institution_id BETWEEN 'SCH011' AND 'SCH015'")
sections = cur.fetchall()
print(f"Total program_sections: {len(sections)}")
for s in sections[:15]:
    print(dict(s))

print("\n=== SCHOOL_PROGRAMS FOR SCH011 - SCH015 ===")
cur.execute("SELECT * FROM school_programs WHERE school_id BETWEEN 'SCH011' AND 'SCH015'")
sp = cur.fetchall()
print(f"Total school_programs: {len(sp)}")
for p in sp[:15]:
    print(dict(p))

conn.close()
