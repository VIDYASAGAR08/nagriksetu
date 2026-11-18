file_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """        else:
            # Create user in invited status
            user_id = str(uuid.uuid4())
            dummy_hash = hash_password(secrets.token_urlsafe(16) + "A1!")
            conn.execute(\"\"\"
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'invited', ?)
            \"\"\", (user_id, email_clean, payload.phone, dummy_hash, payload.role_id, inst_id, full_name_clean))"""

replacement = """        else:
            # Create user in invited status
            user_id = str(uuid.uuid4())
            dummy_hash = hash_password(secrets.token_urlsafe(16) + "A1!")
            phone_val = payload.phone
            if phone_val:
                p_dup = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone_val,)).fetchone()
                if p_dup:
                    phone_val = None
            conn.execute(\"\"\"
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'invited', ?)
            \"\"\", (user_id, email_clean, phone_val, dummy_hash, payload.role_id, inst_id, full_name_clean))"""

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Updated invite_institution_admin phone handling in main.py!")
