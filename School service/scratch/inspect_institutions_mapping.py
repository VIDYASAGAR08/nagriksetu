import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== ALL INSTITUTIONS IN NAGRIKSETU ===")
cur.execute("""
    SELECT sc.school_id, sc.school_name, sc.school_type, sc.category, sc.district,
           COUNT(s.student_id) as student_count
    FROM schools sc
    LEFT JOIN students s ON sc.school_id = s.school_id
    GROUP BY sc.school_id
    ORDER BY sc.school_id
""")
institutions = cur.fetchall()

print(f"{'ID':<8} | {'Type':<15} | {'Category':<15} | {'District':<16} | {'Count':<6} | Name")
print("-" * 90)
for r in institutions:
    print(f"{r[0]:<8} | {r[1]:<15} | {r[2]:<15} | {r[4]:<16} | {r[5]:<6} | {r[1]}")

conn.close()
