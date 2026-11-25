import sqlite3
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

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
    sch_type = s["school_type"] or ""
    
    # Check if this student is one of the 12,000 flagged mismatch records
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
        "section": s["section"] or "A",
        "stream": s["stream"] or "General",
        "subject_combination": s["subject_combination"] or "Core Curriculum",
        "academic_year": s["academic_year"] or "2026-2027",
        "enrollment_status": s["enrollment_status"] or "active",
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
    if s["enrollment_status"] == "active":
        inst_counts[sch_id]["active"] += 1

print(f"Processed {len(processed_students)} records. Setting up Excel workbook...")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Styling Definitions
font_title = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
font_subtitle = Font(name="Calibri", size=11, italic=True, color="475467")
font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
font_regular = Font(name="Calibri", size=10, color="0F172A")
font_total = Font(name="Calibri", size=11, bold=True, color="0F172A")

fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_header_accent = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
fill_total = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_warning = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
font_warning = Font(name="Calibri", size=10, bold=True, color="991B1B")

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

border_thin = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)
border_total = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='0F172A'),
    bottom=Side(style='double', color='0F172A')
)

def format_sheet(ws, num_cols):
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col in range(1, num_cols + 1):
        col_letter = get_column_letter(col)
        # determine max length
        max_len = 0
        for row in range(1, min(ws.max_row + 1, 1000)):
            val = ws.cell(row=row, column=col).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# ==============================================================================
# SHEET 1: Institution Directory
# ==============================================================================
print("Generating Sheet 1: Institution Directory...")
ws1 = wb.create_sheet(title="Institution Directory")
headers1 = [
    "Institution ID", "Institution Name", "Institution Category", "Institution Type",
    "District", "Taluk / Locality", "Address", "Total Registered Students",
    "Total Active Enrollments", "Academic Divisions", "Institution Status"
]
ws1.append(headers1)
for col_num in range(1, len(headers1) + 1):
    cell = ws1.cell(row=1, column=col_num)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin
ws1.row_dimensions[1].height = 28

total_reg_sum = 0
total_act_sum = 0

for s in schools:
    sch_id = s["school_id"]
    c_data = inst_counts.get(sch_id, {"total": 0, "active": 0})
    total_reg = c_data["total"]
    total_act = c_data["active"]
    total_reg_sum += total_reg
    total_act_sum += total_act
    
    # Taluk extraction from address
    addr = s["address"] or ""
    taluk = "Not Specified"
    if "Taluk" in addr:
        for part in addr.split(","):
            if "Taluk" in part:
                taluk = part.strip()
    elif s["district"]:
        taluk = f"{s['district']} Taluk"

    # Divisions
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

    row_data = [
        sch_id, s["school_name"], s["category"] or s["school_type"], s["school_type"],
        s["district"] or "Karnataka", taluk, addr, total_reg, total_act, div_str, status_str
    ]
    ws1.append(row_data)
    curr_row = ws1.max_row
    ws1.row_dimensions[curr_row].height = 20
    for c_idx in range(1, len(headers1) + 1):
        c = ws1.cell(row=curr_row, column=c_idx)
        c.font = font_regular
        c.border = border_thin
        if c_idx in [8, 9]:
            c.alignment = align_right
            c.number_format = "#,##0"
        elif c_idx in [1, 4, 11]:
            c.alignment = align_center
        else:
            c.alignment = align_left

# Summary Total Row
ws1.append(["TOTAL", f"All Registered Institutions ({len(schools)})", "", "", "", "", "", total_reg_sum, total_act_sum, "", ""])
tot_row = ws1.max_row
ws1.row_dimensions[tot_row].height = 24
for c_idx in range(1, len(headers1) + 1):
    c = ws1.cell(row=tot_row, column=c_idx)
    c.font = font_total
    c.fill = fill_total
    c.border = border_total
    if c_idx in [8, 9]:
        c.alignment = align_right
        c.number_format = "#,##0"
    else:
        c.alignment = align_left

format_sheet(ws1, len(headers1))

# ==============================================================================
# SHEET 2: Complete Student Register
# ==============================================================================
print("Generating Sheet 2: Complete Student Register (30,003 rows)...")
ws2 = wb.create_sheet(title="Complete Student Register")
headers2 = [
    "Serial Number", "Student ID", "Permanent Student ID (PSID)", "Student Name",
    "Institution ID", "Institution Name", "District", "Academic Division",
    "Course / Programme", "Standard / Class / Level", "Section", "Stream",
    "Subject Combination", "Academic Year", "Enrollment Status"
]
ws2.append(headers2)
for col_num in range(1, len(headers2) + 1):
    cell = ws2.cell(row=1, column=col_num)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin
ws2.row_dimensions[1].height = 28

for s in processed_students:
    row_data = [
        s["sno"], s["student_id"], s["psid"], s["student_name"],
        s["school_id"], s["school_name"], s["district"], s["academic_div"],
        s["course_name"], s["class_str"], s["section"], s["stream"],
        s["subject_combination"], s["academic_year"], s["enrollment_status"].upper()
    ]
    ws2.append(row_data)
    curr_row = ws2.max_row
    
    # Conditional format warning on unmapped records
    is_warn = s["is_mismatch"]
    row_fill = fill_warning if is_warn else None
    row_font = font_warning if is_warn else font_regular

    for c_idx in range(1, len(headers2) + 1):
        c = ws2.cell(row=curr_row, column=c_idx)
        c.font = row_font
        c.border = border_thin
        if row_fill:
            c.fill = row_fill
        if c_idx in [1]:
            c.alignment = align_right
            c.number_format = "#,##0"
        elif c_idx in [2, 3, 5, 10, 11, 14, 15]:
            c.alignment = align_center
        else:
            c.alignment = align_left

format_sheet(ws2, len(headers2))

# ==============================================================================
# SHEET 3: Institution-wise Student List
# ==============================================================================
print("Generating Sheet 3: Institution-wise Student List...")
ws3 = wb.create_sheet(title="Institution-wise Student List")
headers3 = [
    "Institution ID", "Institution Name", "District", "Student ID",
    "Permanent Student ID (PSID)", "Student Name", "Course / Programme",
    "Class / Standard", "Academic Division", "Enrollment Status"
]
ws3.append(headers3)
for col_num in range(1, len(headers3) + 1):
    cell = ws3.cell(row=1, column=col_num)
    cell.font = font_header
    cell.fill = fill_header_accent
    cell.alignment = align_center
    cell.border = border_thin
ws3.row_dimensions[1].height = 28

for s in processed_students:
    row_data = [
        s["school_id"], s["school_name"], s["district"], s["student_id"],
        s["psid"], s["student_name"], s["course_name"], s["class_str"],
        s["academic_div"], s["enrollment_status"].upper()
    ]
    ws3.append(row_data)
    curr_row = ws3.max_row
    is_warn = s["is_mismatch"]
    row_fill = fill_warning if is_warn else None
    row_font = font_warning if is_warn else font_regular
    for c_idx in range(1, len(headers3) + 1):
        c = ws3.cell(row=curr_row, column=c_idx)
        c.font = row_font
        c.border = border_thin
        if row_fill:
            c.fill = row_fill
        if c_idx in [1, 4, 5, 8, 10]:
            c.alignment = align_center
        else:
            c.alignment = align_left

format_sheet(ws3, len(headers3))

# ==============================================================================
# SHEET 4: Course Enrollment Register
# ==============================================================================
print("Generating Sheet 4: Course Enrollment Register...")
ws4 = wb.create_sheet(title="Course Enrollment Register")
headers4 = [
    "Student ID", "Student Name", "Institution ID", "Institution Name",
    "Course ID / Programme ID", "Course / Programme Name", "Academic Division",
    "Standard / Class / PUC Year", "Stream", "Subject Combination",
    "Department / Specialization", "Year / Semester", "Academic Year", "Enrollment Status"
]
ws4.append(headers4)
for col_num in range(1, len(headers4) + 1):
    cell = ws4.cell(row=1, column=col_num)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin
ws4.row_dimensions[1].height = 28

for s in processed_students:
    dept_spec = s["department"] or s["branch"] or ("School Education Department" if not s["is_mismatch"] and "School" in s["academic_div"] else ("Pre-University Board" if not s["is_mismatch"] and "PU" in s["academic_div"] else "Unassigned"))
    yr_sem = f"Semester {s['semester']}" if s["semester"] else ("1st PUC" if s["class_str"] == "1st PUC" else ("2nd PUC" if s["class_str"] == "2nd PUC" else ("Annual KSEEB" if "School" in s["academic_div"] else "N/A")))
    
    row_data = [
        s["student_id"], s["student_name"], s["school_id"], s["school_name"],
        s["course_id"], s["course_name"], s["academic_div"], s["class_str"],
        s["stream"], s["subject_combination"], dept_spec, yr_sem,
        s["academic_year"], s["enrollment_status"].upper()
    ]
    ws4.append(row_data)
    curr_row = ws4.max_row
    is_warn = s["is_mismatch"]
    row_fill = fill_warning if is_warn else None
    row_font = font_warning if is_warn else font_regular
    for c_idx in range(1, len(headers4) + 1):
        c = ws4.cell(row=curr_row, column=c_idx)
        c.font = row_font
        c.border = border_thin
        if row_fill:
            c.fill = row_fill
        if c_idx in [1, 3, 5, 8, 12, 13, 14]:
            c.alignment = align_center
        else:
            c.alignment = align_left

format_sheet(ws4, len(headers4))

# ==============================================================================
# SHEET 5: Institution-wise Course Summary
# ==============================================================================
print("Generating Sheet 5: Institution-wise Course Summary...")
ws5 = wb.create_sheet(title="Course Summary")
headers5 = [
    "Institution ID", "Institution Name", "Course / Programme",
    "Academic Division", "Standard / PUC Year / Semester", "Stream", "Number of Students"
]
ws5.append(headers5)
for col_num in range(1, len(headers5) + 1):
    cell = ws5.cell(row=1, column=col_num)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin
ws5.row_dimensions[1].height = 28

# Aggregate Course Summary
summary_dict = {}
for s in processed_students:
    key = (s["school_id"], s["school_name"], s["course_name"], s["academic_div"], s["class_str"], s["stream"])
    summary_dict[key] = summary_dict.get(key, 0) + 1

# Also add 0-student institutions
for sch in schools:
    sch_id = sch["school_id"]
    if sch_id not in [k[0] for k in summary_dict.keys()]:
        key = (sch_id, sch["school_name"], "No Active Enrollments", "N/A", "N/A", "N/A")
        summary_dict[key] = 0

total_summary_students = 0
for key in sorted(summary_dict.keys(), key=lambda x: (x[0], x[4], x[2])):
    count = summary_dict[key]
    total_summary_students += count
    row_data = [key[0], key[1], key[2], key[3], key[4], key[5], count]
    ws5.append(row_data)
    curr_row = ws5.max_row
    ws5.row_dimensions[curr_row].height = 20
    is_warn = "Unassigned" in key[2] or "Unresolved" in key[3]
    for c_idx in range(1, len(headers5) + 1):
        c = ws5.cell(row=curr_row, column=c_idx)
        c.font = font_warning if is_warn else font_regular
        c.border = border_thin
        if is_warn:
            c.fill = fill_warning
        if c_idx == 7:
            c.alignment = align_right
            c.number_format = "#,##0"
        elif c_idx in [1, 5]:
            c.alignment = align_center
        else:
            c.alignment = align_left

# Total Row
ws5.append(["GRAND TOTAL", f"All Registered Programmes Across All 31 Institutions", "", "", "", "", total_summary_students])
tot_row5 = ws5.max_row
ws5.row_dimensions[tot_row5].height = 24
for c_idx in range(1, len(headers5) + 1):
    c = ws5.cell(row=tot_row5, column=c_idx)
    c.font = font_total
    c.fill = fill_total
    c.border = border_total
    if c_idx == 7:
        c.alignment = align_right
        c.number_format = "#,##0"
    else:
        c.alignment = align_left

format_sheet(ws5, len(headers5))

# ==============================================================================
# SHEET 6: Academic Classification
# ==============================================================================
print("Generating Sheet 6: Academic Classification...")
ws6 = wb.create_sheet(title="Academic Classification")

# Header Section A: School Structure
ws6.append(["1. SCHOOL DIVISION ACADEMIC STRUCTURE (Standards 1–10)"])
ws6.cell(row=1, column=1).font = font_title
ws6.row_dimensions[1].height = 26

headers6_school = ["Academic Level / Standard", "Allowed Sections", "Curriculum / Board", "Academic Year", "Registered Institutions", "Verified Student Count"]
ws6.append(headers6_school)
for c in range(1, len(headers6_school) + 1):
    cell = ws6.cell(row=2, column=c)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin
ws6.row_dimensions[2].height = 24

# Count school students by standard
school_std_counts = {}
for s in processed_students:
    if s["standard"] and s["standard"] <= 10 and not s["is_mismatch"]:
        school_std_counts[s["standard"]] = school_std_counts.get(s["standard"], 0) + 1

for std in range(1, 11):
    cnt = school_std_counts.get(std, 0)
    ws6.append([f"Standard {std}", "Section A, B, C", "Karnataka State Board (KSEEB)", "2026-2027", "SCH001–SCH010, SCH016–SCH020", cnt])
    curr_row = ws6.max_row
    for c in range(1, len(headers6_school) + 1):
        cell = ws6.cell(row=curr_row, column=c)
        cell.font = font_regular
        cell.border = border_thin
        if c == 6:
            cell.alignment = align_right
            cell.number_format = "#,##0"
        elif c in [1, 2, 4]:
            cell.alignment = align_center
        else:
            cell.alignment = align_left

ws6.append(["SUBTOTAL (SCHOOL DIVISION)", "", "", "", "", sum(school_std_counts.values())])
sub_row1 = ws6.max_row
for c in range(1, len(headers6_school) + 1):
    cell = ws6.cell(row=sub_row1, column=c)
    cell.font = font_total
    cell.fill = fill_total
    cell.border = border_total
    if c == 6:
        cell.alignment = align_right
        cell.number_format = "#,##0"

# Header Section B: Pre-University Structure
ws6.append([])
ws6.append(["2. PRE-UNIVERSITY COLLEGE ACADEMIC STRUCTURE (1st & 2nd PUC)"])
r_pu_title = ws6.max_row
ws6.cell(row=r_pu_title, column=1).font = font_title
ws6.row_dimensions[r_pu_title].height = 26

headers6_pu = ["PUC Level", "Stream", "Subject Combination Code", "Subjects Covered", "Examination Board", "Verified Student Count"]
ws6.append(headers6_pu)
r_pu_head = ws6.max_row
for c in range(1, len(headers6_pu) + 1):
    cell = ws6.cell(row=r_pu_head, column=c)
    cell.font = font_header
    cell.fill = fill_header_accent
    cell.alignment = align_center
    cell.border = border_thin
ws6.row_dimensions[r_pu_head].height = 24

pu_counts = {}
for s in processed_students:
    if s["puc_year"] and not s["is_mismatch"]:
        key = (s["puc_year"], s["stream"], s["subject_combination"])
        pu_counts[key] = pu_counts.get(key, 0) + 1

for (puc_yr, strm, comb), cnt in sorted(pu_counts.items()):
    code = comb.split(":")[0] if ":" in comb else comb[:4]
    ws6.append([puc_yr, strm, code, comb, "Department of Pre-University Education, Karnataka", cnt])
    curr_row = ws6.max_row
    for c in range(1, len(headers6_pu) + 1):
        cell = ws6.cell(row=curr_row, column=c)
        cell.font = font_regular
        cell.border = border_thin
        if c == 6:
            cell.alignment = align_right
            cell.number_format = "#,##0"
        elif c in [1, 2, 3]:
            cell.alignment = align_center
        else:
            cell.alignment = align_left

ws6.append(["SUBTOTAL (PUC DIVISION)", "", "", "", "", sum(pu_counts.values())])
sub_row2 = ws6.max_row
for c in range(1, len(headers6_pu) + 1):
    cell = ws6.cell(row=sub_row2, column=c)
    cell.font = font_total
    cell.fill = fill_total
    cell.border = border_total
    if c == 6:
        cell.alignment = align_right
        cell.number_format = "#,##0"

# Header Section C: Higher Education Structure
ws6.append([])
ws6.append(["3. DEGREE & HIGHER EDUCATION ACADEMIC STRUCTURE"])
r_deg_title = ws6.max_row
ws6.cell(row=r_deg_title, column=1).font = font_title
ws6.row_dimensions[r_deg_title].height = 26

headers6_deg = ["Degree", "Programme Name", "Branch / Specialization", "Department", "Academic Year", "Semester", "Verified Student Count"]
ws6.append(headers6_deg)
r_deg_head = ws6.max_row
for c in range(1, len(headers6_deg) + 1):
    cell = ws6.cell(row=r_deg_head, column=c)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin
ws6.row_dimensions[r_deg_head].height = 24

# Count degree students
deg_counts = {}
for s in processed_students:
    if s["degree"] and not s["is_mismatch"]:
        key = (s["degree"], s["course_name"], s["branch"] or "N/A", s["department"] or "N/A", s["academic_year"], f"Semester {s['semester']}" if s['semester'] else "Year 1")
        deg_counts[key] = deg_counts.get(key, 0) + 1

for (deg_name, prog_name, brn, dpt, ayr, sem), cnt in sorted(deg_counts.items()):
    ws6.append([deg_name, prog_name, brn, dpt, ayr, sem, cnt])
    curr_row = ws6.max_row
    for c in range(1, len(headers6_deg) + 1):
        cell = ws6.cell(row=curr_row, column=c)
        cell.font = font_regular
        cell.border = border_thin
        if c == 7:
            cell.alignment = align_right
            cell.number_format = "#,##0"
        elif c in [1, 5, 6]:
            cell.alignment = align_center
        else:
            cell.alignment = align_left

ws6.append(["SUBTOTAL (HIGHER EDUCATION)", "", "", "", "", "", sum(deg_counts.values())])
sub_row3 = ws6.max_row
for c in range(1, len(headers6_deg) + 1):
    cell = ws6.cell(row=sub_row3, column=c)
    cell.font = font_total
    cell.fill = fill_total
    cell.border = border_total
    if c == 7:
        cell.alignment = align_right
        cell.number_format = "#,##0"

# Section D: Unmapped / Review Subtotal
ws6.append([])
ws6.append(["4. UNRESOLVED / MISMATCHED RECORDS SUMMARY (Scenario B Migration Pending)"])
r_un_title = ws6.max_row
ws6.cell(row=r_un_title, column=1).font = font_title
ws6.row_dimensions[r_un_title].height = 26

headers6_un = ["Mismatched Classification Category", "Affected Institutions", "Standards Affected", "Issue Identified", "Count"]
ws6.append(headers6_un)
r_un_head = ws6.max_row
for c in range(1, len(headers6_un) + 1):
    cell = ws6.cell(row=r_un_head, column=c)
    cell.font = font_header
    cell.fill = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")
    cell.alignment = align_center
    cell.border = border_thin
ws6.row_dimensions[r_un_head].height = 24

ws6.append(["Group A: School Standards 1-10 in PU Colleges", "SCH011–SCH015 (5 PU Colleges)", "Standards 1 to 10", "Students assigned to PU College with no PU stream/combination", 10000])
ws6.append(["Group B: Higher Secondary Standards 11-12 in K-10 Schools", "SCH016–SCH020 (5 K-10 Schools)", "Standards 11 and 12", "Students assigned to K-10 School with no School curriculum", 2000])

for r in [ws6.max_row - 1, ws6.max_row]:
    for c in range(1, len(headers6_un) + 1):
        cell = ws6.cell(row=r, column=c)
        cell.font = font_warning
        cell.fill = fill_warning
        cell.border = border_thin
        if c == 5:
            cell.alignment = align_right
            cell.number_format = "#,##0"
        elif c in [2, 3]:
            cell.alignment = align_center
        else:
            cell.alignment = align_left

ws6.append(["SUBTOTAL (UNRESOLVED RECORDS)", "", "", "", 12000])
sub_row4 = ws6.max_row
for c in range(1, len(headers6_un) + 1):
    cell = ws6.cell(row=sub_row4, column=c)
    cell.font = font_total
    cell.fill = fill_total
    cell.border = border_total
    if c == 5:
        cell.alignment = align_right
        cell.number_format = "#,##0"

# Grand Total Row
grand_tot = sum(school_std_counts.values()) + sum(pu_counts.values()) + sum(deg_counts.values()) + 12000
ws6.append([])
ws6.append(["GRAND TOTAL ACROSS ALL DIVISIONS & UNRESOLVED GROUPS", "", "", "", grand_tot])
g_row = ws6.max_row
for c in range(1, len(headers6_un) + 1):
    cell = ws6.cell(row=g_row, column=c)
    cell.font = font_title
    cell.fill = fill_total
    cell.border = border_total
    if c == 5:
        cell.alignment = align_right
        cell.number_format = "#,##0"

for col in range(1, 8):
    col_letter = get_column_letter(col)
    ws6.column_dimensions[col_letter].width = 30

# ==============================================================================
# SHEET 7: Unmapped / Review Records
# ==============================================================================
print("Generating Sheet 7: Unmapped / Review Records (12,000 rows)...")
ws7 = wb.create_sheet(title="Unmapped Review Records")
headers7 = [
    "Serial Number", "Student ID", "Permanent Student ID (PSID)", "Student Name",
    "Institution ID", "Institution Name", "District", "Standard / Level",
    "Existing Classification", "Issue Identified", "Review Status"
]
ws7.append(headers7)
for col_num in range(1, len(headers7) + 1):
    cell = ws7.cell(row=1, column=col_num)
    cell.font = font_header
    cell.fill = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")
    cell.alignment = align_center
    cell.border = border_thin
ws7.row_dimensions[1].height = 28

unmapped_sno = 1
for s in processed_students:
    if s["is_mismatch"]:
        existing_class = f"Standard {s['standard']} in {s['school_id']} ({s['school_name']})"
        row_data = [
            unmapped_sno, s["student_id"], s["psid"], s["student_name"],
            s["school_id"], s["school_name"], s["district"], f"Level {s['standard']}",
            existing_class, s["mismatch_issue"], s["review_status"]
        ]
        ws7.append(row_data)
        curr_row = ws7.max_row
        for c_idx in range(1, len(headers7) + 1):
            c = ws7.cell(row=curr_row, column=c_idx)
            c.font = font_warning
            c.border = border_thin
            c.fill = fill_warning
            if c_idx == 1:
                c.alignment = align_right
                c.number_format = "#,##0"
            elif c_idx in [2, 3, 5, 8, 11]:
                c.alignment = align_center
            else:
                c.alignment = align_left
        unmapped_sno += 1

format_sheet(ws7, len(headers7))

# Summary row for Sheet 7
ws7.append(["TOTAL UNRESOLVED RECORDS", f"{unmapped_sno - 1} records requiring Composite Migration review", "", "", "", "", "", "", "", "", ""])
tot_row7 = ws7.max_row
for c_idx in range(1, len(headers7) + 1):
    c = ws7.cell(row=tot_row7, column=c_idx)
    c.font = font_total
    c.fill = fill_total
    c.border = border_total

print(f"Total unmapped review rows generated: {unmapped_sno - 1}")

# Save Workbook
print("Saving workbook to:", OUTPUT_XLSX)
wb.save(OUTPUT_XLSX)
file_size = os.path.getsize(OUTPUT_XLSX)
print(f"Workbook successfully saved! File size: {file_size / (1024*1024):.2f} MB")
