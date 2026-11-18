import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

# Check enrollments
cur.execute('PRAGMA table_info(enrollments)')
cols = [c[1] for c in cur.fetchall()]
print('enrollments columns:', cols)

# Check students
cur.execute('PRAGMA table_info(students)')
print('students columns:', [c[1] for c in cur.fetchall()])

# Check admission_applications
cur.execute('PRAGMA table_info(admission_applications)')
print('admission_applications columns:', [c[1] for c in cur.fetchall()])

# Check which tables have program_id or section_id in their schema
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for name, sql in cur.fetchall():
    if 'program_id' in sql or 'section_id' in sql:
        print(f"Table {name} references program_id/section_id")

conn.close()
