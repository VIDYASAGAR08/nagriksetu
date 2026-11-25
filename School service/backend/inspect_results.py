import sqlite3

conn = sqlite3.connect('data/nagriksetu.db')
c = conn.cursor()

c.execute("""
    SELECT s.school_id, ar.subject_name, COUNT(*)
    FROM academic_results ar
    JOIN students s ON s.permanent_student_id = ar.permanent_student_id
    GROUP BY s.school_id, ar.subject_name
""")
print("Academic results per school and subject:")
for r in c.fetchall():
    print(f"  {r[0]} | {r[1]}: {r[2]}")

c.execute("""
    SELECT s.school_id, s.standard, ar.subject_name, COUNT(*)
    FROM academic_results ar
    JOIN students s ON s.permanent_student_id = ar.permanent_student_id
    WHERE s.school_id IN ('SCH011', 'SCH012', 'COL003')
    GROUP BY s.school_id, s.standard, ar.subject_name
""")
print("\nAcademic results in SCH011, SCH012, COL003:")
for r in c.fetchall():
    print(f"  {r[0]} | Std {r[1]} | {r[2]}: {r[3]}")

conn.close()
