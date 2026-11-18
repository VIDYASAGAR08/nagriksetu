import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. PRAGMA integrity_check
cur.execute("PRAGMA integrity_check")
ic = cur.fetchall()
print("PRAGMA integrity_check:", ic)

# 2. PRAGMA foreign_key_check
cur.execute("PRAGMA foreign_key_check")
fk = cur.fetchall()
print("PRAGMA foreign_key_check:", fk)

# 3. Active Institutions Count
cur.execute("SELECT COUNT(*) FROM schools WHERE is_active = 1")
schools_cnt = cur.fetchone()[0]
print("Active institutions count:", schools_cnt)

# By category
cur.execute("SELECT category, COUNT(*) FROM schools WHERE is_active = 1 GROUP BY category")
cats = cur.fetchall()
print("Categories:", cats)

# 4. Total students
cur.execute("SELECT COUNT(*) FROM students")
students_cnt = cur.fetchone()[0]
print("Total students count:", students_cnt)

# 5. Total enrollments
cur.execute("SELECT COUNT(*) FROM student_enrollments")
enr_cnt = cur.fetchone()[0]
print("Total enrollments count:", enr_cnt)

# 6. Admission applications
cur.execute("SELECT COUNT(*), status FROM admission_applications GROUP BY status")
apps = cur.fetchall()
print("Admission applications by status:", apps)

# 7. Institution Staff Permissions count
cur.execute("SELECT COUNT(*) FROM institution_staff_permissions")
isp_cnt = cur.fetchone()[0]
print("Staff permissions mappings count:", isp_cnt)

conn.close()
