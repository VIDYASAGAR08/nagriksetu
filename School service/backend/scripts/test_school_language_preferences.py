import urllib.request
import urllib.error
import json
import sqlite3

def run_tests():
    print("=====================================================================")
    print("      NAGRIKSETU SCHOOL LANGUAGE PREFERENCE COMPREHENSIVE AUDIT     ")
    print("=====================================================================")

    school_ids = [f"SCH{i:03d}" for i in range(1, 11)] + [f"SCH{i:03d}" for i in range(16, 21)]

    # 1. Audit form config for all 15 schools
    print(f"\n[*] Auditing Language Configuration for all 15 Schools: {school_ids}")
    for sid in school_ids:
        url = f"http://localhost:8001/admissions/form-config/{sid}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode())
        
        cfg = data.get("school_config", {})
        first_langs = cfg.get("first_languages")
        second_langs = cfg.get("second_languages")

        assert first_langs == ["Kannada", "Hindi", "Sanskrit"], f"{sid} invalid first_languages: {first_langs}"
        assert "English" not in first_langs, f"{sid} English should not be in first_languages!"
        assert second_langs == ["English"], f"{sid} invalid second_languages: {second_langs}"

        print(f"  [OK] {sid}: 1st: {first_langs} | 2nd: {second_langs}")

    # 2. Test submitting all 3 allowed first languages
    print("\n[*] Testing Valid First Language Options on SCH001:")
    allowed = ["Kannada", "Hindi", "Sanskrit"]
    for lang in allowed:
        payload = {
            "institution_id": "SCH001",
            "division_id": None,
            "applicant_name": f"Test Student {lang}",
            "parent_name": f"Parent of {lang}",
            "parent_phone": "9876543210",
            "parent_email": f"parent.{lang.lower()}@example.com",
            "residential_address": "7th Cross, Malleshwaram, Bengaluru",
            "academic_year": "2026-2027",
            "education_level": "school",
            "requested_standard": 1,
            "first_language_preference": lang,
            "second_language_preference": "English"
        }
        req = urllib.request.Request(
            "http://localhost:8001/admissions/apply",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req)
        res_data = json.loads(res.read().decode())
        print(f"  [OK] First Language '{lang}' ACCEPTED -> Application ID: {res_data['application_id']}")

    # 3. Test Backend Validation: Reject invalid first language (e.g. English, French)
    print("\n[*] Testing Backend Validation: Rejecting Invalid First Language Preferences:")
    invalid_langs = ["English", "French", "Telugu"]
    for inv in invalid_langs:
        payload = {
            "institution_id": "SCH001",
            "division_id": None,
            "applicant_name": f"Invalid {inv}",
            "parent_name": "Test Parent",
            "parent_phone": "9876543210",
            "residential_address": "Test Address, Bengaluru",
            "academic_year": "2026-2027",
            "education_level": "school",
            "requested_standard": 2,
            "first_language_preference": inv,
            "second_language_preference": "English"
        }
        try:
            req = urllib.request.Request(
                "http://localhost:8001/admissions/apply",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req)
            assert False, f"Server should have rejected first language '{inv}'"
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode())["detail"]
            print(f"  [OK] First Language '{inv}' correctly REJECTED with HTTP {e.code}: '{err}'")
            assert e.code == 400

    # 4. Test Backend Enforcement: Never trust frontend-submitted second language
    print("\n[*] Testing Backend Enforcement: Never trusting frontend second language (auto-assigning English):")
    spoofed_payload = {
        "institution_id": "SCH002",
        "division_id": None,
        "applicant_name": "Spoof Second Language Test",
        "parent_name": "Spoof Parent",
        "parent_phone": "9876543210",
        "residential_address": "Test Street, Bengaluru",
        "academic_year": "2026-2027",
        "education_level": "school",
        "requested_standard": 3,
        "first_language_preference": "Kannada",
        "second_language_preference": "Hindi"  # Attempt to spoof Hindi as second language
    }
    req = urllib.request.Request(
        "http://localhost:8001/admissions/apply",
        data=json.dumps(spoofed_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    res_data = json.loads(res.read().decode())
    app_id = res_data["application_id"]

    # Verify actual stored record in database
    conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
    c = conn.cursor()
    row = c.execute("SELECT first_language_preference, second_language_preference FROM admission_applications WHERE application_id = ?", (app_id,)).fetchone()
    stored_first, stored_second = row[0], row[1]
    conn.close()

    assert stored_first == "Kannada", f"Stored first language mismatch: {stored_first}"
    assert stored_second == "English", f"Stored second language should be English, but got: {stored_second}"
    print(f"  [OK] Client sent second_language='Hindi' -> Server forced stored second_language='{stored_second}' (English)!")

    # 5. Database integrity and counts
    conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
    c = conn.cursor()
    assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert len(c.execute("PRAGMA foreign_key_check").fetchall()) == 0
    students = c.execute("SELECT count(*) FROM students").fetchone()[0]
    enrollments = c.execute("SELECT count(*) FROM enrollments").fetchone()[0]
    schools = c.execute("SELECT count(*) FROM schools").fetchone()[0]
    conn.close()

    assert students == 30001
    assert enrollments == 30001
    assert schools == 30
    print(f"\n[OK] Integrity verified: 30,001 students, 30,001 enrollments, 30 total institutions intact.")

    print("\n=====================================================================")
    print("      ALL TESTS PASSED WITH 100% SUCCESS                             ")
    print("=====================================================================")

if __name__ == "__main__":
    run_tests()
