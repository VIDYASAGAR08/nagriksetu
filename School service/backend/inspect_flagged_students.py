import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
cur = conn.cursor()

print('=== Sample of SCH011 FLAGGED students (Standards 1-10) ===')
cur.execute("SELECT student_id, student_name, standard, section, permanent_student_id, stream, subject_combination FROM students WHERE school_id='SCH011' AND review_flag IS NOT NULL LIMIT 5")
for r in cur.fetchall():
    print(r)

print('\n=== Sample of SCH011 UNFLAGGED students (Standards 11-12) ===')
cur.execute("SELECT student_id, student_name, standard, section, permanent_student_id, stream, subject_combination FROM students WHERE school_id='SCH011' AND review_flag IS NULL LIMIT 5")
for r in cur.fetchall():
    print(r)

print('\n=== Sample of SCH016 FLAGGED students (Standards 11-12) ===')
cur.execute("SELECT student_id, student_name, standard, section, permanent_student_id, stream, subject_combination FROM students WHERE school_id='SCH016' AND review_flag IS NOT NULL LIMIT 5")
for r in cur.fetchall():
    print(r)

print('\n=== Sample of SCH016 UNFLAGGED students (Standards 1-10) ===')
cur.execute("SELECT student_id, student_name, standard, section, permanent_student_id, stream, subject_combination FROM students WHERE school_id='SCH016' AND review_flag IS NULL LIMIT 5")
for r in cur.fetchall():
    print(r)

conn.close()
