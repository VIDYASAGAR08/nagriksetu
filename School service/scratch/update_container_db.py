import sqlite3

conn = sqlite3.connect('/app/data/nagriksetu.db')
c = conn.cursor()
c.execute("""
    UPDATE institution_staff_permissions
    SET can_view_applications = 1,
        can_review_details = 1,
        can_request_clarification = 1,
        can_recommend_decision = 1,
        can_approve_stage1 = 1,
        can_view_history = 1,
        can_manage_academics = 1,
        can_manage_students = 1
    WHERE role_id = 'academic_admin'
""")
print('Updated rows in container db:', c.rowcount)
conn.commit()
conn.close()
