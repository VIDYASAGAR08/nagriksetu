import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("""
    SELECT 
        s.school_id, 
        sc.school_name, 
        sc.school_type,
        COUNT(DISTINCT s.permanent_student_id) as total_students,
        COUNT(DISTINCT sa.permanent_student_id) as students_with_att,
        COUNT(DISTINCT ar.enrollment_id) as enrollments_with_results,
        COUNT(DISTINCT sd.permanent_student_id) as students_with_docs
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    LEFT JOIN student_attendance sa ON s.permanent_student_id = sa.permanent_student_id
    LEFT JOIN enrollments e ON s.permanent_student_id = e.permanent_student_id
    LEFT JOIN academic_results ar ON e.enrollment_id = ar.enrollment_id
    LEFT JOIN student_documents sd ON s.permanent_student_id = sd.permanent_student_id
    GROUP BY s.school_id
    ORDER BY s.school_id
""")

rows = cur.fetchall()
print(f"{'Inst ID':<8} | {'Type':<15} | {'Total':<6} | {'With Att':<8} | {'With Res':<8} | {'With Docs':<8} | Name")
print("-" * 80)
for r in rows:
    print(f"{r[0]:<8} | {r[2]:<15} | {r[3]:<6} | {r[4]:<8} | {r[5]:<8} | {r[6]:<8} | {r[1]}")

conn.close()
