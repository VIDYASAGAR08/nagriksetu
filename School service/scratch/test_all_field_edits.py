import urllib.request, json
from auth import create_access_token
from database import get_connection

print("=== TESTING EDIT ON ALL FIELDS ACROSS INSTITUTION TYPES ===")

conn = get_connection()
c = conn.cursor()

# Find an admin and student for SCH019
c.execute("SELECT user_id, email, role, school_id FROM users WHERE school_id = 'SCH019' AND role IN ('school_admin', 'institution_admin') LIMIT 1")
admin_sch019 = dict(c.fetchone())

# Find an admin and student for SCH001
c.execute("SELECT user_id, email, role, school_id FROM users WHERE school_id = 'SCH001' AND role IN ('school_admin', 'institution_admin') LIMIT 1")
admin_sch001 = dict(c.fetchone())

conn.close()

token_sch019 = create_access_token(admin_sch019, school_id='SCH019')
token_sch001 = create_access_token(admin_sch001, school_id='SCH001')

# Test 1: Edit SCH19001 gender, section, blood_group, taluk
payload_1 = {
    "gender": "Female",
    "blood_group": "O+",
    "section": "A",
    "taluk": "Ballari Urban",
    "village_city": "Ballari City",
    "contact_number": "9845012345",
    "reason": "verified"
}
req = urllib.request.Request(
    'http://127.0.0.1:8000/institution/SCH019/students/SCH19001',
    data=json.dumps(payload_1).encode(),
    headers={'Authorization': f'Bearer {token_sch019}', 'Content-Type': 'application/json'},
    method='PUT'
)
with urllib.request.urlopen(req) as resp:
    res1 = json.loads(resp.read().decode())
    print("[TEST 1 - SCH019 SCH19001] Result:", res1)

# Test 2: Edit SCH01125 student_name, medium_of_instruction, first_language
payload_2 = {
    "student_name": "Asha Sharma",
    "first_language": "Kannada",
    "medium_of_instruction": "English",
    "section": "A",
    "reason": "Updated language medium"
}
req2 = urllib.request.Request(
    'http://127.0.0.1:8000/institution/SCH001/students/SCH01125',
    data=json.dumps(payload_2).encode(),
    headers={'Authorization': f'Bearer {token_sch001}', 'Content-Type': 'application/json'},
    method='PUT'
)
with urllib.request.urlopen(req2) as resp:
    res2 = json.loads(resp.read().decode())
    print("[TEST 2 - SCH001 SCH01125] Result:", res2)

print("\nALL FIELD EDIT TESTS COMPLETED SUCCESSFULLY!")
