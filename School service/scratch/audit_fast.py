import sqlite3
import time

t0 = time.time()
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
print(f"Total attendance rows: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM academic_results")
print(f"Total academic result rows: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM student_documents")
print(f"Total document rows: {cur.fetchone()[0]}")

# Fast institution-wise counts
cur.execute("SELECT school_id, school_name, school_type FROM schools ORDER BY school_id")
schools = cur.fetchall()

# Student count per school
cur.execute("SELECT school_id, COUNT(*) FROM students GROUP BY school_id")
students_per_school = dict(cur.fetchall())

# Attendance count per school
cur.execute("""
    SELECT s.school_id, COUNT(DISTINCT sa.permanent_student_id)
    FROM student_attendance sa
    JOIN students s ON sa.permanent_student_id = s.permanent_student_id
    GROUP BY s.school_id
""")
att_per_school = dict(cur.fetchall())

# Results count per school
cur.execute("""
    SELECT s.school_id, COUNT(DISTINCT ar.permanent_student_id)
    FROM academic_results ar
    JOIN students s ON ar.permanent_student_id = s.permanent_student_id
    GROUP BY s.school_id
""")
res_per_school = dict(cur.fetchall())

# Docs count per school
cur.execute("""
    SELECT s.school_id, COUNT(DISTINCT sd.permanent_student_id)
    FROM student_documents sd
    JOIN students s ON sd.permanent_student_id = s.permanent_student_id
    GROUP BY s.school_id
""")
docs_per_school = dict(cur.fetchall())

print("\n--- Institution-wise Coverage Table ---")
print(f"{'Inst ID':<8} | {'Type':<15} | {'Total':<6} | {'Personal':<8} | {'Att':<6} | {'Res':<6} | {'Docs':<6} | Name")
print("-" * 85)
for sid, sname, stype in schools:
    tot = students_per_school.get(sid, 0)
    if tot > 0:
        att = att_per_school.get(sid, 0)
        res = res_per_school.get(sid, 0)
        doc = docs_per_school.get(sid, 0)
        print(f"{sid:<8} | {stype:<15} | {tot:<6} | {tot:<8} | {att:<6} | {res:<6} | {doc:<6} | {sname}")

conn.close()
print(f"\nAudit completed in {time.time() - t0:.2f}s")
