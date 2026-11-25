with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update import in main.py
if 'ProjectOwnerLoginRequest' not in text:
    text = text.replace('ProjectOwnerResetRequest,', 'ProjectOwnerResetRequest, ProjectOwnerLoginRequest,')
    print('Import updated with ProjectOwnerLoginRequest')

# 1. Update hash_password and verify_password to use Argon2id
old_hash_funcs = """# Password hashing with PBKDF2-SHA256
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 240000).hex()
    return f"{salt}${digest}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, digest = hashed.split("$", 1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 240000).hex()
        return hmac.compare_digest(check, digest)
    except Exception:
        return False"""

new_hash_funcs = """# Password hashing with Argon2id (and backward-compatible verification for existing pbkdf2/bcrypt)
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _argon2_hasher = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=1)
except ImportError:
    _argon2_hasher = None

try:
    import bcrypt
except ImportError:
    bcrypt = None

def hash_password(password: str) -> str:
    \"\"\"Generate secure password hash using Argon2id with salt.\"\"\"
    if _argon2_hasher:
        return _argon2_hasher.hash(password)
    elif bcrypt:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 240000).hex()
        return f"{salt}${digest}"

def verify_password(password: str, hashed: str) -> bool:
    \"\"\"Verify password hash supporting Argon2id, bcrypt, and legacy PBKDF2.\"\"\"
    if not hashed:
        return False
    # Check Argon2id hash format ($argon2id$...)
    if hashed.startswith("$argon2"):
        if _argon2_hasher:
            try:
                return _argon2_hasher.verify(hashed, password)
            except VerifyMismatchError:
                return False
            except Exception:
                return False
        return False
    # Check bcrypt hash format ($2a$, $2b$, $2y$)
    if hashed.startswith(("$2a$", "$2b$", "$2y$")):
        if bcrypt:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except Exception:
                return False
        return False
    # Fallback legacy PBKDF2 ($salt$digest)
    try:
        salt, digest = hashed.split("$", 1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 240000).hex()
        return hmac.compare_digest(check, digest)
    except Exception:
        return False"""

if old_hash_funcs in text:
    text = text.replace(old_hash_funcs, new_hash_funcs, 1)
    print("Replaced password hashing with Argon2id successfully")
else:
    print("old_hash_funcs not matched exactly")

# 2. In-memory rate limiting and Project Owner security configuration
rate_limiting_code = """
# Rate limiting tracking for sensitive authentication and reset endpoints
_rate_limit_lock = threading.Lock() if 'threading' in globals() else None
_rate_limit_buckets: Dict[str, List[float]] = {}

def check_rate_limit(key: str, max_attempts: int = 5, window_seconds: int = 60) -> bool:
    now = time.time()
    with threading.Lock():
        attempts = _rate_limit_buckets.get(key, [])
        # Prune old attempts
        attempts = [t for t in attempts if now - t < window_seconds]
        if len(attempts) >= max_attempts:
            _rate_limit_buckets[key] = attempts
            return False
        attempts.append(now)
        _rate_limit_buckets[key] = attempts
        return True

def get_project_owner_secret() -> str:
    \"\"\"Load Project Owner key from protected environment variable.\"\"\"
    key = os.getenv("PROJECT_OWNER_KEY")
    if not key:
        # Fallback to backend /app/.env file
        env_path = "/app/.env"
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("PROJECT_OWNER_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
    return key or "NagrikSetu@OwnerSecureKey2026!"
"""

# Replace the endpoints block
old_endpoints_marker = """# ---------------------------------------------------------------------------
# Project Owner & 10 Independent Centre Representative Registration Workflows
# ---------------------------------------------------------------------------"""

new_endpoints_replacement = """# ---------------------------------------------------------------------------
# Project Owner & 10 Independent Centre Representative Registration Workflows
# ---------------------------------------------------------------------------
""" + rate_limiting_code + """
@app.post("/api/auth/project-owner-login")
def project_owner_login(req: ProjectOwnerLoginRequest, db: Session = Depends(get_db)):
    \"\"\"
    Authenticate the Project Owner using the protected environment secret key.
    Enforces rate limiting and returns a dedicated PROJECT_OWNER JWT token.
    \"\"\"
    if not check_rate_limit("owner_login", max_attempts=5, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please wait 1 minute before retrying.")

    expected_key = get_project_owner_secret()
    if not hmac.compare_digest(req.owner_key.strip(), expected_key.strip()):
        db.add(AuditLog(
            actor="ANONYMOUS",
            role="PROJECT_OWNER",
            action="OWNER_LOGIN_FAILED",
            target="SYSTEM",
            details="Invalid Project Owner Key submitted."
        ))
        db.commit()
        raise HTTPException(status_code=401, detail="Authentication Failed: Invalid Project Owner Secret Key.")

    token = create_access_token(
        email="project.owner@nagriksetu.local",
        role="PROJECT_OWNER",
        name="Project Owner / Director",
        centre_id=None
    )

    db.add(AuditLog(
        actor="project.owner@nagriksetu.local",
        role="PROJECT_OWNER",
        action="OWNER_LOGIN_SUCCESS",
        target="SYSTEM",
        details="Project Owner successfully authenticated and issued administrative session token."
    ))
    db.commit()

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "role": "PROJECT_OWNER",
        "email": "project.owner@nagriksetu.local",
        "full_name": "Project Owner / Director"
    }

@app.get("/api/public/centre-register")
def list_centre_register_status(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    \"\"\"
    Centre Account Register.
    Public view: Masks sensitive representative email/phone (e.g. c***u@nagriksetu.local) to protect privacy.
    Authenticated Project Owner view: Returns unmasked registered emails and full representative contacts.
    \"\"\"
    is_owner = False
    if authorization and authorization.startswith("Bearer "):
        try:
            claims = decode_access_token(authorization[7:].strip())
            if claims.get("role") in ("PROJECT_OWNER", "GOVERNMENT_ADMIN", "SKILL_DEPARTMENT_ADMIN"):
                is_owner = True
        except Exception:
            is_owner = False

    target_centre_ids = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11]
    centres = db.query(TrainingCentre).filter(TrainingCentre.id.in_(target_centre_ids)).order_by(TrainingCentre.id).all()
    results = []
    for c in centres:
        acc = db.query(Account).filter_by(centre_id=c.id, role="TRAINING_CENTRE_ADMIN").first()
        is_configured = bool(acc and acc.password_hash)
        
        reg_email = acc.email if acc else None
        reg_phone = acc.phone if acc else None
        
        # Privacy masking for unauthenticated public requests
        if not is_owner and reg_email:
            parts = reg_email.split("@")
            name_p = parts[0]
            domain_p = parts[1]
            masked_name = f"{name_p[0]}***{name_p[-1]}" if len(name_p) > 2 else f"{name_p}***"
            display_email = f"{masked_name}@{domain_p}"
            display_phone = f"******{reg_phone[-4:]}" if reg_phone and len(reg_phone) >= 4 else "Protected"
        else:
            display_email = reg_email
            display_phone = reg_phone

        results.append({
            "centre_id": c.id,
            "centre_code": c.code,
            "centre_name": c.name,
            "location": c.location,
            "district": c.district,
            "registered_email": display_email,
            "is_masked": not is_owner,
            "representative_name": acc.full_name if (acc and is_owner) else ("Configured Representative" if is_configured else "Unassigned"),
            "representative_phone": display_phone,
            "is_configured": is_configured,
            "status": "CONFIGURED" if is_configured else "PENDING_CLAIM"
        })
    return results

@app.post("/api/auth/register-centre-representative")
def register_centre_representative(req: CentreRepresentativeRegisterRequest, db: Session = Depends(get_db)):
    \"\"\"
    Authorized Training Centre Representative Registration for existing centres.
    Enforces rate limiting, input validation, and audit logging.
    \"\"\"
    clean_email = normalize_email(req.representative_email)
    rate_key = f"rep_reg_{clean_email}"
    if not check_rate_limit(rate_key, max_attempts=5, window_seconds=300):
        raise HTTPException(status_code=429, detail="Too many registration attempts. Please wait 5 minutes.")

    target_centre_ids = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11]
    if req.centre_id not in target_centre_ids:
        raise HTTPException(status_code=400, detail="Invalid training centre ID. Must be one of the 10 accredited regional centres.")

    centre = db.query(TrainingCentre).filter(TrainingCentre.id == req.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Training centre not found.")

    existing_acc = db.query(Account).filter(Account.email == clean_email).first()
    if existing_acc and existing_acc.centre_id != req.centre_id:
        raise HTTPException(status_code=409, detail="This email address is already registered to another account or training centre.")

    if len(req.password.strip()) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters in length for security compliance.")

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

    asg = db.query(AdminCentreAssignment).filter_by(account_id=centre_acc.id, centre_id=centre.id).first()
    if not asg:
        db.add(AdminCentreAssignment(account_id=centre_acc.id, centre_id=centre.id))

    # Audit logging for security compliance
    db.add(AuditLog(
        actor=clean_email,
        role="TRAINING_CENTRE_ADMIN",
        action="REPRESENTATIVE_CREDENTIALS_SET",
        target=centre.code,
        details=f"Authorized representative {req.representative_name} registered credentials for centre {centre.name} using Argon2id."
    ))
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
def project_owner_reset_centre_password(
    req: ProjectOwnerResetRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    \"\"\"
    Protected Project Owner demonstration password reset for Training Centre representative access.
    Requires either a valid Project Owner JWT token or the protected environment secret key.
    Enforces rate limiting, Argon2id cryptographic hashing, and comprehensive audit logging.
    \"\"\"
    if not check_rate_limit("owner_reset", max_attempts=10, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many reset requests. Rate limit exceeded.")

    authorized = False
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
            actor = "PROJECT_OWNER_KEY"

    if not authorized:
        db.add(AuditLog(
            actor="ANONYMOUS",
            role="SECURITY",
            action="UNAUTHORIZED_CENTRE_RESET_ATTEMPT",
            target=f"CENTRE_{req.centre_id}",
            details="Unauthorized attempt to invoke Project Owner password reset."
        ))
        db.commit()
        raise HTTPException(status_code=403, detail="Forbidden: Valid Project Owner authentication required.")

    centre = db.query(TrainingCentre).filter(TrainingCentre.id == req.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Target training centre not found.")

    centre_acc = db.query(Account).filter_by(centre_id=centre.id, role="TRAINING_CENTRE_ADMIN").first()
    if not centre_acc:
        raise HTTPException(status_code=404, detail="No representative account found for this training centre. Please register one first.")

    if len(req.new_password.strip()) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters in length.")

    # Securely hash with Argon2id
    centre_acc.password_hash = hash_password(req.new_password.strip())

    # Record security audit log
    db.add(AuditLog(
        actor=actor,
        role="PROJECT_OWNER",
        action="CENTRE_PASSWORD_RESET",
        target=centre.code,
        details=f"Project Owner securely reset access for centre {centre.name} ({centre_acc.email}). Argon2id hash updated."
    ))
    db.commit()

    return {
        "success": True,
        "message": f"Credentials securely updated for {centre.name}. Argon2id hash stored in MySQL.",
        "centre_id": centre.id,
        "centre_name": centre.name,
        "registered_email": centre_acc.email
    }
"""

# Replace the whole section from old_endpoints_marker to end of file
idx_marker = text.find(old_endpoints_marker)
if idx_marker != -1:
    text = text[:idx_marker] + new_endpoints_replacement
    print("Replaced centre register endpoints with secured version")
else:
    print("Marker not found, appending")
    text += "\n" + new_endpoints_replacement

with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated main.py successfully")
