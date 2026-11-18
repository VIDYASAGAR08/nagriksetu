MAIN_PATH = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(MAIN_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Replace get_admission_form_config
old_cfg = """@app.get("/admissions/form-config/{institution_id}")
def get_admission_form_config(institution_id: str):
    \"\"\"
    Returns database-driven Stage 1 configuration for an institution.
    Provides valid standards, languages, streams, combinations, and programs without hardcoding.
    \"\"\"
    conn = get_connection()
    try:
        inst = conn.execute(
            \"\"\"
            SELECT school_id, school_name, school_type, affiliation, district, state
            FROM schools WHERE school_id = ?
            \"\"\",
            (institution_id,)
        ).fetchone()
        if not inst:
            raise HTTPException(404, f"Institution {institution_id} not found.")

        # 1. Divisions
        div_rows = conn.execute(
            \"\"\"
            SELECT division_id, division_name, division_type, campus_location
            FROM institution_divisions WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            \"\"\",
            (institution_id,)
        ).fetchall()
        divisions = [dict(d) for d in div_rows]

        # 2. Academic programs
        prog_rows = conn.execute(
            \"\"\"
            SELECT program_id, education_level, program_name, degree_type, discipline_or_stream, combination_code, duration_years
            FROM academic_programs WHERE institution_id = ? AND is_active = 1
            ORDER BY education_level, program_name
            \"\"\",
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
            \"\"\"
            SELECT COALESCE(SUM(capacity), 0) AS total_capacity,
                   COALESCE(SUM(current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN capacity > current_strength THEN capacity - current_strength ELSE 0 END), 0) AS available_seats
            FROM program_sections WHERE institution_id = ?
            \"\"\",
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
        conn.close()"""

new_cfg = """@app.get("/admissions/form-config/{institution_id}")
def get_admission_form_config(institution_id: str):
    \"\"\"
    Returns database-driven Stage 1 configuration for an institution.
    Provides valid standards, languages, streams, combinations, and programs without hardcoding.
    Strictly isolates Schools (K-10), PU Colleges, Degree Colleges, and Universities.
    \"\"\"
    conn = get_connection()
    try:
        inst = conn.execute(
            \"\"\"
            SELECT school_id, school_name, school_type, category, affiliation, district, state
            FROM schools WHERE school_id = ?
            \"\"\",
            (institution_id,)
        ).fetchone()
        if not inst:
            raise HTTPException(404, f"Institution {institution_id} not found.")

        cat = inst["category"] or ""
        stype = inst["school_type"] or ""
        is_school = cat == "Schools (K-10)" or stype == "School"
        is_pu = cat == "PU Colleges (11-12)" or "PU" in stype
        is_college = cat == "Degree Colleges" or stype == "Degree College"
        is_univ = cat == "Universities" or stype == "University"

        # 1. Divisions
        div_rows = conn.execute(
            \"\"\"
            SELECT division_id, division_name, division_type, campus_location
            FROM institution_divisions WHERE parent_institution_id = ?
            ORDER BY display_order ASC
            \"\"\",
            (institution_id,)
        ).fetchall()
        divisions = [dict(d) for d in div_rows]

        # 2. Academic programs
        prog_rows = conn.execute(
            \"\"\"
            SELECT program_id, education_level, program_name, degree_type, discipline_or_stream, combination_code, duration_years
            FROM academic_programs WHERE institution_id = ? AND is_active = 1
            ORDER BY education_level, program_name
            \"\"\",
            (institution_id,)
        ).fetchall()
        programs = [dict(p) for p in prog_rows]

        # 3. Detect offered education categories strictly by institution category
        if is_school:
            offered_levels = ["school"]
        elif is_pu:
            offered_levels = ["higher_secondary"]
        elif is_college:
            offered_levels = ["undergraduate"]
        elif is_univ:
            offered_levels = [lvl for lvl in ["undergraduate", "postgraduate", "doctoral"] if any(p["education_level"] == lvl for p in programs)]
            if not offered_levels:
                offered_levels = ["undergraduate"]
        else:
            offered_levels = sorted(list(set(p["education_level"] for p in programs))) or ["school"]

        # 4. Standard levels for schools (1 to 10)
        has_school = is_school or "school" in offered_levels
        standards = list(range(1, 11)) if has_school else []

        # 5. Language options (from enrollments or institutional standards)
        lang_rows = conn.execute(
            "SELECT DISTINCT first_language FROM enrollments WHERE school_id = ? AND first_language IS NOT NULL",
            (institution_id,)
        ).fetchall()
        first_languages = [r[0] for r in lang_rows] if lang_rows else ["Kannada", "English"]
        second_languages = ["English", "Kannada", "Hindi", "Sanskrit"]

        # School specific programs
        school_programs = [
            {
                "program_id": p["program_id"],
                "program_name": p["program_name"]
            }
            for p in programs if p["education_level"] == "school"
        ]

        # 6. PU Streams & Combinations (ONLY for PU Colleges, NEVER for Schools)
        pu_combinations = []
        pu_streams = set()
        if is_pu or (not is_school and "higher_secondary" in offered_levels):
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

        # 7. Diploma Programs (NEVER for Schools)
        diploma_programs = []
        if not is_school and "diploma" in offered_levels:
            diploma_programs = [
                {
                    "program_id": p["program_id"],
                    "program_name": p["program_name"],
                    "discipline_or_stream": p["discipline_or_stream"],
                    "duration_years": p["duration_years"]
                }
                for p in programs if p["education_level"] == "diploma"
            ]

        # 8. Undergraduate Programs (NEVER for Schools)
        ug_programs = []
        if not is_school and any(lvl in offered_levels for lvl in ["undergraduate", "postgraduate", "doctoral"]):
            ug_programs = [
                {
                    "program_id": p["program_id"],
                    "program_name": p["program_name"],
                    "degree_type": p["degree_type"],
                    "discipline_or_stream": p["discipline_or_stream"],
                    "duration_years": p["duration_years"]
                }
                for p in programs if p["education_level"] in ["undergraduate", "postgraduate", "doctoral"]
            ]

        # 9. Seat availability summary
        seat_summary = conn.execute(
            \"\"\"
            SELECT COALESCE(SUM(capacity), 0) AS total_capacity,
                   COALESCE(SUM(current_strength), 0) AS total_strength,
                   COALESCE(SUM(CASE WHEN capacity > current_strength THEN capacity - current_strength ELSE 0 END), 0) AS available_seats
            FROM program_sections WHERE institution_id = ?
            \"\"\",
            (institution_id,)
        ).fetchone()

        return {
            "institution_id": inst["school_id"],
            "institution_name": inst["school_name"],
            "school_type": inst["school_type"],
            "category": inst["category"],
            "is_school": is_school,
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
                "programs": school_programs
            } if has_school else None,
            "pu_config": {
                "levels": ["1st PU (Class 11)", "2nd PU (Class 12)"],
                "streams": sorted(list(pu_streams)) if pu_streams else ["Science", "Commerce", "Arts"],
                "combinations": pu_combinations,
            } if (is_pu or (not is_school and "higher_secondary" in offered_levels)) and (pu_combinations or pu_streams) else None,
            "diploma_config": {
                "programs": diploma_programs,
            } if diploma_programs else None,
            "undergraduate_config": {
                "programs": ug_programs,
            } if ug_programs else None,
            "seat_summary": dict(seat_summary) if seat_summary else {"total_capacity": 0, "available_seats": 0},
            "status": "ready"
        }
    finally:
        conn.close()"""

assert old_cfg in content, "old_cfg not found in main.py"
content = content.replace(old_cfg, new_cfg, 1)

# Now update submit_stage1_admission_application for strict school validation
old_sub = """        # 1. Verify institution exists
        inst = conn.execute(
            "SELECT school_id, school_name, school_type FROM schools WHERE school_id = ?",
            (payload.institution_id,),
        ).fetchone()
        if not inst:
            raise HTTPException(404, "Selected institution not found.")"""

new_sub = """        # 1. Verify institution exists
        inst = conn.execute(
            "SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?",
            (payload.institution_id,),
        ).fetchone()
        if not inst:
            raise HTTPException(404, "Selected institution not found.")

        cat = inst["category"] or ""
        stype = inst["school_type"] or ""
        is_school = cat == "Schools (K-10)" or stype == "School"
        is_pu = cat == "PU Colleges (11-12)" or "PU" in stype"""

assert old_sub in content, "old_sub not found in main.py"
content = content.replace(old_sub, new_sub, 1)

old_val = """        # 4. Type-specific validation against database
        level = payload.education_level.lower()
        if level == "school":
            if not payload.requested_standard or not (1 <= payload.requested_standard <= 10):
                raise HTTPException(400, "School admission requires a valid standard between 1 and 10.")
            if not payload.first_language_preference:
                payload.first_language_preference = "Kannada"
        elif level == "higher_secondary":"""

new_val = """        # 4. Type-specific validation against database
        level = payload.education_level.lower()
        if is_school:
            if level != "school":
                raise HTTPException(400, f"Institution '{inst['school_name']}' is a School (K-10) and only accepts School Education (K-10) applications. Pre-University programme data is not allowed.")
            if payload.combination_code or payload.stream_preference:
                raise HTTPException(400, "School admission does not accept PU streams or combinations.")
        elif is_pu:
            if level != "higher_secondary":
                raise HTTPException(400, f"Institution '{inst['school_name']}' is a Pre-University College and only accepts Pre-University (Classes 11-12) applications.")

        if level == "school":
            if not payload.requested_standard or not (1 <= payload.requested_standard <= 10):
                raise HTTPException(400, "School admission requires a valid standard between 1 and 10.")
            if not payload.first_language_preference:
                payload.first_language_preference = "Kannada"
        elif level == "higher_secondary":"""

assert old_val in content, "old_val not found in main.py"
content = content.replace(old_val, new_val, 1)

with open(MAIN_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Successfully updated backend/main.py for strict school admission validation!")
