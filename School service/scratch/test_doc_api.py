import requests

base_url = "http://localhost:8001"

# 1. Login as K.S Rao
login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("K.S Rao login OK")

# 2. Test GET /admissions/applications/APP-2026-SCH019-6ED0FE/documents
docs_res = requests.get(f"{base_url}/admissions/applications/APP-2026-SCH019-6ED0FE/documents", headers=headers)
print("Docs endpoint status:", docs_res.status_code)
if docs_res.status_code == 200:
    docs = docs_res.json()
    print(f"Retrieved {len(docs)} documents:")
    for d in docs:
        print(" ", d["document_id"], d["document_type"], d["file_name"], d["verification_status"])
else:
    print("Error:", docs_res.text)

# 3. Test GET document file
if docs_res.status_code == 200 and len(docs_res.json()) > 0:
    first_doc = docs_res.json()[0]
    file_res = requests.get(f"{base_url}/admissions/applications/APP-2026-SCH019-6ED0FE/documents/{first_doc['document_id']}/file", headers=headers)
    print("File endpoint status:", file_res.status_code, "Length:", len(file_res.content), "Type:", file_res.headers.get("content-type"))
