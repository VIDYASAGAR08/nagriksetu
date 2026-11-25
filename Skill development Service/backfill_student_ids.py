import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db'
)
cur = conn.cursor()

# Update existing enrolled, in_progress, and completed enrollments with student_id
update_query = """
UPDATE enrollments 
SET student_id = CONCAT('STU-2026-', LPAD(id, 6, '0')) 
WHERE status IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED') 
  AND (student_id IS NULL OR student_id = '');
"""
cur.execute(update_query)
conn.commit()

cur.execute("SELECT id, code, student_id, citizen_ref, citizen_name, status FROM enrollments WHERE status IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED');")
for r in cur.fetchall():
    print(r)
conn.close()
