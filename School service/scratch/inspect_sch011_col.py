import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- SCH011 (Tumakuru Model Pre-University College) ---")
st_count = cur.execute("SELECT count(*) FROM students WHERE school_id = 'SCH011'").fetchone()[0]
enr_count = cur.execute("SELECT count(*) FROM enrollments WHERE school_id = 'SCH011'").fetchone()[0]
print(f"Total students: {st_count}, enrollments: {enr_count}")

# Check distinct streams/combinations in enrollments for SCH011
cur.execute("SELECT standard, stream, subject_combination, count(*) FROM enrollments WHERE school_id = 'SCH011' GROUP BY standard, stream, subject_combination")
for r in cur.fetchall():
    print(dict(r))

# Check colleges (e.g. COL001, COL002, etc.)
print("\n--- COL001 (Ramaiah Institute of Technology) ---")
st_count = cur.execute("SELECT count(*) FROM students WHERE school_id = 'COL001'").fetchone()[0]
enr_count = cur.execute("SELECT count(*) FROM enrollments WHERE school_id = 'COL001'").fetchone()[0]
print(f"Total students: {st_count}, enrollments: {enr_count}")
cur.execute("SELECT standard, stream, subject_combination, count(*) FROM enrollments WHERE school_id = 'COL001' GROUP BY standard, stream, subject_combination")
for r in cur.fetchall():
    print(dict(r))

# Check all schools in schools table
print("\n--- All 30 institutions ---")
cur.execute("SELECT school_id, school_name, school_type, category FROM schools ORDER BY school_id")
for r in cur.fetchall():
    print(dict(r))

conn.close()
