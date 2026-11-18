import re

path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Ensure base64 and os are imported
if "import base64" not in code:
    code = "import base64\nimport os\n" + code

# 2. Add Phase 5 Models
models_marker = "class ParentClarificationResponse(BaseModel):"
models_to_insert = """class Stage2SubmissionCreate(BaseModel):
    date_of_birth: str = Field(min_length=10, max_length=10) # YYYY-MM-DD
    gender: Literal["male", "female", "other"]
    blood_group: Optional[str] = None
    previous_institution_name: Optional[str] = None
    previous_institution_location: Optional[str] = None
    previous_standard_or_degree: Optional[str] = None
    previous_board: Optional[str] = None
    previous_marks_percentage: Optional[float] = None
    emergency_contact_name: str = Field(min_length=2, max_length=100)
    emergency_contact_phone: str = Field(min_length=10, max_length=15)
    custom_fields: Optional[dict] = None


class DocumentUploadPayload(BaseModel):
    document_type: str = Field(min_length=3, max_length=100)
    file_name: str = Field(min_length=3, max_length=255)
    file_data_base64: str = Field(min_length=10)
    mime_type: Optional[str] = "application/pdf"


class DocumentVerificationRequest(BaseModel):
    verification_status: Literal["verified", "rejected", "reupload_requested"]
    verification_notes: Optional[str] = None


class Stage2ReviewActionRequest(BaseModel):
    decision: Literal["detailed_review_completed", "stage2_correction_requested"]
    review_notes: Optional[str] = None

"""

if models_marker in code and "class Stage2SubmissionCreate" not in code:
    code = code.replace(models_marker, models_to_insert + "\n" + models_marker)

# 3. Add Phase 5 Endpoints before notification routes
notif_marker = '@app.get("/notifications")'
phase5_endpoints = '''
# -------------------------------------------------------------
# PHASE 5: STAGE 2 DETAILED ADMISSION & DOCUMENT VERIFICATION
# -------------------------------------------------------------

@app.get("/admissions/applications/{application_id}/stage2-eligibility")
def get_stage2_eligibility(
    application_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Checks if application is approved in Stage 1 and returns Stage 2 eligibility,
    required documents checklist, and existing submission data.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            """
            SELECT a.*, s.school_name AS institution_name, s.school_type
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            WHERE a.application_id = ?
            """,
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        app_data = dict(app_row)
        valid_stage2_statuses = (
            "approved", "stage2_submitted", "documents_uploaded",
            "under_detailed_review", "detailed_review_completed",
            "final_admission_confirmed", "enrolled"
        )
        if app_data["status"] not in valid_stage2_statuses:
            raise HTTPException(
                403,
                f"Stage 2 detailed admission form is strictly locked. Current status is '{app_data['status']}'. Stage 1 preliminary approval by the institution desk is required."
            )

        # Dynamic document checklist
        level = app_data.get("education_level", "school")
        std = app_data.get("requested_standard")
        checklist = [
            {"document_type": "birth_certificate", "label": "Birth Certificate / Government Proof of Age", "is_mandatory": True},
            {"document_type": "passport_photo", "label": "Recent Passport Size Photograph of Applicant", "is_mandatory": True},
        ]
        if level != "school" or (std and std > 1):
            checklist.extend([
                {"document_type": "previous_marks_card", "label": "Previous Standard / Qualifying Marks Card", "is_mandatory": True},
                {"document_type": "transfer_certificate", "label": "Official School / College Transfer Certificate (TC)", "is_mandatory": True},
            ])
        checklist.extend([
            {"document_type": "caste_certificate", "label": "Caste / Social Category Certificate (if claiming quota)", "is_mandatory": False},
            {"document_type": "income_certificate", "label": "Annual Income Certificate (for Fee Concessions)", "is_mandatory": False},
        ])

        # Fetch existing stage 2 submission if any
        sub_row = conn.execute(
            "SELECT * FROM admission_detailed_submissions WHERE application_id = ?",
            (application_id,)
        ).fetchone()

        # Fetch uploaded documents
        docs = conn.execute(
            "SELECT document_id, application_id, document_type, file_name, file_size_bytes, mime_type, verification_status, uploaded_at, verified_at, verification_notes FROM admission_documents WHERE application_id = ?",
            (application_id,)
        ).fetchall()

        return {
            "application_id": application_id,
            "status": app_data["status"],
            "is_eligible": True,
            "applicant_name": app_data["applicant_name"],
            "institution_id": app_data["institution_id"],
            "institution_name": app_data["institution_name"],
            "education_level": app_data["education_level"],
            "requested_standard": app_data.get("requested_standard"),
            "combination_code": app_data.get("combination_code"),
            "requested_program_id": app_data.get("requested_program_id"),
            "required_documents": checklist,
            "stage2_submission": dict(sub_row) if sub_row else None,
            "uploaded_documents": [dict(d) for d in docs]
        }
    finally:
        conn.close()


@app.post("/admissions/applications/{application_id}/stage2-submit")
def submit_stage2_detailed_admission(
    application_id: str,
    payload: Stage2SubmissionCreate,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Submits detailed student demographic information, medical details,
    and previous schooling records for Stage 2.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, status, applicant_name, parent_user_id, parent_phone FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        valid_entry_statuses = ("approved", "stage2_submitted", "documents_uploaded", "stage2_correction_requested")
        if app_row["status"] not in valid_entry_statuses:
            raise HTTPException(
                400,
                f"Cannot submit Stage 2 form for application in '{app_row['status']}' status. Stage 1 approval required."
            )

        sub_id = str(uuid.uuid4())
        custom_json = json.dumps(payload.custom_fields) if payload.custom_fields else None

        conn.execute(
            """
            INSERT OR REPLACE INTO admission_detailed_submissions (
                submission_id, application_id, date_of_birth, gender, blood_group,
                previous_institution_name, previous_institution_location,
                previous_standard_or_degree, previous_board, previous_marks_percentage,
                emergency_contact_name, emergency_contact_phone, custom_fields_json,
                status, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted', CURRENT_TIMESTAMP)
            """,
            (
                sub_id, application_id, payload.date_of_birth, payload.gender,
                payload.blood_group, payload.previous_institution_name,
                payload.previous_institution_location, payload.previous_standard_or_degree,
                payload.previous_board, payload.previous_marks_percentage,
                payload.emergency_contact_name, payload.emergency_contact_phone,
                custom_json
            )
        )

        prev_status = app_row["status"]
        new_status = "stage2_submitted" if prev_status == "approved" else prev_status
        conn.execute(
            "UPDATE admission_applications SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (new_status, application_id)
        )

        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, ?, ?, 'Stage 2 detailed demographic and academic records dossier submitted.')
            """,
            (str(uuid.uuid4()), application_id, prev_status, new_status, current_user.get("user_id") if current_user else "parent")
        )

        conn.execute(
            """
            INSERT INTO portal_notifications (notification_id, recipient_role, institution_id, application_id, title, message, action_url)
            VALUES (?, 'school_admin', ?, ?, 'Stage 2 Dossier Submitted', ?, ?)
            """,
            (
                str(uuid.uuid4()), app_row["institution_id"], application_id,
                f"Stage 2 detailed submission received for {app_row['applicant_name']}.",
                f"/staff?tab=admissions&app_id={application_id}"
            )
        )

        conn.commit()
        return {
            "status": "success",
            "application_id": application_id,
            "submission_id": sub_id,
            "application_status": new_status,
            "message": "Stage 2 detailed admission dossier submitted successfully. Please proceed with mandatory document uploads."
        }
    finally:
        conn.close()


@app.post("/admissions/applications/{application_id}/documents")
def upload_stage2_document(
    application_id: str,
    payload: DocumentUploadPayload,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Securely uploads a supporting document for Stage 2 admission verification.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, status, applicant_name FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Admission application not found.")

        # Decode base64 file data
        try:
            file_bytes = base64.b64decode(payload.file_data_base64)
        except Exception:
            raise HTTPException(400, "Invalid base64 document content.")

        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Document size exceeds the 10 MB limit.")

        doc_id = str(uuid.uuid4())
        safe_filename = "".join(c for c in payload.file_name if c.isalnum() or c in "._- ")
        if not safe_filename:
            safe_filename = f"{payload.document_type}.pdf"

        # Write to secure uploads directory
        upload_dir = os.path.join("/app", "data", "uploads", "admissions", application_id)
        os.makedirs(upload_dir, exist_ok=True)
        file_disk_path = os.path.join(upload_dir, f"{doc_id}_{safe_filename}")
        with open(file_disk_path, "wb") as f_out:
            f_out.write(file_bytes)

        # Record in database
        conn.execute(
            """
            INSERT INTO admission_documents (
                document_id, application_id, document_type, file_name,
                file_path, file_size_bytes, mime_type, verification_status, uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
            """,
            (
                doc_id, application_id, payload.document_type, safe_filename,
                file_disk_path, len(file_bytes), payload.mime_type
            )
        )

        # Update application status to documents_uploaded if in stage2_submitted
        if app_row["status"] in ("approved", "stage2_submitted"):
            conn.execute(
                "UPDATE admission_applications SET status = 'documents_uploaded', updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
                (application_id,)
            )

        conn.commit()
        return {
            "status": "uploaded",
            "document_id": doc_id,
            "application_id": application_id,
            "document_type": payload.document_type,
            "file_name": safe_filename,
            "file_size_bytes": len(file_bytes),
            "verification_status": "pending"
        }
    finally:
        conn.close()


@app.get("/admissions/applications/{application_id}/documents")
def get_stage2_documents(
    application_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Returns list of uploaded documents and their verification status for an application.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT document_id, application_id, document_type, file_name, file_size_bytes,
                   mime_type, verification_status, uploaded_at, verified_at, verification_notes
            FROM admission_documents
            WHERE application_id = ?
            ORDER BY uploaded_at ASC
            """,
            (application_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/documents/{document_id}/verify")
def verify_admission_document(
    application_id: str,
    document_id: str,
    payload: DocumentVerificationRequest,
    user: dict = Depends(require_school_staff),
):
    """
    Authorized institution staff verifies or rejects a Stage 2 supporting document.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        doc_row = conn.execute(
            """
            SELECT d.document_id, d.document_type, d.file_name, a.institution_id, a.parent_user_id
            FROM admission_documents d
            JOIN admission_applications a ON a.application_id = d.application_id
            WHERE d.document_id = ? AND d.application_id = ? AND a.institution_id = ?
            """,
            (document_id, application_id, school_id)
        ).fetchone()
        if not doc_row:
            raise HTTPException(404, "Document not found or unauthorized for this institution.")

        conn.execute(
            """
            UPDATE admission_documents
            SET verification_status = ?, verified_by_user_id = ?, verified_at = CURRENT_TIMESTAMP, verification_notes = ?
            WHERE document_id = ?
            """,
            (payload.verification_status, user["user_id"], payload.verification_notes, document_id)
        )

        # Notify parent if rejected or reupload requested
        if payload.verification_status in ("rejected", "reupload_requested") and doc_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Document Verification Update', ?, ?)
                """,
                (
                    str(uuid.uuid4()), doc_row["parent_user_id"], school_id, application_id,
                    f"Document '{doc_row['file_name']}' ({doc_row['document_type']}) was marked as '{payload.verification_status}': {payload.verification_notes or 'Please re-upload a clear copy.'}",
                    f"/parent?tab=admissions&app_id={application_id}"
                )
            )

        conn.commit()
        return {
            "status": "updated",
            "document_id": document_id,
            "verification_status": payload.verification_status,
            "verification_notes": payload.verification_notes
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/stage2-review")
def review_stage2_dossier(
    application_id: str,
    payload: Stage2ReviewActionRequest,
    user: dict = Depends(require_school_staff),
):
    """
    School staff marks detailed Stage 2 review as completed or requests correction.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")

        # Check document verification status if completing review
        if payload.decision == "detailed_review_completed":
            unverified = conn.execute(
                "SELECT COUNT(*) FROM admission_documents WHERE application_id = ? AND verification_status != 'verified'",
                (application_id,)
            ).fetchone()[0]
            if unverified > 0:
                raise HTTPException(400, f"Cannot complete detailed review: {unverified} supporting document(s) have not been verified.")

        prev_status = app_row["status"]
        new_status = payload.decision
        conn.execute(
            "UPDATE admission_applications SET status = ?, reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (new_status, user["user_id"], application_id)
        )

        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, new_status, user["user_id"], payload.review_notes or "Stage 2 detailed dossier review completed.")
        )

        if app_row["parent_user_id"]:
            msg = "Your Stage 2 dossier and documents have been fully verified. Pending final admission confirmation." if payload.decision == "detailed_review_completed" else f"Correction requested on Stage 2 dossier: {payload.review_notes}"
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Stage 2 Review Update', ?, ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, msg, f"/parent?tab=admissions&app_id={application_id}")
            )

        conn.commit()
        return {"status": new_status, "application_id": application_id}
    finally:
        conn.close()

'''

if notif_marker in code and "@app.get(\"/admissions/applications/{application_id}/stage2-eligibility\")" not in code:
    code = code.replace(notif_marker, phase5_endpoints + "\n" + notif_marker)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("backend/main.py successfully patched with Phase 5 endpoints!")
