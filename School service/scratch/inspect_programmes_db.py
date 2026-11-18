import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Find tables related to programmes, degrees, schools, courses, streams
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in DB:", tables)

# Check schools / institutions and their types
print("\n--- Institutions and columns ---")
cols = [c[1] for c in cur.execute("PRAGMA table_info(schools)").fetchall()]
print("Schools cols:", cols)
schools = cur.execute("SELECT * FROM schools LIMIT 5").fetchall()
for s in schools:
    print(dict(s))

# Check tables with 'program' or 'course' or 'stream' or 'academic'
academic_tables = [t for t in tables if any(k in t.lower() for k in ['program', 'course', 'stream', 'degree', 'academic', 'subject', 'section', 'enroll'])]
print("\nAcademic tables:", academic_tables)

for at in academic_tables:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({at})").fetchall()]
    count = cur.execute(f"SELECT count(*) FROM {at}").fetchone()[0]
    print(f"Table {at} ({count} rows): {cols}")
    sample = cur.execute(f"SELECT * FROM {at} LIMIT 3").fetchall()
    print("  Sample:", [dict(r) for r in sample])

conn.close()
