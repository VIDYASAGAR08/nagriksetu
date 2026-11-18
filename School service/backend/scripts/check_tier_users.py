import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
c = conn.cursor()
for code in ['SCH001', 'SCH011', 'COL001', 'COL010']:
    school = c.execute('SELECT school_id, school_name FROM schools WHERE school_id = ?', (code,)).fetchone()
    name = school[1] if school else 'Not found'
    print(f'=== {code}: {name} ===')
    admins = c.execute('SELECT user_id, email, role, status FROM users WHERE school_id = ? AND role = "school_admin"', (code,)).fetchall()
    print('  Admins:', admins)
    staff = c.execute('SELECT user_id, email, role, status FROM users WHERE school_id = ? AND role != "school_admin" AND role NOT IN ("student", "parent") LIMIT 2', (code,)).fetchall()
    print('  Staff:', staff)
    students = c.execute('SELECT s.permanent_student_id, s.student_id, s.student_name, u.user_id FROM students s LEFT JOIN users u ON (u.permanent_student_id = s.permanent_student_id OR u.student_id = s.student_id) WHERE s.school_id = ? LIMIT 2', (code,)).fetchall()
    print('  Students:', students)

platform_admins = c.execute('SELECT user_id, email, role FROM users WHERE role = "platform_admin"').fetchall()
print('Platform Admins:', platform_admins)

conn.close()
