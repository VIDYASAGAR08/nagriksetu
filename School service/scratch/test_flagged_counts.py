import sqlite3
import csv

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

# Query PU flagged students (Group A)
cur.execute("""
    SELECT 
        s.student_id,
        s.permanent_student_id,
        s.student_name,
        s.school_id,
        sc.school_name,
        sc.school_type,
        s.standard,
        s.review_flag
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    WHERE s.school_id BETWEEN 'SCH011' AND 'SCH015'
      AND s.review_flag = 'FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS'
    ORDER BY s.school_id, s.standard, s.section, s.student_id
""")
pu_flagged = cur.fetchall()
print(f"Total Group A (PU College with Standards 1-10): {len(pu_flagged)}")

# Query School flagged students (Group B)
cur.execute("""
    SELECT 
        s.student_id,
        s.permanent_student_id,
        s.student_name,
        s.school_id,
        sc.school_name,
        sc.school_type,
        s.standard,
        s.review_flag
    FROM students s
    JOIN schools sc ON s.school_id = sc.school_id
    WHERE s.school_id BETWEEN 'SCH016' AND 'SCH020'
      AND s.review_flag = 'FLAGGED_REVIEW_K10_SCHOOL_HAS_PU_STUDENTS'
    ORDER BY s.school_id, s.standard, s.section, s.student_id
""")
school_flagged = cur.fetchall()
print(f"Total Group B (K-10 School with Standards 11-12): {len(school_flagged)}")

conn.close()
