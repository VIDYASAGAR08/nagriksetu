import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

# Check current columns in students and enrollments
cur.execute("PRAGMA table_info(students)")
s_cols = [c[1] for c in cur.fetchall()]
print("division_id in students:", "division_id" in s_cols)
print("academic_division in students:", "academic_division" in s_cols)

cur.execute("PRAGMA table_info(enrollments)")
e_cols = [c[1] for c in cur.fetchall()]
print("division_id in enrollments:", "division_id" in e_cols)
print("academic_division in enrollments:", "academic_division" in e_cols)

conn.close()
