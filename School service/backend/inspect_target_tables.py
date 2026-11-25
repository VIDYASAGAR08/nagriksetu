import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

for t in ["student_attendance", "academic_results", "students", "guardians", "portal_notifications"]:
    print(f"\n--- {t} columns ---")
    cols = cursor.execute(f"PRAGMA table_info({t})").fetchall()
    for c in cols:
        print(f"  {c['name']} ({c['type']})")
    sample = cursor.execute(f"SELECT * FROM {t} LIMIT 1").fetchone()
    if sample:
        print(f"  Sample: {dict(sample)}")

conn.close()
