file_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    existing_perm = conn.execute(\"\"\"
        SELECT permission_id FROM institution_staff_permissions WHERE user_id = ? AND institution_id = ?
    \"\"\", (user_id, inst_id)).fetchone()

    if existing_perm:
        conn.execute(\"\"\"
            UPDATE institution_staff_permissions
            SET role_id = ?, can_view_applications = ?, can_review_details = ?,
                can_request_clarification = ?, can_recommend_decision = ?, can_approve_stage1 = ?,
                can_view_history = ?, can_manage_academics = ?, can_manage_students = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE permission_id = ?
        \"\"\", (
            role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            existing_perm["permission_id"]
        ))
    else:
        conn.execute(\"\"\"
            INSERT INTO institution_staff_permissions (
                permission_id, user_id, institution_id, role_id,
                can_view_applications, can_review_details, can_request_clarification,
                can_recommend_decision, can_approve_stage1, can_view_history,
                can_manage_academics, can_manage_students, granted_by_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            str(uuid.uuid4()), user_id, inst_id, role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            row["reviewed_by_user_id"]
        ))"""

replacement = """    existing_perm = conn.execute(\"\"\"
        SELECT id FROM institution_staff_permissions WHERE user_id = ? AND institution_id = ?
    \"\"\", (user_id, inst_id)).fetchone()

    if existing_perm:
        conn.execute(\"\"\"
            UPDATE institution_staff_permissions
            SET role_id = ?, can_view_applications = ?, can_review_details = ?,
                can_request_clarification = ?, can_recommend_decision = ?, can_approve_stage1 = ?,
                can_view_history = ?, can_manage_academics = ?, can_manage_students = ?,
                updated_at = CURRENT_TIMESTAMP, updated_by = ?
            WHERE id = ?
        \"\"\", (
            role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            row["reviewed_by_user_id"],
            existing_perm["id"]
        ))
    else:
        conn.execute(\"\"\"
            INSERT INTO institution_staff_permissions (
                id, user_id, institution_id, role_id,
                can_view_applications, can_review_details, can_request_clarification,
                can_recommend_decision, can_approve_stage1, can_view_history,
                can_manage_academics, can_manage_students, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            str(uuid.uuid4()), user_id, inst_id, role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            row["reviewed_by_user_id"]
        ))"""

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Fixed institution_staff_permissions schema references in main.py!")
