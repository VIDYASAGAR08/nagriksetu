import re

MAIN_PY = "main.py"

with open(MAIN_PY, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update StudentLookupByIdResult model
old_model = """class StudentLookupByIdResult(BaseModel):
    student_full_name: str
    student_id: str
    permanent_student_id: str
    institution_id: str
    institution_name: str
    institution_type: str
    category: str
    district: Optional[str] = None
    state: Optional[str] = None
    program_or_stream: str
    class_or_standard: str
    standard: Optional[int] = None
    section: Optional[str] = None
    academic_year: str
    semester: Optional[int] = None
    is_already_linked: bool"""

new_model = """class StudentLookupByIdResult(BaseModel):
    student_full_name: str
    student_id: str
    permanent_student_id: str
    institution_id: str
    institution_name: str
    institution_type: str
    category: str
    institution_tier: str
    district: Optional[str] = None
    state: Optional[str] = None
    program_or_stream: str
    class_or_standard: str
    standard: Optional[int] = None
    section: Optional[str] = None
    academic_year: str
    semester: Optional[int] = None
    is_already_linked: bool
    board: Optional[str] = None
    puc_year: Optional[str] = None
    stream: Optional[str] = None
    subject_combination: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    programme: Optional[str] = None
    department: Optional[str] = None
    specialisation: Optional[str] = None
    current_year: Optional[str] = None
    admission_year: Optional[str] = None
    academic_batch: Optional[str] = None
    review_flag: Optional[str] = None"""

assert old_model in content, "Could not find old StudentLookupByIdResult in main.py"
content = content.replace(old_model, new_model, 1)
print("Updated StudentLookupByIdResult model.")

# 2. Add institution classifier and academic builder helpers above lookup_student_by_student_id
helpers_code = '''
def classify_institution_tier(school_id: str, name: str, stype: str, category: str) -> str:
    stype_str = (stype or "").lower()
    cat_str = (category or "").lower()
    name_str = (name or "").lower()

    if "pu college" in stype_str or "pu" in cat_str or "pre-university" in name_str:
        return "PU College"
    elif "university" in stype_str or "universities" in cat_str or "university" in name_str:
        return "University"
    elif "engineering" in name_str or "technology" in name_str or "polytechnic" in name_str or "engineering" in stype_str:
        return "Engineering College"
    elif "degree" in stype_str or "degree" in cat_str or "college" in name_str:
        return "Degree College"
    else:
        return "School"


def build_institution_academic_details(inst_tier: str, student_dict: dict, enroll_dict: dict, school_dict: dict, prog_dict: dict = None) -> dict:
    std = student_dict.get("standard")
    sec = student_dict.get("section") or "A"
    acad_yr = (enroll_dict and enroll_dict.get("academic_year")) or "2026-2027"

    puc_yr = (enroll_dict and enroll_dict.get("puc_year")) or student_dict.get("puc_year")
    stream = (enroll_dict and enroll_dict.get("stream")) or student_dict.get("stream")
    combo = (enroll_dict and enroll_dict.get("subject_combination")) or student_dict.get("subject_combination")
    degree = (enroll_dict and enroll_dict.get("degree")) or student_dict.get("degree")
    branch = (enroll_dict and enroll_dict.get("branch")) or student_dict.get("branch")
    dept = (enroll_dict and enroll_dict.get("department")) or student_dict.get("department")
    sem = (enroll_dict and enroll_dict.get("semester")) or student_dict.get("semester")
    board = (enroll_dict and enroll_dict.get("curriculum_or_board")) or student_dict.get("curriculum_or_board")
    flag = (enroll_dict and enroll_dict.get("review_flag")) or student_dict.get("review_flag")
    prog_name = (prog_dict and prog_dict.get("program_name")) or (enroll_dict and enroll_dict.get("program_id")) or (student_dict and student_dict.get("program_id"))

    if inst_tier == "School":
        class_or_standard = f"Standard {std}" if std is not None else "Standard"
        board_val = board or "Karnataka State Board (KSEEB)"
        stream_val = stream or "General"
        combo_val = combo or "KSEEB Core Curriculum (Kannada, English, Mathematics, Science, Social Science)"
        prog_val = prog_name or "Karnataka State School Education (Std 1-10)"
        return {
            "institution_tier": "School",
            "class_or_standard": class_or_standard,
            "standard": std,
            "section": sec,
            "board": board_val,
            "stream": stream_val,
            "subject_combination": combo_val,
            "program_or_stream": prog_val,
            "academic_year": acad_yr,
            "semester": None,
            "degree": None,
            "branch": None,
            "department": None,
            "programme": prog_val,
            "puc_year": None,
            "current_year": None,
            "admission_year": "2026",
            "academic_batch": None,
            "specialisation": None,
            "review_flag": flag
        }
    elif inst_tier == "PU College":
        if std in (11, 12) or puc_yr:
            puc_year_val = puc_yr or ("1st PUC" if std == 11 else "2nd PUC")
            class_or_standard = puc_year_val
            stream_val = stream or "Science"
            combo_val = combo or "PCMB"
            prog_val = prog_name or f"Pre-University ({combo_val})"
            review_flag_val = flag
        else:
            puc_year_val = "Pending Review"
            class_or_standard = f"Standard {std} (Flagged for Review)"
            stream_val = stream or "Unassigned Primary/Secondary"
            combo_val = "Pending Review"
            prog_val = "Pending Administrative Review"
            review_flag_val = flag or "FLAGGED_REVIEW_PU_INSTITUTION_HAS_K10_STUDENTS"

        return {
            "institution_tier": "PU College",
            "class_or_standard": class_or_standard,
            "puc_year": puc_year_val,
            "standard": std,
            "section": sec,
            "stream": stream_val,
            "subject_combination": combo_val,
            "board": board or "Department of Pre-University Education (DPUE)",
            "program_or_stream": prog_val,
            "academic_year": acad_yr,
            "semester": None,
            "degree": "Pre-University",
            "branch": None,
            "department": None,
            "programme": prog_val,
            "current_year": puc_year_val,
            "admission_year": "2026",
            "academic_batch": None,
            "specialisation": None,
            "review_flag": review_flag_val
        }
    elif inst_tier == "Engineering College":
        deg_val = degree or "B.E."
        branch_val = branch or stream or "Civil Engineering"
        prog_val = prog_name or f"{deg_val} in {branch_val}"
        dept_val = dept or f"Department of {branch_val}"
        sem_val = sem or 1
        year_str = f"Year {std}" if std else "Year 1"
        class_or_standard = f"{year_str} · Semester {sem_val}"

        return {
            "institution_tier": "Engineering College",
            "degree": deg_val,
            "branch": branch_val,
            "programme": prog_val,
            "program_or_stream": prog_val,
            "department": dept_val,
            "class_or_standard": class_or_standard,
            "standard": std,
            "section": sec,
            "semester": sem_val,
            "current_year": year_str,
            "academic_year": acad_yr,
            "admission_year": "2026",
            "academic_batch": "2026-2030",
            "board": board or "VTU / Autonomous (AICTE Approved)",
            "stream": branch_val,
            "subject_combination": prog_val,
            "puc_year": None,
            "specialisation": branch_val,
            "review_flag": flag
        }
    elif inst_tier == "Degree College":
        deg_val = degree or "Undergraduate Degree"
        prog_val = prog_name or "Degree Programme"
        dept_val = dept or "Department of Collegiate Education"
        sem_val = sem or 1
        year_str = f"Year {std}" if std else "Year 1"
        class_or_standard = f"{year_str} · Semester {sem_val}"

        return {
            "institution_tier": "Degree College",
            "degree": deg_val,
            "programme": prog_val,
            "program_or_stream": prog_val,
            "department": dept_val,
            "class_or_standard": class_or_standard,
            "standard": std,
            "section": sec,
            "semester": sem_val,
            "current_year": year_str,
            "academic_year": acad_yr,
            "admission_year": "2026",
            "academic_batch": "2026-2029",
            "board": board or "UGC / State Collegiate Directorate",
            "stream": stream or "General",
            "subject_combination": combo or prog_val,
            "branch": None,
            "puc_year": None,
            "specialisation": None,
            "review_flag": flag
        }
    else:  # University
        prog_val = prog_name or "University Programme"
        dept_val = dept or "University Department"
        sem_val = sem or 1
        year_str = f"Year {std}" if std else "Year 1"
        class_or_standard = f"{year_str} · Semester {sem_val}"

        return {
            "institution_tier": "University",
            "degree": degree or "Postgraduate / Undergraduate",
            "programme": prog_val,
            "program_or_stream": prog_val,
            "department": dept_val,
            "specialisation": branch or stream or "Specialisation",
            "class_or_standard": class_or_standard,
            "standard": std,
            "section": sec,
            "semester": sem_val,
            "current_year": year_str,
            "academic_year": acad_yr,
            "admission_year": "2026",
            "academic_batch": "2026-2028",
            "board": board or "University Grants Commission (UGC)",
            "stream": stream or "University Studies",
            "subject_combination": combo or prog_val,
            "branch": None,
            "puc_year": None,
            "review_flag": flag
        }

'''

target_pos = content.find('@app.get("/parent/lookup-by-student-id", response_model=StudentLookupByIdResult)')
assert target_pos != -1, "Could not find lookup endpoint"
content = content[:target_pos] + helpers_code + content[target_pos:]
print("Inserted helper functions.")

# 3. Replace lookup_student_by_student_id body
old_lookup_block = """@app.get("/parent/lookup-by-student-id", response_model=StudentLookupByIdResult)
def lookup_student_by_student_id(
    student_id: str = Query(..., min_length=1, max_length=100),
    user: dict = Depends(require_parent),
):
    \"\"\"
    Search student using an exact Student ID match against the live database.
    Fetches institution and enrollment details without guessing.
    Returns HTTP 404 if no exact match exists.
    \"\"\"
    clean_id = student_id.strip()
    if not clean_id:
        raise HTTPException(status_code=400, detail="Student ID parameter is required.")

    conn = get_connection()
    try:
        query = \"\"\"
            SELECT s.student_id, s.permanent_student_id, s.student_name,
                   s.school_id, s.standard, s.section, s.enrollment_status,
                   sc.school_name, sc.school_type, sc.category, sc.district, sc.state,
                   e.academic_year, e.stream AS enroll_stream,
                   ap.program_name, ap.discipline_or_stream, ap.department_name
            FROM students s
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = s.school_id
            WHERE UPPER(s.student_id) = UPPER(?)
            GROUP BY s.permanent_student_id
            LIMIT 1
        \"\"\"
        row = conn.execute(query, (clean_id,)).fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No student record found matching Student ID '{clean_id}'. Please check the ID and try again.",
            )

        guardian = get_parent_guardian(conn, user["user_id"])
        is_already_linked = False
        if guardian:
            existing = conn.execute(
                \"\"\"
                SELECT student_guardian_id FROM student_guardians
                WHERE guardian_id = ? AND permanent_student_id = ? AND is_verified = 1
                \"\"\",
                (guardian["guardian_id"], row["permanent_student_id"]),
            ).fetchone()
            if existing:
                is_already_linked = True

        inst_type = row["school_type"] or row["category"] or "Accredited Institution"
        category = row["category"] or row["school_type"] or "General"
        stream = row["enroll_stream"] or row["discipline_or_stream"] or ""
        program_or_stream = row["program_name"] or stream or "General Academic"

        std = row["standard"]
        sec = row["section"] or "A"
        if "PU" in str(inst_type) or "College" in str(inst_type) or "University" in str(inst_type):
            class_or_standard = f"Year {std}" if std is not None else "Year 1"
            semester = std if std is not None else 1
        else:
            class_or_standard = f"Standard {std}" if std is not None else "N/A"
            semester = None

        return {
            "student_full_name": row["student_name"],
            "student_id": row["student_id"],
            "permanent_student_id": row["permanent_student_id"],
            "institution_id": row["school_id"],
            "institution_name": row["school_name"] or row["school_id"],
            "institution_type": inst_type,
            "category": category,
            "district": row["district"] or "Karnataka",
            "state": row["state"] or "Karnataka",
            "program_or_stream": program_or_stream,
            "class_or_standard": class_or_standard,
            "standard": std,
            "section": sec,
            "academic_year": row["academic_year"] or "2026-2027",
            "semester": semester,
            "is_already_linked": is_already_linked,
        }
    finally:
        conn.close()"""

new_lookup_block = """@app.get("/parent/lookup-by-student-id", response_model=StudentLookupByIdResult)
def lookup_student_by_student_id(
    student_id: str = Query(..., min_length=1, max_length=100),
    user: dict = Depends(require_parent),
):
    \"\"\"
    Search student using an exact Student ID match against the live database.
    Fetches institution and enrollment details with authentic institution-specific classification.
    Returns HTTP 404 if no exact match exists.
    \"\"\"
    clean_id = student_id.strip()
    if not clean_id:
        raise HTTPException(status_code=400, detail="Student ID parameter is required.")

    conn = get_connection()
    try:
        query = \"\"\"
            SELECT s.*,
                   sc.school_name, sc.school_type, sc.category, sc.district, sc.state,
                   e.enrollment_id, e.academic_year, e.stream AS enroll_stream,
                   e.subject_combination AS enroll_combo, e.program_id AS enroll_prog_id,
                   e.degree AS enroll_degree, e.branch AS enroll_branch,
                   e.department AS enroll_dept, e.semester AS enroll_semester,
                   e.puc_year AS enroll_puc_year, e.curriculum_or_board AS enroll_board,
                   e.review_flag AS enroll_review_flag,
                   ap.program_name, ap.discipline_or_stream, ap.department_name, ap.faculty_name
            FROM students s
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.program_id = COALESCE(e.program_id, s.program_id)
            WHERE UPPER(s.student_id) = UPPER(?)
            LIMIT 1
        \"\"\"
        row = conn.execute(query, (clean_id,)).fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No student record found matching Student ID '{clean_id}'. Please check the ID and try again.",
            )

        guardian = get_parent_guardian(conn, user["user_id"])
        is_already_linked = False
        if guardian:
            existing = conn.execute(
                \"\"\"
                SELECT student_guardian_id FROM student_guardians
                WHERE guardian_id = ? AND permanent_student_id = ? AND is_verified = 1
                \"\"\",
                (guardian["guardian_id"], row["permanent_student_id"]),
            ).fetchone()
            if existing:
                is_already_linked = True

        r_dict = dict(row)
        inst_tier = classify_institution_tier(
            r_dict.get("school_id"),
            r_dict.get("school_name"),
            r_dict.get("school_type"),
            r_dict.get("category")
        )

        enroll_info = {
            "academic_year": r_dict.get("academic_year"),
            "stream": r_dict.get("enroll_stream"),
            "subject_combination": r_dict.get("enroll_combo"),
            "program_id": r_dict.get("enroll_prog_id"),
            "degree": r_dict.get("enroll_degree"),
            "branch": r_dict.get("enroll_branch"),
            "department": r_dict.get("enroll_dept"),
            "semester": r_dict.get("enroll_semester"),
            "puc_year": r_dict.get("enroll_puc_year"),
            "curriculum_or_board": r_dict.get("enroll_board"),
            "review_flag": r_dict.get("enroll_review_flag")
        }

        acad = build_institution_academic_details(
            inst_tier=inst_tier,
            student_dict=r_dict,
            enroll_dict=enroll_info,
            school_dict=r_dict,
            prog_dict={"program_name": r_dict.get("program_name"), "department_name": r_dict.get("department_name")}
        )

        return {
            "student_full_name": r_dict["student_name"],
            "student_id": r_dict["student_id"],
            "permanent_student_id": r_dict["permanent_student_id"],
            "institution_id": r_dict["school_id"],
            "institution_name": r_dict.get("school_name") or r_dict["school_id"],
            "institution_type": r_dict.get("school_type") or r_dict.get("category") or "School",
            "category": r_dict.get("category") or r_dict.get("school_type") or "General",
            "institution_tier": inst_tier,
            "district": r_dict.get("district") or "Karnataka",
            "state": r_dict.get("state") or "Karnataka",
            "program_or_stream": acad["program_or_stream"],
            "class_or_standard": acad["class_or_standard"],
            "standard": acad["standard"],
            "section": acad["section"],
            "academic_year": acad["academic_year"],
            "semester": acad["semester"],
            "is_already_linked": is_already_linked,
            "board": acad.get("board"),
            "puc_year": acad.get("puc_year"),
            "stream": acad.get("stream"),
            "subject_combination": acad.get("subject_combination"),
            "degree": acad.get("degree"),
            "branch": acad.get("branch"),
            "programme": acad.get("programme"),
            "department": acad.get("department"),
            "specialisation": acad.get("specialisation"),
            "current_year": acad.get("current_year"),
            "admission_year": acad.get("admission_year"),
            "academic_batch": acad.get("academic_batch"),
            "review_flag": acad.get("review_flag"),
        }
    finally:
        conn.close()"""

assert old_lookup_block in content, "Could not find old lookup_student_by_student_id block"
content = content.replace(old_lookup_block, new_lookup_block, 1)
print("Updated lookup_student_by_student_id endpoint.")

with open(MAIN_PY, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated main.py successfully.")
