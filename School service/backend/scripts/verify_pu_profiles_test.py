import requests
import sqlite3
import sys

BASE_URL = "http://localhost:8001"
DB_PATH = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"

def main():
    print("=" * 70)
    print("NAGRIKSETU — PU COLLEGES ACADEMIC STRUCTURE VERIFICATION AUDIT")
    print("=" * 70)

    pu_colleges = [
        ("SCH011", "Tumakuru Model Pre-University College"),
        ("SCH012", "Mysuru Government Pre-University College"),
        ("SCH013", "Mandya Government Pre-University College"),
        ("SCH014", "Hassan Valley Pre-University College"),
        ("SCH015", "Udupi Government Pre-University College"),
    ]

    expected_combinations = {"PCMB", "PCMC", "PCME", "CEBA", "SEBA", "EBAC", "HEPS", "VOC-IT", "HEBA", "MEBA"}

    for inst_id, inst_name in pu_colleges:
        print(f"\n[AUDITING {inst_id}] {inst_name}...")
        
        # 1. School Profile
        r_inst = requests.get(f"{BASE_URL}/schools/{inst_id}")
        assert r_inst.status_code == 200, f"Failed GET /schools/{inst_id}"
        d_inst = r_inst.json()
        assert d_inst.get("category") == "PU Colleges (11-12)", f"Category mismatch: {d_inst.get('category')}"
        assert d_inst.get("school_type") == "PU College", f"Type mismatch: {d_inst.get('school_type')}"
        seat_summary = d_inst.get("seat_summary", {})
        print(f"  -> Profile seat summary: Cap={seat_summary.get('sanctioned_capacity')}, Enr={seat_summary.get('current_strength')}, Avail={seat_summary.get('available_seats')}")
        assert seat_summary.get("sanctioned_capacity") == 1092, f"Expected 1092, got {seat_summary.get('sanctioned_capacity')}"
        assert seat_summary.get("current_strength") == 892, f"Expected 892, got {seat_summary.get('current_strength')}"
        assert seat_summary.get("available_seats") == 200, f"Expected 200, got {seat_summary.get('available_seats')}"

        # 2. Programs
        r_progs = requests.get(f"{BASE_URL}/schools/{inst_id}/programs")
        assert r_progs.status_code == 200, f"Failed GET /schools/{inst_id}/programs"
        progs = r_progs.json()
        print(f"  -> Programs count: {len(progs)} (Expected 10)")
        assert len(progs) == 10, f"Expected 10 programs, got {len(progs)}"
        
        combinations = set()
        for p in progs:
            assert p["education_level"] == "higher_secondary", f"Invalid education_level: {p['education_level']}"
            assert "Std 1-10" not in p["program_name"], f"School program leaked: {p['program_name']}"
            assert "School Education" not in p["program_name"], f"School program leaked: {p['program_name']}"
            combinations.add(p["combination_code"])
        assert combinations == expected_combinations, f"Combinations mismatch: {combinations}"
        print(f"  -> Combinations verified: {sorted(list(combinations))}")

        # 3. Live Seat Availability & Sections
        r_seats = requests.get(f"{BASE_URL}/schools/{inst_id}/seat-availability")
        assert r_seats.status_code == 200, f"Failed GET /schools/{inst_id}/seat-availability"
        d_seats = r_seats.json()
        print(f"  -> Live seat availability: Cap={d_seats.get('total_sanctioned_capacity')}, Enr={d_seats.get('total_current_strength')}, Avail={d_seats.get('total_available_seats')}, Secs={d_seats.get('sections_count')}")
        assert d_seats.get("total_sanctioned_capacity") == 1092
        assert d_seats.get("total_current_strength") == 892
        assert d_seats.get("total_available_seats") == 200
        assert d_seats.get("sections_count") == 20

        sections = d_seats.get("seat_breakdown", [])
        terms = set()
        for s in sections:
            assert s["term_or_year"] in [11, 12], f"Invalid term_or_year for PU: {s['term_or_year']}"
            assert s["combination_code"] in expected_combinations, f"Invalid combination: {s['combination_code']}"
            terms.add(s["term_or_year"])
        assert terms == {11, 12}, f"Terms mismatch: {terms}"
        print(f"  -> Sections verified: 20 sections across 1st PUC (11) and 2nd PUC (12).")
        print(f"  [OK] {inst_id} passed all category-specific academic checks.")

    # 4. Check other tiers
    print("\n[VERIFYING OTHER CATEGORIES REMAIN INTACT]")
    for other_id, exp_cat in [("SCH001", "Schools (K-10)"), ("COL001", "Degree Colleges"), ("COL010", "Universities")]:
        r = requests.get(f"{BASE_URL}/schools/{other_id}/seat-availability")
        d = r.json()
        assert r.status_code == 200
        print(f"  {other_id} ({exp_cat}): Cap={d.get('total_sanctioned_capacity')}, Avail={d.get('total_available_seats')}, Secs={d.get('sections_count')}")

    # 5. Database baseline check
    print("\n[DATABASE BASELINE INTEGRITY CHECKS]")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check")
    assert cur.fetchone()[0] == "ok"
    cur.execute("PRAGMA foreign_key_check")
    assert len(cur.fetchall()) == 0
    cur.execute("SELECT count(*) FROM schools")
    assert cur.fetchone()[0] == 30
    cur.execute("SELECT count(*) FROM students")
    assert cur.fetchone()[0] == 30001
    cur.execute("SELECT count(*) FROM enrollments")
    assert cur.fetchone()[0] == 30001
    conn.close()
    print("  [OK] Database baseline: 30 schools, 30,001 students, 30,001 enrollments intact.")

    print("\n" + "=" * 70)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
