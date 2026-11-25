import sqlite3
import json
import urllib.request
import urllib.error

# Let's inspect an admin user in nagriksetu.db
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
cur = conn.cursor()
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE role IN ('institution_admin', 'school_admin') LIMIT 5")
admins = cur.fetchall()
print("Sample admin users:", admins)

# Also check passwords or test token generation
cur.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard FROM students WHERE school_id = 'SCH001' LIMIT 1")
sample_stu = cur.fetchone()
print("Sample student in SCH001:", sample_stu)

conn.close()
