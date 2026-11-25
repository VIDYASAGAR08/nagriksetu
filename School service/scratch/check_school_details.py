import sqlite3
import csv

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== Schools SCH011 - SCH020 in DB ===")
cur.execute("SELECT school_id, school_name, school_type, district FROM schools WHERE school_id BETWEEN 'SCH011' AND 'SCH020'")
schools = cur.fetchall()
for s in schools:
    print(s)

print("\n=== Flagged Summary in DB ===")
cur.execute("""
    SELECT school_id, review_flag, MIN(standard), MAX(standard), COUNT(*) 
    FROM students 
    WHERE review_flag IS NOT NULL 
    GROUP BY school_id, review_flag
    ORDER BY school_id
""")
for r in cur.fetchall():
    print(r)

print("\n=== Total Students per School SCH011 - SCH020 in DB ===")
cur.execute("""
    SELECT school_id, COUNT(*), 
           SUM(CASE WHEN review_flag IS NOT NULL THEN 1 ELSE 0 END) as flagged,
           SUM(CASE WHEN review_flag IS NULL THEN 1 ELSE 0 END) as unflagged
    FROM students 
    WHERE school_id BETWEEN 'SCH011' AND 'SCH020'
    GROUP BY school_id
    ORDER BY school_id
""")
for r in cur.fetchall():
    print(f"School {r[0]}: Total={r[1]}, Flagged={r[2]}, Unflagged={r[3]}")

conn.close()
