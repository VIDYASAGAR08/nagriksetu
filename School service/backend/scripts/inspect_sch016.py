import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("""
    SELECT ps.program_id, p.program_name, p.education_level, count(*)
    FROM program_sections ps
    JOIN academic_programs p ON ps.program_id = p.program_id
    WHERE ps.institution_id = 'SCH016'
    GROUP BY ps.program_id, p.program_name, p.education_level
""")
for r in cur.fetchall():
    print(r)
conn.close()
