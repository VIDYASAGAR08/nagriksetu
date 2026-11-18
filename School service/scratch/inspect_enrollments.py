import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- enrollments table info ---")
for c in cur.execute("PRAGMA table_info(enrollments)").fetchall():
    print(dict(c))

print("\n--- enrollments sample ---")
for r in cur.execute("SELECT * FROM enrollments LIMIT 5").fetchall():
    print(dict(r))

# Check how collegiate / PU students are enrolled or stored
# Let's inspect schools with school_type != 'School'
print("\n--- schools by school_type ---")
for r in cur.execute("SELECT school_id, school_name, school_type FROM schools WHERE school_type != 'School' LIMIT 15").fetchall():
    print(dict(r))

# Check students in those non-school institutions
non_schools = [r['school_id'] for r in cur.execute("SELECT school_id FROM schools WHERE school_type != 'School'").fetchall()]
print(f"\nNon-school institutions ({len(non_schools)}): {non_schools}")

for ns in non_schools[:5]:
    st_count = cur.execute("SELECT count(*) FROM students WHERE school_id = ?", (ns,)).fetchone()[0]
    enr_count = cur.execute("SELECT count(*) FROM enrollments WHERE school_id = ?", (ns,)).fetchone()[0]
    std_samples = cur.execute("SELECT student_id, permanent_student_id, student_name, standard, section FROM students WHERE school_id = ? LIMIT 3", (ns,)).fetchall()
    enr_samples = cur.execute("SELECT * FROM enrollments WHERE school_id = ? LIMIT 3", (ns,)).fetchall()
    print(f"School {ns}: {st_count} students, {enr_count} enrollments")
    print("  Student samples:", [dict(s) for s in std_samples])
    print("  Enrollment samples:", [dict(e) for e in enr_samples])

conn.close()
