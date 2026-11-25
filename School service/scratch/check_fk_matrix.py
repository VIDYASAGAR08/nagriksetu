import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

tables = [
    'students', 'enrollments', 'student_attendance', 'academic_results',
    'student_documents', 'student_guardians', 'linking_requests',
    'institution_linking_codes', 'service_requests', 'request_corrections',
    'academic_result_audits', 'school_transfers', 'update_requests'
]

print("=== TABLES AND COLUMNS REFERENCING INSTITUTION OR STUDENT ===")
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cur.fetchall()]
    matching = [c for c in cols if any(k in c.lower() for k in ['school', 'inst', 'student', 'perm', 'enr'])]
    print(f"Table '{t}': {matching}")

conn.close()
