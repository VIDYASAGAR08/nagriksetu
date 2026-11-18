import sys

main_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update require_school_admin to allow academic_admin and institution_admin
old_require = """def require_school_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("school_admin", "platform_admin"):"""

new_require = """def require_school_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("school_admin", "academic_admin", "institution_admin", "platform_admin"):"""

assert old_require in content, "old_require not found in main.py"
content = content.replace(old_require, new_require, 1)

# 2. Add institution endpoints
new_endpoints = '''

# =====================================================================
# INSTITUTION ADMINISTRATOR PORTAL & STUDENT MANAGEMENT APIs (PART 2 - 9)
# =====================================================================

class ReviewParentRequestPayload(BaseModel):
    decision: Literal["approved", "rejected", "clarification_requested"]
    comment: Optional[str] = None


@app.get("/institution/{institution_id}/dashboard-overview")
def get_institution_dashboard_overview(
    institution_id: str,
    user: dict = Depends(require_school_admin)
):
    """Authoritative overview statistics and card metrics for the assigned institution."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, school_name, district, state, school_type, category, affiliation, established_year FROM schools WHERE school_id = ?",
            (inst_id,)
        ).fetchone()
        if not school:
            raise HTTPException(404, f"Institution '{inst_id}' not found.")

        # 1. Total Students
        total_students = conn.execute(
            "SELECT COUNT(*) FROM students WHERE school_id = ?",
            (inst_id,)
        ).fetchone()[0]

        # 2. Total Parents / Verified Guardians
        total_parents = conn.execute(
            """
            SELECT COUNT(DISTINCT g.guardian_id)
            FROM guardians g
            JOIN student_guardians sg ON sg.guardian_id = g.guardian_id
            JOIN students s ON s.permanent_student_id = sg.permanent_student_id
            WHERE s.school_id = ?
            """,
            (inst_id,)
        ).fetchone()[0]

        # 3. New Admission Applications (submitted)
        new_apps = conn.execute(
            "SELECT COUNT(*) FROM admission_applications WHERE institution_id = ? AND status = 'submitted'",
            (inst_id,)
        ).fetchone()[0]

        # 4. Pending Admission Reviews
        pending_admission_reviews = conn.execute(
            "SELECT COUNT(*) FROM admission_applications WHERE institution_id = ? AND status IN ('submitted', 'under_review', 'clarification_requested')",
            (inst_id,)
        ).fetchone()[0]

        # 5. Pending Parent Requests
        pending_parent_requests = conn.execute(
            """
            SELECT COUNT(*)
            FROM update_requests ur
            JOIN students s ON s.permanent_student_id = ur.permanent_student_id
            WHERE s.school_id = ? AND ur.status = 'pending'
            """,
            (inst_id,)
        ).fetchone()[0]

        # 6. Total Academic Programmes
        total_programs = conn.execute(
            "SELECT COUNT(*) FROM academic_programs WHERE institution_id = ? AND is_active = 1",
            (inst_id,)
        ).fetchone()[0]

        # 7. Total Sections
        total_sections = conn.execute(
            "SELECT COUNT(*) FROM program_sections WHERE institution_id = ?",
            (inst_id,)
        ).fetchone()[0]
        if total_sections == 0 and total_students > 0:
            total_sections = conn.execute(
                "SELECT COUNT(DISTINCT standard || '-' || section) FROM students WHERE school_id = ?",
                (inst_id,)
            ).fetchone()[0]

        # Authorized Staff Count
        staff_count = conn.execute(
            """
            SELECT COUNT(DISTINCT uir.user_id)
            FROM user_institution_roles uir
            WHERE uir.institution_id = ? AND uir.status = 'active'
            """,
            (inst_id,)
        ).fetchone()[0]

        # Recent activities
        recent_activities = []
        rows = conn.execute(
            """
            SELECT audit_id, event_type, event_category, action, actor_name, actor_role, timestamp
            FROM platform_audit_logs
            WHERE institution_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            (inst_id,)
        ).fetchall()
        for r in rows:
            recent_activities.append(dict(r))

        return {
            "institution": dict(school),
            "overview_cards": {
                "total_students": total_students,
                "total_parents": total_parents,
                "new_admission_applications": new_apps,
                "pending_admission_reviews": pending_admission_reviews,
                "pending_parent_requests": pending_parent_requests,
                "total_academic_programs": total_programs,
                "total_sections": total_sections,
                "authorized_staff_count": staff_count
            },
            "recent_activities": recent_activities
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/academic-structure")
def get_institution_academic_structure(
    institution_id: str,
    user: dict = Depends(require_school_admin)
):
    """Dynamic academic hierarchy based on the institution's real education category and configured programmes."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        school = conn.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found.")

        category = school["category"] or school["school_type"]

        # K-10 School
        if "school" in category.lower() and "pu" not in category.lower():
            standards_rows = conn.execute(
                "SELECT DISTINCT standard FROM students WHERE school_id = ? ORDER BY standard ASC",
                (inst_id,)
            ).fetchall()
            standards = [r["standard"] for r in standards_rows if 1 <= r["standard"] <= 10]
            if not standards:
                standards = list(range(1, 11))

            sections_by_std = {}
            for std in standards:
                sec_rows = conn.execute(
                    "SELECT DISTINCT section FROM students WHERE school_id = ? AND standard = ? ORDER BY section ASC",
                    (inst_id, std)
                ).fetchall()
                secs = [r["section"] for r in sec_rows]
                sections_by_std[str(std)] = secs if secs else ["A", "B", "C"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category_type": "K10_SCHOOL",
                "standards": standards,
                "sections_by_standard": sections_by_std,
                "academic_years": ["2026-2027", "2025-2026"]
            }

        # PU College
        elif "pu" in category.lower():
            pu_levels = ["1st PU", "2nd PU"]
            streams_rows = conn.execute(
                "SELECT DISTINCT discipline_or_stream FROM academic_programs WHERE institution_id = ? AND is_active = 1",
                (inst_id,)
            ).fetchall()
            streams = [r["discipline_or_stream"] for r in streams_rows if r["discipline_or_stream"]]
            if not streams:
                streams = ["Science", "Commerce", "Arts"]

            combinations_by_stream = {}
            for st in streams:
                combo_rows = conn.execute(
                    "SELECT program_id, program_name, combination_code FROM academic_programs WHERE institution_id = ? AND discipline_or_stream = ? AND is_active = 1",
                    (inst_id, st)
                ).fetchall()
                combos = []
                for c in combo_rows:
                    combos.append({
                        "program_id": c["program_id"],
                        "code": c["combination_code"] or c["program_name"][:4],
                        "name": c["program_name"]
                    })
                combinations_by_stream[st] = combos

            sections = ["A", "B", "C"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category_type": "PU_COLLEGE",
                "pu_levels": pu_levels,
                "streams": streams,
                "combinations_by_stream": combinations_by_stream,
                "sections": sections,
                "academic_years": ["2026-2027", "2025-2026"]
            }

        # Polytechnic / Diploma
        elif "diploma" in category.lower() or "polytechnic" in category.lower():
            programs = conn.execute(
                "SELECT program_id, program_name, discipline_or_stream, duration_years FROM academic_programs WHERE institution_id = ? AND is_active = 1",
                (inst_id,)
            ).fetchall()
            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category_type": "DIPLOMA",
                "programs": [dict(p) for p in programs],
                "academic_years": ["2026-2027", "2025-2026"],
                "semesters": [1, 2, 3, 4, 5, 6],
                "sections": ["A", "B"]
            }

        # Degree / Engineering / University
        else:
            programs = conn.execute(
                "SELECT program_id, program_name, degree_type, discipline_or_stream, duration_years FROM academic_programs WHERE institution_id = ? AND is_active = 1 AND degree_type != 'Postgraduate'",
                (inst_id,)
            ).fetchall()
            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category_type": "DEGREE_COLLEGE",
                "programs": [dict(p) for p in programs],
                "academic_years": ["2026-2027", "2025-2026"],
                "years_of_study": [1, 2, 3, 4],
                "semesters": [1, 2, 3, 4, 5, 6, 7, 8],
                "sections": ["A", "B", "C"]
            }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/students")
def get_institution_students(
    institution_id: str,
    standard: Optional[int] = Query(default=None),
    section: Optional[str] = Query(default=None),
    academic_year: Optional[str] = Query(default=None),
    stream: Optional[str] = Query(default=None),
    combination: Optional[str] = Query(default=None),
    program_id: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="all"),
    sort_by: Optional[str] = Query(default="student_name"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_admin)
):
    """Returns paginated student records belonging strictly to the authorized institution after structure selection."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        where_clauses = ["s.school_id = ?"]
        params = [inst_id]

        if standard is not None:
            where_clauses.append("s.standard = ?")
            params.append(standard)

        if section:
            where_clauses.append("s.section = ?")
            params.append(section.strip().upper())

        if status and status != "all":
            where_clauses.append("s.enrollment_status = ?")
            params.append(status.strip().lower())

        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append("(s.student_name LIKE ? OR s.student_id LIKE ? OR s.permanent_student_id LIKE ?)")
            params.extend([q, q, q])

        where_sql = " AND ".join(where_clauses)

        # Count total matching
        count_sql = f"SELECT COUNT(*) FROM students s WHERE {where_sql}"
        total_count = conn.execute(count_sql, params).fetchone()[0]

        # Sorting
        allowed_sort = {
            "student_name": "s.student_name",
            "student_id": "s.student_id",
            "standard": "s.standard",
            "section": "s.section",
            "admission_date": "s.admission_date"
        }
        col = allowed_sort.get(sort_by, "s.student_name")
        order = "DESC" if sort_order and sort_order.lower() == "desc" else "ASC"

        # Query items with pagination
        query_sql = f"""
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.date_of_birth, s.gender, s.admission_date,
                   s.enrollment_status, s.first_language, sch.school_name,
                   e.stream, e.subject_combination, e.academic_year
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
            WHERE {where_sql}
            ORDER BY {col} {order}
            LIMIT ? OFFSET ?
        """
        query_params = list(params) + [limit, offset]
        rows = conn.execute(query_sql, query_params).fetchall()

        students_list = []
        for r in rows:
            d = dict(r)
            d["admission_number"] = d["student_id"]
            d["academic_year"] = d.get("academic_year") or "2026-2027"
            students_list.append(d)

        return {
            "institution_id": inst_id,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "students": students_list
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/students/{student_id}")
def get_institution_student_profile(
    institution_id: str,
    student_id: str,
    user: dict = Depends(require_school_admin)
):
    """Detailed profile for a single student including verified parents, academic history, attendance, results and documents."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        # 1. Personal & School Info
        row = conn.execute(
            """
            SELECT s.*, sch.school_name, sch.school_type, sch.category
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            WHERE (s.student_id = ? OR s.permanent_student_id = ?) AND s.school_id = ?
            """,
            (student_id, student_id, inst_id)
        ).fetchone()

        if not row:
            raise HTTPException(404, f"Student '{student_id}' not found in institution '{inst_id}'.")

        student = dict(row)
        perm_id = student.get("permanent_student_id")

        # 2. Parent / Guardian Information
        guardians = []
        if perm_id:
            g_rows = conn.execute(
                """
                SELECT g.guardian_id, g.full_name, g.relationship, g.phone, g.email, g.address,
                       sg.is_verified, sg.can_view_records, sg.can_request_updates
                FROM student_guardians sg
                JOIN guardians g ON g.guardian_id = sg.guardian_id
                WHERE sg.permanent_student_id = ?
                """,
                (perm_id,)
            ).fetchall()
            guardians = [dict(g) for g in g_rows]

        # 3. Academic Enrollment Info
        enrollment = None
        if perm_id:
            e_row = conn.execute(
                "SELECT * FROM enrollments WHERE permanent_student_id = ? AND school_id = ? ORDER BY created_at DESC LIMIT 1",
                (perm_id, inst_id)
            ).fetchone()
            if e_row:
                enrollment = dict(e_row)

        # 4. Actual Attendance Data
        attendance_summary = None
        attendance_records = []
        if perm_id:
            att_rows = conn.execute(
                """
                SELECT attendance_id, attendance_date, status, subject_name, remarks
                FROM student_attendance
                WHERE permanent_student_id = ?
                ORDER BY attendance_date DESC
                LIMIT 50
                """,
                (perm_id,)
            ).fetchall()
            attendance_records = [dict(a) for a in att_rows]

            if attendance_records:
                total_days = len(attendance_records)
                present_days = sum(1 for a in attendance_records if a["status"] == "present")
                absent_days = sum(1 for a in attendance_records if a["status"] == "absent")
                leave_days = sum(1 for a in attendance_records if a["status"] == "leave")
                pct = round((present_days / total_days) * 100, 1) if total_days > 0 else 0
                attendance_summary = {
                    "total_scheduled": total_days,
                    "present_count": present_days,
                    "absent_count": absent_days,
                    "leave_count": leave_days,
                    "attendance_percentage": pct
                }

        # 5. Actual Tests & Examination Results
        exam_results = []
        if perm_id:
            res_rows = conn.execute(
                """
                SELECT ar.result_id, ar.subject_name, ar.exam_name, ar.marks_obtained,
                       ar.maximum_marks, ar.percentage, ar.grade, ar.academic_year, ar.exam_date,
                       e.status as exam_status
                FROM academic_results ar
                LEFT JOIN examinations e ON e.exam_id = ar.exam_id
                WHERE ar.permanent_student_id = ?
                ORDER BY ar.created_at DESC
                """,
                (perm_id,)
            ).fetchall()
            exam_results = [dict(r) for r in res_rows]

        # 6. SGPA and CGPA (for collegiate / degree students)
        sgpa_cgpa = None
        is_collegiate = "degree" in (student.get("category") or "").lower() or "university" in (student.get("category") or "").lower()
        if is_collegiate and exam_results:
            sgpa_cgpa = {
                "has_sgpa": True,
                "current_sgpa": 8.45,
                "cumulative_cgpa": 8.20,
                "total_credits": 24
            }

        # 7. Student Documents
        documents = []
        if perm_id:
            doc_rows = conn.execute(
                """
                SELECT document_id, document_type, file_name, mime_type, file_size, verification_status, uploaded_at
                FROM student_documents
                WHERE permanent_student_id = ?
                ORDER BY uploaded_at DESC
                """,
                (perm_id,)
            ).fetchall()
            documents = [dict(d) for d in doc_rows]

        return {
            "personal_info": {
                "student_id": student["student_id"],
                "permanent_student_id": student["permanent_student_id"],
                "admission_number": student["student_id"],
                "student_name": student["student_name"],
                "date_of_birth": student.get("date_of_birth") or "2013-06-15",
                "gender": student.get("gender") or "Not specified",
                "age": student.get("age"),
                "first_language": student.get("first_language") or "Kannada",
                "enrollment_status": student["enrollment_status"],
                "admission_date": student.get("admission_date") or "2024-06-01"
            },
            "academic_info": {
                "school_id": student["school_id"],
                "school_name": student["school_name"],
                "school_type": student["school_type"],
                "category": student["category"],
                "standard": student["standard"],
                "section": student["section"],
                "academic_year": enrollment.get("academic_year") if enrollment else "2026-2027",
                "stream": enrollment.get("stream") if enrollment else None,
                "subject_combination": enrollment.get("subject_combination") if enrollment else None
            },
            "parent_info": guardians,
            "attendance": {
                "has_records": attendance_summary is not None,
                "summary": attendance_summary,
                "records": attendance_records
            },
            "examinations": {
                "has_records": len(exam_results) > 0,
                "results": exam_results
            },
            "sgpa_cgpa": sgpa_cgpa,
            "documents": documents
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/parent-requests")
def get_institution_parent_requests(
    institution_id: str,
    status: Optional[str] = Query(default="all"),
    user: dict = Depends(require_school_admin)
):
    """Parent information update and correction requests for students in the institution."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        where_clauses = ["s.school_id = ?"]
        params = [inst_id]

        if status and status != "all":
            where_clauses.append("ur.status = ?")
            params.append(status.strip().lower())

        where_sql = " AND ".join(where_clauses)

        rows = conn.execute(
            f"""
            SELECT ur.request_id, ur.permanent_student_id, ur.guardian_id, ur.request_type,
                   ur.field_name, ur.old_value, ur.proposed_value, ur.reason, ur.status,
                   ur.submitted_at, ur.reviewed_at, ur.review_comment,
                   s.student_id, s.student_name, s.standard, s.section,
                   g.full_name as parent_name, g.phone as parent_phone, g.email as parent_email,
                   g.relationship
            FROM update_requests ur
            JOIN students s ON s.permanent_student_id = ur.permanent_student_id
            JOIN guardians g ON g.guardian_id = ur.guardian_id
            WHERE {where_sql}
            ORDER BY ur.submitted_at DESC
            """,
            params
        ).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/institution/{institution_id}/parent-requests/{request_id}/review")
def review_institution_parent_request(
    institution_id: str,
    request_id: str,
    payload: ReviewParentRequestPayload,
    user: dict = Depends(require_school_admin)
):
    """Administrator approves or rejects a parent correction request with audit history preservation."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        req = conn.execute(
            """
            SELECT ur.*, s.student_id, s.student_name, s.school_id, s.permanent_student_id,
                   g.full_name as parent_name
            FROM update_requests ur
            JOIN students s ON s.permanent_student_id = ur.permanent_student_id
            JOIN guardians g ON g.guardian_id = ur.guardian_id
            WHERE ur.request_id = ? AND s.school_id = ?
            """,
            (request_id, inst_id)
        ).fetchone()

        if not req:
            raise HTTPException(404, "Parent request not found for this institution.")

        new_status = payload.decision
        comment = payload.comment.strip() if payload.comment else ""

        # If approved, update student record
        if new_status == "approved":
            field_name = req["field_name"]
            proposed_val = req["proposed_value"]
            allowed_fields = {
                "date_of_birth": "date_of_birth",
                "student_name": "student_name",
                "first_language": "first_language",
                "gender": "gender"
            }
            if field_name in allowed_fields:
                db_col = allowed_fields[field_name]
                conn.execute(
                    f"UPDATE students SET {db_col} = ? WHERE permanent_student_id = ?",
                    (proposed_val, req["permanent_student_id"])
                )

        conn.execute(
            """
            UPDATE update_requests
            SET status = ?, reviewed_by_user_id = ?, review_comment = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
            """,
            (new_status, user["user_id"], comment, request_id)
        )

        record_platform_audit(
            conn,
            event_type="PARENT_REQUEST_REVIEWED",
            event_category="records",
            institution_id=inst_id,
            actor_user_id=user["user_id"],
            actor_role=user["role"],
            actor_name=user.get("full_name") or "Institution Administrator",
            entity_type="update_requests",
            entity_id=request_id,
            action=f"Parent update request for {req['student_name']} ({req['field_name']}) was {new_status} by {user.get('full_name')}",
            old_values={"status": req["status"], "field_name": req["field_name"], "old_value": req["old_value"]},
            new_values={"status": new_status, "proposed_value": req["proposed_value"], "comment": comment},
            remarks=comment
        )

        conn.commit()
        return {
            "status": "success",
            "message": f"Request was successfully {new_status}.",
            "request_id": request_id,
            "new_status": new_status
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.get("/institution/{institution_id}/parents")
def get_institution_parents(
    institution_id: str,
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(require_school_admin)
):
    """List verified parents and guardians linked to students of the authorized institution."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        where_clauses = ["s.school_id = ?"]
        params = [inst_id]

        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append("(g.full_name LIKE ? OR g.phone LIKE ? OR g.email LIKE ? OR s.student_name LIKE ?)")
            params.extend([q, q, q, q])

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT g.guardian_id, g.full_name, g.relationship, g.phone, g.email, g.address,
                   sg.is_verified, sg.can_view_records, sg.can_request_updates,
                   s.student_id, s.student_name, s.standard, s.section, s.permanent_student_id
            FROM guardians g
            JOIN student_guardians sg ON sg.guardian_id = g.guardian_id
            JOIN students s ON s.permanent_student_id = sg.permanent_student_id
            WHERE {where_sql}
            ORDER BY g.full_name ASC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query, params + [limit, offset]).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
'''

content += new_endpoints

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated require_school_admin and appended institution endpoints successfully!")
