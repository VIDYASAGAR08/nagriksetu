import requests
BASE_URL = "http://localhost:8001"

admin_login1 = requests.post(f"{BASE_URL}/auth/login?institution_id=SCH001", data={"username": "admin.sch001@example.com", "password": "Admin@NagrikSetu2026!"})
token1 = admin_login1.json().get("access_token")
resp1 = requests.get(f"{BASE_URL}/school/admin/staff", headers={"Authorization": f"Bearer {token1}"})
print("SCH001 staff:", resp1.json())

admin_login2 = requests.post(f"{BASE_URL}/auth/login?institution_id=SCH011", data={"username": "newadmin.sch011@example.com", "password": "Admin@NagrikSetu2026!"})
token2 = admin_login2.json().get("access_token")
resp2 = requests.get(f"{BASE_URL}/school/admin/staff", headers={"Authorization": f"Bearer {token2}"})
print("SCH011 staff:", resp2.json())
