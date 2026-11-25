import urllib.request
import urllib.parse
import json
import sqlite3
import sys

BASE_URL = "http://localhost:8000"

def api_get(path, token=None):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_post_form(path, form_data, token=None):
    encoded = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=encoded, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_post_json(path, data, token=None):
    encoded = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=encoded, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

print("=" * 80)
print("NAGRIKSETU DIRECT INSTITUTION ADMINISTRATOR LOGIN VERIFICATION SUITE")
print("=" * 80)

# Check 1 & 2: Public institutions directory and admin-statuses
print("\n--- TEST 1 & 2: Public Institutions Cards & Statuses ---")
status, schools_data = api_get("/schools?limit=100")
assert status == 200, f"Expected 200 from /schools, got {status}"
print(f"Total institutions retrieved: {len(schools_data)}")
assert len(schools_data) >= 30, f"Expected at least 30 institutions, got {len(schools_data)}"

blocked_cards = []
for s in schools_data:
    st = s.get("admin_status") or {}
    btn = st.get("button_label")
    can_login = st.get("can_login")
    if btn != "Continue to Administrator Login →" or not can_login:
        blocked_cards.append((s["school_id"], s["school_name"], btn, can_login))

if blocked_cards:
    print(f"FAILED: {len(blocked_cards)} cards blocked!")
    for b in blocked_cards:
        print(" ", b)
    sys.exit(1)
else:
    print(f"SUCCESS: All {len(schools_data)} institution cards show 'Continue to Administrator Login →' with can_login=True.")
    print("SUCCESS: Zero institution cards blocked by 'Invitation Required' or 'Not Provisioned'.")

# Check 3 & 4: Database Account Uniqueness and One Administrator Account Per Institution
print("\n--- TEST 3 & 4: Administrator Accounts & Email Uniqueness in Database ---")
conn = sqlite3.connect("/app/data/nagriksetu.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Check email uniqueness (for non-null emails)
c.execute("SELECT email, COUNT(*) as cnt FROM users WHERE email IS NOT NULL AND TRIM(email) != '' GROUP BY LOWER(email) HAVING cnt > 1")
duplicates = c.fetchall()
assert len(duplicates) == 0, f"Duplicate emails found: {[dict(d) for d in duplicates]}"
print("SUCCESS: All email addresses in users table are unique.")

# Verify each of the 30 institutions has an active administrator account
doc_credentials = [
    # Schools (15)
    ("SCH001", "Government Model School", "government.model@edu.in", "government@123"),
    ("SCH002", "Shanti Vidya Mandir", "shanti@edu.in", "shanti@123"),
    ("SCH003", "National Public School", "national.public@edu.in", "national@123"),
    ("SCH004", "Sri Vidya School", "sri.vidya@edu.in", "srividya@123"),
    ("SCH005", "Green Valley School", "green.valley@edu.in", "greenvalley@123"),
    ("SCH006", "Bharat Education School", "bharat@edu.in", "bharat@123"),
    ("SCH007", "New Horizon School", "newhorizon@edu.in", "newhorizon@123"),
    ("SCH008", "Vivekananda School", "vivekananda@edu.in", "vivekananda@123"),
    ("SCH009", "Saraswati Vidya Kendra", "saraswati@edu.in", "saraswati@123"),
    ("SCH010", "Karnataka Public School", "karnataka.public@edu.in", "karnataka@123"),
    ("SCH016", "Belagavi Public School", "belagavi@edu.in", "belagavi@123"),
    ("SCH017", "Dharwad Vidya School", "dharwad@edu.in", "dharwad@123"),
    ("SCH018", "Shivamogga Model School", "shivamogga@edu.in", "shivamogga@123"),
    ("SCH019", "Ballari Education School", "ballari@edu.in", "ballari@123"),
    ("SCH020", "Kalaburagi Public School", "kalaburagi@edu.in", "kalaburagi@123"),
    # PU Colleges (5)
    ("SCH011", "Tumakuru Model Pre-University College", "tumakuru.pu@edu.in", "tumakuru@123"),
    ("SCH012", "Mysuru Government Pre-University College", "mysuru.pu@edu.in", "mysuru@123"),
    ("SCH013", "Mandya Government Pre-University College", "mandya.pu@edu.in", "mandya@123"),
    ("SCH014", "Hassan Valley Pre-University College", "hassan.pu@edu.in", "hassan@123"),
    ("SCH015", "Udupi Government Pre-University College", "udupi.pu@edu.in", "udupi@123"),
    # Degree Colleges (5)
    ("COL001", "Ramaiah Institute of Technology (MSRIT)", "ramaiah@edu.in", "ramaiah@123"),
    ("COL002", "R.V. College of Engineering (RVCE)", "rvce@edu.in", "rvce@123"),
    ("COL003", "BMS College of Engineering (BMSCE)", "bms@edu.in", "bms@123"),
    ("COL005", "The National Institute of Engineering (NIE)", "nie@edu.in", "nie@123"),
    ("COL007", "Mount Carmel College (Autonomous)", "mountcarmel@edu.in", "mountcarmel@123"),
    # Universities (5)
    ("COL004", "PES University (Ring Road Campus)", "pes@edu.in", "pes@123"),
    ("COL006", "St. Joseph's University", "stjosephs@edu.in", "stjosephs@123"),
    ("COL008", "KLE Technological University (BVBCET)", "kle.tech@edu.in", "kletech@123"),
    ("COL009", "University of Mysore (Manasagangotri)", "university.mysore@edu.in", "mysore@123"),
    ("COL010", "Visvesvaraya Technological University (VTU)", "vtu@edu.in", "vtu@123"),
]

# Check 5 & 6: Test Login For All 30 Institutions
print("\n--- TEST 5 & 6: Authentication & Dashboard Access Across All 30 Institutions ---")
tokens = {}
login_failures = []

for db_id, name, email, pwd in doc_credentials:
    status_code, res = api_post_form(f"/auth/login?institution_id={db_id}", {
        "username": email,
        "password": pwd
    })
    if status_code != 200 or not res.get("access_token"):
        login_failures.append((db_id, name, email, status_code, res))
        print(f"FAILED: {db_id} ({email}) -> status {status_code}: {res}")
    else:
        tokens[db_id] = res["access_token"]
        assert res["school_id"] == db_id, f"Expected school_id {db_id}, got {res.get('school_id')}"
        assert res["role"] in ("school_admin", "academic_admin"), f"Expected administrator role, got {res.get('role')}"
        # Test dashboard overview access with this token
        ov_code, ov_res = api_get(f"/institution/{db_id}/dashboard-overview", res["access_token"])
        assert ov_code == 200, f"Expected 200 for dashboard-overview {db_id}, got {ov_code}: {ov_res}"
        print(f"PASS: [{db_id}] {email} -> Logged in successfully | Dashboard stats: {ov_res.get('total_students')} students, {ov_res.get('total_parents')} parents")

assert len(login_failures) == 0, f"Login failures: {login_failures}"
print(f"\nSUCCESS: All {len(doc_credentials)} institution administrator accounts authenticated and opened their dashboard overview successfully!")

# Check 7: Cross-Institution Security Isolation
print("\n--- TEST 7: Cross-Institution Security Isolation ---")
# Attempt 1: SCH001 admin tries to log into COL003 via login endpoint
status_code, res = api_post_form("/auth/login?institution_id=COL003", {
    "username": "government.model@edu.in",
    "password": "government@123"
})
assert status_code == 403, f"Expected 403 for SCH001 admin logging into COL003, got {status_code}"
print("PASS: Cross-institution login correctly rejected with HTTP 403 Forbidden.")

# Attempt 2: SCH001 token tries to access COL003 dashboard overview
sch001_token = tokens["SCH001"]
status_code, res = api_get("/institution/COL003/dashboard-overview", sch001_token)
assert status_code == 403, f"Expected 403 for SCH001 token accessing COL003 overview, got {status_code}"
print("PASS: Cross-institution dashboard-overview correctly rejected with HTTP 403 Forbidden.")

# Attempt 3: COL003 token tries to access SCH019 students
col003_token = tokens["COL003"]
status_code, res = api_get("/institution/SCH019/students", col003_token)
assert status_code == 403, f"Expected 403 for COL003 token accessing SCH019 students, got {status_code}"
print("PASS: Cross-institution student records access correctly rejected with HTTP 403 Forbidden.")

# Check 8: Preserved Ballari Administrator Access
print("\n--- TEST 8: Preserved Ballari Administrator Access ---")
status_code, res = api_post_form("/auth/login?institution_id=SCH019", {
    "username": "rao@edu.in",
    "password": "Staff@NagrikSetu2026!"
})
assert status_code == 200, f"Expected 200 for rao@edu.in, got {status_code}: {res}"
assert res["school_id"] == "SCH019", f"Expected school_id SCH019, got {res.get('school_id')}"
status_code, ov_res = api_get("/institution/SCH019/dashboard-overview", res["access_token"])
assert status_code == 200, f"Expected 200 for SCH019 overview with rao token, got {status_code}"
print(f"PASS: Existing Ballari Education School administrator (rao@edu.in) logged in successfully! Mapped students: {ov_res.get('total_students')}")

# Also test Vidya Mandir English School (SCH0099)
print("\n--- TEST 8B: Preserved Vidya Mandir English School Administrator (SCH0099) ---")
c.execute("SELECT password_hash FROM users WHERE email = 'admin.sch0099@gmail.com'")
sch099_row = c.fetchone()
assert sch099_row is not None, "SCH0099 administrator record not found"
print("PASS: SCH0099 administrator account preserved in database.")

# Check 9: Platform Administrator Intact
print("\n--- TEST 9: Platform Administrator Functionality ---")
status_code, res = api_post_form("/auth/login", {
    "username": "admin.central@nagriksetu.gov",
    "password": "Central@NagrikSetu2026!"
})
assert status_code == 200, f"Expected 200 for platform admin, got {status_code}: {res}"
platform_token = res["access_token"]
assert res["role"] == "platform_admin", f"Expected platform_admin role, got {res.get('role')}"
# Platform admin can view overview of ANY institution
status_code, res1 = api_get("/institution/SCH001/dashboard-overview", platform_token)
assert status_code == 200, f"Expected platform admin to access SCH001, got {status_code}"
status_code, res2 = api_get("/institution/COL003/dashboard-overview", platform_token)
assert status_code == 200, f"Expected platform admin to access COL003, got {status_code}"
print("PASS: Platform Administrator authenticated and has universal administrative access.")

# Check 10: System Data Safety & 30,003 Students Preserved
print("\n--- TEST 10: Preserve Existing System Data & 30,003 Students ---")
total_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
print(f"Total students in database: {total_students}")
assert total_students == 30003, f"CRITICAL ERROR: Student count changed from 30,003 to {total_students}"
print("PASS: Exactly 30,003 student records confirmed unchanged!")

total_enrollments = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
print(f"Total enrollments in database: {total_enrollments}")
assert total_enrollments >= 30003, "Enrollments integrity failure"
print("PASS: Enrolments integrity preserved.")

# Check Academic modules for different categories
print("\n--- TEST Academic Modules by Category ---")
# School: SCH001
c_code, struct_sch = api_get("/institution/SCH001/academic-structure", tokens["SCH001"])
assert c_code == 200 and len(struct_sch.get("standards", [])) > 0
print(f"PASS: School SCH001 has {len(struct_sch['standards'])} standards configured.")

# PU College: SCH011
c_code, struct_pu = api_get("/institution/SCH011/academic-structure", tokens["SCH011"])
assert c_code == 200 and len(struct_pu.get("streams", [])) > 0
print(f"PASS: PU College SCH011 has {len(struct_pu['streams'])} streams configured ({', '.join(str(s) for s in struct_pu['streams'][:3])}).")

# Degree College: COL001
c_code, struct_deg = api_get("/institution/COL001/academic-structure", tokens["COL001"])
assert c_code == 200 and len(struct_deg.get("programs", [])) > 0
print(f"PASS: Degree College COL001 has {len(struct_deg['programs'])} academic programs configured.")

# University: COL010
c_code, struct_uni = api_get("/institution/COL010/academic-structure", tokens["COL010"])
assert c_code == 200 and len(struct_uni.get("programs", [])) > 0
print(f"PASS: University COL010 has {len(struct_uni['programs'])} academic programs / faculties configured.")

# Test must_change_password flag
print("\n--- TEST Password Change Policy ---")
c.execute("SELECT must_change_password FROM users WHERE email = 'government.model@edu.in'")
mcp = c.fetchone()[0]
assert mcp == 1, f"Expected must_change_password=1 for new account, got {mcp}"
print("PASS: New administrator account has must_change_password=1 as required.")

conn.close()
print("\n" + "=" * 80)
print("ALL 10 VERIFICATION TESTS PASSED FLAWLESSLY! 100% SUCCESS RATE")
print("=" * 80)
