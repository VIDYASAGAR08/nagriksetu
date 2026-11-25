import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("SELECT * FROM admission_applications WHERE institution_id IN ('COL010', 'COL001', 'COL003') LIMIT 10")
cols = [col[0] for col in c.description]
for r in c.fetchall():
    print(dict(zip(cols, r)))

conn.close()
