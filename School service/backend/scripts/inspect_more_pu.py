import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
cur.execute("SELECT count(*) FROM collegiate_enrollments WHERE institution_id BETWEEN 'SCH011' AND 'SCH015'")
print('collegiate_enrollments for PU:', cur.fetchone()[0])
conn.close()
