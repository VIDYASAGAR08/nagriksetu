file_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    audit_id = str(uuid.uuid4())
    conn.execute(\"\"\"
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_ACCOUNT_ACTIVATED', 'users', ?, ?, 'staff', ?, ?)
    \"\"\", (audit_id, user_id, email_clean, inst_id, json.dumps({"""

replacement = """    audit_id = str(uuid.uuid4())
    conn.execute(\"\"\"
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_ACCOUNT_ACTIVATED', 'users', ?, ?, 'staff', ?, ?)
    \"\"\", (audit_id, user_id, user_id, inst_id, json.dumps({"""

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Fixed audit_logs parameters in activate_approved_candidate!")
