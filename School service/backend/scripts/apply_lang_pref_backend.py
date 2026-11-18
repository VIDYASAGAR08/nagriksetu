MAIN_PATH = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(MAIN_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update get_admission_form_config language options
old_lang_block = """        # 5. Language options (from enrollments or institutional standards)
        lang_rows = conn.execute(
            "SELECT DISTINCT first_language FROM enrollments WHERE school_id = ? AND first_language IS NOT NULL",
            (institution_id,)
        ).fetchall()
        first_languages = [r[0] for r in lang_rows] if lang_rows else ["Kannada", "English"]
        second_languages = ["English", "Kannada", "Hindi", "Sanskrit"]"""

new_lang_block = """        # 5. Language options (from enrollments or institutional standards)
        if is_school:
            first_languages = ["Kannada", "Hindi", "Sanskrit"]
            second_languages = ["English"]
        else:
            lang_rows = conn.execute(
                "SELECT DISTINCT first_language FROM enrollments WHERE school_id = ? AND first_language IS NOT NULL",
                (institution_id,)
            ).fetchall()
            first_languages = [r[0] for r in lang_rows] if lang_rows else ["Kannada", "English"]
            second_languages = ["English", "Kannada", "Hindi", "Sanskrit"]"""

assert old_lang_block in content, "old_lang_block not found in main.py"
content = content.replace(old_lang_block, new_lang_block, 1)

# 2. Update submit_stage1_admission_application validation
old_val_block = """        if level == "school":
            if not payload.requested_standard or not (1 <= payload.requested_standard <= 10):
                raise HTTPException(400, "School admission requires a valid standard between 1 and 10.")
            if not payload.first_language_preference:
                payload.first_language_preference = "Kannada"
        elif level == "higher_secondary":"""

new_val_block = """        if level == "school":
            if not payload.requested_standard or not (1 <= payload.requested_standard <= 10):
                raise HTTPException(400, "School admission requires a valid standard between 1 and 10.")
            
            # School Language Validation: Accept only Kannada, Hindi, or Sanskrit
            first_lang = (payload.first_language_preference or "").strip()
            ALLOWED_SCHOOL_FIRST_LANGS = {"Kannada", "Hindi", "Sanskrit"}
            if first_lang not in ALLOWED_SCHOOL_FIRST_LANGS:
                raise HTTPException(
                    400,
                    f"Invalid first language preference '{first_lang}'. School admission accepts only: Kannada, Hindi, or Sanskrit."
                )
            payload.first_language_preference = first_lang

            # Automatically assign English as the second language (never trust frontend-submitted values)
            payload.second_language_preference = "English"
        elif level == "higher_secondary":"""

assert old_val_block in content, "old_val_block not found in main.py"
content = content.replace(old_val_block, new_val_block, 1)

with open(MAIN_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Successfully updated backend/main.py for final school language preference configuration!")
