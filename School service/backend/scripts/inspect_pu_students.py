import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== ENROLLMENTS BY STANDARD FOR SCH011 - SCH015 ===")
cur.execute("""
    SELECT school_id, standard, count(*) as count
    FROM enrollments
    WHERE school_id BETWEEN 'SCH011' AND 'SCH015'
    GROUP BY school_id, standard
    ORDER BY school_id, standard
""")
for r in cur.fetchall():
    print(f"{r['school_id']} | Std: {r['standard']} | Count: {r['count']}")

conn.close()
