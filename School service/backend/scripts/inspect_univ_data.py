import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== INSTITUTION DIVISIONS / FACULTIES FOR UNIVERSITIES ===")
cur.execute("SELECT * FROM institution_divisions WHERE parent_institution_id IN ('COL004', 'COL006', 'COL008', 'COL009', 'COL010')")
for r in cur.fetchall():
    print(dict(r))

print("\n=== PROGRAMS FOR UNIVERSITIES ===")
cur.execute("SELECT * FROM academic_programs WHERE institution_id IN ('COL004', 'COL006', 'COL008', 'COL009', 'COL010')")
for r in cur.fetchall():
    print(dict(r))

conn.close()
