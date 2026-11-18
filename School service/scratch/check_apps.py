import sqlite3
c = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
print('admission_applications per inst:', c.execute('SELECT institution_id, status, count(*) FROM admission_applications GROUP BY institution_id, status').fetchall())
