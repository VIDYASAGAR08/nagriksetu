import sqlite3

c = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
print('students COL:', c.execute('SELECT count(*) FROM students WHERE school_id LIKE "COL%"').fetchone()[0])
print('enrollments COL:', c.execute('SELECT count(*) FROM enrolments WHERE school_id LIKE "COL%"').fetchone()[0])
print('applications COL:', c.execute('SELECT count(*) FROM admission_applications WHERE school_id LIKE "COL%"').fetchone()[0])
print('applications per COL:', c.execute('SELECT school_id, status, count(*) FROM admission_applications WHERE school_id LIKE "COL%" GROUP BY school_id, status').fetchall())
