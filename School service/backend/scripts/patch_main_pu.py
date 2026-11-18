path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update get_school_programs
old_get_programs = '''@app.get("/schools/{school_id}/programs")
def get_school_programs(school_id: str):
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "School not found")

        programs = conn.execute(
            """
            SELECT p.program_id, p.institution_id as school_id, p.education_level,
                   p.program_name, p.degree_type, p.discipline_or_stream,
                   p.combination_code, p.duration_years,
                   p.is_active,
                   COALESCE(SUM(ps.capacity), 0) as total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) as total_strength,
                   COUNT(ps.section_id) as section_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ?
            GROUP BY p.program_id
            ORDER BY 
                CASE p.education_level 
                    WHEN 'school' THEN 1 
                    WHEN 'higher_secondary' THEN 2 
                    WHEN 'diploma' THEN 3 
                    WHEN 'undergraduate' THEN 4 
                    ELSE 5 
                END,
                p.program_name
            """,
            (school_id,),
        ).fetchall()

        if programs:
            return [dict(p) for p in programs]'''

new_get_programs = '''@app.get("/schools/{school_id}/programs")
def get_school_programs(school_id: str):
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, category, school_type FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()

        if school is None:
            raise HTTPException(404, "School not found")

        sql = """
            SELECT p.program_id, p.institution_id as school_id, p.education_level,
                   p.program_name, p.degree_type, p.discipline_or_stream,
                   p.combination_code, p.duration_years,
                   p.is_active,
                   COALESCE(SUM(ps.capacity), 0) as total_capacity,
                   COALESCE(SUM(ps.current_strength), 0) as total_strength,
                   COUNT(ps.section_id) as section_count
            FROM academic_programs p
            LEFT JOIN program_sections ps ON ps.program_id = p.program_id
            WHERE p.institution_id = ? AND p.is_active = 1
        """
        params = [school_id]
        
        # Category-specific filtering: PU colleges only offer higher_secondary
        cat = school["category"] or ""
        stype = school["school_type"] or ""
        if cat == "PU Colleges (11-12)" or "PU" in stype:
            sql += " AND p.education_level = 'higher_secondary'"
        elif cat == "Schools (K-10)" or stype == "School":
            sql += " AND p.education_level = 'school'"

        sql += """
            GROUP BY p.program_id
            ORDER BY 
                CASE p.education_level 
                    WHEN 'school' THEN 1 
                    WHEN 'higher_secondary' THEN 2 
                    WHEN 'diploma' THEN 3 
                    WHEN 'undergraduate' THEN 4 
                    ELSE 5 
                END,
                p.program_name
        """
        programs = conn.execute(sql, params).fetchall()

        if programs:
            return [dict(p) for p in programs]'''

assert old_get_programs in content, 'old_get_programs not found'
content = content.replace(old_get_programs, new_get_programs)

# 2. Update get_school_seat_availability
old_get_seat = '''@app.get("/schools/{school_id}/seat-availability")
def get_school_seat_availability(
    school_id: str,
    academic_year: Optional[str] = Query(default="2025-26"),
):
    """
    Computes real-time seat availability from program_sections:
    available_seats = MAX(0, capacity - current_strength).
    Zero duplicate structures or invented numbers.
    """
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, school_name, school_type FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found")

        sql = """
            SELECT ps.section_id, ps.program_id, p.program_name, p.education_level,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   ps.term_or_year, ps.semester, ps.section_name,
                   ps.capacity, ps.current_strength,
                   MAX(0, ps.capacity - ps.current_strength) AS available_seats
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE ps.institution_id = ?
        """
        params = [school_id]
        if academic_year and academic_year.lower() != 'all':
            sql += " AND ps.academic_year = ?"
            params.append(academic_year)

        sql += " ORDER BY p.education_level, ps.term_or_year, ps.section_name"
        rows = conn.execute(sql, params).fetchall()
        sections = [dict(r) for r in rows]

        total_capacity = sum(s["capacity"] for s in sections)
        total_enrolled = sum(s["current_strength"] for s in sections)
        total_available = sum(s["available_seats"] for s in sections)

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "school_type": school["school_type"],
            "academic_year": academic_year,
            "total_sanctioned_capacity": total_capacity,
            "total_current_strength": total_enrolled,
            "total_available_seats": total_available,
            "sections_count": len(sections),
            "seat_breakdown": sections,
        }'''

new_get_seat = '''@app.get("/schools/{school_id}/seat-availability")
def get_school_seat_availability(
    school_id: str,
    academic_year: Optional[str] = Query(default=None),
):
    """
    Computes real-time seat availability from program_sections:
    available_seats = MAX(0, capacity - current_strength).
    Zero duplicate structures or invented numbers.
    """
    conn = get_connection()
    try:
        school = conn.execute(
            "SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?",
            (school_id,),
        ).fetchone()
        if not school:
            raise HTTPException(404, "Institution not found")

        cat = school["category"] or ""
        stype = school["school_type"] or ""

        sql = """
            SELECT ps.section_id, ps.program_id, p.program_name, p.education_level,
                   p.degree_type, p.discipline_or_stream, p.combination_code,
                   ps.academic_year, ps.term_or_year, ps.semester, ps.section_name,
                   ps.capacity, ps.current_strength,
                   MAX(0, ps.capacity - ps.current_strength) AS available_seats
            FROM program_sections ps
            JOIN academic_programs p ON p.program_id = ps.program_id
            WHERE ps.institution_id = ?
        """
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
            sql += " AND p.education_level = 'school'"

        sql += " ORDER BY ps.term_or_year, ps.section_name, p.program_name"
        rows = conn.execute(sql, params).fetchall()
        sections = [dict(r) for r in rows]

        total_capacity = sum(s["capacity"] for s in sections)
        total_enrolled = sum(s["current_strength"] for s in sections)
        total_available = sum(s["available_seats"] for s in sections)

        return {
            "institution_id": school["school_id"],
            "institution_name": school["school_name"],
            "school_type": school["school_type"],
            "category": school["category"],
            "academic_year": academic_year or "2026-27",
            "total_sanctioned_capacity": total_capacity,
            "total_current_strength": total_enrolled,
            "total_available_seats": total_available,
            "sections_count": len(sections),
            "seat_breakdown": sections,
        }'''

assert old_get_seat in content, 'old_get_seat not found'
content = content.replace(old_get_seat, new_get_seat)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("backend/main.py successfully patched!")
