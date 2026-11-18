import re

main_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update AcceptInvitationPayload & add VerifyIdentityPayload
old_models = """class AcceptInvitationPayload(BaseModel):
    token: str
    password: str"""

new_models = """class VerifyIdentityPayload(BaseModel):
    institution_id: str
    email: str
    phone: Optional[str] = None


class AcceptInvitationPayload(BaseModel):
    token: Optional[str] = None
    session_token: Optional[str] = None
    password: str"""

assert old_models in content, "old_models not found in main.py"
content = content.replace(old_models, new_models, 1)

# 2. In invite_institution_admin, ensure full_name is in returned dictionary
old_invite_return = """"status": "invited",
            "user_id": user_id,
            "email": email_clean,"""

new_invite_return = """"status": "invited",
            "user_id": user_id,
            "full_name": full_name_clean,
            "email": email_clean,"""

assert old_invite_return in content, "old_invite_return not found in main.py"
content = content.replace(old_invite_return, new_invite_return, 1)

# 3. Add verify_invitation_identity and update accept_invitation
old_accept = """@app.post("/auth/accept-invitation")
def accept_invitation(payload: AcceptInvitationPayload):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    if len(payload.password) < 8:
        raise HTTPException(422, "Password must contain at least 8 characters.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        inv = conn.execute(\"\"\"
            SELECT it.*, u.email, u.full_name, s.school_name
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN schools s ON s.school_id = it.institution_id
            WHERE it.token_hash = ?
        \"\"\", (token_hash,)).fetchone()"""

new_accept = """@app.post("/auth/invitations/verify-identity")
def verify_invitation_identity(payload: VerifyIdentityPayload):
    \"\"\"Validates the intended administrator's official email against the pending invitation for the institution.
    Returns a cryptographically signed setup session token and read-only administrator details.
    Unauthorized attempts with mismatched emails are rejected with HTTP 403 Forbidden.\"\"\"
    inst_id = payload.institution_id.strip()
    email_clean = payload.email.strip().lower()

    conn = get_connection()
    try:
        # Check institution exists
        school = conn.execute("SELECT school_id, school_name, school_type, district FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, f"Institution '{inst_id}' not found.")

        # Find active pending invitation for this institution
        inv = conn.execute(\"\"\"
            SELECT it.*, u.email, u.full_name, u.phone, u.status as user_status
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            WHERE it.institution_id = ?
              AND it.is_used = 0
            ORDER BY it.created_at DESC LIMIT 1
        \"\"\", (inst_id,)).fetchone()

        if not inv:
            raise HTTPException(404, f"No pending administrator invitation found for {school['school_name']} ({inst_id}).")

        # Check expiration
        exp = datetime.fromisoformat(inv["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "The administrator invitation for this institution has expired. Please contact the Platform Administrator for a renewed invitation.")

        # STRICT SECURITY CHECK: Does the provided email match the invited administrator?
        expected_email = inv["email"].strip().lower()
        if email_clean != expected_email:
            record_platform_audit(
                conn,
                event_type="UNAUTHORIZED_INVITATION_CLAIM_ATTEMPT",
                event_category="security",
                institution_id=inst_id,
                actor_user_id=None,
                actor_role="anonymous",
                action=f"Unauthorized claim attempt on {school['school_name']} ({inst_id}) with email '{payload.email}'",
                remarks="Email mismatch on institution invitation claim"
            )
            conn.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Verification Failed: The provided email does not match the official invitee appointed for {school['school_name']}."
            )

        # Transition status to accepted_pending_password if not already
        if inv["user_status"] == "invited":
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE user_institution_roles SET status = 'accepted_pending_password' WHERE user_id = ? AND institution_id = ? AND status = 'invited'",
                (inv["user_id"], inst_id)
            )
            conn.execute(
                "UPDATE users SET status = 'accepted_pending_password' WHERE user_id = ? AND status = 'invited'",
                (inv["user_id"],)
            )
            record_platform_audit(
                conn,
                event_type="INVITATION_ACCEPTED_PENDING_PASSWORD",
                event_category="staff",
                institution_id=inst_id,
                actor_user_id=inv["user_id"],
                actor_role="academic_admin",
                actor_name=inv["full_name"],
                entity_type="invitation_tokens",
                entity_id=inv["token_id"],
                action=f"Academic Administrator identity verified for {inv['full_name']} ({inv['email']}); awaiting password creation",
                old_values={"status": "invited"},
                new_values={"status": "accepted_pending_password"},
                remarks="Candidate verified email identity; awaiting password configuration"
            )
            conn.commit()

        # Generate secure setup session token (valid for 30 minutes)
        import jwt
        from auth import JWT_SECRET_KEY, JWT_ALGORITHM
        setup_session_token = jwt.encode(
            {
                "sub": inv["user_id"],
                "email": inv["email"],
                "institution_id": inst_id,
                "token_id": inv["token_id"],
                "token_hash": inv["token_hash"],
                "purpose": "invitation_setup",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "jti": str(uuid.uuid4())
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        return {
            "status": "verified",
            "session_token": setup_session_token,
            "administrator": {
                "full_name": inv["full_name"],
                "email": inv["email"],
                "phone": inv["phone"],
                "institution_id": inst_id,
                "school_name": school["school_name"],
                "school_type": school["school_type"],
                "district": school["district"],
                "role_id": "academic_admin",
                "role_name": "Academic Administrator"
            }
        }
    finally:
        conn.close()


@app.post("/auth/accept-invitation")
def accept_invitation(payload: AcceptInvitationPayload):
    if len(payload.password) < 8:
        raise HTTPException(422, "Password must contain at least 8 characters.")

    inv_token_id = None
    token_hash = None

    if payload.session_token:
        import jwt
        from auth import JWT_SECRET_KEY, JWT_ALGORITHM
        try:
            decoded = jwt.decode(
                payload.session_token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"require": ["sub", "exp", "iat", "jti"]}
            )
            if decoded.get("purpose") != "invitation_setup":
                raise HTTPException(401, "Invalid session token purpose.")
            inv_token_id = decoded.get("token_id")
            token_hash = decoded.get("token_hash")
        except Exception:
            raise HTTPException(401, "Invalid or expired invitation setup session. Please verify your identity again.")
    elif payload.token:
        token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    else:
        raise HTTPException(400, "Missing invitation token or setup session.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        if inv_token_id:
            inv = conn.execute(\"\"\"
                SELECT it.*, u.email, u.full_name, s.school_name
                FROM invitation_tokens it
                JOIN users u ON u.user_id = it.user_id
                JOIN schools s ON s.school_id = it.institution_id
                WHERE it.token_id = ?
            \"\"\", (inv_token_id,)).fetchone()
        else:
            inv = conn.execute(\"\"\"
                SELECT it.*, u.email, u.full_name, s.school_name
                FROM invitation_tokens it
                JOIN users u ON u.user_id = it.user_id
                JOIN schools s ON s.school_id = it.institution_id
                WHERE it.token_hash = ?
            \"\"\", (token_hash,)).fetchone()"""

assert old_accept in content, "old_accept not found in main.py"
content = content.replace(old_accept, new_accept, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("backend/main.py successfully updated!")
