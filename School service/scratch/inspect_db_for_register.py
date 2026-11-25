import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("PRAGMA table_info(schools)")
print("Schools columns:")
for col in c.fetchall():
    print(f"  {col['name']} ({col['type']})")

c.execute("SELECT school_id, school_name, school_type, category, district, address FROM schools")
schools = [dict(r) for r in c.fetchall()]
print(f"\nSchools count: {len(schools)}")
for s in schools:
    print(f"  {s['school_id']}: {s['school_name']} | Type: {s['school_type']} | Cat: {s['category']}")

# Check institution_divisions
print("\n--- institution_divisions ---")
c.execute("PRAGMA table_info(institution_divisions)")
print("Columns:", [r[1] for r in c.fetchall()])
c.execute("SELECT * FROM institution_divisions")
for r in c.fetchall():
    print(" ", dict(r))

# Check academic_programs
print("\n--- academic_programs ---")
c.execute("PRAGMA table_info(academic_programs)")
print("Columns:", [r[1] for r in c.fetchall()])
c.execute("SELECT count(*) FROM academic_programs")
print("Total programs:", c.fetchone()[0])
c.execute("SELECT * FROM academic_programs LIMIT 10")
for r in c.fetchall():
    print(" ", dict(r))

# Check students per school
c.execute("""
    SELECT s.school_id, s.school_name, count(st.student_id) as student_count
    FROM schools s
    LEFT JOIN students st ON st.school_id = s.school_id
    GROUP BY s.school_id
    ORDER BY s.school_id
""")
print("\nStudents per school:")
for r in c.fetchall():
    print(f"  {r['school_id']} ({r['school_name']}): {r['student_count']}")

# Sample student rows across different schools
print("\nSample students:")
for sch in ['SCH001', 'SCH011', 'SCH016', 'SCH021']:
    c.execute("SELECT student_id, student_name, school_id, standard, puc_year, stream, subject_combination, program_id, degree, branch, department, semester, enrollment_status FROM students WHERE school_id = ? LIMIT 2", (sch,))
    for r in c.fetchall():
        print(f"  {dict(r)}")

# Check distinct combinations of academic fields in students
print("\nDistinct academic combinations in students:")
c.execute("""
    SELECT school_id, standard, puc_year, stream, program_id, degree, branch, semester, count(*) as count
    FROM students
    GROUP BY school_id, standard, puc_year, stream, program_id, degree, branch, semester
    ORDER BY school_id, standard, puc_year
""")
rows = c.fetchall()
print(f"Total distinct combinations: {len(rows)}")
for r in rows[:25]:
    print(f"  {dict(r)}")

conn.close()
