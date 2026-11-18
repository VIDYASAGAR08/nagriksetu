main_py_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_py_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update get_parent_guardian to auto-provision
old_get_parent = """def get_parent_guardian(conn, user_id: str):
    return conn.execute(
        \"\"\"
        SELECT guardian_id, user_id, full_name
        FROM guardians
        WHERE user_id = ?
        \"\"\",
        (user_id,),
    ).fetchone()"""

new_get_parent = """def get_parent_guardian(conn, user_id: str):
    row = conn.execute(
        \"\"\"
        SELECT guardian_id, user_id, full_name
        FROM guardians
        WHERE user_id = ?
        \"\"\",
        (user_id,),
    ).fetchone()
    if row is None:
        user_row = conn.execute(
            \"SELECT user_id, full_name, phone, email FROM users WHERE user_id = ?\",
            (user_id,)
        ).fetchone()
        if user_row:
            gid = str(uuid.uuid4())
            conn.execute(
                \"\"\"
                INSERT INTO guardians (guardian_id, user_id, full_name, relationship, phone, email)
                VALUES (?, ?, ?, 'Guardian', ?, ?)
                \"\"\",
                (gid, user_id, user_row[\"full_name\"] or \"Parent Guardian\", user_row[\"phone\"] or \"9999999999\", user_row[\"email\"] or \"\")
            )
            row = conn.execute(
                \"SELECT guardian_id, user_id, full_name FROM guardians WHERE guardian_id = ?\",
                (gid,)
            ).fetchone()
    return row"""

if old_get_parent in text:
    text = text.replace(old_get_parent, new_get_parent)
    print("Updated get_parent_guardian to auto-provision.")

# 2. Update review_school_linking_request to use get_parent_guardian
old_guardian_lookup = """            # 6. Resolve parent guardian record
            guardian = conn.execute(
                \"\"\"
                SELECT guardian_id, user_id, full_name
                FROM guardians
                WHERE user_id = ?
                \"\"\",
                (lr[\"parent_user_id\"],),
            ).fetchone()

            if guardian is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=\"No guardian profile found for the requesting parent.\",
                )"""

new_guardian_lookup = """            # 6. Resolve parent guardian record
            guardian = get_parent_guardian(conn, lr[\"parent_user_id\"])
            if guardian is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=\"No guardian profile found for the requesting parent.\",
                )"""

if old_guardian_lookup in text:
    text = text.replace(old_guardian_lookup, new_guardian_lookup)
    print("Updated guardian lookup in review_school_linking_request.")

# 3. In confirm_final_admission_and_enrol, auto-link to student_guardians if parent_user_id exists
target_in_enrol = "# 6. Notify parent\n        if app_row[\"parent_user_id\"]:"
replacement_in_enrol = """# 6. Auto-link student to parent guardian
        if app_row[\"parent_user_id\"]:
            p_guardian = get_parent_guardian(conn, app_row[\"parent_user_id\"])
            if p_guardian:
                conn.execute(
                    \"\"\"
                    INSERT OR REPLACE INTO student_guardians (
                        student_guardian_id, permanent_student_id, guardian_id,
                        can_view_records, can_request_updates, is_verified, created_at
                    ) VALUES (?, ?, ?, 1, 1, 1, CURRENT_TIMESTAMP)
                    \"\"\",
                    (str(uuid.uuid4()), perm_student_id, p_guardian[\"guardian_id\"])
                )

        # 7. Notify parent
        if app_row[\"parent_user_id\"]:"""

if target_in_enrol in text:
    text = text.replace(target_in_enrol, replacement_in_enrol)
    print("Added auto-linking to student_guardians in confirm_final_admission_and_enrol.")

with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("backend/main.py successfully patched for Phase 7 Parent Portal.")
