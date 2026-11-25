import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== PU students in SCH016-SCH020 ===")
cur.execute("""
    SELECT s.school_id, s.standard, s.stream, s.subject_combination, e.stream, e.subject_combination, COUNT(*)
    FROM students s
    LEFT JOIN enrollments e ON s.permanent_student_id = e.permanent_student_id
    WHERE s.school_id BETWEEN 'SCH016' AND 'SCH020' AND s.standard IN (11, 12)
    GROUP BY s.school_id, s.standard, s.stream, s.subject_combination, e.stream, e.subject_combination
""")
for r in cur.fetchall():
    print(r)

print("\n=== PU students in SCH011-SCH015 (Standards 11-12) ===")
cur.execute("""
    SELECT s.school_id, s.standard, s.stream, s.subject_combination, COUNT(*)
    FROM students s
    WHERE s.school_id BETWEEN 'SCH011' AND 'SCH015' AND s.standard IN (11, 12)
    GROUP BY s.school_id, s.standard, s.stream, s.subject_combination
""")
for r in cur.fetchall():
    print(r)

conn.close()
