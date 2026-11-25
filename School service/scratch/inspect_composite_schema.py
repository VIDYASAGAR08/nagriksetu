import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

tables_to_check = ['institution_divisions', 'academic_programs', 'schools', 'students', 'enrollments']
for t in tables_to_check:
    print(f"\n--- PRAGMA table_info({t}) ---")
    cur.execute(f"PRAGMA table_info({t})")
    for c in cur.fetchall():
        print(f"  {c[1]}: {c[2]}")

print("\n--- Current institution_divisions rows ---")
cur.execute("SELECT * FROM institution_divisions")
for r in cur.fetchall():
    print(r)

conn.close()
