import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cursor = conn.cursor()

for s_id in ['SCH001', 'SCH011', 'COL001', 'COL002', 'COL008']:
    print(f"\n==================== {s_id} ====================")
    school = cursor.execute("SELECT school_name, school_type, affiliation, is_parent_group FROM schools WHERE school_id = ?", (s_id,)).fetchone()
    print("School:", school)
    
    divs = cursor.execute("SELECT division_id, division_name, division_type, campus_location FROM institution_divisions WHERE parent_institution_id = ?", (s_id,)).fetchall()
    print(f"Divisions ({len(divs)}):")
    for d in divs:
        print("  -", d)

    progs = cursor.execute("SELECT program_id, education_level, program_name, degree_type, discipline_or_stream, combination_code, duration_years FROM academic_programs WHERE institution_id = ?", (s_id,)).fetchall()
    print(f"Programs ({len(progs)}):")
    for p in progs:
        print("  -", p)

    sec_cnt = cursor.execute("SELECT COUNT(*) FROM program_sections WHERE institution_id = ?", (s_id,)).fetchone()[0]
    enr_cnt = cursor.execute("SELECT COUNT(*) FROM enrollments WHERE school_id = ?", (s_id,)).fetchone()[0]
    print(f"Sections count: {sec_cnt}, Enrollments count: {enr_cnt}")
    
    sample_secs = cursor.execute("SELECT section_id, program_id, academic_year, term_or_year, semester, section_name, capacity, current_strength FROM program_sections WHERE institution_id = ? LIMIT 4", (s_id,)).fetchall()
    for s in sample_secs:
        print("    Sec:", s)
