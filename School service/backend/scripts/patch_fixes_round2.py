import re

file_path = "C:/Users/callm/nagriksetu/backend/main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update InviteStaffPayload
old_invite_payload = """class InviteStaffPayload(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    role_id: Literal[
        "school_staff",
        "admissions_officer",
        "academic_admin",
        "student_records_officer"
    ] = "school_staff\""""

new_invite_payload = """class InviteStaffPayload(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    institution_id: Optional[str] = None
    role_id: str = "school_staff\""""

if old_invite_payload in content:
    content = content.replace(old_invite_payload, new_invite_payload, 1)
    print("Updated InviteStaffPayload model")
else:
    print("Could not match old_invite_payload!")

# 2. Update ResetPasswordPayload
old_reset_payload = """class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str"""

new_reset_payload = """class ResetPasswordPayload(BaseModel):
    token: str
    password: Optional[str] = None
    new_password: Optional[str] = None"""

if old_reset_payload in content:
    content = content.replace(old_reset_payload, new_reset_payload, 1)
    print("Updated ResetPasswordPayload model")
else:
    print("Could not match old_reset_payload!")

# 3. Update invite_school_staff validation
old_staff_func_start = """@app.post("/school/admin/staff/invite")
def invite_school_staff(
    payload: InviteStaffPayload,
    user: dict = Depends(require_school_admin)
):
    \"\"\"School Admin invites staff for their OWN school ONLY. Cross-school or platform admin forbidden.\"\"\"
    school_id = user["school_id"]
    email_clean = payload.email.strip().lower()
    full_name_clean = payload.full_name.strip()"""

new_staff_func_start = """@app.post("/school/admin/staff/invite")
def invite_school_staff(
    payload: InviteStaffPayload,
    user: dict = Depends(require_school_admin)
):
    \"\"\"School Admin invites staff for their OWN school ONLY. Cross-school or platform admin forbidden.\"\"\"
    school_id = user["school_id"]
    if payload.role_id == "platform_admin" or payload.role_id not in ("school_staff", "admissions_officer", "academic_admin", "student_records_officer", "school_admin"):
        raise HTTPException(403, "Forbidden: School administrators cannot create platform administrators or unauthorized roles.")
    if payload.institution_id and payload.institution_id != school_id:
        raise HTTPException(403, f"Cross-institution staff creation forbidden: Admin is at {school_id}, cannot invite for {payload.institution_id}.")

    email_clean = payload.email.strip().lower()
    full_name_clean = payload.full_name.strip()"""

if old_staff_func_start in content:
    content = content.replace(old_staff_func_start, new_staff_func_start, 1)
    print("Updated invite_school_staff function")
else:
    print("Could not match old_staff_func_start!")

# 4. Update reset_password function to use payload.new_password or payload.password
old_reset_func = """@app.post("/auth/reset-password")
def reset_password(payload: ResetPasswordPayload):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    if len(payload.new_password) < 12:
        raise HTTPException(422, "Password must contain at least 12 characters.")"""

new_reset_func = """@app.post("/auth/reset-password")
def reset_password(payload: ResetPasswordPayload):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    pwd = payload.new_password or payload.password
    if not pwd or len(pwd) < 12:
        raise HTTPException(422, "Password must contain at least 12 characters.")"""

if old_reset_func in content:
    content = content.replace(old_reset_func, new_reset_func, 1)
    print("Updated reset_password function header")
else:
    print("Could not match old_reset_func!")

# And replace payload.new_password in line 4955
old_hash_line = "new_hash = hash_password(payload.new_password)"
new_hash_line = "new_hash = hash_password(pwd)"
if old_hash_line in content:
    content = content.replace(old_hash_line, new_hash_line, 1)
    print("Updated new_hash line in reset_password")
else:
    print("Could not match old_hash_line!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied patches successfully!")
