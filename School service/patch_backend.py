import re

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# 1. Update ParentLinkingRequestCreate and add ParentClarificationResponse
old_model_block = """class ParentLinkingRequestCreate(BaseModel):
    school_id: str = Field(min_length=1, max_length=50)
    student_ref: str = Field(min_length=1, max_length=100)
    relationship_type: str = Field(min_length=2, max_length=50)
    verification_doc_id: Optional[str] = Field(default=None, max_length=100)
    additional_notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("school_id")
    @classmethod
    def validate_school_id(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("School ID cannot be empty.")
        return s

    @field_validator("student_ref")
    @classmethod
    def validate_student_ref(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Student reference cannot be empty.")
        return s

    @field_validator("relationship_type")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Relationship type cannot be empty.")
        return s


class ParentLinkingRequestResponse(BaseModel):
    request_id: str
    school_id: str
    student_ref: str
    relationship_type: str
    request_status: str
    message: str"""

new_model_block = """class ParentLinkingRequestCreate(BaseModel):
    school_id: Optional[str] = Field(default=None, max_length=50)
    student_ref: Optional[str] = Field(default=None, max_length=100)
    student_id: Optional[str] = Field(default=None, max_length=100)
    permanent_student_id: Optional[str] = Field(default=None, max_length=100)
    relationship_type: str = Field(min_length=2, max_length=50)
    verification_doc_id: Optional[str] = Field(default=None, max_length=100)
    additional_notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("relationship_type")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Relationship type cannot be empty.")
        return s


class ParentClarificationResponse(BaseModel):
    response_notes: Optional[str] = Field(default=None, max_length=2000)
    parent_response: Optional[str] = Field(default=None, max_length=2000)


class ParentLinkingRequestResponse(BaseModel):
    request_id: str
    school_id: Optional[str] = None
    student_ref: Optional[str] = None
    relationship_type: str
    request_status: str
    message: str"""

if old_model_block in content:
    content = content.replace(old_model_block, new_model_block, 1)
    print("Replaced ParentLinkingRequestCreate successfully.")
else:
    print("WARNING: old_model_block not found exactly.")

# 2. Update create_parent_linking_request
old_create_fn = """@app.post(
    "/parent/linking-requests",
    response_model=ParentLinkingRequestResponse,
    status_code=201,
)
def create_parent_linking_request(
    payload: ParentLinkingRequestCreate,
    user: dict = Depends(require_parent),
):
    \"\"\"
    Submit a request to link a student to this parent account.
    Does NOT create a student_guardians relationship during submission.
    Does NOT grant access to student records.
    \"\"\"
    school_id = payload.school_id.strip()
    student_ref = payload.student_ref.strip()
    relationship_type = payload.relationship_type.strip()
    verification_doc_id = (
        payload.verification_doc_id.strip()
        if payload.verification_doc_id and payload.verification_doc_id.strip()
        else None
    )
    additional_notes = (
        payload.additional_notes.strip()
        if payload.additional_notes and payload.additional_notes.strip()
        else None
    )

    conn = get_connection()
    try:
        # Verify guardian profile exists for authenticated parent
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No guardian profile is linked to this account.",
            )

        # Validate that the school exists
        school = conn.execute(
            "SELECT school_id, school_name FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School not found.",
            )

        # Check for existing pending request for same parent, school, and student_ref
        existing_pending = conn.execute(
            \"\"\"
            SELECT request_id
            FROM linking_requests
            WHERE parent_user_id = ?
              AND school_id = ?
              AND student_ref = ?
              AND request_status = 'pending'
            \"\"\",
            (user["user_id"], school_id, student_ref),
        ).fetchone()

        if existing_pending is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A pending linking request already exists for this student and school.",
            )

        request_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())

        try:
            with conn:
                conn.execute(
                    \"\"\"
                    INSERT INTO linking_requests (
                        request_id, parent_user_id, school_id,
                        student_ref, relationship_type,
                        verification_doc_id, additional_notes,
                        request_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                    \"\"\",
                    (
                        request_id,
                        user["user_id"],
                        school_id,
                        student_ref,
                        relationship_type,
                        verification_doc_id,
                        additional_notes,
                    ),
                )

                conn.execute(
                    \"\"\"
                    INSERT INTO audit_logs (
                        audit_id, actor_user_id, actor_role,
                        action, entity_type, entity_id,
                        school_id, ip_address, metadata_json
                    )
                    VALUES (?, ?, 'parent', 'LINKING_REQUEST_SUBMITTED', 'linking_request', ?, ?, NULL, ?)
                    \"\"\",
                    (
                        audit_id,
                        user["user_id"],
                        request_id,
                        school_id,
                        json.dumps({
                            "student_ref": student_ref,
                            "relationship_type": relationship_type,
                            "school_id": school_id,
                        }),
                    ),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A pending linking request already exists for this student and school.",
            )

        return {
            "request_id": request_id,
            "school_id": school_id,
            "student_ref": student_ref,
            "relationship_type": relationship_type,
            "request_status": "pending",
            "message": "Student linking request submitted successfully. Pending school verification.",
        }
    finally:
        conn.close()"""

new_create_fn = """@app.post(
    "/parent/linking-requests",
    response_model=ParentLinkingRequestResponse,
    status_code=201,
)
def create_parent_linking_request(
    payload: ParentLinkingRequestCreate,
    user: dict = Depends(require_parent),
):
    \"\"\"
    Submit a request to link a student to this parent account.
    Does NOT create a student_guardians relationship during submission.
    Does NOT grant access to student records.
    \"\"\"
    st_ref = (payload.student_ref or payload.student_id or "").strip()
    if not st_ref:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Student ID / Reference is required.",
        )

    relationship_type = payload.relationship_type.strip()
    verification_doc_id = (
        payload.verification_doc_id.strip()
        if payload.verification_doc_id and payload.verification_doc_id.strip()
        else None
    )
    additional_notes = (
        payload.additional_notes.strip()
        if payload.additional_notes and payload.additional_notes.strip()
        else None
    )

    conn = get_connection()
    try:
        # Verify or auto-create guardian profile for authenticated parent
        guardian = get_parent_guardian(conn, user["user_id"])
        if guardian is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No guardian profile is linked to this account.",
            )

        # Resolve student record from live database
        student = conn.execute(
            \"\"\"
            SELECT s.student_id, s.permanent_student_id, s.student_name, s.school_id, sc.school_name
            FROM students s
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            WHERE UPPER(s.student_id) = UPPER(?) OR s.permanent_student_id = ?
            \"\"\",
            (st_ref, st_ref),
        ).fetchone()

        if student:
            actual_student_id = student["student_id"]
            perm_id = student["permanent_student_id"]
            st_name = student["student_name"]
            inst_id = student["school_id"]
            inst_name = student["school_name"] or inst_id
        else:
            actual_student_id = st_ref
            perm_id = payload.permanent_student_id
            st_name = st_ref
            inst_id = (payload.school_id or "").strip()
            inst_name = inst_id

        if not inst_id and payload.school_id:
            inst_id = payload.school_id.strip()

        if not inst_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not resolve educational institution for student reference '{st_ref}'.",
            )

        # Validate institution exists
        school = conn.execute(
            "SELECT school_id, school_name FROM schools WHERE school_id = ?",
            (inst_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found.",
            )
        inst_name = school["school_name"]

        # Prevent requesting if already verified
        if perm_id and guardian:
            already_linked = conn.execute(
                \"\"\"
                SELECT student_guardian_id FROM student_guardians
                WHERE guardian_id = ? AND permanent_student_id = ? AND is_verified = 1
                \"\"\",
                (guardian["guardian_id"], perm_id),
            ).fetchone()
            if already_linked:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You are already verified as an authorized guardian for this student.",
                )

        # Check for existing active linking request (pending, clarification_required, pending_review)
        existing_active = conn.execute(
            \"\"\"
            SELECT request_id, request_status
            FROM linking_requests
            WHERE parent_user_id = ?
              AND (
                  (permanent_student_id IS NOT NULL AND permanent_student_id = ?)
                  OR UPPER(student_ref) = UPPER(?)
              )
              AND request_status IN ('pending', 'clarification_required', 'pending_review')
            \"\"\",
            (user["user_id"], perm_id, actual_student_id),
        ).fetchone()

        if existing_active is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active linking request is already in progress ({existing_active['request_status']}). The institution will review and notify you of its decision.",
            )

        request_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())

        try:
            with conn:
                conn.execute(
                    \"\"\"
                    INSERT INTO linking_requests (
                        request_id, parent_user_id, school_id,
                        student_ref, permanent_student_id, relationship_type,
                        verification_doc_id, additional_notes,
                        request_status, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
                    \"\"\",
                    (
                        request_id,
                        user["user_id"],
                        inst_id,
                        actual_student_id,
                        perm_id,
                        relationship_type,
                        verification_doc_id,
                        additional_notes,
                    ),
                )

                # Send in-app notification to institution administrators
                notif_id = str(uuid.uuid4())
                conn.execute(
                    \"\"\"
                    INSERT INTO portal_notifications (
                        notification_id, recipient_role, institution_id,
                        title, message, action_url, related_record_type, related_record_id,
                        category, priority
                    )
                    VALUES (?, 'school_admin', ?, ?, ?, '/school/dashboard', 'linking_request', ?, 'guardian_verification', 'normal')
                    \"\"\",
                    (
                        notif_id,
                        inst_id,
                        "New Student Linking Request",
                        f"New parent-child verification request received for {st_name} (Student ID: {actual_student_id}).",
                        request_id,
                    ),
                )

                conn.execute(
                    \"\"\"
                    INSERT INTO audit_logs (
                        audit_id, actor_user_id, actor_role,
                        action, entity_type, entity_id,
                        school_id, ip_address, metadata_json
                    )
                    VALUES (?, ?, 'parent', 'LINKING_REQUEST_SUBMITTED', 'linking_request', ?, ?, NULL, ?)
                    \"\"\",
                    (
                        audit_id,
                        user["user_id"],
                        request_id,
                        inst_id,
                        json.dumps({
                            "student_ref": actual_student_id,
                            "permanent_student_id": perm_id,
                            "relationship_type": relationship_type,
                            "school_id": inst_id,
                        }),
                    ),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A linking request already exists for this student and institution.",
            )

        return {
            "request_id": request_id,
            "school_id": inst_id,
            "student_ref": actual_student_id,
            "relationship_type": relationship_type,
            "request_status": "pending",
            "message": f"Your request has been submitted successfully to {inst_name}. The institution will review and notify you of its decision.",
        }
    finally:
        conn.close()"""

if old_create_fn in content:
    content = content.replace(old_create_fn, new_create_fn, 1)
    print("Replaced create_parent_linking_request successfully.")
else:
    print("WARNING: old_create_fn not found exactly.")

# 3. Update list_parent_linking_requests and add respond_parent_linking_clarification
old_list_fn = """@app.get("/parent/linking-requests")
def list_parent_linking_requests(
    user: dict = Depends(require_parent),
):
    \"\"\"
    List only linking requests submitted by the authenticated parent.
    Does not expose private student records or other parents' requests.
    Ordered by created_at DESC.
    \"\"\"
    conn = get_connection()
    try:
        rows = conn.execute(
            \"\"\"
            SELECT lr.request_id, lr.school_id, sc.school_name,
                   lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_comment,
                   lr.created_at, lr.reviewed_at
            FROM linking_requests lr
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            WHERE lr.parent_user_id = ?
            ORDER BY lr.created_at DESC
            \"\"\",
            (user["user_id"],),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()"""

new_list_fn = """@app.get("/parent/linking-requests")
def list_parent_linking_requests(
    user: dict = Depends(require_parent),
):
    \"\"\"
    List only linking requests submitted by the authenticated parent.
    Does not expose private student records or other parents' requests.
    Returns complete student identity, institution, status, remarks, and clarification data.
    Ordered by created_at DESC.
    \"\"\"
    conn = get_connection()
    try:
        rows = conn.execute(
            \"\"\"
            SELECT lr.request_id, lr.school_id, sc.school_name, sc.school_type, sc.category,
                   lr.student_ref, lr.permanent_student_id, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_comment, lr.rejection_reason,
                   lr.parent_response, lr.clarification_requested_at, lr.clarification_responded_at,
                   lr.created_at, lr.reviewed_at,
                   s.student_name, s.student_id AS actual_student_id,
                   s.standard, s.section,
                   e.academic_year, e.stream AS enroll_stream,
                   ap.program_name
            FROM linking_requests lr
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            LEFT JOIN students s ON (lr.permanent_student_id = s.permanent_student_id OR UPPER(lr.student_ref) = UPPER(s.student_id))
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = sc.school_id
            WHERE lr.parent_user_id = ?
            GROUP BY lr.request_id
            ORDER BY lr.created_at DESC
            \"\"\",
            (user["user_id"],),
        ).fetchall()

        results = []
        for r in rows:
            d = dict(r)
            d["institution_id"] = d.get("school_id")
            d["institution_name"] = d.get("school_name") or d.get("school_id")
            d["institution_type"] = d.get("school_type") or d.get("category") or "Accredited Institution"
            d["student_id"] = d.get("actual_student_id") or d.get("student_ref")
            d["student_name"] = d.get("student_name") or d.get("student_ref")
            d["relationship"] = d.get("relationship_type")
            d["decision_date"] = d.get("reviewed_at")

            std = d.get("standard")
            sec = d.get("section") or "A"
            inst_type = str(d["institution_type"])
            if "PU" in inst_type or "College" in inst_type or "University" in inst_type:
                d["class_or_standard"] = f"Year {std}" if std is not None else "Year 1"
            else:
                d["class_or_standard"] = f"Standard {std}" if std is not None else "N/A"
            d["program_or_stream"] = d.get("program_name") or d.get("enroll_stream") or "General Academic"
            results.append(d)

        return results
    finally:
        conn.close()


@app.post("/parent/linking-requests/{request_id}/respond-clarification")
def respond_parent_linking_clarification(
    request_id: str,
    payload: ParentClarificationResponse,
    user: dict = Depends(require_parent),
):
    \"\"\"
    Submit a response to an institution's clarification request on a child linking request.
    Transitions request status from 'clarification_required' to 'pending_review'
    and notifies institution administrators.
    \"\"\"
    notes = (payload.response_notes or payload.parent_response or "").strip()
    if not notes:
        raise HTTPException(status_code=422, detail="Response notes cannot be empty.")

    conn = get_connection()
    try:
        lr = conn.execute(
            \"\"\"
            SELECT lr.*, s.student_name, sc.school_name
            FROM linking_requests lr
            LEFT JOIN students s ON (lr.permanent_student_id = s.permanent_student_id OR UPPER(lr.student_ref) = UPPER(s.student_id))
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            WHERE lr.request_id = ?
            \"\"\",
            (request_id,),
        ).fetchone()

        if not lr:
            raise HTTPException(status_code=404, detail="Linking request not found.")

        if lr["parent_user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied: You can only respond to your own linking requests.")

        if lr["request_status"] != "clarification_required":
            raise HTTPException(
                status_code=409,
                detail=f"This request does not currently require clarification (current status: {lr['request_status']}).",
            )

        with conn:
            conn.execute(
                \"\"\"
                UPDATE linking_requests
                SET request_status = 'pending_review',
                    parent_response = ?,
                    clarification_responded_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
                \"\"\",
                (notes, request_id),
            )

            # Insert notification for institution admin
            notif_id = str(uuid.uuid4())
            st_name = lr["student_name"] or lr["student_ref"]
            conn.execute(
                \"\"\"
                INSERT INTO portal_notifications (
                    notification_id, recipient_role, institution_id,
                    title, message, action_url, related_record_type, related_record_id,
                    category, priority
                )
                VALUES (?, 'school_admin', ?, ?, ?, '/school/dashboard', 'linking_request', ?, 'guardian_verification', 'normal')
                \"\"\",
                (
                    notif_id,
                    lr["school_id"],
                    "Parent Clarification Response Received",
                    f"Parent {user.get('full_name', 'Guardian')} responded to clarification request for {st_name} (ID: {lr['student_ref']}).",
                    request_id,
                ),
            )

        return {
            "request_id": request_id,
            "request_status": "pending_review",
            "message": "Clarification submitted successfully. Your request is now under institution review.",
            "parent_response": notes,
        }
    finally:
        conn.close()"""

if old_list_fn in content:
    content = content.replace(old_list_fn, new_list_fn, 1)
    print("Replaced list_parent_linking_requests and added respond_parent_linking_clarification successfully.")
else:
    print("WARNING: old_list_fn not found exactly.")

# 4. Update ReviewLinkingRequest model
old_review_model = """class ReviewLinkingRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    review_comment: str = Field(min_length=3, max_length=1000)
    permanent_student_id: Optional[str] = Field(default=None, max_length=100)
    confirm_student_match: bool = Field(
        default=False,
        description="Explicit confirmation when student_ref does not verbatim match student_id, student_name, or permanent_student_id"
    )

    @field_validator("review_comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 3:
            raise ValueError("Review comment must contain at least 3 non-whitespace characters.")
        return s

    @field_validator("permanent_student_id")
    @classmethod
    def validate_permanent_student_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            s = v.strip()
            return s if s else None
        return None"""

new_review_model = """class ReviewLinkingRequest(BaseModel):
    decision: Optional[str] = None
    action: Optional[str] = None
    review_comment: Optional[str] = Field(default=None, max_length=1000)
    remarks: Optional[str] = Field(default=None, max_length=1000)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    permanent_student_id: Optional[str] = Field(default=None, max_length=100)
    confirm_student_match: bool = Field(
        default=False,
        description="Explicit confirmation when student_ref does not verbatim match student_id, student_name, or permanent_student_id"
    )

    @field_validator("permanent_student_id")
    @classmethod
    def validate_permanent_student_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            s = v.strip()
            return s if s else None
        return None"""

if old_review_model in content:
    content = content.replace(old_review_model, new_review_model, 1)
    print("Replaced ReviewLinkingRequest successfully.")
else:
    print("WARNING: old_review_model not found exactly.")

# 5. Update list_school_linking_requests
old_school_list = """@app.get("/school/linking-requests")
def list_school_linking_requests(
    status_filter: Optional[Literal["pending", "approved", "rejected", "cancelled", "all"]] = Query(default="pending"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    List linking requests for the reviewer's assigned school.
    Defaults to pending requests.
    Does not expose sensitive credentials.
    \"\"\"
    if user["role"] not in ("school_staff", "school_admin", "platform_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff access required.",
        )
    if not user.get("school_id") and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )

    lim_val = limit if isinstance(limit, int) else (limit.default if hasattr(limit, "default") else 50)
    off_val = offset if isinstance(offset, int) else (offset.default if hasattr(offset, "default") else 0)
    stat_val = status_filter if isinstance(status_filter, str) else (status_filter.default if hasattr(status_filter, "default") else "pending")

    conn = get_connection()
    try:
        query = \"\"\"
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
        \"\"\"
        params = [user["school_id"]]

        if stat_val != "all":
            query += " AND lr.request_status = ?"
            params.append(stat_val)

        query += " ORDER BY lr.created_at ASC LIMIT ? OFFSET ?"
        params.extend([lim_val, off_val])

        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["student_id"] = d.get("actual_student_id") or d.get("student_ref")
            d["student_name"] = d.get("student_name") or "Enrolled Student"
            results.append(d)
        return results
    finally:
        conn.close()"""

new_school_list = """@app.get("/school/linking-requests")
def list_school_linking_requests(
    status_filter: Optional[str] = Query(default="pending"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    \"\"\"
    List linking requests for the reviewer's assigned school.
    Defaults to pending requests.
    Does not expose sensitive credentials.
    \"\"\"
    if user["role"] not in ("school_staff", "school_admin", "platform_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff access required.",
        )
    if not user.get("school_id") and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )

    lim_val = limit if isinstance(limit, int) else 50
    off_val = offset if isinstance(offset, int) else 0
    stat_val = status_filter if isinstance(status_filter, str) else "pending"

    conn = get_connection()
    try:
        query = \"\"\"
            SELECT lr.request_id, lr.parent_user_id, u.full_name AS parent_name,
                   u.email AS parent_email, u.phone AS parent_phone,
                   lr.school_id, lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_user_id,
                   lr.reviewer_comment, lr.rejection_reason, lr.parent_response,
                   lr.clarification_requested_at, lr.clarification_responded_at,
                   lr.permanent_student_id,
                   lr.created_at, lr.reviewed_at,
                   s.student_name, s.student_id AS actual_student_id,
                   s.standard, s.section,
                   sc.school_name, sc.school_type, sc.category,
                   e.academic_year, e.stream AS enroll_stream,
                   ap.program_name
            FROM linking_requests lr
            JOIN users u ON u.user_id = lr.parent_user_id
            LEFT JOIN students s ON (lr.permanent_student_id = s.permanent_student_id OR UPPER(lr.student_ref) = UPPER(s.student_id))
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = sc.school_id
            WHERE lr.school_id = ?
        \"\"\"
        params = [user["school_id"]]

        if stat_val != "all":
            query += " AND lr.request_status = ?"
            params.append(stat_val)

        query += " GROUP BY lr.request_id ORDER BY lr.created_at ASC LIMIT ? OFFSET ?"
        params.extend([lim_val, off_val])

        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["student_id"] = d.get("actual_student_id") or d.get("student_ref")
            d["student_name"] = d.get("student_name") or "Enrolled Student"
            std = d.get("standard")
            inst_type = str(d.get("school_type") or d.get("category") or "")
            if "PU" in inst_type or "College" in inst_type or "University" in inst_type:
                d["class_or_standard"] = f"Year {std}" if std is not None else "Year 1"
            else:
                d["class_or_standard"] = f"Standard {std}" if std is not None else "N/A"
            d["program_or_stream"] = d.get("program_name") or d.get("enroll_stream") or "General Academic"
            results.append(d)
        return results
    finally:
        conn.close()"""

if old_school_list in content:
    content = content.replace(old_school_list, new_school_list, 1)
    print("Replaced list_school_linking_requests successfully.")
else:
    print("WARNING: old_school_list not found exactly.")

# 6. Update review_school_linking_request
old_review_fn_start = """@app.post("/school/linking-requests/{request_id}/review")
def review_school_linking_request(
    request_id: str,
    review: ReviewLinkingRequest,
    user: dict = Depends(require_school_staff),
):"""

new_review_fn = """@app.post("/school/linking-requests/{request_id}/review")
def review_school_linking_request(
    request_id: str,
    review: ReviewLinkingRequest,
    user: dict = Depends(get_current_user),
):
    \"\"\"
    Review (Approve, Reject, or Request Clarification) a parent linking request within the reviewer's assigned school.
    Uses atomic transaction with immediate write lock.
    \"\"\"
    if user["role"] not in ("school_staff", "school_admin", "platform_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School staff or administrator access required.",
        )
    if not user.get("school_id") and user["role"] != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to a school.",
        )

    # Resolve action
    raw_action = (review.action or review.decision or "").lower().strip()
    if raw_action in ("approve", "approved", "accept", "accepted"):
        action = "approve"
    elif raw_action in ("reject", "rejected"):
        action = "reject"
    elif raw_action in ("clarify", "clarification_required", "request_clarification"):
        action = "clarify"
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid review action. Must be 'approve', 'reject', or 'clarify'.",
        )

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        # 1. Fetch linking request
        lr = conn.execute(
            \"\"\"
            SELECT lr.*, sc.school_name
            FROM linking_requests lr
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            WHERE lr.request_id = ?
            \"\"\",
            (request_id,),
        ).fetchone()

        if lr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linking request not found.",
            )

        # 2. Verify school authorization
        if user["role"] != "platform_admin" and lr["school_id"] != user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot review requests for another school.",
            )

        # 3. Check request is currently in reviewable status
        if lr["request_status"] not in ("pending", "pending_review", "clarification_required"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"This linking request cannot be reviewed in status '{lr['request_status']}'.",
            )

        audit_id = str(uuid.uuid4())
        actor_role = user["role"]
        school_name = lr["school_name"] or lr["school_id"]

        # Resolve student record
        perm_student_id = review.permanent_student_id or lr["permanent_student_id"]
        if not perm_student_id:
            st_match = conn.execute(
                "SELECT permanent_student_id, student_name, student_id FROM students WHERE student_id = ? OR permanent_student_id = ?",
                (lr["student_ref"], lr["student_ref"]),
            ).fetchone()
            if st_match:
                perm_student_id = st_match["permanent_student_id"]
                st_name = st_match["student_name"]
                st_id = st_match["student_id"]
            else:
                st_name = lr["student_ref"]
                st_id = lr["student_ref"]
        else:
            st_match = conn.execute(
                "SELECT student_name, student_id FROM students WHERE permanent_student_id = ?",
                (perm_student_id,),
            ).fetchone()
            st_name = st_match["student_name"] if st_match else lr["student_ref"]
            st_id = st_match["student_id"] if st_match else lr["student_ref"]

        if action == "approve":
            remarks = (review.remarks or review.review_comment or "Approved by institution administrator upon verification.").strip()

            if not perm_student_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="permanent_student_id is required when approving a linking request.",
                )

            # Verify student exists and belongs to this school
            student = conn.execute(
                \"\"\"
                SELECT student_id, permanent_student_id, school_id, student_name
                FROM students
                WHERE permanent_student_id = ?
                \"\"\",
                (perm_student_id,),
            ).fetchone()

            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found with the provided permanent_student_id.",
                )

            if user["role"] != "platform_admin" and student["school_id"] != user["school_id"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="The student does not belong to your school.",
                )

            # Resolve parent guardian record
            guardian = get_parent_guardian(conn, lr["parent_user_id"])
            if guardian is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No guardian profile found for the requesting parent.",
                )

            # Check if student_guardians relationship already exists
            existing_sg = conn.execute(
                \"\"\"
                SELECT student_guardian_id, can_view_records, can_request_updates, is_verified
                FROM student_guardians
                WHERE permanent_student_id = ? AND guardian_id = ?
                \"\"\",
                (perm_student_id, guardian["guardian_id"]),
            ).fetchone()

            if existing_sg is not None:
                conn.execute(
                    \"\"\"
                    UPDATE student_guardians
                    SET is_verified = 1, can_view_records = 1, can_request_updates = 1
                    WHERE student_guardian_id = ?
                    \"\"\",
                    (existing_sg["student_guardian_id"],),
                )
            else:
                sg_id = str(uuid.uuid4())
                conn.execute(
                    \"\"\"
                    INSERT INTO student_guardians (
                        student_guardian_id, permanent_student_id,
                        guardian_id, can_view_records,
                        can_request_updates, is_verified
                    )
                    VALUES (?, ?, ?, 1, 1, 1)
                    \"\"\",
                    (sg_id, perm_student_id, guardian["guardian_id"]),
                )

            # Update relationship in guardians table if provided
            if lr["relationship_type"]:
                conn.execute(
                    "UPDATE guardians SET relationship = ? WHERE guardian_id = ?",
                    (lr["relationship_type"], guardian["guardian_id"]),
                )

            # Update linking request status to approved
            conn.execute(
                \"\"\"
                UPDATE linking_requests
                SET request_status = 'approved',
                    reviewer_user_id = ?,
                    reviewer_comment = ?,
                    permanent_student_id = ?,
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
                \"\"\",
                (
                    user["user_id"],
                    remarks,
                    perm_student_id,
                    request_id,
                ),
            )

            # Invalidate any pending institution verification codes
            conn.execute(
                \"\"\"
                UPDATE institution_linking_codes
                SET is_used = 1
                WHERE permanent_student_id = ? AND parent_user_id = ? AND is_used = 0
                \"\"\",
                (perm_student_id, lr["parent_user_id"]),
            )

            # Insert parent in-app notification
            notif_id = str(uuid.uuid4())
            conn.execute(
                \"\"\"
                INSERT INTO portal_notifications (
                    notification_id, recipient_user_id, recipient_role, institution_id,
                    title, message, action_url, related_record_type, related_record_id,
                    category, priority
                )
                VALUES (?, ?, 'parent', ?, 'Child Linking Request Approved', ?, '/parent', 'linking_request', ?, 'guardian_verification', 'high')
                \"\"\",
                (
                    notif_id,
                    lr["parent_user_id"],
                    lr["school_id"],
                    f"Your request to link {st_name} (Student ID: {st_id}) has been approved by {school_name}. Your child is now verified and available in your dashboard.",
                    request_id,
                ),
            )

            # Audit log insertion
            conn.execute(
                \"\"\"
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role,
                    action, entity_type, entity_id,
                    school_id, ip_address, metadata_json
                )
                VALUES (?, ?, ?, 'LINKING_REQUEST_APPROVED', 'linking_request', ?, ?, NULL, ?)
                \"\"\",
                (
                    audit_id,
                    user["user_id"],
                    actor_role,
                    request_id,
                    user.get("school_id") or lr["school_id"],
                    json.dumps({
                        "decision": "approved",
                        "reviewer_comment": remarks,
                        "permanent_student_id": perm_student_id,
                        "parent_user_id": lr["parent_user_id"],
                        "student_ref": lr["student_ref"],
                    }),
                ),
            )

            conn.commit()
            return {
                "request_id": request_id,
                "status": "approved",
                "request_status": "approved",
                "message": f"Successfully approved linking request for {st_name}. Child records are now accessible to the parent.",
            }

        elif action == "reject":
            reason = (review.rejection_reason or "").strip()
            remarks = (review.remarks or review.review_comment or "").strip()
            if not reason and not remarks:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="A rejection reason is required when rejecting a linking request.",
                )
            if not reason:
                reason = remarks
            if not remarks:
                remarks = reason

            conn.execute(
                \"\"\"
                UPDATE linking_requests
                SET request_status = 'rejected',
                    rejection_reason = ?,
                    reviewer_user_id = ?,
                    reviewer_comment = ?,
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
                \"\"\",
                (
                    reason,
                    user["user_id"],
                    remarks,
                    request_id,
                ),
            )

            # Insert parent in-app notification
            notif_id = str(uuid.uuid4())
            conn.execute(
                \"\"\"
                INSERT INTO portal_notifications (
                    notification_id, recipient_user_id, recipient_role, institution_id,
                    title, message, action_url, related_record_type, related_record_id,
                    category, priority
                )
                VALUES (?, ?, 'parent', ?, 'Child Linking Request Rejected', ?, '/parent', 'linking_request', ?, 'guardian_verification', 'high')
                \"\"\",
                (
                    notif_id,
                    lr["parent_user_id"],
                    lr["school_id"],
                    f"Your request to link {st_name} (Student ID: {st_id}) was not approved by {school_name}. Reason: {reason}. Remarks: {remarks}",
                    request_id,
                ),
            )

            # Audit log insertion
            conn.execute(
                \"\"\"
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role,
                    action, entity_type, entity_id,
                    school_id, ip_address, metadata_json
                )
                VALUES (?, ?, ?, 'LINKING_REQUEST_REJECTED', 'linking_request', ?, ?, NULL, ?)
                \"\"\",
                (
                    audit_id,
                    user["user_id"],
                    actor_role,
                    request_id,
                    user.get("school_id") or lr["school_id"],
                    json.dumps({
                        "decision": "rejected",
                        "rejection_reason": reason,
                        "reviewer_comment": remarks,
                        "parent_user_id": lr["parent_user_id"],
                    }),
                ),
            )

            conn.commit()
            return {
                "request_id": request_id,
                "status": "rejected",
                "request_status": "rejected",
                "message": "Linking request rejected. Student records remain protected.",
            }

        elif action == "clarify":
            remarks = (review.remarks or review.review_comment or "").strip()
            if not remarks:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Remarks/instructions are required when requesting clarification from the parent.",
                )

            conn.execute(
                \"\"\"
                UPDATE linking_requests
                SET request_status = 'clarification_required',
                    reviewer_user_id = ?,
                    reviewer_comment = ?,
                    clarification_requested_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
                \"\"\",
                (
                    user["user_id"],
                    remarks,
                    request_id,
                ),
            )

            # Insert parent in-app notification
            notif_id = str(uuid.uuid4())
            conn.execute(
                \"\"\"
                INSERT INTO portal_notifications (
                    notification_id, recipient_user_id, recipient_role, institution_id,
                    title, message, action_url, related_record_type, related_record_id,
                    category, priority
                )
                VALUES (?, ?, 'parent', ?, 'Action Required: Clarification Requested', ?, '/parent', 'linking_request', ?, 'guardian_verification', 'high')
                \"\"\",
                (
                    notif_id,
                    lr["parent_user_id"],
                    lr["school_id"],
                    f"{school_name} has requested clarification regarding your linking request for {st_name}: {remarks}",
                    request_id,
                ),
            )

            # Audit log insertion
            conn.execute(
                \"\"\"
                INSERT INTO audit_logs (
                    audit_id, actor_user_id, actor_role,
                    action, entity_type, entity_id,
                    school_id, ip_address, metadata_json
                )
                VALUES (?, ?, ?, 'LINKING_REQUEST_CLARIFICATION_REQUESTED', 'linking_request', ?, ?, NULL, ?)
                \"\"\",
                (
                    audit_id,
                    user["user_id"],
                    actor_role,
                    request_id,
                    user.get("school_id") or lr["school_id"],
                    json.dumps({
                        "decision": "clarification_required",
                        "reviewer_comment": remarks,
                        "parent_user_id": lr["parent_user_id"],
                    }),
                ),
            )

            conn.commit()
            return {
                "request_id": request_id,
                "status": "clarification_required",
                "request_status": "clarification_required",
                "message": "Clarification requested. Parent has been notified.",
            }

    except HTTPException:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()"""

# We can replace review_school_linking_request from def review_school_linking_request to def list_institution_linking_requests
pattern = r'@app\.post\("/school/linking-requests/\{request_id\}/review"\)[\s\S]*?(?=\n@app\.get\("/institution/\{institution_id\}/linking-requests"\))'
match = re.search(pattern, content)
if match:
    content = content[:match.start()] + new_review_fn + "\n\n" + content[match.end():]
    print("Replaced review_school_linking_request successfully.")
else:
    print("WARNING: review_school_linking_request pattern not found.")

# 7. Update list_institution_linking_requests
inst_pattern = r'@app\.get\("/institution/\{institution_id\}/linking-requests"\)[\s\S]*?(?=\n@app\.post\("/school/linking-requests/\{request_id\}/issue-code"\))'
new_inst_list = """@app.get("/institution/{institution_id}/linking-requests")
def list_institution_linking_requests(
    institution_id: str,
    status_filter: Optional[str] = Query(default="all"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    \"\"\"
    List parent-child linking requests for a specific institution.
    Enforces multi-tenant isolation: Only authorized institution admin/staff or platform_admin can access.
    \"\"\"
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot view linking requests for another institution.",
        )

    conn = get_connection()
    try:
        query = \"\"\"
            SELECT lr.request_id, lr.parent_user_id, u.full_name AS parent_name,
                   u.email AS parent_email, u.phone AS parent_phone,
                   lr.school_id, lr.student_ref, lr.relationship_type,
                   lr.verification_doc_id, lr.additional_notes,
                   lr.request_status, lr.reviewer_user_id,
                   lr.reviewer_comment, lr.rejection_reason, lr.parent_response,
                   lr.clarification_requested_at, lr.clarification_responded_at,
                   lr.permanent_student_id,
                   lr.created_at, lr.reviewed_at,
                   s.student_name, s.student_id AS actual_student_id,
                   s.standard, s.section,
                   sc.school_name, sc.school_type, sc.category,
                   e.academic_year, e.stream AS enroll_stream,
                   ap.program_name
            FROM linking_requests lr
            JOIN users u ON u.user_id = lr.parent_user_id
            LEFT JOIN students s ON (lr.permanent_student_id = s.permanent_student_id OR UPPER(lr.student_ref) = UPPER(s.student_id))
            LEFT JOIN schools sc ON sc.school_id = lr.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = sc.school_id
            WHERE lr.school_id = ?
        \"\"\"
        params = [inst_id]
        if status_filter and status_filter != "all":
            query += " AND lr.request_status = ?"
            params.append(status_filter)

        query += " GROUP BY lr.request_id ORDER BY lr.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["student_id"] = d.get("actual_student_id") or d.get("student_ref")
            d["student_name"] = d.get("student_name") or "Enrolled Student"
            std = d.get("standard")
            inst_type = str(d.get("school_type") or d.get("category") or "")
            if "PU" in inst_type or "College" in inst_type or "University" in inst_type:
                d["class_or_standard"] = f"Year {std}" if std is not None else "Year 1"
            else:
                d["class_or_standard"] = f"Standard {std}" if std is not None else "N/A"
            d["program_or_stream"] = d.get("program_name") or d.get("enroll_stream") or "General Academic"
            results.append(d)
        return results
    finally:
        conn.close()"""

match_inst = re.search(inst_pattern, content)
if match_inst:
    content = content[:match_inst.start()] + new_inst_list + "\n\n" + content[match_inst.end():]
    print("Replaced list_institution_linking_requests successfully.")
else:
    print("WARNING: list_institution_linking_requests pattern not found.")

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to backend/main.py.")
