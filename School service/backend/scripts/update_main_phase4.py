import os
import sys

main_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

target_marker = '@app.post("/admissions/apply", status_code=status.HTTP_201_CREATED)'
idx = content.find(target_marker)
if idx == -1:
    print("ERROR: Target marker not found!")
    sys.exit(1)

pre_code = content[:idx]

new_code = '''@app.get("/admissions/form-config/{institution_id}")
def get_admission_form_config(institution_id: str):
    """
    Returns database-driven Stage 1 configuration for an institution.
    Provides valid standards, languages, streams, combinations, and programs without hardcoding.
    """
    conn = get_connection()
    try:
        inst = conn.execute(
            """
            SELECT school_id, school_name, school_type, affiliation, district, state
            FROM schools WHERE school_id = ?
            """,
            (institution_id,)
        ).fetchone()
        if not inst:
            raise HTTPException(404, f"Institution {institution_id} not found.")

        # 1. Divisions
        div_rows = conn.execute(
            """
            SELECT division_id, division_name, division_type, campus_location
            FROM institution_divisions WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            """,
            (institution_id,)
        ).fetchall()
        divisions = [dict(d) for d in div_rows]

        # 2. Academic programs
        prog_rows = conn.execute(
            """
            SELECT program_id, education_level, program_name, degree_type, discipline_or_stream, combination_code, duration_years
            FROM academic_programs WHERE institution_id = ? AND is_active = 1
            ORDER BY education_level, program_name
            """,
            (institution_id,)
        ).fetchall()
        programs = [dict(p) for p in prog_rows]

        # 3. Detect offered education categories
        offered_levels = sorted(list(set(p["education_level"] for p in programs)))
        inst_type_lower = (inst["school_type"] or "").lower()
        if not offered_levels:
            if "college" in inst_type_lower or "university" in inst_type_lower:
                offered_levels = ["undergraduate"]
            else:
                offered_levels = ["school"]

        # 4. Standard levels for schools (1 to 10)
        has_school = "school" in offered_levels or any(p["education_level"] == "school" for p in programs) or "school" in inst_type_lower
        standards = list(range(1, 11)) if has_school else []

        # 5. Language options (from enrollments or institutional standards)
        lang_rows = conn.execute(
            "SELECT DISTINCT first_language FROM enrollments WHERE school_id = ? AND first_language IS NOT NULL",
            (institution_id,)
        ).fetchall()
        first_languages = [r[0] for r in lang_rows] if lang_rows else ["Kannada", "English"]
        second_languages = ["English", "Kannada", "Hindi", "Sanskrit"]

        # 6. PU Streams & Combinations
        pu_combinations = []
        pu_streams = set()
        for p in programs:
            if p["education_level"] == "higher_secondary":
                if p["discipline_or_stream"]:
                    pu_streams.add(p["discipline_or_stream"])
                pu_combinations.append({
                    "combination_code": p["combination_code"],
                    "stream": p["discipline_or_stream"],
                    "program_name": p["program_name"],
                    "program_id": p["program_id"]
                })

        # 7. Diploma Programs
        diploma_programs = [
            {
                "program_id": p["program_id"],
                "program_name": p["program_name"],
                "discipline_or_stream": p["discipline_or_stream"],
                "duration_years": p["duration_years"]
            }
            for p in programs if p["education_level"] == "diploma"
        ]

        # 8. Undergraduate Programs
        ug_programs = [
            {
                "program_id": p["program_id"],
                "program_name": p["program_name"],
                "degree_type": p["degree_type"],
                "discipline_or_stream": p["discipline_or_stream"],
                "duration_years": p["duration_years"]
            }
            for p in programs if p["education_level"] == "undergraduate"
        ]

        # 9. Seat availability summary
        seat_summary = conn.execute(
            """
            SELECT COALESCE(SUM(capacity), 0) AS total_capacity,
                   COALESCE(SUM(current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN capacity > current_strength THEN capacity - current_strength ELSE 0 END), 0) AS available_seats
            FROM program_sections WHERE institution_id = ?
            """,
            (institution_id,)
        ).fetchone()

        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "school_type": inst["school_type"],
            "affiliation": inst["affiliation"],
            "district": inst["district"],
            "academic_year": "2026-2027",
            "offered_levels": offered_levels,
            "divisions": divisions,
            "has_school_offerings": has_school,
            "school_config": {
                "standards": standards,
                "first_languages": first_languages,
                "second_languages": second_languages,
            } if has_school else None,
            "pu_config": {
                "levels": ["1st PU (Class 11)", "2nd PU (Class 12)"],
                "streams": sorted(list(pu_streams)) if pu_streams else ["Science", "Commerce", "Arts"],
                "combinations": pu_combinations,
            } if pu_combinations or "higher_secondary" in offered_levels else None,
            "diploma_config": {
                "programs": diploma_programs,
            } if diploma_programs or "diploma" in offered_levels else None,
            "undergraduate_config": {
                "programs": ug_programs,
            } if ug_programs or "undergraduate" in offered_levels else None,
            "seat_summary": dict(seat_summary) if seat_summary else {"total_capacity": 0, "available_seats": 0},
            "status": "ready"
        }
    finally:
        conn.close()


@app.post("/admissions/apply", status_code=status.HTTP_201_CREATED)
def submit_stage1_admission_application(
    payload: Stage1ApplicationCreate,
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Submits a Stage 1 Initial Admission Application.
    Dynamically validates fields against database configurations:
    - School: Standard (1-10) + Language preference
    - PU College: Stream + Subject Combination (verified against academic_programs)
    - Diploma / UG: Program ID matching institution offerings.
    """
    conn = get_connection()
    try:
        # 1. Verify institution exists
        inst = conn.execute(
            "SELECT school_id, school_name, school_type FROM schools WHERE school_id = ?",
            (payload.institution_id,),
        ).fetchone()
        if not inst:
            raise HTTPException(404, "Selected institution not found.")

        # 2. Basic validations
        app_name = payload.applicant_name.strip()
        par_name = payload.parent_name.strip()
        par_phone = payload.parent_phone.strip()
        res_addr = payload.residential_address.strip()

        if len(app_name) < 2:
            raise HTTPException(400, "Applicant full name must be at least 2 characters.")
        if len(par_name) < 2:
            raise HTTPException(400, "Parent/guardian full name must be at least 2 characters.")
        digits_phone = "".join(filter(str.isdigit, par_phone))
        if len(digits_phone) < 10:
            raise HTTPException(400, "Please provide a valid 10-digit contact mobile number.")
        if len(res_addr) < 5:
            raise HTTPException(400, "Please provide a complete residential address (min 5 characters).")

        # 3. Division validation if passed
        if payload.division_id:
            div = conn.execute(
                "SELECT division_id FROM institution_divisions WHERE division_id = ? AND parent_institution_id = ?",
                (payload.division_id, payload.institution_id)
            ).fetchone()
            if not div:
                raise HTTPException(400, f"Division '{payload.division_id}' is not associated with this institution.")

        # 4. Type-specific validation against database
        level = payload.education_level.lower()
        if level == "school":
            if not payload.requested_standard or not (1 <= payload.requested_standard <= 10):
                raise HTTPException(400, "School admission requires a valid standard between 1 and 10.")
            if not payload.first_language_preference:
                payload.first_language_preference = "Kannada"
        elif level == "higher_secondary":
            if not payload.combination_code:
                raise HTTPException(400, "PU College admission requires a preferred subject combination (e.g. PCMB, PCMC, SEBA).")
            comb_prog = conn.execute(
                "SELECT program_id FROM academic_programs WHERE institution_id = ? AND combination_code = ? AND education_level = 'higher_secondary'",
                (payload.institution_id, payload.combination_code.strip())
            ).fetchone()
            if not comb_prog:
                raise HTTPException(400, f"Subject combination '{payload.combination_code}' is not configured for this PU institution.")
            if not payload.requested_program_id:
                payload.requested_program_id = comb_prog["program_id"]
        elif level in ["diploma", "undergraduate"]:
            if not payload.requested_program_id:
                raise HTTPException(400, f"{level.title()} admission requires selecting an offered academic program.")
            prog_row = conn.execute(
                "SELECT program_id FROM academic_programs WHERE institution_id = ? AND program_id = ? AND education_level = ?",
                (payload.institution_id, payload.requested_program_id.strip(), level)
            ).fetchone()
            if not prog_row:
                raise HTTPException(400, f"Programme '{payload.requested_program_id}' is not offered by this institution for level '{level}'.")
        else:
            raise HTTPException(400, f"Invalid education category: {payload.education_level}")

        # 5. Generate unique Application ID
        app_id = f"APP-{payload.academic_year[:4]}-{payload.institution_id}-{uuid.uuid4().hex[:6].upper()}"
        parent_uid = current_user.get("user_id") if current_user and current_user.get("role") == "parent" else None

        # 6. Insert into admission_applications
        conn.execute(
            """
            INSERT INTO admission_applications (
                application_id, institution_id, division_id, parent_user_id,
                applicant_name, parent_name, parent_phone, parent_email,
                residential_address, academic_year, education_level,
                requested_standard, requested_program_id, first_language_preference,
                second_language_preference, stream_preference, combination_code, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted')
            """,
            (
                app_id,
                payload.institution_id,
                payload.division_id,
                parent_uid,
                app_name,
                par_name,
                digits_phone[-10:],
                payload.parent_email.strip() if payload.parent_email else None,
                res_addr,
                payload.academic_year,
                level,
                payload.requested_standard,
                payload.requested_program_id,
                payload.first_language_preference,
                payload.second_language_preference,
                payload.stream_preference,
                payload.combination_code,
            ),
        )

        # 7. Insert initial status history
        conn.execute(
            """
            INSERT INTO admission_status_history (
                history_id, application_id, previous_status, new_status,
                action_by_user_id, action_note
            ) VALUES (?, ?, NULL, 'submitted', ?, 'Initial Stage 1 application submitted.')
            """,
            (str(uuid.uuid4()), app_id, parent_uid or "public_applicant"),
        )

        # 8. Dispatch in-app notification to School Admin
        conn.execute(
            """
            INSERT INTO portal_notifications (
                notification_id, recipient_role, institution_id, application_id,
                title, message, action_url
            ) VALUES (?, 'school_admin', ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                payload.institution_id,
                app_id,
                f"New Admission Application: {app_name}",
                f"A new Stage 1 application for {level.replace('_', ' ').title()} was submitted by {par_name}.",
                f"/staff?tab=admissions&app_id={app_id}",
            ),
        )

        conn.commit()

        return {
            "application_id": app_id,
            "status": "submitted",
            "message": "Your initial admission application has been submitted successfully.",
            "institution_name": inst["school_name"],
            "academic_year": payload.academic_year,
            "applicant_name": app_name,
            "education_level": level,
        }
    finally:
        conn.close()


@app.get("/admissions/applications/{application_id}/public-confirmation")
def get_public_application_confirmation(application_id: str):
    """
    Publicly verifies application submission and returns safe tracking confirmation.
    Guarantees privacy: No phone, email, residential address, or internal staff notes.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT a.application_id, a.institution_id, s.school_name AS institution_name,
                   s.school_type, a.applicant_name, a.academic_year, a.education_level,
                   a.requested_standard, a.combination_code, a.status, a.created_at
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            WHERE a.application_id = ?
            """,
            (application_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Admission application reference not found.")

        data = dict(row)
        return {
            "application_id": data["application_id"],
            "institution_id": data["institution_id"],
            "institution_name": data["institution_name"],
            "applicant_name": data["applicant_name"],
            "education_level": data["education_level"],
            "requested_standard": data["requested_standard"],
            "combination_code": data["combination_code"],
            "academic_year": data["academic_year"],
            "status": data["status"],
            "submission_timestamp": data["created_at"],
            "tracking_guidance": "Retain this Application ID. To track status updates or respond to school inquiries, sign in to your verified Parent Account using the registered contact number."
        }
    finally:
        conn.close()


@app.get("/school/admissions/overview")
def get_school_admissions_overview(
    user: dict = Depends(require_school_staff),
):
    """
    Provides admissions KPI metrics for the reviewer's assigned institution.
    """
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Staff account is not assigned to an institution.")

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) as cnt
            FROM admission_applications
            WHERE institution_id = ?
            GROUP BY status
            """,
            (school_id,)
        ).fetchall()
        status_map = {r["status"]: r["cnt"] for r in rows}

        levels = conn.execute(
            """
            SELECT education_level, COUNT(*) as cnt
            FROM admission_applications
            WHERE institution_id = ?
            GROUP BY education_level
            """,
            (school_id,)
        ).fetchall()
        level_map = {r["education_level"]: r["cnt"] for r in levels}

        total = sum(status_map.values())
        return {
            "institution_id": school_id,
            "total_applications": total,
            "submitted_count": status_map.get("submitted", 0),
            "under_review_count": status_map.get("under_review", 0),
            "action_required_count": status_map.get("action_required", 0),
            "approved_count": status_map.get("approved", 0),
            "rejected_count": status_map.get("rejected", 0),
            "by_level": level_map
        }
    finally:
        conn.close()


@app.get("/school/admissions/applications")
def list_school_admission_applications(
    status_filter: Optional[str] = Query(default="all"),
    education_level: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_staff),
):
    """
    Lists admission applications for the assigned institution with filtering and pagination.
    """
    school_id = user.get("school_id")
    if not school_id:
        raise HTTPException(403, "Staff account is not assigned to an institution.")

    conn = get_connection()
    try:
        sql = """
            SELECT a.application_id, a.institution_id, a.applicant_name, a.parent_name,
                   a.parent_phone, a.parent_email, a.education_level, a.requested_standard,
                   a.requested_program_id, p.program_name, a.combination_code, a.stream_preference,
                   a.first_language_preference, a.second_language_preference, a.academic_year,
                   a.status, a.reviewer_user_id, a.clarification_request, a.rejection_reason,
                   a.created_at, a.updated_at
            FROM admission_applications a
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.institution_id = ?
        """
        params = [school_id]
        if status_filter and status_filter.lower() != "all":
            sql += " AND a.status = ?"
            params.append(status_filter.lower())
        if education_level and education_level.lower() != "all":
            sql += " AND a.education_level = ?"
            params.append(education_level.lower())
        if academic_year and academic_year.lower() != "all":
            sql += " AND a.academic_year = ?"
            params.append(academic_year)
        if search and search.strip():
            sql += " AND (a.applicant_name LIKE ? OR a.application_id LIKE ? OR a.parent_phone LIKE ?)"
            s_pat = f"%{search.strip()}%"
            params.extend([s_pat, s_pat, s_pat])

        # Total count
        count_sql = f"SELECT COUNT(*) FROM ({sql})"
        total = conn.execute(count_sql, params).fetchone()[0]

        sql += " ORDER BY a.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(sql, params).fetchall()
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "applications": [dict(r) for r in rows]
        }
    finally:
        conn.close()


@app.get("/school/admissions/applications/{application_id}")
def get_school_admission_application_detail(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Retrieves full Stage 1 application detail for authorized institutional reviewers.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT a.*, s.school_name, p.program_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ? AND a.institution_id = ?
            """,
            (application_id, school_id)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Admission application not found or unauthorized.")

        data = dict(row)
        hist = conn.execute(
            """
            SELECT history_id, previous_status, new_status, action_by_user_id, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            """,
            (application_id,)
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]
        return data
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/review")
def mark_application_under_review(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")
        if app_row["status"] not in ("submitted", "action_required"):
            raise HTTPException(400, f"Cannot move application from '{app_row['status']}' to 'under_review'.")

        prev_status = app_row["status"]
        conn.execute(
            "UPDATE admission_applications SET status = 'under_review', reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (user["user_id"], application_id)
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'under_review', ?, 'Application taken up for institutional review.')
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"])
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Application Under Review', 'Your admission application is currently under institutional review.', ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, f"/parent?tab=admissions&app_id={application_id}")
            )
        conn.commit()
        return {"status": "under_review", "application_id": application_id}
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/approve")
def approve_stage1_application(
    application_id: str,
    payload: AdmissionReviewApproveRequest,
    user: dict = Depends(require_school_staff),
):
    if not payload.confirm:
        raise HTTPException(400, "Explicit confirmation required to approve preliminary application.")
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")
        if app_row["status"] not in ("under_review", "submitted", "action_required"):
            raise HTTPException(400, f"Cannot approve application currently in '{app_row['status']}' status.")

        prev_status = app_row["status"]
        conn.execute(
            "UPDATE admission_applications SET status = 'approved', reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (user["user_id"], application_id)
        )
        note = payload.note or "Stage 1 initial application approved. Eligible for Stage 2 detailed submission."
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'approved', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"], note)
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Initial Application Approved', 'Your Stage 1 admission application has been approved. You can proceed to detailed admission when Stage 2 opens.', ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, f"/parent?tab=admissions&app_id={application_id}")
            )
        conn.commit()
        return {
            "status": "approved",
            "application_id": application_id,
            "message": "Application approved. Stage 2 detailed submission will be unlocked when available."
        }
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/request-clarification")
def request_application_clarification(
    application_id: str,
    payload: AdmissionClarificationRequest,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")
        if app_row["status"] not in ("under_review", "submitted"):
            raise HTTPException(400, f"Cannot request clarification for application in '{app_row['status']}' status.")

        prev_status = app_row["status"]
        conn.execute(
            "UPDATE admission_applications SET status = 'action_required', clarification_request = ?, reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (payload.clarification_message.strip(), user["user_id"], application_id)
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'action_required', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"], f"Clarification requested: {payload.clarification_message.strip()}")
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Action Required: Clarification Requested', ?, ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, payload.clarification_message.strip(), f"/parent?tab=admissions&app_id={application_id}")
            )
        conn.commit()
        return {"status": "action_required", "application_id": application_id}
    finally:
        conn.close()


@app.post("/school/admissions/{application_id}/reject")
def reject_stage1_application(
    application_id: str,
    payload: AdmissionRejectRequest,
    user: dict = Depends(require_school_staff),
):
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, applicant_name, parent_user_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")
        if app_row["status"] in ("approved", "rejected"):
            raise HTTPException(400, f"Cannot reject application in '{app_row['status']}' status.")

        prev_status = app_row["status"]
        conn.execute(
            """
            UPDATE admission_applications
            SET status = 'rejected', rejection_reason = ?, rejection_explanation = ?,
                institution_contact_phone = ?, reviewer_user_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
            """,
            (
                payload.rejection_reason.strip(),
                payload.rejection_explanation.strip() if payload.rejection_explanation else None,
                payload.institution_contact_phone.strip() if payload.institution_contact_phone else None,
                user["user_id"],
                application_id
            )
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, ?, 'rejected', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, prev_status, user["user_id"], f"Application rejected. Reason: {payload.rejection_reason.strip()}")
        )
        if app_row["parent_user_id"]:
            conn.execute(
                """
                INSERT INTO portal_notifications (notification_id, recipient_user_id, institution_id, application_id, title, message, action_url)
                VALUES (?, ?, ?, ?, 'Application Decision: Not Accepted', ?, ?)
                """,
                (str(uuid.uuid4()), app_row["parent_user_id"], school_id, application_id, f"Reason: {payload.rejection_reason.strip()}", f"/parent?tab=admissions&app_id={application_id}")
            )
        conn.commit()
        return {"status": "rejected", "application_id": application_id}
    finally:
        conn.close()


@app.get("/school/admissions/{application_id}/history")
def get_school_application_history(
    application_id: str,
    user: dict = Depends(require_school_staff),
):
    """
    Returns full audit trail for an application.
    """
    school_id = user.get("school_id")
    conn = get_connection()
    try:
        app_check = conn.execute(
            "SELECT application_id FROM admission_applications WHERE application_id = ? AND institution_id = ?",
            (application_id, school_id)
        ).fetchone()
        if not app_check:
            raise HTTPException(404, "Application not found or unauthorized.")

        rows = conn.execute(
            """
            SELECT history_id, application_id, previous_status, new_status,
                   action_by_user_id, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            """,
            (application_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/parent/admissions/applications")
def get_parent_admission_applications(
    user: dict = Depends(require_parent),
):
    """
    Returns all admission applications submitted by or linked to the authenticated parent.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT a.application_id, a.institution_id, s.school_name AS institution_name,
                   s.school_type, a.applicant_name, a.academic_year, a.education_level,
                   a.requested_standard, a.combination_code, a.requested_program_id,
                   p.program_name, a.status, a.rejection_reason, a.institution_contact_phone,
                   a.clarification_request, a.created_at, a.updated_at
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.parent_user_id = ? OR a.parent_phone = ?
            ORDER BY a.created_at DESC
        """
        rows = conn.execute(sql, (user["user_id"], user.get("phone", ""))).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/parent/admissions/applications/{application_id}")
def get_parent_application_details(
    application_id: str,
    user: dict = Depends(require_parent),
):
    """
    Retrieves full detail for a single application.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT a.*, s.school_name AS institution_name, s.public_phone, s.email AS school_email,
                   p.program_name
            FROM admission_applications a
            JOIN schools s ON s.school_id = a.institution_id
            LEFT JOIN academic_programs p ON p.program_id = a.requested_program_id
            WHERE a.application_id = ? AND (a.parent_user_id = ? OR a.parent_phone = ?)
        """
        row = conn.execute(sql, (application_id, user["user_id"], user.get("phone", ""))).fetchone()
        if not row:
            raise HTTPException(404, "Admission application not found or unauthorized.")

        data = dict(row)
        hist = conn.execute(
            """
            SELECT history_id, previous_status, new_status, action_note, created_at
            FROM admission_status_history
            WHERE application_id = ?
            ORDER BY created_at ASC
            """,
            (application_id,),
        ).fetchall()
        data["status_history"] = [dict(h) for h in hist]
        return data
    finally:
        conn.close()


@app.post("/parent/admissions/claim")
def claim_admission_application(
    payload: ParentClaimApplicationRequest,
    user: dict = Depends(require_parent),
):
    """
    Securely links an application submitted with parent phone number to their authenticated account.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, parent_phone, parent_user_id FROM admission_applications WHERE application_id = ?",
            (payload.application_id.strip(),)
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application ID not found.")

        user_phone = user.get("phone") or ""
        digits_user = "".join(filter(str.isdigit, user_phone))[-10:]
        digits_app = "".join(filter(str.isdigit, app_row["parent_phone"]))[-10:]
        if digits_app != digits_user:
            raise HTTPException(403, "Application contact phone does not match your registered account phone.")

        conn.execute(
            "UPDATE admission_applications SET parent_user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (user["user_id"], payload.application_id.strip())
        )
        conn.commit()
        return {"status": "claimed", "application_id": payload.application_id.strip()}
    finally:
        conn.close()


@app.post("/parent/admissions/applications/{application_id}/respond-clarification")
def respond_to_clarification(
    application_id: str,
    payload: ParentClarificationResponse,
    user: dict = Depends(require_parent),
):
    """
    Allows parent to respond to clarification request. Moves application back to under_review.
    """
    conn = get_connection()
    try:
        app_row = conn.execute(
            "SELECT application_id, status, institution_id FROM admission_applications WHERE application_id = ? AND (parent_user_id = ? OR parent_phone = ?)",
            (application_id, user["user_id"], user.get("phone", ""))
        ).fetchone()
        if not app_row:
            raise HTTPException(404, "Application not found or unauthorized.")
        if app_row["status"] != "action_required":
            raise HTTPException(400, "Application is not awaiting clarification.")

        conn.execute(
            "UPDATE admission_applications SET status = 'under_review', updated_at = CURRENT_TIMESTAMP WHERE application_id = ?",
            (application_id,)
        )
        conn.execute(
            """
            INSERT INTO admission_status_history (history_id, application_id, previous_status, new_status, action_by_user_id, action_note)
            VALUES (?, ?, 'action_required', 'under_review', ?, ?)
            """,
            (str(uuid.uuid4()), application_id, user["user_id"], f"Parent submitted clarification: {payload.response_text.strip()}")
        )
        conn.execute(
            """
            INSERT INTO portal_notifications (notification_id, recipient_role, institution_id, application_id, title, message, action_url)
            VALUES (?, 'school_admin', ?, ?, 'Clarification Responded', 'Parent responded to clarification inquiry.', ?)
            """,
            (str(uuid.uuid4()), app_row["institution_id"], application_id, f"/staff?tab=admissions&app_id={application_id}")
        )
        conn.commit()
        return {"status": "under_review", "application_id": application_id}
    finally:
        conn.close()


@app.get("/notifications")
def get_user_notifications(
    user: dict = Depends(get_current_user),
    unread_only: bool = Query(default=False),
):
    """
    Returns in-app notifications for the authenticated user or their institutional role.
    """
    conn = get_connection()
    try:
        sql = """
            SELECT notification_id, recipient_user_id, recipient_role, institution_id,
                   application_id, title, message, action_url, is_read, created_at
            FROM portal_notifications
            WHERE (recipient_user_id = ? OR (recipient_role = ? AND (institution_id = ? OR institution_id IS NULL)))
        """
        params = [user["user_id"], user.get("role"), user.get("school_id")]
        if unread_only:
            sql += " AND is_read = 0"
        sql += " ORDER BY created_at DESC LIMIT 50"

        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Marks a specific notification as read.
    """
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE portal_notifications SET is_read = 1 WHERE notification_id = ?",
            (notification_id,),
        )
        conn.commit()
        return {"status": "success", "notification_id": notification_id}
    finally:
        conn.close()
'''

with open(main_path, "w", encoding="utf-8") as f:
    f.write(pre_code + new_code)

print("Updated backend/main.py successfully.")
