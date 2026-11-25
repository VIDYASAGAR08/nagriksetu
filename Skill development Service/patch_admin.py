import os

file_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

target = '''@app.post("/api/admin/centres/{centre_id}/assign-admin")
def assign_centre_admin(
    centre_id: int,
    req: CreateCentreAdminRequest,
    admin: Account = Depends(require_government_admin),
    db: Session = Depends(get_db)
):
    """Securely create or assign a Training Centre Administrator to an approved centre."""'''

replacement = '''@app.post("/api/admin/centres/{centre_id}/assign-admin")
def assign_centre_admin(
    centre_id: int,
    req: CreateCentreAdminRequest,
    admin: Account = Depends(require_government_admin),
    db: Session = Depends(get_db)
):
    """Securely create or assign a Training Centre Administrator to an approved centre."""
    raise HTTPException(
        status_code=403,
        detail="Forbidden: Platform Admin is strictly read-only and cannot create centre accounts or assign credentials. Authorised centre representatives must independently register."
    )'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("PATCH_SUCCESS")
else:
    print("TARGET_NOT_FOUND")
