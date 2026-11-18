import sqlite3
import urllib.request
import json
import sys

def verify():
    print("=====================================================================")
    print("      NAGRIKSETU HIGHER EDUCATION ACADEMIC STRUCTURE AUDIT           ")
    print("=====================================================================")

    # 1. Database level checks
    conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Integrity & FK checks
    integrity = c.execute("PRAGMA integrity_check").fetchone()[0]
    assert integrity == "ok", f"Integrity check failed: {integrity}"
    print("[OK] Database PRAGMA integrity_check == 'ok'")

    fk_violations = c.execute("PRAGMA foreign_key_check").fetchall()
    assert len(fk_violations) == 0, f"FK violations: {fk_violations}"
    print("[OK] Database PRAGMA foreign_key_check == 0 violations")

    # Counts
    students = c.execute("SELECT count(*) as count FROM students").fetchone()["count"]
    enrollments = c.execute("SELECT count(*) as count FROM enrollments").fetchone()["count"]
    assert students == 30001, f"Students count mismatch: {students}"
    assert enrollments == 30001, f"Enrollments count mismatch: {enrollments}"
    print(f"[OK] Students count: {students} | Enrollments count: {enrollments}")

    schools_count = c.execute("SELECT count(*) as count FROM schools").fetchone()["count"]
    assert schools_count == 30, f"Total institutions mismatch: {schools_count}"
    print(f"[OK] Total institutions count: {schools_count}")

    cat_counts = dict(c.execute("SELECT category, count(*) FROM schools GROUP BY category").fetchall())
    print("  Distribution by category:", cat_counts)
    assert cat_counts.get("Schools (K-10)") == 15, "Schools count != 15"
    assert cat_counts.get("PU Colleges (11-12)") == 5, "PU count != 5"
    assert cat_counts.get("Degree Colleges") == 5, "Degree Colleges count != 5"
    assert cat_counts.get("Universities") == 5, "Universities count != 5"
    print("[OK] Exact 15 Schools, 5 PU Colleges, 5 Degree Colleges, 5 Universities verified!")

    # Check that no diploma programs remain active in Degree Colleges or Universities
    dip_col = c.execute("""
        SELECT count(*) as count FROM academic_programs
        WHERE institution_id LIKE 'COL%' AND (education_level = 'diploma' OR program_id LIKE '%DIP%')
    """).fetchone()["count"]
    assert dip_col == 0, f"Found {dip_col} diploma programs in COL*"
    print("[OK] Zero diploma/polytechnic programs in Degree Colleges and Universities")

    # 2. Test All 5 Degree Colleges
    print("\n------------------- VERIFYING 5 DEGREE COLLEGES -------------------")
    expected_colleges = [
        ("COL001", "Ramaiah Institute of Technology (MSRIT)", "Visvesvaraya Technological University (VTU), Belagavi"),
        ("COL002", "R.V. College of Engineering (RVCE)", "Visvesvaraya Technological University (VTU), Belagavi"),
        ("COL003", "BMS College of Engineering (BMSCE)", "Visvesvaraya Technological University (VTU), Belagavi"),
        ("COL005", "The National Institute of Engineering (NIE)", "Visvesvaraya Technological University (VTU), Belagavi"),
        ("COL007", "Mount Carmel College (Autonomous)", "Bengaluru City University"),
    ]

    for cid, cname, expected_affil in expected_colleges:
        # Check DB record
        s = c.execute("SELECT * FROM schools WHERE school_id = ?", (cid,)).fetchone()
        assert s is not None, f"College {cid} not found"
        assert s["category"] == "Degree Colleges", f"{cid} category is {s['category']}"
        assert s["school_type"] == "Degree College", f"{cid} school_type is {s['school_type']}"
        assert expected_affil in s["affiliation"], f"{cid} affiliation mismatch: {s['affiliation']}"

        # Check API endpoint for programs
        url_prog = f"http://localhost:8001/schools/{cid}/programs"
        req = urllib.request.urlopen(url_prog)
        progs = json.loads(req.read().decode())
        assert len(progs) >= 4, f"{cid} has fewer than 4 programs: {len(progs)}"

        # Check API endpoint for seat availability
        url_seat = f"http://localhost:8001/schools/{cid}/seat-availability"
        req_seat = urllib.request.urlopen(url_seat)
        seats = json.loads(req_seat.read().decode())
        assert seats["total_sanctioned_capacity"] > 0, f"{cid} total capacity is 0"
        assert seats["total_available_seats"] > 0, f"{cid} available seats is 0"
        assert seats["sections_count"] > 0, f"{cid} sections_count is 0"

        # Check API academic hierarchy endpoint
        url_hier = f"http://localhost:8001/schools/{cid}/academic-hierarchy"
        req_hier = urllib.request.urlopen(url_hier)
        hier = json.loads(req_hier.read().decode())
        assert hier["is_degree_college"] is True, f"{cid} is_degree_college is False"
        assert hier["is_university"] is False, f"{cid} is_university is True"
        assert hier["affiliation"] == s["affiliation"]

        print(f"[OK] {cid}: {s['school_name']}")
        print(f"     Affiliation: {s['affiliation']}")
        print(f"     Degree Courses: {len(progs)} | Sections: {seats['sections_count']} | Cap: {seats['total_sanctioned_capacity']} | Enrolled: {seats['total_current_strength']} | Available: {seats['total_available_seats']}")

    # 3. Test All 5 Universities
    print("\n-------------------- VERIFYING 5 UNIVERSITIES ---------------------")
    expected_universities = [
        ("COL004", "PES University (Ring Road Campus)", "PES University Act, State Private University (UGC Recognized)"),
        ("COL006", "St. Joseph's University", "St. Joseph's University Act, Jesuit Higher Education Institution (UGC Recognized)"),
        ("COL008", "KLE Technological University (BVBCET)", "KLE Technological University Act, State Private University (UGC Recognized)"),
        ("COL009", "University of Mysore (Manasagangotri)", "Public State University (Established 1916, UGC Act 12B Recognized)"),
        ("COL010", "Visvesvaraya Technological University (VTU)", "State Apex Technological University (Affiliates 200+ Engineering Colleges across Karnataka)"),
    ]

    for uid, uname, expected_affil in expected_universities:
        s = c.execute("SELECT * FROM schools WHERE school_id = ?", (uid,)).fetchone()
        assert s is not None, f"University {uid} not found"
        assert s["category"] == "Universities", f"{uid} category is {s['category']}"
        assert s["school_type"] == "University", f"{uid} school_type is {s['school_type']}"

        # Check API academic hierarchy
        url_hier = f"http://localhost:8001/schools/{uid}/academic-hierarchy"
        req_hier = urllib.request.urlopen(url_hier)
        hier = json.loads(req_hier.read().decode())
        assert hier["is_university"] is True, f"{uid} is_university is False"
        assert hier["is_degree_college"] is False, f"{uid} is_degree_college is True"

        faculties = hier["faculties"]
        assert len(faculties) >= 3, f"{uid} faculties count {len(faculties)} < 3"

        # Check that UG, PG, Doctoral levels exist in hierarchy
        all_levels = set()
        total_departments = 0
        total_progs = 0
        for f in faculties:
            for d in f["departments"]:
                total_departments += 1
                for p in d["programmes"]:
                    total_progs += 1
                    all_levels.add(p["education_level"])

        assert "undergraduate" in all_levels, f"{uid} missing undergraduate level"
        assert "postgraduate" in all_levels, f"{uid} missing postgraduate level"
        assert "doctoral" in all_levels, f"{uid} missing doctoral level"

        # Check API seat availability
        url_seat = f"http://localhost:8001/schools/{uid}/seat-availability"
        req_seat = urllib.request.urlopen(url_seat)
        seats = json.loads(req_seat.read().decode())
        assert seats["total_sanctioned_capacity"] > 0
        assert seats["total_available_seats"] > 0

        print(f"[OK] {uid}: {s['school_name']}")
        print(f"     Statutory Recognition: {s['recognition']}")
        print(f"     Faculties: {len(faculties)} | Departments: {total_departments} | Programmes: {total_progs}")
        print(f"     Academic Levels: {sorted(list(all_levels))}")
        print(f"     Sections: {seats['sections_count']} | Cap: {seats['total_sanctioned_capacity']} | Enrolled: {seats['total_current_strength']} | Available: {seats['total_available_seats']}")

    conn.close()
    print("\n=====================================================================")
    print("      ALL AUDITS PASSED WITH ZERO VIOLATIONS AND COMPLETE INTEGRITY   ")
    print("=====================================================================")

if __name__ == "__main__":
    verify()
