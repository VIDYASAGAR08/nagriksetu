import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

for s_id in ['SCH001', 'SCH011', 'COL001', 'COL004']:
    st_count = c.execute("SELECT COUNT(*) FROM students WHERE school_id=?", (s_id,)).fetchone()[0]
    enr_count = c.execute("SELECT COUNT(*) FROM enrollments WHERE school_id=?", (s_id,)).fetchone()[0]
    print(f"Inst {s_id}: students={st_count}, enrollments={enr_count}")
    sample_stu = c.execute("SELECT student_id, student_name, standard, section, permanent_student_id FROM students WHERE school_id=? LIMIT 2", (s_id,)).fetchall()
    print(f"  Sample students: {sample_stu}")
    sample_enr = c.execute("SELECT enrollment_id, permanent_student_id, academic_year, standard, section, stream, subject_combination FROM enrollments WHERE school_id=? LIMIT 2", (s_id,)).fetchall()
    print(f"  Sample enrollments: {sample_enr}")

conn.close()
