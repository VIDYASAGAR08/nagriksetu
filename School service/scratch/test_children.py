import requests

base_url = "http://localhost:8001"
r = requests.post(f"{base_url}/auth/login", data={"username": "9876543210", "password": "Str0ngPass!2026"})
token = r.json()["access_token"]
children = requests.get(f"{base_url}/parent/children", headers={"Authorization": f"Bearer {token}"}).json()
print("Children returned for parent:")
for c in children:
    print(c["student_name"], c["student_id"], c["permanent_student_id"])
