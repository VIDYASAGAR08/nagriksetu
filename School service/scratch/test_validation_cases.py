import sqlite3

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def validate_and_query_students(institution_id, standard=None, section=None, stream=None, combination=None, program_id=None, division_id=None, year=None, semester=None):
    inst_id = institution_id.strip()
    school = cur.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
    if not school:
        raise ValueError(f"Institution '{inst_id}' not found.")

    cat = (school["category"] or school["school_type"] or "").lower()
    is_school = "school" in cat and "pu" not in cat
    is_pu = "pu" in cat or "pre-university" in cat
    is_diploma = "diploma" in cat or "polytechnic" in cat
    is_degree = not is_school and not is_pu and not is_diploma

    # 1. School (K-10) Validation
    if is_school:
        if stream or combination or program_id or division_id or semester:
            raise ValueError("Stream, combination, and degree programme filters are not applicable to School Education (K-10).")
        if standard is not None and (standard < 1 or standard > 10):
            raise ValueError(f"Standard '{standard}' is invalid for School Education (must be between 1 and 10).")

    # 2. PU College Validation
    elif is_pu:
        if program_id or division_id or semester:
            raise ValueError("Degree programme, division, and semester filters are not applicable to PU Colleges.")
        if standard is not None and standard not in (11, 12):
            raise ValueError(f"Standard '{standard}' is invalid for PU Colleges (must be 11 for 1st PU or 12 for 2nd PU).")

        pu_progs = cur.execute("""
            SELECT program_id, discipline_or_stream, combination_code, program_name
            FROM academic_programs
            WHERE institution_id = ? AND is_active = 1
        """, (inst_id,)).fetchall()

        valid_streams = {p["discipline_or_stream"] for p in pu_progs if p["discipline_or_stream"]}
        valid_combos = {p["combination_code"] for p in pu_progs if p["combination_code"]}
        stream_combos = {}
        for p in pu_progs:
            st = p["discipline_or_stream"]
            cb = p["combination_code"]
            if st and cb:
                stream_combos.setdefault(st, set()).add(cb)

        if stream:
            if stream not in valid_streams:
                raise ValueError(f"Stream '{stream}' is not offered by institution '{inst_id}'. Offered streams: {sorted(list(valid_streams))}")

        if combination:
            if combination not in valid_combos:
                raise ValueError(f"Subject combination '{combination}' is not configured for institution '{inst_id}'.")
            if stream:
                allowed_for_stream = stream_combos.get(stream, set())
                if combination not in allowed_for_stream:
                    actual_stream = next((st for st, cbs in stream_combos.items() if combination in cbs), "another stream")
                    raise ValueError(f"Validation error: Subject combination '{combination}' is a {actual_stream} combination and cannot be selected under '{stream}' for {school['school_name']}.")

    # 3. Degree College / University Validation
    elif is_degree:
        if standard is not None and standard > 5:
            # Degree uses year 1-4/5, not high school standards
            pass

        deg_progs = cur.execute("""
            SELECT program_id, program_name, degree_type, discipline_or_stream, duration_years, faculty_name
            FROM academic_programs
            WHERE institution_id = ? AND is_active = 1
        """, (inst_id,)).fetchall()

        prog_ids = {p["program_id"] for p in deg_progs}
        if program_id:
            if program_id not in prog_ids:
                raise ValueError(f"Programme '{program_id}' is not offered by institution '{inst_id}'.")

    return "VALID"

print("--- Testing Validation Cases ---")
# Case 1: Commerce + PCMB on SCH011 -> must raise ValueError
try:
    validate_and_query_students("SCH011", standard=11, stream="Commerce", combination="PCMB")
    print("FAILED: Commerce + PCMB was NOT rejected!")
except ValueError as e:
    print("SUCCESS: Commerce + PCMB rejected with:", e)

# Case 2: Commerce + CEBA on SCH011 -> must pass
try:
    res = validate_and_query_students("SCH011", standard=11, stream="Commerce", combination="CEBA")
    print("SUCCESS: Commerce + CEBA accepted:", res)
except ValueError as e:
    print("FAILED: Commerce + CEBA rejected with:", e)

# Case 3: Science + PCMB on SCH011 -> must pass
try:
    res = validate_and_query_students("SCH011", standard=11, stream="Science", combination="PCMB")
    print("SUCCESS: Science + PCMB accepted:", res)
except ValueError as e:
    print("FAILED: Science + PCMB rejected with:", e)

# Case 4: K-10 School with stream filter -> must raise ValueError
try:
    validate_and_query_students("SCH019", standard=8, stream="Science")
    print("FAILED: SCH019 with stream was NOT rejected!")
except ValueError as e:
    print("SUCCESS: SCH019 with stream rejected with:", e)

# Case 5: Degree College COL001 with valid program -> must pass
try:
    res = validate_and_query_students("COL001", program_id="PROG-COL001-UG-01")
    print("SUCCESS: COL001 with PROG-COL001-UG-01 accepted:", res)
except ValueError as e:
    print("FAILED: COL001 rejected with:", e)

# Case 6: Degree College COL001 with fake program -> must raise ValueError
try:
    validate_and_query_students("COL001", program_id="PROG-FAKE-999")
    print("FAILED: COL001 with fake program was NOT rejected!")
except ValueError as e:
    print("SUCCESS: COL001 fake program rejected with:", e)

conn.close()
