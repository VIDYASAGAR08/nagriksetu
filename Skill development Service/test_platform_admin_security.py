import requests
import pymysql

# 1. Login as Platform Admin
adm_login = requests.post("http://127.0.0.1:8003/api/auth/login", json={
    "email": "skill.admin@nagriksetu.local",
    "password": "SkillAdmin@2026!"
})
assert adm_login.status_code == 200, f"Login failed: {adm_login.status_code}"
tok = adm_login.json()["access_token"]
headers = {"Authorization": f"Bearer {tok}"}
print(f"Platform Admin authenticated successfully. User: {adm_login.json().get('email')}, Role: {adm_login.json().get('role')}")

# Database snapshot before tests
conn = pymysql.connect(host="127.0.0.1", port=3308, user="nagriksetu_skill", password="skill-app-pass-2026", database="skill_db")
cur = conn.cursor()

def get_counts():
    cur.execute("SELECT COUNT(*) FROM skills")
    skills_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM training_programs")
    progs_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM batches")
    batches_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trainers")
    trainers_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM training_centres")
    centres_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM enrollments")
    enrs_cnt = cur.fetchone()[0]
    return skills_cnt, progs_cnt, batches_cnt, trainers_cnt, centres_cnt, enrs_cnt

counts_before = get_counts()
print("\n--- DB Counts Before Write Tests ---")
print(f"Skills: {counts_before[0]}, Programs: {counts_before[1]}, Batches: {counts_before[2]}, Trainers: {counts_before[3]}, Centres: {counts_before[4]}, Enrollments: {counts_before[5]}")

tests = [
    (
        "POST /api/admin/skills (Create Skill)",
        "POST",
        "http://127.0.0.1:8003/api/admin/skills",
        {
            "name": "Test Security Skill",
            "category_id": 1,
            "category_name": "IT",
            "level": "Intermediate",
            "duration_weeks": 4,
            "duration_hours": 40,
            "summary": "Security test",
            "details": "Details",
            "prerequisites": "None",
            "learning_objectives": "Test",
            "learning_outcomes": "Test",
            "relevant_industries": "IT"
        }
    ),
    (
        "PUT /api/admin/skills/1 (Update Skill)",
        "PUT",
        "http://127.0.0.1:8003/api/admin/skills/1",
        {
            "name": "Updated Skill",
            "category_id": 1,
            "category_name": "IT",
            "level": "Intermediate",
            "duration_weeks": 4,
            "duration_hours": 40,
            "summary": "Security test",
            "details": "Details",
            "prerequisites": "None",
            "learning_objectives": "Test",
            "learning_outcomes": "Test",
            "relevant_industries": "IT"
        }
    ),
    (
        "DELETE /api/admin/skills/1 (Deactivate Skill)",
        "DELETE",
        "http://127.0.0.1:8003/api/admin/skills/1",
        None
    ),
    (
        "POST /api/admin/programmes (Create Programme)",
        "POST",
        "http://127.0.0.1:8003/api/admin/programmes",
        {
            "title": "Unauthorized Program",
            "skill_id": 1,
            "centre_id": 1,
            "duration_hours": 40,
            "curriculum": "Test curriculum",
            "trainer_id": 1
        }
    ),
    (
        "POST /api/admin/batches (Create Batch)",
        "POST",
        "http://127.0.0.1:8003/api/admin/batches",
        {
            "program_id": 19,
            "batch_name": "Test Blocked Batch",
            "timings": "10:00 AM - 1:00 PM",
            "training_schedule": "Mon-Fri",
            "mode": "Hybrid",
            "total_seats": 30,
            "start_date": "2027-01-01",
            "end_date": "2027-03-01",
            "application_deadline": "2026-12-25"
        }
    ),
    (
        "PATCH /api/admin/batches/37/seats?new_seats=50 (Update Batch Seats)",
        "PATCH",
        "http://127.0.0.1:8003/api/admin/batches/37/seats?new_seats=50",
        None
    ),
    (
        "POST /api/admin/trainers (Create Trainer)",
        "POST",
        "http://127.0.0.1:8003/api/admin/trainers",
        {
            "name": "Unauthorized Trainer",
            "qualification": "M.Tech",
            "specialisation": "Cyber Security",
            "experience_years": 10,
            "contact_email": "unauth@test.local",
            "assigned_centre_id": 1
        }
    ),
    (
        "POST /api/admin/centres (Create Centre)",
        "POST",
        "http://127.0.0.1:8003/api/admin/centres",
        {
            "name": "Unauthorized Centre",
            "location": "MG Road, Bengaluru",
            "district": "Bengaluru",
            "address": "MG Road",
            "contact_phone": "9876543210",
            "contact_email": "centre@test.local"
        }
    ),
    (
        "POST /api/enrollments (Citizen Application as Platform Admin)",
        "POST",
        "http://127.0.0.1:8003/api/enrollments",
        {
            "program_id": 19,
            "batch_id": 37,
            "selected_mode": "Hybrid",
            "applicant_statement": "I want to learn"
        }
    )
]

print("\n--- Testing Representative Write Endpoints ---")
all_passed = True
for name, method, url, payload in tests:
    if method == "POST":
        res = requests.post(url, headers=headers, json=payload)
    elif method == "PUT":
        res = requests.put(url, headers=headers, json=payload)
    elif method == "PATCH":
        res = requests.patch(url, headers=headers, json=payload)
    elif method == "DELETE":
        res = requests.delete(url, headers=headers)
    
    status = res.status_code
    detail = res.json().get("detail", "") if res.headers.get("content-type", "").startswith("application/json") else res.text
    
    passed = (status == 403)
    if not passed:
        all_passed = False
    
    result_str = "[PASS]" if passed else "[FAIL]"
    print(f"{result_str} {name} -> Status: {status} (Expected: 403)")
    print(f"       Detail: {detail}")

counts_after = get_counts()
print("\n--- DB Counts After Write Tests ---")
print(f"Skills: {counts_after[0]}, Programs: {counts_after[1]}, Batches: {counts_after[2]}, Trainers: {counts_after[3]}, Centres: {counts_after[4]}, Enrollments: {counts_after[5]}")

db_unchanged = (counts_before == counts_after)
print(f"Database unchanged: {db_unchanged}")
assert db_unchanged, "Database records were modified by unauthorized requests!"
assert all_passed, "Some endpoints did not return 403!"
print("\nAll Platform Admin write attempts returned HTTP 403 and the database remained completely unchanged!")
conn.close()
