import sys
import os

MAIN_PY = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(MAIN_PY, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update ParentRegisterRequest and RegisterResponse
old_parent_req = """class ParentRegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: Optional[str] = Field(default=None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    phone: str = Field(pattern=r"^[6-9]\d{9}$")
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Full name must contain at least 2 non-whitespace characters.")
        return s

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            s = v.strip().lower()
            return s if s else None
        return v


class RegisterResponse(BaseModel):
    user_id: str
    full_name: str
    message: str"""

new_parent_req = """class ParentRegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Full name must contain at least 2 non-whitespace characters.")
        return s

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            s = v.strip().lower()
            if not s:
                return None
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", s):
                raise ValueError("Please provide a valid email format.")
            return s
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return None
            digits = re.sub(r"\D", "", s)
            if len(digits) == 12 and digits.startswith("91"):
                digits = digits[2:]
            elif len(digits) == 11 and digits.startswith("0"):
                digits = digits[1:]
            if not re.match(r"^[6-9]\d{9}$", digits):
                raise ValueError("Please provide a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
            return digits
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must contain at least 8 characters.")
        has_letter = any(c.isalpha() for c in v)
        has_num_or_special = any(not c.isalpha() for c in v)
        if not has_letter or not has_num_or_special:
            raise ValueError("Password must contain at least one letter and at least one number or special character.")
        return v


class RegisterResponse(BaseModel):
    user_id: str
    full_name: str
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    role: Optional[str] = "parent"


class SetupPasswordPayload(BaseModel):
    identifier: str = Field(min_length=3, max_length=150)
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must contain at least 8 characters.")
        has_letter = any(c.isalpha() for c in v)
        has_num_or_special = any(not c.isalpha() for c in v)
        if not has_letter or not has_num_or_special:
            raise ValueError("Password must contain at least one letter and at least one number or special character.")
        return v"""

if old_parent_req in content:
    content = content.replace(old_parent_req, new_parent_req, 1)
    print("Replaced ParentRegisterRequest and RegisterResponse successfully")
else:
    print("Could not find old_parent_req")
    sys.exit(1)

# 2. Update login endpoint to check for missing password
old_login_verify = """        if (
            user is None
            or not user["is_active"]
            or user["status"] == "suspended"
            or not verify_password(form.password, user["password_hash"])
        ):
            auth_limiter.record_failed_login(client_ip, identifier, max_failures=5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user["is_email_verified"] == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email address is not verified. Please complete email verification before logging in."
            )"""

new_login_verify = """        if user is None:
            auth_limiter.record_failed_login(client_ip, identifier, max_failures=5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated or suspended. Please contact your administrator.",
            )

        # Check if user has no password configured yet
        if not user["password_hash"] or user["password_hash"].strip() == "":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account does not have a password configured yet. Please use 'Set Up Password' or 'Forgot Password' to set your password.",
            )

        if not verify_password(form.password, user["password_hash"]):
            auth_limiter.record_failed_login(client_ip, identifier, max_failures=5)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )"""

if old_login_verify in content:
    content = content.replace(old_login_verify, new_login_verify, 1)
    print("Replaced login verify check successfully")
else:
    print("Could not find old_login_verify")
    sys.exit(1)

# 3. Update register_parent
old_register_parent_body = """@app.post("/auth/register", response_model=RegisterResponse, status_code=201)
def register_parent(payload: ParentRegisterRequest):
    \"\"\"
    Public parent registration.
    Always creates role='parent'. The role field is never accepted from the request body.
    \"\"\"
    # --- Input validation and normalization ---
    full_name = payload.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name must contain at least 2 non-whitespace characters.",
        )

    phone = payload.phone.strip()
    email = payload.email.strip().lower() if payload.email and payload.email.strip() else None

    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match.",
        )

    conn = get_connection()
    try:
        # --- Duplicate check (exact phone, case-insensitive email) ---
        existing = conn.execute(
            "SELECT user_id FROM users WHERE phone = ?",
            (phone,),
        ).fetchone()

        if existing is None and email:
            existing = conn.execute(
                "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
                (email,),
            ).fetchone()

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with these details already exists.",
            )

        # --- Hash password ---
        password_hash = hash_password(payload.password)

        # --- Atomic transaction ---
        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())

        try:
            with conn:
                conn.execute(
                    \"\"\"
                    INSERT INTO users (
                        user_id, email, phone, password_hash,
                        role, school_id, is_active, full_name
                    )
                    VALUES (?, ?, ?, ?, 'parent', NULL, 1, ?)
                    \"\"\",
                    (user_id, email, phone, password_hash, full_name),
                )

                conn.execute(
                    \"\"\"
                    INSERT INTO guardians (
                        guardian_id, user_id, full_name, relationship,
                        phone, email
                    )
                    VALUES (?, ?, ?, 'Parent', ?, ?)
                    \"\"\",
                    (guardian_id, user_id, full_name, phone, email),
                )

                conn.execute(
                    \"\"\"
                    INSERT INTO audit_logs (
                        audit_id, actor_user_id, actor_role,
                        action, entity_type, entity_id,
                        school_id, ip_address, metadata_json
                    )
                    VALUES (?, ?, 'parent', 'PARENT_REGISTERED', 'user', ?, NULL, NULL, ?)
                    \"\"\",
                    (
                        audit_id,
                        user_id,
                        user_id,
                        json.dumps({"full_name": full_name}),
                    ),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with these details already exists.",
            )

        return {
            "user_id": user_id,
            "full_name": full_name,
            "message": "Registration successful. You can now log in.",
        }
    finally:
        conn.close()"""

new_register_parent_body = """@app.post("/auth/register", response_model=RegisterResponse, status_code=201)
def register_parent(payload: ParentRegisterRequest):
    \"\"\"
    Public citizen/parent registration using password.
    Always creates role='parent'.
    At least one of email or mobile number must be provided.
    \"\"\"
    full_name = payload.full_name.strip()
    phone = payload.phone
    email = payload.email

    if not phone and not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please provide at least one contact method: an email address or a mobile number.",
        )

    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match.",
        )

    conn = get_connection()
    try:
        # Check duplicate mobile number
        if phone:
            existing_phone = conn.execute(
                "SELECT user_id FROM users WHERE phone = ?",
                (phone,),
            ).fetchone()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this mobile number already exists.",
                )

        # Check duplicate email address
        if email:
            existing_email = conn.execute(
                "SELECT user_id FROM users WHERE email = ? COLLATE NOCASE",
                (email,),
            ).fetchone()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email address already exists.",
                )

        # Hash password using Argon2id
        pwd_hash = hash_password(payload.password)

        user_id = str(uuid.uuid4())
        guardian_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())

        try:
            with conn:
                conn.execute(
                    \"\"\"
                    INSERT INTO users (
                        user_id, email, phone, password_hash,
                        role, school_id, is_active, full_name, is_email_verified
                    )
                    VALUES (?, ?, ?, ?, 'parent', NULL, 1, ?, 1)
                    \"\"\",
                    (user_id, email, phone, pwd_hash, full_name),
                )

                guardian_phone = phone if phone else ""
                guardian_email = email if email else ""
                conn.execute(
                    \"\"\"
                    INSERT INTO guardians (
                        guardian_id, user_id, full_name, relationship,
                        phone, email
                    )
                    VALUES (?, ?, ?, 'Parent', ?, ?)
                    \"\"\",
                    (guardian_id, user_id, full_name, guardian_phone, guardian_email),
                )

                conn.execute(
                    \"\"\"
                    INSERT INTO audit_logs (
                        audit_id, actor_user_id, actor_role,
                        action, entity_type, entity_id,
                        school_id, ip_address, metadata_json
                    )
                    VALUES (?, ?, 'parent', 'PARENT_REGISTERED', 'user', ?, NULL, NULL, ?)
                    \"\"\",
                    (
                        audit_id,
                        user_id,
                        user_id,
                        json.dumps({"full_name": full_name, "has_email": bool(email), "has_phone": bool(phone)}),
                    ),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with these details already exists.",
            )

        user_dict = {
            "user_id": user_id,
            "role": "parent",
            "school_id": None,
            "student_id": None,
            "permanent_student_id": None,
        }
        token = create_access_token(user_dict)

        return {
            "user_id": user_id,
            "full_name": full_name,
            "message": "Registration successful. You can now log in.",
            "access_token": token,
            "token_type": "bearer",
            "role": "parent",
        }
    finally:
        conn.close()


@app.post("/auth/setup-password")
def setup_password(payload: SetupPasswordPayload):
    \"\"\"
    Secure self-service password setup for existing accounts that do not yet have a password.
    Requires matching registered identifier and official full name.
    \"\"\"
    identifier = payload.identifier.strip()
    full_name = payload.full_name.strip()

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=422, detail="Passwords do not match.")

    conn = get_connection()
    try:
        user = conn.execute(
            \"\"\"
            SELECT user_id, email, phone, full_name, password_hash, is_active, status
            FROM users
            WHERE email = ? COLLATE NOCASE OR phone = ?
            \"\"\",
            (identifier, identifier)
        ).fetchone()

        if not user or not user["is_active"] or user["status"] == "suspended":
            raise HTTPException(
                status_code=404,
                detail="No eligible active account found with the provided identifier."
            )

        if user["password_hash"] and user["password_hash"].strip() != "":
            raise HTTPException(
                status_code=400,
                detail="This account already has a password configured. Please sign in or use the Forgot Password link."
            )

        # Verify identity: check full_name against user or guardian
        user_name = (user["full_name"] or "").strip().lower()
        guardian = conn.execute(
            "SELECT full_name FROM guardians WHERE user_id = ?",
            (user["user_id"],)
        ).fetchone()
        guardian_name = (guardian["full_name"] or "").strip().lower() if guardian else ""

        input_name = full_name.lower()
        name_matched = False
        if input_name == user_name or input_name == guardian_name:
            name_matched = True
        elif user_name and (input_name in user_name or user_name in input_name):
            name_matched = True
        elif guardian_name and (input_name in guardian_name or guardian_name in input_name):
            name_matched = True

        if not name_matched:
            raise HTTPException(
                status_code=403,
                detail="The provided full name does not match the official account record. For security, identity verification requires matching registration details."
            )

        new_hash = hash_password(payload.password)
        with conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, is_email_verified = 1 WHERE user_id = ?",
                (new_hash, user["user_id"])
            )
            record_platform_audit(
                conn,
                event_type="PASSWORD_SETUP",
                event_category="SECURITY",
                institution_id=None,
                actor_user_id=user["user_id"],
                actor_role="parent",
                entity_type="user",
                entity_id=user["user_id"],
                action="INITIAL_PASSWORD_CONFIGURED",
                remarks=f"Initial password configured via self-service for account {user['user_id']}"
            )

        return {
            "status": "ok",
            "message": "Password configured successfully. You may now sign in with your credentials."
        }
    finally:
        conn.close()"""

if old_register_parent_body in content:
    content = content.replace(old_register_parent_body, new_register_parent_body, 1)
    print("Replaced register_parent and added setup-password successfully")
else:
    print("Could not find old_register_parent_body")
    sys.exit(1)

# 4. Update forgot_password to handle mobile-only accounts gracefully
old_forgot_pwd = """@app.post("/auth/forgot-password")
def forgot_password(payload: ForgotPasswordPayload):
    identifier = payload.identifier.strip()
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, email FROM users WHERE (email = ? COLLATE NOCASE OR phone = ?) AND is_active = 1 AND status != 'suspended'",
            (identifier, identifier)
        ).fetchone()

        if user and user["email"]:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            reset_id = str(uuid.uuid4())

            conn.execute(\"\"\"
                INSERT INTO password_reset_tokens (reset_id, token_hash, user_id, expires_at, is_used)
                VALUES (?, ?, ?, ?, 0)
            \"\"\", (reset_id, token_hash, user["user_id"], expires_at))
            conn.commit()

            frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_base}/#/reset-password?token={raw_token}"
            try:
                from email_service import send_password_reset_email
                send_password_reset_email(user["email"], reset_url)
            except Exception as e:
                import logging
                logging.getLogger("nagriksetu.email").error(f"Password reset email dispatch failure: {e}")

        return {
            "status": "ok",
            "message": "If an active account exists with the provided details, password reset instructions have been dispatched to your registered email address."
        }
    finally:
        conn.close()"""

new_forgot_pwd = """@app.post("/auth/forgot-password")
def forgot_password(payload: ForgotPasswordPayload):
    identifier = payload.identifier.strip()
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, email, phone FROM users WHERE (email = ? COLLATE NOCASE OR phone = ?) AND is_active = 1 AND status != 'suspended'",
            (identifier, identifier)
        ).fetchone()

        if user and user["email"]:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            reset_id = str(uuid.uuid4())

            conn.execute(\"\"\"
                INSERT INTO password_reset_tokens (reset_id, token_hash, user_id, expires_at, is_used)
                VALUES (?, ?, ?, ?, 0)
            \"\"\", (reset_id, token_hash, user["user_id"], expires_at))
            conn.commit()

            frontend_base = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_base}/#/reset-password?token={raw_token}"
            try:
                from email_service import send_password_reset_email
                send_password_reset_email(user["email"], reset_url)
            except Exception as e:
                import logging
                logging.getLogger("nagriksetu.email").error(f"Password reset email dispatch failure: {e}")

            is_dev = os.getenv("APP_ENV", "development").lower() in ("dev", "development", "local")
            res = {
                "status": "ok",
                "message": "If an active account exists with the provided details, password reset instructions have been dispatched to your registered email address."
            }
            if is_dev:
                res["reset_token"] = raw_token
            return res

        elif user and not user["email"]:
            return {
                "status": "mobile_only",
                "message": "This account is registered with a mobile number only. Automated online password reset is currently available only for email accounts. For security, please contact your School Administrator or the NagrikSetu Institution Helpdesk to verify your identity and assist with password recovery."
            }

        return {
            "status": "ok",
            "message": "If an active account exists with the provided details, password reset instructions have been dispatched to your registered email address."
        }
    finally:
        conn.close()"""

if old_forgot_pwd in content:
    content = content.replace(old_forgot_pwd, new_forgot_pwd, 1)
    print("Replaced forgot_password successfully")
else:
    print("Could not find old_forgot_pwd")
    sys.exit(1)

with open(MAIN_PY, "w", encoding="utf-8") as f:
    f.write(content)

print("ALL BACKEND MAIN.PY UPDATES APPLIED SUCCESSFULLY!")
