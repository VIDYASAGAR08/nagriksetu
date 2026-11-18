import os

main_py_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

endpoints_code = '''

class FinalAdmissionConfirmPayload(BaseModel):
    section_id: str
    admission_date: Optional[str] = None
    notes: Optional[str] = None


@app.get("/school/admissions/{application_id}/available-sections")
def get_available_sections_for_admission(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Returns available sections and seat capacities for an application.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, institution_id, requested_standard, requested_program_id, education_level, academic_year, status FROM admission_applications WHERE application_id = ?",
            (application_id,)
        ).fetchone()
        if not app_row or app_row["institution_id"] != school_id:
            raise HTTPException(404, "Application not found or unauthorized for this institution.")

        std = app_row["requested_standard"]
        prog_id = app_row["requested_program_id"]

        sections = []
        if app_row["education_level"] == "school" and std:
            sections = conn.execute(
                """
                SELECT section_id, institution_id, program_id, term_or_year, section_name, capacity, current_strength
                FROM program_sections
                WHERE institution_id = ? AND term_or_year = ?
                ORDER BY section_name
                """,
                (school_id, std)
            ).fetchall()
        elif prog_id:
            sections = conn.execute(
                """
                SELECT section_id, institution_id, program_id, term_or_year, section_name, capacity, current_strength
                FROM program_sections
                WHERE institution_id = ? AND program_id = ?
                ORDER BY term_or_year, section_name
                """,
                (school_id, prog_id)
            ).fetchall()

        if not sections:
            sections = conn.execute(
                """
                SELECT section_id, institution_id, program_id, term_or_year, section_name, capacity, current_strength
                FROM program_sections
                WHERE institution_id = ?
                ORDER BY term_or_year, section_name
                LIMIT 10
                """,
                (school_id,)
            ).fetchall()

        result = []
        for s in sections:
            rem = max(0, s["capacity"] - s["current_strength"])
            result.append({
                "section_id": s["section_id"],
                "section_name": s["section_name"],
                "program_id": s["program_id"],
                "term_or_year": s["term_or_year"],
                "capacity": s["capacity"],
                "current_strength": s["current_strength"],
                "available_seats": rem,
                "is_full": rem == 0
            })
        return result
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/final-admission-confirm")
def confirm_final_admission_and_enrol(
    application_id: str,
    payload: FinalAdmissionConfirmPayload,
    user: dict = Depends(require_school_staff),
):
    """
    Authorized school staff confirms final admission, creates official student record
    in 'students' and 'enrollments', and increments section capacity safely.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            """
            SELECT a.*, s.school_name AS institution_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            WHERE a.application_id = ? AND a.institution_id = ?
            """,
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")

        # Idempotency: If already enrolled, return existing
        if app_row["status"] in ("enrolled", "final_admission_confirmed"):
            student = conn.execute(
                "SELECT * FROM students WHERE permanent_student_id = ?",
                (app_row["enrolled_student_id"],)
            ).fetchone()
            enrollment = conn.execute(
                "SELECT * FROM enrollments WHERE permanent_student_id = ?",
                (app_row["enrolled_student_id"],)
            ).fetchone()
            return {
                "status": "enrolled",
                "message": "Student is already officially enrolled (Idempotent response).",
                "application_id": application_id,
                "permanent_student_id": app_row["enrolled_student_id"],
                "student_id": student["student_id"] if student else None,
                "enrollment_id": enrollment["enrollment_id"] if enrollment else None,
                "standard": student["standard"] if student else app_row["requested_standard"],
                "section": student["section"] if student else "A",
                "is_already_enrolled": True
            }

        # Prerequisites: Must be verified
        allowed_statuses = ("approved", "stage2_submitted", "documents_uploaded", "detailed_review_completed", "documents_verified")
        if app_row["status"] not in allowed_statuses:
            raise HTTPException(400, f"Cannot confirm final admission: application status is '{app_row['status']}'. It must be verified first.")

        # Check unverified documents
        unverified_docs = conn.execute(
            "SELECT COUNT(*) FROM admission_documents WHERE application_id = ? AND verification_status != 'verified'",
            (application_id,)
        ).fetchone()[0]
        if unverified_docs > 0:
            raise HTTPException(400, f"Cannot confirm final admission: {unverified_docs} supporting document(s) have not been verified.")

        # Section validation & capacity check
        section_row = conn.execute(
            "SELECT * FROM program_sections WHERE section_id = ? AND institution_id = ?",
            (payload.section_id, school_id)
        ).fetchone()
        if not section_row:
            raise HTTPException(404, f"Selected section '{payload.section_id}' not found for institution '{school_id}'.")

        if section_row["current_strength"] >= section_row["capacity"]:
            raise HTTPException(400, f"Selected section '{section_row['section_name']}' is at full capacity ({section_row['current_strength']}/{section_row['capacity']} seats). Cannot enrol additional students.")

        # Stage 2 demographics if available
        stage2_sub = conn.execute(
            "SELECT * FROM admission_detailed_submissions WHERE application_id = ?",
            (application_id,)
        ).fetchone()

        std_val = app_row["requested_standard"] or section_row["term_or_year"] or 1
        std_for_enr = max(1, min(12, int(std_val)))

        sec_name = section_row["section_name"].strip().upper()
        if sec_name not in ("A", "B", "C"):
            sec_name = "A"

        lang_val = app_row["first_language_preference"] or "Kannada"
        if lang_val not in ("Kannada", "Hindi", "Sanskrit"):
            lang_val = "Kannada"

        dob = (stage2_sub["date_of_birth"] if stage2_sub and stage2_sub["date_of_birth"] else None) or "2015-06-01"
        gender = (stage2_sub["gender"] if stage2_sub and stage2_sub["gender"] else None) or "male"
        try:
            birth_year = int(dob.split("-")[0])
            calc_age = max(5, 2026 - birth_year)
        except Exception:
            calc_age = std_for_enr + 5

        adm_date = payload.admission_date or "2026-11-01"

        perm_student_id = f"NS-{uuid.uuid4().hex.upper()}"
        student_pk = f"{school_id}-STD{std_for_enr:02d}-{uuid.uuid4().hex[:6].upper()}"
        enrollment_pk = f"ENR-{uuid.uuid4().hex.upper()}"

        # 1. Insert into students
        conn.execute(
            """
            INSERT INTO students (
                student_id, student_name, school_id, standard, section,
                age, permanent_student_id, first_language, date_of_birth,
                gender, admission_date, enrollment_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                student_pk, app_row["applicant_name"], school_id, std_for_enr, sec_name,
                calc_age, perm_student_id, lang_val, dob, gender, adm_date
            )
        )

        # 2. Insert into enrollments
        conn.execute(
            """
            INSERT INTO enrollments (
                enrollment_id, permanent_student_id, school_id, academic_year,
                standard, section, first_language, stream, subject_combination,
                admission_date, enrollment_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
            """,
            (
                enrollment_pk, perm_student_id, school_id, app_row["academic_year"] or "2026-2027",
                std_for_enr, sec_name, lang_val, app_row["stream_preference"], app_row["combination_code"],
                adm_date
            )
        )

        # 3. Increment section strength
        conn.execute(
            "UPDATE program_sections SET current_strength = current_strength + 1 WHERE section_id = ?",
            (payload.section_id,)
        )

        # 4. Update admission application
        prev_status = app_row["status"]
        conn.execute(
            """
            UPDATE admission_applications
            SET status = 'enrolled',
                enrolled_student_id = ?,
                enrolled_at = CURRENT_TIMESTAMP,
                reviewer_user_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
            """,
            (perm_student_id, user["user_id"], application_id)
        )

        # 5. Insert history
        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status, action_by_user_id, action_note
            ) VALUES (?, ?, ?, 'enrolled', ?, ?)
            """,
            (
                str(uuid.uuid4()), application_id, prev_status, user["user_id"],
                payload.notes or f"Final admission confirmed. Enrolled in Standard {std_for_enr}, Section {sec_name}. Permanent ID: {perm_student_id}"
            )
        )

        # 6. Notify parent
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (
                    notification_id, recipient_user_id, institution_id, application_id, title, message, action_url
                ) VALUES (?, ?, ?, ?, '🎉 Admission Confirmed & Enrolled!', ?, ?)
                """,
                (
                    str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id,
                    f"Congratulations! Official admission confirmed for {app_row['applicant_name']}. Permanent Student ID: {perm_student_id}, Section: {sec_name}.",
                    f"/parent?tab=children"
                )
            )

        conn.commit()

        new_strength = conn.execute(
            "SELECT current_strength FROM program_sections WHERE section_id = ?",
            (payload.section_id,)
        ).fetchone()[0]

        return {
            "status": "enrolled",
            "message": "Student successfully enrolled in official institution academic ledger.",
            "application_id": application_id,
            "permanent_student_id": perm_student_id,
            "student_id": student_pk,
            "enrollment_id": enrollment_pk,
            "school_id": school_id,
            "standard": std_for_enr,
            "section": sec_name,
            "new_section_strength": new_strength,
            "is_already_enrolled": False
        }
    finally:
        conn.close()
'''

if "/school/admissions/{application_id}/final-admission-confirm" not in content:
    # insert right before @app.get("/notifications")
    pos = content.find('@app.get("/notifications")')
    if pos != -1:
        content = content[:pos] + endpoints_code + "\n\n" + content[pos:]
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully injected Phase 6 backend endpoints into main.py.")
    else:
        print("Could not find @app.get('/notifications') in main.py")
else:
    print("Endpoints already exist in main.py.")
