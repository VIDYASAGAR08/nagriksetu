import re

MAIN_PATH = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(MAIN_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# -----------------------------------------------------------------------------
# 1. Update search and division filter in get_institution_students
# -----------------------------------------------------------------------------
old_search_block = """        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append("(s.student_name LIKE ? OR s.student_id LIKE ? OR s.permanent_student_id LIKE ?)")
            params.extend([q, q, q])"""

new_search_block = """        if search and search.strip():
            q = f"%{search.strip()}%"
            where_clauses.append(\"\"\"(
                s.student_name LIKE ? OR s.student_id LIKE ? OR s.permanent_student_id LIKE ? OR
                s.permanent_student_id IN (
                    SELECT sg.permanent_student_id
                    FROM student_guardians sg
                    JOIN guardians g ON g.guardian_id = sg.guardian_id
                    WHERE g.full_name LIKE ? AND sg.is_verified = 1
                )
            )\"\"\")
            params.extend([q, q, q, q])

        if division_id and division_id != "all":
            div_val = division_id.strip().lower()
            if "school" in div_val or div_val == "k-10":
                where_clauses.append("s.standard BETWEEN 1 AND 10")
            elif "pu" in div_val:
                where_clauses.append("(s.standard IN (11, 12) OR s.puc_year IS NOT NULL)")
            elif "degree" in div_val or "college" in div_val:
                where_clauses.append("(s.standard IS NULL OR s.standard > 12)")"""

if old_search_block in content:
    content = content.replace(old_search_block, new_search_block, 1)
    print("Replaced search block.")
else:
    print("ERROR: old_search_block not found!")

# -----------------------------------------------------------------------------
# 2. Update query SQL in get_institution_students to include contacts & update info
# -----------------------------------------------------------------------------
old_query_sql = """        query_sql = f\"\"\"
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.date_of_birth, s.gender, s.admission_date,
                   s.enrollment_status, s.first_language, sch.school_name,
                   e.stream, e.subject_combination, e.academic_year
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
            WHERE {where_sql}
            GROUP BY s.student_id
            ORDER BY {col} {order}
            LIMIT ? OFFSET ?
        \"\"\"
        query_params = list(params) + [limit, offset]
        rows = conn.execute(query_sql, query_params).fetchall()

        students_list = []
        for r in rows:
            d = dict(r)
            d["admission_number"] = d["student_id"]
            d["academic_year"] = d.get("academic_year") or "2026-2027"
            # Clean display name
            d["student_name"] = re.sub(r"\\s+\\d{3,}$", "", d["student_name"]).strip()
            students_list.append(d)"""

new_query_sql = """        query_sql = f\"\"\"
            SELECT s.student_id, s.student_name, s.school_id, s.standard, s.section,
                   s.permanent_student_id, s.date_of_birth, s.gender, s.admission_date,
                   s.enrollment_status, s.first_language, s.contact_number, s.student_email,
                   s.updated_at, s.admission_number, s.puc_year, sch.school_name,
                   e.stream, e.subject_combination, e.academic_year
            FROM students s
            JOIN schools sch ON sch.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
            WHERE {where_sql}
            GROUP BY s.student_id
            ORDER BY {col} {order}
            LIMIT ? OFFSET ?
        \"\"\"
        query_params = list(params) + [limit, offset]
        rows = conn.execute(query_sql, query_params).fetchall()

        students_list = []
        for r in rows:
            d = dict(r)
            d["admission_number"] = d.get("admission_number") or d["student_id"]
            d["academic_year"] = d.get("academic_year") or "2026-2027"
            d["student_name"] = re.sub(r"\\s+\\d{3,}$", "", d["student_name"]).strip()

            std_val = d.get("standard")
            puc_yr = d.get("puc_year")
            if std_val and std_val <= 10:
                d["academic_division"] = "School Division"
                d["class_or_standard_display"] = f"Standard {std_val}"
            elif (std_val and std_val in (11, 12)) or puc_yr:
                d["academic_division"] = "PU Division"
                d["class_or_standard_display"] = puc_yr if puc_yr else ("1st PUC" if std_val == 11 else "2nd PUC")
            else:
                d["academic_division"] = "Higher Education / Degree Division"
                d["class_or_standard_display"] = f"Standard {std_val}" if std_val else "Degree"

            d["contact_info"] = d.get("contact_number") or d.get("student_email") or "—"
            d["last_updated"] = d.get("updated_at") or d.get("admission_date") or "—"
            students_list.append(d)"""

if old_query_sql in content:
    content = content.replace(old_query_sql, new_query_sql, 1)
    print("Replaced query sql block.")
else:
    print("ERROR: old_query_sql not found!")

# -----------------------------------------------------------------------------
# 3. Update get_institution_student_profile to include taluk, village_city, audits, and pending requests
# -----------------------------------------------------------------------------
old_pers_data_district = """            "address": student.get("address") or f"{student.get('district', 'Bengaluru Urban')}, Karnataka",
            "district": student.get("district") or "Bengaluru Urban","""

new_pers_data_district = """            "address": student.get("address") or f"{student.get('district', 'Bengaluru Urban')}, Karnataka",
            "district": student.get("district") or "Bengaluru Urban",
            "taluk": student.get("taluk") or "Bengaluru North",
            "village_city": student.get("village_city") or student.get("district") or "Bengaluru","""

if old_pers_data_district in content:
    content = content.replace(old_pers_data_district, new_pers_data_district, 1)
    print("Updated pers_data with taluk and village_city.")
else:
    print("ERROR: old_pers_data_district not found!")

old_profile_return = """            "documents": documents
        }
    finally:
        conn.close()"""

new_profile_return = """            "documents": documents,
            "record_history": [dict(a) for a in conn.execute(
                \"\"\"
                SELECT audit_id, student_id, permanent_student_id, field_modified,
                       previous_value, updated_value, reason, source, admin_name, created_at
                FROM student_record_audits
                WHERE student_id = ? OR permanent_student_id = ?
                ORDER BY created_at DESC
                \"\"\",
                (student["student_id"], perm_id)
            ).fetchall()],
            "pending_requests": [dict(r) for r in conn.execute(
                \"\"\"
                SELECT request_id, tracking_number, title, category, priority,
                       field_name, current_value, requested_value, status, submitted_at
                FROM service_requests
                WHERE (affected_student_id = ? OR permanent_student_id = ?)
                  AND status NOT IN ('RESOLVED', 'CLOSED', 'REJECTED')
                ORDER BY submitted_at DESC
                \"\"\",
                (student["student_id"], perm_id)
            ).fetchall()]
        }
    finally:
        conn.close()"""

if old_profile_return in content:
    content = content.replace(old_profile_return, new_profile_return, 1)
    print("Updated profile return with record_history and pending_requests.")
else:
    print("ERROR: old_profile_return not found!")

# -----------------------------------------------------------------------------
# 4. Append new Student Record Management Endpoints
# -----------------------------------------------------------------------------
new_endpoints_code = '''

# ==============================================================================
# NAGRIKSETU — INSTITUTION ADMIN STUDENT RECORD MANAGEMENT & EDITING MODULE
# ==============================================================================

class StudentRecordUpdatePayload(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500, description="Mandatory reason for updating student record")
    source: Optional[str] = "Direct Admin Edit"
    request_id: Optional[str] = None
    # Personal Info
    student_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    first_language: Optional[str] = None
    medium_of_instruction: Optional[str] = None
    contact_number: Optional[str] = None
    student_email: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    village_city: Optional[str] = None
    pincode: Optional[str] = None
    enrollment_status: Optional[str] = None
    admission_number: Optional[str] = None
    admission_date: Optional[str] = None
    # Academic Info
    standard: Optional[int] = None
    section: Optional[str] = None
    puc_year: Optional[str] = None
    stream: Optional[str] = None
    subject_combination: Optional[str] = None
    curriculum_or_board: Optional[str] = None
    academic_year: Optional[str] = None

class AttendanceCorrectionPayload(BaseModel):
    new_status: str = Field(..., description="Corrected status: present, absent, or leave")
    remarks: Optional[str] = None
    reason: str = Field(..., min_length=5, max_length=500, description="Mandatory reason for attendance correction")

class ExamResultCorrectionPayload(BaseModel):
    marks_obtained: float = Field(..., ge=0, description="Marks obtained")
    maximum_marks: Optional[float] = Field(None, gt=0, description="Maximum marks")
    grade: Optional[str] = None
    reason: str = Field(..., min_length=5, max_length=500, description="Mandatory reason for examination correction")

class StudentDocumentUploadPayload(BaseModel):
    document_name: str = Field(..., min_length=3, max_length=150)
    document_type: str = Field(..., min_length=3, max_length=100)
    file_name: str = Field(..., min_length=3, max_length=200)
    verification_status: Optional[str] = "verified"
    reason: str = Field(..., min_length=5, max_length=500)


@app.get("/institution/{institution_id}/student-management/stats")
def get_student_management_stats(
    institution_id: str,
    user: dict = Depends(require_school_admin)
):
    """Returns real-time operational metrics for Institution Admin Student Management Desk."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        school = conn.execute("SELECT school_id, school_name, school_type FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found.")

        tot = conn.execute("SELECT COUNT(*) FROM students WHERE school_id = ?", (inst_id,)).fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM students WHERE school_id = ? AND (enrollment_status = 'active' OR enrollment_status IS NULL)", (inst_id,)).fetchone()[0]
        inactive = conn.execute("SELECT COUNT(*) FROM students WHERE school_id = ? AND enrollment_status NOT IN ('active') AND enrollment_status IS NOT NULL", (inst_id,)).fetchone()[0]

        std_rows = conn.execute("""
            SELECT standard, puc_year, COUNT(*) as count
            FROM students
            WHERE school_id = ?
            GROUP BY standard, puc_year
            ORDER BY standard
        """, (inst_id,)).fetchall()

        by_standard = []
        for r in std_rows:
            std = r["standard"]
            puc = r["puc_year"]
            if puc:
                lbl = puc
            elif std and std <= 10:
                lbl = f"Standard {std}"
            elif std in (11, 12):
                lbl = f"{std}th (PUC)"
            else:
                lbl = f"Level {std}" if std else "Unclassified"
            by_standard.append({"standard": std, "puc_year": puc, "label": lbl, "count": r["count"]})

        rec_rows = conn.execute("""
            SELECT sra.audit_id, sra.student_id, sra.permanent_student_id, s.student_name,
                   sra.field_modified, sra.previous_value, sra.updated_value, sra.reason,
                   sra.source, sra.admin_name, sra.created_at
            FROM student_record_audits sra
            JOIN students s ON s.permanent_student_id = sra.permanent_student_id
            WHERE sra.institution_id = ?
            ORDER BY sra.created_at DESC
            LIMIT 10
        """, (inst_id,)).fetchall()

        pend_rows = conn.execute("""
            SELECT request_id, tracking_number, title, category, priority,
                   affected_person_name, affected_student_id, permanent_student_id,
                   field_name, current_value, requested_value, status, submitted_at
            FROM service_requests
            WHERE (assigned_institution_id = ? OR institution_id = ?)
              AND status IN ('PENDING', 'SUBMITTED', 'UNDER_INVESTIGATION', 'CLARIFICATION_PROVIDED')
            ORDER BY submitted_at DESC
            LIMIT 10
        """, (inst_id, inst_id)).fetchall()

        total_pending = conn.execute("""
            SELECT COUNT(*) FROM service_requests
            WHERE (assigned_institution_id = ? OR institution_id = ?)
              AND status IN ('PENDING', 'SUBMITTED', 'UNDER_INVESTIGATION', 'CLARIFICATION_PROVIDED')
        """, (inst_id, inst_id)).fetchone()[0]

        return {
            "institution_id": inst_id,
            "institution_name": school["school_name"],
            "total_students": tot,
            "active_students": active,
            "inactive_students": inactive,
            "by_standard": by_standard,
            "recently_updated": [dict(r) for r in rec_rows],
            "pending_correction_requests_count": total_pending,
            "pending_correction_requests": [dict(r) for r in pend_rows]
        }
    finally:
        conn.close()


@app.put("/institution/{institution_id}/students/{student_id}")
def update_institution_student(
    institution_id: str,
    student_id: str,
    payload: StudentRecordUpdatePayload,
    user: dict = Depends(require_school_admin)
):
    """
    Authorised Institution Admin Student Record Editor.
    Modifies permitted student personal & academic fields, enforces validation,
    protects immutable keys (Student ID, PSID, Institution ID), and records an immutable audit trail.
    """
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    admin_id = user.get("user_id", "ADMIN")
    admin_name = user.get("full_name") or user.get("email") or "Institution Administrator"

    conn = get_connection()
    try:
        student_row = conn.execute("""
            SELECT * FROM students
            WHERE (student_id = ? OR permanent_student_id = ?) AND school_id = ?
        """, (student_id, student_id, inst_id)).fetchone()

        if not student_row:
            raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found in institution '{inst_id}'.")

        student = dict(student_row)
        perm_id = student["permanent_student_id"]
        actual_student_id = student["student_id"]

        enr_row = conn.execute("""
            SELECT * FROM enrollments
            WHERE permanent_student_id = ? AND school_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (perm_id, inst_id)).fetchone()
        enr = dict(enr_row) if enr_row else {}

        # Validate Date of Birth
        if payload.date_of_birth is not None and payload.date_of_birth.strip():
            dob_val = payload.date_of_birth.strip()
            if not re.match(r"^\\d{4}-\\d{2}-\\d{2}$", dob_val):
                raise HTTPException(status_code=400, detail="Invalid date of birth format. Must be YYYY-MM-DD.")

        # Validate Contact Number
        if payload.contact_number is not None and payload.contact_number.strip():
            phone_clean = re.sub(r"[\\s\\-\\+\\(\\)]", "", payload.contact_number)
            if len(phone_clean) < 10 or not phone_clean.isdigit():
                raise HTTPException(status_code=400, detail="Invalid contact number. Must be a valid 10-digit phone number.")

        # Validate Email
        if payload.student_email is not None and payload.student_email.strip():
            if "@" not in payload.student_email or "." not in payload.student_email:
                raise HTTPException(status_code=400, detail="Invalid student email address format.")

        # Validate Academic Division constraints
        school_row = conn.execute("SELECT school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        cat_lower = ((school_row["category"] or "") + " " + (school_row["school_type"] or "")).lower()
        is_pure_school = "school" in cat_lower and "pu" not in cat_lower

        if is_pure_school:
            if payload.standard is not None and (payload.standard < 1 or payload.standard > 10):
                raise HTTPException(status_code=400, detail="Validation error: Standard for school education must be between 1 and 10.")
            if payload.puc_year or payload.stream or payload.subject_combination:
                raise HTTPException(status_code=400, detail="Validation error: PU stream/combination cannot be set for a K-10 school.")

        updated_student_fields = {}
        updated_enrollment_fields = {}
        audits_to_insert = []
        now_iso = datetime.datetime.now().isoformat()

        field_mapping_students = {
            "student_name": payload.student_name,
            "date_of_birth": payload.date_of_birth,
            "gender": payload.gender,
            "blood_group": payload.blood_group,
            "first_language": payload.first_language,
            "medium_of_instruction": payload.medium_of_instruction,
            "contact_number": payload.contact_number,
            "student_email": payload.student_email,
            "address": payload.address,
            "district": payload.district,
            "taluk": payload.taluk,
            "village_city": payload.village_city,
            "pincode": payload.pincode,
            "enrollment_status": payload.enrollment_status,
            "admission_number": payload.admission_number,
            "admission_date": payload.admission_date,
            "standard": payload.standard,
            "section": payload.section,
            "puc_year": payload.puc_year,
            "stream": payload.stream,
            "subject_combination": payload.subject_combination,
            "curriculum_or_board": payload.curriculum_or_board
        }

        for fname, val in field_mapping_students.items():
            if val is not None:
                new_str = str(val).strip()
                old_str = str(student.get(fname) or "").strip()
                if new_str != old_str:
                    updated_student_fields[fname] = val
                    audits_to_insert.append((
                        f"AUD-{uuid.uuid4().hex[:12].upper()}",
                        actual_student_id,
                        perm_id,
                        inst_id,
                        admin_id,
                        admin_name,
                        fname,
                        old_str if old_str else "(empty)",
                        new_str,
                        payload.reason.strip(),
                        payload.source or "Direct Admin Edit",
                        payload.request_id,
                        now_iso
                    ))

        enr_synced = ["standard", "section", "stream", "subject_combination", "puc_year", "curriculum_or_board", "first_language"]
        for fname in enr_synced:
            if fname in updated_student_fields and enr:
                updated_enrollment_fields[fname] = updated_student_fields[fname]

        if not updated_student_fields:
            return {
                "message": "No fields were modified. All submitted values match existing record.",
                "student_id": actual_student_id,
                "modified_fields": []
            }

        updated_student_fields["updated_at"] = now_iso
        set_clauses = [f"{k} = ?" for k in updated_student_fields.keys()]
        sql_stu = f"UPDATE students SET {', '.join(set_clauses)} WHERE permanent_student_id = ?"
        conn.execute(sql_stu, list(updated_student_fields.values()) + [perm_id])

        if updated_enrollment_fields and enr:
            updated_enrollment_fields["updated_at"] = now_iso
            set_enr = [f"{k} = ?" for k in updated_enrollment_fields.keys()]
            sql_enr = f"UPDATE enrollments SET {', '.join(set_enr)} WHERE permanent_student_id = ? AND school_id = ?"
            conn.execute(sql_enr, list(updated_enrollment_fields.values()) + [perm_id, inst_id])

        for a in audits_to_insert:
            conn.execute("""
                INSERT INTO student_record_audits (
                    audit_id, student_id, permanent_student_id, institution_id,
                    admin_user_id, admin_name, field_modified, previous_value,
                    updated_value, reason, source, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, a)

            conn.execute("""
                INSERT INTO platform_audit_logs (
                    id, event_type, event_category, institution_id, actor_user_id,
                    actor_name, actor_role, entity_type, entity_id, action,
                    old_values, new_values, remarks, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"EVT-{uuid.uuid4().hex[:10].upper()}",
                "STUDENT_RECORD_MODIFIED",
                "ADMIN_ACTION",
                inst_id,
                admin_id,
                admin_name,
                user.get("role", "institution_admin"),
                "student",
                actual_student_id,
                f"Updated {a[6]}",
                json.dumps({a[6]: a[7]}),
                json.dumps({a[6]: a[8]}),
                payload.reason.strip(),
                payload.request_id,
                now_iso
            ))

        conn.commit()

        return {
            "success": True,
            "message": f"Successfully updated {len(updated_student_fields)-1} field(s) for student {actual_student_id}.",
            "student_id": actual_student_id,
            "permanent_student_id": perm_id,
            "modified_fields": list(updated_student_fields.keys())
        }
    finally:
        conn.close()


@app.put("/institution/{institution_id}/students/{student_id}/attendance/{attendance_id}")
def correct_student_attendance(
    institution_id: str,
    student_id: str,
    attendance_id: str,
    payload: AttendanceCorrectionPayload,
    user: dict = Depends(require_school_admin)
):
    """Authorised Attendance Correction by Institution Admin."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    admin_id = user.get("user_id", "ADMIN")
    admin_name = user.get("full_name") or user.get("email") or "Institution Administrator"

    conn = get_connection()
    try:
        s_row = conn.execute("SELECT student_id, permanent_student_id FROM students WHERE (student_id = ? OR permanent_student_id = ?) AND school_id = ?", (student_id, student_id, inst_id)).fetchone()
        if not s_row:
            raise HTTPException(404, f"Student '{student_id}' not found in institution '{inst_id}'.")
        perm_id = s_row["permanent_student_id"]
        actual_sid = s_row["student_id"]

        att_row = conn.execute("SELECT * FROM student_attendance WHERE attendance_id = ? AND permanent_student_id = ?", (attendance_id, perm_id)).fetchone()
        if not att_row:
            raise HTTPException(404, f"Attendance record '{attendance_id}' not found for this student.")

        att = dict(att_row)
        old_status = att["status"]
        old_remarks = att.get("remarks") or ""
        new_status = payload.new_status.strip().lower()
        new_remarks = payload.remarks.strip() if payload.remarks else old_remarks

        if old_status == new_status and old_remarks == new_remarks:
            return {"message": "No changes made: submitted status and remarks match existing attendance record."}

        now_iso = datetime.datetime.now().isoformat()
        conn.execute("""
            UPDATE student_attendance
            SET status = ?, remarks = ?, updated_at = ?, recorded_by_user_id = ?
            WHERE attendance_id = ?
        """, (new_status, new_remarks, now_iso, admin_id, attendance_id))

        audit_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"
        conn.execute("""
            INSERT INTO student_record_audits (
                audit_id, student_id, permanent_student_id, institution_id,
                admin_user_id, admin_name, field_modified, previous_value,
                updated_value, reason, source, request_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id,
            actual_sid,
            perm_id,
            inst_id,
            admin_id,
            admin_name,
            f"attendance_{att.get('attendance_date', 'record')}",
            f"{old_status} ({old_remarks})" if old_remarks else old_status,
            f"{new_status} ({new_remarks})" if new_remarks else new_status,
            payload.reason.strip(),
            "Direct Admin Edit",
            None,
            now_iso
        ))

        conn.commit()

        return {
            "success": True,
            "message": f"Attendance record for {att.get('attendance_date')} corrected successfully.",
            "attendance_id": attendance_id,
            "previous_status": old_status,
            "new_status": new_status,
            "updated_at": now_iso
        }
    finally:
        conn.close()


@app.put("/institution/{institution_id}/students/{student_id}/results/{result_id}")
def correct_student_examination_result(
    institution_id: str,
    student_id: str,
    result_id: str,
    payload: ExamResultCorrectionPayload,
    user: dict = Depends(require_school_admin)
):
    """Authorised Examination Result Correction by Institution Admin."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    admin_id = user.get("user_id", "ADMIN")
    admin_name = user.get("full_name") or user.get("email") or "Institution Administrator"

    conn = get_connection()
    try:
        s_row = conn.execute("SELECT student_id, permanent_student_id FROM students WHERE (student_id = ? OR permanent_student_id = ?) AND school_id = ?", (student_id, student_id, inst_id)).fetchone()
        if not s_row:
            raise HTTPException(404, f"Student '{student_id}' not found in institution '{inst_id}'.")
        perm_id = s_row["permanent_student_id"]
        actual_sid = s_row["student_id"]

        res_row = conn.execute("SELECT * FROM academic_results WHERE result_id = ? AND permanent_student_id = ?", (result_id, perm_id)).fetchone()
        if not res_row:
            raise HTTPException(404, f"Examination result '{result_id}' not found for this student.")

        res = dict(res_row)
        old_marks = float(res["marks_obtained"])
        old_max = float(res.get("maximum_marks") or 100.0)
        old_grade = res.get("grade") or "N/A"

        new_marks = float(payload.marks_obtained)
        new_max = float(payload.maximum_marks) if payload.maximum_marks is not None else old_max
        if new_marks > new_max:
            raise HTTPException(status_code=400, detail=f"Marks obtained ({new_marks}) cannot exceed maximum marks ({new_max}).")

        new_pct = round((new_marks / new_max) * 100, 1) if new_max > 0 else 0
        if payload.grade and payload.grade.strip():
            new_grade = payload.grade.strip()
        else:
            if new_pct >= 85:
                new_grade = "A+"
            elif new_pct >= 70:
                new_grade = "A"
            elif new_pct >= 60:
                new_grade = "B+"
            elif new_pct >= 50:
                new_grade = "B"
            elif new_pct >= 35:
                new_grade = "C"
            else:
                new_grade = "F"

        now_iso = datetime.datetime.now().isoformat()
        conn.execute("""
            UPDATE academic_results
            SET marks_obtained = ?, maximum_marks = ?, percentage = ?, grade = ?,
                updated_at = ?, recorded_by_user_id = ?
            WHERE result_id = ?
        """, (new_marks, new_max, new_pct, new_grade, now_iso, admin_id, result_id))

        conn.execute("""
            INSERT INTO academic_result_audits (
                audit_id, result_id, previous_marks, new_marks,
                previous_max_marks, new_max_marks, reason_for_change,
                modified_by_user_id, modified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"ARA-{uuid.uuid4().hex[:8].upper()}",
            result_id,
            old_marks,
            new_marks,
            old_max,
            new_max,
            payload.reason.strip(),
            admin_id,
            now_iso
        ))

        conn.execute("""
            INSERT INTO student_record_audits (
                audit_id, student_id, permanent_student_id, institution_id,
                admin_user_id, admin_name, field_modified, previous_value,
                updated_value, reason, source, request_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"AUD-{uuid.uuid4().hex[:12].upper()}",
            actual_sid,
            perm_id,
            inst_id,
            admin_id,
            admin_name,
            f"result_{res.get('subject_name', 'subject')}",
            f"{old_marks}/{old_max} ({old_grade})",
            f"{new_marks}/{new_max} ({new_grade})",
            payload.reason.strip(),
            "Direct Admin Edit",
            None,
            now_iso
        ))

        conn.commit()

        return {
            "success": True,
            "message": f"Examination result for '{res.get('subject_name')}' updated successfully.",
            "result_id": result_id,
            "marks_obtained": new_marks,
            "maximum_marks": new_max,
            "percentage": new_pct,
            "grade": new_grade,
            "updated_at": now_iso
        }
    finally:
        conn.close()


@app.get("/institution/{institution_id}/students/{student_id}/audit-history")
def get_student_audit_history(
    institution_id: str,
    student_id: str,
    user: dict = Depends(require_school_admin)
):
    """Returns immutable change history and audit trail for a student record."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    conn = get_connection()
    try:
        s_row = conn.execute("SELECT student_id, permanent_student_id, student_name FROM students WHERE (student_id = ? OR permanent_student_id = ?) AND school_id = ?", (student_id, student_id, inst_id)).fetchone()
        if not s_row:
            raise HTTPException(404, f"Student '{student_id}' not found in institution '{inst_id}'.")

        aud_rows = conn.execute("""
            SELECT audit_id, student_id, permanent_student_id, field_modified,
                   previous_value, updated_value, reason, source, admin_name, created_at
            FROM student_record_audits
            WHERE student_id = ? OR permanent_student_id = ?
            ORDER BY created_at DESC
        """, (s_row["student_id"], s_row["permanent_student_id"])).fetchall()

        return {
            "student_id": s_row["student_id"],
            "student_name": s_row["student_name"],
            "total_audit_events": len(aud_rows),
            "audit_trail": [dict(a) for a in aud_rows]
        }
    finally:
        conn.close()


@app.post("/institution/{institution_id}/students/{student_id}/documents")
def add_student_document(
    institution_id: str,
    student_id: str,
    payload: StudentDocumentUploadPayload,
    user: dict = Depends(require_school_admin)
):
    """Adds or uploads a replacement verified document entry to student dossier."""
    inst_id = institution_id.strip()
    if user["role"] != "platform_admin" and user.get("school_id") != inst_id:
        raise HTTPException(status_code=403, detail="Access denied: You are not assigned to this institution.")

    admin_id = user.get("user_id", "ADMIN")
    admin_name = user.get("full_name") or "Institution Administrator"

    conn = get_connection()
    try:
        s_row = conn.execute("SELECT student_id, permanent_student_id FROM students WHERE (student_id = ? OR permanent_student_id = ?) AND school_id = ?", (student_id, student_id, inst_id)).fetchone()
        if not s_row:
            raise HTTPException(404, f"Student '{student_id}' not found in institution '{inst_id}'.")

        doc_id = f"DOC-{uuid.uuid4().hex[:10].upper()}"
        now_iso = datetime.datetime.now().isoformat()

        conn.execute("""
            INSERT INTO student_documents (
                document_id, permanent_student_id, document_type, file_name,
                verification_status, uploaded_by_user_id, verified_by_user_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, s_row["permanent_student_id"], payload.document_type, payload.file_name,
            payload.verification_status or "verified", admin_id, admin_id, now_iso
        ))

        conn.execute("""
            INSERT INTO student_record_audits (
                audit_id, student_id, permanent_student_id, institution_id,
                admin_user_id, admin_name, field_modified, previous_value,
                updated_value, reason, source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"AUD-{uuid.uuid4().hex[:12].upper()}", s_row["student_id"], s_row["permanent_student_id"], inst_id,
            admin_id, admin_name, f"document_{payload.document_type}", "(none)",
            payload.file_name, payload.reason.strip(), "Direct Admin Edit", now_iso
        ))

        conn.commit()

        return {
            "success": True,
            "document_id": doc_id,
            "message": f"Document '{payload.document_name}' added to student dossier successfully."
        }
    finally:
        conn.close()
'''

content += new_endpoints_code

with open(MAIN_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched {MAIN_PATH}. New size: {len(content)} chars.")
