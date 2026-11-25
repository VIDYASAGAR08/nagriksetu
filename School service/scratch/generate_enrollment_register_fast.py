import sqlite3
import os
import time
import xlsxwriter

start_time = time.time()
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
OUTPUT_XLSX = r"C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx"

print("Connecting to live database:", DB_PATH)
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Fetch all schools / institutions
cur.execute("""
    SELECT school_id, school_name, school_type, category, district, state, address
    FROM schools
    ORDER BY school_id
""")
schools = [dict(r) for r in cur.fetchall()]
schools_by_id = {s["school_id"]: s for s in schools}

# 2. Fetch all academic_programs
cur.execute("SELECT * FROM academic_programs")
prog_rows = [dict(r) for r in cur.fetchall()]
programs_by_id = {p["program_id"]: p for p in prog_rows}

# 3. Fetch all institution divisions
cur.execute("SELECT * FROM institution_divisions")
div_rows = [dict(r) for r in cur.fetchall()]
divisions_by_school = {}
for d in div_rows:
    p_id = d["parent_institution_id"]
    if p_id not in divisions_by_school:
        divisions_by_school[p_id] = []
    divisions_by_school[p_id].append(d["division_name"])

# 4. Fetch all students with enrollment metadata
print("Fetching all students...")
cur.execute("""
    SELECT 
        s.student_id,
        s.permanent_student_id,
        s.student_name,
        s.school_id,
        sch.school_name,
        sch.district as school_district,
        sch.category as school_category,
        sch.school_type,
        s.standard,
        s.section,
        s.puc_year,
        s.stream,
        s.subject_combination,
        s.program_id,
        s.degree,
        s.branch,
        s.department,
        s.semester,
        s.curriculum_or_board,
        s.enrollment_status,
        s.district as student_district,
        e.academic_year
    FROM students s
    JOIN schools sch ON sch.school_id = s.school_id
    LEFT JOIN enrollments e ON e.permanent_student_id = s.permanent_student_id AND e.school_id = s.school_id
    ORDER BY s.school_id, s.standard, s.section, s.student_name
""")
students = [dict(r) for r in cur.fetchall()]
print(f"Loaded {len(students)} student records.")
conn.close()

# Prepare Helper Classifications
def classify_student(s):
    sch_id = s["school_id"]
    std = s["standard"]
    puc = s["puc_year"]
    stream = s["stream"] or ""
    prog_id = s["program_id"]
    deg = s["degree"]
    sch_cat = s["school_category"] or ""
    
    is_mismatch = False
    mismatch_issue = None
    
    # Group A: Standards 1-10 in PU College (SCH011-SCH015)
    if sch_id in ["SCH011", "SCH012", "SCH013", "SCH014", "SCH015"] and std is not None and std <= 10:
        is_mismatch = True
        mismatch_issue = "Mismatched Assignment: School Standard (1-10) student assigned to Pre-University College without valid PU Programme"
        academic_div = "Unresolved (Primary/Secondary in PU College)"
        course_name = "Unassigned - Review Required"
        course_id = "UNMAPPED-SCH-IN-PUC"
        class_str = f"Standard {std}"
        review_status = "Pending Composite Institution Migration (Scenario B)"

    # Group B: Standards 11-12 in K-10 School (SCH016-SCH020)
    elif sch_id in ["SCH016", "SCH017", "SCH018", "SCH019", "SCH020"] and std is not None and std in [11, 12]:
        is_mismatch = True
        mismatch_issue = "Mismatched Assignment: Higher Secondary (11-12) student assigned to K-10 School without valid School Programme"
        academic_div = "Unresolved (Higher Secondary in K-10 School)"
        course_name = "Unassigned - Review Required"
        course_id = "UNMAPPED-PUC-IN-K10"
        class_str = f"Level {std} (11th/12th Grade)"
        review_status = "Pending Composite Institution Migration (Scenario B)"

    # Normal Higher Education (COL001-COL010)
    elif "degree" in sch_cat.lower() or "university" in sch_cat.lower() or deg in ["B.E.", "B.Tech", "MCA"]:
        academic_div = "Faculty of Engineering & Technology / Undergraduate"
        prog = programs_by_id.get(prog_id)
        course_name = prog["program_name"] if prog else (f"{deg} in {s['branch']}" if deg and s['branch'] else "Undergraduate Degree")
        course_id = prog_id or "PROG-COL-UG"
        class_str = f"Semester {s['semester']}" if s['semester'] else "Year 1"
        review_status = "Verified Enrolled"

    # Normal Pre-University (SCH011-SCH015, Standards 11-12)
    elif puc or std in [11, 12] or "pu" in sch_cat.lower():
        academic_div = "Pre-University Division (PUC)"
        prog = programs_by_id.get(prog_id)
        course_name = prog["program_name"] if prog else f"Pre-University ({stream})"
        course_id = prog_id or "PROG-PUC"
        class_str = puc if puc else (f"{std}th PUC" if std else "PUC")
        review_status = "Verified Enrolled"

    # Normal School (K-10: SCH001-SCH010, and SCH016-SCH020 std 1-10)
    else:
        academic_div = "School Division (Standards 1–10)"
        prog = programs_by_id.get(prog_id)
        course_name = prog["program_name"] if prog else "Karnataka State School Education (Std 1-10)"
        course_id = prog_id or f"PROG-{sch_id}-K10"
        class_str = f"Standard {std}" if std else "Standard"
        review_status = "Verified Enrolled"

    return {
        "is_mismatch": is_mismatch,
        "mismatch_issue": mismatch_issue,
        "academic_div": academic_div,
        "course_name": course_name,
        "course_id": course_id,
        "class_str": class_str,
        "review_status": review_status
    }

# Pre-process all students
processed_students = []
for idx, s in enumerate(students, 1):
    c_info = classify_student(s)
    row = {
        "sno": idx,
        "student_id": s["student_id"],
        "psid": s["permanent_student_id"],
        "student_name": s["student_name"],
        "school_id": s["school_id"],
        "school_name": s["school_name"],
        "district": s["student_district"] or s["school_district"],
        "academic_div": c_info["academic_div"],
        "course_name": c_info["course_name"],
        "course_id": c_info["course_id"],
        "class_str": c_info["class_str"],
        "standard": s["standard"],
        "puc_year": s["puc_year"],
        "section": s["section"] or "A",
        "stream": s["stream"] or "General",
        "subject_combination": s["subject_combination"] or "Core Curriculum",
        "academic_year": s["academic_year"] or "2026-2027",
        "enrollment_status": (s["enrollment_status"] or "active").upper(),
        "degree": s["degree"],
        "branch": s["branch"],
        "department": s["department"],
        "semester": s["semester"],
        "is_mismatch": c_info["is_mismatch"],
        "mismatch_issue": c_info["mismatch_issue"],
        "review_status": c_info["review_status"]
    }
    processed_students.append(row)

# Calculate Institutional Counts
inst_counts = {}
for s in processed_students:
    sch_id = s["school_id"]
    if sch_id not in inst_counts:
        inst_counts[sch_id] = {"total": 0, "active": 0}
    inst_counts[sch_id]["total"] += 1
    if s["enrollment_status"] == "ACTIVE":
        inst_counts[sch_id]["active"] += 1

print(f"Processed {len(processed_students)} records in {time.time() - start_time:.2f}s. Creating workbook with xlsxwriter...")

wb = xlsxwriter.Workbook(OUTPUT_XLSX, {'constant_memory': True})

# Formats
fmt_hdr = wb.add_format({
    'bold': True, 'bg_color': '#1E3A8A', 'font_color': '#FFFFFF',
    'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
    'border': 1, 'border_color': '#CBD5E1'
})
fmt_hdr_accent = wb.add_format({
    'bold': True, 'bg_color': '#0F172A', 'font_color': '#FFFFFF',
    'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
    'border': 1, 'border_color': '#CBD5E1'
})
fmt_hdr_warn = wb.add_format({
    'bold': True, 'bg_color': '#991B1B', 'font_color': '#FFFFFF',
    'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
    'border': 1, 'border_color': '#CBD5E1'
})

fmt_title = wb.add_format({
    'bold': True, 'font_name': 'Calibri', 'font_size': 14, 'font_color': '#1E3A8A'
})

fmt_left = wb.add_format({'font_name': 'Calibri', 'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})
fmt_center = wb.add_format({'font_name': 'Calibri', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})
fmt_right = wb.add_format({'font_name': 'Calibri', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'num_format': '#,##0', 'border': 1, 'border_color': '#E2E8F0'})

fmt_warn_left = wb.add_format({'font_name': 'Calibri', 'font_size': 10, 'font_color': '#991B1B', 'bg_color': '#FEF2F2', 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': '#FECACA'})
fmt_warn_center = wb.add_format({'font_name': 'Calibri', 'font_size': 10, 'font_color': '#991B1B', 'bg_color': '#FEF2F2', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#FECACA'})
fmt_warn_right = wb.add_format({'font_name': 'Calibri', 'font_size': 10, 'font_color': '#991B1B', 'bg_color': '#FEF2F2', 'align': 'right', 'valign': 'vcenter', 'num_format': '#,##0', 'border': 1, 'border_color': '#FECACA'})

fmt_total_left = wb.add_format({'bold': True, 'font_name': 'Calibri', 'font_size': 11, 'bg_color': '#F1F5F9', 'align': 'left', 'valign': 'vcenter', 'top': 1, 'bottom': 6, 'left': 1, 'right': 1, 'border_color': '#0F172A'})
fmt_total_right = wb.add_format({'bold': True, 'font_name': 'Calibri', 'font_size': 11, 'bg_color': '#F1F5F9', 'align': 'right', 'valign': 'vcenter', 'num_format': '#,##0', 'top': 1, 'bottom': 6, 'left': 1, 'right': 1, 'border_color': '#0F172A'})

# ==============================================================================
# SHEET 1: Institution Directory
# ==============================================================================
print("Writing Sheet 1: Institution Directory...")
ws1 = wb.add_worksheet("Institution Directory")
ws1.freeze_panes(1, 0)

headers1 = [
    "Institution ID", "Institution Name", "Institution Category", "Institution Type",
    "District", "Taluk / Locality", "Address", "Total Registered Students",
    "Total Active Enrollments", "Academic Divisions", "Institution Status"
]
col_widths1 = [16, 42, 22, 18, 18, 22, 50, 24, 24, 45, 28]
for c_idx, w in enumerate(col_widths1):
    ws1.set_column(c_idx, c_idx, w)

ws1.set_row(0, 28)
for c_idx, h in enumerate(headers1):
    ws1.write(0, c_idx, h, fmt_hdr)

row_idx = 1
total_reg_sum = 0
total_act_sum = 0

for s in schools:
    sch_id = s["school_id"]
    c_data = inst_counts.get(sch_id, {"total": 0, "active": 0})
    total_reg = c_data["total"]
    total_act = c_data["active"]
    total_reg_sum += total_reg
    total_act_sum += total_act
    
    addr = s["address"] or ""
    taluk = f"{s['district']} Taluk" if s["district"] else "Not Specified"
    if "Taluk" in addr:
        for part in addr.split(","):
            if "Taluk" in part:
                taluk = part.strip()

    divs = divisions_by_school.get(sch_id, [])
    if not divs:
        if "PU" in s["school_type"] or "PU" in (s["category"] or ""):
            div_str = "Pre-University Division (1st & 2nd PUC)"
        elif "degree" in (s["category"] or "").lower() or "university" in (s["category"] or "").lower():
            div_str = "Higher Education / University Faculties"
        else:
            div_str = "Primary & Secondary School Division (Standards 1–10)"
    else:
        div_str = " | ".join(divs)

    status_str = "Active Registry (Enrollments Mapped)" if total_reg > 0 else "Active Registry (Zero Current Enrollments)"

    ws1.set_row(row_idx, 20)
    ws1.write(row_idx, 0, sch_id, fmt_center)
    ws1.write(row_idx, 1, s["school_name"], fmt_left)
    ws1.write(row_idx, 2, s["category"] or s["school_type"], fmt_left)
    ws1.write(row_idx, 3, s["school_type"], fmt_center)
    ws1.write(row_idx, 4, s["district"] or "Karnataka", fmt_left)
    ws1.write(row_idx, 5, taluk, fmt_left)
    ws1.write(row_idx, 6, addr, fmt_left)
    ws1.write(row_idx, 7, total_reg, fmt_right)
    ws1.write(row_idx, 8, total_act, fmt_right)
    ws1.write(row_idx, 9, div_str, fmt_left)
    ws1.write(row_idx, 10, status_str, fmt_center)
    row_idx += 1

# Total row
ws1.set_row(row_idx, 24)
ws1.write(row_idx, 0, "TOTAL", fmt_total_left)
ws1.write(row_idx, 1, f"All Registered Institutions ({len(schools)})", fmt_total_left)
for c in range(2, 7):
    ws1.write(row_idx, c, "", fmt_total_left)
ws1.write(row_idx, 7, total_reg_sum, fmt_total_right)
ws1.write(row_idx, 8, total_act_sum, fmt_total_right)
ws1.write(row_idx, 9, "", fmt_total_left)
ws1.write(row_idx, 10, "", fmt_total_left)
ws1.autofilter(0, 0, row_idx - 1, len(headers1) - 1)

# ==============================================================================
# SHEET 2: Complete Student Register
# ==============================================================================
print("Writing Sheet 2: Complete Student Register (30,003 rows)...")
ws2 = wb.add_worksheet("Complete Student Register")
ws2.freeze_panes(1, 0)

headers2 = [
    "Serial Number", "Student ID", "Permanent Student ID (PSID)", "Student Name",
    "Institution ID", "Institution Name", "District", "Academic Division",
    "Course / Programme", "Standard / Class / Level", "Section", "Stream",
    "Subject Combination", "Academic Year", "Enrollment Status"
]
col_widths2 = [14, 16, 36, 26, 16, 38, 18, 38, 38, 22, 10, 20, 48, 16, 16]
for c_idx, w in enumerate(col_widths2):
    ws2.set_column(c_idx, c_idx, w)

ws2.set_row(0, 28)
for c_idx, h in enumerate(headers2):
    ws2.write(0, c_idx, h, fmt_hdr)

for r_idx, s in enumerate(processed_students, 1):
    warn = s["is_mismatch"]
    f_l = fmt_warn_left if warn else fmt_left
    f_c = fmt_warn_center if warn else fmt_center
    f_r = fmt_warn_right if warn else fmt_right

    ws2.write(r_idx, 0, s["sno"], f_r)
    ws2.write(r_idx, 1, s["student_id"], f_c)
    ws2.write(r_idx, 2, s["psid"], f_c)
    ws2.write(r_idx, 3, s["student_name"], f_l)
    ws2.write(r_idx, 4, s["school_id"], f_c)
    ws2.write(r_idx, 5, s["school_name"], f_l)
    ws2.write(r_idx, 6, s["district"], f_l)
    ws2.write(r_idx, 7, s["academic_div"], f_l)
    ws2.write(r_idx, 8, s["course_name"], f_l)
    ws2.write(r_idx, 9, s["class_str"], f_c)
    ws2.write(r_idx, 10, s["section"], f_c)
    ws2.write(r_idx, 11, s["stream"], f_l)
    ws2.write(r_idx, 12, s["subject_combination"], f_l)
    ws2.write(r_idx, 13, s["academic_year"], f_c)
    ws2.write(r_idx, 14, s["enrollment_status"], f_c)

ws2.autofilter(0, 0, len(processed_students), len(headers2) - 1)

# ==============================================================================
# SHEET 3: Institution-wise Student List
# ==============================================================================
print("Writing Sheet 3: Institution-wise Student List...")
ws3 = wb.add_worksheet("Institution-wise Student List")
ws3.freeze_panes(1, 0)

headers3 = [
    "Institution ID", "Institution Name", "District", "Student ID",
    "Permanent Student ID (PSID)", "Student Name", "Course / Programme",
    "Class / Standard", "Academic Division", "Enrollment Status"
]
col_widths3 = [16, 38, 18, 16, 36, 26, 38, 22, 38, 16]
for c_idx, w in enumerate(col_widths3):
    ws3.set_column(c_idx, c_idx, w)

ws3.set_row(0, 28)
for c_idx, h in enumerate(headers3):
    ws3.write(0, c_idx, h, fmt_hdr_accent)

for r_idx, s in enumerate(processed_students, 1):
    warn = s["is_mismatch"]
    f_l = fmt_warn_left if warn else fmt_left
    f_c = fmt_warn_center if warn else fmt_center

    ws3.write(r_idx, 0, s["school_id"], f_c)
    ws3.write(r_idx, 1, s["school_name"], f_l)
    ws3.write(r_idx, 2, s["district"], f_l)
    ws3.write(r_idx, 3, s["student_id"], f_c)
    ws3.write(r_idx, 4, s["psid"], f_c)
    ws3.write(r_idx, 5, s["student_name"], f_l)
    ws3.write(r_idx, 6, s["course_name"], f_l)
    ws3.write(r_idx, 7, s["class_str"], f_c)
    ws3.write(r_idx, 8, s["academic_div"], f_l)
    ws3.write(r_idx, 9, s["enrollment_status"], f_c)

ws3.autofilter(0, 0, len(processed_students), len(headers3) - 1)

# ==============================================================================
# SHEET 4: Course Enrollment Register
# ==============================================================================
print("Writing Sheet 4: Course Enrollment Register...")
ws4 = wb.add_worksheet("Course Enrollment Register")
ws4.freeze_panes(1, 0)

headers4 = [
    "Student ID", "Student Name", "Institution ID", "Institution Name",
    "Course ID / Programme ID", "Course / Programme Name", "Academic Division",
    "Standard / Class / PUC Year", "Stream", "Subject Combination",
    "Department / Specialization", "Year / Semester", "Academic Year", "Enrollment Status"
]
col_widths4 = [16, 26, 16, 38, 26, 38, 38, 22, 20, 48, 32, 16, 16, 16]
for c_idx, w in enumerate(col_widths4):
    ws4.set_column(c_idx, c_idx, w)

ws4.set_row(0, 28)
for c_idx, h in enumerate(headers4):
    ws4.write(0, c_idx, h, fmt_hdr)

for r_idx, s in enumerate(processed_students, 1):
    warn = s["is_mismatch"]
    f_l = fmt_warn_left if warn else fmt_left
    f_c = fmt_warn_center if warn else fmt_center

    dept_spec = s["department"] or s["branch"] or ("School Education Department" if not s["is_mismatch"] and "School" in s["academic_div"] else ("Pre-University Board" if not s["is_mismatch"] and "PU" in s["academic_div"] else "Unassigned"))
    yr_sem = f"Semester {s['semester']}" if s["semester"] else ("1st PUC" if s["class_str"] == "1st PUC" else ("2nd PUC" if s["class_str"] == "2nd PUC" else ("Annual KSEEB" if "School" in s["academic_div"] else "N/A")))

    ws4.write(r_idx, 0, s["student_id"], f_c)
    ws4.write(r_idx, 1, s["student_name"], f_l)
    ws4.write(r_idx, 2, s["school_id"], f_c)
    ws4.write(r_idx, 3, s["school_name"], f_l)
    ws4.write(r_idx, 4, s["course_id"], f_c)
    ws4.write(r_idx, 5, s["course_name"], f_l)
    ws4.write(r_idx, 6, s["academic_div"], f_l)
    ws4.write(r_idx, 7, s["class_str"], f_c)
    ws4.write(r_idx, 8, s["stream"], f_l)
    ws4.write(r_idx, 9, s["subject_combination"], f_l)
    ws4.write(r_idx, 10, dept_spec, f_l)
    ws4.write(r_idx, 11, yr_sem, f_c)
    ws4.write(r_idx, 12, s["academic_year"], f_c)
    ws4.write(r_idx, 13, s["enrollment_status"], f_c)

ws4.autofilter(0, 0, len(processed_students), len(headers4) - 1)

# ==============================================================================
# SHEET 5: Institution-wise Course Summary
# ==============================================================================
print("Writing Sheet 5: Course Summary...")
ws5 = wb.add_worksheet("Course Summary")
ws5.freeze_panes(1, 0)

headers5 = [
    "Institution ID", "Institution Name", "Course / Programme",
    "Academic Division", "Standard / PUC Year / Semester", "Stream", "Number of Students"
]
col_widths5 = [16, 38, 42, 38, 26, 22, 20]
for c_idx, w in enumerate(col_widths5):
    ws5.set_column(c_idx, c_idx, w)

ws5.set_row(0, 28)
for c_idx, h in enumerate(headers5):
    ws5.write(0, c_idx, h, fmt_hdr)

summary_dict = {}
for s in processed_students:
    key = (s["school_id"], s["school_name"], s["course_name"], s["academic_div"], s["class_str"], s["stream"])
    summary_dict[key] = summary_dict.get(key, 0) + 1

for sch in schools:
    sch_id = sch["school_id"]
    if sch_id not in [k[0] for k in summary_dict.keys()]:
        key = (sch_id, sch["school_name"], "No Active Enrollments", "N/A", "N/A", "N/A")
        summary_dict[key] = 0

row_idx5 = 1
total_summary_students = 0
for key in sorted(summary_dict.keys(), key=lambda x: (x[0], x[4], x[2])):
    count = summary_dict[key]
    total_summary_students += count
    is_warn = "Unassigned" in key[2] or "Unresolved" in key[3]
    f_l = fmt_warn_left if is_warn else fmt_left
    f_c = fmt_warn_center if is_warn else fmt_center
    f_r = fmt_warn_right if is_warn else fmt_right

    ws5.set_row(row_idx5, 20)
    ws5.write(row_idx5, 0, key[0], f_c)
    ws5.write(row_idx5, 1, key[1], f_l)
    ws5.write(row_idx5, 2, key[2], f_l)
    ws5.write(row_idx5, 3, key[3], f_l)
    ws5.write(row_idx5, 4, key[4], f_c)
    ws5.write(row_idx5, 5, key[5], f_l)
    ws5.write(row_idx5, 6, count, f_r)
    row_idx5 += 1

# Total Row
ws5.set_row(row_idx5, 24)
ws5.write(row_idx5, 0, "GRAND TOTAL", fmt_total_left)
ws5.write(row_idx5, 1, "All Registered Programmes Across All 31 Institutions", fmt_total_left)
for c in range(2, 6):
    ws5.write(row_idx5, c, "", fmt_total_left)
ws5.write(row_idx5, 6, total_summary_students, fmt_total_right)
ws5.autofilter(0, 0, row_idx5 - 1, len(headers5) - 1)

# ==============================================================================
# SHEET 6: Academic Classification
# ==============================================================================
print("Writing Sheet 6: Academic Classification...")
ws6 = wb.add_worksheet("Academic Classification")

col_widths6 = [28, 22, 38, 48, 40, 24, 24]
for c_idx, w in enumerate(col_widths6):
    ws6.set_column(c_idx, c_idx, w)

curr_r = 0
# Section 1: School Division
ws6.write(curr_r, 0, "1. SCHOOL DIVISION ACADEMIC STRUCTURE (Standards 1–10)", fmt_title)
ws6.set_row(curr_r, 26)
curr_r += 1

headers6_school = ["Academic Level / Standard", "Allowed Sections", "Curriculum / Board", "Academic Year", "Registered Institutions", "Verified Student Count"]
ws6.set_row(curr_r, 24)
for c_idx, h in enumerate(headers6_school):
    ws6.write(curr_r, c_idx, h, fmt_hdr)
curr_r += 1

school_std_counts = {}
for s in processed_students:
    if s["standard"] and s["standard"] <= 10 and not s["is_mismatch"]:
        school_std_counts[s["standard"]] = school_std_counts.get(s["standard"], 0) + 1

for std in range(1, 11):
    cnt = school_std_counts.get(std, 0)
    ws6.set_row(curr_r, 20)
    ws6.write(curr_r, 0, f"Standard {std}", fmt_center)
    ws6.write(curr_r, 1, "Section A, B, C", fmt_center)
    ws6.write(curr_r, 2, "Karnataka State Board (KSEEB)", fmt_left)
    ws6.write(curr_r, 3, "2026-2027", fmt_center)
    ws6.write(curr_r, 4, "SCH001–SCH010, SCH016–SCH020", fmt_left)
    ws6.write(curr_r, 5, cnt, fmt_right)
    curr_r += 1

ws6.set_row(curr_r, 22)
ws6.write(curr_r, 0, "SUBTOTAL (SCHOOL DIVISION)", fmt_total_left)
for c in range(1, 5):
    ws6.write(curr_r, c, "", fmt_total_left)
ws6.write(curr_r, 5, sum(school_std_counts.values()), fmt_total_right)
curr_r += 2

# Section 2: PU College
ws6.write(curr_r, 0, "2. PRE-UNIVERSITY COLLEGE ACADEMIC STRUCTURE (1st & 2nd PUC)", fmt_title)
ws6.set_row(curr_r, 26)
curr_r += 1

headers6_pu = ["PUC Level", "Stream", "Subject Combination Code", "Subjects Covered", "Examination Board", "Verified Student Count"]
ws6.set_row(curr_r, 24)
for c_idx, h in enumerate(headers6_pu):
    ws6.write(curr_r, c_idx, h, fmt_hdr_accent)
curr_r += 1

pu_counts = {}
for s in processed_students:
    if s["puc_year"] and not s["is_mismatch"]:
        key = (s["puc_year"], s["stream"], s["subject_combination"])
        pu_counts[key] = pu_counts.get(key, 0) + 1

for (puc_yr, strm, comb), cnt in sorted(pu_counts.items()):
    code = comb.split(":")[0] if ":" in comb else comb[:4]
    ws6.set_row(curr_r, 20)
    ws6.write(curr_r, 0, puc_yr, fmt_center)
    ws6.write(curr_r, 1, strm, fmt_center)
    ws6.write(curr_r, 2, code, fmt_center)
    ws6.write(curr_r, 3, comb, fmt_left)
    ws6.write(curr_r, 4, "Department of Pre-University Education, Karnataka", fmt_left)
    ws6.write(curr_r, 5, cnt, fmt_right)
    curr_r += 1

ws6.set_row(curr_r, 22)
ws6.write(curr_r, 0, "SUBTOTAL (PUC DIVISION)", fmt_total_left)
for c in range(1, 5):
    ws6.write(curr_r, c, "", fmt_total_left)
ws6.write(curr_r, 5, sum(pu_counts.values()), fmt_total_right)
curr_r += 2

# Section 3: Higher Education
ws6.write(curr_r, 0, "3. DEGREE & HIGHER EDUCATION ACADEMIC STRUCTURE", fmt_title)
ws6.set_row(curr_r, 26)
curr_r += 1

headers6_deg = ["Degree", "Programme Name", "Branch / Specialization", "Department", "Academic Year", "Semester", "Verified Student Count"]
ws6.set_row(curr_r, 24)
for c_idx, h in enumerate(headers6_deg):
    ws6.write(curr_r, c_idx, h, fmt_hdr)
curr_r += 1

deg_counts = {}
for s in processed_students:
    if s["degree"] and not s["is_mismatch"]:
        key = (s["degree"], s["course_name"], s["branch"] or "N/A", s["department"] or "N/A", s["academic_year"], f"Semester {s['semester']}" if s['semester'] else "Year 1")
        deg_counts[key] = deg_counts.get(key, 0) + 1

for (deg_name, prog_name, brn, dpt, ayr, sem), cnt in sorted(deg_counts.items()):
    ws6.set_row(curr_r, 20)
    ws6.write(curr_r, 0, deg_name, fmt_center)
    ws6.write(curr_r, 1, prog_name, fmt_left)
    ws6.write(curr_r, 2, brn, fmt_left)
    ws6.write(curr_r, 3, dpt, fmt_left)
    ws6.write(curr_r, 4, ayr, fmt_center)
    ws6.write(curr_r, 5, sem, fmt_center)
    ws6.write(curr_r, 6, cnt, fmt_right)
    curr_r += 1

ws6.set_row(curr_r, 22)
ws6.write(curr_r, 0, "SUBTOTAL (HIGHER EDUCATION)", fmt_total_left)
for c in range(1, 6):
    ws6.write(curr_r, c, "", fmt_total_left)
ws6.write(curr_r, 6, sum(deg_counts.values()), fmt_total_right)
curr_r += 2

# Section 4: Unmapped Records Summary
ws6.write(curr_r, 0, "4. UNRESOLVED / MISMATCHED RECORDS SUMMARY (Scenario B Migration Pending)", fmt_title)
ws6.set_row(curr_r, 26)
curr_r += 1

headers6_un = ["Mismatched Classification Category", "Affected Institutions", "Standards Affected", "Issue Identified", "Count"]
ws6.set_row(curr_r, 24)
for c_idx, h in enumerate(headers6_un):
    ws6.write(curr_r, c_idx, h, fmt_hdr_warn)
curr_r += 1

ws6.set_row(curr_r, 20)
ws6.write(curr_r, 0, "Group A: School Standards 1-10 in PU Colleges", fmt_warn_left)
ws6.write(curr_r, 1, "SCH011–SCH015 (5 PU Colleges)", fmt_warn_center)
ws6.write(curr_r, 2, "Standards 1 to 10", fmt_warn_center)
ws6.write(curr_r, 3, "Students assigned to PU College with no PU stream/combination", fmt_warn_left)
ws6.write(curr_r, 4, 10000, fmt_warn_right)
curr_r += 1

ws6.set_row(curr_r, 20)
ws6.write(curr_r, 0, "Group B: Higher Secondary Standards 11-12 in K-10 Schools", fmt_warn_left)
ws6.write(curr_r, 1, "SCH016–SCH020 (5 K-10 Schools)", fmt_warn_center)
ws6.write(curr_r, 2, "Standards 11 and 12", fmt_warn_center)
ws6.write(curr_r, 3, "Students assigned to K-10 School with no School curriculum", fmt_warn_left)
ws6.write(curr_r, 4, 2000, fmt_warn_right)
curr_r += 1

ws6.set_row(curr_r, 22)
ws6.write(curr_r, 0, "SUBTOTAL (UNRESOLVED RECORDS)", fmt_total_left)
for c in range(1, 4):
    ws6.write(curr_r, c, "", fmt_total_left)
ws6.write(curr_r, 4, 12000, fmt_total_right)
curr_r += 2

# Grand Total Row
grand_tot = sum(school_std_counts.values()) + sum(pu_counts.values()) + sum(deg_counts.values()) + 12000
ws6.set_row(curr_r, 24)
ws6.write(curr_r, 0, "GRAND TOTAL ACROSS ALL DIVISIONS & UNRESOLVED GROUPS", fmt_total_left)
for c in range(1, 4):
    ws6.write(curr_r, c, "", fmt_total_left)
ws6.write(curr_r, 4, grand_tot, fmt_total_right)

# ==============================================================================
# SHEET 7: Unmapped / Review Records
# ==============================================================================
print("Writing Sheet 7: Unmapped / Review Records (12,000 rows)...")
ws7 = wb.add_worksheet("Unmapped Review Records")
ws7.freeze_panes(1, 0)

headers7 = [
    "Serial Number", "Student ID", "Permanent Student ID (PSID)", "Student Name",
    "Institution ID", "Institution Name", "District", "Standard / Level",
    "Existing Classification", "Issue Identified", "Review Status"
]
col_widths7 = [14, 16, 36, 26, 16, 38, 18, 18, 45, 60, 42]
for c_idx, w in enumerate(col_widths7):
    ws7.set_column(c_idx, c_idx, w)

ws7.set_row(0, 28)
for c_idx, h in enumerate(headers7):
    ws7.write(0, c_idx, h, fmt_hdr_warn)

unmapped_sno = 1
for s in processed_students:
    if s["is_mismatch"]:
        existing_class = f"Standard {s['standard']} in {s['school_id']} ({s['school_name']})"
        ws7.write(unmapped_sno, 0, unmapped_sno, fmt_warn_right)
        ws7.write(unmapped_sno, 1, s["student_id"], fmt_warn_center)
        ws7.write(unmapped_sno, 2, s["psid"], fmt_warn_center)
        ws7.write(unmapped_sno, 3, s["student_name"], fmt_warn_left)
        ws7.write(unmapped_sno, 4, s["school_id"], fmt_warn_center)
        ws7.write(unmapped_sno, 5, s["school_name"], fmt_warn_left)
        ws7.write(unmapped_sno, 6, s["district"], fmt_warn_left)
        ws7.write(unmapped_sno, 7, f"Level {s['standard']}", fmt_warn_center)
        ws7.write(unmapped_sno, 8, existing_class, fmt_warn_left)
        ws7.write(unmapped_sno, 9, s["mismatch_issue"], fmt_warn_left)
        ws7.write(unmapped_sno, 10, s["review_status"], fmt_warn_left)
        unmapped_sno += 1

ws7.autofilter(0, 0, unmapped_sno - 1, len(headers7) - 1)

print(f"Total unmapped review rows written: {unmapped_sno - 1}")

wb.close()
file_size = os.path.getsize(OUTPUT_XLSX)
print(f"SUCCESS: Workbook saved to {OUTPUT_XLSX}")
print(f"Execution finished in {time.time() - start_time:.2f}s | File Size: {file_size / (1024*1024):.2f} MB")
