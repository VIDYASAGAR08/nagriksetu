with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate start: def get_institution_academic_structure
start_marker = '@app.get("/institution/{institution_id}/academic-structure")'
end_marker = '@app.get("/institution/{institution_id}/students/{student_id}")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

assert start_idx != -1, "start_marker not found"
assert end_idx != -1, "end_marker not found"

new_code = '''@app.get("/institution/{institution_id}/academic-structure")
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

        category = school["category"] or school["school_type"] or ""
        cat_lower = category.lower()
        is_school = "school" in cat_lower and "pu" not in cat_lower
        is_pu = "pu" in cat_lower or "pre-university" in cat_lower
        is_diploma = "diploma" in cat_lower or "polytechnic" in cat_lower
        is_degree = not is_school and not is_pu and not is_diploma

        # K-10 School
        if is_school:
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

            all_sections = sorted(list({s for secs in sections_by_std.values() for s in secs}))
            if not all_sections:
                all_sections = ["A", "B", "C"]

            # Distinct mediums
            med_rows = conn.execute(
                "SELECT DISTINCT first_language FROM students WHERE school_id = ? AND first_language IS NOT NULL",
                (inst_id,)
            ).fetchall()
            mediums = [m["first_language"] for m in med_rows if m["first_language"]]
            if not mediums:
                mediums = ["Kannada", "English"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "K10_SCHOOL",
                "standards": standards,
                "sections": all_sections,
                "sections_by_standard": sections_by_std,
                "mediums": mediums,
                "academic_years": ["2026-2027", "2025-2026"]
            }

        # PU College (11-12)
        elif is_pu:
            pu_levels = ["1st PU (11th)", "2nd PU (12th)"]
            
            # Streams actually configured in academic_programs for this institution
            streams_rows = conn.execute(
                "SELECT DISTINCT discipline_or_stream FROM academic_programs WHERE institution_id = ? AND is_active = 1 ORDER BY discipline_or_stream",
                (inst_id,)
            ).fetchall()
            streams = [r["discipline_or_stream"] for r in streams_rows if r["discipline_or_stream"]]
            if not streams:
                streams = ["Science", "Commerce", "Arts / Humanities"]

            combinations_by_stream = {}
            sections_by_combo_level = {}
            for st in streams:
                combo_rows = conn.execute(
                    "SELECT program_id, program_name, combination_code FROM academic_programs WHERE institution_id = ? AND discipline_or_stream = ? AND is_active = 1 ORDER BY combination_code, program_name",
                    (inst_id, st)
                ).fetchall()
                combos = []
                for c in combo_rows:
                    code = c["combination_code"] or c["program_name"][:4]
                    # Sections from program_sections
                    sec_rows = conn.execute(
                        "SELECT DISTINCT term_or_year, section_name FROM program_sections WHERE institution_id = ? AND program_id = ? ORDER BY term_or_year, section_name",
                        (inst_id, c["program_id"])
                    ).fetchall()
                    sec_by_lvl = {"11": [], "12": []}
                    for sr in sec_rows:
                        if str(sr["term_or_year"]) in sec_by_lvl:
                            sec_by_lvl[str(sr["term_or_year"])].append(sr["section_name"])
                    if not sec_by_lvl["11"]:
                        sec_by_lvl["11"] = ["A", "B"]
                    if not sec_by_lvl["12"]:
                        sec_by_lvl["12"] = ["A", "B"]

                    sections_by_combo_level[f"{code}_11"] = sec_by_lvl["11"]
                    sections_by_combo_level[f"{code}_12"] = sec_by_lvl["12"]

                    combos.append({
                        "program_id": c["program_id"],
                        "code": code,
                        "name": c["program_name"],
                        "stream": st,
                        "sections_by_level": sec_by_lvl
                    })
                combinations_by_stream[st] = combos

            # Overall combination codes
            combo_codes = sorted(list({c["code"] for clist in combinations_by_stream.values() for c in clist if c.get("code")}))
            
            # Default sections
            sections = ["A", "B", "C"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "PU_COLLEGE",
                "pu_levels": pu_levels,
                "streams": streams,
                "combinations": combo_codes,
                "combinations_by_stream": combinations_by_stream,
                "sections": sections,
                "sections_by_combo_level": sections_by_combo_level,
                "academic_years": ["2026-2027", "2025-2026"]
            }

        # Polytechnic / Diploma
        elif is_diploma:
            programs = conn.execute(
                "SELECT program_id, program_name, discipline_or_stream, duration_years FROM academic_programs WHERE institution_id = ? AND is_active = 1 ORDER BY program_name",
                (inst_id,)
            ).fetchall()
            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "DIPLOMA",
                "programs": [dict(p) for p in programs],
                "academic_years": ["2026-2027", "2025-2026"],
                "semesters": [1, 2, 3, 4, 5, 6],
                "sections": ["A", "B"]
            }

        # Degree College / University
        else:
            # 1. Academic Divisions
            div_rows = conn.execute(
                "SELECT division_id, division_name, division_type FROM institution_divisions WHERE parent_institution_id = ? ORDER BY display_order, division_name",
                (inst_id,)
            ).fetchall()
            divisions = [dict(d) for d in div_rows]

            # 2. Configured Degree Programs
            prog_rows = conn.execute(
                """
                SELECT program_id, program_name, degree_type, discipline_or_stream, combination_code,
                       faculty_name, department_name, duration_years
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                ORDER BY program_name
                """,
                (inst_id,)
            ).fetchall()

            programs = []
            for p in prog_rows:
                p_dict = dict(p)
                pid = p["program_id"]
                dur = p["duration_years"] or 4

                # Associate division_id if faculty_name matches
                matching_div = next((d["division_id"] for d in divisions if d["division_name"].lower() == (p["faculty_name"] or "").lower()), None)
                p_dict["division_id"] = matching_div
                p_dict["program_code"] = p["combination_code"] or pid.replace(f"PROG-{inst_id}-", "")

                # Sections from program_sections
                sec_rows = conn.execute(
                    """
                    SELECT section_id, academic_year, term_or_year, semester, section_name
                    FROM program_sections
                    WHERE institution_id = ? AND program_id = ?
                    ORDER BY term_or_year, semester, section_name
                    """,
                    (inst_id, pid)
                ).fetchall()

                if sec_rows:
                    academic_years = sorted(list({r["academic_year"] for r in sec_rows if r["academic_year"]}))
                    years = sorted(list({r["term_or_year"] for r in sec_rows if r["term_or_year"] is not None}))
                    semesters_by_year = {}
                    sections_by_year_sem = {}
                    all_sections = sorted(list({r["section_name"] for r in sec_rows if r["section_name"]}))

                    for r in sec_rows:
                        y = str(r["term_or_year"])
                        s = r["semester"]
                        sec = r["section_name"]
                        if y not in semesters_by_year:
                            semesters_by_year[y] = set()
                        if s is not None:
                            semesters_by_year[y].add(s)

                        key = f"{y}-{s if s is not None else 1}"
                        if key not in sections_by_year_sem:
                            sections_by_year_sem[key] = set()
                        if sec:
                            sections_by_year_sem[key].add(sec)

                    p_dict["academic_years"] = academic_years if academic_years else ["2026-27", "2025-26"]
                    p_dict["years"] = years if years else list(range(1, dur + 1))
                    p_dict["semesters_by_year"] = {y: sorted(list(slist)) for y, slist in semesters_by_year.items()}
                    p_dict["sections_by_year_sem"] = {k: sorted(list(slist)) for k, slist in sections_by_year_sem.items()}
                    p_dict["sections"] = all_sections if all_sections else ["A", "B"]
                else:
                    p_dict["academic_years"] = ["2026-27", "2025-26"]
                    p_dict["years"] = list(range(1, dur + 1))
                    p_dict["semesters_by_year"] = {str(y): [2 * y - 1, 2 * y] for y in range(1, dur + 1)}
                    p_dict["sections_by_year_sem"] = {f"{y}-{sem}": ["A", "B"] for y in range(1, dur + 1) for sem in [2 * y - 1, 2 * y]}
                    p_dict["sections"] = ["A", "B"]

                programs.append(p_dict)

            # All distinct academic years and sections
            all_ac_years = sorted(list({ay for pr in programs for ay in pr.get("academic_years", [])})) or ["2026-27", "2025-26"]
            all_sections = sorted(list({sec for pr in programs for sec in pr.get("sections", [])})) or ["A", "B", "C"]

            return {
                "institution_id": inst_id,
                "institution_name": school["school_name"],
                "category": category,
                "category_type": "DEGREE_COLLEGE" if "degree" in cat_lower else "UNIVERSITY",
                "divisions": divisions,
                "programs": programs,
                "academic_years": all_ac_years,
                "sections": all_sections
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
    division_id: Optional[str] = Query(default=None),
    year: Optional[int] = Query(default=None),
    semester: Optional[int] = Query(default=None),
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
        school = conn.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found.")

        category = school["category"] or school["school_type"] or ""
        cat_lower = category.lower()
        is_school = "school" in cat_lower and "pu" not in cat_lower
        is_pu = "pu" in cat_lower or "pre-university" in cat_lower
        is_diploma = "diploma" in cat_lower or "polytechnic" in cat_lower
        is_degree = not is_school and not is_pu and not is_diploma

        # -----------------------------------------------------------------
        # TIER-SPECIFIC BACKEND FILTER VALIDATION
        # -----------------------------------------------------------------
        if is_school:
            # Schools cannot accept PU or Degree parameters
            if stream or combination or program_id or division_id or semester:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Validation error: Stream, combination, and degree programme filters are not applicable to School Education (K-10)."
                )
            if standard is not None and (standard < 1 or standard > 10):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation error: Standard '{standard}' is invalid for School Education (must be between 1 and 10)."
                )

        elif is_pu:
            # PU Colleges cannot accept Degree program, division, or semester parameters
            if program_id or division_id or semester:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Validation error: Degree programme, division, and semester filters are not applicable to PU Colleges."
                )
            if standard is not None and standard not in (11, 12):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation error: Standard '{standard}' is invalid for PU Colleges (must be 11 for 1st PU or 12 for 2nd PU)."
                )

            # Query institution's actual configured academic programmes
            pu_progs = conn.execute(
                """
                SELECT program_id, discipline_or_stream, combination_code, program_name
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                """,
                (inst_id,)
            ).fetchall()

            valid_streams = {p["discipline_or_stream"] for p in pu_progs if p["discipline_or_stream"]}
            valid_combos = {p["combination_code"] for p in pu_progs if p["combination_code"]}
            stream_combos = {}
            for p in pu_progs:
                st = p["discipline_or_stream"]
                cb = p["combination_code"]
                if st and cb:
                    stream_combos.setdefault(st, set()).add(cb)

            # Validate Stream
            if stream:
                if stream not in valid_streams:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Validation error: Academic stream '{stream}' is not configured for {school['school_name']} ({inst_id}). Offered streams: {sorted(list(valid_streams))}."
                    )

            # Validate Combination & Stream-to-Combination mapping
            if combination:
                if combination not in valid_combos:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Validation error: Subject combination '{combination}' is not configured for {school['school_name']} ({inst_id})."
                    )
                if stream:
                    allowed_for_stream = stream_combos.get(stream, set())
                    if combination not in allowed_for_stream:
                        actual_stream = next((st for st, cbs in stream_combos.items() if combination in cbs), "another stream")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Validation error: Subject combination '{combination}' is a {actual_stream} combination and cannot be selected under '{stream}' for {school['school_name']}."
                        )

        elif is_degree:
            # Degree colleges / universities
            deg_progs = conn.execute(
                """
                SELECT program_id, program_name, degree_type, discipline_or_stream, duration_years, faculty_name
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                """,
                (inst_id,)
            ).fetchall()

            valid_prog_ids = {p["program_id"] for p in deg_progs}
            if program_id:
                if program_id not in valid_prog_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Validation error: Degree programme '{program_id}' is not configured for {school['school_name']} ({inst_id})."
                    )

        # -----------------------------------------------------------------
        # QUERY MATCHING ENROLLED STUDENTS
        # -----------------------------------------------------------------
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

        # Enforce stream & combination filtering on enrollments
        if is_pu:
            if stream:
                where_clauses.append("(e.stream = ? OR e.stream IS NULL)")
                # When combination is specifically chosen, filter by subject_combination
                if combination:
                    where_clauses.append("e.subject_combination = ?")
                    params.append(combination)

        elif is_degree:
            if program_id:
                where_clauses.append("(e.stream = ? OR e.subject_combination = ? OR e.school_id IS NULL AND 1=0)")
                params.extend([program_id, program_id])

        where_sql = " AND ".join(where_clauses)

        # Count total matching
        count_sql = f"""
            SELECT COUNT(DISTINCT s.student_id)
            FROM students s
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
            WHERE {where_sql}
        """
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
            GROUP BY s.student_id
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
            # Clean display name
            d["student_name"] = re.sub(r"\\s+\\d{3,}$", "", d["student_name"]).strip()
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


'''

new_content = content[:start_idx] + new_code + content[end_idx:]

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("backend/main.py successfully patched.")
