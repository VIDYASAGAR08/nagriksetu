with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        # Hash password with Argon2id
        try:
            pwd_hash = hash_password(payload.password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

        user_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO users (
                user_id, email, phone, password_hash, role,
                school_id, is_active, status, full_name,
                permanent_student_id, student_id, created_at
            ) VALUES (?, ?, ?, ?, 'student', ?, 1, 'active', ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                user_id,
                email_clean,
                payload.phone.strip() if payload.phone else None,
                pwd_hash,
                student["school_id"],
                clean_name,
                student["permanent_student_id"],
                student["student_id"],
            ),
        )'''

replacement = '''        # Check phone uniqueness if phone provided
        phone_clean = payload.phone.strip() if payload.phone and payload.phone.strip() else None
        if phone_clean:
            existing_phone = conn.execute(
                "SELECT user_id FROM users WHERE phone = ?",
                (phone_clean,),
            ).fetchone()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this phone number already exists. Please provide a different phone number or leave it blank.",
                )

        # Hash password with Argon2id
        try:
            pwd_hash = hash_password(payload.password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

        user_id = str(uuid.uuid4())
        try:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, phone, password_hash, role,
                    school_id, is_active, status, full_name,
                    permanent_student_id, student_id, created_at
                ) VALUES (?, ?, ?, ?, 'student', ?, 1, 'active', ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    user_id,
                    email_clean,
                    phone_clean,
                    pwd_hash,
                    student["school_id"],
                    clean_name,
                    student["permanent_student_id"],
                    student["student_id"],
                ),
            )
        except sqlite3.IntegrityError as ie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to register student account: constraint conflict ({str(ie)}).",
            )'''

# Normalize newlines
content_norm = content.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

assert target_norm in content_norm, 'Target not found!'
new_content = content_norm.replace(target_norm, replacement_norm, 1)
with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8', newline='') as f:
    f.write(new_content)
print('Successfully patched backend/main.py')
