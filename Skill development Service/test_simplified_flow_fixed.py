import requests
import json
import pymysql
import jwt
import time

API_BASE = "http://127.0.0.1:8003/api"
JWT_SECRET = "nagriksetu-skill-super-secret-key-2026-xyz-32char"

def get_token(citizen_ref, email, name="Citizen Test User"):
    now = int(time.time())
    payload = {
        "sub": email,
        "role": "CITIZEN",
        "citizen_ref": citizen_ref,
        "name": name,
        "centre_id": None,
        "iat": now,
        "exp": now + 86400
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

token_cit6 = get_token("CIT-000006", "karan123@gmail.com", "Karan Sharma")

# Test target: Programme 2 -> Centre 2 (Mysuru)
# Let's inspect current batch 3 available seats
conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, available_seats, total_seats FROM batches WHERE id = 3")
    b3_before = cur.fetchone()
    cur.execute("SELECT COUNT(*) as cnt FROM enrollments WHERE centre_id = 2")
    c2_count_before = cur.fetchone()['cnt']
conn.close()

print(f"Before Test: Batch 3 has {b3_before['available_seats']} / {b3_before['total_seats']} seats. Centre 2 apps: {c2_count_before}")

simplified_dossier = {
    "section_a_personal": {
        "full_name": "Karan Sharma",
        "citizen_ref": "CIT-000006",
        "email": "karan123@gmail.com",
        "phone": "9876543210"
    },
    "section_b_location": {
        "city_district": "Mysuru",
        "pincode": "570001"
    },
    "section_b_address": {
        "residential_address": "Mysuru",
        "city": "Mysuru",
        "state": "Karnataka",
        "pincode": "570001"
    },
    "section_c_education": {
        "highest_qualification": "Bachelor of Engineering / Science"
    },
    "section_d_employment": {
        "employment_status": "Job Seeker"
    },
    "section_e_training": {
        "program_id": 2,
        "program_code": "PRG-0002",
        "program_title": "National Skilling Mission: Advanced Python & Concurrency",
        "centre_id": 2,
        "centre_name": "Mysuru Regional Skilling Institute",
        "batch_id": 3,
        "delivery_mode": "Hybrid"
    },
    "section_declaration": {
        "agreed": True,
        "terms": "I confirm that the submitted details are accurate and I agree to be contacted by the selected training centre regarding my application.",
        "timestamp": "2026-11-22T10:35:00.000Z"
    }
}

sub_res = requests.post(
    f"{API_BASE}/enrollments",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token_cit6}"},
    json={
        "program_id": 2,
        "batch_id": 3,
        "selected_mode": "Hybrid",
        "applicant_statement": "Simplified application submission via redesigned form.",
        "application_details": simplified_dossier
    }
)

print("Submit HTTP Status:", sub_res.status_code)
sub_data = sub_res.json()
print("Submit Response:", sub_data)

enr_id = sub_data.get("id")
enr_app_id = sub_data.get("application_id")

conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute(f"SELECT id, code, citizen_ref, program_id, centre_id, batch_id, status FROM enrollments WHERE id = {enr_id}")
    saved = cur.fetchone()
    print("Verified Saved Application in MySQL:", saved)
    assert saved['centre_id'] == 2, f"Expected centre_id 2, got {saved['centre_id']}"
    assert saved['program_id'] == 2
    assert saved['batch_id'] == 3
    print("SUCCESS: Centre ID 2 was derived properly from training_programs table!")

    cur.execute("SELECT id, available_seats, total_seats FROM batches WHERE id = 3")
    b3_after = cur.fetchone()
    print(f"After Test: Batch 3 has {b3_after['available_seats']} / {b3_after['total_seats']} seats.")
    assert b3_after['available_seats'] == b3_before['available_seats'] - 1
    print("SUCCESS: Batch available seats decremented accurately by 1.")

    cur.execute("SELECT COUNT(*) as cnt FROM enrollments WHERE centre_id = 2")
    c2_count_after = cur.fetchone()['cnt']
    print(f"Centre 2 total applications in dashboard: {c2_count_after} (was {c2_count_before})")
    assert c2_count_after == c2_count_before + 1
    print("SUCCESS: Application is immediately visible in Centre 2's dashboard.")

conn.close()

# Also test GET /api/enrollments/me for citizen
my_apps = requests.get(f"{API_BASE}/enrollments/me", headers={"Authorization": f"Bearer {token_cit6}"}).json()
print(f"Citizen CIT-000006 now has {len(my_apps)} active application(s).")
assert any(a['id'] == enr_id for a in my_apps), "New enrollment not in /api/enrollments/me"
print("SUCCESS: Application is immediately visible in citizen's 'My Applications' list.")
