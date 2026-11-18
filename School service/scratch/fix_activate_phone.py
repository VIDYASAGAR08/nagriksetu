file_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    else:
        user_id = str(uuid.uuid4())
        # Base role in users table must respect CHECK constraint: 'school_staff'
        conn.execute(\"\"\"
            INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
            VALUES (?, ?, ?, ?, 'school_staff', ?, 1, 'active', ?)
        \"\"\", (user_id, email_clean, phone, pwd_hash, inst_id, full_name))"""

replacement = """    else:
        user_id = str(uuid.uuid4())
        # Prevent unique phone collision
        if phone:
            p_dup = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone,)).fetchone()
            if p_dup:
                phone = None
        # Base role in users table must respect CHECK constraint: 'school_staff'
        conn.execute(\"\"\"
            INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
            VALUES (?, ?, ?, ?, 'school_staff', ?, 1, 'active', ?)
        \"\"\", (user_id, email_clean, phone, pwd_hash, inst_id, full_name))"""

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Updated activate_approved_candidate phone handling in main.py!")
