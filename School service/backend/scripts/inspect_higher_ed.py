import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('PRAGMA table_info(schools)')
print('schools columns:', [row['name'] for row in c.fetchall()])

c.execute('PRAGMA table_info(academic_programs)')
print('academic_programs columns:', [row['name'] for row in c.fetchall()])

c.execute('PRAGMA table_info(institution_divisions)')
print('institution_divisions columns:', [row['name'] for row in c.fetchall()])

c.execute('SELECT school_id, school_name, school_type, category, affiliation FROM schools WHERE school_id LIKE "COL%" ORDER BY school_id')
for row in c.fetchall():
    print(dict(row))

print("\n--- PROGRAMS FOR COL001-COL010 ---")
c.execute('''
    SELECT institution_id, program_id, education_level, degree_type, program_name, discipline_or_stream
    FROM academic_programs
    WHERE institution_id LIKE "COL%"
    ORDER BY institution_id, program_id
''')
for row in c.fetchall():
    print(dict(row))

print("\n--- DIVISIONS FOR COL001-COL010 ---")
c.execute('''
    SELECT division_id, parent_institution_id, division_name, division_type, campus_location, head_of_division
    FROM institution_divisions
    WHERE parent_institution_id LIKE "COL%"
    ORDER BY parent_institution_id, division_id
''')
for row in c.fetchall():
    print(dict(row))

conn.close()
