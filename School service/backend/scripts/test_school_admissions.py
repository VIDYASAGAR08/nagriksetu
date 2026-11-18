import urllib.request
import urllib.error
import json
import sqlite3

def run_tests():
    print("=====================================================================")
    print("      NAGRIKSETU SCHOOL ADMISSION FORM COMPREHENSIVE AUDIT           ")
    print("=====================================================================")

    school_ids = [f"SCH{i:03d}" for i in range(1, 11)] + [f"SCH{i:03d}" for i in range(16, 21)]
    pu_ids = [f"SCH{i:03d}" for i in range(11, 16)]

    print(f"[*] Auditing all 15 schools: {school_ids}")
    for sid in school_ids:
        url = f"http://localhost:8001/admissions/form-config/{sid}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode())

        assert data["is_school"] is True, f"{sid} is_school is False"
        assert data["category"] == "Schools (K-10)", f"{sid} category is {data['category']}"
        assert data["offered_levels"] == ["school"], f"{sid} offered_levels: {data['offered_levels']}"
        assert data["pu_config"] is None, f"{sid} pu_config is NOT None"
        assert data["diploma_config"] is None, f"{sid} diploma_config is NOT None"
        assert data["undergraduate_config"] is None, f"{sid} undergraduate_config is NOT None"
        assert data["school_config"] is not None, f"{sid} school_config is None"
        assert data["school_config"]["standards"] == list(range(1, 11)), f"{sid} standards mismatch"

        print(f"  [OK] {sid}: {data['institution_name'][:28]:<28} | Levels: {data['offered_levels']} | PU config: None | Standards: 1-10")

    print("\n[*] Verifying PU Colleges retain separate PU admission process:")
    for pid in pu_ids:
        url = f"http://localhost:8001/admissions/form-config/{pid}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode())

        assert data["is_school"] is False, f"{pid} is_school is True"
        assert data["category"] == "PU Colleges (11-12)", f"{pid} category is {data['category']}"
        assert data["offered_levels"] == ["higher_secondary"], f"{pid} offered_levels: {data['offered_levels']}"
        assert data["pu_config"] is not None, f"{pid} pu_config is None"
        assert len(data["pu_config"]["combinations"]) > 0, f"{pid} combinations empty"

        print(f"  [OK] {pid}: {data['institution_name'][:28]:<28} | Levels: {data['offered_levels']} | PU Combinations: {len(data['pu_config']['combinations'])}")

    print("\n[*] Testing Valid School Admission Submission on SCH001:")
    valid_payload = {
        "institution_id": "SCH001",
        "division_id": None,
        "applicant_name": "Deepak Gowda",
        "parent_name": "Anand Gowda",
        "parent_phone": "9876543210",
        "parent_email": "anand.gowda@example.com",
        "residential_address": "45 Malleshwaram 7th Cross, Bengaluru",
        "academic_year": "2026-2027",
        "education_level": "school",
        "requested_standard": 1,
        "first_language_preference": "Kannada",
        "second_language_preference": "English"
    }

    req = urllib.request.Request(
        "http://localhost:8001/admissions/apply",
        data=json.dumps(valid_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    res_data = json.loads(res.read().decode())
    print(f"  [OK] Application accepted! ID: {res_data['application_id']}, Status: {res_data['status']}")

    print("\n[*] Testing Backend Validation: Rejecting PU application to a School (SCH001):")
    invalid_payload = {
        "institution_id": "SCH001",
        "division_id": None,
        "applicant_name": "Rohan Kumar",
        "parent_name": "Sunil Kumar",
        "parent_phone": "9876543210",
        "parent_email": "sunil.kumar@example.com",
        "residential_address": "12 Jayanagar, Bengaluru",
        "academic_year": "2026-2027",
        "education_level": "higher_secondary",
        "requested_standard": None,
        "stream_preference": "Science",
        "combination_code": "PCMB"
    }

    try:
        bad_req = urllib.request.Request(
            "http://localhost:8001/admissions/apply",
            data=json.dumps(invalid_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(bad_req)
        print("  [FAIL] Server unexpectedly accepted PU application for a School!")
        assert False, "Should have been rejected"
    except urllib.error.HTTPError as e:
        err_msg = json.loads(e.read().decode())["detail"]
        print(f"  [OK] Correctly rejected with HTTP {e.code}: '{err_msg}'")
        assert e.code == 400

    print("\n[*] Testing Backend Validation: Rejecting PU application to SCH016:")
    invalid_payload_sch016 = dict(invalid_payload, institution_id="SCH016")
    try:
        bad_req2 = urllib.request.Request(
            "http://localhost:8001/admissions/apply",
            data=json.dumps(invalid_payload_sch016).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(bad_req2)
        assert False, "Should have been rejected"
    except urllib.error.HTTPError as e:
        err_msg = json.loads(e.read().decode())["detail"]
        print(f"  [OK] Correctly rejected with HTTP {e.code}: '{err_msg}'")
        assert e.code == 400

    # Verify counts
    conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
    c = conn.cursor()
    students = c.execute("SELECT count(*) FROM students").fetchone()[0]
    enrollments = c.execute("SELECT count(*) FROM enrollments").fetchone()[0]
    schools = c.execute("SELECT count(*) FROM schools").fetchone()[0]
    conn.close()

    print(f"\n[OK] Integrity preserved: Students={students}, Enrollments={enrollments}, Total Institutions={schools}")
    assert students == 30001
    assert enrollments == 30001
    assert schools == 30

    print("\n=====================================================================")
    print("      ALL TESTS PASSED WITH 100% SUCCESS                             ")
    print("=====================================================================")

if __name__ == "__main__":
    run_tests()
