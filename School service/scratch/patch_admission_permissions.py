import sqlite3
import re

backend_main = r'C:\Users\callm\nagriksetu\backend\main.py'
db_path = r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db'

# 1. Update Database permissions for academic_admin
conn = sqlite3.connect(db_path)
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
updated_perms = c.rowcount
conn.commit()
conn.close()
print(f"Updated {updated_perms} institution_staff_permissions rows in database.")

# 2. Patch backend/main.py
with open(backend_main, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix DEFAULT_ROLE_PERMS["academic_admin"]
old_role_perms = '''    "academic_admin": {
        "can_view_applications": 0,
        "can_review_details": 0,
        "can_request_clarification": 0,
        "can_recommend_decision": 0,
        "can_approve_stage1": 0,
        "can_view_history": 0,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },'''

new_role_perms = '''    "academic_admin": {
        "can_view_applications": 1,
        "can_review_details": 1,
        "can_request_clarification": 1,
        "can_recommend_decision": 1,
        "can_approve_stage1": 1,
        "can_view_history": 1,
        "can_manage_academics": 1,
        "can_manage_students": 1,
    },'''

if old_role_perms in code:
    code = code.replace(old_role_perms, new_role_perms)
    print("Fixed DEFAULT_ROLE_PERMS for academic_admin.")
elif old_role_perms.replace('\n', '\r\n') in code:
    code = code.replace(old_role_perms.replace('\n', '\r\n'), new_role_perms.replace('\n', '\r\n'))
    print("Fixed DEFAULT_ROLE_PERMS CRLF for academic_admin.")

# Fix get_staff_permissions
old_gsp = 'if role_id in ("school_admin", "platform_admin"):'
new_gsp = 'if role_id in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):'
if old_gsp in code:
    code = code.replace(old_gsp, new_gsp)
    print("Fixed get_staff_permissions check.")

# Fix all occurrences of `user["role"] not in ("school_admin", "platform_admin")`
old_not_in = 'user["role"] not in ("school_admin", "platform_admin")'
new_not_in = 'user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin")'
cnt_not_in = code.count(old_not_in)
if cnt_not_in > 0:
    code = code.replace(old_not_in, new_not_in)
    print(f"Replaced {cnt_not_in} occurrences of {old_not_in}.")

# Fix r["role_id"] in ("school_admin", "platform_admin")
old_r_in = 'if r["role_id"] in ("school_admin", "platform_admin"):'
new_r_in = 'if r["role_id"] in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):'
if old_r_in in code:
    code = code.replace(old_r_in, new_r_in)
    print("Fixed r[role_id] check in staff list.")

# Fix list_school_admission_applications status_filter logic and alias fields
old_list_apps = '''        if status_filter and status_filter.lower() != "all":
            sql += " AND a.status = ?"
            params.append(status_filter.lower())'''

new_list_apps = '''        if status_filter and status_filter.lower() != "all":
            sf = status_filter.lower()
            if sf in ("clarification_requested", "action_required"):
                sql += " AND a.status IN ('clarification_requested', 'action_required')"
            elif sf == "pending":
                sql += " AND a.status IN ('submitted', 'under_review', 'action_required', 'clarification_requested')"
            else:
                sql += " AND a.status = ?"
                params.append(sf)'''

if old_list_apps in code:
    code = code.replace(old_list_apps, new_list_apps)
    print("Fixed list_school_admission_applications status_filter logic.")
elif old_list_apps.replace('\n', '\r\n') in code:
    code = code.replace(old_list_apps.replace('\n', '\r\n'), new_list_apps.replace('\n', '\r\n'))
    print("Fixed list_school_admission_applications status_filter logic CRLF.")

old_return_apps = '''        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "applications": [dict(r) for r in rows]
        }'''

new_return_apps = '''        app_list = []
        for r in rows:
            rd = dict(r)
            rd["id"] = r["application_id"]
            rd["application_reference"] = r["application_id"]
            rd["student_name"] = r["applicant_name"]
            rd["standard"] = r["requested_standard"]
            app_list.append(rd)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "applications": app_list
        }'''

if old_return_apps in code:
    code = code.replace(old_return_apps, new_return_apps)
    print("Fixed list_school_admission_applications alias fields.")
elif old_return_apps.replace('\n', '\r\n') in code:
    code = code.replace(old_return_apps.replace('\n', '\r\n'), new_return_apps.replace('\n', '\r\n'))
    print("Fixed list_school_admission_applications alias fields CRLF.")

# Ensure pending_admission_reviews includes action_required in dashboard-overview
old_pending_sql = "status IN ('submitted', 'under_review', 'clarification_requested')"
new_pending_sql = "status IN ('submitted', 'under_review', 'clarification_requested', 'action_required')"
if old_pending_sql in code:
    code = code.replace(old_pending_sql, new_pending_sql)
    print("Fixed pending_admission_reviews query in dashboard-overview.")

with open(backend_main, 'w', encoding='utf-8') as f:
    f.write(code)

print("Backend patch successfully written.")
