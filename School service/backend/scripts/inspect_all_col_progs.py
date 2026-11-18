import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for cid in ['COL001', 'COL002', 'COL003', 'COL005', 'COL007', 'COL004', 'COL006', 'COL008', 'COL009', 'COL010']:
    cur.execute("SELECT s.category, s.school_name FROM schools s WHERE s.school_id = ?", (cid,))
    s_row = cur.fetchone()
    print(f"\n==================== {cid}: {s_row['school_name']} ({s_row['category']}) ====================")
    cur.execute("SELECT program_id, education_level, degree_type, discipline_or_stream, program_name, duration_years FROM academic_programs WHERE institution_id = ?", (cid,))
    for p in cur.fetchall():
        print(f"  {p['program_id']} | {p['education_level']} | {p['degree_type']} | {p['discipline_or_stream']} | {p['program_name']}")

conn.close()
