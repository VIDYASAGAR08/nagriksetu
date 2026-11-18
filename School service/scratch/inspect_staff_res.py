import requests
import json

base_url = "http://localhost:8001"
res = requests.post(f"{base_url}/auth/login?institution_id=SCH001", data={"username": "admin.sch001@example.com", "password": "Admin@NagrikSetu2026!"})
token = res.json().get("access_token")

res_staff = requests.get(f"{base_url}/school/admin/staff", headers={"Authorization": f"Bearer {token}"})
print("Staff endpoint response structure:")
print(json.dumps(res_staff.json(), indent=2)[:500])

res_apps = requests.get(f"{base_url}/school/admissions/applications", headers={"Authorization": f"Bearer {token}"})
print("Applications endpoint response structure:")
print(json.dumps(res_apps.json(), indent=2)[:500])
