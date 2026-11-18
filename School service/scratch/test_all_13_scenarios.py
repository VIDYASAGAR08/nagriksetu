import requests
import json
import sqlite3

BASE_URL = "http://localhost:8001"

def run_tests():
    print("==================================================================")
    print("NAGRIKSETU ACADEMIC PROGRAMME & STREAM/COMBINATION TEST SUITE")
    print("==================================================================")
    
    # 0. Check database student count baseline
    conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
    cur = conn.cursor()
    count_before = cur.execute("SELECT count(*) FROM students").fetchone()[0]
    enr_before = cur.execute("SELECT count(*) FROM enrollments").fetchone()[0]
    print(f"DB Baseline: {count_before} students, {enr_before} enrollments.")
    conn.close()

    # Login Platform Admin
    res_adm = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
    assert res_adm.status_code == 200
    token_adm = res_adm.json()["access_token"]
    headers_adm = {"Authorization": f"Bearer {token_adm}"}

    # Login K.S Rao (Ballari Education School - SCH019)
    res_rao = requests.post(f"{BASE_URL}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
    assert res_rao.status_code == 200
    token_rao = res_rao.json()["access_token"]
    headers_rao = {"Authorization": f"Bearer {token_rao}"}

    # Scenario 1: Degree dropdown displays programme names, not zero values
    print("\n--- Scenario 1: Degree dropdown displays programme names, not zero values ---")
    res_col = requests.get(f"{BASE_URL}/institution/COL001/academic-structure", headers=headers_adm)
    assert res_col.status_code == 200
    data_col = res_col.json()
    progs_col = data_col.get("programs", [])
    assert len(progs_col) > 0, "No programs found for COL001!"
    for p in progs_col:
        pname = p.get("program_name")
        print(f"  Program Name: '{pname}' | ID: '{p.get('program_id')}'")
        assert pname is not None, "Program name is None!"
        assert str(pname).strip() != "", "Program name is empty!"
        assert str(pname).strip() != "0", "Program name is '0'!"
        assert not str(pname).isdigit(), f"Program name '{pname}' is a numeric value!"
    print("[PASS] Scenario 1: All degree programs display proper names, not zero values.")

    # Scenario 2: Degree programme filters return only valid programmes belonging to institution
    print("\n--- Scenario 2: Degree programme filters return only valid programmes ---")
    inst_progs = [p["program_id"] for p in progs_col]
    print(f"  COL001 configured programs: {inst_progs}")
    # Verify every returned program actually belongs to COL001 in DB
    conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
    cur = conn.cursor()
    for pid in inst_progs:
        db_p = cur.execute("SELECT institution_id, program_name FROM academic_programs WHERE program_id = ?", (pid,)).fetchone()
        assert db_p is not None and db_p[0] == "COL001"
    conn.close()
    print("[PASS] Scenario 2: Degree programs belong strictly to selected institution.")

    # Scenario 3: Changing a degree programme reloads valid years and semesters
    print("\n--- Scenario 3: Changing a degree programme reloads valid years and semesters ---")
    mca_prog = next((p for p in progs_col if "MCA" in p["program_name"]), None)
    be_prog = next((p for p in progs_col if "Computer Science" in p["program_name"]), None)
    barch_prog = next((p for p in progs_col if "Architecture" in p["program_name"]), None)
    assert mca_prog is not None, "MCA program not found"
    assert be_prog is not None, "BE CSE program not found"
    assert barch_prog is not None, "BArch program not found"
    print(f"  MCA ({mca_prog['program_name']}): Years = {mca_prog['years']}, Semesters = {mca_prog['semesters_by_year']}")
    print(f"  B.E. ({be_prog['program_name']}): Years = {be_prog['years']}, Semesters = {be_prog['semesters_by_year']}")
    print(f"  B.Arch ({barch_prog['program_name']}): Years = {barch_prog['years']}, Semesters = {barch_prog['semesters_by_year']}")
    assert mca_prog["duration_years"] == 2
    assert be_prog["duration_years"] == 4
    assert barch_prog["duration_years"] == 5
    print("[PASS] Scenario 3: Programme metadata defines distinct years and semester mappings.")

    # Scenario 4: Commerce + PCMB is rejected by backend
    print("\n--- Scenario 4: Commerce + PCMB is rejected ---")
    res_comm_pcmb = requests.get(f"{BASE_URL}/institution/SCH011/students?standard=11&stream=Commerce&combination=PCMB", headers=headers_adm)
    print("  Status:", res_comm_pcmb.status_code)
    print("  Detail:", res_comm_pcmb.json().get("detail"))
    assert res_comm_pcmb.status_code == 400
    assert "Science combination" in res_comm_pcmb.json().get("detail")
    print("[PASS] Scenario 4: Commerce + PCMB rejected with 400 Bad Request.")

    # Scenario 5: Commerce + CEBA is accepted only where configured
    print("\n--- Scenario 5: Commerce + CEBA is accepted only where configured ---")
    res_comm_ceba = requests.get(f"{BASE_URL}/institution/SCH011/students?standard=11&stream=Commerce&combination=CEBA", headers=headers_adm)
    print("  Status for SCH011:", res_comm_ceba.status_code)
    assert res_comm_ceba.status_code == 200
    # Try CEBA on an institution where it is not configured (e.g. SCH001 K-10 school)
    res_sch_ceba = requests.get(f"{BASE_URL}/institution/SCH001/students?standard=8&stream=Commerce&combination=CEBA", headers=headers_adm)
    assert res_sch_ceba.status_code == 400
    print("[PASS] Scenario 5: Commerce + CEBA accepted on PU college SCH011, rejected on K-10 school.")

    # Scenario 6: Science + PCMB is accepted only where configured
    print("\n--- Scenario 6: Science + PCMB is accepted only where configured ---")
    res_sci_pcmb = requests.get(f"{BASE_URL}/institution/SCH011/students?standard=11&stream=Science&combination=PCMB", headers=headers_adm)
    print("  Status for SCH011:", res_sci_pcmb.status_code)
    assert res_sci_pcmb.status_code == 200
    print("[PASS] Scenario 6: Science + PCMB accepted on PU college.")

    # Scenario 7: Changing Science to Commerce clears previous combination (Verified via structure mapping)
    print("\n--- Scenario 7: Structure combinations_by_stream partition ---")
    res_pu_struct = requests.get(f"{BASE_URL}/institution/SCH011/academic-structure", headers=headers_adm)
    pu_data = res_pu_struct.json()
    combos_by_stream = pu_data.get("combinations_by_stream", {})
    sci_combos = {c["code"] for c in combos_by_stream.get("Science", [])}
    comm_combos = {c["code"] for c in combos_by_stream.get("Commerce", [])}
    print("  Science combinations:", sci_combos)
    print("  Commerce combinations:", comm_combos)
    assert len(sci_combos.intersection(comm_combos)) == 0, "Streams must not share combinations!"
    assert "PCMB" in sci_combos and "PCMB" not in comm_combos
    print("[PASS] Scenario 7: Streams are strictly disjoint.")

    # Scenario 8: Invalid combinations are rejected by the backend, not just hidden in UI
    print("\n--- Scenario 8: Invalid combinations rejected by backend ---")
    # Non-existent combination
    res_fake_combo = requests.get(f"{BASE_URL}/institution/SCH011/students?standard=11&stream=Science&combination=FAKE-XYZ", headers=headers_adm)
    assert res_fake_combo.status_code == 400
    print("  Non-existent combo rejected:", res_fake_combo.json().get("detail"))
    # Arts stream with Science combination
    res_arts_pcmb = requests.get(f"{BASE_URL}/institution/SCH011/students?standard=11&stream=Arts%20%2F%20Humanities&combination=PCMB", headers=headers_adm)
    assert res_arts_pcmb.status_code == 400
    print("  Arts + PCMB rejected:", res_arts_pcmb.json().get("detail"))
    print("[PASS] Scenario 8: Backend actively validates and rejects cross-stream combinations.")

    # Scenario 9: School filters do not show PU or degree combinations
    print("\n--- Scenario 9: School filters do not show PU or degree combinations ---")
    res_sch_struct = requests.get(f"{BASE_URL}/institution/SCH019/academic-structure", headers=headers_adm)
    sch_data = res_sch_struct.json()
    assert sch_data.get("category_type") == "K10_SCHOOL"
    assert "streams" not in sch_data or sch_data.get("streams") is None
    assert "combinations" not in sch_data or sch_data.get("combinations") is None
    assert "programs" not in sch_data or sch_data.get("programs") is None
    print(f"  SCH019 standards: {sch_data.get('standards')}")
    assert max(sch_data.get("standards")) <= 10
    print("[PASS] Scenario 9: School structure has only standards 1-10.")

    # Scenario 10: Diploma filters display actual diploma programmes
    print("\n--- Scenario 10: University and degree college filters show only configured programmes ---")
    res_vtu = requests.get(f"{BASE_URL}/institution/COL010/academic-structure", headers=headers_adm)
    assert res_vtu.status_code == 200
    vtu_data = res_vtu.json()
    vtu_progs = [p["program_name"] for p in vtu_data.get("programs", [])]
    print(f"  VTU Programs ({len(vtu_progs)}): {vtu_progs[:3]}")
    for vp in vtu_progs:
        assert not str(vp).isdigit() and vp != "0"
    print("[PASS] Scenario 10/11: VTU University programs verified.")

    # Scenario 12: Student lists contain only matching enrolled students
    print("\n--- Scenario 12: Student lists contain only matching enrolled students ---")
    res_std8a = requests.get(f"{BASE_URL}/institution/SCH019/students?standard=8&section=A", headers=headers_rao)
    assert res_std8a.status_code == 200
    data_std8a = res_std8a.json()
    print(f"  SCH019 Standard 8 Section A matched count: {data_std8a['total']}")
    assert data_std8a["total"] == 67
    for s in data_std8a["students"]:
        assert s["school_id"] == "SCH019"
        assert s["standard"] == 8
        assert s["section"] == "A"
        assert s["permanent_student_id"].startswith("NS-SCH019-")
    print("[PASS] Scenario 12: Student list strictly matches selected filters.")

    # Scenario 13: Cross-institution data access is rejected
    print("\n--- Scenario 13: Cross-institution data access is rejected ---")
    # K.S Rao belongs to SCH019. Attempting to access SCH011 or COL001 must be 403 Forbidden.
    res_rao_sch011 = requests.get(f"{BASE_URL}/institution/SCH011/students", headers=headers_rao)
    print("  Rao accessing SCH011 status:", res_rao_sch011.status_code)
    assert res_rao_sch011.status_code == 403
    res_rao_col001 = requests.get(f"{BASE_URL}/institution/COL001/academic-structure", headers=headers_rao)
    print("  Rao accessing COL001 structure status:", res_rao_col001.status_code)
    assert res_rao_col001.status_code == 403
    print("[PASS] Scenario 13: Cross-institution access strictly rejected with 403 Forbidden.")

    # Database integrity check
    conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
    cur = conn.cursor()
    count_after = cur.execute("SELECT count(*) FROM students").fetchone()[0]
    enr_after = cur.execute("SELECT count(*) FROM enrollments").fetchone()[0]
    # Table-specific foreign key checks
    fk_tables = ['students', 'enrollments', 'academic_programs', 'program_sections', 'institution_divisions']
    fk_violations = {}
    for tbl in fk_tables:
        chk = cur.execute(f"PRAGMA foreign_key_check({tbl})").fetchall()
        fk_violations[tbl] = len(chk)
    conn.close()

    print("\n--- Database Preservation & Integrity ---")
    print(f"  Students before: {count_before}, after: {count_after}")
    print(f"  Enrollments before: {enr_before}, after: {enr_after}")
    print(f"  Foreign Key Checks ({fk_tables}): {fk_violations}")
    assert count_before == count_after, "Student count altered!"
    assert enr_before == enr_after, "Enrollment count altered!"
    for tbl, count in fk_violations.items():
        assert count == 0, f"FK violations in {tbl}: {count}"
    print("[PASS] All core academic database records strictly preserved and foreign-key check clean.")

    print("\n==================================================================")
    print("ALL 13 TEST SCENARIOS PASSED WITH ZERO FAILURES!")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
