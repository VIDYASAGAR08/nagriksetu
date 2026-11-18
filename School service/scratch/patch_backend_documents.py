import sys
import os

backend_path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(backend_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacement 1 & 2: Enhancing document query in get_school_admission_application_detail and get_parent_admission_application_detail
old_docs_block = """        # Supporting Documents
        doc_rows = conn.execute(
            \"\"\"
            SELECT document_id, application_id, document_type, file_name, file_size_bytes,
                   mime_type, verification_status, uploaded_at, verified_by_user_id,
                   verified_at, verification_notes
            FROM admission_documents
            WHERE application_id = ?
            ORDER BY uploaded_at ASC
            \"\"\",
            (application_id,)
        ).fetchall()

        docs_list = []
        for dr in doc_rows:
            d = dict(dr)
            d["download_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            d["preview_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            docs_list.append(d)
        data["documents"] = docs_list
        data["total_documents_count"] = len(docs_list)
        data["verified_documents_count"] = sum(1 for d in docs_list if d.get("verification_status") == "verified")
        data["pending_documents_count"] = sum(1 for d in docs_list if d.get("verification_status") == "pending")
        data["reupload_documents_count"] = sum(1 for d in docs_list if d.get("verification_status") in ("reupload_requested", "rejected"))"""

new_docs_block = """        # Supporting Documents
        doc_rows = conn.execute(
            \"\"\"
            SELECT d.document_id, d.application_id, d.document_type, d.file_name, d.file_size_bytes,
                   d.mime_type, d.verification_status, d.uploaded_at, d.verified_by_user_id,
                   d.verified_at, d.verification_notes, u.full_name as verified_by_name
            FROM admission_documents d
            LEFT JOIN users u ON u.user_id = d.verified_by_user_id
            WHERE d.application_id = ?
            ORDER BY d.uploaded_at ASC
            \"\"\",
            (application_id,)
        ).fetchall()

        type_counts = {}
        for dr in doc_rows:
            dt = dr["document_type"]
            type_counts[dt] = type_counts.get(dt, 0) + 1

        type_current = {}
        docs_list = []
        for dr in doc_rows:
            d = dict(dr)
            dt = d["document_type"]
            type_current[dt] = type_current.get(dt, 0) + 1
            ver = type_current[dt]
            d["version"] = ver
            d["is_latest"] = (ver == type_counts[dt])
            d["download_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            d["preview_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            docs_list.append(d)
        data["documents"] = docs_list
        latest_docs = [d for d in docs_list if d.get("is_latest")]
        data["total_documents_count"] = len(latest_docs)
        data["verified_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "verified")
        data["pending_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "pending")
        data["rejected_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") == "rejected")
        data["reupload_documents_count"] = sum(1 for d in latest_docs if d.get("verification_status") in ("reupload_requested", "rejected"))"""

# Replacement 3: verify_admission_document
old_verify_block = """@app.post("/school/admissions/{application_id}/documents/{document_id}/verify")
def verify_admission_document(
    application_id: str,
    document_id: str,
    payload: DocumentVerificationRequest,
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    Authorized institution staff verifies or rejects a Stage 2 supporting document.
    \"\"\"
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        doc_row = conn.execute(
            \"\"\"
            SELECT d.document_id, d.document_type, d.file_name, a.institution_id, a.parent_user_id
            FROM admission_documents d
            JOIN admission_applications a ON a.application_id = d.application_id
            WHERE d.document_id = ? AND d.application_id = ? AND a.institution_id = ?
            \"\"\",
            (document_id, application_id, school_id)
        ).fetchone()
        if not doc_row:
            raise HTTPException(404, "Document not found or unauthorized for this institution.")

        conn.execute(
            \"\"\"
            UPDATE admission_documents
            SET verification_status = ?, verified_by_user_id = ?, verified_at = CURRENT_TIMESTAMP, verification_notes = ?
            WHERE document_id = ?
            \"\"\",
            (payload.verification_status, user["user_id"], payload.verification_notes, document_id)
        )

        # Notify parent if rejected or reupload requested
        if payload.verification_status in ("rejected", "reupload_requested") and doc_row["parent_user_id"]:
            conn.execute(
                \"\"\"
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Document Verification Update', ?, ?)
                \"\"\",
                (
                    str(uuid.uuid4()), doc_row["parent_user_id"], school_id, application_id,
                    f"Document '{doc_row['file_name']}' ({doc_row['document_type']}) was marked as '{payload.verification_status}': {payload.verification_notes or 'Please re-upload a clear copy.'}",
                    f"/parent?tab=admissions&app_id={application_id}"
                )
            )

        # Record in status history for full audit trail
        current_app = conn.execute("SELECT status FROM admission_applications WHERE application_id = ?", (application_id,)).fetchone()
        curr_status = current_app["status"] if current_app else "documents_uploaded"
        action_verb = "verified" if payload.verification_status == "verified" else ("replacement requested" if payload.verification_status == "reupload_requested" else "rejected")
        action_detail = f"Document '{doc_row['file_name']}' ({doc_row['document_type']}) {action_verb}."
        if payload.verification_notes:
            action_detail += f" Note: {payload.verification_notes}"
        conn.execute(
            \"\"\"
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, ?, ?, ?)
            \"\"\",
            (str(uuid.uuid4()), application_id, curr_status, curr_status, user["user_id"], action_detail)
        )

        conn.commit()
        return {
            "status": "updated",
            "document_id": document_id,
            "verification_status": payload.verification_status,
            "verification_notes": payload.verification_notes
        }
    finally:
        conn.close()"""

new_verify_block = """@app.post("/school/admissions/{application_id}/documents/{document_id}/verify")
def verify_admission_document(
    application_id: str,
    document_id: str,
    payload: DocumentVerificationRequest,
    user: dict = Depends(require_school_staff),
):
    \"\"\"
    Authorized institution staff verifies or rejects a Stage 2 supporting document.
    \"\"\"
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        # Check document existence and institution authorization
        doc_row = conn.execute(
            \"\"\"
            SELECT d.document_id, d.document_type, d.file_name, d.verification_status,
                   a.institution_id, a.parent_user_id, a.applicant_name, a.status as app_status
            FROM admission_documents d
            JOIN admission_applications a ON a.application_id = d.application_id
            WHERE d.document_id = ? AND d.application_id = ?
            \"\"\",
            (document_id, application_id)
        ).fetchone()
        if not doc_row:
            raise HTTPException(404, "Document not found for this admission application.")

        if doc_row["institution_id"] != school_id and user.get("role") != "platform_admin":
            raise HTTPException(403, f"Cross-institution access forbidden: Application belongs to {doc_row['institution_id']}, reviewer is assigned to {school_id}.")

        current_status = doc_row["verification_status"]
        target_status = payload.verification_status

        # Prevent repeated acceptance or rejection without an appropriate review workflow
        if target_status == "verified" and current_status == "verified":
            raise HTTPException(400, "Document is already verified. Repeated acceptance is not permitted.")
        if target_status == "rejected" and current_status == "rejected":
            raise HTTPException(400, "Document is already rejected. Repeated rejection is not permitted.")

        # Rejection reason is mandatory when rejecting
        if target_status == "rejected":
            if not payload.verification_notes or not payload.verification_notes.strip():
                raise HTTPException(400, "Rejection reason is mandatory when rejecting a document.")

        clean_notes = payload.verification_notes.strip() if payload.verification_notes else (
            "Document verified and found authentic by institution administrator." if target_status == "verified" else None
        )

        conn.execute(
            \"\"\"
            UPDATE admission_documents
            SET verification_status = ?,
                verified_by_user_id = ?,
                verified_at = CURRENT_TIMESTAMP,
                verification_notes = ?
            WHERE document_id = ?
            \"\"\",
            (target_status, user["user_id"], clean_notes, document_id)
        )

        doc_label = doc_row["document_type"].replace("_", " ").title()

        # Notify parent through in-app notification system
        if doc_row["parent_user_id"]:
            if target_status == "rejected":
                notif_title = f"Document Rejected: {doc_label}"
                notif_msg = (
                    f"Your uploaded certificate '{doc_row['file_name']}' for {doc_label} (Applicant: {doc_row['applicant_name']}) "
                    f"was reviewed and rejected by {doc_row['institution_id']}. Reason: {clean_notes}. "
                    f"Please log in and upload a valid replacement document."
                )
                conn.execute(
                    \"\"\"
                    INSERT INTO portal_notifications (
                        notification_id, recipient_user_id, recipient_role, institution_id,
                        application_id, title, message, action_url, is_read, category, priority
                    ) VALUES (?, ?, 'parent', ?, ?, ?, ?, ?, 0, 'admissions', 'high')
                    \"\"\",
                    (
                        str(uuid.uuid4()), doc_row["parent_user_id"], doc_row["institution_id"],
                        application_id, notif_title, notif_msg, f"/parent?tab=admissions&app_id={application_id}"
                    )
                )
            elif target_status == "verified":
                notif_title = f"Document Verified: {doc_label}"
                notif_msg = (
                    f"Your uploaded certificate '{doc_row['file_name']}' for {doc_label} (Applicant: {doc_row['applicant_name']}) "
                    f"has been verified and accepted by {doc_row['institution_id']}."
                )
                conn.execute(
                    \"\"\"
                    INSERT INTO portal_notifications (
                        notification_id, recipient_user_id, recipient_role, institution_id,
                        application_id, title, message, action_url, is_read, category, priority
                    ) VALUES (?, ?, 'parent', ?, ?, ?, ?, ?, 0, 'admissions', 'normal')
                    \"\"\",
                    (
                        str(uuid.uuid4()), doc_row["parent_user_id"], doc_row["institution_id"],
                        application_id, notif_title, notif_msg, f"/parent?tab=admissions&app_id={application_id}"
                    )
                )

        # Record in application status history for complete audit trail
        reviewer_name = user.get("full_name") or user.get("email") or "Institution Administrator"
        action_verb = "accepted and verified" if target_status == "verified" else ("rejected" if target_status == "rejected" else "marked for replacement")
        action_detail = f"Document '{doc_row['file_name']}' ({doc_label}) {action_verb} by {reviewer_name} (ID: {user['user_id']})."
        if clean_notes:
            action_detail += f" Note/Reason: {clean_notes}"

        conn.execute(
            \"\"\"
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status, action_by_user_id, action_note
            ) VALUES (?, ?, ?, ?, ?, ?)
            \"\"\",
            (str(uuid.uuid4()), application_id, doc_row["app_status"], doc_row["app_status"], user["user_id"], action_detail)
        )

        conn.commit()
        return {
            "status": "updated",
            "document_id": document_id,
            "verification_status": target_status,
            "verification_notes": clean_notes,
            "verified_by_user_id": user["user_id"],
            "verified_at": datetime.datetime.utcnow().isoformat(),
            "message": "Document successfully verified." if target_status == "verified" else "Document marked as rejected."
        }
    finally:
        conn.close()"""

print("Count of old_docs_block:", content.count(old_docs_block))
print("Count of old_verify_block:", content.count(old_verify_block))

if content.count(old_docs_block) == 2 and content.count(old_verify_block) == 1:
    content = content.replace(old_docs_block, new_docs_block)
    content = content.replace(old_verify_block, new_verify_block)
    with open(backend_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: backend/main.py successfully patched!")
else:
    print("MISMATCH in block counts! Check formatting.")
