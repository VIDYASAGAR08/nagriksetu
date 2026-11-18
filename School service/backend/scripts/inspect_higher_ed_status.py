import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== SCHOOLS COL001 - COL010 ===")
cur.execute("SELECT school_id, school_name, category, school_type, affiliation, recognition FROM schools WHERE school_id LIKE 'COL%' ORDER BY school_id")
for r in cur.fetchall():
    print(f"{r['school_id']} | {r['category']} | {r['school_type']} | {r['school_name']} | Affil: {r['affiliation']}")

print("\n=== INSTITUTION DIVISIONS FOR COL001 - COL010 ===")
cur.execute("SELECT * FROM institution_divisions WHERE parent_institution_id LIKE 'COL%' ORDER BY parent_institution_id")
divs = cur.fetchall()
print(f"Total divisions: {len(divs)}")
for d in divs:
    print(f"{d['parent_institution_id']} | Div: {d['division_id']} | Name: {d['division_name']} | Type: {d['division_type']}")

print("\n=== ACADEMIC PROGRAMS FOR COL001 - COL010 ===")
cur.execute("""
    SELECT institution_id, education_level, degree_type, discipline_or_stream, count(*) as count
    FROM academic_programs
    WHERE institution_id LIKE 'COL%'
    GROUP BY institution_id, education_level, degree_type, discipline_or_stream
    ORDER BY institution_id
""")
for r in cur.fetchall():
    print(f"{r['institution_id']} | Level: {r['education_level']} | Degree: {r['degree_type']} | Stream: {r['discipline_or_stream']} | Count: {r['count']}")

conn.close()
