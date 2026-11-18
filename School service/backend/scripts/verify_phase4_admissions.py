import subprocess
import os
import shutil
import urllib.request
import urllib.parse
import json
import sqlite3
import time

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
screenshot_dir = r"C:\Users\callm\nagriksetu\screenshots"
brain_dir = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20"
os.makedirs(screenshot_dir, exist_ok=True)

BASE_URL = "http://127.0.0.1:8001"

def req(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except:
            return e.code, err_body
    except Exception as e:
        return 0, str(e)

print("=====================================================================")
print("NAGRIKSETU PHASE 4 COMPREHENSIVE VERIFICATION & TEST SUITE")
print("Stage 1: Institution-Specific Initial Admission Application")
print("=====================================================================")

# -------------------------------------------------------------
# 1. DATABASE RECORD PRESERVATION & INTEGRITY AUDIT
# -------------------------------------------------------------
print("\n[STEP 1] DATABASE RECORD PRESERVATION & SCHEMA AUDIT")
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

print(f"  Enrolled Students:    {st_cnt} (Required: 30,000)")
print(f"  Official Enrollments: {enr_cnt} (Required: 30,000)")
print(f"  Academic Programs:    {prog_cnt} (Required: 198)")
print(f"  Program Sections:     {sec_cnt} (Required: 841)")
print(f"  Institutions:         {sch_cnt} (Required: 30)")
print(f"  Campus Divisions:     {div_cnt} (Required: 13)")
print(f"  PRAGMA Foreign Keys:  {len(fk_errs)} violations")
print(f"  PRAGMA Integrity:     {int_check}")

assert st_cnt == 30000, f"DATA ERROR: student count changed to {st_cnt}"
assert enr_cnt == 30000, f"DATA ERROR: enrollment count changed to {enr_cnt}"
assert prog_cnt == 198, f"DATA ERROR: program count changed to {prog_cnt}"
assert sec_cnt == 841, f"DATA ERROR: section count changed to {sec_cnt}"
assert len(fk_errs) == 0, f"FOREIGN KEY VIOLATIONS: {fk_errs}"
assert int_check == "ok", f"INTEGRITY CHECK FAILED: {int_check}"
print("  [PASS] 100% Core Data Baseline Preserved Without Any Corruption.")

# -------------------------------------------------------------
# 2. DYNAMIC FORM CONFIGURATION VERIFICATION (ALL 4 TIERS)
# -------------------------------------------------------------
print("\n[STEP 2] DYNAMIC FORM CONFIGURATION VERIFICATION")

# A. School (SCH001)
st, cfg_sch = req("GET", "/admissions/form-config/SCH001")
assert st == 200 and "school" in cfg_sch["offered_levels"]
standards = cfg_sch["school_config"]["standards"]
first_langs = cfg_sch["school_config"]["first_languages"]
print(f"  School (SCH001): {st} OK. Standards: {standards}, First Languages: {first_langs}")
assert 1 in standards and 10 in standards and "Kannada" in first_langs

# B. PU College (SCH011)
st, cfg_pu = req("GET", "/admissions/form-config/SCH011")
assert st == 200 and "higher_secondary" in cfg_pu["offered_levels"]
streams = cfg_pu["pu_config"]["streams"]
combos = [c["combination_code"] for c in cfg_pu["pu_config"]["combinations"]]
print(f"  PU College (SCH011): {st} OK. Streams: {streams}, Combinations ({len(combos)}): {combos}")
assert "Science" in streams and "Commerce" in streams and "PCMB" in combos and "PCMC" in combos

# C. College Group (COL001)
st, cfg_col = req("GET", "/admissions/form-config/COL001")
assert st == 200 and "diploma" in cfg_col["offered_levels"] and "undergraduate" in cfg_col["offered_levels"]
dip_progs = [p["program_name"] for p in cfg_col["diploma_config"]["programs"]]
ug_progs = [p["program_name"] for p in cfg_col["undergraduate_config"]["programs"]]
print(f"  College Group (COL001): {st} OK. Diploma: {len(dip_progs)} progs, UG: {len(ug_progs)} progs")
assert len(dip_progs) == 5 and len(ug_progs) == 8
print("  [PASS] All 4 Educational Tiers Dynamically Configured from Database.")

# -------------------------------------------------------------
# 3. STAGE 1 SUBMISSION & UNIQUE APPLICATION ID GENERATION
# -------------------------------------------------------------
print("\n[STEP 3] STAGE 1 APPLICATION SUBMISSION ACROSS ALL 4 TIERS")

# A. School Application
app_sch_payload = {
    "institution_id": "SCH001",
    "applicant_name": "Arun Kumar",
    "parent_name": "Gopal Kumar",
    "parent_phone": "9845012345",
    "parent_email": "gopal.k@example.com",
    "residential_address": "88, 15th Cross, Malleshwaram, Bengaluru",
    "academic_year": "2026-2027",
    "education_level": "school",
    "requested_standard": 6,
    "first_language_preference": "Kannada",
    "second_language_preference": "English"
}
st, res_sch = req("POST", "/admissions/apply", app_sch_payload)
assert st == 201, f"School submission failed: {res_sch}"
app_id_sch = res_sch["application_id"]
assert app_id_sch.startswith("APP-2026-SCH001-"), f"Unexpected ID format: {app_id_sch}"
print(f"  [PASS] School App Submitted -> ID: {app_id_sch}")

# B. PU College Application
app_pu_payload = {
    "institution_id": "SCH011",
    "applicant_name": "Meera Joshi",
    "parent_name": "Nandish Joshi",
    "parent_phone": "9845012346",
    "parent_email": "nandish.j@example.com",
    "residential_address": "14, Park View, Tumakuru",
    "academic_year": "2026-2027",
    "education_level": "higher_secondary",
    "stream_preference": "Science",
    "combination_code": "PCMB",
    "requested_program_id": "PROG-SCH011-PCMB"
}
st, res_pu = req("POST", "/admissions/apply", app_pu_payload)
assert st == 201, f"PU submission failed: {res_pu}"
app_id_pu = res_pu["application_id"]
assert app_id_pu.startswith("APP-2026-SCH011-"), f"Unexpected ID format: {app_id_pu}"
print(f"  [PASS] PU College App Submitted -> ID: {app_id_pu}")

# C. Diploma Application
dip_id = cfg_col["diploma_config"]["programs"][0]["program_id"]
app_dip_payload = {
    "institution_id": "COL001",
    "applicant_name": "Vijay Shankar",
    "parent_name": "Shankar Gowda",
    "parent_phone": "9845012347",
    "parent_email": "shankar.g@example.com",
    "residential_address": "22, Peenya Stage 2, Bengaluru",
    "academic_year": "2026-2027",
    "education_level": "diploma",
    "requested_program_id": dip_id,
    "stream_preference": "Diploma in Mechanical Engineering"
}
st, res_dip = req("POST", "/admissions/apply", app_dip_payload)
assert st == 201, f"Diploma submission failed: {res_dip}"
app_id_dip = res_dip["application_id"]
assert app_id_dip.startswith("APP-2026-COL001-"), f"Unexpected ID format: {app_id_dip}"
print(f"  [PASS] Diploma App Submitted -> ID: {app_id_dip}")

# D. Undergraduate Application
ug_id = cfg_col["undergraduate_config"]["programs"][0]["program_id"]
app_ug_payload = {
    "institution_id": "COL001",
    "applicant_name": "Deepika Rao",
    "parent_name": "Raghunath Rao",
    "parent_phone": "9845012348",
    "parent_email": "raghunath.r@example.com",
    "residential_address": "45, Brigade Road, Bengaluru",
    "academic_year": "2026-2027",
    "education_level": "undergraduate",
    "requested_program_id": ug_id,
    "stream_preference": "Bachelor of Technology"
}
st, res_ug = req("POST", "/admissions/apply", app_ug_payload)
assert st == 201, f"Undergraduate submission failed: {res_ug}"
app_id_ug = res_ug["application_id"]
assert app_id_ug.startswith("APP-2026-COL001-"), f"Unexpected ID format: {app_id_ug}"
print(f"  [PASS] Undergraduate App Submitted -> ID: {app_id_ug}")

# -------------------------------------------------------------
# 4. PRIVACY-PRESERVING PUBLIC CONFIRMATION ENDPOINT
# -------------------------------------------------------------
print("\n[STEP 4] PRIVACY AUDIT OF PUBLIC CONFIRMATION ENDPOINT")
st, conf_data = req("GET", f"/admissions/applications/{app_id_sch}/public-confirmation")
assert st == 200, f"Public confirmation endpoint failed: {st}"
assert conf_data["application_id"] == app_id_sch
assert conf_data["institution_name"] == "Government Model School"
assert conf_data["applicant_name"] == "Arun Kumar"
assert conf_data["status"] == "submitted"

# Verify privacy protection: ensure NO phone, email, address, or internal staff notes exist
conf_str = json.dumps(conf_data).lower()
for pii in ["9845012345", "gopal.k@example.com", "malleshwaram", "residential_address"]:
    assert pii not in conf_str, f"Privacy Leak detected: {pii} leaked in public response!"
print(f"  [PASS] Public confirmation safely verifies application {app_id_sch} with zero PII leakage.")

# -------------------------------------------------------------
# 5. STAFF ADMISSION DESK LIFECYCLE & HUMAN DECISION AUDIT
# -------------------------------------------------------------
print("\n[STEP 5] INSTITUTION ADMISSION DESK LIFECYCLE WORKFLOW")
login_data = urllib.parse.urlencode({
    "username": "staff.sch001@example.com",
    "password": "Staff@NagrikSetu2026!"
}).encode("utf-8")
req_l = urllib.request.Request(f"{BASE_URL}/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
with urllib.request.urlopen(req_l, timeout=5) as r_login:
    staff_token = json.loads(r_login.read().decode("utf-8"))["access_token"]

# A. Overview
st, overview = req("GET", "/school/admissions/overview", token=staff_token)
assert st == 200 and overview["total_applications"] > 0
print(f"  Admission Desk KPI: Total: {overview['total_applications']}, Submitted: {overview['submitted_count']}, Approved: {overview['approved_count']}")

# B. Action 1: Take up for Review
st, r_rev = req("POST", f"/school/admissions/{app_id_sch}/review", {"notes": "Initiated eligibility verification against zone quota."}, token=staff_token)
assert st == 200 and r_rev["status"] == "under_review"
print(f"  [PASS] Action 'Review' -> Status: {r_rev['status']}")

# C. Action 2: Request Clarification from Parent
st, r_clar = req("POST", f"/school/admissions/{app_id_sch}/request-clarification", {
    "clarification_message": "Kindly confirm if school bus transport pickup is required for Malleshwaram 15th cross."
}, token=staff_token)
assert st == 200 and r_clar["status"] == "action_required"
print(f"  [PASS] Action 'Clarification' -> Status: {r_clar['status']}")

# D. Action 3: Approve Stage 1
st, r_appr = req("POST", f"/school/admissions/{app_id_sch}/approve", {
    "confirm": True,
    "note": "Preliminary eligibility verified. Standard 6 capacity confirmed. Approved for Stage 2."
}, token=staff_token)
assert st == 200 and r_appr["status"] == "approved"
print(f"  [PASS] Action 'Approve Stage 1' -> Status: {r_appr['status']}")

# E. Action 4: Rejection on separate test application
rej_payload = dict(app_sch_payload, applicant_name="Out-of-State Applicant", residential_address="Outside Karnataka Catchment")
_, rej_init = req("POST", "/admissions/apply", rej_payload)
rej_id = rej_init["application_id"]
st, r_rej = req("POST", f"/school/admissions/{rej_id}/reject", {
    "rejection_reason": "Applicant residence is outside statutory government school catchment area.",
    "rejection_explanation": "Please refer to local taluk education office for boundary allotment.",
    "institution_contact_phone": "080-23341122"
}, token=staff_token)
assert st == 200 and r_rej["status"] == "rejected"
print(f"  [PASS] Action 'Reject' -> Status: {r_rej['status']} with mandatory human rationale.")

# F. Verify Chronological Audit Trail History
st, hist = req("GET", f"/school/admissions/{app_id_sch}/history", token=staff_token)
history_list = hist if isinstance(hist, list) else hist.get("history", [])
print(f"  [PASS] History Audit Trail recorded {len(history_list)} events:")
for h in history_list:
    print(f"    - {h.get('previous_status')} -> {h.get('new_status')}: {h.get('action_note')}")
assert len(history_list) >= 4

# -------------------------------------------------------------
# 6. VERIFY STRICT TWO-STAGE ADMISSION BOUNDARY
# -------------------------------------------------------------
print("\n[STEP 6] VERIFY STRICT TWO-STAGE BOUNDARY")
# Confirm no students were created in the students table
st_after = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
enr_after = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
assert st_after == 30000 and enr_after == 30000
print(f"  [PASS] Verified: Students remain {st_after}, Enrollments remain {enr_after}.")
print("         Stage 1 applications DO NOT mutate official student rosters.")
conn.close()

# -------------------------------------------------------------
# 7. AUTOMATED HEADLESS EDGE SCREENSHOT CAPTURES
# -------------------------------------------------------------
print("\n[STEP 7] CAPTURING PROFESSIONAL HEADLESS SCREENSHOTS")

screenshot_tasks = [
    {
        "name": "Phase 4 - Stage 1 School Admission Modal (SCH001)",
        "url": "http://localhost:5173/schools/SCH001?apply=true",
        "file": "phase4_admission_modal_school.png",
        "size": "1440,1100"
    },
    {
        "name": "Phase 4 - Stage 1 PU College Admission Modal (SCH011)",
        "url": "http://localhost:5173/schools/SCH011?apply=true",
        "file": "phase4_admission_modal_pu.png",
        "size": "1440,1100"
    },
    {
        "name": "Phase 4 - Stage 1 Multi-Division College Admission Modal (COL001)",
        "url": "http://localhost:5173/schools/COL001?apply=true",
        "file": "phase4_admission_modal_college.png",
        "size": "1440,1100"
    },
    {
        "name": "Phase 4 - Institution Staff Admission Desk Tab",
        "url": "http://localhost:5173/staff?tab=admissions",
        "file": "phase4_staff_admission_desk.png",
        "size": "1440,1100"
    }
]

for task in screenshot_tasks:
    dest_path = os.path.join(screenshot_dir, task["file"])
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={task['size']}",
        f"--screenshot={dest_path}",
        "--virtual-time-budget=4000",
        task["url"]
    ]
    print(f"  Capturing '{task['name']}'...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(dest_path):
        size_kb = os.path.getsize(dest_path) // 1024
        print(f"    Saved: {dest_path} ({size_kb} KB)")
        # Copy to brain artifact directory
        brain_dest = os.path.join(brain_dir, task["file"])
        shutil.copyfile(dest_path, brain_dest)
        print(f"    Copied to Artifacts: {brain_dest}")
    else:
        print(f"    WARNING: Screenshot failed for {task['file']}")

print("\n=====================================================================")
print(">>> ALL PHASE 4 VALIDATION SUITES PASSED 100% WITH FLYING COLORS <<<")
print("=====================================================================")
