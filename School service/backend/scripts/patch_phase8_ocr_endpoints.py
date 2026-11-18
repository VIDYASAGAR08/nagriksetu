import os

main_py_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import for ocr_service
if "import ocr_service" not in content:
    content = "import ocr_service\n" + content

ocr_routes = '''

class OcrOverridePayload(BaseModel):
    override_notes: str
    verified_match_status: Literal["verified_match", "rejected_mismatch"] = "verified_match"


@app.post("/school/admissions/{application_id}/documents/{document_id}/ocr-analyze")
def run_document_ocr_intelligence(
    application_id: str,
    document_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Runs real Intelligent Document Processing (IDP) and OCR extraction
    on an uploaded admission document without fabricated metrics.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        doc = conn.execute(
            """
            SELECT d.*, a.applicant_name, a.institution_id
            FROM admission_documents d
            JOIN admission_applications a ON a.application_id = d.application_id
            WHERE d.document_id = ? AND d.application_id = ? AND a.institution_id = ?
            """,
            (document_id, application_id, school_id)
        ).fetchone()
        if not doc:
            raise HTTPException(404, "Document not found or unauthorized for this institution.")

        file_path = doc["file_path"]
        if not os.path.exists(file_path):
            local_fallback = os.path.join("/app", "data", "uploads", "admissions", application_id, os.path.basename(file_path))
            if os.path.exists(local_fallback):
                file_path = local_fallback
            else:
                host_fallback = os.path.join("backend", "data", "uploads", "admissions", application_id, os.path.basename(file_path))
                if os.path.exists(host_fallback):
                    file_path = host_fallback
                else:
                    raise HTTPException(404, "Document file not found on disk.")

        # Determine file type & run real extraction
        mime = (doc["mime_type"] or "").lower()
        if "pdf" in mime or file_path.lower().endswith(".pdf"):
            raw_text, confidence = ocr_service.extract_text_from_pdf(file_path)
            ocr_engine = "pypdf_native_stream"
        else:
            raw_text, confidence = ocr_service.extract_text_and_confidence_from_image(file_path)
            ocr_engine = "tesseract_5.5.0_ocr"

        # Parse structured entities
        entities = ocr_service.parse_structured_entities(raw_text)

        # Fetch Stage 2 data for comparison
        stage2_sub = conn.execute(
            "SELECT * FROM admission_detailed_submissions WHERE application_id = ?",
            (application_id,)
        ).fetchone()

        s2_dob = stage2_sub["date_of_birth"] if stage2_sub else None
        s2_marks = stage2_sub["previous_marks_percentage"] if stage2_sub else None

        match_status, discrepancy_notes = ocr_service.compare_and_audit_discrepancies(
            entities, doc["applicant_name"], s2_dob, s2_marks
        )

        extraction_id = str(uuid.uuid4())
        entities_json = json.dumps(entities)

        # Store extraction
        conn.execute(
            """
            INSERT OR REPLACE INTO document_ocr_extractions (
                extraction_id, document_id, application_id, raw_text,
                ocr_engine, average_confidence, extracted_entities_json,
                match_status, discrepancy_notes, extracted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                extraction_id, document_id, application_id, raw_text,
                ocr_engine, confidence, entities_json, match_status, discrepancy_notes
            )
        )
        conn.commit()

        return {
            "extraction_id": extraction_id,
            "document_id": document_id,
            "application_id": application_id,
            "document_type": doc["document_type"],
            "file_name": doc["file_name"],
            "ocr_engine": ocr_engine,
            "confidence_percentage": confidence,
            "extracted_entities": entities,
            "match_status": match_status,
            "discrepancy_notes": discrepancy_notes,
            "raw_text_preview": raw_text[:300] + ("..." if len(raw_text) > 300 else "")
        }
    finally:
        conn.close()


@app.get("/school/admissions/{application_id}/documents/{document_id}/ocr-result")
def get_document_ocr_result(
    application_id: str,
    document_id: str,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT e.*, d.document_type, d.file_name
            FROM document_ocr_extractions e
            JOIN admission_documents d ON d.document_id = e.document_id
            JOIN admission_applications a ON a.application_id = e.application_id
            WHERE e.document_id = ? AND e.application_id = ? AND a.institution_id = ?
            ORDER BY e.extracted_at DESC
            LIMIT 1
            """,
            (document_id, application_id, school_id)
        ).fetchone()
        if not row:
            return {"has_ocr_result": False}

        return {
            "has_ocr_result": True,
            "extraction_id": row["extraction_id"],
            "ocr_engine": row["ocr_engine"],
            "confidence_percentage": row["average_confidence"],
            "extracted_entities": json.loads(row["extracted_entities_json"]),
            "match_status": row["match_status"],
            "discrepancy_notes": row["discrepancy_notes"],
            "extracted_at": row["extracted_at"],
            "raw_text": row["raw_text"]
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/documents/{document_id}/ocr-override")
def override_document_ocr_review(
    application_id: str,
    document_id: str,
    payload: OcrOverridePayload,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE document_ocr_extractions
            SET match_status = ?, discrepancy_notes = ?
            WHERE document_id = ? AND application_id = ?
            """,
            (payload.verified_match_status, f"Human Override by Staff {user['user_id']}: {payload.override_notes}", document_id, application_id)
        )
        conn.commit()
        return {"status": "overridden", "match_status": payload.verified_match_status}
    finally:
        conn.close()
'''

if "/school/admissions/{application_id}/documents/{document_id}/ocr-analyze" not in content:
    # insert before @app.get("/notifications")
    pos = content.find('@app.get("/notifications")')
    if pos != -1:
        content = content[:pos] + ocr_routes + "\n\n" + content[pos:]
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully injected Phase 8 OCR endpoints into main.py.")
    else:
        print("Could not find insertion marker in main.py")
else:
    print("OCR endpoints already exist in main.py.")
