import requests
import json

base_url = "http://localhost:8001"
login_res = requests.post(f"{base_url}/auth/login", data={"username": "rao@edu.in", "password": "Rao@1234"})
assert login_res.status_code == 200
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

res = requests.get(f"{base_url}/school/admissions/applications/APP-2026-SCH019-6ED0FE", headers=headers)
assert res.status_code == 200, f"Failed: {res.text}"
app = res.json()

print("Application:", app.get("application_id"), "| Applicant:", app.get("applicant_name"), "| Status:", app.get("status"))
print("Stage 2 Submitted:", app.get("stage2_submitted"))
print("Stage 2 Details:")
print(json.dumps(app.get("stage2_details"), indent=2))
print(f"Documents ({len(app.get('documents', []))}):")
for d in app.get("documents", []):
    print(f"  [{d['verification_status']}] {d['document_type']} - {d['file_name']} ({d['file_size_bytes']} bytes) -> {d['download_url']}")
print(f"Summary: Verified: {app.get('verified_documents_count')}/{app.get('total_documents_count')}, Pending: {app.get('pending_documents_count')}")

# Also test file access using ?token=
first_doc = app["documents"][0]
file_res = requests.get(f"{base_url}{first_doc['download_url']}?token={token}")
print(f"File ?token= download status: {file_res.status_code}, Length: {len(file_res.content)}")
assert file_res.status_code == 200
