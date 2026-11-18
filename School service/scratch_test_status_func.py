import sqlite3

def get_institution_admin_status_dict(conn, school_id):
    # 1. Check schools
    inst = conn.execute("SELECT school_id, school_name, category, district, school_type FROM schools WHERE school_id = ?", (school_id,)).fetchone()
    if not inst:
        return None

    # 2. Check for active/suspended/invited academic admin or school admin
    # Query user_institution_roles
    roles = conn.execute("""
        SELECT u.user_id, u.email, u.full_name, u.is_active, u.status as user_status,
               uir.id as mapping_id, uir.status as role_status, uir.role_id, uir.created_at
        FROM user_institution_roles uir
        JOIN users u ON u.user_id = uir.user_id
        WHERE uir.institution_id = ?
          AND uir.role_id IN ('academic_admin', 'school_admin')
        ORDER BY uir.created_at DESC
    """, (school_id,)).fetchall()

    # Query latest invitation token
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

    # Evaluate State in priority order:
    # Check if any role is active
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
            "can_login": True,
            "status_description": "Active Academic Administrator configured and verified."
        }

    # Check if suspended
    suspended_role = next((r for r in roles if r["role_status"] == "suspended" or r["user_status"] == "suspended"), None)
    if suspended_role and suspended_role["role_status"] not in ("revoked", "declined"):
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
            "can_login": False,
            "status_description": "Administrator account is temporarily suspended. Contact Platform Administration."
        }

    # Check if accepted_pending_password
    pending_pwd_role = next((r for r in roles if r["role_status"] == "accepted_pending_password" or r["user_status"] == "accepted_pending_password"), None)
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
            "can_login": False,
            "status_description": "Invitation accepted. Password creation required before login is enabled."
        }

    # Check if invited
    if latest_token and latest_token["is_used"] == 0:
        # Check expiry
        import datetime
        try:
            exp = datetime.datetime.fromisoformat(latest_token["expires_at"].replace("Z", ""))
            is_expired = datetime.datetime.utcnow() > exp
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
                "can_login": False,
                "status_description": "Previous administrator invitation has expired. An invitation is required."
            }

    # If revoked or declined
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
            "can_login": False,
            "status_description": "Previous invitation was revoked. An invitation is required."
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
        "can_login": False,
        "status_description": "No administrator invitation has been generated for this institution."
    }

conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
conn.row_factory = sqlite3.Row
print("SCH001 status:", get_institution_admin_status_dict(conn, "SCH001"))
conn.close()
