import sqlite3

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()

# Check that every permanent_student_id in students has a matching enrollment
mismatch = c.execute("""
    SELECT COUNT(*) FROM students s
    LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
    WHERE e.enrollment_id IS NULL
""").fetchone()[0]
print("Students without enrollment:", mismatch)

conn.close()
