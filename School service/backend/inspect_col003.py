import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("SELECT * FROM students WHERE school_id = 'COL003'")
cols = [col[0] for col in c.description]
print("COL003 Students:")
for r in c.fetchall():
    print(dict(zip(cols, r)))

c.execute("SELECT * FROM enrollments WHERE school_id = 'COL003'")
e_cols = [col[0] for col in c.description]
print("\nCOL003 Enrollments:")
for r in c.fetchall():
    print(dict(zip(e_cols, r)))

conn.close()
