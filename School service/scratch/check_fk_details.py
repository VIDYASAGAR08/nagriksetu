import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

# Get flagged PSIDs
cur.execute("SELECT permanent_student_id, school_id, review_flag FROM students WHERE review_flag IS NOT NULL")
flagged_rows = cur.fetchall()
flagged_psids = set(r[0] for r in flagged_rows)
print(f"Total flagged students in DB: {len(flagged_psids)}")

# Check foreign key / linked records across tables
tables_with_psid = [
    'enrollments', 'academic_results', 'student_attendance', 'fees',
    'scholarships', 'student_documents', 'student_guardians', 'update_requests',
    'school_transfers', 'institution_linking_codes', 'collegiate_enrollments',
    'linking_requests'
]

for t in tables_with_psid:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cur.fetchall()]
    id_col = 'permanent_student_id' if 'permanent_student_id' in cols else ('student_ref' if 'student_ref' in cols else None)
    if id_col:
        # Check count of matches
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        total = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM {t} WHERE {id_col} IN (SELECT permanent_student_id FROM students WHERE review_flag IS NOT NULL)")
        match_count = cur.fetchone()[0]
        print(f"Table '{t}': total rows = {total}, referencing flagged students = {match_count}")

# Check dossier fields directly on students table
cur.execute("PRAGMA table_info(students)")
student_cols = [c[1] for c in cur.fetchall()]
print(f"Students table has {len(student_cols)} columns:")
print(student_cols)

# Check dossier completion on flagged students
cur.execute("""
    SELECT COUNT(*) FROM students 
    WHERE review_flag IS NOT NULL 
    AND (attendance_percentage IS NOT NULL OR blood_group IS NOT NULL OR emergency_contact_name IS NOT NULL)
""")
dossier_populated = cur.fetchone()[0]
print(f"Flagged students with populated dossier attributes: {dossier_populated} of {len(flagged_psids)}")

conn.close()
