import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("--- Check Tables and Relations for Flagged Students ---")
# Check parent linking
cur.execute("""
    SELECT COUNT(*) FROM student_parent_links spl
    JOIN students s ON spl.student_id = s.student_id
    WHERE s.review_flag IS NOT NULL
""")
print("Parent links on flagged students:", cur.fetchone()[0])

# Check parent linking requests
cur.execute("""
    SELECT COUNT(*) FROM parent_student_linking_requests plr
    JOIN students s ON plr.student_id = s.student_id
    WHERE s.review_flag IS NOT NULL
""")
print("Parent linking requests on flagged students:", cur.fetchone()[0])

# Check student dossiers
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%dossier%'")
print("Dossier tables:", cur.fetchall())

# Check marks / attendance or other tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("All tables:", tables)

for t in ['student_attendance', 'student_marks', 'student_dossiers', 'student_profiles', 'requests_tickets']:
    if t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        # check if student_id column exists
        cur.execute(f"PRAGMA table_info({t})")
        cols = [c[1] for c in cur.fetchall()]
        if 'student_id' in cols:
            cur.execute(f"SELECT COUNT(*) FROM {t} WHERE student_id IN (SELECT student_id FROM students WHERE review_flag IS NOT NULL)")
            flagged_cnt = cur.fetchone()[0]
            print(f"Table {t}: total={cnt}, referencing flagged students={flagged_cnt}")
        else:
            print(f"Table {t}: total={cnt}, no student_id column")

conn.close()
