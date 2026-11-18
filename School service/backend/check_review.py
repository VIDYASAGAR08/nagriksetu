
import os
import sqlite3

db_path = os.environ["DATABASE_PATH"]
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

request_id = "6d073fa7-c240-4e16-808d-475041b4337c"
student_id = "NS-FB8336A812DE468FB8E475443CF673EB"

request = conn.execute(
    """
    SELECT request_id, status, review_comment, reviewed_at
    FROM update_requests
    WHERE request_id = ?
    """,
    (request_id,),
).fetchone()

print("REQUEST STATUS:")
print(dict(request) if request else "Request not found")

student = conn.execute(
    """
    SELECT student_name, first_language
    FROM students
    WHERE permanent_student_id = ?
    """,
    (student_id,),
).fetchone()

print("\nSTUDENT RECORD:")
print(dict(student) if student else "Student not found")

logs = conn.execute(
    """
    SELECT field_name, old_value, new_value,
           changed_by_user_id, change_reason, changed_at
    FROM school_change_log
    WHERE permanent_student_id = ?
    ORDER BY changed_at DESC
    """,
    (student_id,),
).fetchall()

print("\nAUDIT LOG:")
for log in logs:
    print(dict(log))

conn.close()
