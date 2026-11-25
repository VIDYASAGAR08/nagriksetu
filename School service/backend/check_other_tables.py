import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

print("--- Admission applications per institution ---")
c.execute("SELECT institution_id, count(*) FROM admission_applications GROUP BY institution_id")
for r in c.fetchall():
    print(r)

print("\n--- Users per school_id ---")
c.execute("SELECT school_id, role, count(*) FROM users GROUP BY school_id, role")
for r in c.fetchall():
    print(r)

conn.close()
