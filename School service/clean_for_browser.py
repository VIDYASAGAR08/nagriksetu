import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

# Use student BSDS260001 or SCH19097
# Let's find a student from SCH019
st = c.execute("SELECT student_id, permanent_student_id, student_name FROM students WHERE school_id = 'SCH019' LIMIT 1").fetchone()
st_id, psid, st_name = st
print(f"Target student for browser test: {st_id}, {psid}, {st_name}")

# Clear linking requests and guardian links for this student
c.execute("DELETE FROM linking_requests WHERE permanent_student_id = ? OR student_ref = ?", (psid, st_id))
c.execute("DELETE FROM student_guardians WHERE permanent_student_id = ?", (psid,))
conn.commit()
print("Cleaned up student for fresh browser walkthrough.")
