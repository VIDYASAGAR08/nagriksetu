import re

file_path = "C:/Users/callm/nagriksetu/backend/main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports at top
if "from datetime import datetime, timedelta" not in content[:300]:
    content = "import secrets\nfrom datetime import datetime, timedelta\nimport hashlib\n" + content[content.find("import ocr_service"):]
    print("Added datetime and hashlib imports to top")

# 2. Add institution_id check to list_school_admission_applications for 403 enforcement
old_func_start = """@app.get("/school/admissions/applications")
def list_school_admission_applications(
    status_filter: Optional[str] = Query(default="all"),
    education_level: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    Lists admission applications for the assigned institution with filtering and pagination.
    \"\"\"
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Staff account is not assigned to an institution.")"""

new_func_start = """@app.get("/school/admissions/applications")
def list_school_admission_applications(
    status_filter: Optional[str] = Query(default="all"),
    education_level: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    institution_id: Optional[str] = Query(default=None),
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    Lists admission applications for the assigned institution with filtering and pagination.
    \"\"\"
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Staff account is not assigned to an institution.")
    if institution_id and institution_id != school_id and user.get("role") != "platform_admin":
        raise HTTPException(403, f"Cross-institution access forbidden: Account is assigned to {school_id}, cannot access {institution_id}.")"""

if old_func_start in content:
    content = content.replace(old_func_start, new_func_start, 1)
    print("Added institution_id isolation check to list_school_admission_applications")
else:
    print("Could not match old_func_start!")

# 3. Add cross-institution check to detail endpoint
old_detail_start = """@app.get("/school/admissions/applications/{application_id}")
def get_school_admission_application_detail(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    Retrieves full Stage 1 application detail for authorized institutional reviewers.
    \"\"\"
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        row = conn.execute(
            \"\"\"
            SELECT a.*, s.school_name, p.program_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ? AND a.institution_id = ?
            \"\"\",
            (application_id, school_id)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Admission application not found or unauthorized.")"""

new_detail_start = """@app.get("/school/admissions/applications/{application_id}")
def get_school_admission_application_detail(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    Retrieves full Stage 1 application detail for authorized institutional reviewers.
    \"\"\"
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        existing = conn.execute("SELECT institution_id FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        if not existing:
            raise HTTPException(404, "Admission application not found.")
        if existing["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {existing['institution_id']}, reviewer is at {school_id}.")
        row = conn.execute(
            \"\"\"
            SELECT a.*, s.school_name, p.program_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ? AND a.institution_id = ?
            \"\"\",
            (application_id, school_id)
        ).fetchone()"""

if old_detail_start in content:
    content = content.replace(old_detail_start, new_detail_start, 1)
    print("Added cross-institution check to detail endpoint")
else:
    print("Could not match old_detail_start!")

# 4. In invite_institution_admin, return invitation_token in response
old_invite_return = """        return {
            "status": "invited",
            "user_id": user_id,
            "email": email_clean,
            "institution_id": inst_id,
            "school_name": school["school_name"],
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "dev_token": raw_token,
            "email_delivery": "Simulated/Dev Mode: External SMTP unconfigured. Invitation link generated securely."
        }"""

new_invite_return = """        return {
            "status": "invited",
            "user_id": user_id,
            "email": email_clean,
            "institution_id": inst_id,
            "school_name": school["school_name"],
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "invitation_token": raw_token,
            "dev_token": raw_token,
            "email_delivery": "Simulated/Dev Mode: External SMTP unconfigured. Invitation link generated securely."
        }"""

if old_invite_return in content:
    content = content.replace(old_invite_return, new_invite_return, 1)
    print("Updated invite_institution_admin return dict")
else:
    print("Could not match old_invite_return!")

# 5. In invite_school_staff, return invitation_token in response
old_staff_invite_return = """        return {
            "status": "invited",
            "user_id": user_id,
            "school_id": school_id,
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "dev_token": raw_token
        }"""

new_staff_invite_return = """        return {
            "status": "invited",
            "user_id": user_id,
            "school_id": school_id,
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "invitation_token": raw_token,
            "dev_token": raw_token
        }"""

if old_staff_invite_return in content:
    content = content.replace(old_staff_invite_return, new_staff_invite_return, 1)
    print("Updated invite_school_staff return dict")
else:
    print("Could not match old_staff_invite_return!")

# 6. In forgot-password, return reset_token
old_forgot_return = """            return {
                "status": "ok",
                "message": "If an active account exists with the provided details, password reset instructions have been generated.",
                "dev_reset_url": f"/reset-password?token={raw_token}"
            }"""

new_forgot_return = """            return {
                "status": "ok",
                "message": "If an active account exists with the provided details, password reset instructions have been generated.",
                "reset_token": raw_token,
                "dev_reset_url": f"/reset-password?token={raw_token}"
            }"""

if old_forgot_return in content:
    content = content.replace(old_forgot_return, new_forgot_return, 1)
    print("Updated forgot_password return dict")
else:
    print("Could not match old_forgot_return!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to backend/main.py successfully!")
