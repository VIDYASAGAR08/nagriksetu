import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()

c.execute("""
    SELECT school_id, standard, count(*) as count
    FROM enrollments
    WHERE school_id IN ('SCH016', 'SCH017', 'SCH018', 'SCH019', 'SCH020')
    GROUP BY school_id, standard
    ORDER BY school_id, standard
""")
rows = c.fetchall()
print("Standards in enrollments for SCH016-020:")
for r in rows:
    print(r)

conn.close()
