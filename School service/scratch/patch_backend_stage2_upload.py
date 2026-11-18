backend_path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(backend_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        # Update application status to documents_uploaded if in stage2_submitted
        if app_row["status"] in ("approved", "stage2_submitted"):
            conn.execute(
                "UPDATE admission_applications SET status = 'documents_uploaded', updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
                (application_id,)
            )

        conn.commit()"""

replacement = """        # Update application status to documents_uploaded if in stage2_submitted
        if app_row["status"] in ("approved", "stage2_submitted"):
            conn.execute(
                "UPDATE admission_applications SET status = 'documents_uploaded', updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
                (application_id,)
            )

        # Audit trail for document upload / replacement
        doc_label = payload.document_type.replace("_", " ").title()
        uploader_id = current_user.get("user_id") if current_user else "parent"
        conn.execute(
            \"\"\"
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status, action_by_user_id, action_note
            ) VALUES (?, ?, ?, ?, ?, ?)
            \"\"\",
            (
                str(uuid.uuid4()), application_id, app_row["status"], app_row["status"], uploader_id,
                f"Applicant parent uploaded certificate '{safe_filename}' ({doc_label}) for verification."
            )
        )

        conn.commit()"""

target2 = """        rows = conn.execute(
            \"\"\"
            SELECT document_id, application_id, document_type, file_name, file_size_bytes,
                   mime_type, verification_status, uploaded_at, verified_at, verification_notes
            FROM admission_documents
            WHERE application_id = ?
            ORDER BY uploaded_at ASC
            \"\"\",
            (application_id,)
        ).fetchall()
        return [dict(r) for r in rows]"""

replacement2 = """        rows = conn.execute(
            \"\"\"
            SELECT document_id, application_id, document_type, file_name, file_size_bytes,
                   mime_type, verification_status, uploaded_at, verified_at, verification_notes
            FROM admission_documents
            WHERE application_id = ?
            ORDER BY uploaded_at ASC
            \"\"\",
            (application_id,)
        ).fetchall()

        type_counts = {}
        for r in rows:
            dt = r["document_type"]
            type_counts[dt] = type_counts.get(dt, 0) + 1

        type_current = {}
        docs = []
        for r in rows:
            d = dict(r)
            dt = d["document_type"]
            type_current[dt] = type_current.get(dt, 0) + 1
            ver = type_current[dt]
            d["version"] = ver
            d["is_latest"] = (ver == type_counts[dt])
            d["download_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            d["preview_url"] = f"/admissions/applications/{application_id}/documents/{d['document_id']}/file"
            docs.append(d)
        return docs"""

assert target in content, "target not found"
assert target2 in content, "target2 not found"

content = content.replace(target, replacement, 1)
content = content.replace(target2, replacement2, 1)

with open(backend_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Stage 2 upload and document endpoint patched!")
