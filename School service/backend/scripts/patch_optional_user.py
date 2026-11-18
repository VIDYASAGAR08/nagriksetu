main_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

func_def = """def get_optional_current_user(request: Request) -> Optional[dict]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    try:
        from auth import JWT_SECRET_KEY, JWT_ALGORITHM
        import jwt
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"require": ["sub", "exp", "iat", "jti"]})
        user_id = payload.get("sub")
        if not user_id:
            return None
        conn = get_connection()
        try:
            row = conn.execute("SELECT user_id, phone, email, full_name, role, school_id, is_active FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception:
        return None


"""

old_str_crlf = "def submit_stage1_admission_application(\r\n    payload: Stage1ApplicationCreate,\r\n    current_user: Optional[dict] = Depends(get_current_user),"
new_str_crlf = func_def + "def submit_stage1_admission_application(\r\n    payload: Stage1ApplicationCreate,\r\n    current_user: Optional[dict] = Depends(get_optional_current_user),"

old_str_lf = "def submit_stage1_admission_application(\n    payload: Stage1ApplicationCreate,\n    current_user: Optional[dict] = Depends(get_current_user),"
new_str_lf = func_def + "def submit_stage1_admission_application(\n    payload: Stage1ApplicationCreate,\n    current_user: Optional[dict] = Depends(get_optional_current_user),"

if old_str_crlf in content:
    content = content.replace(old_str_crlf, new_str_crlf, 1)
    print("Replaced CRLF version.")
elif old_str_lf in content:
    content = content.replace(old_str_lf, new_str_lf, 1)
    print("Replaced LF version.")
else:
    print("Target string not found!")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch complete.")
