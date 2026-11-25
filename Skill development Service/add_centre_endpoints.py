with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update import in main.py
if 'CentreRepresentativeRegisterRequest' not in text:
    text = text.replace('CentreRegistrationRequest,', 'CentreRegistrationRequest, CentreRepresentativeRegisterRequest, ProjectOwnerResetRequest,')
    print('Import updated')

new_endpoints = """
# ---------------------------------------------------------------------------
# Project Owner & 10 Independent Centre Representative Registration Workflows
# ---------------------------------------------------------------------------
@app.get("/api/public/centre-register")
def list_centre_register_status(db: Session = Depends(get_db)):
    \"\"\"
    Project Owner Centre Account Register.
    Lists the 10 accredited centres, their representative account emails, and setup status.
    Never exposes passwords or sensitive auth tokens.
    \"\"\"
    target_centre_ids = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11]
    centres = db.query(TrainingCentre).filter(TrainingCentre.id.in_(target_centre_ids)).order_by(TrainingCentre.id).all()
    results = []
    for c in centres:
        acc = db.query(Account).filter_by(centre_id=c.id, role="TRAINING_CENTRE_ADMIN").first()
        is_configured = bool(acc and acc.password_hash)
        results.append({
            "centre_id": c.id,
            "centre_code": c.code,
            "centre_name": c.name,
            "location": c.location,
            "district": c.district,
            "registered_email": acc.email if acc else None,
            "representative_name": acc.full_name if acc else None,
            "representative_phone": acc.phone if acc else None,
            "is_configured": is_configured,
            "status": "CONFIGURED" if is_configured else "PENDING_CLAIM"
        })
    return results

@app.post("/api/auth/register-centre-representative")
def register_centre_representative(req: CentreRepresentativeRegisterRequest, db: Session = Depends(get_db)):
    \"\"\"
    Authorized Training Centre Representative Registration for existing centres.
    Allows the representative of an authorized centre to register their unique email and password.
    Reuses the existing centre record and prevents claiming unauthorized/other centres.
    \"\"\"
    target_centre_ids = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11]
    if req.centre_id not in target_centre_ids:
        raise HTTPException(status_code=400, detail="Invalid training centre ID. Must be one of the 10 accredited regional centres.")

    centre = db.query(TrainingCentre).filter(TrainingCentre.id == req.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Training centre not found.")

    clean_email = normalize_email(req.representative_email)
    existing_acc = db.query(Account).filter(Account.email == clean_email).first()
    if existing_acc and existing_acc.centre_id != req.centre_id:
        raise HTTPException(status_code=409, detail="This email address is already registered to another account or training centre.")

    if len(req.password.strip()) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters in length.")

    # Check if this centre already has an account, update credentials or create new representative account
    centre_acc = db.query(Account).filter_by(centre_id=centre.id, role="TRAINING_CENTRE_ADMIN").first()
    pw_hash = hash_password(req.password.strip())

    if centre_acc:
        centre_acc.email = clean_email
        centre_acc.password_hash = pw_hash
        centre_acc.full_name = req.representative_name.strip()
        centre_acc.phone = req.representative_phone.strip()
        centre_acc.active = True
    else:
        centre_acc = Account(
            email=clean_email,
            password_hash=pw_hash,
            role="TRAINING_CENTRE_ADMIN",
            full_name=req.representative_name.strip(),
            phone=req.representative_phone.strip(),
            centre_id=centre.id,
            active=True
        )
        db.add(centre_acc)
        db.flush()

    # Ensure AdminCentreAssignment
    asg = db.query(AdminCentreAssignment).filter_by(account_id=centre_acc.id, centre_id=centre.id).first()
    if not asg:
        db.add(AdminCentreAssignment(account_id=centre_acc.id, centre_id=centre.id))

    db.commit()

    token = create_access_token(
        email=centre_acc.email,
        role="TRAINING_CENTRE_ADMIN",
        name=centre_acc.full_name,
        centre_id=centre.id
    )

    return {
        "success": True,
        "message": f"Representative account successfully established for {centre.name}.",
        "access_token": token,
        "token_type": "bearer",
        "role": "TRAINING_CENTRE_ADMIN",
        "centre_id": centre.id,
        "email": centre_acc.email,
        "full_name": centre_acc.full_name
    }

@app.post("/api/auth/project-owner-reset-centre-password")
def project_owner_reset_centre_password(req: ProjectOwnerResetRequest, db: Session = Depends(get_db)):
    \"\"\"
    Secure Project Owner demonstration reset for Training Centre representative access.
    Validates the project secret key and securely updates the password hash in MySQL.
    Never exposes or returns plaintext passwords.
    \"\"\"
    EXPECTED_SECRET = "NagrikSetu@Owner2026!"
    if req.secret_key.strip() != EXPECTED_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid Project Owner Demonstration Key.")

    centre = db.query(TrainingCentre).filter(TrainingCentre.id == req.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Target training centre not found.")

    centre_acc = db.query(Account).filter_by(centre_id=centre.id, role="TRAINING_CENTRE_ADMIN").first()
    if not centre_acc:
        raise HTTPException(status_code=404, detail="No representative account found for this training centre. Please register one first.")

    if len(req.new_password.strip()) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters in length.")

    centre_acc.password_hash = hash_password(req.new_password.strip())
    db.commit()

    return {
        "success": True,
        "message": f"Credentials securely updated for {centre.name} ({centre_acc.email}). No plaintext passwords stored.",
        "centre_id": centre.id,
        "centre_name": centre.name,
        "registered_email": centre_acc.email
    }
"""

if '/api/public/centre-register' not in text:
    text += new_endpoints
    with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESS: Added backend endpoints in main.py')
else:
    print('Endpoints already in main.py')
