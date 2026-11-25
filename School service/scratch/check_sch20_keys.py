import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()

cur.execute("SELECT attendance_id, permanent_student_id FROM student_attendance WHERE institution_id='SCH020' LIMIT 5")
print("SCH020 attendance sample:", cur.fetchall())

cur.execute("SELECT result_id, permanent_student_id FROM academic_results WHERE permanent_student_id LIKE 'NS-SCH020%' LIMIT 5")
print("SCH020 results sample:", cur.fetchall())

cur.execute("SELECT document_id, permanent_student_id FROM student_documents WHERE permanent_student_id LIKE 'NS-SCH020%' LIMIT 5")
print("SCH020 documents sample:", cur.fetchall())

conn.close()
