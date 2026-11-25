import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

# 1. Students count by school_id
c.execute("""
    SELECT s.school_id, sc.school_name, sc.school_type, COUNT(s.student_id)
    FROM students s
    JOIN schools sc ON sc.school_id = s.school_id
    GROUP BY s.school_id
    ORDER BY s.school_id
""")
print("Students per institution:")
inst_students = c.fetchall()
for r in inst_students:
    print(f"  {r[0]} | {r[1]} | Type: {r[2]} | Students: {r[3]}")

# 2. Check standard/class distribution in students table grouped by school_type
print("\nStudents table: standard distribution by school_type:")
c.execute("""
    SELECT sc.school_type, s.standard, COUNT(*)
    FROM students s
    JOIN schools sc ON sc.school_id = s.school_id
    GROUP BY sc.school_type, s.standard
    ORDER BY sc.school_type, s.standard
""")
for r in c.fetchall():
    print(f"  Type: {r[0]} | standard: {r[1]} | count: {r[2]}")

# 3. Check enrollments table columns and distribution
print("\nEnrollments table: standard, stream, subject_combination by school_type:")
c.execute("""
    SELECT sc.school_type, e.standard, e.stream, e.subject_combination, COUNT(*)
    FROM enrollments e
    JOIN schools sc ON sc.school_id = e.school_id
    GROUP BY sc.school_type, e.standard, e.stream, e.subject_combination
    ORDER BY sc.school_type, e.standard, e.stream
""")
for r in c.fetchall()[:30]:
    print(f"  Type: {r[0]} | standard: {r[1]} | stream: {r[2]} | combo: {r[3]} | count: {r[4]}")

# 4. Check academic_programs grouped by institution
print("\nAcademic programs per institution:")
c.execute("""
    SELECT institution_id, education_level, COUNT(*)
    FROM academic_programs
    GROUP BY institution_id, education_level
    ORDER BY institution_id
""")
for r in c.fetchall():
    print(f"  {r[0]} | Level: {r[1]} | Count: {r[2]}")

# 5. Check student ID prefixes across institutions
print("\nSample student IDs and prefixes:")
c.execute("""
    SELECT s.school_id, sc.school_type, SUBSTR(s.student_id, 1, 4) as pfx, COUNT(*)
    FROM students s
    JOIN schools sc ON sc.school_id = s.school_id
    GROUP BY s.school_id, SUBSTR(s.student_id, 1, 4)
    ORDER BY s.school_id, pfx
""")
for r in c.fetchall()[:40]:
    print(f"  {r[0]} | {r[1]} | Prefix: {r[2]} | Count: {r[3]}")

conn.close()
