file_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    conn.execute(\"\"\"
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_SUBMITTED', 'staff_application', ?, ?, 'candidate', ?, ?)
    \"\"\", (audit_id, row["application_id"], row["candidate_email"], row["institution_id"], json.dumps({"""

replacement = """    conn.execute(\"\"\"
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_SUBMITTED', 'staff_application', ?, NULL, 'candidate', ?, ?)
    \"\"\", (audit_id, row["application_id"], row["institution_id"], json.dumps({"""

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Fixed audit_logs in main.py!")
