import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== SECTIONS FOR DEGREE COLLEGES & UNIVERSITIES ===")
cur.execute("""
    SELECT s.school_id, s.category, s.school_name, count(ps.section_id) as sec_count,
           sum(ps.capacity) as cap, sum(ps.current_strength) as strength,
           sum(ps.capacity - ps.current_strength) as avail
    FROM schools s
    LEFT JOIN program_sections ps ON s.school_id = ps.institution_id
    WHERE s.school_id LIKE 'COL%'
    GROUP BY s.school_id
    ORDER BY s.category, s.school_id
""")
for r in cur.fetchall():
    print(f"{r['school_id']} | {r['category']:<16} | Secs: {r['sec_count']:<2} | Cap: {r['cap']} | Enr: {r['strength']} | Avail: {r['avail']} | {r['school_name']}")

conn.close()
