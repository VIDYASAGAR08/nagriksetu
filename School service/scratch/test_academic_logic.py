import sqlite3
import uuid

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")

def calculate_grade(marks: float, max_marks: float):
    if max_marks <= 0:
        return 0.0, "N/A"
    pct = round((marks / max_marks) * 100.0, 2)
    if pct >= 90.0:
        grade = "A+"
    elif pct >= 80.0:
        grade = "A"
    elif pct >= 70.0:
        grade = "B+"
    elif pct >= 60.0:
        grade = "B"
    elif pct >= 50.0:
        grade = "C"
    elif pct >= 35.0:
        grade = "D"
    else:
        grade = "F"
    return pct, grade

print("Grade tests:")
print("95/100 ->", calculate_grade(95, 100))
print("82/100 ->", calculate_grade(82, 100))
print("65/100 ->", calculate_grade(65, 100))
print("34/100 ->", calculate_grade(34, 100))

# Test attendance calculation logic
test_psid = "NS-FB8336A812DE468FB8E475443CF673EB" # Asha Sharma
c = conn.cursor()

# Check student exists
stu = c.execute("SELECT student_id, student_name, school_id FROM students WHERE permanent_student_id = ?", (test_psid,)).fetchone()
print("Found student:", dict(stu))

conn.close()
