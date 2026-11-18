import sqlite3
c = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
print('collegiate_enrollments count:', c.execute('SELECT count(*) FROM collegiate_enrollments').fetchone()[0])
print('collegiate_enrollments sample:', c.execute('SELECT * FROM collegiate_enrollments LIMIT 3').fetchall())
print('admission_applications per inst:', c.execute('SELECT school_id, status, count(*) FROM admission_applications GROUP BY school_id, status').fetchall())
