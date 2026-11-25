import sqlite3
import uuid
import datetime

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Test test student in SCH001 (e.g., STU-SCH001-0001 or find one)
cur.execute("SELECT student_id, permanent_student_id, student_name, school_id, standard, section FROM students WHERE school_id = 'SCH001' LIMIT 1")
row = cur.fetchone()
print("Sample student in SCH001:", row)

# Test stats query for SCH001
cur.execute("SELECT COUNT(*) FROM students WHERE school_id = 'SCH001'")
tot = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM students WHERE school_id = 'SCH001' AND (enrollment_status = 'active' OR enrollment_status IS NULL)")
act = cur.fetchone()[0]
cur.execute("SELECT standard, COUNT(*) FROM students WHERE school_id = 'SCH001' GROUP BY standard ORDER BY standard")
by_std = cur.fetchall()
print(f"Stats SCH001: Total={tot}, Active={act}, Standards count={len(by_std)}")

# Test search by parent name query
cur.execute("""
    SELECT count(DISTINCT s.student_id)
    FROM students s
    JOIN student_guardians sg ON sg.permanent_student_id = s.permanent_student_id
    JOIN guardians g ON g.guardian_id = sg.guardian_id
    WHERE s.school_id = 'SCH001' AND g.full_name LIKE '%Kumar%'
""")
parent_search_count = cur.fetchone()[0]
print(f"Parent search count for '%Kumar%' in SCH001: {parent_search_count}")

# Test inserting a dummy audit log and rolling back to ensure schema works
cur.execute("""
    INSERT INTO student_record_audits (
        audit_id, student_id, permanent_student_id, institution_id,
        admin_user_id, admin_name, field_modified, previous_value,
        updated_value, reason, source, request_id, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "TEST-AUD-001", row[0], row[1], "SCH001",
    "USR-ADMIN-01", "Principal", "contact_number", "9876543210",
    "9876543211", "Parent updated emergency phone number", "Direct Admin Edit",
    None, datetime.datetime.utcnow().isoformat()
))
cur.execute("SELECT * FROM student_record_audits WHERE audit_id = 'TEST-AUD-001'")
test_aud = cur.fetchone()
print("Inserted test audit successfully:", test_aud)
conn.rollback() # Don't keep test record in live db
print("Rollback complete.")
conn.close()
