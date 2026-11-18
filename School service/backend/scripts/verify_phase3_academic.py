import subprocess
import html
import os
import shutil
import urllib.request
import json
import sqlite3

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
screenshot_dir = r"C:\Users\callm\nagriksetu\screenshots"
brain_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
os.makedirs(screenshot_dir, exist_ok=True)

print("=== 1. DATABASE RECORD PRESERVATION CHECK ===")
conn = sqlite3.connect(r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db")
c = conn.cursor()
st_cnt = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
enr_cnt = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
prog_cnt = c.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0]
sec_cnt = c.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0]
sch_cnt = c.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
div_cnt = c.execute("SELECT COUNT(*) FROM institution_divisions").fetchone()[0]
fk_errs = c.execute("PRAGMA foreign_key_check").fetchall()
int_check = c.execute("PRAGMA integrity_check").fetchone()[0]

print(f"  Students: {st_cnt} (Expected: 30000)")
print(f"  Enrollments: {enr_cnt} (Expected: 30000)")
print(f"  Academic Programs: {prog_cnt} (Expected: 198)")
print(f"  Program Sections: {sec_cnt} (Expected: 841)")
print(f"  Schools: {sch_cnt} (Expected: 30)")
print(f"  Divisions: {div_cnt} (Expected: 13)")
print(f"  Foreign Key Errors: {len(fk_errs)}")
print(f"  Database Integrity: {int_check}")
assert st_cnt == 30000 and enr_cnt == 30000 and int_check == 'ok' and len(fk_errs) == 0

print("\n=== 2. TESTING ALL 30 INSTITUTION PROFILE & ACADEMIC APIS ===")
schools = c.execute("SELECT school_id, school_type FROM schools ORDER BY school_id").fetchall()
success_cnt = 0
for s_id, s_type in schools:
    url = f"http://localhost:8001/schools/{s_id}"
    req = urllib.request.urlopen(url)
    assert req.status == 200
    
    url_str = f"http://localhost:8001/schools/{s_id}/academic-strength"
    res_str = urllib.request.urlopen(url_str)
    str_data = json.loads(res_str.read())
    assert str_data["total_sanctioned_capacity"] >= 0
    assert "privacy_guarantee" in str_data
    # Verify NO student personal PII in public response
    raw_text = json.dumps(str_data).lower()
    for forbidden in ["aadhaar", "password", "hash", "date_of_birth", "father_name", "mother_name", "annual_income"]:
        assert forbidden not in raw_text, f"Forbidden PII '{forbidden}' found in public academic strength response for {s_id}"
    success_cnt += 1

print(f"  [PASS] All {success_cnt}/30 institution APIs tested successfully with zero privacy leaks.")

print("\n=== 3. TESTING ACADEMIC STRUCTURE BY TIER ===")
# School K-10 (SCH001)
res_sch001 = json.loads(urllib.request.urlopen("http://localhost:8001/schools/SCH001/academic-strength").read())
print(f"  School (SCH001): {res_sch001['total_enrolled_strength']} enrolled, {res_sch001['sections_count']} sections, Languages: {res_sch001['languages_offered']}")

# PU College (SCH011)
res_sch011 = json.loads(urllib.request.urlopen("http://localhost:8001/schools/SCH011/academic-strength").read())
pu_progs = [p['combination_code'] for p in res_sch011['program_aggregates'] if p['combination_code']]
print(f"  PU College (SCH011): {res_sch011['total_enrolled_strength']} enrolled across combinations: {pu_progs}")

# Engineering & Diploma (COL001)
res_col001 = json.loads(urllib.request.urlopen("http://localhost:8001/schools/COL001/academic-strength").read())
dip_ug_progs = [p['program_name'] for p in res_col001['program_aggregates']]
print(f"  College Group (COL001): {res_col001['total_enrolled_strength']} enrolled across {len(dip_ug_progs)} Diploma & UG programmes.")

print("\n=== 4. HEADLESS BROWSER SCREENSHOTS & TESTING ===")
tests = [
    {
        "name": "School Profile & K-10 Academic Structure (SCH001)",
        "url": "http://localhost:5173/#/schools/SCH001",
        "window_size": "1440,3200",
        "file_name": "phase3_school_profile_academics.png",
        "expected_strings": [
            "Government Model School",
            "Academic Structure & Programme Curricula",
            "Karnataka State School Education (Std 1-10)",
            "Live Seat Availability & Quota",
            "Student Directory & Academic Strength",
            "Karnataka Education Data Privacy Safeguard",
            "Total Active Enrolment"
        ]
    },
    {
        "name": "PU Composite College Structure (SCH011)",
        "url": "http://localhost:5173/#/schools/SCH011",
        "window_size": "1440,3200",
        "file_name": "phase3_pu_college_structure.png",
        "expected_strings": [
            "Tumakuru Model School",
            "Pre-University (PCMB",
            "Pre-University (CEBA",
            "Academic Structure & Programme Curricula",
            "Student Directory & Academic Strength",
            "2,400"
        ]
    },
    {
        "name": "Multi-Division Engineering College Architecture (COL001)",
        "url": "http://localhost:5173/#/schools/COL001",
        "window_size": "1440,3400",
        "file_name": "phase3_multidivision_college_profile.png",
        "expected_strings": [
            "Ramaiah Institute of Technology",
            "Faculty of Engineering & Technology",
            "Ramaiah Composite Pre-University College",
            "Ramaiah Polytechnic",
            "Ramaiah College of Arts, Science & Commerce",
            "Academic Divisions & Campus Architecture",
            "B.E. in Computer Science and Engineering",
            "Diploma in Automobile Engineering"
        ]
    },
    {
        "name": "Student Directory & Academic Strength View (COL001)",
        "url": "http://localhost:5173/#/schools/COL001",
        "window_size": "1440,2800",
        "file_name": "phase3_student_directory_academic_strength.png",
        "expected_strings": [
            "Student Directory & Academic Strength",
            "Total Active Enrolment",
            "Sanctioned Capacity",
            "Capacity Utilization",
            "Active Sections Tracked"
        ]
    }
]

all_passed = True
for t in tests:
    print(f"\n--- Testing: {t['name']} ---")
    dest_path = os.path.join(screenshot_dir, t['file_name'])
    brain_path = os.path.join(brain_dir, t['file_name'])
    
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={t['window_size']}",
        "--virtual-time-budget=6000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={dest_path}",
        "--dump-dom",
        t['url']
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    dom = html.unescape(res.stdout)

    matched = 0
    for exp in t['expected_strings']:
        if exp in dom:
            print(f"  [PASS] Found: '{exp}'")
            matched += 1
        else:
            print(f"  [FAIL] Missing: '{exp}'")
            all_passed = False

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        shutil.copyfile(dest_path, brain_path)
        print(f"  Screenshot Saved & Synced: {t['file_name']} ({os.path.getsize(dest_path)} bytes)")
    else:
        print(f"  [WARN] Screenshot not generated for {t['name']}")

print("\n==========================================")
print(f"OVERALL PHASE 3 STATUS: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
print("==========================================")
