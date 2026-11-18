import os

main_file = r"C:\Users\callm\nagriksetu\backend\main.py"

endpoints_code = '''

# =============================================================================
# PHASE 11B GAP: THREE-LEVEL ONBOARDING WORKFLOW & GLOBAL MONITORING
# =============================================================================

class StaffCandidateInvitePayload(BaseModel):
    candidate_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    role_id: str = "school_staff"
    institution_id: Optional[str] = None

class StaffCandidateSubmitPayload(BaseModel):
    token: str
    candidate_name: Optional[str] = None
    candidate_phone: Optional[str] = None
    qualifications: Optional[List[dict]] = None
    employment_details: Optional[dict] = None
    documents: Optional[List[dict]] = None

class StaffCandidateCorrectionPayload(BaseModel):
    correction_notes: str

class StaffCandidateDeclinePayload(BaseModel):
    reason: str

class StaffCandidateApprovePayload(BaseModel):
    review_notes: Optional[str] = None

class StaffCandidateActivatePayload(BaseModel):
    activation_token: str
    password: str


@app.post("/school/admin/staff-applications/invite")
def invite_staff_candidate(
    payload: StaffCandidateInvitePayload,
    current_user: dict = Depends(require_school_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Level 2: Institution Admin generates an application invitation link for a staff candidate.
    Creates a pending staff application, NOT an active user account.
    """
    admin_school_id = current_user.get("school_id")
    target_school_id = payload.institution_id or admin_school_id
    if current_user.get("role") != "platform_admin" and target_school_id != admin_school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden: Cannot invite staff for another institution.")

    school = conn.execute("SELECT school_name, category FROM schools WHERE school_id = ?", (target_school_id,)).fetchone()
    if not school:
        raise HTTPException(status_code=404, detail="Institution not found.")

    email_clean = payload.candidate_email.strip().lower()
    name_clean = payload.candidate_name.strip()
    app_id = f"STF-{datetime.utcnow().year}-{target_school_id}-{uuid.uuid4().hex[:6].upper()}"
    candidate_token = secrets.token_urlsafe(32)

    conn.execute("""
        INSERT INTO staff_applications (
            application_id, candidate_token, institution_id, candidate_email,
            candidate_name, candidate_phone, role_id, status, created_by_user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'invited', ?)
    """, (app_id, candidate_token, target_school_id, email_clean, name_clean, payload.candidate_phone, payload.role_id, current_user["user_id"]))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'INVITE_STAFF_CANDIDATE', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, app_id, current_user["user_id"], current_user.get("role"), target_school_id, json.dumps({
        "candidate_email": email_clean,
        "candidate_name": name_clean,
        "role_id": payload.role_id,
        "institution_id": target_school_id,
        "admin_name": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()

    return {
        "status": "invited",
        "application_id": app_id,
        "candidate_token": candidate_token,
        "candidate_url": f"/staff-application?token={candidate_token}",
        "candidate_email": email_clean,
        "candidate_name": name_clean,
        "institution_id": target_school_id,
        "institution_name": school["school_name"],
        "role_id": payload.role_id,
        "message": "Staff candidate invitation link generated. The candidate must submit credentials and obtain approval before account activation."
    }


@app.get("/school/admin/staff-applications")
def list_staff_applications(
    current_user: dict = Depends(require_school_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Lists all staff candidate applications for caller's institution.
    """
    school_id = current_user.get("school_id")
    if not school_id and current_user.get("role") != "platform_admin":
        raise HTTPException(status_code=403, detail="Not assigned to an institution.")

    query = """
        SELECT sa.*, s.school_name, s.category,
               u_cr.full_name as creator_name, u_rev.full_name as reviewer_name
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        LEFT JOIN users u_cr ON u_cr.user_id = sa.created_by_user_id
        LEFT JOIN users u_rev ON u_rev.user_id = sa.reviewed_by_user_id
    """
    params = []
    if current_user.get("role") != "platform_admin":
        query += " WHERE sa.institution_id = ?"
        params.append(school_id)
    
    query += " ORDER BY sa.created_at DESC"
    rows = conn.execute(query, tuple(params)).fetchall()

    result = []
    for r in rows:
        result.append({
            "application_id": r["application_id"],
            "candidate_token": r["candidate_token"],
            "institution_id": r["institution_id"],
            "institution_name": r["school_name"],
            "category": r["category"],
            "candidate_email": r["candidate_email"],
            "candidate_name": r["candidate_name"],
            "candidate_phone": r["candidate_phone"],
            "role_id": r["role_id"],
            "status": r["status"],
            "qualifications": json.loads(r["qualifications_json"] or "[]"),
            "employment_details": json.loads(r["employment_details_json"] or "{}"),
            "documents": json.loads(r["documents_json"] or "[]"),
            "correction_notes": r["correction_notes"],
            "review_notes": r["review_notes"],
            "created_by": r["creator_name"] or r["created_by_user_id"],
            "reviewed_by": r["reviewer_name"] or r["reviewed_by_user_id"],
            "reviewed_at": r["reviewed_at"],
            "activation_token": r["activation_token"],
            "activation_url": f"/staff-activation?token={r['activation_token']}" if r["activation_token"] else None,
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })
    return result


@app.get("/school/admin/staff-applications/{application_id}")
def get_staff_application_detail(
    application_id: str,
    current_user: dict = Depends(require_school_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Institution Admin inspects submitted staff candidate details, qualifications, employment, and attached docs.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("""
        SELECT sa.*, s.school_name, s.category,
               u_cr.full_name as creator_name, u_rev.full_name as reviewer_name
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        LEFT JOIN users u_cr ON u_cr.user_id = sa.created_by_user_id
        LEFT JOIN users u_rev ON u_rev.user_id = sa.reviewed_by_user_id
        WHERE sa.application_id = ?
    """, (application_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden: Cannot view staff application of another institution.")

    history_rows = conn.execute("""
        SELECT audit_id, action, actor_user_id, actor_role, created_at, metadata_json
        FROM audit_logs
        WHERE entity_id = ?
        ORDER BY created_at ASC
    """, (application_id,)).fetchall()

    history = []
    for h in history_rows:
        meta = json.loads(h["metadata_json"] or "{}")
        history.append({
            "action": h["action"],
            "actor_role": h["actor_role"],
            "timestamp": h["created_at"],
            "details": meta
        })

    return {
        "application_id": row["application_id"],
        "candidate_token": row["candidate_token"],
        "institution_id": row["institution_id"],
        "institution_name": row["school_name"],
        "category": row["category"],
        "candidate_email": row["candidate_email"],
        "candidate_name": row["candidate_name"],
        "candidate_phone": row["candidate_phone"],
        "role_id": row["role_id"],
        "status": row["status"],
        "qualifications": json.loads(row["qualifications_json"] or "[]"),
        "employment_details": json.loads(row["employment_details_json"] or "{}"),
        "documents": json.loads(row["documents_json"] or "[]"),
        "correction_notes": row["correction_notes"],
        "review_notes": row["review_notes"],
        "created_by": row["creator_name"] or row["created_by_user_id"],
        "reviewed_by": row["reviewer_name"] or row["reviewed_by_user_id"],
        "reviewed_at": row["reviewed_at"],
        "activation_token": row["activation_token"],
        "activation_url": f"/staff-activation?token={row['activation_token']}" if row["activation_token"] else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "audit_history": history
    }


@app.post("/school/admin/staff-applications/{application_id}/request-correction")
def request_staff_application_correction(
    application_id: str,
    payload: StaffCandidateCorrectionPayload,
    current_user: dict = Depends(require_school_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Institution Admin requests corrections or missing information from candidate.
    Candidate can then update and resubmit.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("SELECT institution_id, candidate_email, candidate_name, status FROM staff_applications WHERE application_id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden.")

    notes_clean = payload.correction_notes.strip()
    if not notes_clean:
        raise HTTPException(status_code=422, detail="Correction notes are mandatory.")

    conn.execute("""
        UPDATE staff_applications
        SET status = 'correction_requested', correction_notes = ?, reviewed_by_user_id = ?,
            reviewed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (notes_clean, current_user["user_id"], application_id))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_CORRECTION_REQUESTED', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, application_id, current_user["user_id"], current_user.get("role"), row["institution_id"], json.dumps({
        "candidate_email": row["candidate_email"],
        "correction_notes": notes_clean,
        "reviewer": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()
    return {
        "status": "correction_requested",
        "application_id": application_id,
        "correction_notes": notes_clean,
        "message": "Correction request recorded. Candidate can now update and resubmit their application dossier."
    }


@app.post("/school/admin/staff-applications/{application_id}/approve")
def approve_staff_application(
    application_id: str,
    payload: StaffCandidateApprovePayload,
    current_user: dict = Depends(require_school_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Institution Admin approves staff candidate application.
    Generates a secure 72-hour single-use activation token for the candidate to set their password.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("SELECT institution_id, candidate_email, candidate_name, role_id, status FROM staff_applications WHERE application_id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden.")

    if row["status"] not in ("submitted", "resubmitted"):
        raise HTTPException(status_code=400, detail=f"Cannot approve application in '{row['status']}' status. Candidate must submit details first.")

    activation_token = secrets.token_urlsafe(32)
    activation_expires_at = (datetime.utcnow() + timedelta(hours=72)).isoformat()
    notes_clean = (payload.review_notes or "").strip()

    conn.execute("""
        UPDATE staff_applications
        SET status = 'approved', review_notes = ?, activation_token = ?,
            activation_expires_at = ?, reviewed_by_user_id = ?, reviewed_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (notes_clean, activation_token, activation_expires_at, current_user["user_id"], application_id))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_APPROVED', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, application_id, current_user["user_id"], current_user.get("role"), row["institution_id"], json.dumps({
        "candidate_email": row["candidate_email"],
        "role_id": row["role_id"],
        "review_notes": notes_clean,
        "reviewer": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()

    return {
        "status": "approved",
        "application_id": application_id,
        "candidate_email": row["candidate_email"],
        "activation_token": activation_token,
        "activation_url": f"/staff-activation?token={activation_token}",
        "expires_at": activation_expires_at,
        "message": "Staff application approved. Activation token issued for candidate password initialization."
    }


@app.post("/school/admin/staff-applications/{application_id}/decline")
def decline_staff_application(
    application_id: str,
    payload: StaffCandidateDeclinePayload,
    current_user: dict = Depends(require_school_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Institution Admin declines staff candidate application with formal reason.
    """
    school_id = current_user.get("school_id")
    row = conn.execute("SELECT institution_id, candidate_email, candidate_name, status FROM staff_applications WHERE application_id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff application not found.")

    if current_user.get("role") != "platform_admin" and row["institution_id"] != school_id:
        raise HTTPException(status_code=403, detail="Cross-institution access forbidden.")

    reason_clean = payload.reason.strip()
    if not reason_clean:
        raise HTTPException(status_code=422, detail="Decline reason is mandatory.")

    conn.execute("""
        UPDATE staff_applications
        SET status = 'declined', review_notes = ?, reviewed_by_user_id = ?,
            reviewed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (reason_clean, current_user["user_id"], application_id))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_DECLINED', 'staff_application', ?, ?, ?, ?, ?)
    """, (audit_id, application_id, current_user["user_id"], current_user.get("role"), row["institution_id"], json.dumps({
        "candidate_email": row["candidate_email"],
        "decline_reason": reason_clean,
        "reviewer": current_user.get("full_name") or current_user.get("email")
    })))

    conn.commit()

    return {
        "status": "declined",
        "application_id": application_id,
        "candidate_email": row["candidate_email"],
        "reason": reason_clean,
        "message": "Staff candidate application declined with formal notice."
    }


# -----------------------------------------------------------------------------
# Public Candidate Endpoints (No Login Required)
# -----------------------------------------------------------------------------

@app.get("/auth/staff-candidate/application")
def get_candidate_application(token: str = Query(...), conn: sqlite3.Connection = Depends(get_db)):
    """
    Candidate opens their unique invitation link to view or update application.
    """
    row = conn.execute("""
        SELECT sa.*, s.school_name, s.category, s.district
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        WHERE sa.candidate_token = ?
    """, (token.strip(),)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Invalid staff candidate invitation link or token.")

    return {
        "application_id": row["application_id"],
        "candidate_token": row["candidate_token"],
        "institution_id": row["institution_id"],
        "institution_name": row["school_name"],
        "category": row["category"],
        "district": row["district"],
        "candidate_email": row["candidate_email"],
        "candidate_name": row["candidate_name"],
        "candidate_phone": row["candidate_phone"],
        "role_id": row["role_id"],
        "status": row["status"],
        "qualifications": json.loads(row["qualifications_json"] or "[]"),
        "employment_details": json.loads(row["employment_details_json"] or "{}"),
        "documents": json.loads(row["documents_json"] or "[]"),
        "correction_notes": row["correction_notes"],
        "review_notes": row["review_notes"],
        "activation_token": row["activation_token"]
    }


@app.post("/auth/staff-candidate/submit")
def submit_candidate_application(
    payload: StaffCandidateSubmitPayload,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Candidate submits qualifications, employment history, and supporting document summaries.
    Sets status to 'submitted' or 'resubmitted' without creating an active user account.
    """
    row = conn.execute("""
        SELECT * FROM staff_applications WHERE candidate_token = ?
    """, (payload.token.strip(),)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Invalid candidate token.")

    if row["status"] not in ("invited", "correction_requested"):
        raise HTTPException(status_code=400, detail=f"Cannot submit application in '{row['status']}' state.")

    new_status = "resubmitted" if row["status"] == "correction_requested" else "submitted"
    name_clean = (payload.candidate_name or row["candidate_name"]).strip()
    phone_clean = (payload.candidate_phone or row["candidate_phone"] or "").strip() or None
    quals_json = json.dumps(payload.qualifications or [])
    empl_json = json.dumps(payload.employment_details or {})
    docs_json = json.dumps(payload.documents or [])

    conn.execute("""
        UPDATE staff_applications
        SET candidate_name = ?, candidate_phone = ?, qualifications_json = ?,
            employment_details_json = ?, documents_json = ?, status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (name_clean, phone_clean, quals_json, empl_json, docs_json, new_status, row["application_id"]))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_APPLICATION_SUBMITTED', 'staff_application', ?, ?, 'candidate', ?, ?)
    """, (audit_id, row["application_id"], row["candidate_email"], row["institution_id"], json.dumps({
        "status": new_status,
        "candidate_name": name_clean,
        "candidate_email": row["candidate_email"],
        "qualifications_count": len(payload.qualifications or []),
        "documents_count": len(payload.documents or [])
    })))

    conn.commit()

    return {
        "status": new_status,
        "application_id": row["application_id"],
        "message": "Staff candidate dossier submitted successfully. Your application is now pending review by the Institution Administrator."
    }


@app.post("/auth/staff-candidate/activate")
def activate_approved_candidate(
    payload: StaffCandidateActivatePayload,
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Candidate completes account activation ONLY AFTER approval. Sets their secure password.
    Creates active user account in 'users', 'user_institution_roles', and 'institution_staff_permissions'.
    """
    tok = payload.activation_token.strip()
    pwd = payload.password

    if len(pwd) < 12:
        raise HTTPException(status_code=422, detail="Password must contain at least 12 characters.")

    row = conn.execute("""
        SELECT * FROM staff_applications WHERE activation_token = ?
    """, (tok,)).fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Invalid activation token.")

    if row["status"] != "approved":
        raise HTTPException(status_code=400, detail=f"Application is in '{row['status']}' state; only approved candidates can activate.")

    if row["activation_expires_at"]:
        exp = datetime.fromisoformat(row["activation_expires_at"].replace("Z", ""))
        if datetime.utcnow() > exp:
            raise HTTPException(status_code=400, detail="Activation token has expired. Please request a fresh invitation from the administrator.")

    email_clean = row["candidate_email"].strip().lower()
    inst_id = row["institution_id"]
    role_id = row["role_id"]
    full_name = row["candidate_name"].strip()
    phone = row["candidate_phone"]

    # Check if user already exists
    existing = conn.execute("SELECT user_id FROM users WHERE email = ? COLLATE NOCASE", (email_clean,)).fetchone()
    pwd_hash = hash_password(pwd)

    if existing:
        user_id = existing["user_id"]
        conn.execute("""
            UPDATE users
            SET password_hash = ?, is_active = 1, status = 'active', full_name = ?, school_id = ?
            WHERE user_id = ?
        """, (pwd_hash, full_name, inst_id, user_id))
    else:
        user_id = str(uuid.uuid4())
        # Base role in users table must respect CHECK constraint: 'school_staff'
        conn.execute("""
            INSERT INTO users (user_id, email, phone, password_hash, role, school_id, is_active, status, full_name)
            VALUES (?, ?, ?, ?, 'school_staff', ?, 1, 'active', ?)
        """, (user_id, email_clean, phone, pwd_hash, inst_id, full_name))

    # user_institution_roles mapping
    existing_role = conn.execute("""
        SELECT id FROM user_institution_roles WHERE user_id = ? AND institution_id = ?
    """, (user_id, inst_id)).fetchone()

    if existing_role:
        conn.execute("""
            UPDATE user_institution_roles
            SET role_id = ?, status = 'active'
            WHERE id = ?
        """, (role_id, existing_role["id"]))
    else:
        conn.execute("""
            INSERT INTO user_institution_roles (id, user_id, institution_id, role_id, status, created_by)
            VALUES (?, ?, ?, ?, 'active', ?)
        """, (str(uuid.uuid4()), user_id, inst_id, role_id, row["created_by_user_id"]))

    # Seed permissions
    default_perms = DEFAULT_ROLE_PERMS.get(role_id, DEFAULT_ROLE_PERMS["school_staff"]).copy()
    existing_perm = conn.execute("""
        SELECT permission_id FROM institution_staff_permissions WHERE user_id = ? AND institution_id = ?
    """, (user_id, inst_id)).fetchone()

    if existing_perm:
        conn.execute("""
            UPDATE institution_staff_permissions
            SET role_id = ?, can_view_applications = ?, can_review_details = ?,
                can_request_clarification = ?, can_recommend_decision = ?, can_approve_stage1 = ?,
                can_view_history = ?, can_manage_academics = ?, can_manage_students = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE permission_id = ?
        """, (
            role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            existing_perm["permission_id"]
        ))
    else:
        conn.execute("""
            INSERT INTO institution_staff_permissions (
                permission_id, user_id, institution_id, role_id,
                can_view_applications, can_review_details, can_request_clarification,
                can_recommend_decision, can_approve_stage1, can_view_history,
                can_manage_academics, can_manage_students, granted_by_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), user_id, inst_id, role_id,
            1 if default_perms["can_view_applications"] else 0,
            1 if default_perms["can_review_details"] else 0,
            1 if default_perms["can_request_clarification"] else 0,
            1 if default_perms["can_recommend_decision"] else 0,
            1 if default_perms["can_approve_stage1"] else 0,
            1 if default_perms["can_view_history"] else 0,
            1 if default_perms["can_manage_academics"] else 0,
            1 if default_perms["can_manage_students"] else 0,
            row["reviewed_by_user_id"]
        ))

    # Mark application as activated and burn the activation token
    conn.execute("""
        UPDATE staff_applications
        SET status = 'activated', activation_token = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE application_id = ?
    """, (row["application_id"],))

    audit_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO audit_logs (audit_id, action, entity_type, entity_id, actor_user_id, actor_role, school_id, metadata_json)
        VALUES (?, 'STAFF_ACCOUNT_ACTIVATED', 'users', ?, ?, 'staff', ?, ?)
    """, (audit_id, user_id, email_clean, inst_id, json.dumps({
        "application_id": row["application_id"],
        "email": email_clean,
        "role_id": role_id
    })))

    conn.commit()

    return {
        "status": "activated",
        "user_id": user_id,
        "email": email_clean,
        "role_id": role_id,
        "institution_id": inst_id,
        "message": "Account successfully activated! You can now log into your institution staff portal."
    }


# -----------------------------------------------------------------------------
# Level 3: Platform Admin Global Staff Monitoring Endpoint
# -----------------------------------------------------------------------------

@app.get("/admin/staff-monitoring")
def get_global_staff_monitoring(
    institution_id: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Platform Admin monitors staff lifecycle across all 30 institutions:
    Invitations, candidate applications, approvals, rejections, corrections,
    role/permission updates, suspensions, and reactivations.
    """
    # 1. Fetch Summary Metrics across all 30 institutions
    app_stats = conn.execute("""
        SELECT status, COUNT(*) as cnt FROM staff_applications GROUP BY status
    """).fetchall()
    app_map = {r["status"]: r["cnt"] for r in app_stats}

    staff_stats = conn.execute("""
        SELECT u.is_active, uir.status, COUNT(*) as cnt
        FROM user_institution_roles uir
        JOIN users u ON u.user_id = uir.user_id
        GROUP BY u.is_active, uir.status
    """).fetchall()

    total_active_staff = sum(r["cnt"] for r in staff_stats if r["is_active"] == 1 and r["status"] == "active")
    total_suspended_staff = sum(r["cnt"] for r in staff_stats if r["is_active"] == 0 or r["status"] == "suspended")

    # 2. Fetch Applications with Institution Details
    app_query = """
        SELECT sa.*, s.school_name, s.category, s.district,
               u_cr.full_name as creator_name, u_rev.full_name as reviewer_name
        FROM staff_applications sa
        JOIN schools s ON s.school_id = sa.institution_id
        LEFT JOIN users u_cr ON u_cr.user_id = sa.created_by_user_id
        LEFT JOIN users u_rev ON u_rev.user_id = sa.reviewed_by_user_id
        WHERE 1=1
    """
    app_params = []
    if institution_id:
        app_query += " AND sa.institution_id = ?"
        app_params.append(institution_id)
    if category:
        app_query += " AND s.category = ?"
        app_params.append(category)
    if search:
        app_query += " AND (sa.candidate_name LIKE ? OR sa.candidate_email LIKE ? OR sa.application_id LIKE ?)"
        term = f"%{search.strip()}%"
        app_params.extend([term, term, term])

    app_query += " ORDER BY sa.created_at DESC LIMIT ?"
    app_params.append(limit)

    app_rows = conn.execute(app_query, tuple(app_params)).fetchall()

    applications_list = []
    for r in app_rows:
        applications_list.append({
            "application_id": r["application_id"],
            "institution_id": r["institution_id"],
            "institution_name": r["school_name"],
            "category": r["category"],
            "district": r["district"],
            "candidate_name": r["candidate_name"],
            "candidate_email": r["candidate_email"],
            "candidate_phone": r["candidate_phone"],
            "role_id": r["role_id"],
            "status": r["status"],
            "correction_notes": r["correction_notes"],
            "review_notes": r["review_notes"],
            "created_by": r["creator_name"] or r["created_by_user_id"],
            "reviewed_by": r["reviewer_name"] or r["reviewed_by_user_id"],
            "reviewed_at": r["reviewed_at"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })

    # 3. Append-only Audit Ledger for all staff activities
    audit_query = """
        SELECT al.audit_id, al.action, al.entity_type, al.entity_id,
               al.actor_user_id, al.actor_role, al.school_id, al.created_at,
               al.metadata_json, s.school_name, s.category,
               u.full_name as actor_name
        FROM audit_logs al
        LEFT JOIN schools s ON s.school_id = al.school_id
        LEFT JOIN users u ON u.user_id = al.actor_user_id
        WHERE (al.action LIKE '%STAFF%' OR al.action LIKE '%INSTITUTION_ADMIN%' OR al.entity_type IN ('staff_application', 'institution_staff_permissions'))
    """
    audit_params = []
    if institution_id:
        audit_query += " AND al.school_id = ?"
        audit_params.append(institution_id)
    if category:
        audit_query += " AND s.category = ?"
        audit_params.append(category)

    audit_query += " ORDER BY al.created_at DESC LIMIT ?"
    audit_params.append(limit)

    audit_rows = conn.execute(audit_query, tuple(audit_params)).fetchall()

    events_list = []
    for a in audit_rows:
        events_list.append({
            "audit_id": a["audit_id"],
            "action": a["action"],
            "entity_type": a["entity_type"],
            "entity_id": a["entity_id"],
            "actor_user_id": a["actor_user_id"],
            "actor_name": a["actor_name"] or a["actor_user_id"],
            "actor_role": a["actor_role"],
            "institution_id": a["school_id"],
            "institution_name": a["school_name"],
            "category": a["category"],
            "timestamp": a["created_at"],
            "metadata": json.loads(a["metadata_json"] or "{}")
        })

    return {
        "summary": {
            "total_candidate_applications": sum(app_map.values()),
            "pending_applications": app_map.get("submitted", 0) + app_map.get("resubmitted", 0),
            "correction_requested": app_map.get("correction_requested", 0),
            "approved_applications": app_map.get("approved", 0),
            "declined_applications": app_map.get("declined", 0),
            "activated_accounts": app_map.get("activated", 0),
            "active_roster_staff": total_active_staff,
            "suspended_staff": total_suspended_staff,
            "monitored_institutions": 30
        },
        "applications": applications_list,
        "audit_events": events_list
    }
'''

with open(main_file, "a", encoding="utf-8") as f:
    f.write(endpoints_code)

print("Phase 11B gap endpoints appended to main.py successfully!")
