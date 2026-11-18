import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

query = '''
SELECT 
    s.school_id, 
    s.school_name, 
    s.district, 
    s.category, 
    s.school_type,
    count(DISTINCT st.student_id) as student_count,
    count(DISTINCT ap.program_id) as prog_count,
    count(DISTINCT ps.section_id) as section_count
FROM schools s
LEFT JOIN students st ON s.school_id = st.school_id
LEFT JOIN academic_programs ap ON s.school_id = ap.institution_id
LEFT JOIN program_sections ps ON ap.program_id = ps.program_id
GROUP BY s.school_id
ORDER BY 
    CASE s.category
        WHEN 'Schools (K-10)' THEN 1
        WHEN 'PU Colleges (11-12)' THEN 2
        WHEN 'Degree Colleges' THEN 3
        WHEN 'Universities' THEN 4
        ELSE 5
    END, s.school_id
'''

cur.execute(query)
rows = cur.fetchall()
print('| ID | Institution Name | District | Category | Type | Students | Programs | Sections |')
print('|---|---|---|---|---|---:|---:|---:|')
for r in rows:
    print(f"| `{r['school_id']}` | {r['school_name']} | {r['district']} | {r['category']} | {r['school_type']} | {r['student_count']:,} | {r['prog_count']} | {r['section_count']} |")

conn.close()
