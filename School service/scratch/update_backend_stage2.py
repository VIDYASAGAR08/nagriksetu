import re

backend_path = 'C:/Users/callm/nagriksetu/backend/main.py'
with open(backend_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update get_optional_current_user to check query param token as well
old_get_opt = """def get_optional_current_user(request: Request) -> Optional[dict]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()"""

new_get_opt = """def get_optional_current_user(request: Request) -> Optional[dict]:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif request.query_params.get("token"):
        token = request.query_params.get("token").strip()
    if not token:
        return None"""

# 2. Update check_admission_application_access to include institution_admin and academic_admin
old_check_access = """    if role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "student_records_officer", "general_staff"):
        return user.get("school_id") == app_row["institution_id"]"""

new_check_access = """    if role in ("school_admin", "school_staff", "admissions_officer", "academic_admin", "institution_admin", "student_records_officer", "general_staff"):
        return user.get("school_id") == app_row["institution_id"]"""

# 3. Update get_school_admission_application_detail to enrich with Stage 2 details and documents
old_detail_body = """        data = dict(row)
        data['id'] = data['application_id']
        data['application_reference'] = data['application_id']
        data['student_name'] = data.get('applicant_name')
        data['standard'] = data.get('requested_standard')
        hist = conn.execute(
            \"\"\"
            SELECT history_id, previous_status, new_status, action_by_user_id, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            \"\"\",
            (application_id,)
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]
        return data"""

new_detail_body = """        data = dict(row)
        data['id'] = data['application_id']
        data['application_reference'] = data['application_id']
        data['student_name'] = data.get('applicant_name')
        data['standard'] = data.get('requested_standard')
        hist = conn.execute(
            \"\"\"
            SELECT history_id, previous_status, new_status, action_by_user_id, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            \"\"\",
            (application_id,)
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]

        # Stage 2 Detailed Submission
        detailed_row = conn.execute(
            \"\"\"
            SELECT submission_id, application_id, date_of_birth, gender, blood_group,
                   previous_institution_name, previous_institution_location,
                   previous_standard_or_degree, previous_board, previous_marks_percentage,
                   emergency_contact_name, emergency_contact_phone, custom_fields_json,
                   status, submitted_at
            FROM admission_detailed_submissions
            WHERE application_id = ?
            ORDER BY submitted_at DESC
            LIMIT 1
            \"\"\",
            (application_id,)
        ).fetchone()

        if detailed_row:
            s2 = dict(detailed_row)
            if s2.get("custom_fields_json"):
                try:
                    s2["custom_fields"] = json.loads(s2["custom_fields_json"])
                except Exception:
                    s2["custom_fields"] = {}
            else:
                s2["custom_fields"] = {}
            data["stage2_details"] = s2
            data["stage2_submitted"] = True
            data["date_of_birth"] = s2.get("date_of_birth")
            data["gender"] = s2.get("gender")
            data["blood_group"] = s2.get("blood_group")
            data["previous_institution_name"] = s2.get("previous_institution_name")
            data["previous_institution_location"] = s2.get("previous_institution_location")
            data["previous_standard_or_degree"] = s2.get("previous_standard_or_degree")
            data["previous_board"] = s2.get("previous_board")
            data["previous_marks_percentage"] = s2.get("previous_marks_percentage")
            data["emergency_contact_name"] = s2.get("emergency_contact_name")
            data["emergency_contact_phone"] = s2.get("emergency_contact_phone")
            data["stage2_submitted_at"] = s2.get("submitted_at")
        else:
            data["stage2_details"] = None
            data["stage2_submitted"] = False

        # Supporting Documents
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
        data["reupload_documents_count"] = sum(1 for d in docs_list if d.get("verification_status") in ("reupload_requested", "rejected"))

        return data"""

# 4. Update get_parent_application_details to enrich with Stage 2 details and documents
old_parent_detail_body = """        data = dict(row)
        hist = conn.execute(
            \"\"\"
            SELECT history_id, previous_status, new_status, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            \"\"\",
            (application_id,),
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]
        return data"""

new_parent_detail_body = """        data = dict(row)
        hist = conn.execute(
            \"\"\"
            SELECT history_id, previous_status, new_status, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            \"\"\",
            (application_id,),
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]

        # Stage 2 Detailed Submission
        detailed_row = conn.execute(
            \"\"\"
            SELECT submission_id, application_id, date_of_birth, gender, blood_group,
                   previous_institution_name, previous_institution_location,
                   previous_standard_or_degree, previous_board, previous_marks_percentage,
                   emergency_contact_name, emergency_contact_phone, custom_fields_json,
                   status, submitted_at
            FROM admission_detailed_submissions
            WHERE application_id = ?
            ORDER BY submitted_at DESC
            LIMIT 1
            \"\"\",
            (application_id,)
        ).fetchone()

        if detailed_row:
            s2 = dict(detailed_row)
            if s2.get("custom_fields_json"):
                try:
                    s2["custom_fields"] = json.loads(s2["custom_fields_json"])
                except Exception:
                    s2["custom_fields"] = {}
            else:
                s2["custom_fields"] = {}
            data["stage2_details"] = s2
            data["stage2_submitted"] = True
            data["date_of_birth"] = s2.get("date_of_birth")
            data["gender"] = s2.get("gender")
            data["blood_group"] = s2.get("blood_group")
            data["previous_institution_name"] = s2.get("previous_institution_name")
            data["previous_institution_location"] = s2.get("previous_institution_location")
            data["previous_standard_or_degree"] = s2.get("previous_standard_or_degree")
            data["previous_board"] = s2.get("previous_board")
            data["previous_marks_percentage"] = s2.get("previous_marks_percentage")
            data["emergency_contact_name"] = s2.get("emergency_contact_name")
            data["emergency_contact_phone"] = s2.get("emergency_contact_phone")
            data["stage2_submitted_at"] = s2.get("submitted_at")
        else:
            data["stage2_details"] = None
            data["stage2_submitted"] = False

        # Supporting Documents
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
        data["reupload_documents_count"] = sum(1 for d in docs_list if d.get("verification_status") in ("reupload_requested", "rejected"))

        return data"""

# 5. In verify_admission_document, record audit history
old_verify_doc_commit = """        conn.commit()
        return {
            \"status\": \"updated\",
            \"document_id\": document_id,
            \"verification_status\": payload.verification_status,
            \"verification_notes\": payload.verification_notes
        }"""

new_verify_doc_commit = """        # Record in status history for full audit trail
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
            \"status\": \"updated\",
            \"document_id\": document_id,
            \"verification_status\": payload.verification_status,
            \"verification_notes\": payload.verification_notes
        }"""

replacements = [
    (old_get_opt, new_get_opt, "get_optional_current_user"),
    (old_check_access, new_check_access, "check_admission_application_access"),
    (old_detail_body, new_detail_body, "get_school_admission_application_detail"),
    (old_parent_detail_body, new_parent_detail_body, "get_parent_application_details"),
    (old_verify_doc_commit, new_verify_doc_commit, "verify_admission_document audit")
]

for old, new, desc in replacements:
    old_crlf = old.replace('\n', '\r\n')
    new_crlf = new.replace('\n', '\r\n')
    if old_crlf in code:
        code = code.replace(old_crlf, new_crlf, 1)
        print(f"Replaced CRLF: {desc}")
    elif old in code:
        code = code.replace(old, new, 1)
        print(f"Replaced LF: {desc}")
    else:
        print(f"FAILED to find: {desc}")

with open(backend_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved backend/main.py successfully.")
