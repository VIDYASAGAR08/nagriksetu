# Test import and syntax of academic endpoints logic
import sqlite3
import json
import uuid

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row

# Verify we can query student_attendance and examinations
print("Attendance count:", conn.execute("SELECT COUNT(*) FROM student_attendance").fetchone()[0])
print("Examinations count:", conn.execute("SELECT COUNT(*) FROM examinations").fetchone()[0])
print("Announcements count:", conn.execute("SELECT COUNT(*) FROM institution_announcements").fetchone()[0])

conn.close()
print("Tables query successful!")
