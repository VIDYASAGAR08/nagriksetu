import re

file_path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        if exp_dt < now:
            conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The verification code has expired. Please request a new verification code.",
            )

        if code_row["attempts"] >= code_row["max_attempts"]:
            conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many failed attempts. This verification code has been invalidated. Please request a new code.",
            )

        hashed_input = hashlib.sha256(code_input.encode("utf-8")).hexdigest()
        is_match = (hashed_input == code_row["code_hash"])

        if not is_match:
            new_attempts = code_row["attempts"] + 1
            conn.execute(
                "UPDATE institution_linking_codes SET attempts = ? WHERE code_id = ?",
                (new_attempts, code_row["code_id"]),
            )
            rem = max(0, code_row["max_attempts"] - new_attempts)
            if rem == 0:
                conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code. Maximum attempts exceeded. Code has been invalidated.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification code. {rem} attempt(s) remaining.",
            )'''

replacement = '''        if exp_dt < now:
            conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
            conn.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The verification code has expired. Please request a new verification code.",
            )

        if code_row["attempts"] >= code_row["max_attempts"]:
            conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
            conn.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many failed attempts. This verification code has been invalidated. Please request a new code.",
            )

        hashed_input = hashlib.sha256(code_input.encode("utf-8")).hexdigest()
        is_match = (hashed_input == code_row["code_hash"])

        if not is_match:
            new_attempts = code_row["attempts"] + 1
            rem = max(0, code_row["max_attempts"] - new_attempts)
            if rem == 0:
                conn.execute(
                    "UPDATE institution_linking_codes SET attempts = ?, is_used = 1 WHERE code_id = ?",
                    (new_attempts, code_row["code_id"]),
                )
                conn.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code. Maximum attempts exceeded. Code has been invalidated.",
                )
            conn.execute(
                "UPDATE institution_linking_codes SET attempts = ? WHERE code_id = ?",
                (new_attempts, code_row["code_id"]),
            )
            conn.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification code. {rem} attempt(s) remaining.",
            )'''

assert target in text, "Target not found in main.py"
text = text.replace(target, replacement, 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Committed attempts tracking in backend/main.py successfully!")
