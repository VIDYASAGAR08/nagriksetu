import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

print("=== FINAL 30,003 STUDENTS DOSSIER AUDIT ===")

cur.execute("SELECT COUNT(*) FROM students")
total_students = cur.fetchone()[0]
print(f"Total students in DB: {total_students}")

cur.execute("SELECT COUNT(*) FROM students WHERE blood_group IS NOT NULL AND address IS NOT NULL AND date_of_birth IS NOT NULL")
total_personal = cur.fetchone()[0]
print(f"Students with complete personal demographics: {total_personal} ({(total_personal/total_students)*100:.1f}%)")

cur.execute("SELECT COUNT(*) FROM enrollments")
total_enrollments = cur.fetchone()[0]
print(f"Total academic enrollments: {total_enrollments}")

cur.execute("SELECT COUNT(DISTINCT permanent_student_id) FROM student_attendance")
total_att_students = cur.fetchone()[0]
print(f"Students with attendance logs: {total_att_students} ({(total_att_students/total_students)*100:.1f}%)")

cur.execute("SELECT COUNT(DISTINCT permanent_student_id) FROM academic_results")
total_res_students = cur.fetchone()[0]
print(f"Students with examination results: {total_res_students} ({(total_res_students/total_students)*100:.1f}%)")

cur.execute("SELECT COUNT(DISTINCT permanent_student_id) FROM student_documents")
total_doc_students = cur.fetchone()[0]
print(f"Students with verification documents: {total_doc_students} ({(total_doc_students/total_students)*100:.1f}%)")

cur.execute("SELECT COUNT(*) FROM student_attendance")
total_att_rows = cur.fetchone()[0]
print(f"Total attendance rows: {total_att_rows}")

cur.execute("SELECT COUNT(*) FROM academic_results")
total_res_rows = cur.fetchone()[0]
print(f"Total academic result rows: {total_res_rows}")

cur.execute("SELECT COUNT(*) FROM student_documents")
total_doc_rows = cur.fetchone()[0]
print(f"Total document rows: {total_doc_rows}")

print("\n--- Institution-wise Coverage ---")
cur.execute("""
    SELECT 
        s.school_id,
        sc.school_name,
        sc.school_type,
        COUNT(DISTINCT s.student_id) as total_sids,
        COUNT(DISTINCT s.permanent_student_id) as total_psids,
        COUNT(DISTINCT sa.permanent_student_id) as att_psids,
        COUNT(DISTINCT ar.permanent_student_id) as res_psids,
        COUNT(DISTINCT sd.permanent_student_id) as doc_psids
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    LEFT JOIN student_attendance sa ON s.permanent_student_id = sa.permanent_student_id
    LEFT JOIN academic_results ar ON s.permanent_student_id = ar.permanent_student_id
    LEFT JOIN student_documents sd ON s.permanent_student_id = sd.permanent_student_id
    GROUP BY s.school_id
    ORDER BY s.school_id
""")
rows = cur.fetchall()
print(f"{'Inst ID':<8} | {'Type':<15} | {'Total':<6} | {'Personal':<8} | {'Att':<6} | {'Res':<6} | {'Docs':<6} | Name")
print("-" * 85)
for r in rows:
    print(f"{r[0]:<8} | {r[2]:<15} | {r[3]:<6} | {r[4]:<8} | {r[5]:<6} | {r[6]:<6} | {r[7]:<6} | {r[1]}")

conn.close()
