import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def test_structure(inst_id):
    school = cur.execute("SELECT school_id, school_name, school_type, category FROM schools WHERE school_id = ?", (inst_id,)).fetchone()
    if not school:
        return {"error": "Not found"}

    cat = (school["category"] or school["school_type"] or "").lower()
    is_school = "school" in cat and "pu" not in cat
    is_pu = "pu" in cat or "pre-university" in cat
    is_diploma = "diploma" in cat or "polytechnic" in cat
    is_degree = not is_school and not is_pu and not is_diploma

    print(f"=== {inst_id} ({school['school_name']}) ===")
    print(f"  Category: {school['category']}, is_pu: {is_pu}, is_degree: {is_degree}")

    if is_degree:
        # 1. Divisions
        div_rows = cur.execute("SELECT division_id, division_name, division_type FROM institution_divisions WHERE parent_institution_id = ? ORDER BY display_order, division_name", (inst_id,)).fetchall()
        divisions = [dict(d) for d in div_rows]

        # 2. Programs
        prog_rows = cur.execute("""
            SELECT program_id, program_name, degree_type, discipline_or_stream, combination_code,
                   faculty_name, department_name, duration_years
            FROM academic_programs
            WHERE institution_id = ? AND is_active = 1
            ORDER BY program_name
        """, (inst_id,)).fetchall()

        programs = []
        for p in prog_rows:
            p_dict = dict(p)
            pid = p["program_id"]
            dur = p["duration_years"] or 4
            
            # Map division_id if matches faculty_name
            matching_div = next((d["division_id"] for d in divisions if d["division_name"].lower() == (p["faculty_name"] or "").lower()), None)
            p_dict["division_id"] = matching_div

            # Fetch sections from program_sections
            sec_rows = cur.execute("""
                SELECT section_id, academic_year, term_or_year, semester, section_name
                FROM program_sections
                WHERE institution_id = ? AND program_id = ?
                ORDER BY term_or_year, semester, section_name
            """, (inst_id, pid)).fetchall()

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

        print(f"  Divisions ({len(divisions)}): {[d['division_name'] for d in divisions]}")
        print(f"  Programs ({len(programs)}):")
        for p in programs[:3]:
            print(f"    - {p['program_name']} ({p['degree_type']}) | Div: {p['division_id']} | Years: {p['years']} | Secs: {p['sections']}")

    elif is_pu:
        streams_rows = cur.execute("""
            SELECT DISTINCT discipline_or_stream
            FROM academic_programs
            WHERE institution_id = ? AND is_active = 1
            ORDER BY discipline_or_stream
        """, (inst_id,)).fetchall()
        streams = [r["discipline_or_stream"] for r in streams_rows if r["discipline_or_stream"]]
        if not streams:
            streams = ["Science", "Commerce", "Arts / Humanities"]

        combinations_by_stream = {}
        for st in streams:
            combo_rows = cur.execute("""
                SELECT program_id, program_name, combination_code, discipline_or_stream
                FROM academic_programs
                WHERE institution_id = ? AND discipline_or_stream = ? AND is_active = 1
                ORDER BY combination_code, program_name
            """, (inst_id, st)).fetchall()
            combos = []
            for c in combo_rows:
                code = c["combination_code"] or c["program_name"][:4]
                # Check sections for this combination
                sec_rows = cur.execute("""
                    SELECT DISTINCT term_or_year, section_name
                    FROM program_sections
                    WHERE institution_id = ? AND program_id = ?
                    ORDER BY term_or_year, section_name
                """, (inst_id, c["program_id"])).fetchall()
                sections_by_level = {"11": [], "12": []}
                for s in sec_rows:
                    if str(s["term_or_year"]) in sections_by_level:
                        sections_by_level[str(s["term_or_year"])].append(s["section_name"])
                if not sections_by_level["11"]:
                    sections_by_level["11"] = ["A", "B"]
                if not sections_by_level["12"]:
                    sections_by_level["12"] = ["A", "B"]

                combos.append({
                    "program_id": c["program_id"],
                    "code": code,
                    "name": c["program_name"],
                    "stream": st,
                    "sections_by_level": sections_by_level
                })
            combinations_by_stream[st] = combos

        print(f"  Streams ({len(streams)}): {streams}")
        for st, clist in combinations_by_stream.items():
            print(f"    {st}: {[c['code'] for c in clist]}")

print("Testing COL001 (Degree College):")
test_structure("COL001")
print("\nTesting COL004 (University):")
test_structure("COL004")
print("\nTesting SCH011 (PU College):")
test_structure("SCH011")
print("\nTesting SCH019 (School):")
test_structure("SCH019")

conn.close()
