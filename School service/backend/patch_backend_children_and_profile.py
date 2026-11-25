MAIN_PY = "main.py"

with open(MAIN_PY, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update list_parent_children
old_list_children = """        rows = conn.execute(
            \"\"\"
            SELECT s.student_id, s.permanent_student_id,
                   s.student_name, s.school_id, sc.school_name,
                   sc.school_type, sc.category,
                   s.standard, s.section, s.first_language,
                   s.enrollment_status,
                   e.academic_year, e.stream as enroll_stream,
                   ap.program_name, ap.discipline_or_stream, ap.department_name
            FROM student_guardians sg
            JOIN students s
              ON s.permanent_student_id = sg.permanent_student_id
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.institution_id = s.school_id
            WHERE sg.guardian_id = ?
              AND sg.is_verified = 1
              AND sg.can_view_records = 1
            GROUP BY s.permanent_student_id
            ORDER BY s.student_name
            \"\"\",
            (guardian["guardian_id"],),
        ).fetchall()

        children = []
        for r in rows:
            d = dict(r)
            d["institution_name"] = d.get("school_name") or d.get("school_id")
            d["institution_type"] = d.get("school_type") or d.get("category") or "School"
            stream = d.get("enroll_stream") or d.get("discipline_or_stream") or ""
            d["program_or_stream"] = d.get("program_name") or stream or "General Academic"
            
            std = d.get("standard")
            sec = d.get("section") or "A"
            if "PU" in str(d["institution_type"]) or "College" in str(d["institution_type"]) or "University" in str(d["institution_type"]):
                d["class_or_standard"] = f"Year {std}" if std is not None else "Year 1"
            else:
                d["class_or_standard"] = f"Standard {std}" if std is not None else "N/A"
                
            d["program_or_class"] = f"{d['program_or_stream']} · {d['class_or_standard']} ({sec})"
            d["is_verified"] = 1
            children.append(d)"""

new_list_children = """        rows = conn.execute(
            \"\"\"
            SELECT s.*,
                   sc.school_name, sc.school_type, sc.category,
                   e.enrollment_id, e.academic_year, e.stream as enroll_stream,
                   e.subject_combination as enroll_combo, e.program_id as enroll_prog_id,
                   e.degree as enroll_degree, e.branch as enroll_branch,
                   e.department as enroll_dept, e.semester as enroll_semester,
                   e.puc_year as enroll_puc_year, e.curriculum_or_board as enroll_board,
                   e.review_flag as enroll_review_flag,
                   ap.program_name, ap.discipline_or_stream, ap.department_name
            FROM student_guardians sg
            JOIN students s
              ON s.permanent_student_id = sg.permanent_student_id
            LEFT JOIN schools sc ON sc.school_id = s.school_id
            LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id
            LEFT JOIN academic_programs ap ON ap.program_id = COALESCE(e.program_id, s.program_id)
            WHERE sg.guardian_id = ?
              AND sg.is_verified = 1
              AND sg.can_view_records = 1
            ORDER BY s.student_name
            \"\"\",
            (guardian["guardian_id"],),
        ).fetchall()

        children = []
        for r in rows:
            d = dict(r)
            inst_tier = classify_institution_tier(
                d.get("school_id"),
                d.get("school_name"),
                d.get("school_type"),
                d.get("category")
            )
            enroll_info = {
                "academic_year": d.get("academic_year"),
                "stream": d.get("enroll_stream"),
                "subject_combination": d.get("enroll_combo"),
                "program_id": d.get("enroll_prog_id"),
                "degree": d.get("enroll_degree"),
                "branch": d.get("enroll_branch"),
                "department": d.get("enroll_dept"),
                "semester": d.get("enroll_semester"),
                "puc_year": d.get("enroll_puc_year"),
                "curriculum_or_board": d.get("enroll_board"),
                "review_flag": d.get("enroll_review_flag")
            }
            acad = build_institution_academic_details(
                inst_tier=inst_tier,
                student_dict=d,
                enroll_dict=enroll_info,
                school_dict=d,
                prog_dict={"program_name": d.get("program_name"), "department_name": d.get("department_name")}
            )
            d["institution_name"] = d.get("school_name") or d.get("school_id")
            d["institution_type"] = d.get("school_type") or d.get("category") or "School"
            d["institution_tier"] = inst_tier
            d["class_or_standard"] = acad["class_or_standard"]
            d["program_or_stream"] = acad["program_or_stream"]
            d["puc_year"] = acad.get("puc_year")
            d["stream"] = acad.get("stream")
            d["subject_combination"] = acad.get("subject_combination")
            d["degree"] = acad.get("degree")
            d["branch"] = acad.get("branch")
            d["programme"] = acad.get("programme")
            d["department"] = acad.get("department")
            d["semester"] = acad.get("semester")
            d["board"] = acad.get("board")
            d["program_or_class"] = f"{acad['program_or_stream']} · {acad['class_or_standard']} (Sec {acad['section']})"
            d["is_verified"] = 1
            children.append(d)"""

assert old_list_children in content, "Could not find old list_parent_children block"
content = content.replace(old_list_children, new_list_children, 1)
print("Updated list_parent_children.")

# 2. Update get_institution_student_profile acad_data
old_acad_data = """        acad_data = {
            "school_id": student["school_id"],
            "school_name": student["school_name"],
            "school_type": student["school_type"],
            "category": student["category"],
            "standard": student["standard"],
            "section": student["section"],
            "academic_year": enrollment.get("academic_year") if enrollment else "2026-2027",
            "stream": enrollment.get("stream") if enrollment else None,
            "subject_combination": enrollment.get("subject_combination") if enrollment else None
        }"""

new_acad_data = """        inst_tier = classify_institution_tier(
            student.get("school_id"),
            student.get("school_name"),
            student.get("school_type"),
            student.get("category")
        )
        prog_row = None
        if enrollment and enrollment.get("program_id"):
            prog_row = conn.execute("SELECT program_name, department_name, faculty_name FROM academic_programs WHERE program_id = ?", (enrollment["program_id"],)).fetchone()
        elif student.get("program_id"):
            prog_row = conn.execute("SELECT program_name, department_name, faculty_name FROM academic_programs WHERE program_id = ?", (student["program_id"],)).fetchone()

        acad_built = build_institution_academic_details(
            inst_tier=inst_tier,
            student_dict=student,
            enroll_dict=enrollment or {},
            school_dict=student,
            prog_dict=dict(prog_row) if prog_row else None
        )
        acad_data = {
            "school_id": student["school_id"],
            "school_name": student["school_name"],
            "school_type": student["school_type"],
            "category": student["category"],
            "institution_tier": inst_tier,
            "standard": student["standard"],
            "section": student["section"],
            "academic_year": acad_built["academic_year"],
            "class_or_standard": acad_built["class_or_standard"],
            "stream": acad_built.get("stream"),
            "subject_combination": acad_built.get("subject_combination"),
            "program_id": acad_built.get("program_id") or (enrollment.get("program_id") if enrollment else student.get("program_id")),
            "programme": acad_built.get("programme") or acad_built.get("program_or_stream"),
            "program_or_stream": acad_built.get("program_or_stream"),
            "degree": acad_built.get("degree"),
            "branch": acad_built.get("branch"),
            "department": acad_built.get("department"),
            "semester": acad_built.get("semester"),
            "puc_year": acad_built.get("puc_year"),
            "current_year": acad_built.get("current_year"),
            "board": acad_built.get("board"),
            "curriculum_or_board": acad_built.get("board"),
            "admission_year": acad_built.get("admission_year"),
            "academic_batch": acad_built.get("academic_batch"),
            "review_flag": acad_built.get("review_flag"),
            "status": student.get("enrollment_status") or "Active"
        }"""

assert old_acad_data in content, "Could not find old acad_data in get_institution_student_profile"
content = content.replace(old_acad_data, new_acad_data, 1)
print("Updated get_institution_student_profile acad_data.")

with open(MAIN_PY, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated main.py successfully.")
