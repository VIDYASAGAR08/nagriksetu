import sqlite3
import json

conn = sqlite3.connect("data/nagriksetu.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

student_count = cursor.execute("SELECT COUNT(1) FROM students").fetchone()[0]
print(f"Total Students: {student_count}")

schools = cursor.execute("""
    SELECT s.school_id, s.school_name, s.school_type, COUNT(st.student_id) AS student_count
    FROM schools s
    LEFT JOIN students st ON st.school_id = s.school_id
    GROUP BY s.school_id
    ORDER BY s.school_id
""").fetchall()

print(f"\nTotal Institutions: {len(schools)}")
for s in schools:
    print(f"  {s['school_id']}: {s['school_name']} [{s['school_type']}] -> {s['student_count']} students")

tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"\nTables in database ({len(tables)}):")
for t in sorted(tables):
    count = cursor.execute(f"SELECT COUNT(1) FROM {t}").fetchone()[0]
    cols = [c[1] for c in cursor.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"  {t} ({count} rows) -> cols: {', '.join(cols[:8])}...")

conn.close()
