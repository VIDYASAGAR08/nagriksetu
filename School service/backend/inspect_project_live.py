import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()

print('=== DATABASE INTEGRITY & FOREIGN KEYS ===')
print('Integrity check:', c.execute('PRAGMA integrity_check').fetchall())
print('FK check:', c.execute('PRAGMA foreign_key_check').fetchall())

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print(f'\n=== TABLES IN NAGRIKSETU.DB ({len(tables)} tables) ===')
for t in tables:
    count = c.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
    print(f'  {t:30}: {count:>8} rows')

# Detailed inspection of specific key tables
print('\n=== KEY VERIFICATION METRICS ===')
print('Students count:', c.execute('SELECT count(*) FROM students').fetchone()[0])
print('Enrollments count:', c.execute('SELECT count(*) FROM enrollments').fetchone()[0])
print('Academic Programs count:', c.execute('SELECT count(*) FROM academic_programs').fetchone()[0])
print('Program Sections count:', c.execute('SELECT count(*) FROM program_sections').fetchone()[0])
print('Schools count:', c.execute('SELECT count(*) FROM schools').fetchone()[0])
print('Users count:', c.execute('SELECT count(*) FROM users').fetchone()[0])
print('Guardians count:', c.execute('SELECT count(*) FROM guardians').fetchone()[0])
print('Student Guardians count:', c.execute('SELECT count(*) FROM student_guardians').fetchone()[0])
print('Update Requests count:', c.execute('SELECT count(*) FROM update_requests').fetchone()[0])
print('School Achievements count:', c.execute('SELECT count(*) FROM school_achievements').fetchone()[0])
print('School Programs count:', c.execute('SELECT count(*) FROM school_programs').fetchone()[0])

# Inspect schools table columns
print('\n=== SCHOOLS TABLE COLUMNS ===')
for col in c.execute('PRAGMA table_info(schools)').fetchall():
    print(f'  {col[1]}: {col[2]}')

# Check users and roles
print('\n=== USERS AND ROLES ===')
for u in c.execute('SELECT user_id, email, phone, role, school_id, is_active FROM users').fetchall():
    print(f'  {u[1] or u[2]:30} | Role: {u[3]:15} | School: {str(u[4]):10} | Active: {u[5]}')

conn.close()
