import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('''
    SELECT p.institution_id, p.program_id, p.program_name, p.education_level, count(s.section_id) as section_count
    FROM academic_programs p
    LEFT JOIN program_sections s ON p.program_id = s.program_id
    WHERE p.institution_id LIKE "COL%"
    GROUP BY p.program_id
    ORDER BY p.institution_id, p.program_id
''')
for row in c.fetchall():
    print(dict(row))

c.execute('''
    SELECT count(*) as total_students FROM students
''')
print("Total students:", c.fetchone()['total_students'])

c.execute('''
    SELECT count(*) as total_enrollments FROM enrollments
''')
print("Total enrollments:", c.fetchone()['total_enrollments'])

c.execute('''
    SELECT e.program_id, count(*) as count
    FROM enrollments e
    WHERE e.school_id LIKE "COL%"
    GROUP BY e.program_id
''')
print("\nEnrollments by program for COL*:")
for row in c.fetchall():
    print(dict(row))

conn.close()
