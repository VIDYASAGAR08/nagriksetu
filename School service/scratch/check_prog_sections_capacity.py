import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("""
    SELECT institution_id, COUNT(*), SUM(current_strength), SUM(capacity)
    FROM program_sections
    GROUP BY institution_id
    ORDER BY institution_id
""")
print("=== program_sections capacity by institution ===")
for r in cur.fetchall():
    print(f"Inst {r[0]}: sections={r[1]}, current_strength={r[2]}, capacity={r[3]}")

conn.close()
