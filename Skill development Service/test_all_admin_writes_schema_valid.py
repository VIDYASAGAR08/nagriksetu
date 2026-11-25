import urllib.request
import json

BASE_URL = "http://localhost:8003"

def make_req(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except:
            return e.code, {"raw": body}

# 1. Login as Platform Admin
status, login_res = make_req("/api/auth/login", method="POST", data={
    "email": "skill.admin@nagriksetu.local",
    "password": "SkillAdmin@2026!"
})
assert status == 200, f"Admin login failed: {login_res}"
token = login_res["access_token"]
print("Platform Admin logged in successfully. Token acquired.")

# Test endpoints
test_endpoints = [
    {
        "name": "POST /api/admin/skills (Create Skill)",
        "method": "POST",
        "url": "/api/admin/skills",
        "body": {
            "name": "Unauthorized Test Skill",
            "category_name": "Computer Science & Information Technology",
            "level": "Beginner",
            "duration_weeks": 8,
            "duration_hours": 120,
            "summary": "Unauthorized test description",
            "details": "Unauthorized detailed description",
            "prerequisites": "Basic literacy"
        }
    },
    {
        "name": "PUT /api/admin/skills/1 (Update Skill)",
        "method": "PUT",
        "url": "/api/admin/skills/1",
        "body": {
            "name": "Unauthorized Updated Skill",
            "category_name": "Computer Science & Information Technology",
            "level": "Intermediate",
            "duration_weeks": 10,
            "duration_hours": 140,
            "summary": "Unauthorized update description",
            "details": "Unauthorized update details",
            "prerequisites": "Basic python"
        }
    },
    {
        "name": "DELETE /api/admin/skills/1 (Delete Skill)",
        "method": "DELETE",
        "url": "/api/admin/skills/1",
        "body": None
    },
    {
        "name": "POST /api/admin/programmes (Create Programme)",
        "method": "POST",
        "url": "/api/admin/programmes",
        "body": {
            "code": "PRG-9999",
            "skill_id": 1,
            "centre_id": 1,
            "trainer_id": 1,
            "title": "Unauthorized Test Programme",
            "description": "Unauthorized programme description",
            "provider_name": "Unauthorized Academy",
            "mode": "Classroom",
            "duration_hours": 120,
            "fee": 0,
            "scholarship_available": True,
            "eligibility_criteria": "10th Pass",
            "prerequisites": "Basic literacy"
        }
    },
    {
        "name": "POST /api/admin/batches (Create Batch - Schema-Valid)",
        "method": "POST",
        "url": "/api/admin/batches",
        "body": {
            "program_id": 19,
            "batch_name": "Unauthorized Schema-Valid Batch",
            "timings": "09:00 AM - 12:00 PM",
            "training_schedule": "Monday to Friday",
            "mode": "Classroom",
            "total_seats": 30,
            "start_date": "2026-12-01",
            "end_date": "2027-02-28",
            "application_deadline": "2026-11-30"
        }
    },
    {
        "name": "PATCH /api/admin/batches/37/seats (Update Batch Seats)",
        "method": "PATCH",
        "url": "/api/admin/batches/37/seats",
        "body": {
            "available_seats": 50
        }
    },
    {
        "name": "POST /api/admin/trainers (Create Trainer)",
        "method": "POST",
        "url": "/api/admin/trainers",
        "body": {
            "name": "Unauthorized Trainer",
            "qualification": "Ph.D. in Computer Science",
            "specialisation": "Cybersecurity",
            "experience_years": 10,
            "contact_email": "unauthorized.trainer@nagriksetu.local",
            "assigned_centre_id": 1,
            "availability": "Weekdays"
        }
    },
    {
        "name": "POST /api/admin/centres (Create Training Centre)",
        "method": "POST",
        "url": "/api/admin/centres",
        "body": {
            "name": "Unauthorized Training Hub",
            "district": "Bengaluru Urban",
            "location": "Whitefield",
            "state": "Karnataka",
            "address": "ITPL Main Road",
            "contact_phone": "+91 9999999999",
            "contact_email": "unauth@centre.local"
        }
    },
    {
        "name": "PATCH /api/admin/centres/1/status (Update Centre Status)",
        "method": "PATCH",
        "url": "/api/admin/centres/1/status",
        "body": {
            "approval_status": "REJECTED"
        }
    },
    {
        "name": "POST /api/admin/centres/1/assign-admin (Assign Centre Admin)",
        "method": "POST",
        "url": "/api/admin/centres/1/assign-admin",
        "body": {
            "email": "unauth.admin@nagriksetu.local",
            "full_name": "Unauthorized Admin",
            "password": "Password@123"
        }
    }
]

print("\n" + "=" * 80)
print("TESTING ALL PLATFORM ADMIN WRITE ENDPOINTS WITH SCHEMA-VALID BODIES")
print("=" * 80)

results = []
for ep in test_endpoints:
    st, resp = make_req(ep["url"], method=ep["method"], data=ep["body"], token=token)
    is_403 = (st == 403)
    results.append({
        "name": ep["name"],
        "status": st,
        "is_403": is_403,
        "detail": resp.get("detail", str(resp))
    })
    status_str = "PASS (HTTP 403 Forbidden)" if is_403 else f"FAIL (HTTP {st})"
    print(f"[{status_str}] {ep['name']}")
    print(f"       Detail: {resp.get('detail', str(resp))[:100]}")

all_passed = all(r["is_403"] for r in results)
print("=" * 80)
print(f"SUMMARY: {sum(1 for r in results if r['is_403'])} / {len(results)} WRITE ENDPOINTS RETURNED HTTP 403")
print(f"ALL STRICTLY PROTECTED: {all_passed}")
print("=" * 80)
