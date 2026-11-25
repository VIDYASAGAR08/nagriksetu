import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

print("--- Standards Breakdown per Institution ---")
c.execute("""
    SELECT s.school_id, sc.school_name, sc.school_type, s.standard, COUNT(*)
    FROM students s
    JOIN schools sc ON sc.school_id = s.school_id
    GROUP BY s.school_id, s.standard
    ORDER BY s.school_id, s.standard
""")
for r in c.fetchall():
    print(f"  {r[0]} ({r[2]}) | Std: {r[3]} | Count: {r[4]}")

print("\n--- PU College Programs (SCH011 - SCH015) in academic_programs ---")
c.execute("""
    SELECT institution_id, program_id, program_name, degree_type, discipline_or_stream, combination_code, department_name, faculty_name, duration_years
    FROM academic_programs
    WHERE institution_id IN ('SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015')
    ORDER BY institution_id, program_id
""")
for r in c.fetchall():
    print(f"  {r[0]} | {r[1]} | {r[2]} | Stream: {r[4]} | Code: {r[5]}")

print("\n--- Degree & Engineering College Programs in academic_programs ---")
c.execute("""
    SELECT institution_id, program_id, program_name, degree_type, discipline_or_stream, combination_code, department_name, faculty_name
    FROM academic_programs
    WHERE institution_id LIKE 'COL%'
    ORDER BY institution_id, program_id
""")
for r in c.fetchall()[:25]:
    print(f"  {r[0]} | {r[1]} | {r[2]} | Deg: {r[3]} | Stream: {r[4]} | Dept: {r[6]}")

conn.close()
