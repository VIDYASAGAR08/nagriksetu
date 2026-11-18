import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("""
    SELECT institution_id, academic_year, count(*) as count
    FROM program_sections
    GROUP BY institution_id, academic_year
    ORDER BY institution_id, academic_year
""")
for r in cur.fetchall():
    print(r)
conn.close()
