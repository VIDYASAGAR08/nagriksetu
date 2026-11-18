"""
update_backend_institution_admins.py
Applies institution admin API routes, multi-workspace selection,
invitation acceptance, and staff management to backend/main.py.
"""

import re

MAIN_PATH = "backend/main.py"

with open(MAIN_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
if "import secrets" not in content:
    content = "import secrets\n" + content
if "from typing import Literal, Optional, List, Dict, Any" not in content:
    content = content.replace("from typing import Literal, Optional", "from typing import Literal, Optional, List, Dict, Any")

# 2. Update LoginResponse
old_login_resp = """class LoginResponse(BaseModel):
    access_token: str
    token_type: str"""

new_login_resp = """class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    requires_workspace_selection: bool = False
    temp_token: Optional[str] = None
    workspaces: Optional[List[Dict[str, Any]]] = None
    role: Optional[str] = None
    school_id: Optional[str] = None"""

if old_login_resp in content:
    content = content.replace(old_login_resp, new_login_resp)

# 3. Update login function
old_login_fn = """@app.post("/auth/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    \"\"\"Use the username field for an email address or phone number.\"\"\"
    identifier = form.username.strip()

    conn = get_connection()
    try:
        user = conn.execute(
            \"\"\"
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active
            FROM users
            WHERE email = ? COLLATE NOCASE OR phone = ?
            \"\"\",
            (identifier, identifier),
        ).fetchone()
    finally:
        conn.close()

    if (
        user is None
        or not user["is_active"]
        or not verify_password(form.password, user["password_hash"])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(dict(user)),
        "token_type": "bearer",
    }"""

new_login_fn = """@app.post("/auth/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    \"\"\"Use the username field for an email address or phone number.\"\"\"
    identifier = form.username.strip()

    conn = get_connection()
    try:
        user = conn.execute(
            \"\"\"
            SELECT user_id, email, phone, password_hash,
                   role, school_id, is_active, status, full_name
            FROM users
            WHERE email = ? COLLATE NOCASE OR phone = ?
            \"\"\",
            (identifier, identifier),
        ).fetchone()

        if (
            user is None
            or not user["is_active"]
            or user["status"] == "suspended"
            or not verify_password(form.password, user["password_hash"])
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last_login
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user["user_id"],)
        )
        conn.commit()

        # Query active institution assignments
        inst_roles = conn.execute(
            \"\"\"
            SELECT uir.institution_id, s.school_name, s.school_type, uir.role_id
            FROM user_institution_roles uir
            JOIN schools s ON s.school_id = uir.institution_id
            WHERE uir.user_id = ? AND uir.status = 'active'
            \"\"\",
            (user["user_id"],)
        ).fetchall()

        # If user has multiple assigned institutions, require workspace selection
        if len(inst_roles) > 1 and user["role"] != "platform_admin":
            from auth import create_temp_token
            return {
                "requires_workspace_selection": True,
                "temp_token": create_temp_token(dict(user)),
                "workspaces": [
                    {
                        "institution_id": r["institution_id"],
                        "school_name": r["school_name"],
                        "school_type": r["school_type"],
                        "role_id": r["role_id"],
                    }
                    for r in inst_roles
                ],
            }

        active_school = inst_roles[0]["institution_id"] if inst_roles else user["school_id"]
        effective_role = inst_roles[0]["role_id"] if (inst_roles and user["role"] != "platform_admin") else user["role"]
        return {
            "access_token": create_access_token(dict(user), school_id=active_school),
            "token_type": "bearer",
            "role": effective_role,
            "school_id": active_school,
        }
    finally:
        conn.close()"""

if old_login_fn in content:
    content = content.replace(old_login_fn, new_login_fn)

# 4. Update get_my_account
old_me_fn = """@app.get("/auth/me")
def get_my_account(user: dict = Depends(get_current_user)):
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "phone": user["phone"],
        "role": user["role"],
        "school_id": user["school_id"],
        "is_active": bool(user["is_active"]),
    }"""

new_me_fn = """@app.get("/auth/me")
def get_my_account(user: dict = Depends(get_current_user)):
    conn = get_connection()
    try:
        workspaces = conn.execute(
            \"\"\"
            SELECT uir.institution_id, s.school_name, s.school_type, uir.role_id, uir.status
            FROM user_institution_roles uir
            JOIN schools s ON s.school_id = uir.institution_id
            WHERE uir.user_id = ? AND uir.status = 'active'
            \"\"\",
            (user["user_id"],)
        ).fetchall()

        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "phone": user["phone"],
            "full_name": user.get("full_name"),
            "role": user["role"],
            "school_id": user["school_id"],
            "is_active": bool(user["is_active"]),
            "status": user.get("status", "active"),
            "workspaces": [
                {
                    "institution_id": w["institution_id"],
                    "school_name": w["school_name"],
                    "school_type": w["school_type"],
                    "role_id": w["role_id"],
                }
                for w in workspaces
            ],
        }
    finally:
        conn.close()"""

if old_me_fn in content:
    content = content.replace(old_me_fn, new_me_fn)

# 5. Append New Institution Admin Endpoints
new_endpoints = """

# =====================================================================
# INSTITUTION ADMIN MANAGEMENT & WORKSPACE SELECTION ENDPOINTS
# =====================================================================

class InviteAdminPayload(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    institution_id: str
    role_id: Literal[
        "school_admin",
        "admissions_officer",
        "academic_admin",
        "student_records_officer",
        "school_staff"
    ] = "school_admin"


class AcceptInvitationPayload(BaseModel):
    token: str
    password: str


class SelectWorkspacePayload(BaseModel):
    temp_token: str
    institution_id: str


class InviteStaffPayload(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    role_id: Literal[
        "school_staff",
        "admissions_officer",
        "academic_admin",
        "student_records_officer"
    ] = "school_staff"


class ForgotPasswordPayload(BaseModel):
    identifier: str


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str


@app.get("/admin/institution-admins")
def list_institution_admins(user: dict = Depends(require_platform_admin)):
    \"\"\"Lists all institution administrators and staff assignments across schools.\"\"\"
    conn = get_connection()
    try:
        rows = conn.execute(\"\"\"
            SELECT u.user_id, u.full_name, u.email, u.phone, u.status as user_status,
                   u.is_active, u.created_at as user_created_at, u.last_login,
                   uir.id as role_mapping_id, uir.institution_id, s.school_name,
                   s.school_type, uir.role_id, uir.status as role_status,
                   it.token_id, it.expires_at as invitation_expires_at, it.is_used as invitation_used
            FROM user_institution_roles uir
            JOIN users u ON u.user_id = uir.user_id
            JOIN schools s ON s.school_id = uir.institution_id
            LEFT JOIN invitation_tokens it ON it.user_id = u.user_id AND it.institution_id = uir.institution_id
            ORDER BY uir.created_at DESC
        \"\"\").fetchall()

        result = []
        for r in rows:
            invitation_state = "accepted"
            if r["invitation_used"] == 0:
                invitation_state = "pending"
            elif r["invitation_used"] is None:
                invitation_state = "active"

            result.append({
                "mapping_id": r["role_mapping_id"],
                "user_id": r["user_id"],
                "full_name": r["full_name"],
                "email": r["email"],
                "phone": r["phone"],
                "institution_id": r["institution_id"],
                "school_name": r["school_name"],
                "school_type": r["school_type"],
                "role_id": r["role_id"],
                "status": r["role_status"] if r["is_active"] == 1 else "suspended",
                "invitation_status": invitation_state,
                "created_at": r["user_created_at"],
                "last_login": r["last_login"]
            })
        return result
    finally:
        conn.close()


@app.post("/admin/institution-admins/invite")
def invite_institution_admin(
    payload: InviteAdminPayload,
    user: dict = Depends(require_platform_admin)
):
    \"\"\"Platform Admin creates a new institution administrator with a cryptographic single-use invitation token.\"\"\"
    email_clean = payload.email.strip().lower()
    full_name_clean = payload.full_name.strip()
    inst_id = payload.institution_id.strip()

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        # 1. Verify institution exists
        school = conn.execute("SELECT school_name FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, f"Institution '{inst_id}' does not exist.")

        # 2. Check if user already exists
        existing_user = conn.execute("SELECT user_id, role, is_active FROM users WHERE email = ? COLLATE NOCASE", (email_clean,)).fetchone()

        if existing_user:
            user_id = existing_user["user_id"]
            # Check if role in institution already assigned
            existing_role = conn.execute(
                "SELECT id FROM user_institution_roles WHERE user_id = ? AND institution_id = ? AND role_id = ?",
                (user_id, inst_id, payload.role_id)
            ).fetchone()
            if existing_role:
                raise HTTPException(409, f"User already has role '{payload.role_id}' in institution '{inst_id}'.")
        else:
            # Create user in invited status
            user_id = str(uuid.uuid4())
            dummy_hash = hash_password(secrets.token_urlsafe(16) + "A1!")
            conn.execute(\"\"\"
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'invited', ?)
            \"\"\", (user_id, email_clean, payload.phone, dummy_hash, payload.role_id, inst_id, full_name_clean))

        # 3. Create entry in user_institution_roles
        role_mapping_id = str(uuid.uuid4())
        conn.execute(\"\"\"
            INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
            VALUES (?, ?, ?, ?, 'invited', ?)
        \"\"\", (role_mapping_id, user_id, inst_id, payload.role_id, user["user_id"]))

        # 4. Generate cryptographic invitation token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
        token_id = str(uuid.uuid4())

        conn.execute(\"\"\"
            INSERT INTO invitation_tokens (token_id, token_hash, user_id, institution_id, role_id, expires_at, is_used, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        \"\"\", (token_id, token_hash, user_id, inst_id, payload.role_id, expires_at, user["user_id"]))

        # 5. Audit Log
        audit_id = str(uuid.uuid4())
        conn.execute(\"\"\"
            INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
            VALUES (?, 'INVITE_INSTITUTION_ADMIN', 'user_institution_roles', ?, ?, ?, ?, ?)
        \"\"\", (audit_id, role_mapping_id, user["user_id"], user["role"], inst_id, json.dumps({
            "email": email_clean,
            "role_id": payload.role_id,
            "institution_id": inst_id
        })))

        conn.commit()

        # In non-production/dev without SMTP, honest disclosure and dev URL
        return {
            "status": "invited",
            "user_id": user_id,
            "email": email_clean,
            "institution_id": inst_id,
            "school_name": school["school_name"],
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "dev_token": raw_token,
            "email_delivery": "Simulated/Dev Mode: External SMTP unconfigured. Invitation link generated securely."
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/admin/institution-admins/{user_id}/suspend")
def suspend_institution_admin(user_id: str, user: dict = Depends(require_platform_admin)):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET is_active = 0, status = 'suspended' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'suspended' WHERE user_id = ?", (user_id,))
        conn.commit()
        return {"status": "suspended", "user_id": user_id}
    finally:
        conn.close()


@app.post("/admin/institution-admins/{user_id}/reactivate")
def reactivate_institution_admin(user_id: str, user: dict = Depends(require_platform_admin)):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET is_active = 1, status = 'active' WHERE user_id = ?", (user_id,))
        conn.execute("UPDATE user_institution_roles SET status = 'active' WHERE user_id = ?", (user_id,))
        conn.commit()
        return {"status": "active", "user_id": user_id}
    finally:
        conn.close()


@app.post("/admin/institution-admins/{user_id}/resend-invitation")
def resend_institution_invitation(user_id: str, user: dict = Depends(require_platform_admin)):
    conn = get_connection()
    try:
        target = conn.execute("SELECT email, full_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not target:
            raise HTTPException(404, "User not found.")

        role_row = conn.execute("SELECT institution_id, role_id FROM user_institution_roles WHERE user_id = ?", (user_id,)).fetchone()
        if not role_row:
            raise HTTPException(404, "User institution role not found.")

        # Invalidate old tokens
        conn.execute("UPDATE invitation_tokens SET is_used = 1 WHERE user_id = ?", (user_id,))

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
        token_id = str(uuid.uuid4())

        conn.execute(\"\"\"
            INSERT INTO invitation_tokens (token_id, token_hash, user_id, institution_id, role_id, expires_at, is_used, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        \"\"\", (token_id, token_hash, user_id, role_row["institution_id"], role_row["role_id"], expires_at, user["user_id"]))
        conn.commit()

        return {
            "status": "resent",
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "dev_token": raw_token
        }
    finally:
        conn.close()


@app.get("/auth/verify-invitation")
def verify_invitation_token(token: str = Query(...)):
    token_hash = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        row = conn.execute(\"\"\"
            SELECT it.*, u.email, u.full_name, s.school_name, s.school_type
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN schools s ON s.school_id = it.institution_id
            WHERE it.token_hash = ?
        \"\"\", (token_hash,)).fetchone()

        if not row:
            raise HTTPException(400, "Invalid invitation token.")

        if row["is_used"] == 1:
            raise HTTPException(400, "This invitation token has already been used.")

        # Check expiration
        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This invitation token has expired.")

        return {
            "valid": True,
            "email": row["email"],
            "full_name": row["full_name"],
            "institution_id": row["institution_id"],
            "school_name": row["school_name"],
            "school_type": row["school_type"],
            "role_id": row["role_id"]
        }
    finally:
        conn.close()


@app.post("/auth/accept-invitation")
def accept_invitation(payload: AcceptInvitationPayload):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    if len(payload.password) < 12:
        raise HTTPException(422, "Password must contain at least 12 characters.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        inv = conn.execute(\"\"\"
            SELECT * FROM invitation_tokens WHERE token_hash = ?
        \"\"\", (token_hash,)).fetchone()

        if not inv:
            raise HTTPException(400, "Invalid invitation token.")
        if inv["is_used"] == 1:
            raise HTTPException(400, "This invitation token has already been used.")

        exp = datetime.fromisoformat(inv["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This invitation token has expired.")

        new_hash = hash_password(payload.password)

        # Activate user and set password
        conn.execute(\"\"\"
            UPDATE users 
            SET password_hash = ?, is_active = 1, status = 'active'
            WHERE user_id = ?
        \"\"\", (new_hash, inv["user_id"]))

        # Activate user_institution_role
        conn.execute(\"\"\"
            UPDATE user_institution_roles
            SET status = 'active'
            WHERE user_id = ? AND institution_id = ? AND role_id = ?
        \"\"\", (inv["user_id"], inv["institution_id"], inv["role_id"]))

        # Mark token as used
        conn.execute(\"\"\"
            UPDATE invitation_tokens
            SET is_used = 1, used_at = CURRENT_TIMESTAMP
            WHERE token_id = ?
        \"\"\", (inv["token_id"],))

        conn.commit()
        return {"status": "activated", "message": "Account activated successfully. You can now sign in."}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/auth/select-workspace")
def select_institution_workspace(payload: SelectWorkspacePayload):
    \"\"\"Allows a multi-institution administrator to select their active institution workspace.\"\"\"
    import jwt
    from auth import JWT_SECRET_KEY, JWT_ALGORITHM
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired workspace selection token.",
    )
    try:
        decoded = jwt.decode(
            payload.temp_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat", "jti"]}
        )
        if decoded.get("purpose") != "workspace_selection":
            raise unauthorized
        user_id = decoded["sub"]
    except Exception:
        raise unauthorized

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, email, phone, role, school_id, is_active, status, full_name FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        if not user or user["is_active"] != 1 or user["status"] == "suspended":
            raise unauthorized

        inst_role = conn.execute(\"\"\"
            SELECT role_id FROM user_institution_roles
            WHERE user_id = ? AND institution_id = ? AND status = 'active'
        \"\"\", (user_id, payload.institution_id)).fetchone()

        if not inst_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this institution workspace."
            )

        user_data = dict(user)
        user_data["role"] = inst_role["role_id"]
        user_data["school_id"] = payload.institution_id

        access_token = create_access_token(user_data, school_id=payload.institution_id)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": inst_role["role_id"],
            "school_id": payload.institution_id
        }
    finally:
        conn.close()


@app.get("/school/admin/staff")
def list_institution_staff(user: dict = Depends(require_school_admin)):
    \"\"\"Lists staff assigned to the administrator's own school_id.\"\"\"
    school_id = user["school_id"]
    conn = get_connection()
    try:
        rows = conn.execute(\"\"\"
            SELECT u.user_id, u.full_name, u.email, u.phone, u.status as user_status,
                   u.is_active, uir.role_id, uir.status as role_status, uir.created_at
            FROM user_institution_roles uir
            JOIN users u ON u.user_id = uir.user_id
            WHERE uir.institution_id = ?
            ORDER BY uir.created_at DESC
        \"\"\", (school_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/school/admin/staff/invite")
def invite_school_staff(
    payload: InviteStaffPayload,
    user: dict = Depends(require_school_admin)
):
    \"\"\"School Admin invites staff for their OWN school ONLY. Cross-school or platform admin forbidden.\"\"\"
    school_id = user["school_id"]
    email_clean = payload.email.strip().lower()
    full_name_clean = payload.full_name.strip()

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        existing_user = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (email_clean,)).fetchone()
        if existing_user:
            user_id = existing_user["user_id"]
            existing_role = conn.execute(
                "SELECT id FROM user_institution_roles WHERE user_id = ? AND institution_id = ? AND role_id = ?",
                (user_id, school_id, payload.role_id)
            ).fetchone()
            if existing_role:
                raise HTTPException(409, f"Staff member already assigned role '{payload.role_id}' in this school.")
        else:
            user_id = str(uuid.uuid4())
            dummy_hash = hash_password(secrets.token_urlsafe(16) + "S1!")
            conn.execute(\"\"\"
                INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'invited', ?)
            \"\"\", (user_id, email_clean, payload.phone, dummy_hash, payload.role_id, school_id, full_name_clean))

        role_mapping_id = str(uuid.uuid4())
        conn.execute(\"\"\"
            INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
            VALUES (?, ?, ?, ?, 'invited', ?)
        \"\"\", (role_mapping_id, user_id, school_id, payload.role_id, user["user_id"]))

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
        token_id = str(uuid.uuid4())

        conn.execute(\"\"\"
            INSERT INTO invitation_tokens (token_id, token_hash, user_id, institution_id, role_id, expires_at, is_used, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        \"\"\", (token_id, token_hash, user_id, school_id, payload.role_id, expires_at, user["user_id"]))

        conn.commit()
        return {
            "status": "invited",
            "user_id": user_id,
            "school_id": school_id,
            "role_id": payload.role_id,
            "invitation_url": f"/accept-invitation?token={raw_token}",
            "dev_token": raw_token
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/auth/forgot-password")
def forgot_password(payload: ForgotPasswordPayload):
    identifier = payload.identifier.strip()
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, email FROM users WHERE (email = ? COLLATE NOCASE OR phone = ?) AND is_active = 1 AND status != 'suspended'",
            (identifier, identifier)
        ).fetchone()

        if user:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            reset_id = str(uuid.uuid4())

            conn.execute(\"\"\"
                INSERT INTO password_reset_tokens (reset_id, token_hash, user_id, expires_at, is_used)
                VALUES (?, ?, ?, ?, 0)
            \"\"\", (reset_id, token_hash, user["user_id"], expires_at))
            conn.commit()

            return {
                "status": "ok",
                "message": "If an active account exists with the provided details, password reset instructions have been generated.",
                "dev_reset_url": f"/reset-password?token={raw_token}"
            }

        return {
            "status": "ok",
            "message": "If an active account exists with the provided details, password reset instructions have been generated."
        }
    finally:
        conn.close()


@app.get("/auth/verify-reset-token")
def verify_reset_token(token: str = Query(...)):
    token_hash = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        row = conn.execute(\"\"\"
            SELECT prt.*, u.email
            FROM password_reset_tokens prt
            JOIN users u ON u.user_id = prt.user_id
            WHERE prt.token_hash = ?
        \"\"\", (token_hash,)).fetchone()

        if not row:
            raise HTTPException(400, "Invalid password reset token.")
        if row["is_used"] == 1:
            raise HTTPException(400, "This password reset token has already been used.")

        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This password reset token has expired.")

        return {"valid": True, "email": row["email"]}
    finally:
        conn.close()


@app.post("/auth/reset-password")
def reset_password(payload: ResetPasswordPayload):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    if len(payload.new_password) < 12:
        raise HTTPException(422, "Password must contain at least 12 characters.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(\"\"\"
            SELECT * FROM password_reset_tokens WHERE token_hash = ?
        \"\"\", (token_hash,)).fetchone()

        if not row or row["is_used"] == 1:
            raise HTTPException(400, "Invalid or already used password reset token.")

        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This password reset token has expired.")

        new_hash = hash_password(payload.new_password)

        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, row["user_id"]))
        conn.execute("UPDATE password_reset_tokens SET is_used = 1, used_at = CURRENT_TIMESTAMP WHERE reset_id = ?", (row["reset_id"],))
        conn.commit()

        return {"status": "ok", "message": "Password reset successfully. You can now log in with your new password."}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
"""

content += new_endpoints

with open(MAIN_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] backend/main.py updated successfully.")
