import re

MAIN_PATH = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(MAIN_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add get_institution_admin_status_dict helper function above list_schools
STATUS_HELPER = '''def get_institution_admin_status_dict(conn, school_id, inst_row=None):
    if inst_row is None:
        inst = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools WHERE school_id = ?", (school_id,)).fetchone()
        if not inst:
            return None
    else:
        inst = inst_row

    roles = conn.execute("""
        SELECT u.user_id, u.email, u.full_name, u.is_active, u.status as user_status,
               uir.id as mapping_id, uir.status as role_status, uir.role_id, uir.created_at
        FROM user_institution_roles uir
        JOIN users u ON u.user_id = uir.user_id
        WHERE uir.institution_id = ?
          AND uir.role_id IN ('academic_admin', 'school_admin')
        ORDER BY uir.created_at DESC
    """, (school_id,)).fetchall()

    latest_token = conn.execute("""
        SELECT it.token_id, it.user_id, it.expires_at, it.is_used, it.created_at,
               u.email, u.full_name, u.status as user_status, u.is_active,
               uir.status as uir_status
        FROM invitation_tokens it
        JOIN users u ON u.user_id = it.user_id
        LEFT JOIN user_institution_roles uir ON uir.user_id = it.user_id AND uir.institution_id = it.institution_id
        WHERE it.institution_id = ?
          AND it.role_id IN ('academic_admin', 'school_admin')
        ORDER BY it.created_at DESC
        LIMIT 1
    """, (school_id,)).fetchone()

    # Priority 1: ACTIVE Administrator
    active_role = next((r for r in roles if r["role_status"] == "active" and r["is_active"] == 1 and r["user_status"] == "active"), None)
    if active_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "ACTIVE",
            "button_label": "Continue to Administrator Login →",
            "has_active_admin": True,
            "has_pending_invitation": False,
            "is_invited": False,
            "is_pending_password": False,
            "is_suspended": False,
            "can_login": True,
            "status_description": "Active Academic Administrator configured and verified."
        }

    # Priority 2: SUSPENDED Administrator (slot retained)
    suspended_role = next((r for r in roles if (r["role_status"] == "suspended" or r["user_status"] == "suspended") and r["role_status"] not in ("revoked", "declined")), None)
    if suspended_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "SUSPENDED",
            "button_label": "Account Suspended",
            "has_active_admin": False,
            "has_pending_invitation": False,
            "is_invited": False,
            "is_pending_password": False,
            "is_suspended": True,
            "can_login": False,
            "status_description": "Administrator account is temporarily suspended by Platform Administration."
        }

    # Priority 3: ACCEPTED_PENDING_PASSWORD
    pending_pwd_role = next((r for r in roles if (r["role_status"] == "accepted_pending_password" or r["user_status"] == "accepted_pending_password") and r["role_status"] not in ("revoked", "declined")), None)
    if pending_pwd_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "ACCEPTED_PENDING_PASSWORD",
            "button_label": "Complete Account Setup",
            "has_active_admin": False,
            "has_pending_invitation": True,
            "is_invited": False,
            "is_pending_password": True,
            "is_suspended": False,
            "can_login": False,
            "status_description": "Invitation accepted. Password creation required before login is enabled."
        }

    # Priority 4: INVITED
    if latest_token and latest_token["is_used"] == 0:
        try:
            exp = datetime.fromisoformat(latest_token["expires_at"].replace("Z", ""))
            is_expired = datetime.utcnow() > exp
        except Exception:
            is_expired = False

        if not is_expired and latest_token["uir_status"] not in ("revoked", "declined"):
            if latest_token["uir_status"] == "accepted_pending_password" or latest_token["user_status"] == "accepted_pending_password":
                return {
                    "institution_id": inst["school_id"],
                    "institution_name": inst["school_name"],
                    "category": inst["category"],
                    "district": inst["district"],
                    "school_type": inst["school_type"],
                    "status": "ACCEPTED_PENDING_PASSWORD",
                    "button_label": "Complete Account Setup",
                    "has_active_admin": False,
                    "has_pending_invitation": True,
                    "is_invited": False,
                    "is_pending_password": True,
                    "is_suspended": False,
                    "can_login": False,
                    "status_description": "Invitation accepted. Password creation required before login is enabled."
                }
            return {
                "institution_id": inst["school_id"],
                "institution_name": inst["school_name"],
                "category": inst["category"],
                "district": inst["district"],
                "school_type": inst["school_type"],
                "status": "INVITED",
                "button_label": "Invitation Available",
                "has_active_admin": False,
                "has_pending_invitation": True,
                "is_invited": True,
                "is_pending_password": False,
                "is_suspended": False,
                "can_login": False,
                "status_description": "Administrator invitation issued. Pending invitee acceptance."
            }
        elif is_expired:
            return {
                "institution_id": inst["school_id"],
                "institution_name": inst["school_name"],
                "category": inst["category"],
                "district": inst["district"],
                "school_type": inst["school_type"],
                "status": "EXPIRED",
                "button_label": "Invitation Required",
                "has_active_admin": False,
                "has_pending_invitation": False,
                "is_invited": False,
                "is_pending_password": False,
                "is_suspended": False,
                "can_login": False,
                "status_description": "Previous administrator invitation has expired. An invitation is required."
            }

    # Priority 5: REVOKED / DECLINED
    revoked_role = next((r for r in roles if r["role_status"] in ("revoked", "declined")), None)
    if revoked_role:
        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "status": "NOT_INVITED",
            "button_label": "Invitation Required",
            "has_active_admin": False,
            "has_pending_invitation": False,
            "is_invited": False,
            "is_pending_password": False,
            "is_suspended": False,
            "can_login": False,
            "status_description": "Previous invitation or assignment was revoked. An invitation is required."
        }

    # Default: NOT_INVITED
    return {
        "institution_id": inst["school_id"],
        "institution_name": inst["school_name"],
        "category": inst["category"],
        "district": inst["district"],
        "school_type": inst["school_type"],
        "status": "NOT_INVITED",
        "button_label": "Invitation Required",
        "has_active_admin": False,
        "has_pending_invitation": False,
        "is_invited": False,
        "is_pending_password": False,
        "is_suspended": False,
        "can_login": False,
        "status_description": "No administrator invitation has been generated for this institution."
    }
'''

# Find def list_schools
old_list_schools_start = '@app.get("/schools")\ndef list_schools('
assert old_list_schools_start in code, "Could not find list_schools"

# Replace list_schools
new_list_schools = '''@app.get("/schools")
def list_schools(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.school_id, s.school_name, s.district, s.state,
                   s.school_type, s.category, s.address, s.established_year,
                   s.description, s.public_phone, s.website, s.facilities_json,
                   s.logo_url, s.cover_image_url, s.affiliation, s.recognition,
                   COALESCE(SUM(ps.capacity), 0) AS total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN ps.capacity > ps.current_strength THEN ps.capacity - ps.current_strength ELSE 0 END), 0) AS available_seats
            FROM schools s
            LEFT JOIN program_sections ps ON ps.institution_id = s.school_id
            GROUP BY s.school_id
            ORDER BY s.school_name
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["admin_status"] = get_institution_admin_status_dict(conn, d["school_id"], d)
            result.append(d)
        return result
    finally:
        conn.close()'''

# Replace from @app.get("/schools") down to return [dict(row) for row in rows]\n    finally:\n        conn.close()
target_schools_block = '''@app.get("/schools")
def list_schools(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.school_id, s.school_name, s.district, s.state,
                   s.school_type, s.category, s.address, s.established_year,
                   s.description, s.public_phone, s.website, s.facilities_json,
                   s.logo_url, s.cover_image_url, s.affiliation, s.recognition,
                   COALESCE(SUM(ps.capacity), 0) AS total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN ps.capacity > ps.current_strength THEN ps.capacity - ps.current_strength ELSE 0 END), 0) AS available_seats
            FROM schools s
            LEFT JOIN program_sections ps ON ps.institution_id = s.school_id
            GROUP BY s.school_id
            ORDER BY s.school_name
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()'''

assert target_schools_block in code, "target_schools_block not found"
code = code.replace(target_schools_block, STATUS_HELPER + "\n\n" + new_list_schools, 1)

# 2. Update verify_invitation_token to transition user to accepted_pending_password
old_verify_block = '''@app.get("/auth/verify-invitation")
def verify_invitation_token(token: str = Query(...)):
    token_hash = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT it.*, u.email, u.full_name, s.school_name, s.school_type
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN schools s ON s.school_id = it.institution_id
            WHERE it.token_hash = ?
        """, (token_hash,)).fetchone()

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
        conn.close()'''

new_verify_block = '''@app.get("/auth/verify-invitation")
def verify_invitation_token(token: str = Query(...)):
    token_hash = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT it.*, u.email, u.full_name, u.status as user_status, s.school_name, s.school_type
            FROM invitation_tokens it
            JOIN users u ON u.user_id = it.user_id
            JOIN schools s ON s.school_id = it.institution_id
            WHERE it.token_hash = ?
        """, (token_hash,)).fetchone()

        if not row:
            raise HTTPException(400, "Invalid invitation token.")

        if row["is_used"] == 1:
            raise HTTPException(400, "This invitation token has already been used.")

        # Check expiration
        exp = datetime.fromisoformat(row["expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(400, "This invitation token has expired.")

        # State C: When invited administrator opens & verifies invitation, transition status to accepted_pending_password
        if row["user_status"] == "invited":
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE user_institution_roles SET status = 'accepted_pending_password' WHERE user_id = ? AND institution_id = ? AND status = 'invited'",
                (row["user_id"], row["institution_id"])
            )
            conn.execute(
                "UPDATE users SET status = 'accepted_pending_password' WHERE user_id = ? AND status = 'invited'",
                (row["user_id"],)
            )
            record_platform_audit(
                conn,
                event_type="INVITATION_ACCEPTED_PENDING_PASSWORD",
                event_category="staff",
                institution_id=row["institution_id"],
                actor_user_id=row["user_id"],
                actor_role="academic_admin",
                actor_name=row["full_name"],
                entity_type="invitation_tokens",
                entity_id=row["token_id"],
                action=f"Academic Administrator invitation opened and accepted by {row['full_name']} ({row['email']}); awaiting password creation",
                old_values={"status": "invited"},
                new_values={"status": "accepted_pending_password"},
                remarks="Candidate verified token; awaiting password configuration"
            )
            conn.commit()

        return {
            "valid": True,
            "email": row["email"],
            "full_name": row["full_name"],
            "institution_id": row["institution_id"],
            "school_name": row["school_name"],
            "school_type": row["school_type"],
            "role_id": row["role_id"],
            "status": "ACCEPTED_PENDING_PASSWORD"
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()'''

assert old_verify_block in code, "old_verify_block not found"
code = code.replace(old_verify_block, new_verify_block, 1)

# 3. Update check_institution_admin_status and add get_all_institution_admin_statuses
old_admin_status_block = '''@app.get("/auth/institution/{institution_id}/admin-status")
def check_institution_admin_status(institution_id: str):
    conn = get_connection()
    try:
        inst = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools WHERE school_id = ?", (institution_id,)).fetchone()
        if not inst:
            raise HTTPException(404, f"Institution '{institution_id}' not found.")
        
        # Check active admins in users or user_institution_roles
        admin_count = conn.execute("""
            SELECT COUNT(DISTINCT u.user_id)
            FROM users u
            LEFT JOIN user_institution_roles uir ON u.user_id = uir.user_id
            WHERE u.is_active = 1 AND u.status = 'active'
              AND (
                (u.role = 'school_admin' AND u.school_id = ?)
                OR
                (uir.institution_id = ? AND uir.role_id = 'school_admin' AND uir.status = 'active')
              )
        """, (institution_id, institution_id)).fetchone()[0]

        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "category": inst["category"],
            "district": inst["district"],
            "school_type": inst["school_type"],
            "has_active_admin": admin_count > 0,
            "active_admin_count": admin_count
        }
    finally:
        conn.close()'''

new_admin_status_block = '''@app.get("/auth/institutions/admin-statuses")
def get_all_institution_admin_statuses():
    """Returns the administrator invitation and activation status for all institutions."""
    conn = get_connection()
    try:
        schools = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools ORDER BY school_id").fetchall()
        result = {}
        for s in schools:
            result[s["school_id"]] = get_institution_admin_status_dict(conn, s["school_id"], s)
        return result
    finally:
        conn.close()


@app.get("/auth/institution/{institution_id}/admin-status")
def check_institution_admin_status(institution_id: str):
    conn = get_connection()
    try:
        status_info = get_institution_admin_status_dict(conn, institution_id)
        if not status_info:
            raise HTTPException(404, f"Institution '{institution_id}' not found.")
        return status_info
    finally:
        conn.close()'''

assert old_admin_status_block in code, "old_admin_status_block not found"
code = code.replace(old_admin_status_block, new_admin_status_block, 1)

with open(MAIN_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("backend/main.py successfully patched with status endpoints!")
