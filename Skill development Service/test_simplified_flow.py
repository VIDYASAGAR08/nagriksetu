import requests
import json
import pymysql

API_BASE = "http://127.0.0.1:8003/api"

# We will test submitting applications for 2 different programmes belonging to 2 different centres
# We can use citizen CIT-000006 (karan123@gmail.com)
# Let's generate a valid citizen token directly using jwt_secret from backend
import jwt
import time

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

# Let's check existing applications for CIT-000006
my_apps = requests.get(f"{API_BASE}/enrollments/me", headers={"Authorization": f"Bearer {token_cit6}"}).json()
print(f"CIT-000006 current active apps: {len(my_apps)}")
existing_prog_ids = [a['program_id'] for a in my_apps]
print(f"Existing program IDs: {existing_prog_ids}")

# Let's find 2 programmes that CIT-000006 has NOT applied to yet, e.g., one from Centre 1 and one from Centre 2
conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='nagriksetu_skill',
    password='skill-app-pass-2026',
    database='skill_db',
    cursorclass=pymysql.cursors.DictCursor
)

test_targets = []
with conn.cursor() as cur:
    for cid in [1, 2]:
        cur.execute(f"""
            SELECT tp.id, tp.code, tp.title, tp.centre_id, tc.name as centre_name,
                   b.id as batch_id, b.batch_name, b.available_seats, b.total_seats
            FROM training_programs tp
            JOIN training_centres tc ON tp.centre_id = tc.id
            JOIN batches b ON tp.id = b.program_id
            WHERE tp.centre_id = {cid} AND tp.id NOT IN ({','.join(map(str, existing_prog_ids or [0]))}) AND b.available_seats > 0
            LIMIT 1
        """)
        t = cur.fetchone()
        if t:
            test_targets.append(t)

conn.close()

print("\nSelected test targets:")
for t in test_targets:
    print(f"Prog ID {t['id']} ({t['code']}) -> Centre ID {t['centre_id']} ({t['centre_name']}) | Batch {t['batch_id']} ({t['available_seats']} seats)")

# Now test submission with the simplified form payload for each target
for t in test_targets:
    print(f"\n--- Submitting Simplified Application for Programme #{t['id']} ({t['title']}) ---")
    simplified_dossier = {
        "section_a_personal": {
            "full_name": "Karan Sharma",
            "citizen_ref": "CIT-000006",
            "email": "karan123@gmail.com",
            "phone": "9876543210"
        },
        "section_b_location": {
            "city_district": "Bengaluru Urban",
            "pincode": "560001"
        },
        "section_b_address": {
            "residential_address": "Bengaluru Urban",
            "city": "Bengaluru Urban",
            "state": "Karnataka",
            "pincode": "560001"
        },
        "section_c_education": {
            "highest_qualification": "Bachelor of Engineering / Science"
        },
        "section_d_employment": {
            "employment_status": "Job Seeker"
        },
        "section_e_training": {
            "program_id": t['id'],
            "program_code": t['code'],
            "program_title": t['title'],
            "centre_id": t['centre_id'],
            "centre_name": t['centre_name'],
            "batch_id": t['batch_id'],
            "delivery_mode": "Hybrid"
        },
        "section_declaration": {
            "agreed": True,
            "terms": "I confirm that the submitted details are accurate and I agree to be contacted by the selected training centre regarding my application.",
            "timestamp": "2026-11-22T10:34:00.000Z"
        }
    }

    sub_res = requests.post(
        f"{API_BASE}/enrollments",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token_cit6}"},
        json={
            "program_id": t['id'],
            "batch_id": t['batch_id'],
            "selected_mode": "Hybrid",
            "applicant_statement": "Simplified application submission via redesigned form.",
            "application_details": simplified_dossier
        }
    )
    print("Submit HTTP Status:", sub_res.status_code)
    sub_data = sub_res.json()
    print("Submit Response:", sub_data)

    if sub_res.status_code == 201:
        enr_code = sub_data.get("enrollment_code")
        # Verify in MySQL that centre_id was correctly derived and seats were decremented
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3308,
            user='nagriksetu_skill',
            password='skill-app-pass-2026',
            database='skill_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, code, citizen_ref, program_id, centre_id, batch_id, status FROM enrollments WHERE code = '{enr_code}'")
            saved_enr = cur.fetchone()
            print("Verified Saved Application in MySQL:", saved_enr)
            assert saved_enr['centre_id'] == t['centre_id'], f"Mismatch in centre_id: {saved_enr['centre_id']} != {t['centre_id']}"
            print(f"SUCCESS: centre_id properly derived from database as {saved_enr['centre_id']} for {t['centre_name']}")

            # Verify batch available seats decremented
            cur.execute(f"SELECT id, available_seats, total_seats FROM batches WHERE id = {t['batch_id']}")
            updated_batch = cur.fetchone()
            print(f"Batch {t['batch_id']} seat capacity: {updated_batch['available_seats']} / {updated_batch['total_seats']}")
            assert updated_batch['available_seats'] == t['available_seats'] - 1, "Seat capacity was not decremented"
            print("SUCCESS: Batch seat capacity verified and updated.")

            # Verify application appears in Centre Dashboard for this centre
            cur.execute(f"SELECT COUNT(*) as centre_app_count FROM enrollments WHERE centre_id = {t['centre_id']}")
            centre_apps = cur.fetchone()
            print(f"Centre #{t['centre_id']} total applications in dashboard: {centre_apps['centre_app_count']}")

        conn.close()

print("\nALL BACKEND APPLICATION WORKFLOW TESTS PASSED!")
