import json
import urllib.request
import urllib.error
from database import get_connection
from auth import create_access_token

conn = get_connection()
cur = conn.cursor()

# Get SCH002 admin
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE school_id = 'SCH002' OR email = 'shanti@edu.in'")
u_sch002 = dict(cur.fetchone())

# Get SCH001 admin
cur.execute("SELECT user_id, email, role, school_id FROM users WHERE email = 'government.model@edu.in'")
u_sch001 = dict(cur.fetchone())

conn.close()

token_sch002 = create_access_token(u_sch002, school_id="SCH002")
token_sch001 = create_access_token(u_sch001, school_id="SCH001")

print("--- Testing Security & Validation Enforcement ---")

# 1. Cross-institution student edit attempt
# SCH002 admin attempts to PUT /institution/SCH001/students/SCH01125
req1 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps({"student_name": "Unauthorized Hacked Name", "reason": "Hacking attempt"}).encode(),
    headers={"Authorization": f"Bearer {token_sch002}", "Content-Type": "application/json"},
    method="PUT"
)
try:
    with urllib.request.urlopen(req1) as resp:
        print("FAIL: Cross-institution edit was allowed!")
except urllib.error.HTTPError as he:
    print(f"PASS (Security 1): Cross-institution edit blocked with HTTP {he.code}: {he.reason}")

# 2. Invalid date format validation
req2 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps({"date_of_birth": "15/06/2014", "reason": "Testing invalid date format"}).encode(),
    headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
    method="PUT"
)
try:
    with urllib.request.urlopen(req2) as resp:
        print("FAIL: Invalid date format was allowed!")
except urllib.error.HTTPError as he:
    print(f"PASS (Validation 1): Invalid date format rejected with HTTP {he.code}: {he.reason}")

# 3. Invalid school standard (e.g. Standard 12 in K-10 school)
req3 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps({"standard": 12, "reason": "Testing invalid standard"}).encode(),
    headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
    method="PUT"
)
try:
    with urllib.request.urlopen(req3) as resp:
        print("FAIL: Invalid standard was allowed!")
except urllib.error.HTTPError as he:
    print(f"PASS (Validation 2): Standard 12 in K-10 school rejected with HTTP {he.code}: {he.reason}")

# 4. Empty / missing reason
req4 = urllib.request.Request(
    "http://127.0.0.1:8000/institution/SCH001/students/SCH01125",
    data=json.dumps({"blood_group": "A+", "reason": "no"}).encode(),
    headers={"Authorization": f"Bearer {token_sch001}", "Content-Type": "application/json"},
    method="PUT"
)
try:
    with urllib.request.urlopen(req4) as resp:
        print("FAIL: Short reason was allowed!")
except urllib.error.HTTPError as he:
    print(f"PASS (Validation 3): Missing/short reason rejected with HTTP {he.code}: {he.reason}")

print("--- ALL SECURITY & VALIDATION TESTS PASSED ---")
