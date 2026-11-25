import os

file_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

target = '''    authorized = False
    actor = "PROJECT_OWNER"
    
    # 1. Check Bearer token authorization
    if authorization and authorization.startswith("Bearer "):
        try:
            claims = decode_access_token(authorization[7:].strip())
            if claims.get("role") in ("PROJECT_OWNER", "GOVERNMENT_ADMIN"):
                authorized = True
                actor = claims.get("sub", "PROJECT_OWNER")
        except Exception:
            authorized = False

    # 2. Check secret key against protected environment variable
    if not authorized and req.secret_key:
        expected_secret = get_project_owner_secret()
        if hmac.compare_digest(req.secret_key.strip(), expected_secret.strip()):
            authorized = True
            actor = "PROJECT_OWNER_KEY"'''

replacement = '''    authorized = False
    actor = "PROJECT_OWNER"
    
    # Strictly require authenticated Bearer token (PROJECT_OWNER or GOVERNMENT_ADMIN)
    if authorization and authorization.startswith("Bearer "):
        try:
            claims = decode_access_token(authorization[7:].strip())
            if claims.get("role") in ("PROJECT_OWNER", "GOVERNMENT_ADMIN"):
                authorized = True
                actor = claims.get("sub", "PROJECT_OWNER")
        except Exception:
            authorized = False'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("MAIN_PY_AUTH_HARDENED")
else:
    print("TARGET_NOT_FOUND")
