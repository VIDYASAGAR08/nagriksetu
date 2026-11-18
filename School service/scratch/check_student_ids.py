import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()
mismatches = c.execute("SELECT student_id, school_id FROM students WHERE length(student_id) != 8 LIMIT 20").fetchall()
print("Length != 8:", mismatches)
sample_by_prefix = c.execute("SELECT SUBSTR(student_id, 1, 3), COUNT(*) FROM students GROUP BY SUBSTR(student_id, 1, 3)").fetchall()
print("Prefix distribution:", sample_by_prefix)
conn.close()
