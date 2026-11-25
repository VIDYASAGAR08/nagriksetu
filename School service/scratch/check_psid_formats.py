import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== PSID samples across institutions ===")
for sid in ['SCH001', 'SCH002', 'SCH010', 'SCH011', 'SCH012', 'SCH020', 'COL003']:
    cur.execute(f"SELECT student_id, permanent_student_id FROM students WHERE school_id='{sid}' LIMIT 3")
    print(f"School {sid}: {cur.fetchall()}")

conn.close()
