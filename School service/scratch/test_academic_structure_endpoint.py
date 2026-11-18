import requests
import json
import sqlite3

base_url = "http://localhost:8001"

conn = sqlite3.connect(r'C:\Users\callm\nagriksetu\backend\data\nagriksetu.db')
cur = conn.cursor()
admins = cur.execute("SELECT email, role, school_id FROM users WHERE role IN ('platform_admin', 'school_admin', 'academic_admin') LIMIT 5").fetchall()
print("Admins in DB:", admins)
conn.close()

# Login as platform admin
login_res = requests.post(f"{base_url}/auth/login", data={"username": "admin.central@nagriksetu.gov", "password": "Central@NagrikSetu2026!"})
print("Platform admin login status:", login_res.status_code)
token = login_res.json()["access_token"]

# Test academic-structure for COL001 (Degree College)
res_col = requests.get(f"{base_url}/institution/COL001/academic-structure", headers={"Authorization": f"Bearer {token}"})
print("COL001 structure status:", res_col.status_code)
print("COL001 structure data:")
print(json.dumps(res_col.json(), indent=2))

# Test academic-structure for SCH011 (PU College)
res_pu = requests.get(f"{base_url}/institution/SCH011/academic-structure", headers={"Authorization": f"Bearer {token}"})
print("\nSCH011 structure status:", res_pu.status_code)
print("SCH011 structure data:")
print(json.dumps(res_pu.json(), indent=2))
