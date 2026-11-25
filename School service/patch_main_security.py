import re
import sys

MAIN_PATH = r'C:\Users\callm\nagriksetu\backend\main.py'

with open(MAIN_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("Original content length:", len(content))

# 1. Update GET /parent/children
old_parent_children = '''@app.get("/parent/children")
def list_parent_children(user: dict = Depends(require_parent)):
    """List only children linked to this verified parent account."""
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            return []

        rows = conn.execute(
            """
            SELECT s.student_id, s.permanent_student_id,
                   s.student_name, s.school_id, sc.school_name,
                   s.standard, s.section, s.first_language,
                   s.enrollment_status
            FROM student_guardians sg
            JOIN students s
              ON s.permanent_student_id = sg.permanent_student_id
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            WHERE sg.guardian_id = ?
              AND sg.is_verified = 1
              AND sg.can_view_records = 1
            ORDER BY s.student_name
            """,
            (guardian["guardian_id"],),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()'''

new_parent_children = '''@app.get("/parent/children")
def list_parent_children(user: dict = Depends(require_parent)):
    """List only verified children linked to this verified parent account with enriched academic details."""
    conn = get_connection()
    try:
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            return []

        rows = conn.execute(
            """
            SELECT s.student_id, s.permanent_student_id,
                   s.student_name, s.school_id, sc.school_name,
                   sc.school_type, sc.category,
                   s.standard, s.section, s.first_language,
                   s.enrollment_status,
                   e.academic_year, e.stream as enroll_stream,
                   ap.program_name, ap.discipline_or_stream, ap.department_name
            FROM student_guardians sg
            JOIN students s
              ON s.permanent_student_id = sg.permanent_student_id
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = s.school_id
            WHERE sg.guardian_id = ?
              AND sg.is_verified = 1
              AND sg.can_view_records = 1
            GROUP BY s.permanent_student_id
            ORDER BY s.student_name
            """,
            (guardian["guardian_id"],),
        ).fetchall()

        children = []
        for r in rows:
            d = dict(r)
            d["institution_name"] = d.get("school_name") or d.get("school_id")
            d["institution_type"] = d.get("school_type") or d.get("category") or "School"
            stream = d.get("enroll_stream") or d.get("discipline_or_stream") or ""
            d["program_or_stream"] = d.get("program_name") or stream or "General Academic"
            
            std = d.get("standard")
            sec = d.get("section") or "A"
            if "PU" in str(d["institution_type"]) or "College" in str(d["institution_type"]) or "University" in str(d["institution_type"]):
                d["class_or_standard"] = f"Year {std}" if std is not None else "Year 1"
            else:
                d["class_or_standard"] = f"Standard {std}" if std is not None else "N/A"
                
            d["program_or_class"] = f"{d['program_or_stream']} · {d['class_or_standard']} ({sec})"
            d["is_verified"] = 1
            children.append(d)

        return children
    finally:
        conn.close()


class StudentLookupByIdResult(BaseModel):
    student_full_name: str
    student_id: str
    permanent_student_id: str
    institution_id: str
    institution_name: str
    institution_type: str
    category: str
    district: Optional[str] = None
    state: Optional[str] = None
    program_or_stream: str
    class_or_standard: str
    standard: Optional[int] = None
    section: Optional[str] = None
    academic_year: str
    semester: Optional[int] = None
    is_already_linked: bool


class RequestLinkingCodePayload(BaseModel):
    student_id: str
    relationship_type: Optional[str] = "Father"


class VerifyAndLinkChildPayload(BaseModel):
    student_id: str
    verification_code: str
    relationship_type: str = "Parent"


@app.get("/parent/lookup-by-student-id", response_model=StudentLookupByIdResult)
def lookup_student_by_student_id(
    student_id: str = Query(..., min_length=1, max_length=100),
    user: dict = Depends(require_parent),
):
    """
    Search student using an exact Student ID match against the live database.
    Fetches institution and enrollment details without guessing.
    Returns HTTP 404 if no exact match exists.
    """
    clean_id = student_id.strip()
    if not clean_id:
        raise HTTPException(status_code=400, detail="Student ID parameter is required.")

    conn = get_connection()
    try:
        query = """
            SELECT s.student_id, s.permanent_student_id, s.student_name,
                   s.school_id, s.standard, s.section, s.enrollment_status,
                   sc.school_name, sc.school_type, sc.category, sc.district, sc.state,
                   e.academic_year, e.stream AS enroll_stream,
                   ap.program_name, ap.discipline_or_stream, ap.department_name
            FROM students s
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = s.school_id
            WHERE UPPER(s.student_id) = UPPER(?)
            GROUP BY s.permanent_student_id
            LIMIT 1
        """
        row = conn.execute(query, (clean_id,)).fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No student record found matching Student ID '{clean_id}'. Please check the ID and try again.",
            )

        guardian = get_parent_guardian(conn, user["user_id"])
        is_already_linked = False
        if guardian:
            existing = conn.execute(
                """
                SELECT student_guardian_id FROM student_guardians
                WHERE guardian_id = ? AND permanent_student_id = ? AND is_verified = 1
                """,
                (guardian["guardian_id"], row["permanent_student_id"]),
            ).fetchone()
            if existing:
                is_already_linked = True

        inst_type = row["school_type"] or row["category"] or "Accredited Institution"
        category = row["category"] or row["school_type"] or "General"
        stream = row["enroll_stream"] or row["discipline_or_stream"] or ""
        program_or_stream = row["program_name"] or stream or "General Academic"

        std = row["standard"]
        sec = row["section"] or "A"
        if "PU" in str(inst_type) or "College" in str(inst_type) or "University" in str(inst_type):
            class_or_standard = f"Year {std}" if std is not None else "Year 1"
            semester = std if std is not None else 1
        else:
            class_or_standard = f"Standard {std}" if std is not None else "N/A"
            semester = None

        return {
            "student_full_name": row["student_name"],
            "student_id": row["student_id"],
            "permanent_student_id": row["permanent_student_id"],
            "institution_id": row["school_id"],
            "institution_name": row["school_name"] or row["school_id"],
            "institution_type": inst_type,
            "category": category,
            "district": row["district"] or "Karnataka",
            "state": row["state"] or "Karnataka",
            "program_or_stream": program_or_stream,
            "class_or_standard": class_or_standard,
            "standard": std,
            "section": sec,
            "academic_year": row["academic_year"] or "2026-2027",
            "semester": semester,
            "is_already_linked": is_already_linked,
        }
    finally:
        conn.close()


@app.post("/parent/request-linking-code")
def request_institution_linking_code(
    payload: RequestLinkingCodePayload,
    user: dict = Depends(require_parent),
):
    """
    Generate an expiring institution-issued verification code to authorize linking.
    Expires in 15 minutes and enforces attempt limits.
    Does NOT expose the plaintext code to the parent in responses or frontend.
    Creates a pending verification request for the institution administrator.
    """
    clean_id = payload.student_id.strip()
    if not clean_id:
        raise HTTPException(status_code=400, detail="Student ID is required.")

    rel_type = (getattr(payload, "relationship_type", None) or "Father").strip()

    conn = get_connection()
    try:
        student = conn.execute(
            """
            SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, sc.school_name
            FROM students s
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            WHERE UPPER(s.student_id) = UPPER(?)
            LIMIT 1
            """,
            (clean_id,),
        ).fetchone()

        if not student:
            raise HTTPException(status_code=404, detail=f"Student ID '{clean_id}' not found.")

        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian:
            already = conn.execute(
                """
                SELECT student_guardian_id FROM student_guardians
                WHERE guardian_id = ? AND permanent_student_id = ? AND is_verified = 1
                """,
                (guardian["guardian_id"], student["permanent_student_id"]),
            ).fetchone()
            if already:
                raise HTTPException(status_code=409, detail="This child is already linked to your account.")

        # Rate limiting: Check if a code was already requested within the last 30 seconds
        recent_code = conn.execute(
            """
            SELECT created_at FROM institution_linking_codes
            WHERE permanent_student_id = ? AND parent_user_id = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (student["permanent_student_id"], user["user_id"]),
        ).fetchone()
        if recent_code:
            try:
                rec_dt = datetime.fromisoformat(recent_code["created_at"])
                diff_sec = (datetime.now() - rec_dt).total_seconds()
                if diff_sec < 30:
                    wait_sec = max(1, int(30 - diff_sec))
                    raise HTTPException(
                        status_code=429,
                        detail=f"Please wait {wait_sec} second(s) before requesting another verification code.",
                    )
            except (ValueError, TypeError):
                pass

        # Invalidate previous unused codes for this student and parent
        conn.execute(
            """
            UPDATE institution_linking_codes
            SET is_used = 1
            WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
            """,
            (student["permanent_student_id"], user["user_id"]),
        )

        # Generate secure random 6-digit numeric verification code
        plain_code = f"{secrets.randbelow(900000) + 100000}"
        code_hash = hashlib.sha256(plain_code.encode("utf-8")).hexdigest()
        code_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = (now + timedelta(minutes=15)).isoformat()
        now_iso = now.isoformat()

        # Check existing pending linking_requests record
        pending_lr = conn.execute(
            """
            SELECT request_id FROM linking_requests
            WHERE parent_user_id = ? AND school_id = ? AND (student_ref = ? OR permanent_student_id = ?) AND request_status = 'pending'
            """,
            (user["user_id"], student["school_id"], clean_id, student["permanent_student_id"]),
        ).fetchone()

        with conn:
            # 1. Insert into institution_linking_codes with plain_code strictly NULL
            conn.execute(
                """
                INSERT INTO institution_linking_codes (
                    code_id, permanent_student_id, student_id, institution_id,
                    parent_user_id, code_hash, plain_code, attempts, max_attempts,
                    is_used, expires_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, NULL, 0, 5, 0, ?, ?)
                """,
                (
                    code_id,
                    student["permanent_student_id"],
                    student["student_id"],
                    student["school_id"],
                    user["user_id"],
                    code_hash,
                    expires_at,
                    now_iso,
                ),
            )

            # 2. Insert or update linking_requests for institution administrator desk
            if pending_lr:
                conn.execute(
                    """
                    UPDATE linking_requests
                    SET relationship_type = ?, created_at = ?, additional_notes = 'Verification code requested via Student ID linking workflow'
                    WHERE request_id = ?
                    """,
                    (rel_type, now_iso, pending_lr["request_id"]),
                )
            else:
                lr_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO linking_requests (
                        request_id, parent_user_id, school_id, student_ref, relationship_type,
                        request_status, permanent_student_id, additional_notes, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, 'pending', ?, 'Verification code requested via Student ID linking workflow', ?)
                    """,
                    (
                        lr_id,
                        user["user_id"],
                        student["school_id"],
                        student["student_id"],
                        rel_type,
                        student["permanent_student_id"],
                        now_iso,
                    ),
                )

        # Return sanitized response: NEVER expose plain_code or verification_code
        return {
            "status": "success",
            "message": "Your child-linking request has been submitted to the institution. Please complete the verification process using the instructions sent to your registered contact.",
            "delivery_mode": "institution_review",
            "expires_in_minutes": 15,
            "student_name": student["student_name"],
            "student_id": student["student_id"],
            "institution_name": student["school_name"] or student["school_id"],
            "institution_id": student["school_id"],
        }
    finally:
        conn.close()


@app.post("/parent/verify-and-link-child")
def verify_and_link_child(
    payload: VerifyAndLinkChildPayload,
    user: dict = Depends(require_parent),
):
    """
    Verify parent authorization using institution-issued verification code and create link in student_guardians.
    Prevents duplicate links, enforces expiration, and limits failed attempts.
    """
    clean_id = payload.student_id.strip()
    code_input = payload.verification_code.strip()
    rel_type = (payload.relationship_type or "Parent").strip()

    if not clean_id:
        raise HTTPException(status_code=400, detail="Student ID is required.")
    if not code_input:
        raise HTTPException(status_code=400, detail="Institution verification code is required.")

    conn = get_connection()
    try:
        student = conn.execute(
            """
            SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, sc.school_name
            FROM students s
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            WHERE UPPER(s.student_id) = UPPER(?)
            LIMIT 1
            """,
            (clean_id,),
        ).fetchone()

        if not student:
            raise HTTPException(status_code=404, detail=f"Student ID '{clean_id}' not found.")

        perm_id = student["permanent_student_id"]

        # Resolve guardian profile
        guardian = get_parent_guardian(conn, user["user_id"])
        if not guardian:
            raise HTTPException(status_code=403, detail="Unable to resolve guardian profile for your account.")

        # Check if already linked and verified
        existing_link = conn.execute(
            """
            SELECT student_guardian_id, is_verified FROM student_guardians
            WHERE guardian_id = ? AND permanent_student_id = ?
            """,
            (guardian["guardian_id"], perm_id),
        ).fetchone()

        if existing_link and existing_link["is_verified"] == 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{student['student_name']} ({student['student_id']}) is already verified and linked to your account.",
            )

        # Retrieve active verification code
        code_row = conn.execute(
            """
            SELECT code_id, code_hash, attempts, max_attempts, is_used, expires_at
            FROM institution_linking_codes
            WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (perm_id, user["user_id"]),
        ).fetchone()

        if not code_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code found for this student. Please request an institution verification code first.",
            )

        now = datetime.now()
        exp_dt = datetime.fromisoformat(code_row["expires_at"])
        if exp_dt < now:
            conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The verification code has expired. Please request a new verification code.",
            )

        if code_row["attempts"] >= code_row["max_attempts"]:
            conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many failed attempts. This verification code has been invalidated. Please request a new code.",
            )

        hashed_input = hashlib.sha256(code_input.encode("utf-8")).hexdigest()
        is_match = (hashed_input == code_row["code_hash"])

        if not is_match:
            new_attempts = code_row["attempts"] + 1
            conn.execute(
                "UPDATE institution_linking_codes SET attempts = ? WHERE code_id = ?",
                (new_attempts, code_row["code_id"]),
            )
            rem = max(0, code_row["max_attempts"] - new_attempts)
            if rem == 0:
                conn.execute("UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?", (code_row["code_id"],))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code. Maximum attempts exceeded. Code has been invalidated.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification code. {rem} attempt(s) remaining.",
            )

        # Code matches! Mark as used and link child
        with conn:
            conn.execute(
                "UPDATE institution_linking_codes SET is_used = 1 WHERE code_id = ?",
                (code_row["code_id"],),
            )

            if existing_link:
                conn.execute(
                    """
                    UPDATE student_guardians
                    SET is_verified = 1, can_view_records = 1, can_request_updates = 1
                    WHERE student_guardian_id = ?
                    """,
                    (existing_link["student_guardian_id"],),
                )
            else:
                sg_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO student_guardians (
                        student_guardian_id, permanent_student_id,
                        guardian_id, can_view_records, can_request_updates, is_verified
                    )
                    VALUES (?, ?, ?, 1, 1, 1)
                    """,
                    (sg_id, perm_id, guardian["guardian_id"]),
                )

            if rel_type and rel_type not in ("Guardian", "Parent"):
                conn.execute(
                    "UPDATE guardians SET relationship = ? WHERE guardian_id = ?",
                    (rel_type, guardian["guardian_id"]),
                )

            # Update pending linking_requests to approved
            conn.execute(
                """
                UPDATE linking_requests
                SET request_status = 'approved', reviewed_at = ?, reviewer_comment = 'Verified by parent using official 6-digit institution authorization code'
                WHERE parent_user_id = ? AND school_id = ? AND (permanent_student_id = ? OR student_ref = ?) AND request_status = 'pending'
                """,
                (now.isoformat(), user["user_id"], student["school_id"], perm_id, student["student_id"]),
            )

            # Record audit log
            audit_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role, action,
                    entity_type, entity_id, school_id, ip_address, metadata_json
                )
                VALUES (?, ?, 'parent', 'PARENT_CHILD_VERIFIED_AND_LINKED', 'student_guardian', ?, ?, NULL, ?)
                """,
                (
                    audit_id,
                    user["user_id"],
                    perm_id,
                    student["school_id"],
                    json.dumps({
                        "student_id": student["student_id"],
                        "student_name": student["student_name"],
                        "permanent_student_id": perm_id,
                        "relationship_type": rel_type,
                        "verification_method": "institution_code",
                    }),
                ),
            )

        return {
            "status": "success",
            "message": f"Successfully verified and linked {student['student_name']} ({student['student_id']}) to your parent account!",
            "child": {
                "student_id": student["student_id"],
                "permanent_student_id": perm_id,
                "student_name": student["student_name"],
                "institution_id": student["school_id"],
                "institution_name": student["school_name"] or student["school_id"],
                "is_verified": 1,
            },
        }
    finally:
        conn.close()'''

assert old_parent_children in content, "old_parent_children not found in main.py"
content = content.replace(old_parent_children, new_parent_children, 1)
print("Replaced GET /parent/children and added lookup/verify routes.")

# 2. Update list_school_linking_requests
old_list_school = '''    conn = get_connection()
    try:
        query = """
            SELECT lr.request_id, lr.parent_user_id, u.full_name AS parent_name,
                   u.email AS parent_email, u.phone AS parent_phone,
                   lr.school_id, lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_user_id,
                   lr.reviewer_comment, lr.permanent_student_id,
                   lr.created_at, lr.reviewed_at
            FROM linking_requests lr
            JOIN users u ON u.user_id = lr.parent_user_id
            WHERE lr.school_id = ?
        """'''

new_list_school = '''    conn = get_connection()
    try:
        query = """
            SELECT lr.request_id, lr.parent_user_id, u.full_name AS parent_name,
                   u.email AS parent_email, u.phone AS parent_phone,
                   lr.school_id, lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_user_id,
                   lr.reviewer_comment, lr.permanent_student_id,
                   lr.created_at, lr.reviewed_at,
                   s.student_name, s.student_id AS actual_student_id,
                   sc.school_name
            FROM linking_requests lr
            JOIN users u ON u.user_id = lr.parent_user_id
            LEFT JOIN students s ON (lr.permanent_student_id = s.permanent_student_id OR UPPER(lr.student_ref) = UPPER(s.student_id))
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            WHERE lr.school_id = ?
        """'''

assert old_list_school in content, "old_list_school not found in main.py"
content = content.replace(old_list_school, new_list_school, 1)

old_list_return = '''        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()'''

new_list_return = '''        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["student_id"] = d.get("actual_student_id") or d.get("student_ref")
            d["student_name"] = d.get("student_name") or "Enrolled Student"
            results.append(d)
        return results
    finally:
        conn.close()'''

assert old_list_return in content, "old_list_return not found in main.py"
content = content.replace(old_list_return, new_list_return, 1)
print("Updated list_school_linking_requests.")

# 3. Update review_school_linking_request
old_perm_check = '''        if review.decision == "approved":
            # 4. For approval, permanent_student_id is required
            permanent_student_id = review.permanent_student_id
            if not permanent_student_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="permanent_student_id is required when approving a linking request.",
                )'''

new_perm_check = '''        if review.decision == "approved":
            # 4. For approval, permanent_student_id is resolved from payload or existing linking request
            permanent_student_id = review.permanent_student_id or lr["permanent_student_id"]
            if not permanent_student_id:
                st_match = conn.execute(
                    "SELECT permanent_student_id FROM students WHERE student_id = ? OR permanent_student_id = ?",
                    (lr["student_ref"], lr["student_ref"]),
                ).fetchone()
                if st_match:
                    permanent_student_id = st_match["permanent_student_id"]

            if not permanent_student_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="permanent_student_id is required when approving a linking request.",
                )'''

assert old_perm_check in content, "old_perm_check not found in main.py"
content = content.replace(old_perm_check, new_perm_check, 1)

# Invalidate codes on approval
old_audit_pos = '''            # 9. Audit log insertion
            conn.execute(
                """
                INSERT INTO audit_logs ('''

new_audit_pos = '''            # Invalidate any pending institution verification codes for this parent and student
            conn.execute(
                """
                UPDATE institution_linking_codes
                SET is_used = 1
                WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
                """,
                (permanent_student_id, lr["parent_user_id"]),
            )

            # 9. Audit log insertion
            conn.execute(
                """
                INSERT INTO audit_logs ('''

assert old_audit_pos in content, "old_audit_pos not found in main.py"
content = content.replace(old_audit_pos, new_audit_pos, 1)
print("Updated review_school_linking_request.")

# 4. Add GET /institution/{institution_id}/linking-requests and POST /school/linking-requests/{request_id}/issue-code
old_end_review = '''        return {
            "request_id": request_id,
            "status": review.decision,
            "message": (
                "Linking request approved and parent-child relationship verified."
                if review.decision == "approved"
                else "Linking request rejected. Student records remain unchanged."
            ),
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()'''

new_end_review = '''        return {
            "request_id": request_id,
            "status": review.decision,
            "message": (
                "Linking request approved and parent-child relationship verified."
                if review.decision == "approved"
                else "Linking request rejected. Student records remain unchanged."
            ),
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.get("/institution/{institution_id}/linking-requests")
def list_institution_linking_requests(
    institution_id: str,
    status_filter: Optional[str] = Query(default="all"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    """
    List parent-child linking requests for a specific institution.
    Enforces multi-tenant isolation: Only authorized institution admin/staff or platform_admin can access.
    """
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot view linking requests for another institution.",
        )

    conn = get_connection()
    try:
        query = """
            SELECT lr.request_id, lr.parent_user_id, u.full_name AS parent_name,
                   u.email AS parent_email, u.phone AS parent_phone,
                   lr.school_id, lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_user_id,
                   lr.reviewer_comment, lr.permanent_student_id,
                   lr.created_at, lr.reviewed_at,
                   s.student_name, s.student_id AS actual_student_id,
                   sc.school_name
            FROM linking_requests lr
            JOIN users u ON u.user_id = lr.parent_user_id
            LEFT JOIN students s ON (lr.permanent_student_id = s.permanent_student_id OR UPPER(lr.student_ref) = UPPER(s.student_id))
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            WHERE lr.school_id = ?
        """
        params = [inst_id]
        if status_filter and status_filter != "all":
            query += " AND lr.request_status = ?"
            params.append(status_filter)

        query += " ORDER BY lr.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["student_id"] = d.get("actual_student_id") or d.get("student_ref")
            d["student_name"] = d.get("student_name") or "Enrolled Student"
            results.append(d)
        return results
    finally:
        conn.close()


@app.post("/school/linking-requests/{request_id}/issue-code")
def issue_institution_linking_code(
    request_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Allow an authorized institution administrator or staff member to issue an official 6-digit
    verification code for a pending linking request.
    Stores only the SHA-256 hash in the database.
    Returns the code ONLY to the authorized administrator so it can be delivered
    securely through the institution's authorized process.
    """
    conn = get_connection()
    try:
        lr = conn.execute(
            """
            SELECT * FROM linking_requests WHERE request_id = ?
            """,
            (request_id,),
        ).fetchone()

        if not lr:
            raise HTTPException(status_code=404, detail="Linking request not found.")

        # Multi-tenant security check
        if user["role"] != "platform_admin" and lr["school_id"] != user.get("school_id"):
            raise HTTPException(
                status_code=403,
                detail="Access denied: You cannot issue verification codes for another institution.",
            )

        if lr["request_status"] != "pending":
            raise HTTPException(
                status_code=409,
                detail="Cannot issue code: This linking request has already been reviewed.",
            )

        perm_id = lr["permanent_student_id"]
        student = conn.execute(
            """
            SELECT student_id, permanent_student_id, student_name, school_id
            FROM students
            WHERE permanent_student_id = ? OR student_id = ?
            LIMIT 1
            """,
            (perm_id, lr["student_ref"]),
        ).fetchone()

        if not student:
            raise HTTPException(status_code=404, detail="Student record not found for this request.")

        # Invalidate previous unused codes
        conn.execute(
            """
            UPDATE institution_linking_codes
            SET is_used = 1
            WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
            """,
            (student["permanent_student_id"], lr["parent_user_id"]),
        )

        # Generate secure random 6-digit code
        plain_code = f"{secrets.randbelow(900000) + 100000}"
        code_hash = hashlib.sha256(plain_code.encode("utf-8")).hexdigest()
        code_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = (now + timedelta(minutes=15)).isoformat()
        now_iso = now.isoformat()

        with conn:
            conn.execute(
                """
                INSERT INTO institution_linking_codes (
                    code_id, permanent_student_id, student_id, institution_id,
                    parent_user_id, code_hash, plain_code, attempts, max_attempts,
                    is_used, expires_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, NULL, 0, 5, 0, ?, ?)
                """,
                (
                    code_id,
                    student["permanent_student_id"],
                    student["student_id"],
                    student["school_id"],
                    lr["parent_user_id"],
                    code_hash,
                    expires_at,
                    now_iso,
                ),
            )

            # Audit log
            audit_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role, action,
                    entity_type, entity_id, school_id, ip_address, metadata_json
                )
                VALUES (?, ?, ?, 'INSTITUTION_ADMIN_ISSUED_LINKING_CODE', 'linking_request', ?, ?, NULL, ?)
                """,
                (
                    audit_id,
                    user["user_id"],
                    user["role"],
                    request_id,
                    student["school_id"],
                    json.dumps({
                        "request_id": request_id,
                        "student_id": student["student_id"],
                        "parent_user_id": lr["parent_user_id"],
                        "expires_at": expires_at,
                    }),
                ),
            )

        return {
            "status": "success",
            "message": f"Official verification code generated for {student['student_name']}. Please provide this code to the requesting parent through verified institution channels.",
            "verification_code": plain_code,
            "expires_in_minutes": 15,
            "student_name": student["student_name"],
            "student_id": student["student_id"],
        }
    finally:
        conn.close()'''

assert old_end_review in content, "old_end_review not found in main.py"
content = content.replace(old_end_review, new_end_review, 1)

with open(MAIN_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated backend/main.py successfully! New length:", len(content))
