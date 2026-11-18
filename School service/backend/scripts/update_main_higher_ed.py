import re

MAIN_PATH = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(MAIN_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. In get_school_programs, add faculty_name, department_name and category-specific filtering
old_prog_query = """            SELECT p.program_id, p.institution_id as school_id, p.education_level,
                   p.program_name, p.degree_type, p.discipline_or_stream,
                   p.combination_code, p.duration_years,
                   p.is_active,
                   COALESCE(SUM(ps.capacity), 0) as total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) as total_strength,
                   COUNT(ps.section_id) as section_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ? AND p.is_active = 1
        \"\"\"
        params = [school_id]
        
        # Category-specific filtering: PU colleges only offer higher_secondary
        cat = school["category"] or ""
        stype = school["school_type"] or ""
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'\""""

new_prog_query = """            SELECT p.program_id, p.institution_id as school_id, p.education_level,
                   p.program_name, p.degree_type, p.discipline_or_stream,
                   p.combination_code, p.faculty_name, p.department_name, p.duration_years,
                   p.is_active,
                   COALESCE(SUM(ps.capacity), 0) as total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) as total_strength,
                   COUNT(ps.section_id) as section_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ? AND p.is_active = 1
        \"\"\"
        params = [school_id]
        
        # Category-specific filtering
        cat = school["category"] or ""
        stype = school["school_type"] or ""
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'"
        elif cat == "Degree Colleges" or stype == "Degree College":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate')"
        elif cat == "Universities" or stype == "University":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate', 'doctoral')\""""

assert old_prog_query in content, "old_prog_query not found in main.py"
content = content.replace(old_prog_query, new_prog_query, 1)

# 2. In get_school_seat_availability, add faculty_name, department_name and category-specific filtering
old_seat_query = """            SELECT ps.section_id, ps.program_id, p.program_name, p.education_level,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   ps.academic_year, ps.term_or_year, ps.semester, ps.section_name,
                   ps.capacity, ps.current_strength,
                   MAX(0, ps.capacity - ps.current_strength) AS available_seats
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE ps.institution_id = ?
        \"\"\"
        params = [school_id]

        if academic_year and academic_year.lower() != 'all':
            sql += " AND ps.academic_year = ?"
            params.append(academic_year)
        else:
            # Auto-detect active academic year from institution sections
            ay_row = conn.execute(
                "SELECT academic_year FROM program_sections WHERE institution_id = ? ORDER BY academic_year DESC LIMIT 1",
                (school_id,)
            ).fetchone()
            if ay_row and ay_row["academic_year"]:
                active_ay = ay_row["academic_year"]
                sql += " AND ps.academic_year = ?"
                params.append(active_ay)
                academic_year = active_ay
            else:
                academic_year = "2026-27"

        # For PU colleges, only return higher_secondary sections
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'\""""

new_seat_query = """            SELECT ps.section_id, ps.program_id, p.program_name, p.education_level,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   p.faculty_name, p.department_name,
                   ps.academic_year, ps.term_or_year, ps.semester, ps.section_name,
                   ps.capacity, ps.current_strength,
                   MAX(0, ps.capacity - ps.current_strength) AS available_seats
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE ps.institution_id = ?
        \"\"\"
        params = [school_id]

        if academic_year and academic_year.lower() != 'all':
            sql += " AND ps.academic_year = ?"
            params.append(academic_year)
        else:
            # Auto-detect active academic year from institution sections
            ay_row = conn.execute(
                "SELECT academic_year FROM program_sections WHERE institution_id = ? ORDER BY academic_year DESC LIMIT 1",
                (school_id,)
            ).fetchone()
            if ay_row and ay_row["academic_year"]:
                active_ay = ay_row["academic_year"]
                sql += " AND ps.academic_year = ?"
                params.append(active_ay)
                academic_year = active_ay
            else:
                academic_year = "2026-27"

        # Category-specific filtering
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'"
        elif cat == "Degree Colleges" or stype == "Degree College":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate')"
        elif cat == "Universities" or stype == "University":
            sql += " AND p.education_level IN ('undergraduate', 'postgraduate', 'doctoral')\""""

assert old_seat_query in content, "old_seat_query not found in main.py"
content = content.replace(old_seat_query, new_seat_query, 1)

# 3. Add academic-hierarchy endpoint right after get_school_divisions
hierarchy_endpoint = '''


@app.get("/schools/{school_id}/academic-hierarchy")
def get_school_academic_hierarchy(school_id: str):
    """
    Returns the formal hierarchical academic structure for an institution.
    For Universities:
      University -> Faculty/School -> Department -> Programme -> Academic Year/Level
    For Degree Colleges:
      Displays degree programmes with specialisations, branches, and university affiliation.
    """
    conn = get_connection()
    try:
        school = conn.execute(
            """
            SELECT school_id, school_name, school_type, category, affiliation,
                   recognition, campus_name, district, state
            FROM schools
            WHERE school_id = ?
            """,
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "Institution not found")

        cat = school["category"] or ""
        stype = school["school_type"] or ""
        is_univ = cat == "Universities" or stype == "University"
        is_college = cat == "Degree Colleges" or stype == "Degree College"

        # Fetch active divisions / faculties
        div_rows = conn.execute(
            """
            SELECT division_id, division_name, division_type, campus_location,
                   head_of_division, contact_phone, contact_email, description, display_order
            FROM institution_divisions
            WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            """,
            (school_id,),
        ).fetchall()
        divisions = [dict(d) for d in div_rows]

        # Fetch active academic programs
        prog_rows = conn.execute(
            """
            SELECT p.program_id, p.institution_id, p.education_level, p.program_name,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   p.faculty_name, p.department_name, p.duration_years, p.is_active,
                   COALESCE(SUM(ps.capacity), 0) AS total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) AS total_strength,
                   COALESCE(SUM(MAX(0, ps.capacity - ps.current_strength)), 0) AS available_seats,
                   COUNT(ps.section_id) AS sections_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ? AND p.is_active = 1
            GROUP BY p.program_id
            ORDER BY 
                CASE p.education_level 
                    WHEN 'undergraduate' THEN 1 
                    WHEN 'postgraduate' THEN 2 
                    WHEN 'doctoral' THEN 3 
                    ELSE 4 
                END,
                p.faculty_name, p.department_name, p.program_name
            """,
            (school_id,),
        ).fetchall()
        programs = [dict(p) for p in prog_rows]

        # Build hierarchical structure for University
        faculties_dict = {}
        for d in divisions:
            faculties_dict[d["division_name"]] = {
                "faculty_name": d["division_name"],
                "division_id": d["division_id"],
                "division_type": d["division_type"],
                "head_of_division": d["head_of_division"],
                "campus_location": d["campus_location"],
                "contact_email": d["contact_email"],
                "description": d["description"],
                "departments": {}
            }

        for p in programs:
            fac_name = p.get("faculty_name") or "General Studies"
            dept_name = p.get("department_name") or (p.get("discipline_or_stream") or "General Department")
            
            if fac_name not in faculties_dict:
                faculties_dict[fac_name] = {
                    "faculty_name": fac_name,
                    "division_id": None,
                    "division_type": "Faculty",
                    "head_of_division": None,
                    "campus_location": None,
                    "contact_email": None,
                    "description": None,
                    "departments": {}
                }

            if dept_name not in faculties_dict[fac_name]["departments"]:
                faculties_dict[fac_name]["departments"][dept_name] = {
                    "department_name": dept_name,
                    "programmes": []
                }

            faculties_dict[fac_name]["departments"][dept_name]["programmes"].append({
                "program_id": p["program_id"],
                "program_name": p["program_name"],
                "education_level": p["education_level"],
                "degree_type": p["degree_type"],
                "discipline_or_stream": p["discipline_or_stream"],
                "duration_years": p["duration_years"],
                "total_capacity": p["total_capacity"],
                "total_strength": p["total_strength"],
                "available_seats": p["available_seats"],
                "sections_count": p["sections_count"]
            })

        # Format faculties into a clean list
        faculties_list = []
        for f in faculties_dict.values():
            depts_list = []
            for d in f["departments"].values():
                depts_list.append(d)
            f_copy = {**f, "departments": depts_list}
            faculties_list.append(f_copy)

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "category": school["category"],
            "school_type": school["school_type"],
            "is_university": is_univ,
            "is_degree_college": is_college,
            "affiliation": school["affiliation"],
            "recognition": school["recognition"],
            "campus_name": school["campus_name"],
            "district": school["district"],
            "state": school["state"],
            "faculties": faculties_list,
            "total_programs": len(programs),
            "programs_flat": programs
        }
    finally:
        conn.close()
'''

target_after = """            SELECT division_id, parent_institution_id, division_name,
                   division_type, campus_location, head_of_division,
                   contact_phone, contact_email, facilities_summary,
                   description, display_order
            FROM institution_divisions
            WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            \"\"\",
            (school_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()"""

assert target_after in content, "target_after not found in main.py"
content = content.replace(target_after, target_after + hierarchy_endpoint, 1)

with open(MAIN_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Successfully updated backend/main.py with higher education academic structure and hierarchy endpoints!")
