# -*- coding: utf-8 -*-
import pymysql

db = pymysql.connect(host='skill-service-db', port=3306, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cursor = db.cursor()

# 1. Total Skills & active skills
cursor.execute('SELECT COUNT(*), active FROM skills GROUP BY active')
print('Skills by active (count, active):', cursor.fetchall())
cursor.execute('SELECT COUNT(*) FROM skills')
print('Total skills in database:', cursor.fetchone()[0])
cursor.execute("SELECT id, code, name, active FROM skills WHERE code = 'SKL-0104'")
print('SKL-0104:', cursor.fetchone())

# 2. Total Enrollments & by status
cursor.execute('SELECT COUNT(*), status FROM enrollments GROUP BY status')
print('Enrollments by status (count, status):', cursor.fetchall())
cursor.execute('SELECT COUNT(*) FROM enrollments')
print('Total enrollments in database:', cursor.fetchone()[0])

# 3. ENR-000103 details
cursor.execute('''
    SELECT e.id, e.enrollment_code, e.citizen_id, c.full_name, c.email, 
           e.program_id, p.code as prog_code, p.title as prog_title,
           e.centre_id, tc.code as centre_code, tc.name as centre_name,
           e.batch_id, b.batch_code, b.name as batch_name,
           e.status, e.training_progress_pct, e.attendance_pct, e.internal_remarks, e.created_at
    FROM enrollments e
    LEFT JOIN citizens c ON e.citizen_id = c.id
    LEFT JOIN training_programs p ON e.program_id = p.id
    LEFT JOIN training_centres tc ON e.centre_id = tc.id
    LEFT JOIN training_batches b ON e.batch_id = b.id
    WHERE e.enrollment_code = 'ENR-000103'
''')
print('ENR-000103 full row:', cursor.fetchone())

# 4. Centres CTR-0006 to CTR-0010
cursor.execute('''
    SELECT tc.id, tc.code, tc.name, tc.is_active, tc.approval_status, tc.notes,
           (SELECT COUNT(*) FROM training_programs WHERE centre_id = tc.id) as prog_count,
           (SELECT COUNT(*) FROM enrollments WHERE centre_id = tc.id) as enr_count,
           (SELECT COUNT(*) FROM accounts WHERE centre_id = tc.id) as acc_count
    FROM training_centres tc
    WHERE tc.code IN ('CTR-0006', 'CTR-0007', 'CTR-0008', 'CTR-0009', 'CTR-0010')
    ORDER BY tc.id
''')
for row in cursor.fetchall():
    print('Centre detail:', row)

# 5. Accounts for these centres
cursor.execute('''
    SELECT a.id, a.email, a.role, a.centre_id, tc.code, tc.name
    FROM accounts a
    JOIN training_centres tc ON a.centre_id = tc.id
    WHERE tc.code IN ('CTR-0006', 'CTR-0007', 'CTR-0008', 'CTR-0009', 'CTR-0010')
''')
print('Assigned Accounts:', cursor.fetchall())

db.close()
