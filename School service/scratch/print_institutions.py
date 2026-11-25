import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("""
    SELECT sc.school_id, sc.school_name, sc.school_type, sc.district,
           COUNT(s.student_id) as student_count
    FROM schools sc
    LEFT JOIN students s ON sc.school_id = s.school_id
    GROUP BY sc.school_id
    ORDER BY sc.school_id
""")
institutions = cur.fetchall()

print(f"{'ID':<8} | {'Type':<15} | {'District':<16} | {'Count':<6} | Name")
print("-" * 80)
for r in institutions:
    print(f"{r[0]:<8} | {r[2]:<15} | {r[3]:<16} | {r[4]:<6} | {r[1]}")

conn.close()
